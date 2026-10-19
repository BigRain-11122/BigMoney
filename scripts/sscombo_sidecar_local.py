#!/usr/bin/env python
"""Local qfq->raw factor sidecar face for the divlowvol sleeve (r1051 bm-b).

Why this file exists
  scripts/fund_divlowvol_p1.py imports its factor sidecars from
  Money02/data/bars/<sym>.factor.json, which does not exist on bm-b
  (Money02 is another machine's tree and is no-touch by law). Without a
  sidecar the frozen kernel skips every candidate (`if pack is None or
  sc is None: continue`), the pre-screen universe never reaches
  UNIVERSE_FLOOR=60 on any tail month, and _firing_months() fails closed
  with "no clean-tail t0" -- exactly the r1050 [BLOCKED] divlowvol face.

  Prereg research/FUND-STAGESTYLE-COMBO-P1.md sec.2c names the local rebuild
  road as the main one. This script materializes the missing input face
  locally, without touching any frozen kernel:

    f(t) = raw_price(t) / close_qfq(t), stepwise, f(latest) = 1.0

  reconstructed by inverting the standard multiplicative qfq adjustment
  against the in-repo dividend event face
  (data/fund_history_export/div_events_faces.parquet, T-154) walking the
  events BACKWARD from the panel's last price date:

      acc = 1.0
      for each ex-date e (descending):
          raw_prev = close_qfq(last trading day < e) * acc
          r        = 1 - cash_per_share(e) / raw_prev
          f(e)     = acc              # factor that applies from e onward
          acc      = acc * r          # factor that applies before e

  Emitted per symbol as {"d": ["YYYY-MM-DD", ...], "f": [...]} -- the exact
  shape fund_divlowvol_p1._load_sidecars expects, so sidecar_f_at and
  ttm_cash_sum stay single-source imports (zero re-implementation).

Honesty boundaries (declared, not silently absorbed)
  * Only cash dividends are modelled. Splits / rights issues are not in the
    div event face; a symbol whose implied ratio leaves (0.5, 1.0] is flagged
    in the index and counted in `flags` -- the yield face for those symbols
    is approximate.
  * Events with ex_date after the panel cutoff are skipped: a qfq series
    downloaded before the ex-date cannot yet reflect them.
  * f(t) is an identity inversion of a vendor adjustment, not an estimate:
    recovered raw prices are contemporaneous, so no look-ahead enters the
    yield (cash window is (t-365d, t], strictly past).
  * Sidecar absence still means "no adjustment events" downstream; this tool
    only writes files for codes that appear in the dividend face (5,124 in
    the T-154 export), matching the Money02 census.

Usage
    python scripts/sscombo_sidecar_local.py materialize [--force]
    python scripts/sscombo_sidecar_local.py status
    python scripts/sscombo_sidecar_local.py selftest

Exit codes: 0 normal, 2 mechanism fault, 3 precondition missing (panel or
dividend face not materialized -- honest no-op, not a pass).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_CACHE = os.path.join(ROOT, "data", "cache", "p1c_local")
SIDECAR_DIR = os.path.join(ROOT, "data", "cache", "p1c_sidecars")
DIV_PARQUET = os.path.join(ROOT, "data", "fund_history_export",
                           "div_events_faces.parquet")
INDEX_JSON = os.path.join(SIDECAR_DIR, "_index.json")

META_NAME = "meta.json"
RATIO_LO, RATIO_HI = 0.5, 1.0          # plausible per-event ratio band


# --------------------------------------------------------------------- inputs
def load_panel():
    meta_path = os.path.join(PANEL_CACHE, META_NAME)
    if not os.path.exists(meta_path):
        return None
    meta = json.load(open(meta_path, encoding="utf-8"))
    dates = np.load(os.path.join(PANEL_CACHE, "dates.npy"))
    idx = pd.to_datetime(np.asarray(dates).astype("datetime64[us]"))
    close = np.load(os.path.join(PANEL_CACHE, "close.npy"), mmap_mode="r")
    return idx, np.asarray(close), meta


def load_div_events():
    if not os.path.exists(DIV_PARQUET):
        return None
    df = pd.read_parquet(DIV_PARQUET)
    df = df.assign(code_s=df["code"].astype(str))
    df = df.assign(ex_int=df["ex_date"].astype("string")
                   .str.replace("-", "", regex=False).astype("int64"),
                   cps=df["cash_div_per_10"].astype("float64") / 10.0)
    # same-day multi-component rows SUM (T-154 export law)
    return (df.groupby(["code_s", "ex_int"], as_index=False)["cps"].sum())


# ------------------------------------------------------------------ kernel
def factor_face(dates_int: np.ndarray, close: np.ndarray, ex_int: np.ndarray,
                cps: np.ndarray) -> tuple:
    """Return (d_list, f_list, flags) for one symbol, ascending by date.

    dates_int: YYYYMMDD int64 axis of the panel; close: qfq closes on it
    (NaN where not listed); ex_int/cps: that symbol's dividend events.
    f_list[k] is the factor applying on [d_list[k], d_list[k+1]).
    """
    valid = np.isfinite(close) & (close > 0)
    if not valid.any() or len(ex_int) == 0:
        return [], [], []
    last_pos = int(np.where(valid)[0][-1])
    last_date = int(dates_int[last_pos])
    keep = ex_int <= last_date
    ex_int, cps = ex_int[keep], cps[keep]
    if len(ex_int) == 0:
        return [], [], []

    d_out, f_out, flags = [], [], []
    # acc = product of per-event ratios for events STRICTLY AFTER the current
    # one; qfq(t) = raw(t) * acc  =>  f(t) = raw/qfq = 1/acc on that segment.
    acc = 1.0
    for k in range(len(ex_int) - 1, -1, -1):
        e, c = int(ex_int[k]), float(cps[k])
        prev = int(np.searchsorted(dates_int, e, side="left")) - 1
        while prev >= 0 and not valid[prev]:
            prev -= 1
        if prev < 0:
            break                       # no quoted price before this event
        d_out.append(e)
        f_out.append(round(1.0 / acc, 8))
        if c <= 0:
            continue                    # zero-cash row: factor unchanged
        # qfq(prev) = raw(prev) * r_e * acc and r_e = 1 - c/raw(prev)
        # => raw(prev) = qfq(prev)/acc + c
        raw_prev = float(close[prev]) / acc + c
        if not np.isfinite(raw_prev) or raw_prev <= 0:
            flags.append(f"bad_raw@{e}:raw={raw_prev:.4f}")
            break
        r = 1.0 - c / raw_prev
        if r <= 0:
            flags.append(f"nonpositive_ratio@{e}:c={c:.4f},raw={raw_prev:.4f}")
            break
        if not (RATIO_LO < r <= RATIO_HI) and abs(r - 1.0) > 1e-12:
            flags.append(f"ratio_band@{e}:r={r:.6f}")
        acc *= r
    d_out.reverse()
    f_out.reverse()
    if d_out and acc < 1.0:
        # dates BEFORE the first event carry the full backward product; the
        # consumer (sidecar_f_at) floors to f_list[0], so anchor it explicitly
        # at the panel's first date.
        d_out.insert(0, int(dates_int[0]))
        f_out.insert(0, round(1.0 / acc, 8))
    return d_out, f_out, flags


# ---------------------------------------------------------------- commands
def cmd_materialize(args) -> int:
    panel = load_panel()
    if panel is None:
        print("panel cache missing -- run stagestyle_combo_p1_backtest.py "
              "materialize first")
        return 3
    idx, close, meta = panel
    ev = load_div_events()
    if ev is None:
        print(f"dividend face missing: {DIV_PARQUET}")
        return 3
    syms = sorted(os.path.basename(p)[:-4]
                  for p in glob.glob(os.path.join(ROOT, "data", "astock_daily",
                                                  "per", "*.csv")))
    if len(syms) != close.shape[1]:
        print(f"symbol axis drift: files={len(syms)} panel={close.shape[1]}")
        return 2
    dates_int = np.asarray(idx.strftime("%Y%m%d")).astype(np.int64)
    os.makedirs(SIDECAR_DIR, exist_ok=True)
    index_path = os.path.join(SIDECAR_DIR, "_index.json")
    if os.path.exists(index_path) and not args.force:
        doc = json.load(open(index_path, encoding="utf-8"))
        if doc.get("cutoff") == meta["cutoff"] and \
                doc.get("n_symbols") == len(syms):
            print(f"sidecars present: {doc['n_files']} files "
                  f"cutoff={doc['cutoff']} flags={doc['n_flagged']} "
                  f"(use --force to rebuild)")
            return 0

    sym_pos = {s: j for j, s in enumerate(syms)}
    n_files = 0
    n_events = 0
    flagged = {}
    missing = []
    for code, g in ev.groupby("code_s", sort=True):
        j = sym_pos.get(str(code))
        if j is None:
            missing.append(str(code))
            continue
        d_list, f_list, flags = factor_face(
            dates_int, np.asarray(close[:, j], dtype=np.float64),
            g["ex_int"].to_numpy(), g["cps"].to_numpy())
        if not d_list:
            continue
        payload = {
            "code": str(code),
            "d": [f"{x // 10000:04d}-{x // 100 % 100:02d}-{x % 100:02d}"
                  for x in d_list],
            "f": f_list,
            "method": "qfq-inversion-v1 (cash dividends only)",
            "cutoff": meta["cutoff"],
        }
        with open(os.path.join(SIDECAR_DIR, f"{code}.factor.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        n_files += 1
        n_events += len(d_list)
        if flags:
            flagged[str(code)] = flags
    doc = {
        "cutoff": meta["cutoff"],
        "n_symbols": len(syms),
        "n_files": n_files,
        "n_events": n_events,
        "n_flagged": len(flagged),
        "flags_sample": dict(list(flagged.items())[:20]),
        "missing_from_panel": missing[:20],
        "n_missing_from_panel": len(missing),
        "method": "qfq-inversion-v1",
        "source": ["data/fund_history_export/div_events_faces.parquet",
                   "data/cache/p1c_local (qfq close panel)"],
        "law": "f(latest)=1.0; events after panel cutoff skipped",
        "built_ts": pd.Timestamp.now().isoformat(),
    }
    with open(index_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"sidecars materialized: {n_files} files / {n_events} event steps "
          f"cutoff={doc['cutoff']} flagged={doc['n_flagged']} "
          f"missing_from_panel={doc['n_missing_from_panel']} -> {SIDECAR_DIR}")
    return 0


def cmd_status(args) -> int:
    index_path = os.path.join(SIDECAR_DIR, "_index.json")
    if not os.path.exists(index_path):
        print("sidecars: ABSENT (divlowvol sleeve will fail closed)")
        return 3
    doc = json.load(open(index_path, encoding="utf-8"))
    print(json.dumps({k: doc[k] for k in ("cutoff", "n_files", "n_events",
                                          "n_flagged", "n_missing_from_panel",
                                          "method", "built_ts")},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_selftest(args) -> int:
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # synthetic axis: 5 days, one event on day 3 paying 1.0 on a raw price
    # of 11.0 (qfq before the ex-date is 10.0 because r = 10/11)
    dates = np.array([20200101, 20200102, 20200103, 20200106, 20200107])
    close = np.array([10.0, 10.0, 9.0, 9.0, 9.0])
    d, f, flags = factor_face(dates, close, np.array([20200103]),
                              np.array([1.0]))
    check("T1_shape", d == [20200101, 20200103] and len(f) == 2,
          f"d={d} f={f}")
    check("T2_pre_event_factor", abs(f[0] - 11.0 / 10.0) < 1e-8
          and abs(f[1] - 1.0) < 1e-12, f"f={f}")
    # recovered raw price on the last day before the ex-date must be 11.0
    check("T2b_raw_recovery", abs(close[1] * f[0] - 11.0) < 1e-6,
          f"raw={close[1] * f[0]:.6f} want=11.0")

    # two events: the factor must fall monotonically toward 1.0 as time
    # advances (f = raw/qfq), and every step must be >= 1.0
    dates2 = np.array([20200101, 20200102, 20200103, 20200106, 20200107,
                       20200108, 20200109])
    close2 = np.array([10.0, 10.0, 9.0, 9.0, 8.0, 8.0, 8.0])
    d2, f2, _ = factor_face(dates2, close2, np.array([20200103, 20200108]),
                            np.array([1.0, 0.8]))
    check("T3_monotone_forward", len(f2) == 3
          and all(f2[i] >= f2[i + 1] - 1e-12 for i in range(len(f2) - 1))
          and abs(f2[-1] - 1.0) < 1e-12 and min(f2) >= 1.0 - 1e-12,
          f"d={d2} f={f2}")

    # no events -> empty face (sidecar_f_at then returns 1.0 everywhere)
    d3, f3, _ = factor_face(dates, close, np.array([], dtype=np.int64),
                            np.array([]))
    check("T4_empty_face", d3 == [] and f3 == [], f"d={d3}")

    # events after the panel cutoff are skipped (PIT: qfq cannot reflect them)
    d4, f4, _ = factor_face(dates, close, np.array([20200109]),
                            np.array([1.0]))
    check("T5_future_event_skipped", d4 == [], f"d={d4}")

    # NaN holes: the pre-event search must walk to the last quoted day
    close5 = np.array([10.0, np.nan, 9.0, 9.0, 9.0])
    d5, f5, _ = factor_face(dates, close5, np.array([20200103]),
                            np.array([1.0]))
    check("T6_nan_walk_back", len(d5) == 2 and abs(f5[0] - 1.1) < 1e-8
          and abs(f5[-1] - 1.0) < 1e-12, f"d={d5} f={f5}")

    # zero-cash rows never change the factor
    d6, f6, _ = factor_face(dates, close, np.array([20200103]),
                            np.array([0.0]))
    check("T7_zero_cash", len(d6) == 1 and abs(f6[0] - 1.0) < 1e-12,
          f"f={f6}")

    # materialized face (if any) must be monotone per file and end at 1.0
    files = sorted(glob.glob(os.path.join(SIDECAR_DIR, "*.factor.json")))
    sample = files[:200]
    mono_ok, end_ok = True, True
    for p in sample:
        sd = json.load(open(p, encoding="utf-8"))
        fv = sd["f"]
        if len(fv) >= 2 and any(fv[i] < fv[i + 1] - 1e-9
                                for i in range(len(fv) - 1)):
            mono_ok = False
        if fv and abs(fv[-1] - 1.0) > 1e-9:
            end_ok = False
    check("T8_disk_monotone", mono_ok, f"sample={len(sample)}")
    check("T9_disk_ends_at_one", end_ok, f"sample={len(sample)}")

    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    print(f"selftest: {len(checks) - len(bad)}/{len(checks)} PASS")
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("materialize")
    m.add_argument("--force", action="store_true")
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    return {"materialize": cmd_materialize, "status": cmd_status,
            "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())