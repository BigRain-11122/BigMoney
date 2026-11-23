"""The bond-free book de-levers into cash that pays nothing -- price that sleeve.

Why this face exists
--------------------
`scripts/etf_nobond_vt.py` is the production candidate: drop the bond sleeve, then cap the
book's own realised vol at 8%. Sizing only ever de-levers (`scale = min(1, target/est)`),
so whatever is not invested -- `1 - scale` -- sits at zero return. The face prints the cost
of the vol target (15.18% -> 11.16% CAGR) as if that were the price of the brake, but part
of that price is simply money nobody got paid for.

Two things move that sleeve, and they are different questions:

1. **Day count.** Repo accrues on natural days. A 20-trading-day rebalance period spans
   ~30 natural days, so a per-trading-day accrual under-states the sleeve by ~33%. The
   sibling face `research/ASTOCK_VETO_CASH_DAYCOUNT.md` found exactly this on the veto book
   (53% under-statement). Both calibers are printed here, so nobody has to guess which one
   a number used.
2. **Vehicle.** GC001 pays the exchange rate but trades in 100,000 CNY lots, so a sleeve
   under that cannot buy it at all; a money ETF (511880) has no lot floor and pays a lower
   rate. Both are measured on this book's own calendar, so the answer is "what could this
   sleeve actually have earned", not "what does the index say cash earns".

Negative controls (built in, both asserted in `selftest`/`check`)
----------------------------------------------------------------
* The **base arm never de-levers** (scale = 1 on every decision), so its cash weight is 0
  everywhere and paying it any rate must move nothing: delta must be exactly 0.0000pp. A
  non-zero delta means the cash sleeve is being applied to money that was invested.
* **repo = 0** must reproduce the published `nobond_vt08` series bit-for-bit, because the
  cash factor is a multiplicative 1.0. That is what makes the delta attributable.

Usage
-----
    python scripts/etf_nobond_cash_leg.py            # run, write face + md
    python scripts/etf_nobond_cash_leg.py --check     # re-derive verdicts from the face
    python scripts/etf_nobond_cash_leg.py selftest    # offline, synthetic, fast
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "results", "etf_nobond_cash_leg.json")
DOC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "research", "ETF_NOBOND_CASH_LEG.md")
REPO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "data", "repo_daily", "GC001.csv")
MONEY_ETF = "sh511880"
DAILY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "daily")
IS_END = "2023-12-31"
REBAL, NHOLD, COST = 20, 5, 0.0010
VT = 0.08


# ---------------------------------------------------------------- pure helpers
def repo_yield(path=REPO_PATH):
    """GC001 close, annualised percent (the exchange quotes repo as an annual rate)."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    return df["close"].astype(float)


def step_scales(dates, diag):
    """Scale in force on each step (dates[i] -> dates[i+1]).

    The engine sizes at a decision and then accrues the step from that same bar's open, so
    the step starting at a decision already carries that decision's scale. Steps between
    decisions carry the last one.
    """
    by_date = {row["date"]: float(row["scale"]) for row in diag}
    out, cur = [], 1.0
    for d in dates[:-1]:
        cur = by_date.get(str(pd.Timestamp(d).date()), cur)
        out.append(cur)
    return out


def cash_weights(scales):
    return [max(0.0, min(1.0, 1.0 - s)) for s in scales]


def cash_factors(dates, cash_w, rate_at, natural=True):
    """Cash sleeve accrues `rate` (annual %) over the step, on natural or trading days."""
    out = []
    for i, w in enumerate(cash_w):
        if w <= 0.0:
            out.append(1.0)
            continue
        d0, d1 = pd.Timestamp(dates[i]), pd.Timestamp(dates[i + 1])
        days = max(1, (d1 - d0).days) if natural else 1
        rate = rate_at(d0)
        r = 0.0 if rate is None else float(rate) / 100.0 * days / 365.0
        out.append(1.0 + w * r)
    return out


