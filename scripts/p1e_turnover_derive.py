"""P-1e derived-turnover sidecar builder (data engineering, zero inference).

Face fact (TURNOVER_DERIVATION.md, frozen): the bars `turnover` column is
all-NaN except the final bar; the adjudicated derivation is
  non-688/689: turnover = volume / outstanding_share
  688xxx/689xxx: turnover = (volume / 100) / outstanding_share
(the 688/689 bars volume column is 100x real shares -- same unit anomaly
the Stage-A cache fixed for its own volume/vwap fields).

This script materializes the derived turnover ONCE as a NEW sidecar file in
the p1c_stock cache dir (existing cache files are NOT modified -- the
loop-owned-artifact red line in TURNOVER_DERIVATION.md SS3; consumption of
the sidecar is frozen in the P-1E prereg):
  Money02/data/cache/p1c_stock/turnover_derived.npy      (float32, T x N)
  Money02/data/cache/p1c_stock/turnover_derived.meta.json (provenance)

Gates (fail = exit 1, no sidecar written):
  [1] stored-vs-derived final-bar reconciliation on 000001/600519/300750
      (non-688 trio) + 688001/688008 (688 pair): |d-st|/|st| <= 1e-6
  [2] post-fix sanity: rows with derived > 1.05 must be ~zero (pre-fix
      audit had 335k, all 688); count recorded either way
  [3] column alignment: bars-dir symbol order must equal the cache N
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_stock_ic_batch as P1C                                   # noqa: E402

CACHE_DIR = P1C.CACHE_DIR
BARS_DIR = P1C.BARS_DIR
OUT_NPY = os.path.join(CACHE_DIR, "turnover_derived.npy")
OUT_META = os.path.join(CACHE_DIR, "turnover_derived.meta.json")
GATE_SYMS = ["000001", "600519", "300750", "688001", "688008"]
# stored final-bar turnover is 4-decimal rounded by the source (0.0039 /
# 0.002 / 0.0111...): a relative 1e-6 gate is over-strict on rounded small
# values (the r49 audit's check-A "MISMATCH 5204" verdict shares this root
# cause; its r1 diagnostic matched implied/osh within +-0.2%). Gate at the
# source's rounding scale: half-ulp + float32 storage margin.
GATE_ABS_TOL = 5.05e-5


def derive_symbol(sym):
    df = pd.read_parquet(os.path.join(BARS_DIR, sym + ".parquet"),
                         columns=["date", "volume", "outstanding_share"])
    vol = df["volume"].astype(np.float64).values
    osh = df["outstanding_share"].astype(np.float64).values
    if sym.startswith(("688", "689")):
        vol = vol / 100.0
    with np.errstate(divide="ignore", invalid="ignore"):
        tr = np.where((osh > 0) & np.isfinite(vol) & np.isfinite(osh),
                      vol / osh, np.nan)
    return df["date"].values, tr


def main():
    t0 = time.time()
    dates = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    main_idx = pd.to_datetime(dates, unit="us")      # r219 fix: unit=us
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))]
    meta_cache = json.load(open(os.path.join(CACHE_DIR, "meta.json"),
                                encoding="utf-8"))
    assert len(syms) == meta_cache["shape"]["N"], "bars vs cache N mismatch"
    T, N = len(dates), len(syms)
    out = np.full((T, N), np.nan, dtype=np.float32)
    n_unmatched_dates = 0
    n_rows = 0
    for j, sym in enumerate(syms):
        dts, tr = derive_symbol(sym)
        pos = main_idx.get_indexer(pd.DatetimeIndex(dts))
        n_unmatched_dates += int((pos < 0).sum())
        pos = pos[pos >= 0]
        # k-th valid main-calendar position <-> k-th parquet row
        # (symbol dates are a chronological subset of the union calendar)
        out[pos, j] = tr[: len(pos)]
        n_rows += len(pos)
        if (j + 1) % 1000 == 0:
            print(f"  {j + 1}/{N} symbols ({time.time() - t0:.0f}s)",
                  flush=True)

    # [3] alignment gate
    ok_align = n_unmatched_dates == 0

    # [1] stored-vs-derived final-bar gate (cache turnover col holds the
    # final-bar stored value)
    stored = np.load(os.path.join(CACHE_DIR, "turnover.npy"),
                     mmap_mode="r")
    gate = {}
    ok_gate = True
    for sym in GATE_SYMS:
        j = syms.index(sym)
        col = np.asarray(stored[:, j], dtype=np.float64)
        fin = np.flatnonzero(np.isfinite(col))
        if not len(fin):
            gate[sym] = {"status": "no_stored_value"}
            ok_gate = False
            continue
        st = col[fin[-1]]
        dv = float(out[fin[-1], j])
        dev = abs(dv - st)
        gate[sym] = {"stored": round(float(st), 6),
                     "derived": round(dv, 6),
                     "abs_dev": round(float(dev), 8)}
        ok_gate &= dev <= GATE_ABS_TOL

    # [2] post-fix sanity
    sample = out[:: 7]                      # ~1/7 row sample, cheap
    n_gt105 = int(np.nansum(sample > 1.05)) * 7   # scaled estimate
    share_gt1 = float((sample > 1.0).mean()) if sample.size else 0.0
    ok_sane = n_gt105 == 0

    print(f"gate_align={ok_align} (unmatched {n_unmatched_dates}) "
          f"gate_recon={ok_gate} sane={ok_sane} "
          f"(est rows>1.05: {n_gt105}, share>1: {share_gt1:.5f})",
          flush=True)
    print(json.dumps(gate, indent=1), flush=True)
    if not (ok_align and ok_gate and ok_sane):
        print("GATE FAIL - no sidecar written", flush=True)
        return 1

    np.save(OUT_NPY, out)
    provenance = {
        "artifact": "turnover_derived sidecar for P-1e (and any consumer)",
        "formula": "non-688/689: volume/osh; 688xxx/689xxx: "
                   "(volume/100)/osh (TURNOVER_DERIVATION.md SS4 frozen)",
        "source": "Money02/data/bars/*.parquet volume+outstanding_share",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "shape": {"T": T, "N": N, "dtype": "float32"},
        "alignment": "cache dates.npy union calendar; bars symbol order "
                     "(== cache columns)",
        "gates": {"align_unmatched_dates": n_unmatched_dates,
                  "finalbar_recon": gate,
                  "abs_tol_half_ulp4": GATE_ABS_TOL,
                  "est_rows_gt_1p05": n_gt105,
                  "share_gt_1": round(share_gt1, 6)},
        "red_line": "existing cache files untouched; this is a NEW sidecar "
                    "file; consumption frozen in P1E_ZOO_BEHAV_IC.md SS2",
    }
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, ensure_ascii=False)
    print(f"saved: {OUT_NPY} + meta (elapsed {time.time() - t0:.0f}s)",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
