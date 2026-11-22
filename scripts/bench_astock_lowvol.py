"""Bench cell 3: A-share low-volatility -- the one A-share factor our own IC table likes.

Context
-------
The A-share composite book was judged negative (2026-10-25): 20-name concentration
plus 1.5-1.8x/year turnover ate the raw factor. The IC table from that work says
what was left: vol_20 -0.051, vol_60 -0.050, extreme_freq -0.050, ma_bias_60 -0.044,
mom_20 -0.036. Every one of those is the same story -- high volatility, stretched
and recently-hot names underperform. The composite tried to use all six at once in
20 names. This cell asks the narrower question: does the single cleanest factor
(low 60-day realized vol), held in a *wide* basket with a slow rebalance, survive
costs and an equal-weight control?

Construction (frozen before the run)
------------------------------------
universe   all per-symbol daily files with >= 400 bars, price > 1, median daily
           amount >= 20M CNY, and a valid 60d vol on that bar (point-in-time)
portfolio  bottom quintile of 60d annualised vol, equal weight, rebalance every
           20 bars, hold to the next rebalance
control    equal-weight the whole eligible universe on the same schedule
cost       10bp per side (commission + stamp), charged on notional traded
execution  signal from close t, fill at close t+1 (the cell's convention)

Criteria:
  H1  net annualised >= 4.0%
  H2  out-of-sample (2024+) net >= 3.0% and Sharpe >= 0.40
  H3  both halves of the sample positive
  H4  drop the best calendar year, still >= 1.5%/yr
  H5  excess over the equal-weight control >= 2.0%/yr with t >= 1.5
  GO only if all five pass. H5 is the one that matters: a low-vol basket that
  merely rides the market is not a line, it is beta in a nicer dress.

Known limits (disclosed)
  * survivorship: the panel holds today's listed names; delisted failures are
    absent, which flatters every long-only A-share test. The equal-weight control
    shares the same list, so the *excess* is the part less damaged by it.
  * no industry neutrality in this cell (the industry-neutral residual has its
    own face and its own one-year-story verdict).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

PER = os.path.join(bc.DATA, "astock_daily", "per")
CACHE = os.path.join(bc.DATA, "astock_daily", "_panel_cache_v1.parquet")
OUT_JSON = os.path.join(bc.RESULTS, "bench_astock_lowvol.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-ASTOCK-LOWVOL.md")

START = "2015-01-01"
MIN_BARS = 400
MIN_AMOUNT = 20_000_000.0
VOL_WINDOW = 60
REBALANCE = 20
COST_BP_SIDE = 10.0
QUANTILE = 0.20
SPLIT = "2024-01-01"

H1_PCT = 4.0
H2_PCT = 3.0
H2_SHARPE = 0.40
H4_PCT = 1.5
H5_EXCESS_PCT = 2.0
H5_T = 1.5


def build_cache(force=False):
    """Wide (date x symbol) close / amount matrices, cached as parquet."""
    if os.path.exists(CACHE) and not force:
        d = pd.read_parquet(CACHE)
        return d["close"], d["amount"]

    files = [f for f in os.listdir(PER) if f.endswith(".csv")]
    closes, amounts = [], []
    for i, f in enumerate(files):
        try:
            df = pd.read_csv(os.path.join(PER, f), usecols=["date", "close", "amount"])
        except Exception:
            continue
        if len(df) < MIN_BARS:
            continue
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] >= pd.Timestamp(START)]
        if len(df) < 100:
            continue
        s = df.set_index("date")
        sym = f[:-4]
        closes.append(s["close"].rename(sym))
        amounts.append(s["amount"].rename(sym))
        if (i + 1) % 1000 == 0:
            print(f"  ... {i + 1}/{len(files)} files", flush=True)

    close = pd.concat(closes, axis=1).sort_index()
    amount = pd.concat(amounts, axis=1).reindex(close.index)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    # one flat table (date, symbol, close, amount); pivot on read
    flat = close.stack().rename("close").to_frame()
    flat["amount"] = amount.stack()
    flat.reset_index().to_parquet(CACHE, index=False)
    return close, amount


def load_panel():
    if os.path.exists(CACHE):
        raw = pd.read_parquet(CACHE)
        close = raw.pivot(index="date", columns="level_1", values="close")
        amount = raw.pivot(index="date", columns="level_1", values="amount")
        close.index = pd.to_datetime(close.index)
        return close.sort_index(), amount.reindex(close.index)
    return build_cache()


def eligible_mask(close, amount):
    """Point-in-time eligibility: enough history, price, liquidity."""
    nbars = close.notna().cumsum()
    liq = amount.rolling(60, min_periods=20).median() >= MIN_AMOUNT
    return (nbars >= MIN_BARS) & (close > 1.0) & liq


def run():
    bc.weight_priority()
    close, amount = load_panel()
    close = close.sort_index()
    rets = close.pct_change(fill_method=None)
    vol60 = rets.rolling(VOL_WINDOW, min_periods=40).std() * np.sqrt(bc.TRADING_DAYS)
    ok = eligible_mask(close, amount) & vol60.notna()

    dates = close.index
    reb_dates = [i for i in range(VOL_WINDOW, len(dates)) if (i - VOL_WINDOW) % REBALANCE == 0]

    strat_r, ew_r, excess = [], [], []
    holdings = []
    prev_w = None
    prev_ew = None
    for k, i in enumerate(reb_dates):
        d = dates[i]
        mask = ok.loc[d]
        names = mask[mask].index
        if len(names) < 50:
            continue
        v = vol60.loc[d, names].sort_values()
        n_low = max(20, int(len(names) * QUANTILE))
        low = list(v.index[:n_low])

        w = pd.Series(1.0 / len(low), index=low)
        ew = pd.Series(1.0 / len(names), index=names)

        end = dates[reb_dates[k + 1]] if k + 1 < len(reb_dates) else dates[-1]
        fwd = rets.loc[(rets.index > d) & (rets.index <= end)]
        if fwd.empty:
            continue

        def period(pw, prev, universe):
            r = (fwd[universe] * pw).sum(axis=1, min_count=1)
            cost = 0.0
            if prev is not None:
                allk = pw.index.union(prev.index)
                turnover = (pw.reindex(allk, fill_value=0)
                            - prev.reindex(allk, fill_value=0)).abs().sum()
                cost = turnover * COST_BP_SIDE / 10000.0
            return r, cost

        r_strat, c_strat = period(w, prev_w, low)
        r_ew, c_ew = period(ew, prev_ew, names)
        strat_r.append((r_strat - c_strat / max(len(r_strat), 1)))
        ew_r.append((r_ew - c_ew / max(len(r_ew), 1)))
        excess.append(strat_r[-1] - ew_r[-1])
        holdings.append({"date": str(d.date()), "names": len(low),
                         "universe": len(names)})
        prev_w, prev_ew = w, ew

    if not strat_r:
        return {"ok": False, "error": "no rebalance period produced returns"}

    s = pd.concat(strat_r).sort_index()
    e = pd.concat(ew_r).sort_index()
    x = pd.concat(excess).sort_index()

    reading = bc.split_perf(s.values, s.index, split=SPLIT)
    reading_ew = bc.split_perf(e.values, e.index, split=SPLIT)
    xs = bc.perf(x.values, x.index)
    t_excess = xs["t_stat"]

    checks = {
        "H1_net_ge_4pct": bool(reading["full"]["ann_pct"] is not None
                               and reading["full"]["ann_pct"] >= H1_PCT),
        "H2_oos_ge_3pct_and_sr_ge_0.4": bool(
            reading["oos"]["ann_pct"] is not None
            and reading["oos"]["ann_pct"] >= H2_PCT
            and (reading["oos"]["sharpe"] or -9) >= H2_SHARPE),
        "H3_both_halves_positive": bool(
            reading.get("first_half_ann_pct") is not None
            and reading["first_half_ann_pct"] > 0
            and (reading.get("second_half_ann_pct") or -9) > 0),
        "H4_drop_best_year_ge_1.5pct": bool(
            reading["full"]["drop_best_year_ann_pct"] is not None
            and reading["full"]["drop_best_year_ann_pct"] >= H4_PCT),
        "H5_excess_ge_2pct_t_ge_1.5": bool(
            xs["ann_pct"] is not None and xs["ann_pct"] >= H5_EXCESS_PCT
            and (t_excess or -9) >= H5_T),
    }

    payload = {
        "cell": "astock_lowvol",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(dates[-1].date()),
        "coverage": {"symbols": int(close.shape[1]), "bars": int(len(dates)),
                     "start": str(dates[0].date()), "end": str(dates[-1].date()),
                     "rebalances": len(holdings),
                     "avg_names": round(float(np.mean([h["names"] for h in holdings])), 1)
                     if holdings else None},
        "criteria": {"H1_pct": H1_PCT, "H2_pct": H2_PCT, "H2_sharpe": H2_SHARPE,
                     "H4_pct": H4_PCT, "H5_excess_pct": H5_EXCESS_PCT, "H5_t": H5_T,
                     "split": SPLIT, "cost_bp_side": COST_BP_SIDE,
                     "rebalance_bars": REBALANCE, "quantile": QUANTILE,
                     "vol_window": VOL_WINDOW, "universe_min_amount": MIN_AMOUNT},
        "verdict": bc.verdict_of(checks),
        "checks": checks,
        "lowvol_book": {"common_window": reading["full"], "is_before_2024": reading["is"],
                        "oos_2024_after": reading["oos"],
                        "first_half_ann_pct": reading.get("first_half_ann_pct"),
                        "second_half_ann_pct": reading.get("second_half_ann_pct")},
        "equal_weight_control": {"common_window": reading_ew["full"],
                                 "oos_2024_after": reading_ew["oos"]},
        "excess_vs_ew": xs,
        "holdings_tail": holdings[-5:],
    }

    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, payload)

    f = reading["full"]
    o = reading["oos"]
    ewf = reading_ew["full"]
    md = [
        "# A股低波单因子试验（bench cell 3）", "",
        f"evidence cutoff {payload['evidence_cutoff']} | generated {payload['generated']} | "
        f"标的 {payload['coverage']['symbols']} 只 | bar {payload['coverage']['bars']} | "
        f"每次持仓约 {payload['coverage']['avg_names']} 只",
        "",
        f"**判决 {payload['verdict']}**",
        "",
        "| 项 | 年化 | 夏普 | 回撤 | 样本外年化 | 样本外夏普 |",
        "|---|---|---|---|---|---|",
        f"| 低波组合（净） | {bc.fmt_pct(f['ann_pct'])} | {bc.fmt_num(f['sharpe'])} | "
        f"{bc.fmt_pct(f['mdd_pct'])} | {bc.fmt_pct(o['ann_pct'])} | {bc.fmt_num(o['sharpe'])} |",
        f"| 同池等权（对照） | {bc.fmt_pct(ewf['ann_pct'])} | {bc.fmt_num(ewf['sharpe'])} | "
        f"{bc.fmt_pct(ewf['mdd_pct'])} | {bc.fmt_pct(reading_ew['oos']['ann_pct'])} | "
        f"{bc.fmt_num(reading_ew['oos']['sharpe'])} |",
        f"| 超额（低波−等权） | {bc.fmt_pct(xs['ann_pct'])} | — | {bc.fmt_pct(xs['mdd_pct'])} | "
        f"— | t={bc.fmt_num(xs['t_stat'])} |",
        "",
        f"逐年（低波，%）：{f['years']}",
        "",
        f"判据：{json.dumps(checks, ensure_ascii=False)}",
        "",
        "## 这次没有回答的问题", "",
        "- 生存者偏差：面板是现存标的，退市失败者不在内；等权对照共用同一张表，超额部分受影响较小。",
        "- 没有做行业中性（那是另一张面，且已被判 one-year story）。",
        "- 没有做市值分层：低波可能与大盘重叠，本格未拆。",
    ]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")

    print(json.dumps({"ok": True, "verdict": payload["verdict"], "checks": checks,
                      "full": f, "oos": o, "excess": xs,
                      "coverage": payload["coverage"]}, ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    if "--rebuild-cache" in sys.argv:
        build_cache(force=True)
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
