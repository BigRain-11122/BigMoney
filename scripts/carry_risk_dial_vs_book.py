#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the dial says 8 %; the book that is actually being paper-tracked ran 14.05 % -- what capital
makes those two sentences the same sentence?

WHY THIS FILE EXISTS
--------------------
Four published faces each hold one piece of this book and no face holds the join:

    results/idx_fut_carry_sizing_spec.json   8 % budget -> one hedge lot needs 1,132,145 CNY (IC)
                                             and 1,161,161 CNY (IM) of capital
    results/idx_fut_carry_rent_by_component.json   the as-built 1 IC + 1 IM + 0.4347 sleeve book,
                                             1052 bars, ann vol 14.0528 %, ann compound 27.1913 %
    results/idx_fut_carry_rebudget_floor.json     the capital window [lower, upper] of each weight
                                             set against the sleeve's own 1 % ADV line
    results/etf_book_capacity_edge.json      the six-name ADV line itself, 60 sessions

So a reader can learn "one lot needs 1.13 M", "the book ran 14 %", "the window opens at 1.0 M" --
and still not be able to answer the only question the 8 % dial was ever for:

    at what capital is this book's risk actually 8 % of my money, and does the equity
    sleeve still fit inside its own liquidity line there?

Two readings are printed side by side because they answer different books and disagree on the
median session (r1313: two pre-registered conditions may return opposite answers -- print both,
never average):

  weights reading   the book is defined in weights, so the sleeve scales with capital:
                    sleeve = 0.4347 x NAV, capacity end = ADV line / 0.4347
  same-size reading the book is the CNY size being tracked today (1 lot + 1 lot + 434,700 of
                    sleeve); more capital only dilutes, capacity end = the line itself

WHAT IS OUT OF SCOPE (printed, not implied)
-------------------------------------------
financing, margin calls, transaction costs, and the equity sleeve's own risk contribution to the
book's volatility.  Cutting the sleeve to fit the ADV line changes the book's vol by less than
proportionally -- that trade is not priced here and must not be read off this page.

frozen verdict tokens (fixed before the first run):
  DIAL_FITS_EVERY_SESSION        dial capital <= capacity end on today, median and worst
  DIAL_FITS_THE_BEST_SESSION_ONLY  it fits today but the median session closes it
  DIAL_FITS_NOWHERE              it does not even fit on the friendliest session
  DATA_BLOCKED                   an input face or a required field is missing; refuse, never
                                 default to zero

same-size token (second column, never merged into the first):
  SAME_SIZE_INSIDE_EVERY_SESSION / SAME_SIZE_BREACHES_THE_WORST_SESSION /
  SAME_SIZE_BREACHES_EVEN_THE_MEDIAN

Usage:
    python scripts/carry_risk_dial_vs_book.py run
    python scripts/carry_risk_dial_vs_book.py check
    python scripts/carry_risk_dial_vs_book.py --selftest
"""

from __future__ import print_function

import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_REL = os.path.join("results", "carry_risk_dial_vs_book.json")
DOC_REL = os.path.join("research", "CARRY_RISK_DIAL_VS_BOOK.md")
OUT_PATH = os.path.join(ROOT, OUT_REL)
DOC_PATH = os.path.join(ROOT, DOC_REL)

RENT = "results/idx_fut_carry_rent_by_component.json"
FLOOR = "results/idx_fut_carry_rebudget_floor.json"
CAP = "results/etf_book_capacity_edge.json"

SCHEMA = "carry-risk-dial-vs-book/v1"
KIND = "carry_risk_dial_vs_book"
NAV_LENS_CNY = 1000000.0
DIAL_PCT = 8.0
RUNG = "1/1"

V_EVERY = "DIAL_FITS_EVERY_SESSION"
V_BEST = "DIAL_FITS_THE_BEST_SESSION_ONLY"
V_NOWHERE = "DIAL_FITS_NOWHERE"
V_BLOCK = "DATA_BLOCKED"
VERDICTS = (V_EVERY, V_BEST, V_NOWHERE, V_BLOCK)

S_INSIDE = "SAME_SIZE_INSIDE_EVERY_SESSION"
S_WORST = "SAME_SIZE_BREACHES_THE_WORST_SESSION"
S_MEDIAN = "SAME_SIZE_BREACHES_EVEN_THE_MEDIAN"
SAME_SIZE_TOKENS = (S_INSIDE, S_WORST, S_MEDIAN)


# ------------------------------------------------------------------ io
def _abs(path, root=None):
    return path if os.path.isabs(path) else os.path.join(root or ROOT, path)


def _read_json(path, root=None):
    p = _abs(path, root)
    if not os.path.exists(p):
        return None
    with io.open(p, "rb") as fh:
        raw = fh.read()
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def _digest(path, root=None):
    p = _abs(path, root)
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with io.open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# ------------------------------------------------------------------ derive
def _num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _now():
    """House style wants the offset with a colon (+08:00); strftime's %z prints +0800."""
    raw = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    return raw[:-2] + ":" + raw[-2:] if len(raw) > 2 and raw[-5] in "+-" else raw


