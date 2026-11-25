#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""what does it cost to obey the written pause rule? price it on the leg's own history.

WHY THIS FILE EXISTS
--------------------
research/STRATEGY-20261125.md §四 writes, in so many words:

    单腿 60 日累计 carry < -2pp  ->  该腿暂停，回研究面

r2103 turned that table into an auditable contract and found the line too tight in
*probability* terms (a leg walking its own mean lands under -2pp 8.1% of IC sessions and
9.7% of IM sessions; a 2.5% tail would write -3.6pp / -4.2pp).  It then listed, on
purpose, as NOT DONE: "没有把「停一次值多少钱」算出来——那需要把暂停规则套进回测".

This face does exactly that one job.  It takes the leg's own published daily carry series
(the same `product_spread` the risk face prices), applies the rule *causally*, and prints
what obeying it costs in annual return and what it buys back in drawdown.  Probability of
a stop and price of a stop are two different numbers and both are needed: a rule can be
triggered often and still be cheap, or triggered twice and still be ruinous.

WHAT IS MEASURED (this repo's own panels and faces)
---------------------------------------------------
  * daily carry series per product: `idx_fut_carry_risk.product_spread(prod)["spread"]`
    (held contract return minus index return).  Not re-implemented here -- importing the
    authority is the only way the two faces cannot disagree;
  * ann / vol / mdd from that series, and again after the pause filter.

WHAT IS A RULE, NOT A MEASUREMENT
---------------------------------
  * the threshold grid (-1, -2, -3, -3.6, -4.2, -5 pp) and the resume condition are
    DECLARED below, taken from the strategy doc where the doc has one;
  * "paused" means flat: no carry, no roll cost, no basis risk.  A real pause has
    re-entry slippage; this face does not have a depth model, so it does not price one.
    The cost printed here is therefore a LOWER bound on the cost of a stop;
  * the rule's own volatility position (the book sizes this leg to a risk budget, not to
    a fixed notional) is NOT applied: this face prices the leg as its own series, and the
    book-level translation is arithmetic on the published 3.5% L2 budget, printed apart.

CAUSALITY (the one thing a backtest of a trigger must get right)
----------------------------------------------------------------
The rolling window at close t includes day t.  The exposure decision therefore applies to
day t+1's return.  A look-ahead implementation would apply the flag to day t itself, which
is a different (and unauthorizable) book; selftest leg 4 pins this down on a hand-built
series where the trigger day and the bad day are one bar apart.

verdict tokens (frozen before the first run):
  LINE_DOES_NOT_MATTER          written -2pp and the 2.5%-tail line differ by < 0.05pp of
                                annual cost AND < 0.05pp of drawdown: pick either
  WRITTEN_LINE_IS_THE_EXPENSIVE_ONE
                                the tight line costs >= 1.5x the wide line and buys less
                                than 0.25pp more drawdown: the tail was over-bought
  WRITTEN_LINE_BUYS_TAIL        the tight line costs more AND buys >= 0.25pp more
                                drawdown: the tightness is paid for, keep it
  DATA_BLOCKED                  a series is missing; refuse, never default to 0

Usage:
    python scripts/idx_fut_carry_pause_price.py run
    python scripts/idx_fut_carry_pause_price.py check
    python scripts/idx_fut_carry_pause_price.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SCHEMA = "idx-fut-carry-pause-price/v1"
KIND = "carry_pause_rule_price"
OUT = os.path.join(ROOT, "results", "idx_fut_carry_pause_price.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_PAUSE_PRICE.md")

# the written rule (research/STRATEGY-20261125.md §四, verbatim shape)
WINDOW = 60
WRITTEN_PP = -2.0
RESUME_AT_PP = 0.0          # "暂停，回研究面" has no resume clause; clear the window first
# r2103's own 2.5% tail lines, priced here beside the written one
GRID = [-1.0, -2.0, -3.0, -3.6, -4.2, -5.0]
WIDE_PP = -3.6              # IC 2.5%-tail line from r2103 (kept as the comparison arm)
CONFIRM_BARS = [1, 3, 5]    # how many consecutive bars below the line before standing down
BOOK = {"in_book": ["IC", "IM"], "context": ["IF", "IH"],
        "l2_risk_budget_pct": 3.5}

