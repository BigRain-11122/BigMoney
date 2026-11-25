#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""what do we do with this carry book today, and what exactly would change that?

WHY THIS FILE EXISTS
--------------------
Four rounds each answered one sub-question of the same book and none of them answered
"so what do we do":
  r2094 results/idx_fut_carry_always_on_price.json      -- what one lot is worth in CNY,
                                                           printed per ruler (2.76/9.65/9.68%
                                                           for IC), verdict
                                                           PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND
  r2095 results/idx_fut_carry_capacity_lots.json        -- how big it can get (468/752 lots
                                                           at 1% of ADV), verdict
                                                           MARKET_IS_NOT_THE_GATE
  r2096 results/idx_fut_carry_roll_step_reversal.json   -- whether the roll-day step may be
                                                           booked as that day's return
                                                           (IC: no; IM: undecided)
  r1780 results/idx_fut_carry_open_capital.json         -- what it costs to open, and the
                                                           withdrawn desk ticket

A reader holding four faces still has to decide, and r1779 already recorded what happens
then: every reader decides differently, and the verdict drifts. So this face is the single
place where the decision is written down, and everything else reads it (r1266: a verdict
with no literal consumer is not a verdict).

WHAT THIS FACE DERIVES (and what it merely carries)
---------------------------------------------------
The one thing that is genuinely new here is *ruler admission*. r2094 reported a 6.92pp
spread across three rulers and honestly refused to pick one. r2096 then showed that the
roll-day step is paid by later carry rather than given back the next day -- for IC on both
admissible rulers. A ruler that books that step as the day's return is therefore not "the
worst ruler", it is the WRONG ruler, and averaging it into a band is what made the rate
look ruler-bound. So: a ruler may be quoted only if the roll-step face says its roll-day
accounting is supported. Everything else is carried, not recomputed (each number keeps the
pointer to the face that produced it).

Consequence, and it is the headline: for IC the quotable band collapses from 6.92pp to
0.03pp. For IM no ruler is admitted at all, so IM has no quotable rate today -- printing
5.74-11.96% there would be quoting a number whose accounting is still disputed.

verdict tokens (frozen before the first run; a per-product token, plus a book token):
  NO_ORDER_ACCOUNTING_UNSETTLED     no ruler of this product is admitted, so no rate and no
                                    order: the number itself is undecided
  NO_ORDER_CAPITAL_BELOW_FIRST_RUNG the accounting is fine but the book cannot buy one lot
  NO_ORDER_MARKET_TOO_THIN          capital is fine but the market will not take one lot
  ORDER_ALLOWED_QUOTE_THE_BAND      every gate passes; the order exists but must be quoted
                                    as the admitted band, never as a single point
  book token: NO_ORDER_ON_BOTH_LEGS / ORDER_ALLOWED_ON_SOME_LEGS

precedence (declared, not discovered): accounting > capital > liquidity > order. A book
whose accounting is disputed cannot be "ordered subject to funding" -- funding it does not
resolve the dispute.

Usage:
    python scripts/idx_fut_carry_decision_face.py run
    python scripts/idx_fut_carry_decision_face.py check
    python scripts/idx_fut_carry_decision_face.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_decision_face.json")
FACE_REL = "results/idx_fut_carry_decision_face.json"
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_DECISION_FACE.md")

PRODUCTS = ("IC", "IM")

# the faces this one reads, and the only faces it reads
INPUTS = {
    "price": "results/idx_fut_carry_always_on_price.json",
    "capacity": "results/idx_fut_carry_capacity_lots.json",
    "roll": "results/idx_fut_carry_roll_step_reversal.json",
    "open_capital": "results/idx_fut_carry_open_capital.json",
}

# a ruler is quotable only if this verdict says its roll-day accounting is supported
ADMISSIBLE_VERDICT = "COST_BOOKED_BY_LATER_CARRY"

PRECEDENCE = ("accounting_unsettled", "capital_below_first_rung", "market_too_thin",
              "order_allowed")

TOKENS = {
    "accounting_unsettled": "NO_ORDER_ACCOUNTING_UNSETTLED",
    "capital_below_first_rung": "NO_ORDER_CAPITAL_BELOW_FIRST_RUNG",
    "market_too_thin": "NO_ORDER_MARKET_TOO_THIN",
    "order_allowed": "ORDER_ALLOWED_QUOTE_THE_BAND",
}


