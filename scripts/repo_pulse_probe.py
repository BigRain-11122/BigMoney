"""REPO term-ladder rate pulse detector (T11, P2 tech queue, pure
measurement -- ZERO backtest, ZERO strategy claims, no engine touch).

Why: GC001 pre-holiday spikes are an in-repo empirical fact (research/
shortline/REPO_PANEL.md: 2015-02-10 GC001 53.44% true pre-Spring-Festival
cash squeeze). This probe measures the PULSE STRUCTURE of the panel:
which days are pulses, how they align with month-end / long-holiday-eve
/ quarter-end calendar faces, and conditional frequencies. Descriptive
statistics only -- any strategy face is out of scope (T-67 style
freeze discipline: measurement first, prereg later, if ever).

Data face: data/repo_daily/GC001.csv (columns date,open,high,low,
close,volume; close = annualized %; 15:30 collect law, sina same-source,
update_repo.py owned). This script never writes the panel.

Pulse definition (frozen here, not tuned on outcomes):
  - robust z vs trailing 20-obs baseline: z = (close - med20) /
    (1.4826 * MAD20); pulse if z >= 5.0
  - absolute tiers: T1 >= 10% annualized, T2 >= 20% (extreme squeeze)
  - a day qualifies as PULSE if (z >= 5.0) OR close >= 10.0

Calendar faces (from the panel's own trading calendar):
  - month_end_win: within last 3 calendar days of the month
  - quarter_end: last trading day of Mar/Jun/Sep/Dec
  - pre_long_holiday: gap to next trading day >= 3 calendar days
    (Spring Festival / National Day eves)
  - pre_weekend: Friday (next trading day >= 2 calendar days away)

Usage:
    python scripts/repo_pulse_probe.py            # measure -> results/repo_pulse_probe.json
    python scripts/repo_pulse_probe.py selftest   # offline synthetic guard

Exit codes: 0 ok | 2 mechanism error (panel missing / malformed).
"""
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

PANEL = os.path.join(PATHS.data_dir, "repo_daily", "GC001.csv")
OUT = os.path.join(PATHS.results_dir, "repo_pulse_probe.json")
BASE_WIN = 20          # trailing baseline window (obs before current day)
Z_PULSE = 5.0          # robust z pulse line (frozen, not tuned)
ABS_T1 = 10.0          # annualized % absolute tier-1
ABS_T2 = 20.0          # annualized % absolute tier-2
ME_WIN_DAYS = 3        # last-N-calendar-days-of-month window
LONG_HOL_GAP = 3       # calendar-day gap to next bar = long-holiday eve


def load_panel(path=PANEL):
    df = pd.read_csv(path)
    need = {"date", "close"}
    if not need.issubset(df.columns):
        raise RuntimeError(f"panel columns {list(df.columns)} lack {need}")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    if df["close"].isna().any():
        raise RuntimeError("panel close has NaN rows")
    return df


def annotate(df):
    """Calendar faces per row, derived from the panel's own calendar
    (no external holiday tables -- gap-based inference only)."""
    dates = df["date"]            # datetime64 dtype: keep for .dt math
    nxt = dates.shift(-1)
    df["gap_next"] = (nxt - dates).dt.days
    df["gap_prev"] = (dates - dates.shift(1)).dt.days
    df["pre_long_holiday"] = (df["gap_next"] >= LONG_HOL_GAP)
    df["pre_weekend"] = (df["gap_next"] >= 2)
    # month-end window: last ME_WIN_DAYS calendar days of the month
    dim = dates.dt.days_in_month
    df["month_end_win"] = dates.dt.day > (dim - ME_WIN_DAYS)
    df["quarter_end"] = (
        df["month_end_win"]
        & dates.dt.month.isin([3, 6, 9, 12])
        & (dates.dt.day + ME_WIN_DAYS >= dim)
    )
    # trailing robust baseline (previous BASE_WIN obs, current excluded):
    # single-pass sliding window -- a naive double-rolling MAD defers the
    # first valid z to 2*BASE_WIN-1 (first-attempt selftest red)
    arr = df["close"].to_numpy(dtype=float)
    med = pd.Series(arr).shift(1).rolling(BASE_WIN).median().to_numpy()
    mad = np.full(len(arr), np.nan)
    for p in range(BASE_WIN, len(arr)):
        w = arr[p - BASE_WIN:p]
        m = np.median(w)
        mad[p] = np.median(np.abs(w - m))
    scale = 1.4826 * mad
    with np.errstate(invalid="ignore", divide="ignore"):
        df["z"] = (arr - med) / scale   # NaN z (warmup rows) -> pulse_z False
    df["pulse_z"] = df["z"] >= Z_PULSE
    df["pulse_abs_t1"] = df["close"] >= ABS_T1
    df["pulse_abs_t2"] = df["close"] >= ABS_T2
    df["pulse"] = df["pulse_z"] | df["pulse_abs_t1"]
    return df