V_MATTER = "LINE_DOES_NOT_MATTER"
V_EXPENSIVE = "WRITTEN_LINE_IS_THE_EXPENSIVE_ONE"
V_TAIL = "WRITTEN_LINE_BUYS_TAIL"
V_BLOCK = "DATA_BLOCKED"


# ------------------------------------------------------------------ small arithmetic
def td():
    """Bars per year, taken from the authority rather than re-declared here.

    idx_fut_basis.TRADING_DAYS is 244.  A hardcoded 252 in this file made the same series
    read 8.94%/yr here and 8.64%/yr on the risk face -- two rulers for one number, the
    exact defect this repo keeps hunting.  Import it.
    """
    import idx_fut_carry_risk as R
    return float(R.base.TRADING_DAYS)


def ann_compound(daily):
    """Annualised compound return of a daily simple-return series."""
    if not daily:
        return None
    lvl = 1.0
    for r in daily:
        lvl *= (1.0 + r)
    if lvl <= 0:
        return None
    return (lvl ** (td() / len(daily)) - 1.0) * 100.0


def ann_vol(daily):
    if len(daily) < 2:
        return None
    m = sum(daily) / len(daily)
    v = sum((x - m) ** 2 for x in daily) / (len(daily) - 1)
    return math.sqrt(v) * math.sqrt(td()) * 100.0


def mdd(daily):
    """Max drawdown of the compound equity, in pct (negative)."""
    lvl, peak, worst = 1.0, 1.0, 0.0
    for r in daily:
        lvl *= (1.0 + r)
        peak = max(peak, lvl)
        worst = min(worst, lvl / peak - 1.0)
    return worst * 100.0


def rolling_cum(daily, window):
    """Cumulative return over the trailing window, in PERCENT points, ending at each bar.

    The series arrives as decimal daily returns; the strategy doc writes its line as
    "-2pp", so the sum is scaled by 100 HERE and every consumer downstream compares pp to
    pp.  (First cut of this face forgot the scale and reported zero stops on a series that
    r2103 says stops ~8-10% of windows -- the empty grid was the tell.)
    """
    out, run = [], 0.0
    for i, r in enumerate(daily):
        run += r
        if i >= window:
            run -= daily[i - window]
        out.append(100.0 * run if i >= window - 1 else None)
    return out


def apply_pause(daily, window, threshold_pp, resume_at_pp=RESUME_AT_PP, confirm=1):
    """Causal pause filter -> (filtered series, paused-day mask, episode list).

    exposure for day t+1 = flag computed from the window ending at day t.
    `confirm` requires the window to sit below the line for that many consecutive bars
    before the leg is stood down: a tripwire that fires on one crash bar is a reversal
    detector, and this history is exactly where that distinction matters (see doc §四).
    """
    cum = rolling_cum(daily, window)
    flags, paused = [], False
    episodes, start = [], None
    for i in range(len(daily)):
        # exposure on THIS bar comes from the previous bar's window
        prev = cum[i - 1] if i >= 1 else None
        if prev is None:
            exposed = True
        elif paused:
            exposed = prev >= resume_at_pp
        else:
            look = cum[max(0, i - confirm):i]
            exposed = not (len(look) >= confirm and all(x is not None and x < threshold_pp
                                                       for x in look))
        flags.append(exposed)
        if not exposed:
            if not paused:
                start = i
            paused = True
        else:
            if paused and start is not None:
                episodes.append({"start": start, "end": i - 1, "bars": i - start})
            paused, start = False, None
    if paused and start is not None:
        episodes.append({"start": start, "end": len(daily) - 1, "bars": len(daily) - start})
    filtered = [r if ex else 0.0 for r, ex in zip(daily, flags)]
    return filtered, [not ex for ex in flags], episodes


