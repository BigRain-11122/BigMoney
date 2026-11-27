#!/usr/bin/env python3
"""「100 万开不了这本书」是资本事实，还是「用最近 12 个月量波动」这个选择的产物？

WHY THIS FILE EXISTS
--------------------
``idx_fut_carry_open_capital``（r1780）把 carry 书的可执行行写成 0 手，并把
1,137,862.5 元印成「开这本书要的资本」。那枚 1,137,862.5 是
``91,029 / 8%``，而 91,029 出自 ``results/idx_fut_carry_paper/SIZING.json``：

    "window": ["2025-11-26", "2026-11-26"], "days": 242

也就是说整本书的尺寸是由**最近 242 个收益日**这一段波动定出来的。r2192 在另一条腿
上量到同一本书的每手波动是 71,040（十年回放窗），两个数差 28%，当时按「不同窗不同
测量」并列披露、没有仲裁。可是读者要拿它下决定，并列披露等于把选择丢给读者 ——
r1779 的教训。

本面把这一问答到底：
  1. **先证明尺一样**：在同一段面板上重算那 242 天的波动，必须逐位复现 91,029.0，
     并把 91,029/8% 复现到 1,137,862.5（任一失配 = 不发布，exit 2）；
  2. **把窗口换成客观序列**：242 / 484 / 726 / 1210 / 全样本，各自印每手年化波动、
     在 100 万 8% 目标下买几手、第一手要多少资本；
  3. **把「今天」放回分布里**：全样本（1965 个收益日）上所有 242 日滚动窗共 1724 个，
     今日读数在其中的分位、以及历史上有多少比例的年份在 100 万上是买得起的；
  4. **量这条规则真实有多硬**：用滚动窗做前向检验 —— 按上一年的波动定手数、看下一年的
     实现波动有没有把它顶出 8% 预算，得到「8% 硬上限」的实际越限率，以及要把它做成
     p90 意义上的硬上限需要给波动尺乘多少；
  5. **落一个选择**（ADOPTION 常量，其余各面只能读它）：保留最近 12 个月当尺（上限是
     对下一年的承诺，只能用最近的样本估），但从此不许把它的输出叫「这本书要的资本」，
     只能叫「今天的第一手门槛」，并随面印出解除条件。

口径与边界
----------
  * 点数是可加的 P&L（不是收益率），换钱只用已发布的 200 元/点合约乘数
    （``idx_fut_carry_one_lot_ruler`` 的 ``precision_tick_basis``：200 x 0.0001 = 0.02），
    以及已发布的每手资本口径；本面不新造分母。
  * 年化天数 252（两臂父面 ``_ann_sharpe`` 的口径），与 SIZING 的 242 天窗对齐 ——
    同一本书的两条读数只有在同一分母上才可比。
  * 前向检验是**重叠**样本（步长 1 天），有效独立样本远小于 1482；本面把它当描述性
    频率印，不当显著性检验（p 值不在本面射程内，见 what_is_still_missing）。

verdict tokens（跑之前冻结）
  THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD
      今日读数 ≥ 滚动窗 p90 且历史上 ≥60% 的年份在 100 万上买得起 —— 「要 1,137,862
      才能开」是今天这段波动的读数，不是这本书的结构性门槛
  THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD
      今日读数 < p75 或历史买得起率 < 40% —— 门槛基本是资本给的
  THE_FIRST_RUNG_IS_PARTLY_A_VOLATILITY_READ
      中间区

  THE_EIGHT_PERCENT_CAP_HOLDS                     越限率 ≤ 10%
  THE_EIGHT_PERCENT_CAP_IS_BREACHED_ABOUT_ONE_YEAR_IN_FOUR   10% < 越限率 ≤ 33%
  THE_EIGHT_PERCENT_CAP_IS_BREACHED_HALF_THE_TIME  越限率 > 33%
  UNREADABLE                                      复现腿失配或读数缺失 —— 不发布

只读：不碰 LEDGER.json / STATE.json / 任何已发布面；确定性（同面板同字节，除 generated）。
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import idx_fut_carry_paper as CP  # noqa: E402
import idx_fut_basis as BASE  # noqa: E402

TZ = timezone(timedelta(hours=8))

OPEN_SRC = "results/idx_fut_carry_open_capital.json"
SIZING_SRC = "results/idx_fut_carry_paper/SIZING.json"
RULER_SRC = "results/idx_fut_carry_one_lot_ruler.json"
CAP_SRC = "results/idx_fut_carry_capacity_lots.json"

OUT_JSON = ROOT / "results" / "carry_first_rung_vol_ruler.json"
OUT_MD = ROOT / "results" / "carry_first_rung_vol_ruler.md"

PRODUCT = "IC"
ANNUALISATION_DAYS = 252
ONE_YEAR_BARS = 242          # SIZING 自己的窗口长度（days=242）
MIN_BARS = 120
TOL_CNY = 0.01               # 已发布值都是 2dp 或 0dp 的元
MULTIPLIER_FALLBACK = 200.0  # IC 合约乘数（元/点），权威面见 multiplier_authority

ADOPTION = {
    "decided": "保留最近 242 个收益日当尺，但从此不许把它的输出叫「这本书要的资本」，只能叫「今天的第一手门槛」",
    "decided_in": "bm-c round 2193",
    "ruler": "trailing 242 returns (SIZING.json 自己的窗口)",
    "because": "风险上限是对下一年的一句承诺，所以尺必须看最近这一段；十年平均看不见正在发烧的当期。"
               "但用它算出来的数会动：它是「今天的第一手门槛」，不是「这本书的资本要求」——"
               "任何把后者写进页面的读数，大多数年份都会是错的",
    "what_the_adoption_forbids": [
        "把 1,137,862.5 印成「开这本书要的资本」而不带它的窗口与它在滚动分布里的分位",
        "因为最近 12 个月正处在自己历史的 p94，就把尺换成最平静的那把（十年）来把仓位放大",
    ],
    "alternatives_not_adopted": [
        {"ruler": "十年回放窗（1961-1965 bar）", "adopted": False,
         "because_not": "它是所有已发布读数里最平静的一枚（71,149 对 91,029），照它买手等于拿一段"
                        "包含更多平静期的十年去放大今天的仓位；同一套算术说，那样 8% 上限会在"
                        "大约四分之一的年份被顶破"},
        {"ruler": "滚动 242 日窗的中位数", "adopted": False,
         "because_not": "八年的中位数不是关于未来十二个月的一句话"},
    ],
}

WINDOW_LABEL = {
    "one_year_242": "最近 1 年（242 收益日）",
    "two_year_484": "最近 2 年（484）",
    "three_year_726": "最近 3 年（726）",
    "five_year_1210": "最近 5 年（1210）",
    "full_sample": "全样本",
}


def _now():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _load(rel):
    p = ROOT / rel
    if not p.exists():
        return {}
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _sha(rel):
    p = ROOT / rel
    if not p.exists():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def radius():
    """已发布的每点乘数（元/点）；读不到权威串就退回 200 并如实标注。"""
    face = _load(RULER_SRC)
    basis = ((face.get("rule") or {}).get("precision_tick_basis") or "")
    stated = MULTIPLIER_FALLBACK if "200 x" not in basis else 200.0
    return stated, ("results/idx_fut_carry_one_lot_ruler.json::rule.precision_tick_basis"
                     if "200 x" in basis else "fallback constant")


# ------------------------------------------------------------------ measurement
def series(cutoff):
    """(dates, excess_points)：对冲残差的每手日 P&L，父面自己的回放窗。"""
    rows, _rolls = CP.position_series(PRODUCT)
    if not rows:
        return None
    cut = [r for r in rows if r[0] <= cutoff]
    if len(cut) < MIN_BARS + 2:
        return None
    idx = BASE.load_index(BASE.PAIRS[PRODUCT][0])
    s = CP.per_lot_daily(cut, idx, years=10)
    if not s:
        return None
    dates = [r[0] for r in cut[1:]]
    pts = list(s["excess_points"])
    if len(dates) != len(pts):
        return None
    return dates, pts


def sd(xs):
    n = len(xs)
    if n < 2:
        return None
    mu = sum(xs) / n
    return math.sqrt(sum((x - mu) ** 2 for x in xs) / (n - 1))


def vol_cny(xs, mult, tdays=ANNUALISATION_DAYS):
    """每手年化波动（元）。"""
    s = sd(xs)
    if s is None:
        return None
    return s * math.sqrt(tdays) * mult


def mean_cny(xs, mult, tdays=ANNUALISATION_DAYS):
    return sum(xs) / len(xs) * tdays * mult


def lots_at(vol, capital, target_pct):
    """floor(目标预算 / 每手波动) —— 已发布规则本身，不重写。"""
    if not vol or vol <= 0:
        return None
    return int(math.floor((target_pct / 100.0) * capital / vol))


def first_rung(vol, target_pct):
    if not vol or vol <= 0:
        return None
    return round(vol / (target_pct / 100.0), 2)


def pct_rank(values, x):
    if not values:
        return None
    below = sum(1 for v in values if v < x)
    return round(100.0 * below / len(values), 2)


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


def judge(today_pct, share_one_lot_pct):
    if today_pct is None or share_one_lot_pct is None:
        return "UNREADABLE"
    if today_pct >= 90.0 and share_one_lot_pct >= 60.0:
        return "THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD"
    if today_pct < 75.0 or share_one_lot_pct < 40.0:
        return "THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD"
    return "THE_FIRST_RUNG_IS_PARTLY_A_VOLATILITY_READ"


def cap_verdict(breach_rate_pct):
    if breach_rate_pct is None:
        return "UNREADABLE"
    if breach_rate_pct <= 10.0:
        return "THE_EIGHT_PERCENT_CAP_HOLDS"
    if breach_rate_pct <= 33.0:
        return "THE_EIGHT_PERCENT_CAP_IS_BREACHED_ABOUT_ONE_YEAR_IN_FOUR"
    return "THE_EIGHT_PERCENT_CAP_IS_BREACHED_HALF_THE_TIME"


# -------------------------------------------------------------------- the face
def build(cutoff=None):
    open_face = _load(OPEN_SRC)
    sizing_face = _load(SIZING_SRC)
    capital = (open_face.get("accounts") or {}).get(PRODUCT, {}).get("capital_cny")
    target = (open_face.get("accounts") or {}).get(PRODUCT, {}).get("target_pct")
    published_vol = (open_face.get("accounts") or {}).get(PRODUCT, {}).get("per_lot_vol_cny_hedged")
    published_rung = ((open_face.get("book") or {}).get("cheapest_to_open") or {}).get("funding_cny")
    sizing_acct = (sizing_face.get("accounts") or {}).get(PRODUCT, {})
    sizing_window = sizing_acct.get("window")
    sizing_days = sizing_acct.get("days")
    cut = cutoff or open_face.get("evidence_cutoff") or sizing_face.get("evidence_cutoff")

    payload = {
        "schema": "carry-first-rung-vol-ruler/v1",
        "face": "carry_first_rung_vol_ruler",
        "machine": "bm-c",
        "product": PRODUCT,
        "evidence_cutoff": cut,
        "question": "「100 万开不了这本书」是资本事实，还是「用最近 12 个月量波动」这个选择的产物？",
        "inputs": {
            "open_capital": {"face": OPEN_SRC, "sha256": _sha(OPEN_SRC),
                             "generated": open_face.get("generated"),
                             "cutoff": open_face.get("evidence_cutoff")},
            "sizing": {"face": SIZING_SRC, "sha256": _sha(SIZING_SRC),
                       "generated": sizing_face.get("generated"),
                       "cutoff": sizing_face.get("evidence_cutoff")},
        },
    }
    if not (capital and target and published_vol):
        payload["judgement"] = {"verdict": "UNREADABLE",
                                "why": "已发布的 capital/target/per_lot_vol 读不到"}
        return payload

    mult, mult_src = radius()
    payload["multiplier"] = {"cny_per_point": mult, "authority": mult_src,
                            "precision_tick_basis": ((_load(RULER_SRC).get("rule") or {})
                                                     .get("precision_tick_basis"))}

    ser = series(cut)
    if not ser:
        payload["judgement"] = {"verdict": "UNREADABLE", "why": "面板回放读不出（position_series/per_lot_daily）"}
        return payload
    dates, pts = ser
    payload["panel"] = {"first_return": dates[0], "last_return": dates[-1],
                        "return_bars": len(pts)}

    # ---- 1. 复现腿：同一段 242 天必须复现已发布的 91,029.0
    tail = pts[-ONE_YEAR_BARS:]
    repro_vol = vol_cny(tail, mult)
    # 已发布的第一手门槛是按 2dp 的波动算的（91,029.0 / 8% = 1,137,862.5）；用未舍入的
    # 91,029.0043 会多出 5 分钱——那不是另一个读数，是同一个数在另一处精度上相加
    repro_rung = first_rung(round(repro_vol, 2), target)
    payload["reproduction"] = {
        "published_vol_cny": published_vol,
        "recomputed_vol_cny": round(repro_vol, 2),
        "published_window": sizing_window,
        "published_days": sizing_days,
        "recomputed_return_window": [dates[-ONE_YEAR_BARS], dates[-1]],
        "recomputed_bars": len(tail),
        "note": "父面的 window 起点是锚日（无收益），242 个收益落在 recomputed_return_window",
        "verdict": ("MATCH" if abs(repro_vol - published_vol) <= TOL_CNY else "MISMATCH"),
        "published_first_rung_cny": published_rung,
        "recomputed_first_rung_cny": repro_rung,
        "first_rung_verdict": ("MATCH" if (published_rung and abs(repro_rung - published_rung) <= TOL_CNY)
                               else "MISMATCH"),
    }
    if payload["reproduction"]["verdict"] != "MATCH":
        payload["judgement"] = {"verdict": "UNREADABLE",
                                "why": "复现腿失配：重算 %.2f vs 已发布 %.2f —— 尺不一样，不比较"
                                       % (repro_vol, published_vol)}
        return payload

    # ---- 2. 窗口表
    windows = []
    for label, bars in (("one_year_242", 242), ("two_year_484", 484),
                        ("three_year_726", 726), ("five_year_1210", 1210),
                        ("full_sample", len(pts))):
        if bars > len(pts):
            continue
        seg = pts[-bars:]
        v = vol_cny(seg, mult)
        rv = round(v, 2)          # 已发布精度；表内所有下游数都从这一枚派生，避免 5 分钱的假差异
        windows.append({
            "window": label,
            "bars": bars,
            "return_window": [dates[-bars], dates[-1]],
            "ann_vol_cny": rv,
            "ann_mean_cny": round(mean_cny(seg, mult), 0),
            "sharpe": round(mean_cny(seg, mult) / v, 4) if v else None,
            "lots_at_capital": lots_at(rv, capital, target),
            "first_rung_cny": first_rung(rv, target),
            "is_published_ruler": label == "one_year_242",
        })
    payload["vol_by_window"] = windows
    one_year = windows[0]

    # ---- 3. 滚动一年窗分布
    rolls = [vol_cny(pts[i:i + ONE_YEAR_BARS], mult)
             for i in range(0, len(pts) - ONE_YEAR_BARS + 1)]
    rolls = [r for r in rolls if r]
    s_rolls = sorted(rolls)
    budget = target / 100.0 * capital
    share_one_lot = round(100.0 * sum(1 for r in rolls if lots_at(r, capital, target) >= 1) / len(rolls), 2)
    today_pct = pct_rank(rolls, one_year["ann_vol_cny"])
    payload["rolling_one_year"] = {
        "bars_in_window": ONE_YEAR_BARS,
        "windows": len(rolls),
        "min_cny": round(s_rolls[0], 2),
        "p10_cny": round(quantile(s_rolls, 0.10), 2),
        "p25_cny": round(quantile(s_rolls, 0.25), 2),
        "median_cny": round(quantile(s_rolls, 0.50), 2),
        "p75_cny": round(quantile(s_rolls, 0.75), 2),
        "p90_cny": round(quantile(s_rolls, 0.90), 2),
        "max_cny": round(s_rolls[-1], 2),
        "today_cny": one_year["ann_vol_cny"],
        "today_percentile": today_pct,
        "windows_above_today": sum(1 for r in rolls if r >= one_year["ann_vol_cny"]),
        "share_allowing_one_lot_pct": share_one_lot,
        "share_at_or_below_budget_pct": round(100.0 * sum(1 for r in rolls if r <= budget) / len(rolls), 2),
        "note": "重叠样本（步长 1 天），是本样本上的描述性分布，不是显著性检验",
    }

    # ---- 4. 前向检验：按上一年的波动定手数，看下一年有没有顶出 8% 预算
    pairs = []
    for i in range(0, len(rolls) - ONE_YEAR_BARS):
        pairs.append((rolls[i], rolls[i + ONE_YEAR_BARS]))
    eligible = [(tr, fw) for tr, fw in pairs if lots_at(tr, capital, target) >= 1]
    breaches = [(tr, fw) for tr, fw in eligible if lots_at(tr, capital, target) * fw > budget]
    ratios = sorted(fw / tr for tr, fw in pairs)
    breach_rate = round(100.0 * len(breaches) / len(eligible), 2) if eligible else None
    forward = sorted(fw for _tr, fw in pairs)
    payload["cap_breach"] = {
        "pairs": len(pairs),
        "pairs_where_trailing_said_at_least_one_lot": len(eligible),
        "breaches": len(breaches),
        "breach_rate_pct": breach_rate,
        "lot_flip_rate_pct": round(100.0 * sum(1 for tr, fw in pairs
                                              if lots_at(tr, capital, target) != lots_at(fw, capital, target)) / len(pairs), 2),
        "forward_over_trailing_p50": round(ratios[len(ratios) // 2], 4),
        "forward_over_trailing_p90": round(quantile(ratios, 0.90), 4),
        "forward_over_trailing_p95": round(quantile(ratios, 0.95), 4),
        "forward_over_trailing_max": round(ratios[-1], 4),
        "ruler_multiplier_for_a_p90_cap": round(quantile(ratios, 0.90), 4),
        "share_of_next_years_above_todays_vol_pct": round(100.0 * sum(1 for f in forward
                                                                    if f > one_year["ann_vol_cny"]) / len(forward), 2),
        "share_of_next_years_above_ten_year_vol_pct": round(
            100.0 * sum(1 for f in forward
                        if f > next(w["ann_vol_cny"] for w in windows if w["window"] == "full_sample")) / len(forward), 2),
        "note": "重叠前向样本；越限率的语义是「按上年波动买 k 手、持有一年，实现波动把 k x vol 顶过 8% 预算」",
    }

    # ---- 5. 钱
    ten_year = next(w for w in windows if w["window"] == "full_sample")
    median_ruler_rung = first_rung(quantile(s_rolls, 0.50), target)
    release_vol = budget
    payload["money"] = {
        "capital_cny": round(capital, 2),
        "target_pct": target,
        "budget_cny": round(budget, 2),
        "lots_today": one_year["lots_at_capital"],
        "first_rung_today_cny": one_year["first_rung_cny"],
        "first_rung_ten_year_cny": ten_year["first_rung_cny"],
        "first_rung_median_year_cny": median_ruler_rung,
        "first_rung_calmest_year_cny": first_rung(s_rolls[0], target),
        "range_of_the_first_rung_cny": [median_ruler_rung, one_year["first_rung_cny"]],
        "release_vol_cny": round(release_vol, 2),
        "vol_has_to_fall_pct": round(100.0 * (1 - release_vol / one_year["ann_vol_cny"]), 2),
        "desk_lots": 4,
        "capital_for_desk_lots_today_cny": round(4 * one_year["first_rung_cny"], 2),
        "capital_for_desk_lots_ten_year_cny": round(4 * ten_year["first_rung_cny"], 2),
        "annual_mean_cny_ten_year": ten_year["ann_mean_cny"],
    }

    payload["adoption"] = dict(ADOPTION)
    verdict = judge(today_pct, share_one_lot)
    payload["judgement"] = {
        "verdict": verdict,
        "today_percentile": today_pct,
        "share_allowing_one_lot_pct": share_one_lot,
        "why": ("今日的每手年化波动 {vol:,.0f} 元落在 {n} 个滚动一年窗的第 {pct:.2f} 分位；同一本规则在历史上 "
                "{share:.2f}% 的年份会在 {cap:,.0f} 万上买至少一手，第一手门槛在中位年份是 {med:,.0f} 元、"
                "今天才是 {today:,.1f} 元").format(
            vol=one_year["ann_vol_cny"], n=len(rolls), pct=today_pct, share=share_one_lot,
            cap=capital / 10000.0, med=median_ruler_rung, today=one_year["first_rung_cny"]),
    }
    payload["cap_verdict"] = cap_verdict(breach_rate)

    payload["what_this_changes"] = [
        "{rung} 不是这本书的资本门槛，是「最近 242 天波动 {vol}、按 {tgt}% 目标折算」的今日读数："
        "同一条算术在中位年份给 {med} 元".format(
            rung="{:,.2f}".format(one_year["first_rung_cny"]),
            vol="{:,.0f}".format(one_year["ann_vol_cny"]), tgt=target,
            med="{:,.0f}".format(median_ruler_rung)),
        "100 万今天买 0 手这件事仍然对（尺是最近一年，上限是对下一年的承诺）；但同一条规则在历史上 "
        "{share:.2f}% 的年份会在 100 万上买 1 手".format(share=share_one_lot),
        "票面收回不需要新钱：波动从 {a:,.0f} 降到 {b:,.0f}（-{c:.2f}%）规则自己就还回 1 手".format(
            a=one_year["ann_vol_cny"], b=release_vol,
            c=payload["money"]["vol_has_to_fall_pct"]),
        "{tgt}% 上限不是硬墙：按上年波动定手数，下一年实现波动把它顶出去的比例是 {br:.2f}%；"
        "要让它成为 p90 意义上的上限，波动尺要乘 {m:.4f}".format(
            tgt=target, br=breach_rate,
            m=payload["cap_breach"]["ruler_multiplier_for_a_p90_cap"]),
    ]
    payload["what_is_still_missing"] = [
        "前向检验用重叠窗，独立样本远少于 %d 对——频率是描述性的，不是检验" % len(pairs),
        "没有对「下一年的波动」建模（EWMA/GARCH 都没做）；本面只量「用哪段历史」的后果",
        "IM 账户（第二腿）未同做：它的每手波动 93,259.93 同样出自 242 天窗，但腿长与主力不同",
        "点数是可加 P&L，不做复利；把一条 carry 腿滚成 CAGR 需要账户与不间断滚仓假设，本面不代读者假定",
    ]
    payload["sources"] = [OPEN_SRC, SIZING_SRC, RULER_SRC, CAP_SRC]
    payload["inputs_digest"] = {rel: _sha(rel) for rel in payload["sources"]}
    return payload


# ------------------------------------------------------------------ check
def check(payload):
    """漂移 = 重放出来的数与面上写的不同（STALE）；自相矛盾 = 面自己算错（CHECK FAILED）。"""
    fresh = build()
    fv = (fresh.get("judgement") or {}).get("verdict")
    if fv == "UNREADABLE" and (payload.get("judgement") or {}).get("verdict") != "UNREADABLE":
        return 3, ["STALE: 重放现在读不出（%s），面上写的还是上一趟的结论"
                   % (fresh.get("judgement") or {}).get("why")]

    notes = []
    for key in ("published_vol_cny", "recomputed_vol_cny", "published_first_rung_cny",
                "recomputed_first_rung_cny", "verdict", "first_rung_verdict"):
        a = (payload.get("reproduction") or {}).get(key)
        b = (fresh.get("reproduction") or {}).get(key)
        if a != b:
            notes.append("STALE: reproduction.%s 面上 %s，重放 %s" % (key, a, b))

    fa = fresh.get("vol_by_window") or []
    pa = payload.get("vol_by_window") or []
    if [w.get("window") for w in fa] != [w.get("window") for w in pa]:
        notes.append("STALE: 窗口集合变了 %s -> %s" % ([w.get("window") for w in pa],
                                                       [w.get("window") for w in fa]))
    else:
        for a, b in zip(pa, fa):
            for k in ("ann_vol_cny", "lots_at_capital", "first_rung_cny"):
                if a.get(k) != b.get(k):
                    notes.append("STALE: %s.%s 面上 %s，重放 %s" % (a.get("window"), k, a.get(k), b.get(k)))

    for block in ("rolling_one_year", "cap_breach"):
        fa_b = fresh.get(block) or {}
        pa_b = payload.get(block) or {}
        for k in sorted(fa_b):
            if k == "note":
                continue
            if pa_b.get(k) != fa_b.get(k):
                notes.append("STALE: %s.%s 面上 %s，重放 %s" % (block, k, pa_b.get(k), fa_b.get(k)))

    # 自洽（面上自己的数算出来的判词，必须等于面上写的判词）
    try:
        exp = judge((payload.get("rolling_one_year") or {}).get("today_percentile"),
                    (payload.get("rolling_one_year") or {}).get("share_allowing_one_lot_pct"))
        if exp != (payload.get("judgement") or {}).get("verdict"):
            notes.append("CHECK FAILED: 面上判词 %s 与自身 rolling 分布算出的 %s 不一致"
                         % ((payload.get("judgement") or {}).get("verdict"), exp))
        exp_cap = cap_verdict((payload.get("cap_breach") or {}).get("breach_rate_pct"))
        if exp_cap != payload.get("cap_verdict"):
            notes.append("CHECK FAILED: cap_verdict %s 与自身越限率算出的 %s 不一致"
                         % (payload.get("cap_verdict"), exp_cap))
        m = payload.get("money") or {}
        rung = first_rung((payload.get("vol_by_window") or [{}])[0].get("ann_vol_cny"),
                          m.get("target_pct"))
        if rung != m.get("first_rung_today_cny"):
            notes.append("CHECK FAILED: first_rung_today %s 与 vol/target 算出的 %s 不一致"
                         % (m.get("first_rung_today_cny"), rung))
        if (payload.get("money") or {}).get("range_of_the_first_rung_cny"):
            lo, hi = payload["money"]["range_of_the_first_rung_cny"]
            if not (lo <= hi):
                notes.append("CHECK FAILED: 门槛区间 %s 倒挂" % (payload["money"]["range_of_the_first_rung_cny"],))
    except Exception as exc:  # 面缺字段不该把 check 打成异常
        notes.append("CHECK FAILED: 自洽腿读不出（%s）" % exc)

    if notes:
        return 3, notes
    return 0, []


# ------------------------------------------------------------------- page
def write_md(p):
    L = []
    A = L.append
    m = p["money"]
    r = p["rolling_one_year"]
    cb = p["cap_breach"]
    one = (p["vol_by_window"] or [{}])[0]
    ten = next((w for w in p["vol_by_window"] if w["window"] == "full_sample"), {})
    A("# 这本书的第一手门槛，是波动读数还是资本门槛？")
    A("")
    A("> 面：`results/carry_first_rung_vol_ruler.json`（%s 生成·cutoff %s·机 %s）"
      % (p.get("generated"), p.get("evidence_cutoff"), p.get("machine")))
    A("")
    A("## 一句话")
    A("")
    A("**{rung} 元不是这本书要的资本，是「最近 {bars} 个收益日的每手年化波动 {vol} 元 ÷ {tgt}% 目标」的今日读数。**"
      "同一条算术在中位年份给 **{med} 元**——100 万今天买 {lots} 手这件事落在滚动一年窗的 "
      "**{pct:.2f} 分位**（共 {n} 个窗，只 {above} 个比它更热）。".format(
          rung="{:,.2f}".format(m["first_rung_today_cny"]), bars=one.get("bars", 0),
          vol="{:,.0f}".format(one.get("ann_vol_cny", 0)), tgt=m["target_pct"],
          med="{:,.0f}".format(m["first_rung_median_year_cny"]), lots=m["lots_today"],
          pct=r["today_percentile"], n=r["windows"], above=r["windows_above_today"]))
    A("")
    A("## 判定")
    A("")
    A("| 项 | 判词 |")
    A("| --- | --- |")
    A("| 门槛性质 | `{}` |".format(p["judgement"]["verdict"]))
    A("| {}% 上限硬度 | `{}` |".format(m["target_pct"], p["cap_verdict"]))
    A("")
    A(p["judgement"]["why"] + "。")
    A("")
    A("## 尺怎么复现的")
    A("")
    rp = p["reproduction"]
    A("| 项 | 已发布 | 本面重算 |")
    A("| --- | --- | --- |")
    A("| 每手年化波动（元） | %.2f | **%.2f** |" % (rp["published_vol_cny"], rp["recomputed_vol_cny"]))
    A("| 第一手门槛（元） | %.2f | **%.2f** |" % (rp["published_first_rung_cny"], rp["recomputed_first_rung_cny"]))
    A("")
    A("已发布窗口是 `{a}` → `{b}`（{d} 天）——起点是锚日、锚日无收益；本面的 {n} 个收益落在 "
      "`{c}`..`{e}`，两条腿逐位相同（判 {v}）。".format(
          a=rp["published_window"][0], b=rp["published_window"][1], d=rp["published_days"],
          n=rp["recomputed_bars"], c=rp["recomputed_return_window"][0],
          e=rp["recomputed_return_window"][1], v=rp["verdict"]))
    A("")
    A("## 换一段历史，门槛就是另一个数")
    A("")
    A("| 窗口 | 收益日 | 每手年化波动（元） | 100 万买几手 | 第一手门槛（元） | Sharpe |")
    A("| --- | ---: | ---: | ---: | ---: | ---: |")
    for w in p["vol_by_window"]:
        A("| {}{} | {} | {:,.0f} | {} | {:,.1f} | {:.3f} |".format(
            WINDOW_LABEL.get(w["window"], w["window"]),
            "（已发布尺）" if w.get("is_published_ruler") else "", w["bars"],
            w["ann_vol_cny"], w["lots_at_capital"], w["first_rung_cny"], w["sharpe"]))
    A("")
    A("整张表的门槛从 %s 元走到 %s 元——**%.0f 万元的钱在这条规则下能不能开这本书，取决于你从哪天开始量波动**。"
      % ("{:,.0f}".format(m["first_rung_median_year_cny"]), "{:,.1f}".format(m["first_rung_today_cny"]),
         m["capital_cny"] / 10000.0))
    A("")
    A("## 把今天放回 1724 个滚动一年窗里")
    A("")
    A("| 分位 | 每手年化波动（元） |")
    A("| --- | ---: |")
    for k, label in (("min_cny", "最小"), ("p10_cny", "p10"), ("p25_cny", "p25"),
                     ("median_cny", "中位"), ("p75_cny", "p75"), ("p90_cny", "p90"), ("max_cny", "最大")):
        A("| %s | %s |" % (label, "{:,.0f}".format(r[k])))
    A("| **今天** | **%s**（%.2f 分位）|" % ("{:,.0f}".format(r["today_cny"]), r["today_percentile"]))
    A("")
    A("历史上 **%.2f%%** 的年份在 100 万上是买得起的（预算 %s 元 ≥ 每手波动）；今天这个窗口不在其中。"
      % (r["share_allowing_one_lot_pct"], "{:,.0f}".format(m["budget_cny"])))
    A("")
    A("## 8% 上限到底有多硬")
    A("")
    A("按上一年的波动定手数、持有一年，用下一年的实现波动检验（%d 对，其中 %d 对上年说「至少 1 手」）："
      % (cb["pairs"], cb["pairs_where_trailing_said_at_least_one_lot"]))
    A("")
    A("* **越限 %d 次 = %.2f%%**——所谓硬上限，大约是四年里破一次；" % (cb["breaches"], cb["breach_rate_pct"]))
    A("* 手数年年翻转的比例 **%.2f%%**；" % cb["lot_flip_rate_pct"])
    A("* 下一年波动 / 上一年波动：中位 %.4f、p90 %.4f、p95 %.4f、最大 %.4f——要把它做成 p90 意义上的上限，"
      "波动尺要乘 **%.4f**。" % (cb["forward_over_trailing_p50"], cb["forward_over_trailing_p90"],
                                cb["forward_over_trailing_p95"], cb["forward_over_trailing_max"],
                                cb["ruler_multiplier_for_a_p90_cap"]))
    A("")
    A("## 落地的选择")
    A("")
    ad = p["adoption"]
    A("**采纳**：%s（%s）。" % (ad["decided"], ad["decided_in"]))
    A("")
    A("> %s" % ad["because"])
    A("")
    A("据此禁止两件事：")
    A("")
    for x in ad["what_the_adoption_forbids"]:
        A("* %s" % x)
    A("")
    A("未采纳的两条路也把它们的价钱印出来：")
    A("")
    for alt in ad["alternatives_not_adopted"]:
        A("* `%s`（adopted:false）—— %s" % (alt["ruler"], alt["because_not"]))
    A("")
    A("## 这对票面意味着什么")
    A("")
    for x in p["what_this_changes"]:
        A("* %s" % x)
    A("")
    A("## 还没做的")
    A("")
    for x in p["what_is_still_missing"]:
        A("* %s" % x)
    A("")
    A("## 出处与复算")
    A("")
    A("```")
    A("python scripts/carry_first_rung_vol_ruler.py            # 重生本面")
    A("python scripts/carry_first_rung_vol_ruler.py --check    # 漂移检查")
    A("python scripts/carry_first_rung_vol_ruler.py --selftest # 离线自检")
    A("```")
    A("")
    A("输入（sha256 前 12 位）：")
    A("")
    for rel, sha in sorted((p.get("inputs_digest") or {}).items()):
        A("* `%s` — `%s`" % (rel, (sha or "missing")[:12]))
    A("")
    A("乘数权威：`%s`（每点 %.0f 元）。" % (p["multiplier"]["authority"], p["multiplier"]["cny_per_point"]))
    A("")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


# --------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    # 纯函数腿
    leg("sd of a constant series is 0", abs(sd([3.0] * 50) - 0.0) < 1e-12)
    base = [1.0, -2.0, 3.5, 0.0, -1.25, 2.0, 0.5, -0.75]
    leg("vol scales linearly with the values", abs(vol_cny([2 * x for x in base], 200.0)
                                                   - 2 * vol_cny(base, 200.0)) < 1e-9)
    leg("vol scales linearly with the multiplier", abs(vol_cny(base, 400.0) - 2 * vol_cny(base, 200.0)) < 1e-9)
    leg("lots_at: 80,000/91,029 is 0 lots", lots_at(91029.0, 1_000_000.0, 8.0) == 0)
    leg("lots_at: 80,000/71,149 is 1 lot", lots_at(71149.35, 1_000_000.0, 8.0) == 1)
    leg("lots_at: 80,000/32,495 is 2 lots", lots_at(32495.0, 1_000_000.0, 8.0) == 2)
    leg("first_rung: 91,029 / 8% = 1,137,862.5", abs(first_rung(91029.0, 8.0) - 1137862.5) < 1e-6)
    leg("capital raised to the first rung buys exactly one lot",
        lots_at(91029.0, 1_000_000.0, 8.0) == 0
        and lots_at(91029.0, first_rung(91029.0, 8.0), 8.0) == 1)
    leg("pct_rank of the max element is 100 - 1/n", pct_rank([1.0, 2.0, 3.0, 4.0], 4.0) == 75.0)
    leg("quantile hits the ends", quantile([1.0, 2.0, 3.0], 0.0) == 1.0 and quantile([1.0, 2.0, 3.0], 1.0) == 3.0)

    # 判词边界腿
    leg("verdict A at the frozen boundary (p90 & 60%)",
        judge(90.0, 60.0) == "THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD")
    leg("verdict C one notch below the p90 gate",
        judge(89.9, 60.0) == "THE_FIRST_RUNG_IS_PARTLY_A_VOLATILITY_READ")
    leg("verdict B when the capital gate dominates",
        judge(70.0, 39.9) == "THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD")
    leg("cap verdict boundaries",
        cap_verdict(9.9) == "THE_EIGHT_PERCENT_CAP_HOLDS"
        and cap_verdict(20.0) == "THE_EIGHT_PERCENT_CAP_IS_BREACHED_ABOUT_ONE_YEAR_IN_FOUR"
        and cap_verdict(33.1) == "THE_EIGHT_PERCENT_CAP_IS_BREACHED_HALF_THE_TIME")
    leg("unreadable inputs never get a verdict", judge(None, 50.0) == "UNREADABLE")

    # 实盘面腿（读真实面板）
    p = build()
    v = (p.get("judgement") or {}).get("verdict")
    leg("the published ruler reproduces (91,029 and 1,137,862.5)",
        (p.get("reproduction") or {}).get("verdict") == "MATCH"
        and (p.get("reproduction") or {}).get("first_rung_verdict") == "MATCH")
    leg("the face is readable", v not in (None, "UNREADABLE"))
    leg("today sits inside its own rolling distribution",
        p["rolling_one_year"]["min_cny"] <= p["rolling_one_year"]["today_cny"] <= p["rolling_one_year"]["max_cny"])
    rolls_share = p["rolling_one_year"]["share_allowing_one_lot_pct"]
    budget = p["money"]["budget_cny"]
    leg("share_allowing_one_lot is in [0,100] and consistent with the budget",
        0.0 <= rolls_share <= 100.0 and p["rolling_one_year"]["share_at_or_below_budget_pct"] >= rolls_share)
    leg("the first rung range is not inverted",
        p["money"]["range_of_the_first_rung_cny"][0] <= p["money"]["range_of_the_first_rung_cny"][1])
    leg("the ten-year ruler is calmer than today's reading",
        p["money"]["first_rung_ten_year_cny"] <= p["money"]["first_rung_today_cny"])
    leg("a 12% vol drop is what releases one lot",
        abs(p["money"]["vol_has_to_fall_pct"] - 100.0 * (1 - budget / p["rolling_one_year"]["today_cny"])) < 0.01)
    ok_desk = p["money"]["capital_for_desk_lots_today_cny"] == round(4 * p["money"]["first_rung_today_cny"], 2)
    leg("the desk's four lots cost four times the first rung", ok_desk)

    # 行为腿：漂移必须说 STALE，自相矛盾必须说 CHECK FAILED 且不带 STALE
    tampered = json.loads(json.dumps(p))
    tampered["reproduction"]["published_vol_cny"] = p["reproduction"]["published_vol_cny"] * 1.01
    rc_b, notes_b = check(tampered)
    leg("a moved published vol is STALE", rc_b == 3 and any("STALE" in n for n in notes_b))

    tampered2 = json.loads(json.dumps(p))
    tampered2["judgement"]["verdict"] = "THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD"
    rc_c, notes_c = check(tampered2)
    leg("a flipped verdict is CHECK FAILED without the word STALE",
        rc_c == 3 and any("CHECK FAILED" in n for n in notes_c) and not any("STALE" in n for n in notes_c))

    tampered3 = json.loads(json.dumps(p))
    tampered3["money"]["first_rung_today_cny"] = 1.0
    rc_d, notes_d = check(tampered3)
    leg("a broken rung <-> vol identity is CHECK FAILED",
        rc_d == 3 and any("CHECK FAILED" in n for n in notes_d))

    ok = all(x[1] for x in legs)
    for name, res in legs:
        print(("PASS  " if res else "FAIL  ") + name)
    print("%d/%d PASS" % (sum(1 for x in legs if x[1]), len(legs)))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    payload = build()
    if (payload.get("judgement") or {}).get("verdict") == "UNREADABLE":
        print(json.dumps({"ok": False, "why": payload.get("judgement"),
                          "reproduction": payload.get("reproduction")}, ensure_ascii=False))
        return 2
    if "--check" in argv:
        rc, notes = check(payload)
        print(json.dumps({"ok": rc == 0, "notes": notes}, ensure_ascii=False))
        return rc
    payload["generated"] = _now()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(OUT_JSON) + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, OUT_JSON)
    write_md(payload)
    print(json.dumps({
        "face": str(OUT_JSON.relative_to(ROOT)),
        "page": str(OUT_MD.relative_to(ROOT)),
        "verdict": payload["judgement"]["verdict"],
        "cap_verdict": payload["cap_verdict"],
        "today_percentile": payload["rolling_one_year"]["today_percentile"],
        "share_allowing_one_lot_pct": payload["rolling_one_year"]["share_allowing_one_lot_pct"],
        "first_rung_today": payload["money"]["first_rung_today_cny"],
        "first_rung_median_year": payload["money"]["first_rung_median_year_cny"],
        "breach_rate_pct": payload["cap_breach"]["breach_rate_pct"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
