"""zoo #94 lhb_inst_dist_timing -- judged verdict on the data face that actually exists.

The berth (`research/shortline/ASTYLE_ZOO.md` #94) froze its parameterisation on
2026-09-26 (bm-b r218, digest `DIGEST-20260926-zoo-paramfreeze-92-94.md` §四):
IS_NetBuy = the sum over institutional seats of (buy - sell) per day, normalised by
CSI300 turnover, then HMA(30)/HMA(100) dual trend: long 0.9 when the two lines agree in
direction outside zero, flat in the middle ("做空中间" is the report's narrative, not the
implementation).

Its own registry row carries a data precondition -- "LHB 席位明细是否含机构席位逐席买卖
金额 (akshare LHB 席位明细族·若仅汇总面=数据面缺位如实降级)". That check is the first
thing this run does, and it fails: `Money02/data/lhb/lhb_detail.parquet` (268,044 rows,
2007-01-04..2026-11-06) is the aggregate list face -- one row per (stock, date, reason)
with 龙虎榜净买额 / 买入额 / 卖出额, and no seat column at all. The institutional-seat
rule cannot be computed from what is on disk.

So this run prices the HONEST DOWNGRADE the registry permits: the numerator is every
seat's net buy (龙虎榜净买额) instead of the institutional subset. It is a different
quantity -- the frozen rule stays untested -- and the face says so in `frozen_rule` and
`verdict_scope` rather than pretending the substitution is neutral.

Three further deviations, all declared in the face:

  1. daily series: rows are de-duplicated on (代码, 上榜日) -- the panel repeats a stock
     per 上榜原因 -- then summed across stocks. A trading day with no LHB events is 0
     net buy (not "unknown"), because a day without a list is a day the exchange
     published no seat activity.
  2. normaliser: the CSI300 turnover series is not in the repo, so the primary leg
     divides by the traded value of the instrument this book actually holds
     (sh510300 amount). Since the signal is sign + ordering of two HMAs, a positive
     constant divisor changes nothing; a time-varying one does, so the raw (un-normalised)
     leg is published beside it.
  3. the book's long weight is the berth's 0.9, so buy-and-hold for comparison is a
     same-convention 1.0 benchmark; the difference in exposure is printed, never tuned.

Execution: signal from bar t's close, weight applied from open t+1, cost 13.041bp per side
on the traded weight, marks to close (the shared curve in zoo96 -- one implementation).
The null is 200 circular phase shifts of the state series against the same bars.

Usage:
  python scripts/zoo94_lhb_inst_dist_probe.py            # run + publish
  python scripts/zoo94_lhb_inst_dist_probe.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from zoo96_volume_regime_probe import (  # noqa: E402  (one curve/stats/null/nulls)
    COST_PER_SIDE,
    COST_X3,
    curve,
    hma,
    null_test,
    stats,
)

OUT = os.path.join(ROOT, "results", "supply_berth", "zoo94_lhb_inst_dist_probe.json")
INDEX_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
LHB_PARQUET = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")

FAST = 30           # frozen: HMA(30)
SLOW = 100          # frozen: HMA(100)
LONG_W = 0.9        # frozen: target position 0.9
DRAWS = 200
SEED = 0

CRITERIA = {
    "call": "does the LHB net-buy dual-HMA state time 510300 after cost?",
    "passes": {
        "net_excess": "net CAGR minus the benchmark's > 0",
        "beats_null": "the phase-null p (share of shifts that match or beat it) < 0.05",
        "drawdown": "max drawdown not worse than the benchmark's",
        "exposure": "long share reported, never tuned",
    },
    "verdicts": ["ADOPT_AS_CANDIDATE", "REFUSE_AS_CANDIDATE",
                 "UNDECIDABLE_NULL_THIN", "INSUFFICIENT_BARS"],
    "thresholds": {"fast": FAST, "slow": SLOW, "long_weight": LONG_W},
    "cost": {"per_side": COST_PER_SIDE, "x3_robustness": COST_X3},
    "execution": "signal at close t, weight from open t+1, mark to close",
}

FROZEN_RULE = (
    "institutional seats' (buy - sell) summed per day / CSI300 turnover, HMA(30) vs "
    "HMA(100), long 0.9 on agreement outside zero, flat in the middle"
)
TESTED_RULE = (
    "all-seat net buy (龙虎榜净买额) summed per day after de-duplicating (代码, 上榜日) / "
    "sh510300 traded value, HMA(30) vs HMA(100), long 0.9 on agreement outside zero, "
    "flat in the middle"
)


# --------------------------------------------------------------------------- #
# the signal source
# --------------------------------------------------------------------------- #
def daily_net_buy(path: str = LHB_PARQUET, stats: dict | None = None):
    """(dates, net buy per date) from the aggregate LHB list face.

    The panel repeats a stock once per 上榜原因, and those rows are NOT interchangeable:
    a "连续三个交易日" row reports a multi-day cumulative net buy while a same-day reason
    reports that day's. The de-dup therefore prefers a same-day reason; when a stock-day
    only has cumulative-window rows, its cumulative reading is kept (losing 45k events
    would cost more than the level distortion it brings -- the count is published).

    Among same-day reasons the values agree in 183,228 of 183,918 stock-days; the 690
    that disagree are averaged rather than first-picked, because "first" would let the
    panel's row order decide a published number.
    """
    import pandas as pd

    df = pd.read_parquet(path, columns=["代码", "上榜日", "上榜原因", "龙虎榜净买额"])
    df["龙虎榜净买额"] = pd.to_numeric(df["龙虎榜净买额"], errors="coerce")
    df = df[np.isfinite(df["龙虎榜净买额"])]
    df["cumulative"] = df["上榜原因"].astype(str).str.contains("连续")
    same_day = df[~df["cumulative"]]
    cum_only = df[df["cumulative"]]

    picked = same_day.groupby(["代码", "上榜日"], as_index=False)["龙虎榜净买额"].mean()
    have = set(map(tuple, picked[["代码", "上榜日"]].to_numpy().tolist()))
    cum_only = cum_only.loc[[tuple(k) not in have for k in
                             cum_only[["代码", "上榜日"]].to_numpy().tolist()]]
    cum_pick = cum_only.groupby(["代码", "上榜日"], as_index=False)["龙虎榜净买额"].max()
    merged = pd.concat([picked, cum_pick], ignore_index=True)
    per_day = merged.groupby("上榜日")["龙虎榜净买额"].sum().sort_index()

    if stats is not None:
        dup = same_day.groupby(["代码", "上榜日"])["龙虎榜净买额"].nunique()
        stats.update({
            "lhb_rows": int(len(df)),
            "cumulative_rows": int(df["cumulative"].sum()),
            "same_day_stock_days": int(len(dup)),
            "same_day_disagreeing_stock_days": int((dup > 1).sum()),
            "cumulative_only_stock_days": int(len(cum_pick)),
        })
    dates = [str(d) for d in per_day.index.tolist()]
    return dates, per_day.to_numpy(dtype=np.float64)


def align(dates_signal, values, dates_index):
    """Signal days -> index bars; a bar with no event that day is 0 net buy."""
    pos = {d: i for i, d in enumerate(dates_signal)}
    out = np.zeros(len(dates_index), dtype=np.float64)
    hit = np.zeros(len(dates_index), dtype=bool)
    for i, d in enumerate(dates_index):
        j = pos.get(d)
        if j is not None:
            out[i] = values[j]
            hit[i] = True
    return out, hit


def normalise(net: np.ndarray, amount: np.ndarray) -> np.ndarray:
    """Net buy per yuan traded; NaN where the denominator is unusable."""
    a = np.asarray(amount, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = net / a
    out[~np.isfinite(out)] = np.nan
    return out


def state_of(fast: np.ndarray, slow: np.ndarray, weight: float = LONG_W) -> np.ndarray:
    """Berth rule: long when the two HMAs agree in direction outside zero, else flat.

    NaN on either line stays NaN (no state without a reading).
    """
    f = np.asarray(fast, dtype=np.float64)
    s = np.asarray(slow, dtype=np.float64)
    st = np.full(f.shape, np.nan)
    ok = np.isfinite(f) & np.isfinite(s)
    cond = ((f > s) & (f > 0) & (s > 0)) | ((f < s) & (f < 0) & (s < 0))
    st[ok] = 0.0
    st[ok & cond] = float(weight)
    return st


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
def _index() -> "object":
    import pandas as pd

    df = pd.read_csv(INDEX_CSV, dtype={"date": str})
    df = df[["date", "open", "close", "amount"]].dropna(subset=["date", "open", "close"])
    df = df[(df["open"] > 0) & (df["close"] > 0)]
    return df.reset_index(drop=True)


def run() -> dict:
    t0 = time.time()
    ix = _index()
    dates = ix["date"].tolist()
    openp = ix["open"].to_numpy(dtype=np.float64)
    close = ix["close"].to_numpy(dtype=np.float64)
    amount = ix["amount"].to_numpy(dtype=np.float64)
    dts = np.array([np.datetime64(d) for d in dates])

    sig_dates, sig_vals = daily_net_buy()
    dedup_stats: dict = {}
    sig_dates, sig_vals = daily_net_buy(stats=dedup_stats)
    net, hit = align(sig_dates, sig_vals, dates)
    nz = normalise(net, amount)
    hma_net_f, hma_net_s = hma(net, FAST), hma(net, SLOW)
    hma_nz_f, hma_nz_s = hma(nz, FAST), hma(nz, SLOW)
    st_nz = state_of(hma_nz_f, hma_nz_s)
    st_raw = state_of(hma_net_f, hma_net_s)

    arms = {}
    for name, st in (("normalised", st_nz), ("raw", st_raw)):
        lv = curve(dts, openp, close, st)
        arms[name] = stats(lv, dts)
        finite = np.where(np.isfinite(st))[0]
        arms[name]["bars"] = int(len(finite))
        arms[name]["long_share"] = round(float(np.nanmean(st[finite]) / LONG_W), 4) \
            if len(finite) else None
        arms[name]["mean_weight"] = round(float(np.nanmean(st[finite])), 4) if len(finite) else None
        sw = int(np.sum(np.diff(st[finite]) != 0)) if len(finite) > 1 else 0
        yrs = max(arms[name].get("years") or 1e-9, 1e-9)
        arms[name]["switches"] = sw
        arms[name]["switches_per_year"] = round(sw / yrs, 2)
        arms[name]["first_bar"] = str(dates[int(finite[0])]) if len(finite) else None
    bench_lv = curve(dts, openp, close, np.ones(len(dts)), 0.0)
    bench = stats(bench_lv, dts)
    excess_nz = float(arms["normalised"]["cagr"] - bench["cagr"])
    excess_raw = float(arms["raw"]["cagr"] - bench["cagr"])
    null_nz = null_test(dts, openp, close, st_nz, excess_nz)
    null_raw = null_test(dts, openp, close, st_raw, excess_raw)
    arms["normalised_cost_x3"] = stats(curve(dts, openp, close, st_nz, COST_X3), dts)
    arms["raw_cost_x3"] = stats(curve(dts, openp, close, st_raw, COST_X3), dts)

    reasons = []
    if arms["normalised"].get("bars", 0) < 250:
        verdict = "INSUFFICIENT_BARS"
        reasons.append("fewer than 250 traded bars")
    else:
        if not (excess_nz > 0):
            reasons.append("net excess %+.2fpp/yr is not positive" % (100 * excess_nz))
        if null_nz.get("p_value") is None or null_nz.get("p_value") >= 0.05:
            reasons.append("phase null p=%s does not beat 5%%" % null_nz.get("p_value"))
        if arms["normalised"]["maxdd"] < bench["maxdd"]:
            reasons.append("max drawdown %.2f%% is worse than buy-and-hold %.2f%%"
                           % (100 * arms["normalised"]["maxdd"], 100 * bench["maxdd"]))
        verdict = "REFUSE_AS_CANDIDATE" if reasons else "ADOPT_AS_CANDIDATE"
        if verdict == "ADOPT_AS_CANDIDATE" and \
                arms["normalised_cost_x3"]["cagr"] < bench["cagr"]:
            verdict = "REFUSE_AS_CANDIDATE"
            reasons.append("the x3-cost leg already gives back the whole excess")
        if np.sign(excess_nz) != np.sign(excess_raw):
            reasons.append(
                "the two honest normalisations disagree in sign (per-yuan %+.2fpp/yr "
                "p=%s vs raw %+.2fpp/yr p=%s), so the normaliser is an open question"
                % (100 * excess_nz, null_nz.get("p_value"), 100 * excess_raw,
                   null_raw.get("p_value")))

    doc = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": "scripts/zoo94_lhb_inst_dist_probe.py",
        "berth": "zoo #94 lhb_inst_dist_timing (frozen bm-b r218)",
        "evidence_cutoff": str(dates[-1]),
        "criteria": CRITERIA,
        "frozen_rule": FROZEN_RULE,
        "tested_rule": TESTED_RULE,
        "verdict_scope": (
            "the tested rule, not the frozen one: the institutional-seat numerator is "
            "absent from the in-repo LHB face, so this verdict says nothing about the "
            "frozen institutional-only variant"),
        "deviations": [
            "numerator is all-seat net buy (龙虎榜净买额), not institutional seats: "
            "Money02/data/lhb/lhb_detail.parquet has no seat column (data precondition "
            "in the registry row fails, downgrade applied)",
            "de-duplicated on (代码, 上榜日) preferring a same-day 上榜原因: the panel "
            "repeats a stock per reason and a '连续三个交易日' reason reports a multi-day "
            "cumulative net buy, not that day's",
            "a stock-day carrying only cumulative-window rows keeps its cumulative "
            "reading (the count is printed) rather than being dropped",
            "a trading day with no LHB events counts as 0 net buy",
            "normaliser is sh510300 traded value (CSI300 turnover is not in the repo); "
            "the raw un-normalised leg is published beside it",
            "long weight 0.9 per the berth, so the 1.0 buy-and-hold benchmark differs in "
            "exposure -- the long share is printed, never tuned",
        ],
        "dedup": dedup_stats,
        "panel": {
            "lhb_rows": None, "lhb_first": sig_dates[0], "lhb_last": sig_dates[-1],
            "lhb_days": len(sig_dates),
            "bars": int(len(dates)), "first_bar": dates[0], "last_bar": dates[-1],
            "index": "sh510300",
            "event_bars": int(hit.sum()),
            "event_bar_share": round(float(hit.mean()), 4),
        },
        "arms": arms,
        "benchmark": bench,
        "excess_pp": round(100 * excess_nz, 3),
        "excess_pp_raw": round(100 * excess_raw, 3),
        "null": null_nz,
        "null_raw": null_raw,
        "normaliser_disagrees": bool(np.sign(excess_nz) != np.sign(excess_raw)),
        "verdict": verdict,
        "verdict_reasons": reasons,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    try:
        import pandas as pd
        doc["panel"]["lhb_rows"] = int(len(pd.read_parquet(LHB_PARQUET, columns=["代码"])))
    except Exception as exc:  # a missing row count must not void the face
        doc["panel"]["lhb_rows_error"] = str(exc)[:120]
    return doc


def write(doc: dict, out: str = OUT) -> str:
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    return out


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"name": name, "pass": bool(ok), "detail": str(detail)[:160]})

    # 1. de-duplication: a stock repeated for two reasons contributes once
    import io as _io
    import pandas as pd

    fixture = pd.DataFrame({
        "代码": ["000001", "000001", "000002", "000003", "000004"],
        "上榜日": ["2024-01-02"] * 5,
        "上榜原因": ["日涨幅偏离值达到7%的前五只证券", "连续三个交易日内涨幅偏离值累计达到20%",
                 "日涨幅偏离值达到7%的前五只证券", "日振幅值达到15%的前五只证券",
                 "连续三个交易日内涨幅偏离值累计达到20%"],
        "龙虎榜净买额": [10.0, 99.0, -3.0, 4.0, 5.0],
    })
    tmp = os.path.join(ROOT, "results", "_zoo94_fixture.parquet")
    fixture.to_parquet(tmp, index=False)
    try:
        d1, v1 = daily_net_buy(tmp)
    finally:
        os.remove(tmp)
    # 10 (same-day, not the 99 cumulative) - 3 + 4 + 5 (cumulative-only still counts)
    leg("dedup prefers same-day reason", abs(v1[0] - 16.0) < 1e-9, v1)

    fixture2 = pd.DataFrame({
        "代码": ["000001", "000001"],
        "上榜日": ["2024-01-02"] * 2,
        "上榜原因": ["日涨幅偏离值达到7%的前五只证券", "日振幅值达到15%的前五只证券"],
        "龙虎榜净买额": [2.0, 4.0],
    })
    fixture2.to_parquet(tmp, index=False)
    try:
        _, v2 = daily_net_buy(tmp)
    finally:
        os.remove(tmp)
    leg("disagreeing same-day rows averaged", abs(v2[0] - 3.0) < 1e-9, v2)

    # 2. the live panel's own de-dup premise: same-day reasons agree almost everywhere
    import pandas as pd

    if os.path.exists(LHB_PARQUET):
        raw = pd.read_parquet(LHB_PARQUET, columns=["代码", "上榜日", "上榜原因", "龙虎榜净买额"])
        same = raw[~raw["上榜原因"].astype(str).str.contains("连续")]
        g = same.groupby(["代码", "上榜日"])["龙虎榜净买额"].nunique(dropna=True)
        share = float((g <= 1).sum()) / max(len(g), 1)
        leg("live panel: same-day reasons agree >=99%", share >= 0.99, round(share, 5))
    else:
        leg("live panel present", False, "missing parquet")

    # 3. alignment: an index bar with no event that day is 0, and it is marked unhit
    net, hit = align(["2024-01-02", "2024-01-04"], np.array([5.0, -2.0]),
                     ["2024-01-02", "2024-01-03", "2024-01-04"])
    leg("align zero-fills quiet bars", np.array_equal(net, [5.0, 0.0, -2.0]), net)
    leg("align marks event bars", np.array_equal(hit, [True, False, True]), hit)

    # 4. normalisation divides by traded value and stays NaN on a zero denominator
    nz = normalise(np.array([10.0, 10.0]), np.array([100.0, 0.0]))
    leg("normalise per yuan", abs(nz[0] - 0.1) < 1e-12 and not np.isfinite(nz[1]), nz)

    # 5. the four state combinations (and the 0.9 weight)
    f = np.array([1.0, 1.0, -1.0, -0.5, np.nan])
    s = np.array([0.5, 2.0, -0.5, -1.0, 1.0])
    st = state_of(f, s)
    leg("state: up-agree long", abs(st[0] - 0.9) < 1e-12, st[0])
    leg("state: up-disagree flat", st[1] == 0.0, st[1])
    leg("state: down-agree long", abs(st[2] - 0.9) < 1e-12, st[2])
    leg("state: down-disagree flat", st[3] == 0.0, st[3])
    leg("state: NaN stays NaN", not np.isfinite(st[4]), st[4])

    # 6. the shared curve, used with a full 1.0 weight and no cost, reproduces close/close
    d = np.arange(np.datetime64("2024-01-01"), np.datetime64("2024-01-11"))
    c = np.array([10, 11, 10.5, 12, 12.5, 12, 13, 13.5, 13, 14], dtype=float)
    o = np.concatenate([[c[0]], c[:-1] * 1.0])
    lv = curve(d, o, c, np.ones(10), 0.0)
    # curve() starts publishing at bar 1 (bar 0 is the base), so the ratio is close[-1]/close[1]
    leg("curve reproduces close/close", abs(lv[-1] / lv[0] - c[-1] / c[1]) < 1e-12,
        float(lv[-1] / lv[0]))

    # 7. a flat state earns nothing and pays no cost
    lv_flat = curve(d, o, c, np.zeros(10), COST_PER_SIDE)
    leg("flat state is flat", abs(lv_flat[-1] - 1.0) < 1e-12, float(lv_flat[-1]))

    # 8. the run is deterministic in its numbers (a second call must agree)
    if os.path.exists(INDEX_CSV) and os.path.exists(LHB_PARQUET):
        a1 = run()
        a2 = run()
        keys = ("excess_pp", "excess_pp_raw", "verdict")
        same = all(a1[k] == a2[k] for k in keys)
        same = same and a1["panel"] == a2["panel"]
        same = same and a1["arms"]["normalised"]["cagr"] == a2["arms"]["normalised"]["cagr"]
        leg("run is deterministic", same, (a1["excess_pp"], a2["excess_pp"]))
        leg("verdict is one of the frozen words", a1["verdict"] in CRITERIA["verdicts"],
            a1["verdict"])
    else:
        leg("inputs present", False, "missing panel")

    passed = sum(1 for x in legs if x["pass"])
    print("[selftest] %d/%d PASS" % (passed, len(legs)))
    for x in legs:
        if not x["pass"]:
            print("  FAIL %s | %s" % (x["name"], x["detail"]))
    return 0 if passed == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--stdout", action="store_true", help="print the face, do not publish")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    doc = run()
    if args.stdout:
        print(json.dumps(doc, ensure_ascii=False, indent=1))
    else:
        path = write(doc)
        print("[zoo94] verdict=%s excess=%+.2fpp/yr (raw %+.2f) p=%s -> %s"
              % (doc["verdict"], doc["excess_pp"], doc["excess_pp_raw"],
                 doc["null"].get("p_value"), path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())