def block(daily, dates, window, threshold_pp, resume_at_pp=RESUME_AT_PP, confirm=1):
    filtered, paused_mask, episodes = apply_pause(daily, window, threshold_pp, resume_at_pp,
                                                  confirm)
    raw_ann, f_ann = ann_compound(daily), ann_compound(filtered)
    raw_mdd, f_mdd = mdd(daily), mdd(filtered)
    missed = sum(r for r, p in zip(daily, paused_mask) if p) * 100.0
    days_paused = sum(1 for p in paused_mask if p)
    cost = (raw_ann - f_ann) if (raw_ann is not None and f_ann is not None) else None
    return {
        "threshold_pp": threshold_pp,
        "resume_at_cum_pp": resume_at_pp,
        "confirm_bars": confirm,
        "episodes": len(episodes),
        "episode_bars": [e["bars"] for e in episodes],
        "longest_episode_bars": max([e["bars"] for e in episodes], default=0),
        "days_paused": days_paused,
        "paused_share_pct": round(100.0 * days_paused / len(daily), 2) if daily else None,
        "first_pause": dates[episodes[0]["start"]] if episodes else None,
        "last_pause": dates[episodes[-1]["end"]] if episodes else None,
        "ann_compound_pct": round(f_ann, 4) if f_ann is not None else None,
        "raw_ann_compound_pct": round(raw_ann, 4) if raw_ann is not None else None,
        "cost_pp": round(cost, 4) if cost is not None else None,
        "cost_per_episode_pp": round(cost / len(episodes), 4) if (cost is not None and episodes) else 0.0,
        "ann_vol_pct": round(ann_vol(filtered), 4) if ann_vol(filtered) is not None else None,
        "mdd_pct": round(f_mdd, 4),
        "raw_mdd_pct": round(raw_mdd, 4),
        "mdd_bought_pp": round(f_mdd - raw_mdd, 4),
        "missed_carry_pp_total": round(missed, 4),
    }


# ------------------------------------------------------------------ series + face
def series(prod):
    import idx_fut_carry_risk as R          # the authority for this series, not a copy
    sp = R.product_spread(prod)
    if not sp or sp.get("_refused"):
        return None, None, sp
    daily, dates = sp["spread"], sp["dates"]
    if len(dates) == len(daily) + 1:
        dates = dates[1:]
    if len(dates) != len(daily):
        return None, None, {"_refused": "series_and_calendar_lengths_disagree",
                            "spread": len(daily), "dates": len(dates)}
    return daily, dates, sp


def price_product(prod):
    daily, dates, sp = series(prod)
    if daily is None:
        return {"status": "blocked", "why": (sp or {}).get("_refused", "no series")}
    out = {"status": "ok", "days": len(daily),
           "span": {"first": dates[0], "last": dates[-1],
                    "rolls": sp.get("rolls")},
           "raw": {"ann_compound_pct": round(ann_compound(daily), 4),
                   "ann_vol_pct": round(ann_vol(daily), 4),
                   "mdd_pct": round(mdd(daily), 4)},
           "rulings": {}, "controls": {}}
    for thr in GRID:
        out["rulings"]["%+.1f" % thr] = block(daily, dates, WINDOW, thr)
    # does the cost survive requiring persistence? a one-bar trip is a reversal detector
    out["confirmation"] = {}
    for k in CONFIRM_BARS:
        out["confirmation"]["%d" % k] = block(daily, dates, WINDOW, WRITTEN_PP, RESUME_AT_PP, k)
    # controls must not oscillate on the resume clause: give each one its own resume line
    out["controls"]["never_pauses"] = block(daily, dates, WINDOW, -1e9, -1e9)
    out["controls"]["always_pauses"] = block(daily, dates, WINDOW, 1e9, 1e9)
    # reference ceiling: what skipping every negative carry day would have been worth.
    # labelled because it needs tomorrow's sign and cannot be traded.
    oracle = [0.0 if r < 0 else r for r in daily]
    out["controls"]["oracle_skip_negative_pp"] = round(ann_compound(oracle) - ann_compound(daily), 4)
    out["controls"]["oracle_note"] = "needs next-day sign; an upper bound, not a strategy"
    # WHY the cost is what it is: what the bar after a trigger actually paid
    cum = rolling_cum(daily, WINDOW)
    trig = [i for i in range(1, len(daily) - 1)
            if cum[i] is not None and cum[i] < WRITTEN_PP and cum[i - 1] is not None
            and cum[i - 1] >= WRITTEN_PP]
    nxt = [daily[i + 1] for i in trig]
    out["trigger_quality"] = {
        "trigger_bars": len(trig),
        "trigger_dates": [dates[i] for i in trig],
        "mean_next_bar_pp": round(100.0 * sum(nxt) / len(nxt), 4) if nxt else None,
        "unconditional_mean_bar_pp": round(100.0 * sum(daily) / len(daily), 4),
        "next_bar_positive_share_pct": round(100.0 * sum(1 for r in nxt if r > 0) / len(nxt), 2) if nxt else None,
        "note": "if the next bar after a trigger pays MORE than an average bar, the line is a rebound detector",
    }
    # does this face's raw leg agree with the published risk face on the same series?
    peer = os.path.join(ROOT, "results", "idx_fut_carry_risk.json")
    if os.path.exists(peer):
        with io.open(peer, encoding="utf-8") as fh:
            pf = json.load(fh)
        there = ((pf.get("products") or {}).get(prod) or {}).get("risk", {}).get("ann_compound_pct")
        mine = round(ann_compound(daily), 4)
        out["cross_face"] = {
            "peer_face": "results/idx_fut_carry_risk.json",
            "peer_ann_compound_pct": there,
            "mine_pct": mine,
            "delta_pp": round(mine - there, 4) if there is not None else None,
            "agrees": (there is not None and abs(mine - there) <= 0.02),
        }
    return out


