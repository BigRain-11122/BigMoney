#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""can the equal-risk re-budget actually be placed? -- the two ends of a capital window

WHY THIS FILE EXISTS
--------------------
r2113 (results/idx_fut_carry_rent_by_component.json) priced an equal-risk-share re-budget:
the equity sleeve to 1.000x NAV, IC to 0.4501x, IM to 0.3897x, and judged
REBUDGETING_WOULD_HELP (Sharpe 1.836 -> 2.043 for 3.76pp of annual return given up). It
ended with the question it did not answer: "does the re-budgeted 1.000x NAV equity sleeve
fit inside the equity book's own capacity" -- the same question r1780 asked about the desk
ticket ("0 lots is a correct number, not an order").

Both ends already exist as published faces and neither had been priced against the other:
  * etf_book_capacity_edge prints, per session, the capital at which the book's own five
    names reach 1% of their 20-bar ADV (today 1,043,801 CNY; 60-session median 496,476);
  * idx_fut_carry_margin prints the notional of one lot at the panel's own close
    (IC 1,153,800 / IM 1,086,880 on 2026-11-25). A weight below one lot's notional cannot
    be held -- the book holds 0 or 1 -- so every weight has a smallest NAV at which it can
    be met without being exceeded.

So each weight set has a LOWER end (NAV at which each weighted futures leg can hold at
least one whole lot) and an UPPER end (NAV at which its equity weight reaches the ADV
line). If lower > upper the re-budget is a direction, not an order, and this face prints
both ends instead of a number.