def cond_rate(df, mask):
    n = int(mask.sum())
    if n == 0:
        return {"n": 0, "rate": None}
    return {"n": n, "rate": round(float(df.loc[mask, "pulse"].mean()), 6)}


def measure(df):
    total = int(len(df))
    pulses = df[df["pulse"]]
    other = ~df["month_end_win"]
    pre_lh = df["pre_long_holiday"]
    qe = df["quarter_end"]
    top = pulses.sort_values("close", ascending=False).head(10)
    top_rows = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "close_pct": round(float(c), 3),
            "z": (round(float(z), 2) if pd.notna(z) else None),
            "month_end_win": bool(m),
            "quarter_end": bool(q),
            "pre_long_holiday": bool(h),
            "pre_weekend": bool(w),
        }
        for d, c, z, m, q, h, w in zip(
            top["date"], top["close"], top["z"], top["month_end_win"],
            top["quarter_end"], top["pre_long_holiday"], top["pre_weekend"])
    ]
    return {
        "panel": "GC001",
        "rows": total,
        "date_min": df["date"].min().strftime("%Y-%m-%d"),
        "date_max": df["date"].max().strftime("%Y-%m-%d"),
        "pulse_total": int(df["pulse"].sum()),
        "pulse_abs_t1": int(df["pulse_abs_t1"].sum()),
        "pulse_abs_t2": int(df["pulse_abs_t2"].sum()),
        "cond": {
            "month_end_win": cond_rate(df, df["month_end_win"]),
            "non_month_end": cond_rate(df, other),
            "pre_long_holiday": cond_rate(df, pre_lh),
            "quarter_end": cond_rate(df, qe),
            "pre_weekend": cond_rate(df, df["pre_weekend"]),
        },
        "top10_by_close": top_rows,
        "claim": ("pure measurement only: descriptive pulse frequencies; "
                  "no backtest, no strategy, no PnL, no admission face"),
    }


def run():
    df = annotate(load_panel())
    res = measure(df)
    res["generated"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in
                      ("panel", "rows", "pulse_total", "pulse_abs_t1",
                       "pulse_abs_t2", "cond")}, ensure_ascii=False, indent=1))
    print(f"[repo_pulse_probe] saved {OUT}")
    return 0


def selftest():
    """Offline synthetic guard: flat 2.0% baseline, one 50% squeeze on a
    long-holiday eve inside the month-end window -> must flag pulse with
    all three calendar faces, and a flat tail day must NOT flag."""
    base = [2.0 + 0.01 * (i % 5) for i in range(BASE_WIN + 8)]
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-02", periods=len(base), freq="D"),
        "close": base,
    })
    # carve a month-end + long-holiday-eve squeeze day (index BASE_WIN+2)
    d = df["date"].iloc[BASE_WIN + 2]
    df.loc[df.index[BASE_WIN + 2], "date"] = d.replace(day=30)
    df.loc[df.index[BASE_WIN + 2], "close"] = 50.0
    # next bar jumps 5 calendar days ahead -> pre_long_holiday for squeeze day
    df.loc[df.index[BASE_WIN + 3], "date"] = (
        df["date"].iloc[BASE_WIN + 2] + pd.Timedelta(days=5))
    df = df.sort_values("date").reset_index(drop=True)
    a = annotate(df)
    sq = a[(a["close"] == 50.0)].iloc[0]
    assert bool(sq["pulse"]) and bool(sq["pulse_abs_t1"]) \
        and bool(sq["pulse_abs_t2"]), "squeeze day must flag pulse tiers"
    assert bool(sq["z"] >= Z_PULSE), "squeeze day robust z must pass line"
    assert bool(sq["month_end_win"]), "day-28 must be in month-end window"
    assert bool(sq["pre_long_holiday"]), "5-day gap must flag long-holiday eve"
    flat = a[(a["close"] < 3.0) & (a["close"] > 1.0)]
    assert not bool(flat["pulse"].any()), "flat days must not flag"
    assert len(measure(a)["top10_by_close"]) >= 1, "top table must list squeeze"
    print("[repo_pulse_probe] selftest PASS "
          "(pulse tiers + calendar faces + flat-reject)")
    return 0


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        try:
            return run()
        except (OSError, RuntimeError, ValueError) as e:
            print(f"[repo_pulse_probe] FAIL: {e}")
            return 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