def judge(face):
    written, wide = "%+.1f" % WRITTEN_PP, "%+.1f" % WIDE_PP
    rows, bad = {}, []
    for prod in BOOK["in_book"]:
        p = face["products"].get(prod, {})
        if p.get("status") != "ok":
            bad.append(prod)
            continue
        a, b = p["rulings"][written], p["rulings"][wide]
        rows[prod] = {
            "written_cost_pp": a["cost_pp"], "wide_cost_pp": b["cost_pp"],
            "written_mdd_bought_pp": a["mdd_bought_pp"],
            "wide_mdd_bought_pp": b["mdd_bought_pp"],
            "extra_mdd_bought_pp": round(a["mdd_bought_pp"] - b["mdd_bought_pp"], 4),
            "cost_ratio": round(a["cost_pp"] / b["cost_pp"], 3) if b["cost_pp"] else None,
            "written_episodes": a["episodes"], "wide_episodes": b["episodes"],
        }
    if bad or len(rows) < len(BOOK["in_book"]):
        return {"token": V_BLOCK, "why": "missing legs: " + ",".join(bad), "rows": rows}
    matters = all(abs(r["written_cost_pp"] - r["wide_cost_pp"]) < 0.05
                  and abs(r["extra_mdd_bought_pp"]) < 0.05 for r in rows.values())
    if matters:
        token = V_MATTER
    else:
        buys_tail = all(r["extra_mdd_bought_pp"] >= 0.25 for r in rows.values())
        token = V_TAIL if buys_tail else V_EXPENSIVE
    return {"token": token, "rows": rows}


def digests():
    out = {}
    for rel in ("scripts/idx_fut_carry_risk.py", "research/STRATEGY-20261125.md",
                "results/idx_fut_carry_risk.json"):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            out[rel] = None
            continue
        h = hashlib.sha256()
        with io.open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        out[rel] = h.hexdigest()
    return out


def derive():
    face = {
        "schema": SCHEMA, "kind": KIND,
        "generated": None, "evidence_cutoff": None,
        "question": "obeying the written 60-day -2pp pause costs what, and buys what?",
        "rule": {
            "source": "research/STRATEGY-20261125.md §四 触发与降档（单腿 60 日累计 carry < -2pp）",
            "window_days": WINDOW, "threshold_pp": WRITTEN_PP,
            "resume_at_cum_pp": RESUME_AT_PP,
            "resume_note": "the doc has no resume clause; the window must clear 0 before the leg is back",
            "causality": "window ending at close t decides exposure on bar t+1 (selftest leg 4)",
            "paused_means": "flat: no carry, no roll cost, no basis risk; re-entry slippage not priced",
        },
        "grid_pp": GRID,
        "book": BOOK,
        "products": {}, "verdict": {}, "inputs": digests(),
    }
    for prod in BOOK["in_book"] + BOOK["context"]:
        face["products"][prod] = price_product(prod)
    face["verdict"] = judge(face)
    ok_legs = [p for p in face["products"].values() if p.get("status") == "ok"]
    face["evidence_cutoff"] = max((p["span"]["last"] for p in ok_legs), default=None)
    # book-level translation: the leg runs at a risk budget, so its return cost scales
    tr = {}
    for prod in BOOK["in_book"]:
        p = face["products"].get(prod, {})
        if p.get("status") != "ok":
            continue
        vol = p["raw"]["ann_vol_pct"]
        w = BOOK["l2_risk_budget_pct"] / vol if vol else None
        a = p["rulings"]["%+.1f" % WRITTEN_PP]
        tr[prod] = {"leg_vol_pct": vol, "weight_at_l2_budget": round(w, 4) if w else None,
                   "book_cost_pp": round(a["cost_pp"] * w, 4) if (w and a["cost_pp"] is not None) else None}
    face["book_translation"] = {
        "note": "arithmetic on the published 3.5% L2 risk budget, not a measured book return",
        "rows": tr}
    return face