WHAT IS MEASURED (this repo's own panels and faces)
--------------------------------------------------
  * one-lot notional per product at the panel's own close, imported from the margin face
    (never recomputed here -- r2098's rule: a face reads its inputs);
  * the equity sleeve's 1%-ADV capital, read per session from the capacity edge face and
    reduced to today / median / worst session;
  * both weights sets from r2113: as-built (multiples that are exactly whole lots at the
    1M lens) and the equal-risk re-budget.

WHAT IS A RULE, NOT A MEASUREMENT
---------------------------------
  * the 1% ADV line itself -- inherited from the capacity face so the two books are
    comparable; every CNY ceiling here moves inversely with it;
  * whole lots: no fractional lot is assumed anywhere (that is the point of the lower end);
  * the capacities are read on the capacity face's own five names. A wider equity pool
    would raise the ceiling, and this face says so instead of guessing by how much.

WHAT IT REFUSES TO PRINT
------------------------
  * an impact cost of taking the size: daily bars carry no depth (same refusal as the
    capacity face);
  * a single "recommended capital": the window is printed as an interval with both ends
    named, because a reader with a different ADV line gets a different interval.

verdict tokens (frozen before the first run):
  WINDOW_OPEN           lower end <= upper end today: the weight set is placeable, and the
                        interval is printed (today / median / worst session)
  FLOOR_ABOVE_CAPACITY  lower end > upper end today: no capital at which these weights can
                        be held without the equity sleeve breaching its own ADV line
  NO_FUTURES_LEG        the weight set carries no futures notional (capacity end only)
  DATA_BLOCKED          an upstream face or a required field is missing; refuse, never
                        default to zero

Usage:
    python scripts/idx_fut_carry_rebudget_floor.py run
    python scripts/idx_fut_carry_rebudget_floor.py check
    python scripts/idx_fut_carry_rebudget_floor.py --selftest
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
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_rebudget_floor.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_REBUDGET_FLOOR.md")

RENT = "results/idx_fut_carry_rent_by_component.json"
MARGIN = "results/idx_fut_carry_margin.json"
CAP = "results/etf_book_capacity_edge.json"
OPEN_CAP = "results/idx_fut_carry_open_capital.json"

SCHEMA = "idx-fut-carry-rebudget-floor/v1"
NAV_LENS_CNY = 1000000.0
LINE_PCT = 1.0

V_OPEN = "WINDOW_OPEN"
V_EMPTY = "FLOOR_ABOVE_CAPACITY"
V_NOFUT = "NO_FUTURES_LEG"
V_BLOCK = "DATA_BLOCKED"
VERDICTS = (V_OPEN, V_EMPTY, V_NOFUT, V_BLOCK)

LEG_TO_PRODUCT = {"IC_leg": "IC", "IM_leg": "IM"}


# ------------------------------------------------------------------ io
def _read_json(path, root=None):
    p = path if os.path.isabs(path) else os.path.join(root or ROOT, path)
    if not os.path.exists(p):
        return None
    with io.open(p, "rb") as fh:
        raw = fh.read()
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def _digest(path, root=None):
    p = path if os.path.isabs(path) else os.path.join(root or ROOT, path)
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with io.open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# ------------------------------------------------------------------ math
def _median(xs):
    """The capacity face's own median: the upper middle element of the sorted window
    (etf_book_capacity_edge.py prints caps_sorted[len(caps)//2]). Adopting its definition
    rather than averaging the two middles is what lets the same number appear on both
    faces -- two estimators of one quantity would read as two answers (r1911's class)."""
    s = sorted(xs)
    n = len(s)
    if not n:
        return None
    return s[n // 2]


def _weight_set(rent_rung, key):
    """Return {equity_arm, IC_leg, IM_leg} multiples of NAV for one weight set."""
    if key == "as_built":
        src = rent_rung.get("weights_x_nav") or {}
    else:
        src = ((rent_rung.get("equal_risk_share_capped") or {}).get("implied_notional_x_nav")
               or {})
    out = {}
    for leg in ("equity_arm", "IC_leg", "IM_leg"):
        if leg not in src:
            return None
        out[leg] = float(src[leg])
    return out


def _price_set(weights, notionals, cap_readings):
    """Lower end = NAV at which every weighted futures leg holds one whole lot.
    Upper end = NAV at which the equity weight reaches the ADV line."""
    legs = {}
    lower = 0.0
    for leg in ("IC_leg", "IM_leg"):
        w = weights[leg]
        prod = LEG_TO_PRODUCT[leg]
        notional = notionals.get(prod)
        row = {
            "product": prod,
            "weight_x_nav": round(w, 6),
            "notional_per_lot_cny": notional,
            "lots_at_lens_nav": (round(w * NAV_LENS_CNY / notional, 6)
                                 if notional else None),
            "one_lot_floor_nav_cny": (round(notional / w, 2) if (notional and w > 0)
                                      else None),
        }
        legs[leg] = row
        if notional is None:
            return None
        if w > 0:
            lower = max(lower, notional / w)

    eq_w = weights["equity_arm"]
    equity = {
        "weight_x_nav": round(eq_w, 6),
        "share_of_line_at_lens_nav_pct": (round(eq_w * NAV_LENS_CNY
                                              / cap_readings["today_cny"] * 100.0, 6)
                                          if eq_w and cap_readings["today_cny"] else None),
        "nav_where_at_line_today_cny": (round(cap_readings["today_cny"] / eq_w, 2)
                                        if eq_w else None),
        "nav_where_at_line_median_cny": (round(cap_readings["median_cny"] / eq_w, 2)
                                         if eq_w else None),
        "nav_where_at_line_worst_cny": (round(cap_readings["worst_cny"] / eq_w, 2)
                                        if eq_w else None),
    }

    if lower <= 0.0:
        verdict = V_NOFUT
        window = None
    else:
        upper_today = cap_readings["today_cny"] / eq_w if eq_w else 0.0
        upper_median = cap_readings["median_cny"] / eq_w if eq_w else 0.0
        upper_worst = cap_readings["worst_cny"] / eq_w if eq_w else 0.0
        verdict = V_OPEN if lower <= upper_today else V_EMPTY
        window = {
            "lower_cny": round(lower, 2),
            "upper_today_cny": round(upper_today, 2),
            "upper_median_cny": round(upper_median, 2),
            "upper_worst_cny": round(upper_worst, 2),
            "open_today": verdict == V_OPEN,
            "width_today_cny": round(upper_today - lower, 2),
            "floor_over_upper_today": (round(lower / upper_today, 6)
                                       if upper_today else None),
            "equity_weight_that_would_fit_at_floor": (
                round(cap_readings["today_cny"] / lower, 6) if lower else None),
        }

    binding = None
    if lower > 0:
        binding = max(((leg, legs[leg]["one_lot_floor_nav_cny"]) for leg in legs
                       if legs[leg]["one_lot_floor_nav_cny"]), key=lambda t: t[1])[0]
    return {
        "verdict": verdict,
        "legs": legs,
        "equity": equity,
        "window": window,
        "binding_leg": binding,
    }


# ------------------------------------------------------------------ derive
def derive(root=None):
    root = root or ROOT
    rent = _read_json(RENT, root)
    margin = _read_json(MARGIN, root)
    cap = _read_json(CAP, root)
    open_cap = _read_json(OPEN_CAP, root)

    face = {
        "schema": SCHEMA,
        "kind": "idx_fut_carry_rebudget_floor",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": ("r2113 judged the equal-risk re-budget worth 0.208 of Sharpe on paper -- "
                     "at what capital, if any, can those weights actually be held without "
                     "breaching either end of the book: one whole futures lot, and the equity "
                     "sleeve's own 1% ADV line?"),
        "rules": {
            "lower_end": ("NAV at which a weighted futures leg holds one whole lot: "
                          "notional_per_lot / weight. Below it the book is either 0 lots or "
                          "over its own target weight"),
            "upper_end": ("NAV at which the equity weight reaches the 1% ADV line: "
                          "capacity_where_at_line / equity_weight"),
            "one_lot_notional": "imported from idx_fut_carry_margin at the panel's own close",
            "line_pct": LINE_PCT,
            "lens_nav_cny": NAV_LENS_CNY,
            "verdict_rule": ("OPEN if lower <= upper read on the most permissive session "
                             "(today); EMPTY otherwise. A face that fails on its friendliest "
                             "reading is a strong statement"),
            "not_recomputed": ["per-lot notional", "the ADV line and its 60-session window",
                               "r2113's weights and its Sharpe arithmetic"],
        },
        "inputs": {
            "rent_by_component": {"path": RENT, "sha256": _digest(RENT, root)},
            "margin": {"path": MARGIN, "sha256": _digest(MARGIN, root)},
            "capacity_edge": {"path": CAP, "sha256": _digest(CAP, root)},
            "open_capital": {"path": OPEN_CAP, "sha256": _digest(OPEN_CAP, root)},
        },
        "rungs": {},
        "cross_face": {},
        "scope_limits": [],
        "verdict": V_BLOCK,
    }

    if not (rent and margin and cap):
        face["why"] = "a required upstream face is missing"
        return face

    prods = margin.get("products") or {}
    notionals = {}
    for prod in ("IC", "IM"):
        row = prods.get(prod) or {}
        notionals[prod] = row.get("notional_per_lot_cny")
    if any(v is None for v in notionals.values()):
        face["why"] = "margin face does not price both products"
        return face

    sessions = cap.get("sessions") or []
    readings = [s.get("capital_where_at_line_cny") for s in sessions
                if isinstance(s.get("capital_where_at_line_cny"), (int, float))]
    if not readings:
        face["why"] = "capacity face carries no per-session reading"
        return face
    cap_readings = {
        "n_sessions": len(readings),
        "today_cny": readings[-1],
        "median_cny": _median(readings),
        "worst_cny": min(readings),
        "best_cny": max(readings),
        "today_bar": (sessions[-1] or {}).get("bar"),
        "names": cap.get("picks") or [],
    }
    face["equity_capacity"] = {
        "n_sessions": cap_readings["n_sessions"],
        "today_cny": round(cap_readings["today_cny"], 2),
        "today_bar": cap_readings["today_bar"],
        "median_cny": round(cap_readings["median_cny"], 2),
        "worst_cny": round(cap_readings["worst_cny"], 2),
        "best_cny": round(cap_readings["best_cny"], 2),
        "names": cap_readings["names"],
        "line_pct": LINE_PCT,
    }

    rent_rungs = rent.get("rungs") or {}
    primary = None
    for key in sorted(rent_rungs.keys()):
        rung = rent_rungs[key]
        entry = {
            "ic_lots_published": rung.get("ic_lots"),
            "im_lots_published": rung.get("im_lots"),
            "judgment_rebudget": (rung.get("judgment") or {}).get("rebudget"),
            "sets": {},
        }
        for set_key in ("as_built", "re_budget"):
            weights = _weight_set(rung, set_key)
            if weights is None:
                continue
            priced = _price_set(weights, notionals, cap_readings)
            if priced is None:
                continue
            entry["sets"][set_key] = priced
            if set_key == "re_budget":
                primary = priced["verdict"] if primary is None else primary
        face["rungs"][key] = entry

    face["notionals"] = {
        "IC": {"notional_per_lot_cny": notionals["IC"],
               "close": (prods.get("IC") or {}).get("close"),
               "bar": (prods.get("IC") or {}).get("bar")},
        "IM": {"notional_per_lot_cny": notionals["IM"],
               "close": (prods.get("IM") or {}).get("close"),
               "bar": (prods.get("IM") or {}).get("bar")},
    }

    # ---- cross-face readings, named rather than averaged
    summary = cap.get("summary") or {}
    cf = {}
    diffs = [abs(cap_readings["median_cny"] - summary.get("capital_median_cny", float("nan"))),
             abs(cap_readings["worst_cny"] - summary.get("capital_min_cny", float("nan")))]
    cf["capacity_summary"] = {
        "status": ("CROSS_FACE_MATCHES" if max(diffs) <= 0.01
                   else "CROSS_FACE_DISAGREES"),
        "from_sessions": {"median_cny": round(cap_readings["median_cny"], 2),
                          "worst_cny": round(cap_readings["worst_cny"], 2)},
        "from_summary": {"median_cny": summary.get("capital_median_cny"),
                         "worst_cny": summary.get("capital_min_cny")},
    }
    accounts = (open_cap or {}).get("accounts") or {}
    cf_rows = {}
    for prod in ("IC", "IM"):
        first = ((accounts.get(prod) or {}).get("funding") or {}).get("first_rung_cny")
        if isinstance(first, (int, float)) and notionals[prod]:
            cf_rows[prod] = {
                "vol_ruler_first_rung_cny": first,
                "notional_ruler_cny": notionals[prod],
                "ratio_vol_over_notional": round(first / notionals[prod], 6),
            }
    cf["open_capital"] = {
        "status": "DIFFERENT_RULER_NAMED" if cf_rows else "FACE_MISSING",
        "rows": cf_rows,
        "why": ("the first rung on the open-capital face divides per-lot volatility by the "
                "8% risk budget; this face divides a lot's notional by a weight. Two rulers, "
                "not two answers -- neither is averaged into the other"),
    }
    face["cross_face"] = cf

    # ---- top-level verdict = the rung r2113 judged helpful
    helpful = [k for k, v in face["rungs"].items()
               if v.get("judgment_rebudget") == "REBUDGETING_WOULD_HELP"
               and "re_budget" in (v.get("sets") or {})]
    if helpful:
        face["verdict"] = face["rungs"][helpful[0]]["sets"]["re_budget"]["verdict"]
        face["verdict_rung"] = helpful[0]
    else:
        face["verdict"] = V_BLOCK
        face["why"] = "no rung carries a re-budget to price"
        return face

    # ---- the sentence a reader needs
    rung = face["rungs"][face["verdict_rung"]]
    reb = rung["sets"]["re_budget"]
    built = rung["sets"].get("as_built") or {}
    if face["verdict"] == V_EMPTY:
        face["sentence"] = (
            "在 r2113 判「重配会更好」的那一档上，重配权重没有任何资本能放下：两条期货腿的"
            "整手地板是 {lower} 元（约束腿 {leg}），而权益袖 1.000 倍在今天的 1% ADV 线上"
            "只容得下 {upper} 元——下限是上限的 {mult} 倍。"
            "作为对照，现在的权重在这条线上是开着的：[{bl}, {bu}]（今日口径）。"
        ).format(lower=format(int(round(reb["window"]["lower_cny"])), ","),
                 leg=reb["binding_leg"],
                 upper=format(int(round(reb["window"]["upper_today_cny"])), ","),
                 mult=format(reb["window"]["floor_over_upper_today"], ".2f"),
                 bl=format(int(round(built["window"]["lower_cny"])), ",") if built.get("window") else "n/a",
                 bu=format(int(round(built["window"]["upper_today_cny"])), ",") if built.get("window") else "n/a")
    elif face["verdict"] == V_OPEN:
        face["sentence"] = (
            "重配权重能放下：整手地板 {lower} 元 <= 权益袖 1% ADV 线 {upper} 元，"
            "窗口 [{lower}, {upper}] 元（今日口径）。"
        ).format(lower=format(int(round(reb["window"]["lower_cny"])), ","),
                 upper=format(int(round(reb["window"]["upper_today_cny"])), ","))
    else:
        face["sentence"] = "这一档没有期货腿：只有权益袖的容量一端可以印。"

    face["scope_limits"] = [
        "容量上限读的是容量面自己的五个名字；更宽的票池会抬高上限，本面只说「会更高」不猜高多少",
        "1% ADV 是闸选的线不是量出来的线；换线每个上限按同一比例移动（0.5% 减半、2% 翻倍）",
        "整手地板用的是面板自己的收盘价；隔日价格移动会把地板按同一比例拖动",
        "不印冲击成本：日线没有深度，本面停在「占成交额多少」这一端",
        "r2113 的夏普增益是历史分段的算术，不是对未来的承诺；本面只回答它能不能被持有",
    ]
    return face


# ------------------------------------------------------------------ page
def _cny(x):
    return format(int(round(x)), ",")


def _pct(x, nd=4):
    return format(x, "." + str(nd) + "f")


def render_doc(face):
    L = []
    L.append("# 等风险重配能不能真的下单：一条资本窗口的两个端点")
    L.append("")
    L.append("generated {} | 判决 **{}** | 证据截止 {} | 档 {} | 1% ADV 线（容量面自己的五个名字）".format(
        face.get("generated"), face.get("verdict"), _cutoff(face), face.get("verdict_rung")))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append(face.get("sentence") or "（无判词）")
    L.append("")
    eq = face.get("equity_capacity") or {}
    L.append("权益袖那一端（1% ADV 上「满仓权益」能有多少资本）：今天 **{} 元**（{}），"
             "60 个 session 中位 **{} 元**、最差 **{} 元**、最好 **{} 元**；名字 = {}".format(
                 _cny(eq.get("today_cny") or 0), eq.get("today_bar"),
                 _cny(eq.get("median_cny") or 0), _cny(eq.get("worst_cny") or 0),
                 _cny(eq.get("best_cny") or 0), "、".join(eq.get("names") or [])))
    L.append("")

    for rung_key in sorted((face.get("rungs") or {}).keys()):
        entry = face["rungs"][rung_key]
        L.append("## 档 {}（r2113 已发布：IC {} 手 / IM {} 手，重配判词 {}）".format(
            rung_key, entry.get("ic_lots_published"), entry.get("im_lots_published"),
            entry.get("judgment_rebudget")))
        L.append("")
        for set_key in ("as_built", "re_budget"):
            s = (entry.get("sets") or {}).get(set_key)
            if not s:
                continue
            label = "现在这套权重" if set_key == "as_built" else "等风险重配（r2113）"
            L.append("### {}".format(label))
            L.append("")
            L.append("| 腿 | 权重 ×NAV | 每手名义额 (元) | 1M 镜头上是多少手 | 整手地板 NAV (元) |")
            L.append("|---|---:|---:|---:|---:|")
            for leg in ("IC_leg", "IM_leg"):
                row = s["legs"][leg]
                L.append("| {} | {} | {} | {} | {} |".format(
                    row["product"], _pct(row["weight_x_nav"], 4),
                    _cny(row["notional_per_lot_cny"]),
                    _pct(row["lots_at_lens_nav"], 4) if row["lots_at_lens_nav"] is not None else "n/a",
                    _cny(row["one_lot_floor_nav_cny"]) if row["one_lot_floor_nav_cny"] else "—"))
            e = s["equity"]
            L.append("")
            L.append("权益袖权重 **{} ×NAV**：在 1M 镜头上占线的 **{}%**；1% ADV 线对应的 NAV = "
                     "今天 **{} 元** / 中位 **{} 元** / 最差 **{} 元**。".format(
                         _pct(e["weight_x_nav"], 4),
                         _pct(e["share_of_line_at_lens_nav_pct"], 4) if e["share_of_line_at_lens_nav_pct"] is not None else "n/a",
                         _cny(e["nav_where_at_line_today_cny"] or 0),
                         _cny(e["nav_where_at_line_median_cny"] or 0),
                         _cny(e["nav_where_at_line_worst_cny"] or 0)))
            w = s.get("window")
            if w:
                L.append("")
                L.append("窗口：下限 **{} 元**（约束腿 {}）→ 上限 今天 **{} 元** / 中位 **{} 元** / "
                         "最差 **{} 元**；判 **{}**{}".format(
                             _cny(w["lower_cny"]), s.get("binding_leg"),
                             _cny(w["upper_today_cny"]), _cny(w["upper_median_cny"]),
                             _cny(w["upper_worst_cny"]), s["verdict"],
                             "" if w["open_today"] else
                             "（下限是今日上限的 {} 倍）".format(_pct(w["floor_over_upper_today"], 2))))
                if not w["open_today"] and w.get("equity_weight_that_would_fit_at_floor"):
                    L.append("")
                    L.append("把窗口打开的第一条路：在同一资本（{} 元）上把权益袖权重压到 "
                             "≤ **{} ×NAV**，而不是 1.000。".format(
                                 _cny(w["lower_cny"]),
                                 _pct(w["equity_weight_that_would_fit_at_floor"], 4)))
            L.append("")

    L.append("## 跨面对账（说清是哪把尺子，不取平均）")
    L.append("")
    cf = face.get("cross_face") or {}
    cap_cf = cf.get("capacity_summary") or {}
    L.append("- 容量面摘要 vs 本面从 sessions 重算：**{}**（中位 {} vs {}，最差 {} vs {}）。".format(
        cap_cf.get("status"),
        _cny((cap_cf.get("from_sessions") or {}).get("median_cny") or 0),
        _cny((cap_cf.get("from_summary") or {}).get("median_cny") or 0),
        _cny((cap_cf.get("from_sessions") or {}).get("worst_cny") or 0),
        _cny((cap_cf.get("from_summary") or {}).get("worst_cny") or 0)))
    oc = cf.get("open_capital") or {}
    for prod, row in sorted((oc.get("rows") or {}).items()):
        L.append("- {}：开仓面的首档 **{} 元** 是「每手波动 ÷ 8% 预算」这把尺子，"
                 "本面的每手名义额是 **{} 元**，比值 {} —— **{}**。".format(
                     prod, _cny(row["vol_ruler_first_rung_cny"]),
                     _cny(row["notional_ruler_cny"]),
                     _pct(row["ratio_vol_over_notional"], 4), oc.get("status")))
    L.append("")
    L.append("## 本面不印什么")
    L.append("")
    for s in (face.get("scope_limits") or []):
        L.append("- " + s)
    L.append("")
    L.append("## 判词口径")
    L.append("")
    for k in ("lower_end", "upper_end", "verdict_rule"):
        L.append("- **{}**：{}".format(k, (face.get("rules") or {}).get(k)))
    L.append("")
    return "\n".join(L)


def _cutoff(face):
    for key in ("evidence_cutoff",):
        if face.get(key):
            return face[key]
    eq = face.get("equity_capacity") or {}
    return eq.get("today_bar") or "?"


# ------------------------------------------------------------------ check
def check(quiet=False):
    """A moved input face says STALE; identical inputs with different numbers say
    CHECK_FAILED (r1850/r1935/r2098). The page is part of the face: if it does not
    re-render from the published JSON, it lags its writer (r1781)."""
    published = _read_json(OUT_PATH)
    if published is None:
        print("STALE face missing: results/idx_fut_carry_rebudget_floor.json")
        return 3
    fresh = derive()

    moved = sorted(k for k, v in (published.get("inputs") or {}).items()
                   if (fresh.get("inputs") or {}).get(k) != v)
    if moved:
        if not quiet:
            print("STALE: input face(s) moved: {} -- rebuild this face".format(", ".join(moved)))
        return 3

    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict {!r} -> {!r}".format(published.get("verdict"), fresh.get("verdict")))
    for rung_key, entry in (fresh.get("rungs") or {}).items():
        old = (published.get("rungs") or {}).get(rung_key) or {}
        for set_key, s in (entry.get("sets") or {}).items():
            o = (old.get("sets") or {}).get(set_key) or {}
            if not o:
                problems.append("{}/{} set missing in the published face".format(rung_key, set_key))
                continue
            if o.get("verdict") != s.get("verdict"):
                problems.append("{}/{} verdict {!r} -> {!r}".format(
                    rung_key, set_key, o.get("verdict"), s.get("verdict")))
            for leg in ("IC_leg", "IM_leg"):
                a = (o.get("legs") or {}).get(leg) or {}
                b = (s.get("legs") or {}).get(leg) or {}
                for key in ("weight_x_nav", "notional_per_lot_cny", "one_lot_floor_nav_cny"):
                    va, vb = a.get(key), b.get(key)
                    if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                        if abs(float(va) - float(vb)) > 0.02:
                            problems.append("{}/{} {} {} {!r} -> {!r}".format(
                                rung_key, set_key, leg, key, va, vb))
                    elif va != vb:
                        problems.append("{}/{} {} {} {!r} -> {!r}".format(
                            rung_key, set_key, leg, key, va, vb))
            wa, wb = (o.get("window") or {}), (s.get("window") or {})
            if bool(wa) != bool(wb):
                problems.append("{}/{} window presence changed".format(rung_key, set_key))
            for key in ("lower_cny", "upper_today_cny", "upper_median_cny"):
                va, vb = wa.get(key), wb.get(key)
                if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                    if abs(float(va) - float(vb)) > 0.02:
                        problems.append("{}/{} window {} {!r} -> {!r}".format(
                            rung_key, set_key, key, va, vb))

    if problems:
        print("CHECK FAILED results/idx_fut_carry_rebudget_floor.json (same inputs, different numbers)")
        for p in problems[:12]:
            print("  - " + p)
        return 3

    # the page must re-render byte-identically from the published JSON
    want = render_doc(published)
    got = None
    if os.path.exists(DOC_PATH):
        with io.open(DOC_PATH, "r", encoding="utf-8") as fh:
            got = fh.read()
    if got != want:
        print("STALE: research/IDX_FUT_CARRY_REBUDGET_FLOOR.md does not re-render from the "
              "published face (pay the writer)")
        return 3

    if not quiet:
        print("CHECK_OK idx_fut_carry_rebudget_floor (verdict {}, rung {})".format(
            published.get("verdict"), published.get("verdict_rung")))
    return 0


# ------------------------------------------------------------------ run
def run():
    face = derive()
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    with io.open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    print("WROTE results/idx_fut_carry_rebudget_floor.json verdict={} rung={}".format(
        face.get("verdict"), face.get("verdict_rung")))
    for rung_key in sorted((face.get("rungs") or {}).keys()):
        for set_key in ("as_built", "re_budget"):
            s = ((face["rungs"][rung_key].get("sets") or {}).get(set_key))
            if not s:
                continue
            w = s.get("window") or {}
            print("  {}/{}: {} | lower {} | upper(today) {}".format(
                rung_key, set_key, s["verdict"],
                _cny(w.get("lower_cny") or 0), _cny(w.get("upper_today_cny") or 0)))
    print("  " + (face.get("sentence") or ""))
    return 0


# ------------------------------------------------------------------ selftest
def _selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    face = derive()
    leg("verdict is one of the frozen tokens", face.get("verdict") in VERDICTS,
        face.get("verdict"))
    leg("all four inputs digested", all((face.get("inputs") or {}).get(k, {}).get("sha256")
                                        for k in ("rent_by_component", "margin",
                                                  "capacity_edge", "open_capital")))

    rungs = face.get("rungs") or {}
    leg("rung 1/1 priced", "1/1" in rungs, ",".join(sorted(rungs.keys())))

    bad = []
    for rung_key, entry in rungs.items():
        for set_key, s in (entry.get("sets") or {}).items():
            for leg_key in ("IC_leg", "IM_leg"):
                row = s["legs"][leg_key]
                if row["weight_x_nav"] <= 0:
                    continue
                # identity: floor x weight == one lot's notional
                calc = row["one_lot_floor_nav_cny"] * row["weight_x_nav"]
                if abs(calc - row["notional_per_lot_cny"]) > 0.05:
                    bad.append((rung_key, set_key, leg_key, calc, row["notional_per_lot_cny"]))
                # identity: lots at the lens == weight x lens / notional
                calc_lots = row["weight_x_nav"] * NAV_LENS_CNY / row["notional_per_lot_cny"]
                if abs(calc_lots - row["lots_at_lens_nav"]) > 1e-5:
                    bad.append((rung_key, set_key, leg_key, "lots", calc_lots,
                                row["lots_at_lens_nav"]))
    leg("floor x weight == one lot's notional (and lots = weight x lens / notional)",
        not bad, str(bad[:2]))

    # the as-built weights must be whole lots at the 1M lens, or the floor math is measuring
    # a different book than r2113 (r1779: name the ruler before dividing by it)
    bad = []
    for rung_key, entry in rungs.items():
        s = (entry.get("sets") or {}).get("as_built")
        if not s:
            continue
        for leg_key, lots in (("IC_leg", entry.get("ic_lots_published")),
                              ("IM_leg", entry.get("im_lots_published"))):
            row = s["legs"][leg_key]
            want = (lots or 0) * row["notional_per_lot_cny"] / NAV_LENS_CNY
            if abs(want - row["weight_x_nav"]) > 1e-4:
                bad.append((rung_key, leg_key, want, row["weight_x_nav"]))
    leg("as-built weights are exactly whole lots at the 1M lens", not bad, str(bad[:2]))

    # the capacity readings must agree with the capacity face's own summary
    cf = (face.get("cross_face") or {}).get("capacity_summary") or {}
    leg("capacity sessions agree with the capacity face summary",
        cf.get("status") == "CROSS_FACE_MATCHES", cf.get("status"))

    # the open-capital face is a different ruler, and this face must say which
    oc = (face.get("cross_face") or {}).get("open_capital") or {}
    leg("open-capital first rung is named as a different ruler",
        oc.get("status") in ("DIFFERENT_RULER_NAMED", "FACE_MISSING"), oc.get("status"))

    # window arithmetic on the valuable rung
    reb = ((rungs.get("1/1") or {}).get("sets") or {}).get("re_budget") or {}
    w = reb.get("window") or {}
    leg("re-budget rung priced with a window", bool(w), str(sorted(w.keys())))
    if w:
        lower = max(r["one_lot_floor_nav_cny"] for r in reb["legs"].values()
                    if r["one_lot_floor_nav_cny"])
        leg("lower end is the max of the per-leg floors", abs(lower - w["lower_cny"]) <= 0.01,
            "{} vs {}".format(lower, w["lower_cny"]))
        eq_w = reb["equity"]["weight_x_nav"]
        cap_today = (face.get("equity_capacity") or {}).get("today_cny")
        leg("upper end is capacity / equity weight",
            abs(cap_today / eq_w - w["upper_today_cny"]) <= 0.02,
            "{} vs {}".format(cap_today / eq_w, w["upper_today_cny"]))
        leg("verdict follows the rule (open iff lower <= upper on today's reading)",
            (reb["verdict"] == V_OPEN) == (lower <= w["upper_today_cny"]),
            reb["verdict"])
        leg("an empty window names the equity weight that would fit",
            reb["verdict"] != V_EMPTY or (w.get("equity_weight_that_would_fit_at_floor") or 0) > 0)

    # ---- behaviour legs: the same three states check() must tell apart
    tmpdir = tempfile.mkdtemp(prefix="r2114rebudget_")
    saved_out, saved_doc = globals()["OUT_PATH"], globals()["DOC_PATH"]
    try:
        good = os.path.join(tmpdir, "good.json")
        shutil.copyfile(OUT_PATH if os.path.exists(OUT_PATH) else _write_tmp_face(tmpdir), good)
        globals()["OUT_PATH"] = good
        shutil.copyfile(saved_doc if os.path.exists(saved_doc) else _write_tmp_doc(tmpdir, face),
                        os.path.join(tmpdir, "face.md"))
        globals()["DOC_PATH"] = os.path.join(tmpdir, "face.md")
        with io.open(good, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        with io.open(saved_doc, "r", encoding="utf-8") as fh:
            doc_bytes = fh.read()
        with io.open(globals()["DOC_PATH"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_bytes)

        ok_rc = check(quiet=True)
        leg("check() passes on an untouched copy", ok_rc == 0, "rc={}".format(ok_rc))

        tampered = json.loads(json.dumps(payload))
        tampered["rungs"]["1/1"]["sets"]["re_budget"]["legs"]["IC_leg"][
            "one_lot_floor_nav_cny"] += 1000.0
        _dump(tampered, globals()["OUT_PATH"])
        rc, out = _capture_check()
        leg("a hand-edited number says CHECK FAILED and not STALE",
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out.splitlines()[:1])

        moved = json.loads(json.dumps(payload))
        moved["inputs"]["margin"]["sha256"] = "0" * 64
        _dump(moved, globals()["OUT_PATH"])
        rc, out = _capture_check()
        leg("a moved input face says STALE", rc == 3 and "STALE" in out, out.splitlines()[:1])

        _dump(payload, globals()["OUT_PATH"])
        with io.open(globals()["DOC_PATH"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_bytes.replace("窗口", "窗 口", 1))
        rc, out = _capture_check()
        leg("a page that no longer re-renders says STALE",
            rc == 3 and "STALE" in out and "re-render" in out, out.splitlines()[:1])

        with io.open(globals()["DOC_PATH"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_bytes)
        os.remove(globals()["OUT_PATH"])
        rc, out = _capture_check()
        leg("a missing face says STALE face missing", rc == 3 and "face missing" in out,
            out.splitlines()[:1])
    finally:
        globals()["OUT_PATH"], globals()["DOC_PATH"] = saved_out, saved_doc
        shutil.rmtree(tmpdir, ignore_errors=True)

    # page must print the three tokens a reader needs
    doc = ""
    if os.path.exists(DOC_PATH):
        with io.open(DOC_PATH, "r", encoding="utf-8") as fh:
            doc = fh.read()
    leg("page prints the verdict and both ends",
        face.get("verdict", "") in doc and "下限" in doc and "上限" in doc)
    leg("page prints the cross-face ruler note", "DIFFERENT_RULER_NAMED" in doc or "尺子" in doc)

    bad = [t for t in legs if not t[1]]
    for name, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  <- " + str(detail)) if (detail and not ok) else ""))
    print("{} legs, {} failed".format(len(legs), len(bad)))
    return 0 if not bad else 1


def _dump(obj, path):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


def _write_tmp_face(tmpdir):
    face = derive()
    p = os.path.join(tmpdir, "built.json")
    _dump(face, p)
    return p


def _write_tmp_doc(tmpdir, face):
    p = os.path.join(tmpdir, "built.md")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    return p


def _capture_check():
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = check()
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


# ------------------------------------------------------------------ main
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("run", "--run"):
        return run()
    if argv[0] in ("check", "--check"):
        return check()
    if argv[0] in ("--selftest", "selftest"):
        return _selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