def derive(root=None):
    root = root or ROOT
    rent = _read_json(RENT, root)
    floor = _read_json(FLOOR, root)
    cap = _read_json(CAP, root)

    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "generated": _now(),
        "question": ("the 8 % dial prices one hedge lot at 1.13 M; the book being paper-tracked "
                     "ran 14.05 % vol on a 1 M NAV. At what capital is this book's risk really "
                     "8 % of the money, and does the equity sleeve still fit its 1 % ADV line "
                     "there?"),
        "rung": RUNG,
        "rules": {
            "risk_in_money": ("the book's annual vol as a share of NAV x the lens NAV -- the "
                              "CNY amount is what the dial has to divide"),
            "dial_capital": "vol_money_cny / (dial_pct/100): the NAV at which that same risk is 8 %",
            "weights_reading": ("the book is defined in weights, so the sleeve scales with "
                                "capital: capacity end = ADV line / equity weight"),
            "same_size_reading": ("the book is today's CNY size; more capital only dilutes, so "
                                  "the capacity end is the ADV line itself"),
            "dial_pct": DIAL_PCT,
            "lens_nav_cny": NAV_LENS_CNY,
            "verdict_rule": ("EVERY if dial capital <= capacity end on today, median and worst; "
                             "BEST if only today; NOWHERE otherwise"),
            "not_recomputed": ["the book's volatility", "the ADV line and its 60-session window",
                               "the sleeve weight", "per-lot vol or margin"],
        },
        "inputs": {
            "rent_by_component": {"path": RENT, "sha256": _digest(RENT, root)},
            "rebudget_floor": {"path": FLOOR, "sha256": _digest(FLOOR, root)},
            "capacity_edge": {"path": CAP, "sha256": _digest(CAP, root)},
            "nav_cny": NAV_LENS_CNY,
            "dial_pct": DIAL_PCT,
        },
    }

    if not (rent and floor and cap):
        face["verdict"] = V_BLOCK
        face["verdict_same_size"] = V_BLOCK
        face["sentence"] = "一或多个输入面缺失（rent / floor / capacity）——拒绝出数，不用零代替。"
        return face

    rung = (rent.get("rungs") or {}).get(RUNG)
    if not rung:
        face["verdict"] = V_BLOCK
        face["verdict_same_size"] = V_BLOCK
        face["sentence"] = "租金面里没有 {}/1 这一档——无法定位这本书的权重与波动。".format(RUNG)
        return face

    weights = rung.get("weights_x_nav") or {}
    book = rung.get("book") or {}
    vol_pct = _num(book.get("vol_pct"))
    comp_pct = _num(book.get("ann_compound_pct"))
    eq_w = _num(weights.get("equity_arm"))
    if vol_pct is None or eq_w is None or eq_w <= 0:
        face["verdict"] = V_BLOCK
        face["verdict_same_size"] = V_BLOCK
        face["sentence"] = "租金面 {}/1 缺 vol_pct 或 equity_arm 权重——拒绝出数。".format(RUNG)
        return face

    eqcap = (floor.get("equity_capacity") or {})
    cap_today = _num(eqcap.get("today_cny"))
    cap_median = _num(eqcap.get("median_cny"))
    cap_worst = _num(eqcap.get("worst_cny"))
    if None in (cap_today, cap_median, cap_worst):
        face["verdict"] = V_BLOCK
        face["verdict_same_size"] = V_BLOCK
        face["sentence"] = "重配地板面缺 equity_capacity 的 today/median/worst——拒绝出数。"
        return face

    # what the book's measured risk is, in money, and at what NAV it is 8 % of the money
    vol_money = vol_pct / 100.0 * NAV_LENS_CNY
    dial_capital = vol_money / (DIAL_PCT / 100.0)
    scale_needed = dial_capital / NAV_LENS_CNY
    sleeve_money = eq_w * NAV_LENS_CNY

    return_at_dial = (comp_pct / scale_needed) if comp_pct is not None else None
    dial_cost_pp = (comp_pct - return_at_dial) if return_at_dial is not None else None

    # reading A: the book is defined in weights -> the sleeve scales with capital
    up = {}
    for key, c in (("today", cap_today), ("median", cap_median), ("worst", cap_worst)):
        up[key] = {
            "capacity_cny": round(c, 2),
            "capacity_nav_cny": round(c / eq_w, 2),
            "dial_fits": dial_capital <= c / eq_w,
        }
    fits = [up[k]["dial_fits"] for k in ("today", "median", "worst")]
    if all(fits):
        verdict = V_EVERY
    elif fits[0]:
        verdict = V_BEST
    else:
        verdict = V_NOWHERE
    dial_window = {
        "lower_cny": round(dial_capital, 2),
        "upper_today_cny": up["today"]["capacity_nav_cny"],
        "upper_median_cny": up["median"]["capacity_nav_cny"],
        "upper_worst_cny": up["worst"]["capacity_nav_cny"],
        "width_today_cny": round(up["today"]["capacity_nav_cny"] - dial_capital, 2),
        "sleeve_weight_that_would_fit_at_dial_capital_median": round(
            cap_median / dial_capital, 6),
    }

    # reading B: the book is today's CNY size; extra capital only dilutes
    same = {}
    for key, c in (("today", cap_today), ("median", cap_median), ("worst", cap_worst)):
        same[key] = {
            "capacity_cny": round(c, 2),
            "sleeve_money_cny": round(sleeve_money, 2),
            "share_of_line_pct": round(sleeve_money / c * 100.0, 4) if c else None,
            "fits": sleeve_money <= c,
        }
    sfit = [same[k]["fits"] for k in ("today", "median", "worst")]
    if all(sfit):
        verdict_same = S_INSIDE
    elif sfit[0] and sfit[1]:
        verdict_same = S_WORST
    elif sfit[0]:
        verdict_same = S_MEDIAN
    else:
        verdict_same = S_MEDIAN
    if not all(sfit):
        # today is the friendliest session by construction; if even it fails say so plainly
        verdict_same = S_MEDIAN if not sfit[0] else verdict_same

    face.update({
        "verdict": verdict,
        "verdict_same_size": verdict_same,
        "book": {
            "vol_pct": round(vol_pct, 4),
            "ann_compound_pct": round(comp_pct, 4) if comp_pct is not None else None,
            "days": book.get("days"),
            "span": rung.get("span"),
            "weights_x_nav": {k: round(v, 6) for k, v in weights.items()
                              if isinstance(v, (int, float))},
            "equity_weight": round(eq_w, 6),
        },
        "dial": {
            "pct": DIAL_PCT,
            "excess_over_dial_pp": round(vol_pct - DIAL_PCT, 4),
            "vol_money_cny_per_year": round(vol_money, 2),
            "capital_where_risk_is_dial_cny": round(dial_capital, 2),
            "multiple_of_lens_nav": round(scale_needed, 6),
            "return_at_that_capital_pct": (round(return_at_dial, 4)
                                           if return_at_dial is not None else None),
            "cost_of_the_dial_pp": (round(dial_cost_pp, 4)
                                    if dial_cost_pp is not None else None),
            "sharpe_unchanged_because": ("return and vol both divide by the same capital; the "
                                         "dial is a size, not a quality"),
        },
        "capacity": {
            "line_pct": eqcap.get("line_pct"),
            "n_sessions": eqcap.get("n_sessions"),
            "names": eqcap.get("names"),
            "today_bar": eqcap.get("today_bar"),
            "sleeve_money_cny": round(sleeve_money, 2),
            "weights_reading": up,
            "same_size_reading": same,
        },
        "dial_window": dial_window,
        "cross_face": _cross_face(floor, cap, eq_w),
        # C2 wants a YYYY-MM-DD bar on every published face. This face invents no bar:
        # it carries the book's own (the rent face's), and prints its neighbours so a
        # reader can see the three are not the same generation when they are not.
        "evidence_cutoff": rent.get("evidence_cutoff") or cap.get("evidence_cutoff"),
        "upstream_cutoffs": {
            "rent_by_component": rent.get("evidence_cutoff"),
            "rebudget_floor": floor.get("evidence_cutoff"),
            "capacity_edge": cap.get("evidence_cutoff"),
        },
    })
    face["sentence"] = _sentence(face)
    return face