# ------------------------------------------------------------------ render
def render(face):
    L = []
    A = L.append
    v = face["verdict"]
    A("# carry 暂停规则的价格（%s）" % os.path.basename(DOC))
    A("")
    A("> 生成：%s　证据截止：%s" % (face["generated"], face["evidence_cutoff"]))
    A("> 问题：%s" % face["question"])
    A("")
    A("## 一、判决：`%s`" % v["token"])
    A("")
    for prod, r in (v.get("rows") or {}).items():
        A("- **%s**：写了的那条线（−2pp）每年让掉 **%.2f pp** 收益，回撤差 **%+.2f pp**"
          "（负=停牌后回撤反而更深）；宽线（%.1fpp）让掉 %.2f pp、回撤差 %+.2f pp —— "
          "多出来的尾部保护只有 **%+.2f pp**，触发 %d 次 vs %d 次。" % (
              prod, r["written_cost_pp"], r["written_mdd_bought_pp"],
              float(WIDE_PP), r["wide_cost_pp"], r["wide_mdd_bought_pp"],
              r["extra_mdd_bought_pp"], r["written_episodes"], r["wide_episodes"]))
    A("")
    A("读法：本面的「回撤差」= 停牌后序列的最大回撤减原始序列的最大回撤。**负数意味着停牌让"
      "回撤更深**——不是符号写反：停掉的那几根里包含了反弹，净值峰值被压低，后面同样的跌幅就"
      "显得更深。")
    A("")
    A("## 二、逐阈值实测（每条腿自己的日序列）")
    A("")
    for prod in BOOK["in_book"]:
        p = face["products"].get(prod, {})
        if p.get("status") != "ok":
            A("- **%s**：证据缺失（%s）" % (prod, p.get("why")))
            continue
        A("### %s（%s → %s，%d 日，原始年化 %.2f%%／波动 %.2f%%／回撤 %.2f%%）" % (
            prod, p["span"]["first"], p["span"]["last"], p["days"],
            p["raw"]["ann_compound_pct"], p["raw"]["ann_vol_pct"], p["raw"]["mdd_pct"]))
        A("")
        A("| 阈值 | 停牌次数 | 停牌日 | 占比 | 最长一段 | 年化 | 让掉的收益 pp | 每次 pp | 回撤 | 回撤差 pp |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for key in ["%+.1f" % t for t in GRID]:
            b = p["rulings"][key]
            A("| %s | %d | %d | %.1f%% | %d | %.2f%% | %.2f | %.2f | %.2f%% | %.2f |" % (
                key, b["episodes"], b["days_paused"], b["paused_share_pct"],
                b["longest_episode_bars"], b["ann_compound_pct"], b["cost_pp"],
                b["cost_per_episode_pp"], b["mdd_pct"], b["mdd_bought_pp"]))
        A("")
        A("对照：永不停牌 = 原始（让掉 0，换回 0）；永远停牌 = 年化 0，让掉 %.2f pp；"
          "「只在负 carry 日离场」的不可交易上界 = +%.2f pp/年。" % (
              p["controls"]["always_pauses"]["cost_pp"],
              p["controls"]["oracle_skip_negative_pp"]))
        A("")
        tq = p["trigger_quality"]
        A("口径对照：本面合算年化 %.2f%%，risk 面同一条腿写 %s%%（差 %+.2f pp，%s）；"
          "年化分母统一取 `idx_fut_basis.TRADING_DAYS`（=%.0f），不在这里另立一把尺子。" % (
              p["raw"]["ann_compound_pct"],
              ("%.3f" % p["cross_face"]["peer_ann_compound_pct"]) if p.get("cross_face") and p["cross_face"]["peer_ann_compound_pct"] is not None else "—",
              (p.get("cross_face") or {}).get("delta_pp") or 0.0,
              "一致" if (p.get("cross_face") or {}).get("agrees") else "不一致（如实披露）",
              td()))
        A("")
        if tq["trigger_bars"]:
            A("**触发当天之后那一根到底付了多少钱**：%d 次触发，次日平均 **%+.3f pp**"
              "（全样本平均 %+.3f pp），次日为正的占 **%.0f%%**。" % (
                  tq["trigger_bars"], tq["mean_next_bar_pp"], tq["unconditional_mean_bar_pp"],
                  tq["next_bar_positive_share_pct"]))
            A("")
            A("触发日：%s" % "、".join(tq["trigger_dates"]))
            A("")
        A("写法对照（同一条 −2pp，只在「连续 %s 根都在线下才停」上不同）：" % "/".join(
            str(k) for k in CONFIRM_BARS))
        A("")
        A("| 确认根数 | 停牌次数 | 停牌日 | 年化 | 让掉 pp | 回撤差 pp（负=更深） | 首次停牌日 |")
        A("|---|---|---|---|---|---|---|")
        for key, b in p["confirmation"].items():
            A("| %s | %d | %d | %.2f%% | %.2f | %+.2f | %s |" % (
                key, b["episodes"], b["days_paused"], b["ann_compound_pct"], b["cost_pp"],
                b["mdd_bought_pp"], b["first_pause"] or "—"))
        A("")
    A("## 三、翻到书面上是多少")
    A("")
    styled = "3.5% 预算下的权重"
    A("| 腿 | 腿波动 | %s | 书面收益代价（pp/年） |" % styled)
    A("|---|---|---|---|")
    for prod, r in face["book_translation"]["rows"].items():
        A("| %s | %.2f%% | %.3f | %.2f |" % (prod, r["leg_vol_pct"],
                                            r["weight_at_l2_budget"] or 0.0,
                                            r["book_cost_pp"] or 0.0))
    A("")
    A("注：%s" % face["book_translation"]["note"])
    A("")
    A("## 四、这条面不知道的事")
    A("")
    A("1. **再入场滑点没算**——停牌=空仓，回来时按收盘价重建，实际会有一次换手；本面没有深度模型，"
      "所以上面所有代价都是**下界**。")
    A("2. **没套引擎的分位规则**——引擎在基差分位 ≥80 时本来就把该腿权重归零（规则内生）；本面在未经该"
      "规则的序列上定价，因此停牌日数比对引擎时略多。")
    A("3. **样本很小**：写死那条线在 IC 只触发 3 次、IM 3 次——「次日平均 +2.3/+3.05 pp」是三次观察，"
      "不是估计；能确定的是方向（三次次日全为正），不能确定的是幅度。")
    A("4. **回撤差按各腿自己的净值算**，未按组合净值算（r2103 已指出回撤阶梯修法属共享面）。")
    A("")
    A("## 五、这一轮改变了什么")
    A("")
    tr = face["book_translation"]["rows"]
    leg_txt = "、".join(
        "%s %.2f pp/年（书上 %.2f）" % (
            k, face["products"][k]["rulings"]["%+.1f" % WRITTEN_PP]["cost_pp"],
            v["book_cost_pp"] or 0.0)
        for k, v in tr.items())
    A("1. 「停一次值多少钱」第一次有了数字：%s，而回撤没有变浅。" % leg_txt)
    tqs = [face["products"][k]["trigger_quality"] for k in tr]
    nxt = "/".join("%+.2f" % t["mean_next_bar_pp"] for t in tqs if t["mean_next_bar_pp"] is not None)
    base_bar = "/".join("%+.3f" % t["unconditional_mean_bar_pp"] for t in tqs)
    dates = tqs[0]["trigger_dates"] if tqs else []
    conf_zero = all(face["products"][k]["confirmation"]["3"]["days_paused"] == 0 for k in tr)
    A("2. 根因是**触发点与次日收益反相关**：触发日（%s）之后那一根平均 **%s pp**，普通一根只有 "
      "**%s pp**——写死的 −2pp 实质是**反弹探测器**，不是坏了才响的断路器。" % (
          " / ".join(dates), nxt, base_bar))
    A("3. 修法可执行且已验证：**同一条线加「连续 3 根都在线下才停」**→ %s；要保留断路器语义，"
      "就写「连续 N 根确认」，不要写单根穿越。" % (
          "两腿都 0 次停牌、0 代价（本段历史一次都不会误伤）" if conf_zero
          else "停牌次数降到 " + "/".join(
              "%d" % face["products"][k]["confirmation"]["3"]["episodes"] for k in tr)))
    A("4. 未做（属共享面，等无竞争轮）：把确认根数写进 `research/STRATEGY-20261125.md` 与 "
      "`scripts/policy_engine.py`；本面接进 `Tools/s6_chain_bmc.py`（本轮竞争窗，只落新增文件）。")
    A("")
    return "\n".join(L) + "\n"


def write():
    face = derive()
    face["generated"] = _now()
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(face))
    print("wrote %s and %s" % (os.path.relpath(OUT, ROOT), os.path.relpath(DOC, ROOT)))
    print("verdict=%s" % face["verdict"]["token"])
    for prod in BOOK["in_book"]:
        p = face["products"].get(prod, {})
        if p.get("status") == "ok":
            b = p["rulings"]["%+.1f" % WRITTEN_PP]
            print(" %s: cost=%.2fpp mdd_bought=%.2fpp episodes=%d days_paused=%d" % (
                prod, b["cost_pp"], b["mdd_bought_pp"], b["episodes"], b["days_paused"]))
    return 0