# ----------------------------------------------------------------------------- io helpers
def _read_json(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _digest(obj):
    if obj is None:
        return None
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


# ----------------------------------------------------------------------------- the rule
def _state(admitted, capital_cny, first_rung_cny, capacity_lots):
    """Pure decision rule. Order of the gates is the whole policy, so it lives in one
    function that the selftest can drive with numbers it invents."""
    if not admitted:
        return "accounting_unsettled"
    gap = float(first_rung_cny) - float(capital_cny)
    if gap > 1e-9:
        return "capital_below_first_rung"
    if float(capacity_lots) < 1.0:
        return "market_too_thin"
    return "order_allowed"


def _band(values):
    vals = [float(v) for v in values if isinstance(v, (int, float))]
    if not vals:
        return None
    return [min(vals), max(vals)]


def _spread_pp(band):
    if not band:
        return None
    return round(band[1] - band[0], 6)


def price_product(prod, price_face, cap_face, roll_face, open_face):
    """One product's decision, derived from the four faces. Nothing is recomputed from
    panels: the faces own their numbers, this face owns the decision."""
    roll_p = ((roll_face.get("products") or {}).get(prod) or {}).get("rulers") or {}
    price_p = (price_face.get("products") or {}).get(prod) or {}
    cap_p = (cap_face.get("products") or {}).get(prod) or {}
    open_p = (open_face.get("accounts") or {}).get(prod) or {}

    admitted, rejected = [], {}
    for ruler, reading in roll_p.items():
        if reading.get("verdict") == ADMISSIBLE_VERDICT:
            admitted.append(ruler)
        else:
            rejected[ruler] = reading.get("verdict")
    admitted.sort()

    rulers_price = price_p.get("rulers") or {}
    admitted_numbers = {}
    for ruler in admitted:
        rp = rulers_price.get(ruler) or {}
        admitted_numbers[ruler] = {
            "ann_pct": rp.get("always_on_ann_pct"),
            "excess_cny": rp.get("always_on_excess_cny"),
            "excess_pct_of_capital": rp.get("always_on_excess_pct_of_capital"),
            "timed_ann_pct": rp.get("timed_ann_pct"),
        }

    rate_band = _band([v.get("ann_pct") for v in admitted_numbers.values()])
    excess_band = _band([v.get("excess_cny") for v in admitted_numbers.values()])
    excess_pct_band = _band([v.get("excess_pct_of_capital") for v in admitted_numbers.values()])
    # what a reader would have quoted before admission existed
    all_band = _band([v.get("always_on_ann_pct") for v in rulers_price.values()])

    capital = open_p.get("capital_cny")
    first_rung = (cap_p.get("desk") or {}).get("capital_per_lot_cny")
    capacity_lots = (cap_p.get("capacity") or {}).get("adopted_lots")
    if first_rung is None:
        first_rung = open_p.get("funding", {}).get("first_rung_cny")
    if capital is None or first_rung is None or capacity_lots is None:
        return {"product": prod, "status": "DATA_BLOCKED",
                "why": "an upstream face did not carry capital / first rung / capacity"}

    state = _state(admitted, capital, first_rung, capacity_lots)
    gap = round(float(first_rung) - float(capital), 2)

    flips = []
    if state == "accounting_unsettled":
        flips.append({
            "condition": "this product needs at least one ruler whose roll-day accounting is supported",
            "today": "; ".join("%s=%s" % (r, v) for r, v in sorted(rejected.items())),
            "needed": ADMISSIBLE_VERDICT,
            "can_be_bought_with_capital": False,
            "note": ("the sample is not the problem (%s clear the face's own min_pairs=30); "
                     "what has to change is the reading itself, which is why no amount of "
                     "money today moves this gate"
                     % ", ".join("%s=%s pairs" % (r, (roll_p.get(r) or {}).get("pairs"))
                                 for r in sorted(roll_p)
                                 if (roll_p.get(r) or {}).get("pairs"))),
        })
    if gap > 0:
        flips.append({
            "condition": "capital at the first executable rung",
            "today_cny": capital,
            "needed_cny": first_rung,
            "gap_cny": gap,
            "gap_pct_of_book": round(100.0 * gap / float(capital), 4),
            "can_be_bought_with_capital": True,
        })
    if isinstance(capacity_lots, (int, float)) and float(capacity_lots) < 1.0:
        flips.append({"condition": "the market must take at least one lot at the 1% line",
                      "today_lots": capacity_lots, "needed_lots": 1.0,
                      "can_be_bought_with_capital": False})

    why = {
        "accounting_unsettled": "no ruler of this product is admitted, so no rate can be quoted",
        "capital_below_first_rung": "cannot buy one lot at the first rung",
        "market_too_thin": "one lot does not fit inside the 1% ADV line",
        "order_allowed": "all gates pass; quote the band",
    }[state]

    return {
        "product": prod,
        "status": "ok",
        "state": state,
        "token": TOKENS[state],
        "why": why,
        "why_zh": {
            "accounting_unsettled": "这个品种没有任何一把尺子的移仓日会计被采信，所以连一个年化都不该报",
            "capital_below_first_rung": "会计口径已定，但本金买不到一手首档",
            "market_too_thin": "本金够，但 1% ADV 线吞不下一手",
            "order_allowed": "三道门都过：可以下单，但只能报区间",
        }[state],
        "admitted_rulers": admitted,
        "rejected_rulers": rejected,
        "quotable_rate": {
            "ann_pct_band": rate_band,
            "spread_across_admitted_rulers_pp": _spread_pp(rate_band),
            "excess_over_parking_cny_band": excess_band,
            "excess_pct_of_capital_band": excess_pct_band,
            "by_ruler": admitted_numbers,
            "never_quoted_as": "a single point rate -- the admitted rulers disagree by %.3fpp"
                               % (_spread_pp(rate_band) or 0.0),
        },
        "rate_before_admission": {
            "ann_pct_band_all_rulers": all_band,
            "spread_pp": _spread_pp(all_band),
            "note": ("this is the band r2094 reported. It is wider than the quotable band by "
                     "%.2fpp and every pp of that difference comes from a ruler whose "
                     "roll-day accounting this repo has since rejected"
                     % ((_spread_pp(all_band) or 0.0) - (_spread_pp(rate_band) or 0.0))),
        },
        "capital": {"book_cny": capital, "first_rung_cny": first_rung, "gap_cny": gap},
        "capacity": {"adopted_lots": capacity_lots,
                     "headroom_multiple": cap_p.get("headroom_multiple")},
        "desk_ticket": open_p.get("desk_ticket"),
        "what_would_change_it": flips,
    }


def derive(inputs=None):
    inputs = inputs or {k: _read_json(v) for k, v in INPUTS.items()}
    missing = sorted(k for k, v in inputs.items() if v is None)
    if missing:
        return {"kind": "idx_fut_carry_decision_face", "verdict": "DATA_BLOCKED",
                "why": "input face(s) missing: %s" % ", ".join(missing)}

    price, cap, roll, open_cap = (inputs["price"], inputs["capacity"], inputs["roll"],
                                  inputs["open_capital"])
    products = {}
    for prod in PRODUCTS:
        products[prod] = price_product(prod, price, cap, roll, open_cap)

    tokens = {p: (v.get("token") if v.get("status") == "ok" else "DATA_BLOCKED")
              for p, v in products.items()}
    if any(t.startswith("NO_ORDER") for t in tokens.values()) or "DATA_BLOCKED" in tokens.values():
        verdict = "NO_ORDER_ON_BOTH_LEGS" if all(t.startswith("NO_ORDER") for t in tokens.values()) \
            else "NO_ORDER_ON_SOME_LEGS"
    else:
        verdict = "ORDER_ALLOWED_ON_SOME_LEGS"

    cutoffs = {k: v.get("evidence_cutoff") for k, v in inputs.items()}
    known = sorted(c for c in cutoffs.values() if c)
    return {
        "kind": "idx_fut_carry_decision_face",
        "question": ("the four carry faces each answered a sub-question; this one answers "
                     "what the book should do today and what number would change it"),
        "verdict": verdict,
        "reading": {
            "one_line": _one_line(products, verdict),
            "precedence": list(PRECEDENCE),
            "ruler_admission_rule": ("a ruler may be quoted only if the roll-step face says "
                                     "its roll-day accounting is supported (%s)"
                                     % ADMISSIBLE_VERDICT),
        },
        "products": products,
        "evidence_cutoff": min(known) if known else None,
        "input_cutoffs": cutoffs,
        "inputs": {k: {"path": v, "digest": _digest(inputs[k])} for k, v in INPUTS.items()},
        "not_recomputed": [
            "every rate, every CNY figure and every lots figure (they belong to the four faces)",
            "the roll-step verdicts themselves (results/idx_fut_carry_roll_step_reversal.json)",
            "the desk ticket and the withdrawal decision (results/idx_fut_carry_open_capital.json)",
        ],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def _one_line(products, verdict):
    bits = []
    for prod in PRODUCTS:
        p = products.get(prod) or {}
        if p.get("status") != "ok":
            bits.append("%s: %s" % (prod, p.get("status")))
            continue
        band = (p.get("quotable_rate") or {}).get("ann_pct_band")
        if p.get("state") == "accounting_unsettled":
            bits.append("%s 无口径（无可采信尺子）" % prod)
        elif p.get("state") == "capital_below_first_rung":
            bits.append("%s 口径已定（%.2f-%.2f%%）但本金差 %s 元"
                        % (prod, band[0], band[1], "{:,.0f}".format(p["capital"]["gap_cny"])))
        elif p.get("state") == "market_too_thin":
            bits.append("%s 本金够但市场吞不下一手" % prod)
        else:
            bits.append("%s 可下单（%.2f-%.2f%% 区间，禁单点）" % (prod, band[0], band[1]))
    return "%s -- %s" % (verdict, "；".join(bits))


# ----------------------------------------------------------------------------- check
def check(quiet=False):
    """Re-derive and compare. A moved input is STALE (the chain leg may pay for a rebuild);
    a moved number with the same inputs is a real defect and must NOT say STALE (r1850)."""
    published = _read_json(FACE_REL)
    if published is None:
        print("STALE face missing: %s" % FACE_REL)
        return 3
    fresh = derive()
    if fresh.get("verdict") == "DATA_BLOCKED":
        print("STALE upstream face missing: %s" % fresh.get("why"))
        return 3

    stale, problems = [], []
    for prod in PRODUCTS:
        a = (published.get("products") or {}).get(prod) or {}
        b = (fresh.get("products") or {}).get(prod) or {}
        if a.get("status") != b.get("status"):
            problems.append("%s status %r -> %r" % (prod, a.get("status"), b.get("status")))
            continue
        if a.get("status") != "ok":
            continue
        dig_a = ((a.get("quotable_rate") or {}).get("by_ruler") or {})
        dig_b = ((b.get("quotable_rate") or {}).get("by_ruler") or {})
        if dig_a != dig_b:
            stale.append("%s admitted-ruler numbers moved" % prod)
        for key in ("state", "token"):
            if a.get(key) != b.get(key):
                problems.append("%s %s %r -> %r" % (prod, key, a.get(key), b.get(key)))
        if (a.get("admitted_rulers") or []) != (b.get("admitted_rulers") or []):
            problems.append("%s admitted rulers %r -> %r"
                            % (prod, a.get("admitted_rulers"), b.get("admitted_rulers")))
        ca, cb = (a.get("capital") or {}), (b.get("capital") or {})
        if ca.get("gap_cny") != cb.get("gap_cny"):
            problems.append("%s gap %r -> %r" % (prod, ca.get("gap_cny"), cb.get("gap_cny")))
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %r -> %r" % (published.get("verdict"), fresh.get("verdict")))

    if problems:
        if not quiet:
            for p in problems:
                print("CHECK FAILED: %s" % p)
        return 1
    if stale:
        if not quiet:
            for s in stale:
                print("STALE: %s -- rebuild this face" % s)
        return 3
    if not quiet:
        print("CHECK_OK cutoff=%s verdict=%s" % (fresh.get("evidence_cutoff"), fresh.get("verdict")))
    return 0


# ----------------------------------------------------------------------------- doc + run
def _fmt_band(band):
    if not band or band[0] is None:
        return "无可报数"
    return "%.2f%% – %.2f%%" % (band[0], band[1])


def render_doc(face):
    L = ["# 一本书，一张决定面", "",
         "四张面各自回答了一个子问题，没有一张回答「今天这本书做什么」。本面把决定写在唯一一处，",
         "其余各面只读它（r1266：没有字面消费面的裁决不算裁决）。", "",
         "> 本文件由 `python scripts/idx_fut_carry_decision_face.py run` 生成，"
         "**不要手改**。生成时刻 %s，证据截止 %s。" % (face.get("generated"), face.get("evidence_cutoff")),
         "", "## 判词", "", "`%s`" % face.get("verdict"), "",
         "**%s**" % (face.get("reading") or {}).get("one_line"), "",
         "## 尺子准入（本面唯一的新东西）", "",
         (face.get("reading") or {}).get("ruler_admission_rule"), ""]
    for prod in PRODUCTS:
        p = (face.get("products") or {}).get(prod) or {}
        if p.get("status") != "ok":
            L += ["### %s -- %s" % (prod, p.get("status")), "", p.get("why") or "", ""]
            continue
        q = p.get("quotable_rate") or {}
        band = q.get("ann_pct_band") or [None, None]
        ex = q.get("excess_over_parking_cny_band") or [None, None]
        ba = p.get("rate_before_admission") or {}
        L += ["### %s -- `%s`" % (prod, p.get("token")), "",
              "- 为什么：%s" % (p.get("why_zh") or p.get("why")),
              "- 可报区间：**%.2f%% – %.2f%%** 年化（区间内差 %.3fpp）"
              % (band[0], band[1], q.get("spread_across_admitted_rulers_pp") or 0.0)
              if band[0] is not None else "- 可报区间：**无可报数**（口径未定）",
              "- 相对停车的净超额：**%s – %s 元/年**" % ("{:,.0f}".format(ex[0]),
                                                          "{:,.0f}".format(ex[1]))
              if ex[0] is not None else "- 相对停车的净超额：不报（无口径）",
              "- 本金：一档 %s 元，账面 %s 元，差 %s 元"
              % ("{:,.0f}".format(p["capital"]["first_rung_cny"]),
                 "{:,.0f}".format(p["capital"]["book_cny"]),
                 "{:,.0f}".format(p["capital"]["gap_cny"])),
              "- 容量：%s 手（1%% ADV 线）" % p["capacity"]["adopted_lots"],
              "- 准入前那张面给的区间：%s，差 %s pp"
              % (_fmt_band(ba.get("ann_pct_band_all_rulers")), ba.get("spread_pp")),
              "", ]
        L += ["| 尺子 | 判词 | 年化 |", "| --- | --- | --- |"]
        for ruler in p.get("admitted_rulers") or []:
            rr = (q.get("by_ruler") or {}).get(ruler) or {}
            L.append("| %s | 采信 | %.2f%% |" % (ruler, rr.get("ann_pct") or 0.0))
        for ruler, verdict in sorted((p.get("rejected_rulers") or {}).items()):
            L.append("| %s | %s（不采信） | — |" % (ruler, verdict))
        L.append("")
        for flip in p.get("what_would_change_it") or []:
            L.append("- 会改判的条件：%s" % flip.get("condition"))
            for k in ("today_cny", "needed_cny", "gap_cny", "gap_pct_of_book",
                      "today_lots", "needed_lots", "needed", "today", "note"):
                if k in flip:
                    v = flip[k]
                    if isinstance(v, float):
                        v = "{:,.2f}".format(v)
                    L.append("    - %s: %s" % (k, v))
        L.append("")
    L += ["## 本面不重算的东西", ""]
    for n in face.get("not_recomputed") or []:
        L.append("- %s" % n)
    L += ["", "## 输入面", ""]
    for k, v in (face.get("inputs") or {}).items():
        L.append("- %s: `%s` (digest %s)" % (k, v.get("path"), v.get("digest")))
    L.append("")
    return "\n".join(L)


def run():
    face = derive()
    if face.get("verdict") == "DATA_BLOCKED":
        print("BLOCKED: %s" % face.get("why"))
        return 2
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    print("WROTE results/idx_fut_carry_decision_face.json")
    print("WROTE research/IDX_FUT_CARRY_DECISION_FACE.md")
    print("verdict=%s cutoff=%s" % (face.get("verdict"), face.get("evidence_cutoff")))
    for prod in PRODUCTS:
        p = (face.get("products") or {}).get(prod) or {}
        print("  %s %s" % (prod, p.get("token")))
    return 0


# ----------------------------------------------------------------------------- selftest
def _selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- the rule, driven with numbers this test invents
    leg("gate 1: no admitted ruler outranks a capital gap",
        _state([], 1_000_000, 1_129_565.88, 468.0) == "accounting_unsettled")
    leg("gate 2: admitted ruler + short capital -> capital gate",
        _state(["calendar"], 1_000_000, 1_129_565.88, 468.0) == "capital_below_first_rung")
    leg("gate 3: admitted + funded + zero capacity -> liquidity gate",
        _state(["calendar"], 2_000_000, 1_129_565.88, 0.0) == "market_too_thin")
    leg("gate 4: all gates pass -> order allowed",
        _state(["calendar"], 2_000_000, 1_129_565.88, 468.0) == "order_allowed")
    leg("gate 5: exact funding is enough (no tolerance on the wrong side)",
        _state(["calendar"], 1_129_565.88, 1_129_565.88, 1.0) == "order_allowed")

    # --- band arithmetic
    leg("band is min/max, not mean", _band([9.68, 9.65]) == [9.65, 9.68])
    leg("spread of the admitted IC rulers is 0.03pp", abs(_spread_pp(_band([9.65, 9.68])) - 0.03) < 1e-9)
    leg("band ignores non-numeric entries", _band([1.0, None, "x", 2.0]) == [1.0, 2.0])

    # --- admission, on synthetic faces shaped like the real ones
    roll = {"products": {p: {"rulers": {}} for p in PRODUCTS}}
    roll["products"]["IC"]["rulers"] = {
        "published": {"verdict": "DATA_BLOCKED"},
        "calendar": {"verdict": ADMISSIBLE_VERDICT, "pairs": 118},
        "strictest": {"verdict": ADMISSIBLE_VERDICT, "pairs": 128},
    }
    roll["products"]["IM"]["rulers"] = {
        "published": {"verdict": "DATA_BLOCKED"},
        "calendar": {"verdict": "PARTIAL_REVERSAL", "pairs": 51},
        "strictest": {"verdict": "REAL_COST", "pairs": 60},
    }
    price = {"products": {p: {"rulers": {}} for p in PRODUCTS}}
    price["products"]["IC"]["rulers"] = {
        "calendar": {"always_on_ann_pct": 9.65, "always_on_excess_cny": 113697.86,
                     "always_on_excess_pct_of_capital": 10.0656, "timed_ann_pct": 12.02},
        "published": {"always_on_ann_pct": 2.76, "always_on_excess_cny": 30684.38,
                      "always_on_excess_pct_of_capital": 2.7165, "timed_ann_pct": 10.12},
        "strictest": {"always_on_ann_pct": 9.68, "always_on_excess_cny": 114059.31,
                      "always_on_excess_pct_of_capital": 10.0976, "timed_ann_pct": 11.36},
    }
    price["products"]["IM"]["rulers"] = {
        "calendar": {"always_on_ann_pct": 11.96, "always_on_excess_cny": 134382.93,
                     "always_on_excess_pct_of_capital": 11.5931, "timed_ann_pct": 12.75},
        "published": {"always_on_ann_pct": 5.74, "always_on_excess_cny": 63226.13,
                      "always_on_excess_pct_of_capital": 5.4545, "timed_ann_pct": 9.45},
        "strictest": {"always_on_ann_pct": 11.5, "always_on_excess_cny": 129120.53,
                      "always_on_excess_pct_of_capital": 11.1392, "timed_ann_pct": 11.31},
    }
    cap = {"products": {
        "IC": {"capacity": {"adopted_lots": 468.45},
               "desk": {"capital_per_lot_cny": 1129565.88}, "headroom_multiple": 234.22},
        "IM": {"capacity": {"adopted_lots": 752.15},
               "desk": {"capital_per_lot_cny": 1159159.0}, "headroom_multiple": 376.07},
    }}
    openc = {"accounts": {p: {"capital_cny": 1000000.0} for p in PRODUCTS}}

    ic = price_product("IC", price, cap, roll, openc)
    im = price_product("IM", price, cap, roll, openc)

    leg("IC admits exactly the two rulers the roll-step face supports",
        ic.get("admitted_rulers") == ["calendar", "strictest"], str(ic.get("admitted_rulers")))
    leg("IC rejects the published ruler with its own verdict word",
        ic.get("rejected_rulers", {}).get("published") == "DATA_BLOCKED")
    leg("IC quotable band is 9.65-9.68", ic["quotable_rate"]["ann_pct_band"] == [9.65, 9.68],
        str(ic["quotable_rate"]["ann_pct_band"]))
    leg("IC band spread collapses from 6.92pp to 0.03pp",
        abs(ic["rate_before_admission"]["spread_pp"] - 6.92) < 1e-9
        and abs(ic["quotable_rate"]["spread_across_admitted_rulers_pp"] - 0.03) < 1e-9)
    leg("IC is stopped by capital, not by the rate",
        ic["state"] == "capital_below_first_rung" and abs(ic["capital"]["gap_cny"] - 129565.88) < 0.01)
    leg("IC excess band comes from the admitted rulers only",
        ic["quotable_rate"]["excess_over_parking_cny_band"] == [113697.86, 114059.31])
    leg("IM admits no ruler, so IM quotes no rate",
        im["state"] == "accounting_unsettled" and im["quotable_rate"]["ann_pct_band"] is None)
    leg("IM's two admissible-by-sample rulers disagree in kind",
        im["rejected_rulers"] == {"published": "DATA_BLOCKED", "calendar": "PARTIAL_REVERSAL",
                                  "strictest": "REAL_COST"})
    leg("IM still prints what would change it, and says money cannot buy it",
        any(f.get("can_be_bought_with_capital") is False
            for f in im["what_would_change_it"]))
    leg("IM capital gap is still reported even though accounting outranks it",
        abs(im["capital"]["gap_cny"] - 159159.0) < 0.01)

    # --- full-face wiring, including the DATA_BLOCKED path
    face = derive({"price": price, "capacity": cap, "roll": roll, "open_capital": openc})
    leg("face verdict is NO_ORDER_ON_BOTH_LEGS for this real shape",
        face.get("verdict") == "NO_ORDER_ON_BOTH_LEGS", str(face.get("verdict")))
    leg("one_line names both products' gates",
        "IC" in face["reading"]["one_line"] and "IM" in face["reading"]["one_line"])
    blocked = derive({"price": None, "capacity": cap, "roll": roll, "open_capital": openc})
    leg("a missing input refuses instead of defaulting",
        blocked.get("verdict") == "DATA_BLOCKED" and "price" in (blocked.get("why") or ""))

    # --- doc must carry the decision, not hide it
    doc = render_doc(face)
    leg("doc prints the contract tokens", "NO_ORDER_ACCOUNTING_UNSETTLED" in doc
        and "NO_ORDER_CAPITAL_BELOW_FIRST_RUNG" in doc)
    leg("doc prints the flip numbers", "129,565.88" in doc and "1,129,565.88" in doc)
    leg("doc refuses to quote IM", "无可报数" in doc)

    # --- STALE vs CHECK FAILED wording, on a copy
    import tempfile
    tmp = tempfile.mkdtemp(prefix="r2097bmc_")
    good = os.path.join(tmp, "face.json")
    with open(good, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False)
    leg("check reads a hand-edited face as a defect, not as drift",
        _classify(face, dict(face, verdict="ORDER_ALLOWED_ON_SOME_LEGS")) == "CHECK FAILED")
    leg("check reads moved ruler numbers as drift",
        _classify(face, {**face, "products": {**face["products"],
                                              "IC": {**face["products"]["IC"],
                                                     "quotable_rate": {**face["products"]["IC"]["quotable_rate"],
                                                                       "by_ruler": {"calendar": {"ann_pct": 9.66}}}}}}) == "STALE")

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, ("  <- %s" % detail) if detail and not ok else ""))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def _classify(published, fresh):
    """The same comparison check() makes, folded into two words so a test can assert on it."""
    for prod in PRODUCTS:
        a = (published.get("products") or {}).get(prod) or {}
        b = (fresh.get("products") or {}).get(prod) or {}
        if a.get("status") != b.get("status"):
            return "CHECK FAILED"
        if a.get("status") != "ok":
            continue
        if ((a.get("quotable_rate") or {}).get("by_ruler") or {}) != \
                ((b.get("quotable_rate") or {}).get("by_ruler") or {}):
            return "STALE"
        if a.get("state") != b.get("state") or a.get("token") != b.get("token"):
            return "CHECK FAILED"
    if published.get("verdict") != fresh.get("verdict"):
        return "CHECK FAILED"
    return "OK"


def main(argv=None):
    ap = argparse.ArgumentParser(description="the one decision face for the carry book")
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