def _cross_face(floor, cap, eq_w):
    """The capacity readings this face uses come from the floor face; that face in turn
    recomputed them from the capacity face's sessions. Two faces, two 'today' bars -- name it
    instead of picking quietly."""
    eqcap = floor.get("equity_capacity") or {}
    summ = cap.get("summary") or {}
    med = _num(eqcap.get("median_cny"))
    worst = _num(eqcap.get("worst_cny"))
    cmed = _num(summ.get("capital_median_cny"))
    cworst = _num(summ.get("capital_min_cny"))
    same = (med is not None and cmed is not None and abs(med - cmed) <= 0.02
            and worst is not None and cworst is not None and abs(worst - cworst) <= 0.02)
    today = _num(eqcap.get("today_cny"))
    ctoday = _num(summ.get("capital_where_at_line_today_cny"))
    return {
        "median_and_worst": "CROSS_FACE_MATCHES" if same else "CROSS_FACE_DISAGREES",
        "today": {
            "floor_face_cny": today,
            "floor_face_bar": eqcap.get("today_bar"),
            "capacity_face_cny": ctoday,
            "capacity_face_bar": cap.get("session"),
            "delta_cny": (round(today - ctoday, 2)
                          if today is not None and ctoday is not None else None),
            "why": ("the two faces read different bars: the floor face takes the equity panel's "
                    "own last bar, the capacity face its own session. Both are printed; this "
                    "face reads the floor face because it is the face that owns this book's "
                    "window"),
        },
    }


