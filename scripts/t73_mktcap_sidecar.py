"""T-73 s2 slice-D support: raw-close x share-count size sidecar builder
(data engineering, zero inference; mirrors p1e_turnover_derive.py precedent).

Purpose: the s2 factor-history slice needs a cross-sectional SIZE face.
The P1C cache close is qfq (event-adjusted), so cache_close x osh would be a
double-adjusted size proxy. The bars parquet carries `preclose` + `pct_chg`,
and the exchange convention

    raw_close_t = preclose_t * (1 + pct_chg_t / 100)

reconstructs the actual traded (unadjusted) close EXACTLY (pct_chg is defined
by the exchange against preclose, including ex-div/ex-right basis days).
Verified on 000001 last bar: preclose 11.73 x (1 - 0.170503/100) = 11.71000
== cache close 11.71 (qfq anchors to raw at the final bar).

OSH PROVENANCE (empirical probe this build, R258): the bars `outstanding_share`
column is the CURRENT share snapshot ffilled BACKWARD (000001/300750/600519
show ~1 trivial change on the final bar only, zero across full history) --
NOT per-row historical shares. Therefore

    mktcap_t = raw_close_t * osh_t

is a SIZE PROXY, not a true historical cap:
  - splits/高送转: past caps of share-multiplying names OVERSTATED
  - dilutive issuance: past caps of share-growing names OVERSTATED
  - OOS 2025+ segment: osh_today == osh_t -> caps near-TRUE
(The turnover_derived sidecar shares this osh provenance -- its final-bar
recon gate passed for the same reason; historical turnover levels carry the
inverse distortion. Recorded for cross-family honesty, R258.)

This script materializes the sidecar ONCE as a NEW file in the p1c_stock cache
dir (existing cache files are NOT modified -- loop-owned-artifact red line,
turnover_derived precedent):
  Money02/data/cache/p1c_stock/mktcap_raw.npy       (float32, T x N, CNY-proxy)
  Money02/data/cache/p1c_stock/mktcap_raw.meta.json (provenance)

Gates (fail = exit 1, no sidecar written):
  [1] alignment: bars rows must be a subset of the cache union calendar
      (n_unmatched_dates == 0)
  [2] final-bar recon on 000001/600519/300750/688001/688008: reconstructed
      raw_close at the symbol's last bar == cache close.npy last finite value
      (rel tol 5e-4; source rounding preclose 2dp / pct 6dp)
  [3] osh coverage: rows with finite volume but osh not (>0, finite) counted
  [4] sanity: mktcap > 0 wherever finite; share of positive rows recorded
  [5] osh-provenance probe: per-gate-sym osh change count recorded in meta
      (empirical evidence of the current-ffilled-back face; informational)
Descriptive (no gate): per-symbol osh jump events (ratio >= 2 or <= 0.5 on
consecutive bars rows) -- expected ~0 given the provenance face.
"""
import glob
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_stock_ic_batch as P1C                                   # noqa: E402

CACHE_DIR = P1C.CACHE_DIR
BARS_DIR = P1C.BARS_DIR
OUT_NPY = os.path.join(CACHE_DIR, "mktcap_raw.npy")
OUT_META = os.path.join(CACHE_DIR, "mktcap_raw.meta.json")
GATE_SYMS = ["000001", "600519", "300750", "688001", "688008"]
GATE_REL_TOL = 5e-4


def reconstruct_raw_close(preclose, pct_chg):
    """Exchange-exact raw close reconstruction (pct in PERCENT vs preclose)."""
    with np.errstate(invalid="ignore"):
        return np.where(np.isfinite(preclose) & np.isfinite(pct_chg),
                        preclose * (1.0 + pct_chg / 100.0), np.nan)


def derive_symbol(sym):
    df = pd.read_parquet(os.path.join(BARS_DIR, sym + ".parquet"),
                         columns=["date", "preclose", "pct_chg",
                                  "outstanding_share", "volume"])
    pc = df["preclose"].astype(np.float64).values
    pct = df["pct_chg"].astype(np.float64).values
    osh = df["outstanding_share"].astype(np.float64).values
    vol = df["volume"].astype(np.float64).values
    raw = reconstruct_raw_close(pc, pct)
    with np.errstate(invalid="ignore"):
        cap = np.where(np.isfinite(raw) & np.isfinite(osh) & (osh > 0),
                       raw * osh, np.nan)
    # [3] coverage: volume finite but osh unusable
    n_vol_finite_osh_bad = int(
        (np.isfinite(vol) & ~(np.isfinite(osh) & (osh > 0))).sum())
    # descriptive: corporate-action jumps in share count
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = osh[1:] / osh[:-1]
    jumps = int(np.nansum((ratio >= 2.0) | (ratio <= 0.5)))
    return {"dates": df["date"].values, "cap": cap,
            "raw_last": (float(raw[np.isfinite(raw)][-1])
                         if np.isfinite(raw).any() else np.nan),
            "vol_finite_osh_bad": n_vol_finite_osh_bad, "osh_jumps": jumps,
            "osh_changes": int(np.nansum(np.diff(osh) != 0))}


