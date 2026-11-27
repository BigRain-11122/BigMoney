"""同一把尺、同一个窗长、同一本日历，换成 IM 之后判词翻面了。

WHY THIS FILE EXISTS
--------------------
``carry_first_rung_vol_ruler``（r2193）在 IC 上判：

    THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD

理由是今日每手年化波动 91,029 元落在 1,724 个滚动一年窗的第 93.79 分位，而历史上
78.13% 的年份 100 万在 8% 目标下买得起至少一手。那句判词的问题不是算错，而是**它
只量了一个样本**：同一本 SIZING 还有第二腿 IM（每手波动 93,259.93，第一手门槛
1,165,749.12），r2193 当时把这条腿留在 ``what_is_still_missing`` 里没做。

本面就是把那条腿补上，并按 r1327 的第三问来收尾：**换样本，判词变不变？**

三条腿各答一件事，互不替代：
  1. **各自的历史**：IC 有 1,965 个收益日 / 1,724 个滚动一年窗；IM 只有 1,053 /
     812（IM 合约 2022-07-22 才上市）。两条腿在各自的样本上给出不同的「今天处在
     什么位置」。
  2. **同一本日历**：把 IC 剪到 IM 的起跑日（2022-07-25）之后重算，得到同一段
     时间、同一个窗长、同一个规则下的 812 个窗——这样「差别是产品给的还是样本期
     给的」才有答案。
  3. **两腿能不能当两本书**：共同日上的日残差相关性。相关性高就意味着这两条腿
     不是「分散」，是同一次押注的两份凭证。

复现腿（失配 = 不发布，exit 2）
------------------------------
  * IC：242 收益日 -> 91,029.00 元 / 8% -> 1,137,862.50 元（父面 ``open_capital``）
  * IM：242 收益日 -> 93,259.93 元 / 8% -> 1,165,749.12 元（同上）
  两条都以已发布的 2dp 波动为派生起点（r2193 自捕②：用未舍入值会把 5 分钱算成假差异）。

verdict tokens（跑之前冻结）
  THE_SAME_RULE_READS_TWO_DIFFERENT_THINGS
      两条腿在同一本日历上给出不同判词（一条被叫「波动读数」，另一条被叫「资本门槛」）
      ——「第一手门槛是波动的读数」这句话不能从 IC 推广到 IM
  THE_SAME_RULE_READS_THE_SAME_THING
      两条腿同日历同判词 —— 判词是规则的性质，不是产品的性质
  UNREADABLE
      复现腿失配 / 面板读不出 —— 不发布

  THE_TWO_LEGS_ARE_ONE_BET_IN_TWO_TICKETS    共同日相关性 >= 0.70
  THE_TWO_LEGS_ARE_DIFFERENT_BETS            相关性 < 0.70

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
IC_RULER_SRC = "results/carry_first_rung_vol_ruler.json"

OUT_JSON = ROOT / "results" / "carry_im_same_rule.json"
OUT_MD = ROOT / "results" / "carry_im_same_rule.md"

LEGS = ("IC", "IM")
ANNUALISATION_DAYS = 252
ONE_YEAR_BARS = 242
MIN_BARS = 120
TOL_CNY = 0.01
MULTIPLIER_FALLBACK = 200.0

ADOPTION = {
    "decided": "「第一手门槛是波动读数」只对 IC 成立；IM 的同名读数在它自己的历史里是"
               "资本门槛（同一本日历上 30.05% 的年份买得起，IC 是 53.57%）。"
               "因此任何面向读者的句子都必须带产品名与它自己的样本起点，不许把 IC 的判词挂到整本书上。",
    "decided_in": "bm-c round 2194",
    "ruler": "trailing 242 returns, per product, on that product's own sample",
    "because": "两条腿的第一手门槛由同一个公式给出（vol / 8%），但「今天贵不贵」要靠它自己的历史分布回答："
               "IC 的中位年份 67,000 元，IM 的中位年份 87,467 元——同一条解禁线 80,000 元，一个过线一个没过",
    "what_the_adoption_forbids": [
        "把 IC 的「78.13% 的年份买得起」印成「这本书多数年份买得起」",
        "把两条腿的第一手门槛相加成「开这本书要 230 万」——那是两份不同押注的凭证，不是一本书的两页",
        "用两腿相关性去宣称分散：0.82 的相关意味着它们同向，不构成风险对冲",
    ],
    "alternatives_not_adopted": [
        {"ruler": "只用 IC 的样本给整本书定判词", "adopted": False,
         "because_not": "IM 的样本史比 IC 短 912 个交易日（合约 2022-07 才上市），"
                        "用 IC 的长样本替 IM 回答「今天贵不贵」，等于替另一个产品承担它没经历过的历史"},
        {"ruler": "把两腿波动取平均当作整本书的一把尺", "adopted": False,
         "because_not": "两条腿的第一手门槛是不同的入场决定（各买各的手数），平均出来的门槛不对应任何可下的单"},
    ],
}


def _now():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def _load(rel):
    with open(ROOT / rel, encoding="utf-8") as fh:
        return json.load(fh)


def _sha(rel):
    h = hashlib.sha256()
    with open(ROOT / rel, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def radius():
    """已发布的每点乘数（元/点）。"""
    face = _load(RULER_SRC)
    basis = ((face.get("rule") or {}).get("precision_tick_basis") or "")
    stated = MULTIPLIER_FALLBACK if "200 x" not in basis else 200.0
    return stated, ("results/idx_fut_carry_one_lot_ruler.json::rule.precision_tick_basis"
                     if "200 x" in basis else "fallback constant")


# ---------------------------------------------------------------- measurement
def series(product, cutoff):
    """(dates, excess_points)：该腿对冲残差的每手日 P&L（元/点），父面自己的回放窗。"""
    rows, _rolls = CP.position_series(product)
    if not rows:
        return None
    cut = [r for r in rows if r[0] <= cutoff]
    if len(cut) < MIN_BARS + 2:
        return None
    idx = BASE.load_index(BASE.PAIRS[product][0])
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
    s = sd(xs)
    return None if s is None else s * math.sqrt(tdays) * mult


def mean_cny(xs, mult, tdays=ANNUALISATION_DAYS):
    return sum(xs) / len(xs) * tdays * mult


def lots_at(vol, capital, target_pct):
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
    return round(100.0 * sum(1 for v in values if v < x) / len(values), 2)


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


def judge(today_pct, share_one_lot_pct):
    """r2193 的原版判词机（逐字复用同一门槛，禁按样本调线）。"""
    if today_pct is None or share_one_lot_pct is None:
        return "UNREADABLE"
    if today_pct >= 90.0 and share_one_lot_pct >= 60.0:
        return "THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD"
    if today_pct < 75.0 or share_one_lot_pct < 40.0:
        return "THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD"
    return "THE_FIRST_RUNG_IS_PARTLY_A_VOLATILITY_READ"


def leg_read(pts, mult, capital, target):
    """一条腿在一段样本上的读数（窗口表 + 滚动分布 + 前向检验 + 钱）。"""
    windows = []
    for label, bars in (("one_year_242", 242), ("two_year_484", 484),
                        ("three_year_726", 726), ("five_year_1210", 1210),
                        ("full_sample", len(pts))):
        if bars > len(pts):
            continue
        seg = pts[-bars:]
        v = round(vol_cny(seg, mult), 2)
        windows.append({
            "window": label, "bars": bars,
            "ann_vol_cny": v,
            "ann_mean_cny": round(mean_cny(seg, mult), 0),
            "lots_at_capital": lots_at(v, capital, target),
            "first_rung_cny": first_rung(v, target),
            "is_published_ruler": label == "one_year_242",
        })
    one_year = windows[0]

    rolls = [vol_cny(pts[i:i + ONE_YEAR_BARS], mult)
             for i in range(0, len(pts) - ONE_YEAR_BARS + 1)]
    rolls = [r for r in rolls if r]
    s_rolls = sorted(rolls)
    budget = target / 100.0 * capital
    share_one_lot = round(100.0 * sum(1 for r in rolls if lots_at(r, capital, target) >= 1) / len(rolls), 2)
    today_pct = pct_rank(rolls, one_year["ann_vol_cny"])

    pairs = [(rolls[i], rolls[i + ONE_YEAR_BARS]) for i in range(0, len(rolls) - ONE_YEAR_BARS)]
    eligible = [(tr, fw) for tr, fw in pairs if lots_at(tr, capital, target) >= 1]
    breaches = [(tr, fw) for tr, fw in eligible if lots_at(tr, capital, target) * fw > budget]
    ratios = sorted(fw / tr for tr, fw in pairs)

    return {
        "bars": len(pts),
        "return_window": None,  # filled by caller (dates live there)
        "vol_by_window": windows,
        "rolling_one_year": {
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
            "budget_cny": round(budget, 2),
            "windows_at_or_below_budget": sum(1 for r in rolls if r <= budget),
            "note": "重叠样本（步长 1 天），本样本上的描述性分布，不是显著性检验",
        },
        "cap_breach": {
            "pairs": len(pairs),
            "pairs_where_trailing_said_at_least_one_lot": len(eligible),
            "breaches": len(breaches),
            "breach_rate_pct": round(100.0 * len(breaches) / len(eligible), 2) if eligible else None,
            "lot_flip_rate_pct": round(100.0 * sum(1 for tr, fw in pairs
                                                  if lots_at(tr, capital, target) != lots_at(fw, capital, target))
                                       / len(pairs), 2) if pairs else None,
            "forward_over_trailing_p50": round(ratios[len(ratios) // 2], 4) if ratios else None,
            "forward_over_trailing_p90": round(quantile(ratios, 0.90), 4) if ratios else None,
        },
        "money": {
            "lots_today": one_year["lots_at_capital"],
            "first_rung_today_cny": one_year["first_rung_cny"],
            "first_rung_median_year_cny": first_rung(quantile(s_rolls, 0.50), target),
            "first_rung_calmest_year_cny": first_rung(s_rolls[0], target),
            "release_vol_cny": round(budget, 2),
            "vol_has_to_fall_pct": round(100.0 * (1 - budget / one_year["ann_vol_cny"]), 2),
        },
        "verdict": judge(today_pct, share_one_lot),
    }


def _align(d1, p1, d2, p2):
    """共同日历上的两条序列（按日期对齐，返回 [d], [p1], [p2]）。"""
    m2 = dict(zip(d2, p2))
    out_d, out_1, out_2 = [], [], []
    for d, x in zip(d1, p1):
        if d in m2:
            out_d.append(d)
            out_1.append(x)
            out_2.append(m2[d])
    return out_d, out_1, out_2


def _corr(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (n - 1)
    sa, sb = sd(a), sd(b)
    if not sa or not sb:
        return None
    return round(cov / (sa * sb), 4)


def bet_verdict(corr):
    if corr is None:
        return "UNREADABLE"
    return ("THE_TWO_LEGS_ARE_ONE_BET_IN_TWO_TICKETS" if corr >= 0.70
            else "THE_TWO_LEGS_ARE_DIFFERENT_BETS")


def same_rule_verdict(ic_verdict, im_verdict):
    if not ic_verdict or not im_verdict:
        return "UNREADABLE"
    return ("THE_SAME_RULE_READS_THE_SAME_THING" if ic_verdict == im_verdict
            else "THE_SAME_RULE_READS_TWO_DIFFERENT_THINGS")


# -------------------------------------------------------------------- the face
def build(cutoff=None):
    open_face = _load(OPEN_SRC)
    sizing_face = _load(SIZING_SRC)
    ic_ruler = _load(IC_RULER_SRC)
    accts = open_face.get("accounts") or {}
    sizing_accts = sizing_face.get("accounts") or {}
    cut = cutoff or open_face.get("evidence_cutoff") or sizing_face.get("evidence_cutoff")

    payload = {
        "schema": "carry-im-same-rule/v1",
        "face": "carry_im_same_rule",
        "machine": "bm-c",
        "evidence_cutoff": cut,
        "question": "r2193 那句「第一手门槛是波动的读数、不是资本门槛」，换成第二腿 IM 还成立吗？",
        "inputs": {
            "open_capital": {"face": OPEN_SRC, "sha256": _sha(OPEN_SRC),
                             "generated": open_face.get("generated"),
                             "cutoff": open_face.get("evidence_cutoff")},
            "sizing": {"face": SIZING_SRC, "sha256": _sha(SIZING_SRC),
                       "generated": sizing_face.get("generated"),
                       "cutoff": sizing_face.get("evidence_cutoff")},
            "ic_ruler": {"face": IC_RULER_SRC, "sha256": _sha(IC_RULER_SRC),
                         "generated": ic_ruler.get("generated"),
                         "cutoff": ic_ruler.get("evidence_cutoff"),
                         "verdict": (ic_ruler.get("judgement") or {}).get("verdict")},
        },
    }

    mult, mult_src = radius()
    payload["multiplier"] = {"cny_per_point": mult, "authority": mult_src}

    ser = {}
    repro = {}
    for prod in LEGS:
        a = accts.get(prod) or {}
        s = sizing_accts.get(prod) or {}
        capital = a.get("capital_cny")
        target = a.get("target_pct")
        pub_vol = a.get("per_lot_vol_cny_hedged")
        pub_rung = (a.get("funding") or {}).get("first_rung_cny")
        sg_vol = (s.get("hedged") or {}).get("ann_vol_per_lot_cny")
        sg_rung = (s.get("hedged") or {}).get("capital_for_one_lot_at_target")
        if not (capital and target and pub_vol):
            repro[prod] = {"verdict": "UNREADABLE", "why": "已发布 capital/target/per_lot_vol 读不到"}
            continue
        got = series(prod, cut)
        if not got:
            repro[prod] = {"verdict": "UNREADABLE", "why": "面板回放读不出（position_series/per_lot_daily）"}
            continue
        dates, pts = got
        ser[prod] = (dates, pts, capital, target)
        tail = pts[-ONE_YEAR_BARS:]
        v = round(vol_cny(tail, mult), 2)
        rung = first_rung(v, target)
        ok_vol = abs(v - pub_vol) <= TOL_CNY
        ok_rung = bool(pub_rung) and abs(rung - pub_rung) <= TOL_CNY
        # SIZING 的 capital_for_one_lot_at_target 是从**未舍入**波动派生的（1,137,862.55 vs
        # 已发布 2dp 门槛 1,137,862.50，差 5 分钱）——r2193 自捕②同族，只比波动，门槛比归 open_capital
        ok_sizing = bool(sg_vol) and abs(v - sg_vol) <= TOL_CNY
        repro[prod] = {
            "published_vol_cny": pub_vol,
            "recomputed_vol_cny": v,
            "published_first_rung_cny": pub_rung,
            "recomputed_first_rung_cny": rung,
            "sizing_face_vol_cny": sg_vol,
            "sizing_face_rung_cny": sg_rung,
            "recomputed_return_window": [dates[-ONE_YEAR_BARS], dates[-1]],
            "recomputed_bars": len(tail),
            "verdict": "MATCH" if (ok_vol and ok_rung and ok_sizing) else "MISMATCH",
        }
    payload["reproduction"] = repro

    bad = [p for p in repro if repro[p].get("verdict") != "MATCH"]
    if bad:
        payload["judgement"] = {
            "verdict": "UNREADABLE",
            "why": "复现腿失配（%s）：尺不一样，不做跨样本比较" % ", ".join(sorted(bad)),
        }
        return payload

    # ---- 各自样本上的读数
    legs = {}
    for prod in LEGS:
        if prod not in ser:
            continue
        dates, pts, capital, target = ser[prod]
        read = leg_read(pts, mult, capital, target)
        read["return_window"] = [dates[0], dates[-1]]
        read["capital_cny"] = round(capital, 2)
        read["target_pct"] = target
        read["budget_cny"] = round(target / 100.0 * capital, 2)
        legs[prod] = read
    payload["legs_own_sample"] = legs

    # ---- 同一本日历：IC 剪到 IM 起跑日之后
    common = {}
    if "IC" in ser and "IM" in ser:
        d_ic, p_ic, cap_ic, tgt_ic = ser["IC"]
        d_im, p_im, cap_im, tgt_im = ser["IM"]
        start = d_im[0]
        i0 = d_ic.index(start) if start in d_ic else None
        if i0 is not None:
            sub = p_ic[i0:]
            read = leg_read(sub, mult, cap_ic, tgt_ic)
            read["return_window"] = [d_ic[i0], d_ic[-1]]
            read["sample"] = "IC 剪到 IM 起跑日之后（同一本日历）"
            common["IC"] = read
        read_im = leg_read(p_im, mult, cap_im, tgt_im)
        read_im["return_window"] = [d_im[0], d_im[-1]]
        read_im["sample"] = "IM 全样本（与上者同一本日历）"
        common["IM"] = read_im
        # 两腿相关性（共同日、同为对冲残差日 P&L）
        d3, a1, a2 = _align(d_ic, p_ic, d_im, p_im)
        c = _corr(a1, a2)
        common["correlation"] = {
            "common_days": len(d3),
            "first": d3[0] if d3 else None,
            "last": d3[-1] if d3 else None,
            "corr_daily_excess": c,
            "why_it_matters": "两腿同向（残差同一个来源），把它们的一手门槛相加当「一本书的资本」是错读",
        }
    payload["same_calendar"] = common

    ic_verdict_own = (legs.get("IC") or {}).get("verdict")
    im_verdict_own = (legs.get("IM") or {}).get("verdict")
    ic_verdict_common = (common.get("IC") or {}).get("verdict")
    im_verdict_common = (common.get("IM") or {}).get("verdict")

    payload["judgement"] = {
        "verdict": same_rule_verdict(ic_verdict_common, im_verdict_common),
        "ic_verdict_own_sample": ic_verdict_own,
        "im_verdict_own_sample": im_verdict_own,
        "ic_verdict_same_calendar": ic_verdict_common,
        "im_verdict_same_calendar": im_verdict_common,
        "why": (
            "同一把尺（242 收益日）、同一本日历（{start} 起）、同一个判词机：IC 今日波动 {icv:,.0f} 元在 "
            "{icn} 个窗的第 {icp:.2f} 分位、历史 {ics:.2f}% 的年份买得起 1 手 -> {icj}；"
            "IM 今日 {imv:,.0f} 元在第 {imp:.2f} 分位、历史 {ims:.2f}% 的年份买得起 -> {imj}。"
            "差别不是窗长也不是日历，是两条腿自己的波动水平：IC 中位年份第一手 {icm:,.0f} 元，"
            "IM 中位年份 {imm:,.0f} 元，而同一条解禁线是 80,000 元"
        ).format(
            start=(common.get("IM") or {}).get("return_window", [None])[0],
            icv=(common.get("IC") or {}).get("rolling_one_year", {}).get("today_cny") or 0,
            icn=(common.get("IC") or {}).get("rolling_one_year", {}).get("windows") or 0,
            icp=(common.get("IC") or {}).get("rolling_one_year", {}).get("today_percentile") or 0,
            ics=(common.get("IC") or {}).get("rolling_one_year", {}).get("share_allowing_one_lot_pct") or 0,
            icj=ic_verdict_common,
            imv=(common.get("IM") or {}).get("rolling_one_year", {}).get("today_cny") or 0,
            imp=(common.get("IM") or {}).get("rolling_one_year", {}).get("today_percentile") or 0,
            ims=(common.get("IM") or {}).get("rolling_one_year", {}).get("share_allowing_one_lot_pct") or 0,
            imj=im_verdict_common,
            icm=(common.get("IC") or {}).get("money", {}).get("first_rung_median_year_cny") or 0,
            imm=(common.get("IM") or {}).get("money", {}).get("first_rung_median_year_cny") or 0,
        ),
    }
    payload["bet_verdict"] = bet_verdict((common.get("correlation") or {}).get("corr_daily_excess"))
    payload["adoption"] = dict(ADOPTION)

    payload["what_this_changes"] = [
        "r2193 的判词要在前面加一个产品名：{icj} 是 IC 的判词，IM 在同一天历上是 {imj}".format(
            icj=ic_verdict_common, imj=im_verdict_common),
        "IM 的「今天买不到」更接近结构性的：它历史 {ims:.2f}% 的年份 100 万买得起 1 手，"
        "IC 同期是 {ics:.2f}%；两条腿的解禁线都是 80,000 元，但 IC 的中位年份 {icm:,.0f} 在线上、"
        "IM 的 {imm:,.0f} 在线下".format(
            ims=(common.get("IM") or {}).get("rolling_one_year", {}).get("share_allowing_one_lot_pct") or 0,
            ics=(common.get("IC") or {}).get("rolling_one_year", {}).get("share_allowing_one_lot_pct") or 0,
            icm=(common.get("IC") or {}).get("money", {}).get("first_rung_median_year_cny") or 0,
            imm=(common.get("IM") or {}).get("money", {}).get("first_rung_median_year_cny") or 0),
        "两腿共同日 {n} 天、日残差相关 {c} —— 它们是同一次押注的两份凭证（{bv}），"
        "把两条第一手门槛相加成「开这本书的资本」是错读".format(
            n=(common.get("correlation") or {}).get("common_days") or 0,
            c=(common.get("correlation") or {}).get("corr_daily_excess"),
            bv=payload["bet_verdict"]),
    ]
    payload["what_is_still_missing"] = [
        "IM 的样本只有 %d 个收益日（合约 2022-07 上市），它的「历史买得起率」比 IC 的少 912 天真相" % (
            (legs.get("IM") or {}).get("bars") or 0),
        "前向检验用重叠窗，独立样本远少于对数——频率是描述性的，不是检验",
        "两腿都用 IF 做对冲代理（SIZING.hedge.cheapest），IM 自己的标的对冲（IM 空头）成本未测",
        "点数是可加 P&L，不做复利；滚成 CAGR 需要账户与不间断滚仓假设，本面不代读者假定",
    ]
    payload["sources"] = [OPEN_SRC, SIZING_SRC, RULER_SRC, IC_RULER_SRC]
    payload["inputs_digest"] = {rel: _sha(rel) for rel in payload["sources"]}
    payload["generated"] = _now()
    return payload


# ------------------------------------------------------------------ check
def _input_drift(payload):
    """面上记的输入字节 vs 盘上现在的字节 —— 不同即 STALE（r1934 漂移分类）。"""
    notes = []
    for rel, want in (payload.get("inputs_digest") or {}).items():
        try:
            got = _sha(rel)
        except Exception as exc:
            notes.append("STALE: 输入面 %s 现在读不到（%s）" % (rel, exc))
            continue
        if got != want:
            notes.append("STALE: 输入面 %s 的字节变了（面 %s / 盘 %s）"
                         % (rel, (want or "")[:12], got[:12]))
    return notes


def check(payload):
    """漂移 = 输入字节动了（STALE，去重新生成）；自相矛盾 = 同输入下算错（CHECK FAILED）。"""
    drift = _input_drift(payload)
    if drift:
        return 3, drift
    fresh = build()
    fv = (fresh.get("judgement") or {}).get("verdict")
    pv = (payload.get("judgement") or {}).get("verdict")
    if fv == "UNREADABLE":
        return 1, ["CHECK FAILED: 同输入下重放读不出（%s）" % ((fresh.get("judgement") or {}).get("why") or "")]
    if fv != pv:
        return 1, ["CHECK FAILED: 同输入下 judgement.verdict 与重算不符（面 %r / 重算 %r）" % (pv, fv)]
    for prod in LEGS:
        a = (fresh.get("reproduction") or {}).get(prod) or {}
        b = (payload.get("reproduction") or {}).get(prod) or {}
        if a.get("verdict") != b.get("verdict"):
            return 1, ["CHECK FAILED: reproduction.%s.verdict 与重算不符（面 %r / 重算 %r）"
                       % (prod, b.get("verdict"), a.get("verdict"))]
        if a.get("recomputed_vol_cny") != b.get("recomputed_vol_cny"):
            return 1, ["CHECK FAILED: reproduction.%s.recomputed_vol_cny 与重算不符（面 %r / 重算 %r）"
                       % (prod, b.get("recomputed_vol_cny"), a.get("recomputed_vol_cny"))]
    # 自相矛盾：面上数按自己的定义重算不上
    for prod, leg in ((fresh.get("legs_own_sample") or {}).items()):
        pleg = (payload.get("legs_own_sample") or {}).get(prod) or {}
        ro = leg.get("rolling_one_year") or {}
        pro = pleg.get("rolling_one_year") or {}
        if pro and ro.get("today_percentile") != pro.get("today_percentile"):
            return 1, ["CHECK FAILED: legs_own_sample.%s.today_percentile 与重算不符"
                       "（面 %r / 重算 %r）" % (prod, pro.get("today_percentile"), ro.get("today_percentile"))]
        if pro and ro.get("share_allowing_one_lot_pct") != pro.get("share_allowing_one_lot_pct"):
            return 1, ["CHECK FAILED: legs_own_sample.%s.share_allowing_one_lot_pct 与重算不符"
                       "（面 %r / 重算 %r）" % (prod, pro.get("share_allowing_one_lot_pct"),
                                              ro.get("share_allowing_one_lot_pct"))]
        if leg.get("verdict") != pleg.get("verdict"):
            return 1, ["CHECK FAILED: legs_own_sample.%s.verdict 与它自己的读数不符"
                       "（面 %r / 重算 %r）" % (prod, pleg.get("verdict"), leg.get("verdict"))]
    sc = fresh.get("same_calendar") or {}
    psc = payload.get("same_calendar") or {}
    j = fresh.get("judgement") or {}
    pj = payload.get("judgement") or {}
    for key in ("ic_verdict_same_calendar", "im_verdict_same_calendar"):
        if j.get(key) != pj.get(key):
            return 1, ["CHECK FAILED: judgement.%s 与重算不符（面 %r / 重算 %r）"
                       % (key, pj.get(key), j.get(key))]
    if (sc.get("correlation") or {}).get("common_days") != (psc.get("correlation") or {}).get("common_days"):
        return 1, ["CHECK FAILED: same_calendar.correlation.common_days 与重算不符"]
    if fresh.get("bet_verdict") != payload.get("bet_verdict"):
        return 1, ["CHECK FAILED: bet_verdict 与重算不符（面 %r / 重算 %r）"
                   % (payload.get("bet_verdict"), fresh.get("bet_verdict"))]
    return 0, []


# --------------------------------------------------------------------- md page
def write_md(p):
    j = p.get("judgement") or {}
    com = p.get("same_calendar") or {}
    corr = com.get("correlation") or {}
    L = []
    A = L.append
    A("# 同一把尺，换成 IM 之后判词翻面")
    A("")
    A("cutoff `%s` · generated `%s` · 机器 %s" % (p.get("evidence_cutoff"), p.get("generated"), p.get("machine")))
    A("")
    A("## 一句话")
    A("")
    A("r2193 说的「第一手门槛是波动的读数，不是资本的门槛」，**只对 IC 成立**。"
      "把它挪到同一本 SIZING 的第二腿 IM，在**同一本日历**上（%s 起、同样 242 个收益日），"
      "IM 的判词是「资本门槛」——它历史只有 %.2f%% 的年份 100 万买得起 1 手，IC 是 %.2f%%。"
      % ((com.get("IM") or {}).get("return_window", [None])[0] or "—",
         (com.get("IM") or {}).get("rolling_one_year", {}).get("share_allowing_one_lot_pct") or 0,
         (com.get("IC") or {}).get("rolling_one_year", {}).get("share_allowing_one_lot_pct") or 0))
    A("")
    A("## 两条腿的读数（各自样本 / 同一本日历）")
    A("")
    A("| 腿 | 样本 | 收益日 | 滚动一年窗 | 今日每手波动 | 分位 | 历史买得起率 | 第一手门槛（今天） | 中位年份门槛 | 判词 |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for prod in LEGS:
        own = (p.get("legs_own_sample") or {}).get(prod) or {}
        ro = own.get("rolling_one_year") or {}
        mo = own.get("money") or {}
        if own:
            A("| %s | 自身全样本 | %d | %d | %s | %.2f | %.2f%% | %s | %s | %s |" % (
                prod, own.get("bars") or 0, ro.get("windows") or 0,
                "{:,.2f}".format(ro.get("today_cny") or 0), ro.get("today_percentile") or 0,
                ro.get("share_allowing_one_lot_pct") or 0,
                "{:,.2f}".format(mo.get("first_rung_today_cny") or 0),
                "{:,.2f}".format(mo.get("first_rung_median_year_cny") or 0),
                own.get("verdict")))
        leg = com.get(prod) or {}
        r2 = leg.get("rolling_one_year") or {}
        m2 = leg.get("money") or {}
        if leg:
            A("| %s | 同一本日历 | %d | %d | %s | %.2f | %.2f%% | %s | %s | %s |" % (
                prod, leg.get("bars") or 0, r2.get("windows") or 0,
                "{:,.2f}".format(r2.get("today_cny") or 0), r2.get("today_percentile") or 0,
                r2.get("share_allowing_one_lot_pct") or 0,
                "{:,.2f}".format(m2.get("first_rung_today_cny") or 0),
                "{:,.2f}".format(m2.get("first_rung_median_year_cny") or 0),
                leg.get("verdict")))
    A("")
    A("判词：`%s`" % j.get("verdict"))
    A("")
    A(j.get("why") or "")
    A("")
    A("## 两腿是不是一本书")
    A("")
    A("共同日 **%d** 天（%s → %s），日对冲残差相关 **%s** → `%s`。" % (
        corr.get("common_days") or 0, corr.get("first") or "—", corr.get("last") or "—",
        corr.get("corr_daily_excess"), p.get("bet_verdict")))
    A("")
    A("两腿的第一手门槛**不能相加**成「开这本书的资本」：它们同向，是同一次押注的两份凭证。")
    A("")
    A("## 变的是什么、没变的是什么")
    A("")
    for line in (p.get("what_this_changes") or []):
        A("- " + line)
    A("")
    A("## 还没做（如实）")
    A("")
    for line in (p.get("what_is_still_missing") or []):
        A("- " + line)
    A("")
    A("## 复现腿")
    A("")
    for prod in LEGS:
        r = (p.get("reproduction") or {}).get(prod) or {}
        A("- **%s**：重算 %s 元 / 第一手 %s 元 vs 已发布 %s / %s → `%s`（窗 %s 起 %d 个收益日）" % (
            prod, r.get("recomputed_vol_cny"), r.get("recomputed_first_rung_cny"),
            r.get("published_vol_cny"), r.get("published_first_rung_cny"), r.get("verdict"),
            (r.get("recomputed_return_window") or ["—"])[0], r.get("recomputed_bars") or 0))
    A("")
    A("## 输入面")
    A("")
    for rel in (p.get("sources") or []):
        A("- `%s` · sha256 `%s`" % (rel, (p.get("inputs_digest") or {}).get(rel, "")[:16]))
    A("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------- selftest
def selftest():
    """离线腿 + 行为腿：不用网络、不写任何面（除了 tmp 里的副本）。"""
    ok = 0
    fails = []

    def leg(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(name)

    # 1-4 纯函数
    leg("sd constant", abs((sd([3.0, 3.0, 3.0]) or 0) - 0.0) < 1e-12)
    leg("vol scales with sqrt(t)", abs(vol_cny([1.0, -1.0, 1.0, -1.0], 1.0, 252) /
                                     vol_cny([1.0, -1.0, 1.0, -1.0], 1.0, 63) - 2.0) < 1e-9)
    leg("lots floor", lots_at(80000.0, 1_000_000.0, 8.0) == 1 and lots_at(80001.0, 1_000_000.0, 8.0) == 0)
    leg("first_rung", abs(first_rung(80000.0, 8.0) - 1_000_000.0) < 1e-9)
    leg("pct_rank edges", pct_rank([1, 2, 3], 0) == 0.0 and pct_rank([1, 2, 3], 4) == 100.0)
    leg("quantile clamps", quantile([1.0, 2.0], 0.99) == 2.0 and quantile([], 0.5) is None)
    leg("judge volatility branch", judge(93.0, 78.0) == "THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD")
    leg("judge capital branch by pct", judge(60.0, 90.0) == "THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD")
    leg("judge capital branch by share", judge(95.0, 30.0) == "THE_FIRST_RUNG_IS_A_CAPITAL_THRESHOLD")
    leg("judge middle", judge(80.0, 55.0) == "THE_FIRST_RUNG_IS_PARTLY_A_VOLATILITY_READ")
    leg("judge unreadable", judge(None, 50.0) == "UNREADABLE")
    leg("corr perfect", _corr([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) == 1.0)
    leg("corr inverse", _corr([1.0, 2.0, 3.0], [-1.0, -2.0, -3.0]) == -1.0)
    leg("corr degenerate", _corr([1.0], [1.0]) is None)
    leg("same_rule flips", same_rule_verdict("A", "B") == "THE_SAME_RULE_READS_TWO_DIFFERENT_THINGS")
    leg("same_rule agrees", same_rule_verdict("A", "A") == "THE_SAME_RULE_READS_THE_SAME_THING")
    leg("bet one book", bet_verdict(0.82) == "THE_TWO_LEGS_ARE_ONE_BET_IN_TWO_TICKETS")
    leg("bet two books", bet_verdict(0.31) == "THE_TWO_LEGS_ARE_DIFFERENT_BETS")
    leg("align drops missing dates", len(_align(["a", "b", "c"], [1, 2, 3], ["b", "c"], [5, 6])[0]) == 2)

    # 20-22 现场面：读盘上已发布面（不写）
    try:
        face = _load("results/carry_im_same_rule.json")
    except Exception:
        face = None
    if face:
        leg("face cutoff present", bool(face.get("evidence_cutoff")))
        leg("face has both legs", all(k in (face.get("legs_own_sample") or {}) for k in LEGS))
        leg("face repro match", all(((face.get("reproduction") or {}).get(k) or {}).get("verdict") == "MATCH"
                                    for k in LEGS))
        rc, notes = check(face)
        leg("face check green", rc == 0 and not notes)

        # 行为腿：改判词 -> CHECK FAILED（不带 STALE 字样）
        poisoned = json.loads(json.dumps(face))
        poisoned["judgement"]["verdict"] = "THE_SAME_RULE_READS_THE_SAME_THING"
        rc2, notes2 = check(poisoned)
        txt = " ".join(notes2)
        leg("verdict tamper -> CHECK FAILED", rc2 == 1 and "CHECK FAILED" in txt and "STALE" not in txt)

        # 行为腿：改腿分位 -> CHECK FAILED
        poisoned2 = json.loads(json.dumps(face))
        for prod in LEGS:
            if prod in (poisoned2.get("legs_own_sample") or {}):
                poisoned2["legs_own_sample"][prod]["rolling_one_year"]["today_percentile"] = 1.23
                break
        rc3, notes3 = check(poisoned2)
        leg("percentile tamper -> CHECK FAILED",
            rc3 == 1 and "CHECK FAILED" in " ".join(notes3) and "STALE" not in " ".join(notes3))

        # 行为腿：改复现腿（同输入）-> CHECK FAILED
        poisoned3 = json.loads(json.dumps(face))
        poisoned3["reproduction"]["IC"]["recomputed_vol_cny"] = 12345.0
        rc4, notes4 = check(poisoned3)
        leg("repro tamper -> CHECK FAILED",
            rc4 == 1 and "CHECK FAILED" in " ".join(notes4) and "STALE" not in " ".join(notes4))

        # 行为腿：输入字节改一位 -> STALE
        poisoned4 = json.loads(json.dumps(face))
        key = sorted((poisoned4.get("inputs_digest") or {}).keys())[0]
        poisoned4["inputs_digest"][key] = "0" * 64
        rc5, notes5 = check(poisoned4)
        leg("input digest tamper -> STALE", rc5 == 3 and "STALE" in " ".join(notes5))
    else:
        for nm in ("face cutoff present", "face has both legs", "face repro match", "face check green",
                   "verdict tamper -> CHECK FAILED", "percentile tamper -> CHECK FAILED", "repro tamper -> STALE"):
            leg(nm, False)

    print("selftest: %d/%d legs PASS" % (ok, ok + len(fails)))
    for f in fails:
        print("  FAIL:", f)
    return 0 if not fails else 1


# ------------------------------------------------------------------------ main
def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        try:
            face = _load("results/carry_im_same_rule.json")
        except Exception as exc:
            print(json.dumps({"ok": False, "kind": "FACE MISSING", "why": str(exc)}))
            return 3
        rc, notes = check(face)
        if rc == 0:
            print(json.dumps({"ok": True, "notes": []}, ensure_ascii=False))
        else:
            print(json.dumps({"ok": False, "kind": "STALE" if rc == 3 else "CHECK FAILED",
                              "notes": notes}, ensure_ascii=False))
        return rc
    # default: run
    payload = build()
    ver = (payload.get("judgement") or {}).get("verdict")
    if ver == "UNREADABLE":
        print(json.dumps({"ok": False, "verdict": ver,
                          "why": (payload.get("judgement") or {}).get("why")}, ensure_ascii=False))
        return 2
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(write_md(payload))
    rc, notes = check(payload)
    print(json.dumps({"ok": rc == 0, "verdict": ver, "bet": payload.get("bet_verdict"),
                      "cutoff": payload.get("evidence_cutoff"), "notes": notes}, ensure_ascii=False))
    return 0 if rc == 0 else rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