def _money(cny):
    if cny is None:
        return "—"
    return "{:,.0f}".format(cny)


def _sentence(face):
    d = face.get("dial") or {}
    w = face.get("dial_window") or {}
    s = face.get("capacity", {}).get("same_size_reading", {})
    if face.get("verdict") == V_BLOCK:
        return face.get("sentence") or "输入缺失，拒绝出数。"
    parts = [
        "这本书实测年波动 **{:.2f}%**，按 100 万本金算是 **{} 元**——要把这笔波动压到 8%，"
        "资本得是 **{} 元**（今天的 {:.3f} 倍）".format(
            face["book"]["vol_pct"], _money(d.get("vol_money_cny_per_year")),
            _money(d.get("capital_where_risk_is_dial_cny")), d.get("multiple_of_lens_nav") or 0),
    ]
    if d.get("return_at_that_capital_pct") is not None:
        parts.append("代价是账面年化从 {:.2f}% 摊薄到 **{:.2f}%**（夏普不变：8% 是尺码不是质量）".format(
            face["book"]["ann_compound_pct"], d["return_at_that_capital_pct"]))
    if face.get("verdict") == V_BEST:
        parts.append("而权益袖的 1% ADV 线只在最松的那一天（今天 {} 元）容得下这个资本，"
                     "中位 session 只到 {} 元——**这个窗口今天开着、一半的日子关着**".format(
                         _money(w.get("upper_today_cny")), _money(w.get("upper_median_cny"))))
    elif face.get("verdict") == V_EVERY:
        parts.append("权益袖在所有 session 都容得下（最紧的一天 {} 元 ≥ {} 元）".format(
            _money(w.get("upper_worst_cny")), _money(w.get("lower_cny"))))
    else:
        parts.append("连最松的一天也容不下（{} 元 < {} 元）".format(
            _money(w.get("upper_today_cny")), _money(w.get("lower_cny"))))
    if s.get("worst", {}).get("share_of_line_pct") is not None:
        parts.append("换个读法（book 就是今天这个钱数、加资本只做稀释）：袖子的 {} 元占今天那条线的 "
                     "{:.1f}%、中位 {:.1f}%、最紧的一天 **{:.1f}%**".format(
                         _money(s["today"].get("sleeve_money_cny")),
                         s["today"]["share_of_line_pct"], s["median"]["share_of_line_pct"],
                         s["worst"]["share_of_line_pct"]))
    return "。".join(parts) + "。"


# ------------------------------------------------------------------ page
def _pit(v):
    return "✓" if v else "✗"


