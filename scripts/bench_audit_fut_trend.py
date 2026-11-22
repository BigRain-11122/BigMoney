"""Independent re-derivation of the futures-trend verdict (bench audit, not a new cell).

Why
---
Four cells closed negative in one evening. A negative is only worth anything if
the code that produced it is right. This script re-implements the ma_cross arm
from scratch -- plain numpy loops, no pandas rolling, no shared helper -- and
compares the result to the published number. It also reports the data hygiene
that the roll treatment depends on, and what the answer would be if the roll
jumps were NOT removed (so a reader can see how much of the result is the roll
surgery).

It changes no face. Exit code 0 = reproduces within tolerance.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT = os.path.join(bc.RESULTS, "bench_audit_fut_trend.json")
PRODUCTS = bc.FUTURES
FAST, SLOW, VOLW, REBAL = 50, 200, 60, 5
COST_BP = 3.0
TOL_ANN_PP = 0.35      # agreement at 0.35pp/yr is far tighter than any decision


def load(code):
    p = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates("date").set_index("date").sort_index()
    return df[(df["close"] > 0) & df["close"].notna()]


def hygiene(raw):
    """Duplicates, non-positive prices, long gaps, roll count -- per product."""
    out = {}
    for code, df in raw.items():
        c = df["close"].values
        gaps = np.diff(df.index.values).astype("timedelta64[D]").astype(int)
        out[code] = {
            "bars": int(len(df)),
            "start": str(df.index[0].date()),
            "end": str(df.index[-1].date()),
            "zero_or_negative": int((c <= 0).sum()),
            "max_gap_days": int(gaps.max()) if len(gaps) else 0,
            "gaps_over_10d": int((gaps > 10).sum()),
        }
    return out


def adjusted(df, drop_rolls=True):
    """Roll-adjusted price and returns, in a plain loop (independent of bench_core)."""
    c = df["close"].values.astype(float)
    n = len(c)
    r = np.zeros(n)
    for i in range(1, n):
        r[i] = c[i] / c[i - 1] - 1.0
    med = float(np.median(np.abs(r[1:]))) if n > 2 else 0.0
    thr = max(8.0 * med, 0.005)
    rolls = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if abs(r[i]) >= thr:
            rolls[i] = drop_rolls
    r_adj = np.where(rolls, 0.0, r)
    price = np.ones(n)
    for i in range(1, n):
        price[i] = price[i - 1] * (1.0 + r_adj[i])
    return price, r_adj, rolls


def ma_cross_arm(raw, dates, drop_rolls=True, sizing="dynamic", long_only=False):
    """Weekly-rebalanced 50/200 MA cross, equal risk, 10% target, 3bp/side.

    sizing='dynamic' reproduces the published rule (budget per instrument =
    target / sqrt(number of instruments live on that bar)); sizing='fixed'
    divides by the full universe regardless of how many are live. The audit
    runs both, because the published magnitude depends on that choice.
    """
    prices, rets, rolls = {}, {}, {}
    for code, df in raw.items():
        price, r, roll = adjusted(df, drop_rolls=drop_rolls)
        s_price = pd.Series(price, index=df.index).reindex(dates)
        s_ret = pd.Series(r, index=df.index).reindex(dates)
        prices[code] = s_price.values
        rets[code] = s_ret.values
        rolls[code] = int(roll.sum())

    codes = list(raw)
    n_days = len(dates)
    pos = np.zeros((n_days, len(codes)))
    sig_ok = np.zeros((n_days, len(codes)), dtype=bool)
    vol_ann = np.full_like(pos, np.nan)
    for j, code in enumerate(codes):
        p, r = prices[code], rets[code]
        for i in range(SLOW, n_days):
            if not np.isfinite(p[i]) or not np.isfinite(p[i - SLOW]):
                continue
            fast = np.nanmean(p[i - FAST + 1:i + 1])
            slow = np.nanmean(p[i - SLOW + 1:i + 1])
            if not np.isfinite(fast) or not np.isfinite(slow):
                continue
            sig = 1.0 if long_only else (1.0 if fast > slow else -1.0)
            window = r[max(0, i - VOLW + 1):i + 1]
            window = window[np.isfinite(window)]
            if len(window) < 30:
                continue
            sd = float(np.std(window, ddof=1)) * math.sqrt(bc.TRADING_DAYS)
            if sd <= 0:
                continue
            vol_ann[i, j] = sd
            sig_ok[i, j] = True
            pos[i, j] = sig

    live = sig_ok.sum(axis=1)
    for i in range(n_days):
        denom = np.sqrt(live[i]) if sizing == "dynamic" else np.sqrt(len(codes))
        if not np.isfinite(denom) or denom <= 0:
            pos[i, :] = 0.0
            continue
        for j in range(len(codes)):
            if not sig_ok[i, j]:
                pos[i, j] = 0.0
            else:
                w = (0.10 / denom) / vol_ann[i, j]
                pos[i, j] = np.clip(pos[i, j] * w, -2.0, 2.0)

    held = np.full_like(pos, np.nan)
    last = np.zeros(pos.shape[1])
    for i in range(n_days):
        if i % REBAL == 0:
            last = pos[i]
        held[i] = last

    eq = []
    for i in range(1, n_days):
        r_today = np.array([rets[c][i] if np.isfinite(rets[c][i]) else 0.0 for c in codes])
        p_y = held[i - 1]
        pn = float(np.nansum(p_y * r_today))
        turn = float(np.nansum(np.abs(np.nan_to_num(held[i]) - np.nan_to_num(p_y))))
        pn -= turn * COST_BP / 10000.0
        eq.append(pn)
    eq = np.array(eq)
    years = len(eq) / bc.TRADING_DAYS
    total = float(np.cumprod(1.0 + eq)[-1])
    ann = (total ** (1.0 / years) - 1.0) * 100 if total > 0 else -100.0
    vol = float(np.std(eq, ddof=1)) * math.sqrt(bc.TRADING_DAYS) * 100
    sharpe = (float(np.mean(eq)) * bc.TRADING_DAYS) / (vol / 100) if vol > 0 else 0.0
    return {"ann_pct": round(ann, 3), "vol_pct": round(vol, 3),
            "sharpe": round(sharpe, 3), "years": round(years, 2),
            "rolls_removed": sum(rolls.values()), "series": eq,
            "avg_live": round(float(np.mean(live[live > 0])), 1) if (live > 0).any() else 0.0}


def main():
    raw = {c: load(c) for c in PRODUCTS if os.path.exists(os.path.join(bc.DATA, "futures_daily", c + ".csv"))}
    hyg = hygiene(raw)
    all_dates = sorted(set().union(*[set(df.index) for df in raw.values()]))
    dates = pd.DatetimeIndex(all_dates)

    with_adj = ma_cross_arm(raw, dates, drop_rolls=True)
    without = ma_cross_arm(raw, dates, drop_rolls=False)

    published = None
    p = os.path.join(bc.RESULTS, "bench_fut_trend.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        arm = next((a for a in d.get("arms", []) if a["style"] == "ma_cross"), None)
        if arm:
            published = {"ann_pct": arm["common_window"]["ann_pct"],
                         "sharpe": arm["common_window"]["sharpe"],
                         "verdict": arm["verdict"],
                         "window_start": d["coverage"].get("verdict_window_start"),
                         "hold_ann_pct": (d.get("benchmark_buy_and_hold") or {})
                         .get("common_window", {}).get("ann_pct"),
                         "hold_sharpe": (d.get("benchmark_buy_and_hold") or {})
                         .get("common_window", {}).get("sharpe")}
    # the published arm starts at the >=5-instrument window; recompute on it too
    if published and published.get("window_start"):
        start = pd.Timestamp(published["window_start"])
        sub = dates[dates >= start]
        sub_raw = {c: raw[c][raw[c].index >= start] for c in raw}
        with_adj_win = ma_cross_arm(sub_raw, sub, drop_rolls=True, sizing="dynamic")
        without_win = ma_cross_arm(sub_raw, sub, drop_rolls=False, sizing="dynamic")
        fixed_win = ma_cross_arm(sub_raw, sub, drop_rolls=True, sizing="fixed")
        hold_dyn = ma_cross_arm(sub_raw, sub, drop_rolls=True, sizing="dynamic", long_only=True)
        hold_fix = ma_cross_arm(sub_raw, sub, drop_rolls=True, sizing="fixed", long_only=True)
    else:
        with_adj_win, without_win, fixed_win = with_adj, without, with_adj
        hold_dyn = hold_fix = None

    diff = None
    ok = None
    if published:
        diff = round(with_adj_win["ann_pct"] - published["ann_pct"], 3)
        ok = abs(diff) <= TOL_ANN_PP

    sensitivity = None
    if hold_dyn and hold_fix:
        sensitivity = {
            "sizing_rule": "budget per instrument = target / sqrt(live count), vs target / sqrt(full universe)",
            "dynamic": {"ma_cross_ann_pct": with_adj_win["ann_pct"],
                        "hold_ann_pct": hold_dyn["ann_pct"],
                        "excess_pp": round(with_adj_win["ann_pct"] - hold_dyn["ann_pct"], 2),
                        "avg_live": with_adj_win["avg_live"]},
            "fixed": {"ma_cross_ann_pct": fixed_win["ann_pct"],
                      "hold_ann_pct": hold_fix["ann_pct"],
                      "excess_pp": round(fixed_win["ann_pct"] - hold_fix["ann_pct"], 2)},
            "reading": "if the excess over holding keeps its sign and rough size under both "
                       "sizing rules, the 'no second line' verdict does not depend on the rule",
        }

    payload = {
        "audit": "fut_trend_ma_cross_independent",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "method": "numpy loop re-implementation (no pandas rolling, no bench_core helpers)",
        "independent_full": {k: v for k, v in with_adj.items() if k != "series"},
        "independent_verdict_window": {k: v for k, v in with_adj_win.items() if k != "series"},
        "published": published,
        "diff_pp": diff,
        "reproduces_within_tolerance": ok,
        "tolerance_pp": TOL_ANN_PP,
        "sizing_sensitivity": sensitivity,
        "roll_treatment_impact": {
            "ann_with_rolls_removed_pct": with_adj_win["ann_pct"],
            "ann_with_rolls_kept_pct": without_win["ann_pct"],
            "delta_pp": round(without_win["ann_pct"] - with_adj_win["ann_pct"], 2),
            "reading": "a negative delta means the raw continuous series understates a trend book "
                       "(roll jumps hurt it); the published number is the one that removes them",
        },
        "data_hygiene": hyg,
        "verdict": ("REPRODUCED" if ok else ("MISMATCH" if ok is False else "NO_PUBLISHED_FACE")),
    }
    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT, payload)

    print(json.dumps({"verdict": payload["verdict"],
                      "independent_ann_pct": with_adj_win["ann_pct"],
                      "published_ann_pct": (published or {}).get("ann_pct"),
                      "diff_pp": diff,
                      "roll_impact_pp": payload["roll_treatment_impact"]["delta_pp"],
                      "rolls_removed": with_adj["rolls_removed"],
                      "hygiene_zero_prices": sum(h["zero_or_negative"] for h in hyg.values())},
                     ensure_ascii=False, indent=1))
    return 0 if payload["verdict"] in ("REPRODUCED", "NO_PUBLISHED_FACE") else 1


if __name__ == "__main__":
    sys.exit(main())
