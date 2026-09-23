"""Turnover derivation probe (pure data engineering, zero inference).

MSG-20260923-1937 SS3: bars turnover column is all-NaN except the final
bar, while outstanding_share is complete; turnover = volume /
outstanding_share was verified exact on 000001/600519/300750. This probe
extends the check to the full 5,222-file universe and records provenance
for P-1c Stage-B (GTJA 033/062 revival) and B-layer liquidity fuel.

Data audit only: no IC computations, no engine runs, ledger N untouched.
The P-1c cache is NOT modified (loop-owned artifact; consumption decisions
belong to Stage-B's own prereg).

Checks (frozen in this script before the run):
  A. stored-vs-derived: where the stored turnover column is finite
     (expected: final bar only), |derived - stored|/|stored| <= 1e-6
  B. outstanding_share coverage per symbol (null fraction)
  C. derived coverage (finite rows) vs bar rows
  D. sanity: derived > 1.05 anomaly count (turnover vs total outstanding
     shares should not materially exceed 100%; recorded, not filtered)

Output: results/shortline/turnover_derivation.json
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
OUT_PATH = os.path.join(ROOT, "results", "shortline",
                        "turnover_derivation.json")
REL_TOL = 1e-6
ANOMALY_TURN = 1.05
WORKERS = 8  # gentle: P-B batch + loop round share the box (O-1738 80% cap)


def check_one(path):
    sym = os.path.basename(path)[:-8]
    try:
        df = pd.read_parquet(path, columns=["volume", "outstanding_share",
                                            "turnover"])
    except Exception as ex:
        return {"sym": sym, "status": "read_error", "err": type(ex).__name__}
    vol = df["volume"].to_numpy(float)
    osh = df["outstanding_share"].to_numpy(float)
    tur = df["turnover"].to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        derived = np.where(osh > 0, vol / osh, np.nan)
    stored_fin = np.isfinite(tur)
    der_fin = np.isfinite(derived)
    n_stored = int(stored_fin.sum())
    mism, max_rel = 0, 0.0
    if n_stored:
        rel = (np.abs(derived[stored_fin] - tur[stored_fin])
               / np.maximum(np.abs(tur[stored_fin]), 1e-12))
        max_rel = float(np.nanmax(rel))
        mism = int((rel > REL_TOL).sum())
    return {"sym": sym, "status": "ok", "rows": int(len(df)),
            "osh_null_frac": round(float(np.isnan(osh).mean()), 6),
            "stored_finite_rows": n_stored,
            "derived_finite_rows": int(der_fin.sum()),
            "stored_vs_derived_mismatch_rows": mism,
            "stored_vs_derived_max_rel": max_rel,
            "derived_gt_anomaly_rows": int((derived > ANOMALY_TURN).sum()),
            "derived_max": (float(np.nanmax(derived)) if der_fin.any()
                            else None)}


def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    print(f"universe files: {len(files)}", flush=True)
    recs = []
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, r in enumerate(ex.map(check_one, files, chunksize=32)):
            recs.append(r)
            if (i + 1) % 1000 == 0:
                print(f"  {i+1}/{len(files)} ({time.time()-t0:.0f}s)",
                      flush=True)
    ok = [r for r in recs if r["status"] == "ok"]
    errs = [r for r in recs if r["status"] != "ok"]
    mism_rows = sum(r["stored_vs_derived_mismatch_rows"] for r in ok)
    mism_syms = [r["sym"] for r in ok if r["stored_vs_derived_mismatch_rows"]]
    osh_null_max = max((r["osh_null_frac"] for r in ok), default=1.0)
    osh_null_mean = float(np.mean([r["osh_null_frac"] for r in ok])) if ok else 1.0
    anomaly_rows = sum(r["derived_gt_anomaly_rows"] for r in ok)
    anomaly_syms = [r["sym"] for r in ok if r["derived_gt_anomaly_rows"]][:20]
    derived_cov = (sum(r["derived_finite_rows"] for r in ok)
                   / max(1, sum(r["rows"] for r in ok)))
    verdict_pass = (not errs) and mism_rows == 0
    out = {
        "meta": {"batch": "turnover derivation probe (data audit)",
                 "note": "research/shortline/TURNOVER_DERIVATION.md",
                 "claim_rider": "MSG-20260923-1937 SS3",
                 "formula": "turnover = volume / outstanding_share",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "ledger_note": "pure data engineering: N untouched, zero "
                                "engine runs, zero IC computations"},
        "universe": {"files": len(files), "ok": len(ok),
                     "read_error": len(errs),
                     "read_error_syms": [e["sym"] for e in errs][:20]},
        "check_A_stored_vs_derived": {
            "tol": REL_TOL,
            "mismatch_rows": mism_rows,
            "mismatch_symbols": mism_syms[:20],
            "n_mismatch_symbols": len(mism_syms),
            "max_rel_dev": max((r["stored_vs_derived_max_rel"] for r in ok),
                               default=None)},
        "check_B_osh_coverage": {"max_null_frac": osh_null_max,
                                  "mean_null_frac": round(osh_null_mean, 6)},
        "check_C_derived_coverage": {"finite_rows_over_rows":
                                      round(derived_cov, 6)},
        "check_D_sanity": {"threshold": ANOMALY_TURN,
                           "rows_gt_threshold": anomaly_rows,
                           "example_symbols": anomaly_syms},
        "verdict": ("PASS" if verdict_pass else
                     "FAIL" if errs else "MISMATCH"),
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "workers": WORKERS, "cpu_cap_policy": "O-20260923-1738"},
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in
                      ("universe", "check_A_stored_vs_derived",
                       "check_B_osh_coverage", "check_C_derived_coverage",
                       "check_D_sanity", "verdict")}, ensure_ascii=False),
          flush=True)
    print(f"=== turnover derivation probe: {out['verdict']} "
          f"({time.time()-t0:.0f}s) ===", flush=True)
    sys.exit(0 if verdict_pass else 1)


if __name__ == "__main__":
    main()