def render_doc(face):
    b = face.get("book") or {}
    d = face.get("dial") or {}
    w = face.get("dial_window") or {}
    cap = face.get("capacity") or {}
    up = cap.get("weights_reading") or {}
    same = cap.get("same_size_reading") or {}
    xf = face.get("cross_face") or {}

    L = []
    L.append("<!-- BEGIN:CARRY-RISK-DIAL-VS-BOOK -->")
    L.append("")
    L.append("# 说好 8% 的风险，这本书实际跑了多少；要多大的本钱才配得上这句话")
    L.append("")
    L.append("generated {} | evidence_cutoff {}（书的 bar；本面不产生 bar） | 档 {}".format(
        face.get("generated", ""), face.get("evidence_cutoff") or "—", face.get("rung")))
    L.append("")
    uc = face.get("upstream_cutoffs") or {}
    L.append("上游三张面各自的截点：租金 {} / 地板 {} / 容量 {}。".format(
        uc.get("rent_by_component") or "—", uc.get("rebudget_floor") or "（面未声明）",
        uc.get("capacity_edge") or "—"))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append(face.get("sentence", ""))
    L.append("")
    L.append("判词：**{}**（权重读法） / **{}**（同尺寸读法）".format(
        face.get("verdict"), face.get("verdict_same_size")))
    L.append("")
    L.append("## 这本书现在的读数")
    L.append("")
    L.append("| 量 | 值 | 出处 |")
    L.append("| --- | --- | --- |")
    L.append("| 年化波动 | {:.4f}% | `idx_fut_carry_rent_by_component.json` 档 {} book.vol_pct |".format(
        b.get("vol_pct") or 0.0, face.get("rung")))
    L.append("| 年化复利 | {} | 同上 book.ann_compound_pct |".format(
        "{:.4f}%".format(b.get("ann_compound_pct")) if b.get("ann_compound_pct") is not None else "—"))
    L.append("| 样本 | {} 根 bar（{} → {}） | 同上 |".format(
        b.get("days"), (b.get("span") or ["—", "—"])[0], (b.get("span") or ["—", "—"])[1]))
    ws = b.get("weights_x_nav") or {}
    L.append("| 权重（×NAV） | 权益袖 {} / IC {} / IM {} | 同上 weights_x_nav |".format(
        ws.get("equity_arm"), ws.get("IC_leg"), ws.get("IM_leg")))
    L.append("")
    L.append("## 8% 这把旋钮要多少钱")
    L.append("")
    L.append("| 量 | 值 | 算法 |")
    L.append("| --- | --- | --- |")
    L.append("| 这笔波动的钱 | **{} 元/年** | {:.4f}% × {} |".format(
        _money(d.get("vol_money_cny_per_year")), b.get("vol_pct") or 0.0,
        _money(cap.get("sleeve_money_cny") / (b.get("equity_weight") or 1) if cap else None)))
    L.append("| 波动占资本的 8% 所需资本 | **{} 元** | 波动钱 ÷ 8% |".format(
        _money(d.get("capital_where_risk_is_dial_cny"))))
    L.append("| 今天是它的几倍 | {:.3f}× | 所需资本 ÷ 100 万 |".format(
        d.get("multiple_of_lens_nav") or 0.0))
    L.append("| 超旋钮多少 | {} 个百分点 | {:.4f}% − 8% |".format(
        d.get("excess_over_dial_pp"), b.get("vol_pct") or 0.0))
    if d.get("return_at_that_capital_pct") is not None:
        L.append("| 摊薄后的账面年化 | {:.4f}%（原 {:.4f}%，少 {} 个点） | 复利钱 ÷ 所需资本 |".format(
            d["return_at_that_capital_pct"], b.get("ann_compound_pct") or 0.0,
            d.get("cost_of_the_dial_pp")))
    L.append("")
    L.append("夏普两边一样：收益和波动除的是同一个资本。**8% 是尺码，不是质量**（这条"
             "沿用 `idx_fut_carry_sizing_spec.json` 2026-11-17 的采纳理由）。")
    L.append("")
    L.append("## 权益袖自己的 1% ADV 线，用两种读法各算一遍")
    L.append("")
    L.append("| session | 1% ADV 线 | 读法 A：袖=0.4347×NAV → 容量资本 | A 容得下 | "
             "读法 B：袖={} 元 → 占线比 | B 容得下 |".format(_money(cap.get("sleeve_money_cny"))))
    L.append("| --- | --- | --- | --- | --- | --- |")
    for key, label in (("today", "今天"), ("median", "中位"), ("worst", "最紧")):
        a = up.get(key) or {}
        s = same.get(key) or {}
        L.append("| {} | {} | {} | {} | {} | {} |".format(
            label, _money(a.get("capacity_cny")), _money(a.get("capacity_nav_cny")),
            _pit(a.get("dial_fits")),
            ("{:.2f}%".format(s["share_of_line_pct"])
             if s.get("share_of_line_pct") is not None else "—"),
            _pit(s.get("fits"))))
    L.append("")
    L.append("窗口（读法 A）：**[{} , {}]** 于今天（宽 {} 元）；中位日上界 {} 元、最紧日 {} 元。".format(
        _money(w.get("lower_cny")), _money(w.get("upper_today_cny")),
        _money(w.get("width_today_cny")), _money(w.get("upper_median_cny")),
        _money(w.get("upper_worst_cny"))))
    if w.get("sleeve_weight_that_would_fit_at_dial_capital_median") is not None:
        L.append("")
        L.append("如果坚持在中位 session 上也开着，袖子权重得从 {:.4f} 压到 **{:.4f}**——"
                 "压低袖子会怎样改这本书的波动，本面**不算**（见边界）。".format(
                     b.get("equity_weight") or 0.0,
                     w["sleeve_weight_that_would_fit_at_dial_capital_median"]))
    L.append("")
    L.append("## 跨面对账")
    L.append("")
    L.append("- 中位/最紧两条线与容量面：**{}**".format(xf.get("median_and_worst")))
    t = xf.get("today") or {}
    if t:
        L.append("- 「今天」两个面读的 bar 不同：地板面（{}）{} 元 vs 容量面（{}）{} 元，差 {} 元。"
                 "本面读地板面——那是这本书窗口的属主面。".format(
                     t.get("floor_face_bar"), _money(t.get("floor_face_cny")),
                     t.get("capacity_face_bar"), _money(t.get("capacity_face_cny")),
                     _money(t.get("delta_cny"))))
    L.append("")
    L.append("## 边界（本面不做的事）")
    L.append("")
    L.append("1. **不重算波动**：14.05% 是租金面在 1052 根 bar 上的读数，本面只把它换成钱再除以 8%。")
    L.append("2. **不给融资、保证金、成本**：那是 `idx_fut_carry_margin` / `sizing_spec` 的面。")
    L.append("3. **压低袖子对波动的影响不算**：袖子的风险贡献是 7.5% 的风险份额，砍一半不等于"
             "波动减半——那是一次测量，这里没有做。")
    L.append("4. **两种读法不合并**：读法 A 与读法 B 在哪个 session 上关窗这件事上给出不同答案，"
             "各自印各自的数；读者必须先知道自己问的是「按权重配的书」还是「今天这个钱数的书」。")
    L.append("")
    L.append("## 怎么复跑")
    L.append("")
    L.append("```")
    L.append("python scripts/carry_risk_dial_vs_book.py run      # 重算 + 重渲染本页")
    L.append("python scripts/carry_risk_dial_vs_book.py check    # 输入动了说 STALE，数字不符说 CHECK FAILED")
    L.append("python scripts/carry_risk_dial_vs_book.py --selftest")
    L.append("```")
    L.append("")
    L.append("<!-- END:CARRY-RISK-DIAL-VS-BOOK -->")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ check