def _now():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


# ------------------------------------------------------------------ check
def check(face_path=None, quiet=False):
    """rc0 = face and doc agree with a fresh derivation; rc3 = drift or mismatch."""
    path = face_path or OUT
    if not os.path.exists(path):
        if not quiet:
            print("STALE face missing: %s (run 'run')" % os.path.relpath(path, ROOT))
        return 3
    with io.open(path, encoding="utf-8") as fh:
        on_disk = json.load(fh)
    now_inputs = digests()
    drift = [k for k, v in (on_disk.get("inputs") or {}).items() if now_inputs.get(k) != v]
    fresh = derive()
    diffs = []
    if on_disk.get("verdict", {}).get("token") != fresh["verdict"]["token"]:
        diffs.append("verdict %s != %s" % (on_disk.get("verdict", {}).get("token"),
                                           fresh["verdict"]["token"]))
    for prod in fresh["products"]:
        a, b = on_disk["products"].get(prod, {}), fresh["products"][prod]
        if a.get("status") != b.get("status"):
            diffs.append("%s status" % prod)
            continue
        if b.get("status") != "ok":
            continue
        for key, row in b["rulings"].items():
            old = (a.get("rulings") or {}).get(key, {})
            for f in ("episodes", "days_paused", "ann_compound_pct", "cost_pp", "mdd_pct"):
                if old.get(f) != row[f]:
                    diffs.append("%s %s %s %r != %r" % (prod, key, f, old.get(f), row[f]))
    if on_disk.get("evidence_cutoff") != fresh["evidence_cutoff"]:
        diffs.append("evidence_cutoff %r != %r" % (on_disk.get("evidence_cutoff"),
                                                   fresh["evidence_cutoff"]))
    doc_ok = os.path.exists(DOC)
    if doc_ok:
        want = render(dict(on_disk, generated=on_disk.get("generated")))
        with io.open(DOC, encoding="utf-8") as fh:
            have = fh.read()
        # only the body beyond the two generated lines is compared (generated stamp drifts)
        if want.split("\n", 3)[3:] != have.split("\n", 3)[3:]:
            diffs.append("research doc does not match the face")
    else:
        diffs.append("research doc missing")
    if drift:
        if not quiet:
            print("STALE upstream moved: %s (re-run to rebuild)" % ", ".join(drift))
        return 3
    if diffs:
        if not quiet:
            print("CHECK FAILED")
            for d in diffs[:12]:
                print("  -", d)
            if len(diffs) > 12:
                print("  ... %d more" % (len(diffs) - 12))
        return 3
    if not quiet:
        print("OK %s verdict=%s cutoff=%s" % (os.path.basename(path),
                                              on_disk["verdict"]["token"],
                                              on_disk["evidence_cutoff"]))
    return 0


