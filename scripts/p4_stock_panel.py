"""P-4 batch 2a: stock panel + limit-up/mood factor batch (P4_STOCK_PANEL.md).

Pure data/factor build over MONEY02 bars (5222 parquet, dual-verified):
per-symbol daily limit-up detection (tiered by board %), streaks, distances,
plus market-level daily mood thermometer (aggregate across symbols).
Zero engine runs, zero forward-looking fields (all signals past-only).
Parallel: 25 workers (O-20260923-1738 80% cap).
Outputs: results/stock_mood_daily.csv + results/stock_factors_snapshot.parquet
"""
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

BARS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "Money02", "data", "bars")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results")


def classify_board(sym: str) -> float:
    if sym.startswith(("30", "68")):
        return 20.0
    return 10.0  # main boards (ST tier detected by 5% threshold)


def process_one(path: str):
    sym = os.path.basename(path)[:-8]
    try:
        df = pd.read_parquet(path, columns=["date", "open", "close", "high",
                                            "pct_chg", "preclose", "amount"])
    except Exception as ex:
        return sym, None, f"read_error: {type(ex).__name__}"
    if len(df) < 250:
        return sym, None, "short_history"
    df = df.sort_values("date").reset_index(drop=True)

    pct = df["pct_chg"]
    board = classify_board(sym)
    # tiered limit-up flags (past-only, uses same-day close facts)
    zt10 = (pct >= 9.85) & (pct <= 10.3)
    zt20 = (pct >= 19.7) & (pct <= 20.6)
    zt5 = (pct >= 4.85) & (pct <= 5.3)
    zt = zt10 | zt20 | zt5

    # streak length at each day (past-only running)
    grp = (~zt).cumsum()
    lb_height = zt.groupby(grp).cumsum()

    # zhanban proxy: touched limit intraday but closed below (approx via high)
    if board == 20.0:
        hi_pct = (df["high"] / df["preclose"] - 1) * 100
    else:
        hi_pct = (df["high"] / df["preclose"] - 1) * 100
    zhanban = ((hi_pct >= 9.7) | (hi_pct >= 19.5)) & ~zt

    # per-symbol factors (all past-looking)
    zt_count_60 = zt.rolling(60, min_periods=1).sum()
    days_since_zt = zt[::-1].cumsum()  # placeholder, replaced below
    # days since last zt (vectorized past-only)
    last_zt_idx = zt.cummax() * np.arange(1, len(zt) + 1)
    seen = np.where(zt.cummax().values == 0, np.nan, last_zt_idx)
    days_since = np.arange(1, len(zt) + 1) - seen
    bias20 = df["close"] / df["close"].shift(20) - 1
    zt_dist = 1 - pct / board
    nxt_open = df["open"].shift(-1)
    nxt_close = df["close"].shift(-1)
    prem_open = np.where(zt, (nxt_open / df["close"] - 1), np.nan)
    prem_close = np.where(zt, (nxt_close / df["close"] - 1), np.nan)
    # past-only 60d mean premium AFTER past limit-ups
    s_open = pd.Series(prem_open, index=df.index).shift(1)
    s_close = pd.Series(prem_close, index=df.index).shift(1)
    zt_ret_60_open = s_open.rolling(60, min_periods=1).mean()
    zt_ret_60_close = s_close.rolling(60, min_periods=1).mean()

    # market contributions (compact per-day frame)
    contrib = pd.DataFrame({
        "date": df["date"],
        "zt": zt.astype(np.int8),
        "zt5": zt5.astype(np.int8),
        "zt20": zt20.astype(np.int8),
        "zhanban": zhanban.astype(np.int8),
        "lb": lb_height.astype(np.float32),
    })

    # snapshot (latest row, past-only factors)
    i = len(df) - 1
    snap = {
        "sym": sym,
        "board": board,
        "last_date": str(df["date"].iloc[i].date()),
        "rows": len(df),
        "zt_count_60": float(zt_count_60.iloc[i]),
        "lb_height": float(lb_height.iloc[i]),
        "days_since_zt": float(days_since[i]) if np.isfinite(days_since[i]) else np.nan,
        "zt_dist": float(zt_dist.iloc[i]),
        "bias_extreme_20": float(bias20.iloc[i]),
        "zt_ret_60_open": float(zt_ret_60_open.iloc[i]),
        "zt_ret_60_close": float(zt_ret_60_close.iloc[i]),
        "amount_20d_mean": float(df["amount"].rolling(20, min_periods=1)
                                 .mean().iloc[i]),
    }
    return sym, (contrib, snap), "ok"


def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    print(f"universe files: {len(files)}")
    status = {"ok": 0, "short_history": 0, "read_error": 0}
    contribs, snaps = [], []
    with ProcessPoolExecutor(max_workers=25) as ex:
        for sym, payload, st in ex.map(process_one, files, chunksize=8):
            status[st] = status.get(st, 0) + 1
            if payload is not None:
                contribs.append(payload[0])
                snaps.append(payload[1])
            if (status["ok"] + status.get("short_history", 0)
                    + status.get("read_error", 0)) % 500 == 0:
                print(f"  ...{sum(status.values())} done ({time.time()-t0:.0f}s)")

    print(f"per-symbol pass done in {time.time()-t0:.0f}s | {status}")
    cat = pd.concat(contribs, ignore_index=True)
    g = cat.groupby("date")
    mood = pd.DataFrame({
        "zt_total": g["zt"].sum(),
        "zt5": g["zt5"].sum(),
        "zt20": g["zt20"].sum(),
        "zhanban": g["zhanban"].sum(),
        "lb_height_mean": g["lb"].mean(),
    }).reset_index()
    mood["mood_temp"] = (
        (mood["zt_total"] - mood["zt_total"].rolling(60, min_periods=60).mean())
        / (mood["zt_total"].rolling(60, min_periods=60).std() + 1e-9))
    mood.to_csv(os.path.join(OUT_DIR, "stock_mood_daily.csv"),
                index=False, encoding="utf-8")
    snap_df = pd.DataFrame(snaps)
    snap_df.to_parquet(os.path.join(OUT_DIR, "stock_factors_snapshot.parquet"))

    # sanity anchors (honest, recorded)
    m15 = mood[mood["date"].astype(str).str.startswith("2015-05")]
    peak = mood.loc[mood["zt_total"].idxmax()] if len(mood) else None

    out = {
        "batch": "P4-2a-stock-panel-mood",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "universe": {"files": len(files), **status},
        "rows_market_daily": len(mood),
        "sanity": {
            "zt_total_mean_recent_500d": round(float(
                mood["zt_total"].tail(500).mean()), 1),
            "peak_zt_total": None if peak is None else {
                "date": str(peak["date"]), "zt_total": int(peak["zt_total"])},
            "may2015_mean_zt": round(float(m15["zt_total"].mean()), 1)
            if len(m15) else None,
        },
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "workers": 25,
                  "cpu_cap_policy": "O-20260923-1738"},
    }
    with open(os.path.join(OUT_DIR, "stock_panel_mood.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