def check(quiet=False, root=None):
    root = root or ROOT
    out_path = _abs(OUT_REL, root)
    doc_path = _abs(DOC_REL, root)
    published = _read_json(out_path)
    if published is None:
        print("STALE face missing: {}".format(OUT_REL))
        return 3
    fresh = derive(root)

    moved = sorted(k for k, v in (published.get("inputs") or {}).items()
                   if (fresh.get("inputs") or {}).get(k) != v)
    if moved:
        if not quiet:
            print("STALE: input face(s) moved: {} -- rebuild this face".format(", ".join(moved)))
        return 3

    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict {!r} -> {!r}".format(
            published.get("verdict"), fresh.get("verdict")))
    if published.get("verdict_same_size") != fresh.get("verdict_same_size"):
        problems.append("verdict_same_size {!r} -> {!r}".format(
            published.get("verdict_same_size"), fresh.get("verdict_same_size")))
    for block, keys, tol in (("dial", ("excess_over_dial_pp", "vol_money_cny_per_year",
                                       "capital_where_risk_is_dial_cny",
                                       "multiple_of_lens_nav",
                                       "return_at_that_capital_pct"), 0.02),
                             ("dial_window", ("lower_cny", "upper_today_cny",
                                              "upper_median_cny", "upper_worst_cny"), 0.02)):
        a = published.get(block) or {}
        b = fresh.get(block) or {}
        for k in keys:
            va, vb = _num(a.get(k)), _num(b.get(k))
            if va is None or vb is None:
                if a.get(k) != b.get(k):
                    problems.append("{} {} {!r} -> {!r}".format(block, k, a.get(k), b.get(k)))
                continue
            if abs(va - vb) > tol:
                problems.append("{} {} {!r} -> {!r}".format(block, k, va, vb))
    for reading in ("weights_reading", "same_size_reading"):
        a_all = (published.get("capacity") or {}).get(reading) or {}
        b_all = (fresh.get("capacity") or {}).get(reading) or {}
        for key in ("today", "median", "worst"):
            a, b = a_all.get(key) or {}, b_all.get(key) or {}
            if bool(a) != bool(b):
                problems.append("capacity.{} {} presence changed".format(reading, key))
                continue
            if a.get("fits") != b.get("fits"):
                problems.append("capacity.{} {} fits {!r} -> {!r}".format(
                    reading, key, a.get("fits"), b.get("fits")))
            for f in ("capacity_cny", "capacity_nav_cny", "sleeve_money_cny",
                      "share_of_line_pct"):
                va, vb = _num(a.get(f)), _num(b.get(f))
                if va is not None and vb is not None and abs(va - vb) > 0.02:
                    problems.append("capacity.{} {} {} {!r} -> {!r}".format(
                        reading, key, f, va, vb))

    if problems:
        print("CHECK FAILED {} (same inputs, different numbers)".format(OUT_REL))
        for p in problems[:12]:
            print("  - " + p)
        return 3

    want = render_doc(published)
    got = None
    if os.path.exists(doc_path):
        with io.open(doc_path, "r", encoding="utf-8") as fh:
            got = fh.read()
    if got != want:
        print("STALE: {} does not re-render from the published face (pay the writer)".format(
            DOC_REL))
        return 3

    if not quiet:
        print("CHECK_OK carry_risk_dial_vs_book (verdict {}, same-size {})".format(
            published.get("verdict"), published.get("verdict_same_size")))
    return 0


