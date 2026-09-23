"""Diagnostic probe: outstanding_share / volume semantics in bars parquet.

Follow-up to the turnover derivation probe (check A verdict = MISMATCH):
at the final bar (where stored turnover is finite) the implied denominator
implied = volume / stored_turnover is compared with outstanding_share.

Findings (2026-09-23, full 5,222-file universe, print-only run):
  - r1 = implied / osh ~= 1.0000 for 4,480 syms (all non-STAR boards):
    turnover = volume / osh is EXACT there.
  - r1 ~= 100.0 for 666 syms, ALL 688xxx (STAR board): the unit gap is in
    the VOLUME column (688 files: volume = 100x true shares; vwap anchor:
    amount/volume = close/100 on 688001/688008), NOT in osh (osh = true
    total shares; stored turnover = true shares / osh checks out).
  - r2 = osh_now / osh_252d median 1.0 (p1/p99 0.9996/1.0005): osh is
    time-stable per symbol.
  - derived > 1.05 anomaly rows are ALL post-2015 and all 688 = pure unit
    artifact, no bad data.

Corrected formula (see research/shortline/TURNOVER_DERIVATION.md):
  non-688: turnover = volume / osh
  688xxx: turnover = (volume / 100) / osh
Alert: any consumer of 688 volume or vwap (= amount/volume) fields must
apply the 100x correction (P-1c cache vwap column, stock panels,
volume-level cross-sectional factors).

Pure data diagnostic: no repo writes, no IC, ledger N untouched.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "Money02", "data", "bars")


def one(path):
    sym = os.path.basename(path)[:-8]
    try:
        df = pd.read_parquet(path, columns=["date", "volume",
                                            "outstanding_share", "turnover"])
    except Exception:
        return None
    df = df.sort_values("date")
    tur = df["turnover"].to_numpy(float)
    fin = np.isfinite(tur) & (np.abs(tur) > 1e-12)
    if not fin.any():
        return {"sym": sym, "ok": False}
    i = int(np.max(np.nonzero(fin)[0]))
    vol = float(df["volume"].to_numpy(float)[i])
    osh_now = float(df["outstanding_share"].to_numpy(float)[i])
    j = max(0, i - 252)
    osh_past = float(df["outstanding_share"].to_numpy(float)[j])
    implied = vol / tur[i]
    osh = df["outstanding_share"].to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        der = df["volume"].to_numpy(float) / osh
    d = df["date"].to_numpy()
    anom = np.isfinite(der) & (der > 1.05)
    early = anom & (d <= np.datetime64("2015-12-31"))
    return {"sym": sym, "ok": True,
            "r1": implied / osh_now if osh_now > 0 else np.nan,
            "r2": osh_now / osh_past if osh_past > 0 else np.nan,
            "anom_early": int(early.sum()),
            "anom_late": int(anom.sum() - early.sum())}


def main():
    files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
    recs = [r for r in (one(p) for p in files) if r and r.get("ok")]
    r1 = np.array([r["r1"] for r in recs])
    r2 = np.array([r["r2"] for r in recs])
    print("n_syms:", len(recs))
    print("r1 quantiles p1/p5/p25/p50/p75/p95/p99:",
          [round(float(np.nanquantile(r1, q)), 4)
           for q in (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99)])
    for lo, hi, tag in [(0.99, 1.01, "r1~1 (formula exact)"),
                         (99.0, 101.0, "r1~100 (688 volume x100)")]:
        print(f"  {tag}:", int(((r1 >= lo) & (r1 < hi)).sum()))
    by_prefix = {}
    for r in recs:
        by_prefix.setdefault(r["sym"][:3], []).append(r["r1"])
    med = {p: round(float(np.nanmedian(v)), 4) for p, v in by_prefix.items()
           if len(v) >= 50}
    print("r1 median by code prefix (n>=50):", dict(sorted(med.items())))
    print("r2 median:", round(float(np.nanmedian(r2)), 6),
          "p1/p99:", [round(float(np.nanquantile(r2, q)), 4)
                      for q in (0.01, 0.99)])
    print("anomaly rows early(<=2015):", sum(r["anom_early"] for r in recs),
          "late:", sum(r["anom_late"] for r in recs))


if __name__ == "__main__":
    sys.exit(main())