def selftest() -> int:
    # reconstruction formula: exact + NaN propagation
    assert reconstruct_raw_close(np.array([100.0]), np.array([1.0]))[0] == 101.0
    assert np.isnan(reconstruct_raw_close(np.array([100.0]), np.array([np.nan]))[0])
    assert np.isnan(reconstruct_raw_close(np.array([np.nan]), np.array([1.0]))[0])
    # ex-right day included: preclose is the ex-basis, close vs it = raw trade
    r = reconstruct_raw_close(np.array([10.0]), np.array([10.0]))
    assert abs(r[0] - 11.0) < 1e-12
    # osh jump detector semantics
    osh = np.array([1e8, 1e8, 2e8, 2e8, 5e7], dtype=float)
    ratio = osh[1:] / osh[:-1]
    jumps = int(np.nansum((ratio >= 2.0) | (ratio <= 0.5)))
    assert jumps == 2                      # 1e8->2e8 and 2e8->5e7
    print("t73_mktcap_sidecar selftest: raw-close reconstruction + NaN "
          "propagation + jump detector PASS")
    return 0


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
    n_vol_finite_osh_bad = 0
    n_osh_jumps = 0
    last_raw = {}
    osh_changes_gate = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for j, res in enumerate(ex.map(derive_symbol, syms)):
            pos = main_idx.get_indexer(pd.DatetimeIndex(res["dates"]))
            n_unmatched_dates += int((pos < 0).sum())
            pos_ok = pos[pos >= 0]
            out[pos_ok, j] = res["cap"][: len(pos_ok)]
            n_vol_finite_osh_bad += res["vol_finite_osh_bad"]
            n_osh_jumps += res["osh_jumps"]
            last_raw[syms[j]] = res["raw_last"]
            if syms[j] in GATE_SYMS:
                osh_changes_gate[syms[j]] = res["osh_changes"]
            if (j + 1) % 1000 == 0:
                print(f"  {j + 1}/{N} symbols ({time.time() - t0:.0f}s)",
                      flush=True)

    # [1] alignment gate
    ok_align = n_unmatched_dates == 0

    # [2] final-bar recon gate: reconstructed raw close == cache close last
    stored = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
    gate = {}
    ok_gate = True
    for sym in GATE_SYMS:
        j = syms.index(sym)
        col = np.asarray(stored[:, j], dtype=np.float64)
        fin = np.flatnonzero(np.isfinite(col))
        if not len(fin) or not np.isfinite(last_raw.get(sym, np.nan)):
            gate[sym] = {"status": "missing_face"}
            ok_gate = False
            continue
        st = col[fin[-1]]
        dv = last_raw[sym]
        rel = abs(dv - st) / max(abs(st), 1e-12)
        gate[sym] = {"cache_last": round(float(st), 6),
                     "raw_recon": round(dv, 6),
                     "rel_dev": round(float(rel), 8)}
        ok_gate &= rel <= GATE_REL_TOL

    # [4] sanity: positive where finite
    sample = out[::7]
    share_pos = float((sample[np.isfinite(sample)] > 0).mean()) \
        if np.isfinite(sample).any() else 0.0
    n_finite = int(np.isfinite(out).sum())

    print(f"gate_align={ok_align} (unmatched {n_unmatched_dates}) "
          f"gate_recon={ok_gate} osh_bad={n_vol_finite_osh_bad} "
          f"osh_jump_events={n_osh_jumps} finite_rows={n_finite} "
          f"share_pos={share_pos:.6f}", flush=True)
    print(json.dumps(gate, indent=1), flush=True)
    if not (ok_align and ok_gate and share_pos == 1.0):
        print("GATE FAIL - no sidecar written", flush=True)
        return 1

    np.save(OUT_NPY, out)
    provenance = {
        "artifact": "mktcap_raw sidecar (T-73 s2 slice-D SIZE face; any consumer)",
        "formula": "raw_close_t = preclose_t*(1+pct_chg_t/100) (exchange pct "
                   "convention, ex-days included); mktcap = raw_close * "
                   "outstanding_share",
        "honesty_face": "SIZE PROXY, not true historical cap: bars osh = "
                        "CURRENT snapshot ffilled backward (empirical probe: "
                        "~1 final-bar-only change per gate sym, zero "
                        "historical) -- splits/dilutive issuance OVERSTATE "
                        "past caps of share-growing names; OOS 2025+ segment "
                        "near-TRUE (osh_today == osh_t). raw_close itself is "
                        "exchange-exact (verified 000001 final bar 11.71).",
        "osh_provenance_probe_gate_syms": osh_changes_gate,
        "cross_family_note": "turnover_derived sidecar shares this osh "
                            "provenance (its final-bar-only recon gate "
                            "passes for the same reason); historical "
                            "turnover levels carry the inverse distortion",
        "source": "Money02/data/bars/*.parquet preclose+pct_chg+"
                  "outstanding_share",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "shape": {"T": T, "N": N, "dtype": "float32"},
        "alignment": "cache dates.npy union calendar; bars symbol order "
                     "(== cache columns); turnover_derived precedent",
        "gates": {"align_unmatched_dates": n_unmatched_dates,
                  "finalbar_recon": gate, "rel_tol": GATE_REL_TOL,
                  "vol_finite_osh_bad": n_vol_finite_osh_bad,
                  "finite_rows": n_finite, "share_positive": share_pos},
        "descriptive_corporate_actions": {
            "osh_jump_events_ge2x_or_le_half": n_osh_jumps},
        "red_line": "existing cache files untouched; this is a NEW sidecar "
                    "file; consumption frozen in the t73_s2_factor_history "
                    "prereg header",
    }
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, ensure_ascii=False)
    print(f"saved: {OUT_NPY} + meta (elapsed {time.time() - t0:.0f}s)",
          flush=True)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"run": main, "selftest": selftest}[cmd]())