# ------------------------------------------------------------------ run
def run():
    face = derive()
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    with io.open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    print("WROTE {} verdict={} same-size={}".format(OUT_REL, face.get("verdict"),
                                                    face.get("verdict_same_size")))
    for key in ("excess_over_dial_pp", "capital_where_risk_is_dial_cny"):
        print("  dial.{} = {}".format(key, (face.get("dial") or {}).get(key)))
    print("  window = [{}, {}] today".format((face.get("dial_window") or {}).get("lower_cny"),
                                             (face.get("dial_window") or {}).get("upper_today_cny")))
    return 0


# ------------------------------------------------------------------ selftest
def _stage(root):
    """A miniature tree holding only the faces this one reads, so a negative control can
    mutate a number without touching the real repo."""
    for rel in (RENT, FLOOR, CAP):
        src = _abs(rel, ROOT)
        dst = _abs(rel, root)
        d = os.path.dirname(dst)
        if not os.path.isdir(d):
            os.makedirs(d)
        shutil.copyfile(src, dst)
    out_dir = os.path.dirname(_abs(OUT_REL, root))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    doc_dir = os.path.dirname(_abs(DOC_REL, root))
    if not os.path.isdir(doc_dir):
        os.makedirs(doc_dir)


def _write_face(root, face):
    with io.open(_abs(OUT_REL, root), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    with io.open(_abs(DOC_REL, root), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))