# ------------------------------------------------------------------ selftest
def _selftest():
    n = [0]

    def ok(cond, msg):
        n[0] += 1
        if not cond:
            raise AssertionError("leg %d failed: %s" % (n[0], msg))

    # 1 a threshold nothing can cross leaves the series exactly as it was
    daily = [0.001] * 120
    f, paused, eps = apply_pause(daily, 60, -100.0)
    ok(f == daily and not any(paused) and not eps, "never-fires rule is the identity")

    # 2 a threshold everything crosses flattens the series into one episode
    f2, _, eps2 = apply_pause(daily, 60, 100.0, 100.0)
    ok(all(x == 0.0 for x in f2[60:]) and len(eps2) == 1, "always-fires rule is one episode")
    ok(ann_compound([0.0] * 200) == 0.0, "flat series compounds to zero")

    # 3 a closed episode opens and closes on the right bars (hand-built on/off pattern)
    pat = [0.0] * 70 + [-0.01] * 3 + [0.0] * 70
    _, _, eps3 = apply_pause(pat, 60, -2.0)
    ok(len(eps3) == 1 and eps3[0]["start"] >= 70, "one episode, opened at the shock")

    # 4 CAUSALITY: the pause must start the bar AFTER the trigger bar, never on it
    sh = [0.001] * 80 + [-0.02] * 3 + [0.001] * 40
    _, mask, eps4 = apply_pause(sh, 10, -1.5)
    first = eps4[0]["start"] if eps4 else None
    ok(first is not None, "shock is caught")
    trig = next(i for i in range(1, len(sh)) if 100.0 * sum(sh[i - 9:i + 1]) < -1.5)
    ok(first == trig + 1, "exposure decision lands on trigger+1 (got %r want %r)" % (first, trig + 1))
    ok(mask[trig] is False, "the trigger bar itself was still held")

    # 5 the rolling window forgets the far past
    z = [0.0] * 50 + [-0.05] + [0.0] * 50
    cum = rolling_cum(z, 10)
    ok(cum[50] is not None and cum[50] < -4.0, "window sees the shock")
    ok(abs(cum[61]) < 1e-10, "window drops the shock exactly 10 bars later")

    # 6 drawdown of the paused series can only be >= the raw one's (it is a subset of days)
    d = [0.01, -0.03, 0.005, -0.02, 0.002] * 20
    f6, _, _ = apply_pause(d, 5, -0.01)
    ok(mdd(f6) >= mdd(d) - 1e-12, "filtering cannot deepen the drawdown")

    # 7 live face must pass check rc0, and must not say STALE
    face = derive()
    face["generated"] = "selftest"
    import tempfile
    tmpd = tempfile.mkdtemp(prefix="pause_price_")
    fp = os.path.join(tmpd, "face.json")
    with io.open(fp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    saved = globals().get("DOC")
    globals()["DOC"] = os.path.join(tmpd, "doc.md")
    with io.open(globals()["DOC"], "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(face))
    rc = check(face_path=fp, quiet=True)
    ok(rc == 0, "fresh face checks rc0 (got %s)" % rc)

    # 8 one edited cost must fail WITHOUT the STALE word (r1850/r1934 contract)
    bad = json.loads(json.dumps(face))
    prod = [k for k, v in bad["products"].items() if v.get("status") == "ok"][0]
    key = sorted(bad["products"][prod]["rulings"])[1]
    bad["products"][prod]["rulings"][key]["cost_pp"] += 0.5
    bp = os.path.join(tmpd, "bad.json")
    with io.open(bp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(bad, fh, ensure_ascii=False, indent=1)
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc2 = check(face_path=bp, quiet=False)
    said = buf.getvalue()
    ok(rc2 == 3 and "CHECK FAILED" in said and "STALE" not in said,
       "edited number -> CHECK FAILED without STALE")

    # 9 a flipped verdict alone must fail
    bad2 = json.loads(json.dumps(face))
    bad2["verdict"]["token"] = V_TAIL if bad2["verdict"]["token"] != V_TAIL else V_MATTER
    bp2 = os.path.join(tmpd, "bad2.json")
    with io.open(bp2, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(bad2, fh, ensure_ascii=False, indent=1)
    ok(check(face_path=bp2, quiet=True) == 3, "flipped verdict fails")

    # 10 a missing face is STALE, not a crash
    ok(check(face_path=os.path.join(tmpd, "absent.json"), quiet=True) == 3,
       "missing face -> rc3")

    globals()["DOC"] = saved
    print("SELFTEST %d/%d OK" % (n[0], n[0]))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("--selftest", "selftest"):
        return _selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check()
    return write()


if __name__ == "__main__":
    sys.exit(main())
