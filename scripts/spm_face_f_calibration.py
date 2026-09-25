"""SPM face-(f) judgment-line calibration (T-53 slice-3).

Descriptive statistics over OFFICIAL index monthly series -- no strategy
signal, no tuning, no optimization target. Purpose: calibrate the frozen
rolling-6m/12m beat-rate lines (0.70) against external-reality investable
public benchmarks (face f, CALIBRATION EVIDENCE ONLY, line stays frozen).

Sources (all official, in-repo akshare 1.18.96):
  000300  CSI 300            -- sina index daily (ak.stock_zh_index_daily)
  000905  CSI 500            -- sina index daily
  H30269  CSI Dividend Low-Vol -- CSI official (ak.stock_zh_index_hist_csindex)
  H11001  CSI Aggregate Bond   -- CSI official (ak.stock_zh_index_hist_csindex)

Exit codes: 0 = written; 2 = source failure (honest, no partial write).
"""
import json
import sys

import akshare as ak
import numpy as np
import pandas as pd

OUT = "results/spm_face_f_calibration.json"
BENCH = "000300"


def _month_ends(df: pd.DataFrame, date_col: str, close_col: str) -> tuple:
    d = df.copy()
    d["d"] = pd.to_datetime(d[date_col])
    d = d.sort_values("d").set_index("d")[close_col]
    last_daily = d.index.max()
    me = d.resample("ME").last().dropna()
    # drop in-progress final month (partial month = not a completed observation)
    if len(me) and me.index[-1] >= last_daily.replace(day=1):
        me = me.iloc[:-1]
    return me, last_daily


def rolling_stats(ret: pd.Series, win: int) -> dict:
    roll = (1.0 + ret).rolling(win).apply(np.prod, raw=True) - 1.0
    roll = roll.dropna()
    return {
        "n_windows": int(len(roll)),
        "positive_rate": float((roll > 0).mean()),
        "mean_ret": float(roll.mean()),
        "worst_window": float(roll.min()),
        "best_window": float(roll.max()),
    }


def main() -> int:
    series = {}
    last_daily = None
    # -- sina-sourced exchange indices (reuse established in-repo channel)
    for sym, name in (("sh000300", "000300"), ("sh000905", "000905")):
        df = ak.stock_zh_index_daily(symbol=sym)
        df = df.reset_index() if df.index.name else df
        date_col = "date" if "date" in df.columns else df.columns[0]
        series[name], ld = _month_ends(df, date_col, "close")
        last_daily = max(last_daily or ld, ld)
    # -- CSI official H-indices
    for code in ("H30269", "H11001"):
        df = ak.stock_zh_index_hist_csindex(symbol=code, start_date="20050101", end_date="20260925")
        series[code], ld = _month_ends(df, "日期", "收盘")
        last_daily = max(last_daily or ld, ld)

    # align to common monthly calendar, inner join per pair vs bench
    monthly = pd.concat(
        {k: v for k, v in series.items()}, axis=1, join="inner"
    ).dropna(how="any")
    rets = monthly.pct_change().dropna()

    out = {
        "schema": "spm_face_f_calibration_v1",
        "purpose": "T-53 slice-3 face-(f) judgment-line calibration evidence (CALIBRATION ONLY, 0.70 lines frozen)",
        "method": "official index month-end closes -> monthly simple returns -> rolling 6m/12m compound windows; positive_rate = windows with return>0; beat_rate = windows beating CSI300 total return; descriptive stats, no signal, no tuning",
        "descriptive_calibration": True,
        "sample": {
            "first_month": str(monthly.index[0].date()),
            "last_complete_month": str(monthly.index[-1].date()),
            "n_months_common": int(len(monthly)),
            "last_daily_bar": str(last_daily.date()),
            "partial_final_month_dropped": True,
        },
        "evidence_cutoff": str(last_daily.date()),
        "indices": {},
        "windows": ["6m", "12m"],
        "note": "indices are investable public beta/factor benchmarks, not managed-futures fund series; SG-Trend/Barclay portal monthly channels probed dead this round (see digest sec9)",
    }

    for name in ("000300", "000905", "H30269", "H11001"):
        r = rets[name]
        ann = float((1.0 + r).prod() ** (12.0 / len(r)) - 1.0)
        vol = float(r.std() * np.sqrt(12))
        entry = {
            "months": int(len(r)),
            "annualized_return": round(ann, 4),
            "annual_vol": round(vol, 4),
            "naive_sharpe_no_rf": round(ann / vol, 3) if vol > 0 else None,
        }
        for win in (6, 12):
            entry[f"roll_{win}m"] = rolling_stats(r, win)
            rel = r - rets[BENCH]
            roll_rel = (1.0 + rel).rolling(win).apply(np.prod, raw=True) - 1.0
            roll_rel = roll_rel.dropna()
            entry[f"beat_{BENCH}_roll_{win}m"] = {
                "n_windows": int(len(roll_rel)),
                "beat_rate": float((roll_rel > 0).mean()),
            }
        out["indices"][name] = entry

    # scenario: dividend low-vol vs bench directly (single printed verdict line)
    h = out["indices"]["H30269"]
    print("H30269 6m positive", round(h["roll_6m"]["positive_rate"], 3),
          "| beat300 6m", round(h[f"beat_{BENCH}_roll_6m"]["beat_rate"], 3),
          "| 12m positive", round(h["roll_12m"]["positive_rate"], 3),
          "| beat300 12m", round(h[f"beat_{BENCH}_roll_12m"]["beat_rate"], 3))

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    json.load(open(OUT, encoding="utf-8"))
    print("written", OUT)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # honest source failure
        print("SOURCE-FAIL", type(exc).__name__, str(exc)[:200])
        sys.exit(2)