def blend(ser, factors):
    """Carry the cash sleeve alongside the published equity path.

    `ser * cumprod(factors)` rather than re-accumulating the book's own step ratios: the
    published path is used as it stands, so with every factor 1.0 the result is the input
    bit-for-bit (that is the negative control -- re-accumulating would silently introduce
    rounding and make the control unreachable).
    """
    cum = np.cumprod(np.asarray(factors, dtype=float))
    return pd.Series(ser.to_numpy() * cum, index=ser.index)


def step_dates(openp, close, start=R.START):
    op = openp.reindex(columns=close.columns)
    return [d for d in op.index if d >= pd.Timestamp(start)]


def arm(close, openp, amt, score, vol_target):
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, NHOLD, COST,
                                      vol_target=vol_target, diag=diag)
    return ser, turn, diag


def summarize(ser, label):
    m = A.stats2(ser, label)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    return m


# ---------------------------------------------------------------- main run
def run():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    print("bond-free universe", len(cols), "flips repaired", n_flip, flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)
    dates = step_dates(openp[cols], close[cols])

    repo = repo_yield()
    mef_path = os.path.join(DAILY_DIR, MONEY_ETF + ".csv")
    mef = pd.read_csv(mef_path, parse_dates=["date"]).set_index("date").sort_index()["close"].astype(float)

    def repo_at(d):
        s = repo.loc[:d]
        return float(s.iloc[-1]) if len(s) else None

    def mef_at(d):
        s = mef.loc[:d]
        return float(s.iloc[-1]) if len(s) else None

    arms, cash_stats = [], {}
    for label, vt in (("nobond_base", None), ("nobond_vt08", VT)):
        ser, turn, diag = arm(close[cols], openp[cols], amt[cols], sc, vt)
        scales = step_scales(dates, diag)
        cw = cash_weights(scales)
        assert len(cw) == len(ser), (len(cw), len(ser))

        # repo on natural days, repo on trading days, money ETF on its own prices
        f_nat = cash_factors(dates, cw, repo_at, natural=True)
        f_td = cash_factors(dates, cw, repo_at, natural=False)
        mef_ret = {}
        for i, w in enumerate(cw):
            if w <= 0.0:
                mef_ret[i] = 1.0
                continue
            a, b = mef_at(pd.Timestamp(dates[i])), mef_at(pd.Timestamp(dates[i + 1]))
            mef_ret[i] = 1.0 + w * ((b / a - 1.0) if (a and b and a > 0) else 0.0)
        f_mef = [mef_ret[i] for i in range(len(cw))]
        f_zero = [1.0] * len(cw)

        s0 = blend(ser, f_zero)
        s_nat = blend(ser, f_nat)
        s_td = blend(ser, f_td)
        s_mef = blend(ser, f_mef)
        # the zero arm must be the published series, untouched
        assert np.allclose(s0.to_numpy(), ser.to_numpy(), rtol=0.0, atol=0.0), "repo=0 changed the book"

        row = {"label": label, "turnover": round(turn, 2),
               "no_cash": summarize(ser, label + "_nocash"),
               "repo_natural": summarize(s_nat, label + "_repo_nat"),
               "repo_tradingday": summarize(s_td, label + "_repo_td"),
               "money_etf": summarize(s_mef, label + "_mef")}
        arms.append(row)

        nz = [w for w in cw if w > 0]
        cash_stats[label] = {
            "mean_cash_weight": round(float(np.mean(cw)), 4),
            "max_cash_weight": round(float(np.max(cw)), 4),
            "share_of_steps_in_cash": round(len(nz) / float(len(cw)), 4),
            "natural_days_total": int(sum((pd.Timestamp(dates[i + 1]) - pd.Timestamp(dates[i])).days
                                          for i in range(len(dates) - 1))),
            "trading_days_total": len(dates) - 1,
        }
        print(label, row["no_cash"]["cagr"], row["repo_natural"]["cagr"],
              row["money_etf"]["cagr"], flush=True)

    base, vt08 = arms[0], arms[1]
    cash_stats["natural_over_trading"] = round(
        cash_stats["nobond_vt08"]["natural_days_total"]
        / float(cash_stats["nobond_vt08"]["trading_days_total"]), 4)

    def pp(a, b):
        return round((b - a) * 100.0, 4)

    base_cagr = base["repo_natural"]["cagr"]     # base pays nothing (cash weight 0)
    head = {
        "base_cagr_pct": round(base_cagr * 100.0, 4),
        "vt08_nocash_cagr_pct": round(vt08["no_cash"]["cagr"] * 100.0, 4),
        "vt08_repo_natural_cagr_pct": round(vt08["repo_natural"]["cagr"] * 100.0, 4),
        "vt08_repo_tradingday_cagr_pct": round(vt08["repo_tradingday"]["cagr"] * 100.0, 4),
        "vt08_money_etf_cagr_pct": round(vt08["money_etf"]["cagr"] * 100.0, 4),
        "cash_leg_pp_natural": pp(vt08["no_cash"]["cagr"], vt08["repo_natural"]["cagr"]),
        "cash_leg_pp_tradingday": pp(vt08["no_cash"]["cagr"], vt08["repo_tradingday"]["cagr"]),
        "cash_leg_pp_money_etf": pp(vt08["no_cash"]["cagr"], vt08["money_etf"]["cagr"]),
        "base_arm_cash_delta_pp": pp(base["no_cash"]["cagr"], base["repo_natural"]["cagr"]),
        "vol_target_cost_before_pp": pp(vt08["no_cash"]["cagr"], base_cagr),
        "vol_target_cost_after_pp": pp(vt08["repo_natural"]["cagr"], base_cagr),
        "daycount_understatement_pct": round(
            (cash_stats["natural_over_trading"] - 1.0) * 100.0, 2),
    }
    head["share_of_vt_cost_that_is_unpaid_cash_pct"] = round(
        100.0 * head["cash_leg_pp_natural"] / head["vol_target_cost_before_pp"], 2) \
        if head["vol_target_cost_before_pp"] else None

    gate = 0.25  # one quarter of a point decides whether the sleeve is worth wiring
    if head["cash_leg_pp_natural"] < gate:
        verdict = "CASH_SLEEVE_TOO_SMALL_TO_WIRE"
    elif head["vol_target_cost_after_pp"] < 0.5 * head["vol_target_cost_before_pp"]:
        verdict = "MOST_OF_THE_VOL_TARGET_COST_WAS_UNPAID_CASH"
    else:
        verdict = "CASH_SLEEVE_REAL_BUT_MOST_OF_THE_COST_IS_THE_BRAKE"

    mef_cagr = summarize(mef, "money_etf_own")["cagr"]
    rep = repo[repo.index >= pd.Timestamp(R.START)]
    out = {
        "schema": "etf-nobond-cash-leg/v1",
        "evidence_cutoff": str(close.index.max().date()),
        "universe": len(cols),
        "flips_repaired": int(n_flip),
        "spec": {"rebal": REBAL, "n_hold": NHOLD, "cost_per_side": COST,
                 "vol_target": VT, "is_end": IS_END,
                 "execution": "decide at close t, own from open t (entry_lag=0, the caliber every"
                              " printed number in etf_nobond_vt.json uses)"},
        "cash_vehicle": {
            "repo": "GC001 close, annualised percent, accrued on natural days (trading-day arm"
                    " printed beside it)",
            "repo_star_of_window_median_pct": round(float(rep.median()), 4),
            "repo_star_of_window_mean_pct": round(float(rep.mean()), 4),
            "money_etf": MONEY_ETF,
            "money_etf_price_only_cagr_pct": round(mef_cagr * 100.0, 4),
            "money_etf_note": "price-only: a money ETF pays its yield out as distributions and this"
                              " panel carries no distribution series, so the price CAGR is a FLOOR"
                              " on the vehicle, not its yield. It is printed so the lot-floor"
                              " argument has a number, not so it can be read as 'the ETF pays 0.07%'.",
            "lot_floor_note": "SSE repo trades in 100,000 CNY lots, so a cash sleeve under that"
                              " cannot buy GC001 on the day; a money ETF has no floor and pays"
                              " what its own price shows.",
        },
        "cash_stats": cash_stats,
        "headline": head,
        "verdict": verdict,
        "arms": arms,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    write_doc(out)
    print(json.dumps(head, ensure_ascii=False, indent=1), flush=True)
    print("verdict", verdict, flush=True)
    return out


def write_doc(out):
    h = out["headline"]
    c = out["cash_stats"]
    v = out["cash_vehicle"]
    vt_o = next(a for a in out["arms"] if a["label"] == "nobond_vt08")

    def _v(arm, key, field):
        val = arm[key].get(field)
        if val is None:
            return float("nan")
        return val * 100.0 if (field.startswith("cagr") or field.startswith("maxdd")) else val
    lines = [
        "# 无债档的现金腿：刹车踩下去的那部分钱，一分利息都没拿",
        "",
        "> 自动生成，勿手改。生成器 `scripts/etf_nobond_cash_leg.py`，数据面 `results/etf_nobond_cash_leg.json`。",
        "> 证据截止 %s（面板最后一根 bar）。执行口径=收盘决策、当根开盘拥有（entry_lag=0，"
        "与 `etf_nobond_vt.json` 里所有在印数字同口径）。" % out["evidence_cutoff"],
        "",
        "## 一句话",
        "",
        "8%% 波动目标的账面代价（%.2f%% → %.2f%%，差 %.2fpp）里，有 **%.2fpp** 不是刹车的价钱，"
        "而是没投出去的钱按零利率躺着的代价——按 GC001 自然日计息补上后，代价降到 %.2fpp。"
        % (h["base_cagr_pct"], h["vt08_nocash_cagr_pct"], h["vol_target_cost_before_pp"],
           h["cash_leg_pp_natural"], h["vol_target_cost_after_pp"]),
        "",
        "## 那张腿有多大",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 平均现金权重（vt08） | %.2f%% |" % (c["nobond_vt08"]["mean_cash_weight"] * 100),
        "| 最高现金权重 | %.2f%% |" % (c["nobond_vt08"]["max_cash_weight"] * 100),
        "| 有现金的步数占比 | %.2f%% |" % (c["nobond_vt08"]["share_of_steps_in_cash"] * 100),
        "| 自然日 / 交易日 | %.4f 倍（%d / %d） |" % (
            c["natural_over_trading"], c["nobond_vt08"]["natural_days_total"],
            c["nobond_vt08"]["trading_days_total"]),
        "",
        "## 三种口径",
        "",
        "| 现金腿 | 年化 | 比零利率多 |",
        "|---|---|---|",
        "| 零（在印口径） | %.2f%% | — |" % h["vt08_nocash_cagr_pct"],
        "| GC001·自然日 | %.2f%% | +%.2fpp |" % (h["vt08_repo_natural_cagr_pct"], h["cash_leg_pp_natural"]),
        "| GC001·交易日（错的口径） | %.2f%% | +%.2fpp |" % (
            h["vt08_repo_tradingday_cagr_pct"], h["cash_leg_pp_tradingday"]),
        "| 货币 ETF %s（**只算价格**） | %.2f%% | +%.2fpp（下界） |" % (
            v["money_etf"], h["vt08_money_etf_cagr_pct"], h["cash_leg_pp_money_etf"]),
        "",
        "货币 ETF 那一行只算价格、不算分红：它把钱按分红派出去，本地面板没有分红序列，"
        "所以这一行是**下界**而不是「这只 ETF 只付 %.2f%%」——本面不带分红面，就不替它下结论。"
        % v["money_etf_price_only_cagr_pct"],
        "",
        "交易日计息会把这条腿少算 **%.2f%%**（20 个交易日的持仓期实际占款约 30 个自然日）。"
        % h["daycount_understatement_pct"],
        "",
        "## 分段（这条腿是不是只在某一段）",
        "",
        "| 口径 | 全窗年化/夏普/回撤 | 2020-2023 年化/夏普 | 2024+ 年化/夏普/回撤 |",
        "|---|---|---|---|",
        "| 零利率 | %.2f%% / %.3f / %.2f%% | %.2f%% / %.3f | %.2f%% / %.3f / %.2f%% |" % (
            _v(vt_o, "no_cash", "cagr"), _v(vt_o, "no_cash", "sharpe"), _v(vt_o, "no_cash", "maxdd"),
            _v(vt_o, "no_cash", "cagr_is"), _v(vt_o, "no_cash", "sharpe_is"),
            _v(vt_o, "no_cash", "cagr_oos"), _v(vt_o, "no_cash", "sharpe_oos"),
            _v(vt_o, "no_cash", "maxdd_oos")),
        "| GC001·自然日 | %.2f%% / %.3f / %.2f%% | %.2f%% / %.3f | %.2f%% / %.3f / %.2f%% |" % (
            _v(vt_o, "repo_natural", "cagr"), _v(vt_o, "repo_natural", "sharpe"), _v(vt_o, "repo_natural", "maxdd"),
            _v(vt_o, "repo_natural", "cagr_is"), _v(vt_o, "repo_natural", "sharpe_is"),
            _v(vt_o, "repo_natural", "cagr_oos"), _v(vt_o, "repo_natural", "sharpe_oos"),
            _v(vt_o, "repo_natural", "maxdd_oos")),
        "",
        "分段也给同一答案：IS +%.2fpp、OOS +%.2fpp，夏普 %.3f → %.3f，回撤从 -%.2f%% 收到 -%.2f%%。"
        "补上这条腿既没有把风险换大，也没有把收益集中在某一段。"
        % (_v(vt_o, "repo_natural", "cagr_is") - _v(vt_o, "no_cash", "cagr_is"),
           _v(vt_o, "repo_natural", "cagr_oos") - _v(vt_o, "no_cash", "cagr_oos"),
           _v(vt_o, "no_cash", "sharpe"), _v(vt_o, "repo_natural", "sharpe"),
           -_v(vt_o, "no_cash", "maxdd"), -_v(vt_o, "repo_natural", "maxdd")),
        "",
        "## 两个负控",
        "",
        "1. **基础臂不降杠杆**，现金权重处处为 0，给它任何利率都不该动一分：实测 Δ=%.4fpp。"
        % h["base_arm_cash_delta_pp"],
        "2. **利率置零**必须逐位复现 `etf_nobond_vt.json` 的 nobond_vt08 序列（现金因子恒等 1.0），"
        "`run` 里是断言，不是注释。",
        "",
        "## 可执行性（这条腿的真实约束）",
        "",
        v["lot_floor_note"],
        "",
        "窗口内 GC001 利率中位 %.2f%%、均值 %.2f%%（这是这条腿的真实价格）。所以「现金腿值多少」"
        "取决于账户大小：100 万元本金、平均现金权重 %.0f%% 时约 %d 万元，够买 %d 手 GC001；"
        "小于 10 万元的现金日只能退到货币 ETF，按上表那一行的下界折价（真实派息未计）。"
        % (v["repo_star_of_window_median_pct"], v["repo_star_of_window_mean_pct"],
           c["nobond_vt08"]["mean_cash_weight"] * 100,
           int(round(1_000_000 * c["nobond_vt08"]["mean_cash_weight"] / 10000)),
           int(round(1_000_000 * c["nobond_vt08"]["mean_cash_weight"] / 100000))),
        "",
        "## 判词",
        "",
        "`%s`：现金腿 +%.2fpp，占波动目标账面代价的 %.2f%%。"
        % (out["verdict"], h["cash_leg_pp_natural"], h["share_of_vt_cost_that_is_unpaid_cash_pct"]),
        "",
        "读数注意：本面只加了一条现金利息，没有改选股、没有改成本、没有动波动目标本身；"
        "四个臂的换手与成本完全一致，所以差额只能来自那条腿。",
        "",
    ]
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


# ---------------------------------------------------------------- check / selftest
def check():
    with io.open(OUT, encoding="utf-8") as fh:
        d = json.load(fh)
    h, c = d["headline"], d["cash_stats"]
    problems = []
    # the base arm must not move (its cash weight is zero everywhere)
    if abs(h["base_arm_cash_delta_pp"]) > 1e-9:
        problems.append("base arm moved %.6fpp although it never de-levers" % h["base_arm_cash_delta_pp"])
    # the cash leg must be positive and the natural-day caliber the larger one
    if h["cash_leg_pp_natural"] <= 0:
        problems.append("cash leg is not positive")
    if not h["cash_leg_pp_natural"] > h["cash_leg_pp_tradingday"]:
        problems.append("natural-day accrual is not larger than trading-day accrual")
    # arithmetic identities on the published numbers
    if abs((h["vt08_repo_natural_cagr_pct"] - h["vt08_nocash_cagr_pct"])
           - h["cash_leg_pp_natural"]) > 1e-6:
        problems.append("cash_leg_pp_natural does not re-derive from the two printed CAGRs")
    if abs((h["base_cagr_pct"] - h["vt08_nocash_cagr_pct"])
           - h["vol_target_cost_before_pp"]) > 1e-6:
        problems.append("vol_target_cost_before_pp does not re-derive")
    if abs((h["base_cagr_pct"] - h["vt08_repo_natural_cagr_pct"])
           - h["vol_target_cost_after_pp"]) > 1e-6:
        problems.append("vol_target_cost_after_pp does not re-derive")
    # cash weights must be a proper fraction
    for k, v in c.items():
        if k == "natural_over_trading":
            continue
        if not (0.0 <= v["mean_cash_weight"] <= 1.0) or not (0.0 <= v["max_cash_weight"] <= 1.0):
            problems.append("%s cash weight out of [0,1]" % k)
    if c["nobond_base"]["max_cash_weight"] != 0.0:
        problems.append("base arm carries cash -- sizing should be 1.0 every decision")
    for p in problems:
        print("PROBLEM:", p)
    print("CHECK %s  verdict=%s  cash_leg=%.4fpp" %
          ("OK" if not problems else "FAILED", d["verdict"], h["cash_leg_pp_natural"]))
    return 0 if not problems else 3


def selftest():
    legs = []
    # L1 step_scales carries the last decision forward
    dates = pd.date_range("2024-01-01", periods=6, freq="B")
    diag = [{"date": str(dates[0].date()), "scale": 0.5},
            {"date": str(dates[3].date()), "scale": 0.25}]
    sc = step_scales(list(dates), diag)
    legs.append(("step_scales carries forward", sc == [0.5, 0.5, 0.5, 0.25, 0.25]))
    # L2 a decision on the final bar cannot be applied to a step that does not exist
    legs.append(("last decision unused", len(sc) == 5))
    # L3 cash weights are the complement, clipped
    legs.append(("cash weight complement", cash_weights([0.0, 0.4, 1.0, 1.7]) == [1.0, 0.6, 0.0, 0.0]))
    # L4 natural-day accrual beats trading-day accrual over a 30-day step
    d2 = [pd.Timestamp("2024-03-01"), pd.Timestamp("2024-03-31")]
    fn = cash_factors(d2, [1.0], lambda d: 2.0, natural=True)[0]
    ft = cash_factors(d2, [1.0], lambda d: 2.0, natural=False)[0]
    legs.append(("natural > trading", fn > ft > 1.0))
    legs.append(("natural arithmetic exact", abs(fn - (1 + 0.02 * 30 / 365)) < 1e-12))
    # L5 a zero cash weight is exactly 1.0 whatever the rate (this is the bit-identity leg)
    legs.append(("zero weight neutral", cash_factors(d2, [0.0], lambda d: 99.0)[0] == 1.0))
    # L6 blend with unit factors reproduces the input series bit-for-bit
    ser = pd.Series([1.0, 1.01, 0.995, 1.02], index=pd.date_range("2024-01-01", periods=4))
    same = blend(ser, [1.0] * 4)
    legs.append(("unit factors bit-identical", np.array_equal(same.to_numpy(), ser.to_numpy())))
    # L7 blend applies the cash factor outside the book factor
    doubled = blend(ser, [1.02, 1.0, 1.0, 1.0])
    legs.append(("cash factor multiplies", abs(doubled.iloc[0] - 1.02) < 1e-12
                 and abs(doubled.iloc[-1] - ser.iloc[-1] * 1.02) < 1e-12))
    # L8 a missing rate contributes nothing rather than crashing
    legs.append(("missing rate handled", cash_factors(d2, [1.0], lambda d: None)[0] == 1.0))
    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print(("PASS " if v else "FAIL ") + name)
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "selftest":
        sys.exit(selftest())
    elif arg in ("--check", "check"):
        sys.exit(check())
    else:
        run()