def _edit_json(path, fn):
    with io.open(path, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    fn(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(d, ensure_ascii=False, indent=1))


def _quiet_check(root):
    """Capture the words, not just the rc: a silent STALE looks exactly like a crash, and the
    point of these legs is to prove which sentence the tool says."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = check(quiet=False, root=root)
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    tmp = tempfile.mkdtemp(prefix="carry_dial_")
    try:
        _stage(tmp)
        face = derive(tmp)
        leg("a real tree derives a verdict", face.get("verdict") in VERDICTS,
            str(face.get("verdict")))
        leg("the same-size token is its own vocabulary",
            face.get("verdict_same_size") in SAME_SIZE_TOKENS,
            str(face.get("verdict_same_size")))

        # the arithmetic is a division, so check it by hand on the published inputs
        vol = face["book"]["vol_pct"]
        want_cap = vol / 100.0 * NAV_LENS_CNY / (DIAL_PCT / 100.0)
        leg("dial capital == vol money / dial",
            abs(want_cap - face["dial"]["capital_where_risk_is_dial_cny"]) < 0.02,
            "{:.2f}".format(want_cap))
        leg("excess is vol minus the dial",
            abs(face["dial"]["excess_over_dial_pp"] - (vol - DIAL_PCT)) < 1e-9,
            str(face["dial"]["excess_over_dial_pp"]))

        # reading A and reading B are different books: they must not be the same number
        wa = face["capacity"]["weights_reading"]["median"]["capacity_nav_cny"]
        sb = face["capacity"]["same_size_reading"]["median"]["sleeve_money_cny"]
        leg("the two readings price different things", abs(wa - sb) > 1.0,
            "{} vs {}".format(wa, sb))

        _write_face(tmp, face)
        rc, out = _quiet_check(tmp)
        leg("a clean copy checks green", rc == 0, "rc={} {}".format(rc, out.strip()[:80]))

        # control 1: published numbers tampered -> CHECK FAILED, and it must not say STALE
        bad = json.loads(json.dumps(face))
        bad["dial"]["capital_where_risk_is_dial_cny"] += 5000.0
        _write_face(tmp, bad)
        rc, out = _quiet_check(tmp)
        leg("a tampered number is CHECK FAILED", rc == 3 and "CHECK FAILED" in out, out.strip()[:80])
        leg("a tampered number never claims STALE", "STALE" not in out, out.strip()[:80])

        # control 2: an input face moves -> STALE (pay the writer), different words
        _write_face(tmp, face)
        capp = _abs(CAP, tmp)
        _edit_json(capp, lambda d: d["summary"].__setitem__(
            "capital_median_cny", d["summary"]["capital_median_cny"] + 1.0))
        rc, out = _quiet_check(tmp)
        leg("a moved input face is STALE", rc == 3 and "STALE" in out, out.strip()[:80])
        leg("a moved input face is not CHECK FAILED",
            "CHECK FAILED" not in out, out.strip()[:80])

        # control 3: the page lags its face -> STALE
        _stage_inputs = {rel: _abs(rel, ROOT) for rel in (RENT, FLOOR, CAP)}
        for rel, src in _stage_inputs.items():
            shutil.copyfile(src, _abs(rel, tmp))
        _write_face(tmp, face)
        with io.open(_abs(DOC_REL, tmp), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("stale page\n")
        rc, out = _quiet_check(tmp)
        leg("a page that does not re-render is STALE", rc == 3 and "STALE" in out,
            out.strip()[:80])

        # control 4: a missing input face must refuse, not default to zero
        os.remove(_abs(CAP, tmp))
        blocked = derive(tmp)
        leg("a missing input refuses", blocked.get("verdict") == V_BLOCK,
            str(blocked.get("verdict")))
        leg("a missing input prints no window",
            blocked.get("dial_window") is None, "window={}".format(blocked.get("dial_window")))

        _stage_inputs = None
        # restore a clean tree and prove the face returns byte-identically
        for rel in (RENT, FLOOR, CAP):
            shutil.copyfile(_abs(rel, ROOT), _abs(rel, tmp))
        again = derive(tmp)
        _write_face(tmp, again)
        rc, out = _quiet_check(tmp)
        leg("restored bytes check green again", rc == 0, out.strip()[:80])
        for key in ("verdict", "verdict_same_size"):
            leg("restore keeps {}".format(key), again.get(key) == face.get(key),
                "{} vs {}".format(again.get(key), face.get(key)))

        # control 5: the sentence a reader sees must carry the money, not just percentages
        sent = face.get("sentence") or ""
        leg("the sentence prints a CNY figure", "元" in sent, sent[:60])
        leg("the sentence names the 8 % dial", "8%" in sent, sent[:60])
        leg("the page prints both verdicts",
            face.get("verdict") in render_doc(face)
            and face.get("verdict_same_size") in render_doc(face), "")
        leg("the page prints no literal double percent", "%%" not in render_doc(face), "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [l for l in legs if not l[1]]
    for name, ok, detail in legs:
        print("[{}] {}{}".format("PASS" if ok else "FAIL", name,
                                 (" | " + detail) if detail else ""))
    if failed:
        print("{} of {} FAILED".format(len(failed), len(legs)))
        return 1
    print("{} of {} PASS".format(len(legs), len(legs)))
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").strip().lower()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
