"""What the 5pp target is worth -- the wait priced in years, in remakes, and in money.

r1764/r1766 printed the ruler's own answer: pulling the 5-seat book's select-leg MDE80
from 8.74pp down to 5.0pp needs 5,077 bars against the 1,662 on the shelf.  That number
is honest and unusable on its own -- nobody said what three times the sample buys, or
what it costs to sit and wait for it.  This face prices the wait, on the book's own
published numbers only (no panel read, no new backtest, no new claim):

  years     3,415 more bars at the calendar's own pace
  remakes   how many times the book turns over while you wait, from its own published
            mean turnover per bar
  money     what N years of the book's own published excess is worth, against what N
            years of its own published cost is worth, weighted by the face's own
            one-sided false-positive rate

The money half collapses to one number: the break-even false-positive rate p*.  If
p* >= 1 the wait cannot pay for itself even at certainty that the book has no edge.

Everything is quoted from ONE upstream receipt (results/etf_book_seat_mde.json, the
5-seat row); this face adds no measurement of its own and would rather say STALE than
price an input that moved.

Modes: run (default) | --check | --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAT_FACE = "results/etf_book_seat_mde.json"
OUT = os.path.join(BASE, "results", "etf_book_target_price.json")
MD = os.path.join(BASE, "research", "ETF_BOOK_TARGET_PRICE.md")

LENS_CNY = 1_000_000.0
SEATS = 5
TARGETS = (8.0, 7.0, 6.0, 5.0)          # below the current MDE80; the current row costs 0
HORIZONS_YEARS = (2.0, 5.0, 10.0)       # what a fixed wait buys instead
RATIO_FAIR = 10.0                       # 10x headroom before "the wait is the mistake"
TOL = 1e-9


def _read_json(rel):
    path = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def as_fraction(value):
    """pp -> fraction, with the conversion recorded rather than assumed.

    Every money field on the upstream receipt is in pp (7.7638, -1.3962); the compounding
    below needs fractions.  A value already <= 1.0 is taken as a fraction so synthetic
    fixtures can pass either shape, and unit_guess says which read was used, because the
    r1775 lesson is that the same helper on two conventions is a silent 100x.
    """
    if value is None:
        return None, None
    v = float(value)
    if abs(v) > 1.0:
        return v / 100.0, "pp"
    return v, "fraction"


def seat_row(face, seats=SEATS):
    for r in (face or {}).get("rows") or []:
        if int(r.get("n_hold", -1)) == int(seats):
            return r
    return None


def bars_for_target(bars_now, mde_now, target):
    """The same ruler r1764 used: MDE scales as 1/sqrt(n), so n ~ (mde/target)^2."""
    if bars_now is None or mde_now is None or target is None:
        return None
    bars_now, mde_now, target = float(bars_now), float(mde_now), float(target)
    if target <= 0:
        return None
    if target >= mde_now:
        return bars_now          # already at or past this precision: no wait, never negative
    return bars_now * (mde_now / target) ** 2


def years_for_bars(wait_bars, per_year):
    if wait_bars is None or not per_year:
        return None
    return float(wait_bars) / float(per_year)


def money_forgo(lens, excess_frac, years):
    """Excess the claim refuses to earn while it waits (edge is real)."""
    if None in (lens, excess_frac, years):
        return None
    return float(lens) * ((1.0 + float(excess_frac)) ** float(years) - 1.0)


def money_fake_cost(lens, cost_frac, years):
    """Drag the claim avoids by not running a book that has no edge (cost is negative)."""
    if None in (lens, cost_frac, years):
        return None
    c = abs(float(cost_frac))
    if c >= 1.0:
        return None
    return float(lens) * (1.0 - (1.0 - c) ** float(years))


def verdict_for(ratio):
    if ratio is None:
        return "NO_VERDICT"
    if ratio >= RATIO_FAIR:
        return "WAITING_COSTS_MORE_THAN_IT_INSURES"
    if ratio >= 1.0:
        return "THE_TARGET_IS_A_FAIR_TRADE"
    return "WAITING_IS_CHEAP"


def price_row(mde_now, bars_now, target, per_year, block, turnover,
              excess_frac, cost_frac, p, lens=LENS_CNY):
    bars = bars_for_target(bars_now, mde_now, target)
    wait = None if bars is None else max(0.0, float(bars) - float(bars_now))
    years = years_for_bars(wait, per_year)
    forgo = money_forgo(lens, excess_frac, years)
    fake = money_fake_cost(lens, cost_frac, years)
    avoided = None if (fake is None or p is None) else float(p) * fake
    ratio = None
    if forgo is not None and avoided:
        ratio = forgo / avoided
    p_star = None
    if forgo is not None and fake:
        p_star = forgo / fake
    return {
        "target_pp": round(float(target), 4),
        "bars_needed": None if bars is None else int(round(bars)),
        "wait_bars": None if wait is None else int(round(wait)),
        "wait_years": None if years is None else round(years, 3),
        "rebalances_in_wait": None if wait is None or not block else round(wait / float(block), 2),
        "book_turns_in_wait": None if wait is None or turnover is None else round(wait * float(turnover), 1),
        "forgo_cny": None if forgo is None else round(forgo, 1),
        "avoided_cny": None if avoided is None else round(avoided, 1),
        "ratio": None if ratio is None else round(ratio, 4),
        "p_star": None if p_star is None else round(p_star, 4),
        "verdict": verdict_for(ratio),
    }


def horizon_row(mde_now, bars_now, per_year, years):
    """What a fixed wait buys instead: the same ruler, run forward."""
    if not per_year:
        return None
    bars = float(bars_now) + float(years) * float(per_year)
    return {
        "years": float(years),
        "bars": int(round(bars)),
        "mde80_pp": round(float(mde_now) * math.sqrt(float(bars_now) / bars), 4),
    }


def price(face, lens=LENS_CNY):
    row = seat_row(face)
    if row is None:
        return {"verdict": "NO_5_SEAT_ROW",
                "vertex": "the upstream seat-MDE face has no 5-seat row; nothing to price"}
    rule = (face or {}).get("rule") or {}
    per_year = float(rule.get("per_year") or 252.0)
    block = int(rule.get("block") or 20)
    mde_now = float(row.get("select_mde80_pp"))
    bars_now = float(row.get("bars"))
    turnover = row.get("mean_turnover")
    p = float(row.get("select_p_direction"))
    excess_frac, excess_unit = as_fraction(row.get("excess_ann_pp"))
    cost_frac, cost_unit = as_fraction(row.get("cost_ann_pp"))

    rows = []
    cur = price_row(mde_now, bars_now, mde_now, per_year, block, turnover,
                    excess_frac, cost_frac, p, lens)
    cur["target_pp"] = round(mde_now, 4)
    cur["note"] = "the precision in force today"
    rows.append(cur)
    for t in TARGETS:
        rows.append(price_row(mde_now, bars_now, t, per_year, block, turnover,
                              excess_frac, cost_frac, p, lens))

    target5 = [r for r in rows if abs(r["target_pp"] - 5.0) < 1e-9]
    main = target5[0] if target5 else rows[-1]
    verdict = {
        "verdict": main["verdict"],
        "target_pp": main["target_pp"],
        "wait_years": main["wait_years"],
        "forgo_cny": main["forgo_cny"],
        "avoided_cny": main["avoided_cny"],
        "ratio": main["ratio"],
        "p_star": main["p_star"],
        "p_star_above_one": (main["p_star"] is not None and main["p_star"] > 1.0),
    }
    sentence = None
    if main["wait_years"] is not None:
        p_star = main["p_star"] or 0.0
        tail = ("等要划算，需要「这本书没有 edge」这一前提的概率高于 %.2f——而概率最多 1.00，"
                "所以这条路在任何概率下都不划算" % p_star) if p_star > 1.0 else (
            "等要划算，需要「这本书没有 edge」的概率高于 %.0f%%" % (100.0 * p_star))
        sentence = (
            "把选股腿的尺子从 %.2fpp 压到 5.0pp，要再攒 %s 根 bar = %.1f 年（样本还要长 %.2f 倍）："
            "这期间这本书会换 %.0f 次仓、账面翻 %.0f 遍。若 edge 为真，等掉的是 %.0f 元（每 100 万）；"
            "若这本书根本没有 edge，等它省下的成本只有 %.0f 元 × p=%.4f = %.0f 元——差 %.0f 倍。%s。"
            % (mde_now, format(main["wait_bars"], ","), main["wait_years"],
               (main["bars_needed"] or 0) / bars_now,
               main["rebalances_in_wait"], main["book_turns_in_wait"],
               main["forgo_cny"] or 0.0,
               (main["avoided_cny"] / p if p else 0.0), p, main["avoided_cny"] or 0.0,
               main["ratio"] or 0.0, tail)
        )
    return {
        "evidence_cutoff": (face or {}).get("evidence_cutoff"),
        "panel_last_bar": (face or {}).get("panel_last_bar"),
        "input_face": SEAT_FACE,
        "input_script": (face or {}).get("script"),
        "rule": {
            "lens_cny": lens,
            "seats": SEATS,
            "per_year": per_year,
            "block": block,
            "mean_turnover": turnover,
            "p_direction": p,
            "excess_ann_pp": row.get("excess_ann_pp"),
            "cost_ann_pp": row.get("cost_ann_pp"),
            "select_ann_pp": row.get("select_ann_pp"),
            "excess_unit_guess": excess_unit,
            "cost_unit_guess": cost_unit,
            "mde80_now_pp": mde_now,
            "bars_now": int(bars_now),
            "targets": list(TARGETS),
            "ratio_fair": RATIO_FAIR,
        },
        "rows": rows,
        "horizons": [h for h in (horizon_row(mde_now, bars_now, per_year, y)
                                 for y in HORIZONS_YEARS) if h],
        "verdict": verdict,
        "sentence": sentence,
    }


def _fmt(x, dec=1):
    if x is None:
        return "—"
    if isinstance(x, int):
        return format(x, ",")
    if float(x).is_integer() and dec <= 1:
        return format(int(x), ",")
    return ("%." + str(dec) + "f") % float(x)


def md_lines(d):
    r = d["rule"]
    v = d["verdict"]
    out = []
    out.append("# 5pp 这把尺子值多少钱：把「再攒多少年」标价（r1891）")
    out.append("")
    out.append("**结论：%s**" % v["verdict"])
    out.append("")
    if d.get("sentence"):
        out.append(d["sentence"])
        out.append("")
    out.append("上游读数全部来自 `%s`（%s 那次测量，cutoff %s）：5 座选股腿 %.4fpp、"
               "自己的 MDE80 %.4fpp、样本 %s 根 bar。" % (
                   d["input_face"], d.get("input_script"), d.get("evidence_cutoff"),
                   r["select_ann_pp"], r["mde80_now_pp"], format(r["bars_now"], ",")))
    out.append("")
    out.append("## 1. 每个目标各自要等多久、等掉多少钱")
    out.append("")
    out.append("| 目标 MDE80 | 需要 bar | 要再攒 | 年 | 其间换仓次数 | 账面翻几遍 | 等掉的 alpha（元/100万） | 省下的成本×p（元） | 倍数 | 判读 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for row in d["rows"]:
        out.append("| %.4f pp | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            row["target_pp"],
            _fmt(row["bars_needed"]), _fmt(row["wait_bars"]),
            _fmt(row["wait_years"], 3), _fmt(row["rebalances_in_wait"], 1),
            _fmt(row["book_turns_in_wait"], 1),
            _fmt(row["forgo_cny"], 0), _fmt(row["avoided_cny"], 0),
            _fmt(row["ratio"], 1), row["verdict"]))
    out.append("")
    out.append("倍数 = 等掉的 alpha ÷ (省下的成本 × p)。p 用的是这张面自己的单边假阳性率 %.4f；"
               "成本用这本书自己的成本腿 %.2fpp/年，alpha 用这本书自己的超额腿 %.2fpp/年——两个数都在同一份回执里。"
               % (r["p_direction"], r["cost_ann_pp"], r["excess_ann_pp"]))
    out.append("")
    out.append("## 2. 反过来问：等固定几年能买到多少精度")
    out.append("")
    out.append("| 再等 | 样本 bar | 那时的 MDE80 |")
    out.append("|---|---|---|")
    for h in d["horizons"]:
        out.append("| %.0f 年 | %s | %.4f pp |" % (h["years"], format(h["bars"], ","), h["mde80_pp"]))
    out.append("")
    out.append("同一把尺子往前推：等 10 年也只从 %.2fpp 走到 %.2fpp，仍够不着 5pp。"
               % (r["mde80_now_pp"], d["horizons"][-1]["mde80_pp"] if d["horizons"] else float("nan")))
    out.append("")
    out.append("## 3. 这张面说什么、不说什么")
    out.append("")
    out.append("- 说：**为 5pp 而等**这件事本身有价格，且价格可以只用这本书自己的两个已发布数字算出来。")
    out.append("- 说：p* = %.4f —— 只有当「这本书没有 edge」的概率高于它，等才划算%s。"
               % (v["p_star"] or 0.0, "（而这个数大于 1，即永远不划算）" if v.get("p_star_above_one") else ""))
    out.append("- 不说：edge 是否真实。那张面自己的读数（t、p）留在上游，本面只搬不改。")
    out.append("- 不说：等待期间这本书会变差或变好——换仓次数与翻账次数只是把「量到的是不是同一件东西」摆出来，"
               "不做判断。")
    out.append("- 边界：成本腿只算交易成本，不含冲击与税收；元/100 万是本面固定的镜头，不是建议资金规模。")
    out.append("")
    out.append("（本面自带 `--check`：从回执与上游面重新推导每一个数；上游面 cutoff 一动即判 STALE。）")
    return out


def check():
    rec = _read_json(OUT)
    if not rec:
        print("[check] STALE: no receipt at %s (face missing)" % OUT)
        return 2
    face = _read_json(SEAT_FACE)
    if not face:
        print("[check] STALE: face missing %s" % SEAT_FACE)
        return 2
    if rec.get("evidence_cutoff") != face.get("evidence_cutoff"):
        print("[check] STALE: receipt priced cutoff %r, upstream face is now %r" % (
            rec.get("evidence_cutoff"), face.get("evidence_cutoff")))
        return 3
    redo = price(face, lens=(rec.get("rule") or {}).get("lens_cny", LENS_CNY))
    fails = []
    if redo.get("verdict", {}).get("verdict") != (rec.get("verdict") or {}).get("verdict"):
        fails.append("verdict: receipt=%r rederive=%r" % (
            (rec.get("verdict") or {}).get("verdict"), redo.get("verdict", {}).get("verdict")))
    a = {r["target_pp"]: r for r in redo.get("rows") or []}
    b = {r["target_pp"]: r for r in rec.get("rows") or []}
    if set(a) != set(b):
        fails.append("target rows: receipt=%r rederive=%r" % (sorted(b), sorted(a)))
    for t in sorted(set(a) & set(b)):
        for k in ("bars_needed", "wait_bars", "wait_years", "rebalances_in_wait",
                  "book_turns_in_wait", "forgo_cny", "avoided_cny", "ratio", "p_star"):
            x, y = b[t].get(k), a[t].get(k)
            if (x is None) != (y is None):
                fails.append("%s.%s: receipt=%r rederive=%r" % (t, k, x, y))
            elif x is not None and abs(float(x) - float(y)) > max(TOL, abs(float(y)) * 1e-9):
                fails.append("%s.%s: receipt=%r rederive=%r" % (t, k, x, y))
    if (redo.get("horizons") or []) != (rec.get("horizons") or []):
        fails.append("horizons differ: receipt=%r rederive=%r" % (rec.get("horizons"), redo.get("horizons")))
    print("[check] %d target row(s) re-derived, %d mismatch" % (len(b), len(fails)))
    for f in fails:
        print("  MISMATCH " + f)
    return 0 if not fails else 1


def _fixture():
    return {
        "evidence_cutoff": "2026-11-13",
        "panel_last_bar": "2026-11-13",
        "script": "scripts/etf_book_seat_mde.py",
        "rule": {"per_year": 252.0, "block": 20},
        "rows": [
            {"n_hold": 2, "bars": 1662, "select_mde80_pp": 10.7319, "select_p_direction": 0.0355,
             "excess_ann_pp": 7.7, "cost_ann_pp": -1.4, "mean_turnover": 0.05},
            {"n_hold": 5, "bars": 1662, "select_mde80_pp": 8.7389, "select_p_direction": 0.0055,
             "excess_ann_pp": 7.7638, "cost_ann_pp": -1.3962, "mean_turnover": 0.0553},
        ],
    }


def selftest():
    fails = []

    def leg(cond, msg):
        if not cond:
            fails.append(msg)

    fx = _fixture()
    d = price(fx)
    rows = {r["target_pp"]: r for r in d["rows"]}

    # L1 the ruler's own identity: at the precision in force there is no wait
    cur = [r for r in d["rows"] if r.get("note")][0]
    leg(cur["wait_bars"] == 0 and cur["wait_years"] == 0.0, "L1 current row must cost 0, got %r" % (cur,))

    # L2 the 1/sqrt(n) scaling reproduces the published 5,077 without being told it
    leg(rows[5.0]["bars_needed"] == int(round(1662 * (8.7389 / 5.0) ** 2)),
        "L2 bars(5pp) arithmetic, got %r" % (rows[5.0]["bars_needed"],))
    leg(abs(rows[5.0]["bars_needed"] - 5077) <= 1, "L2 must land on r1764's own 5,077, got %r"
        % (rows[5.0]["bars_needed"],))

    # L3 monotone: a tighter target can never need fewer bars
    seq = [rows[t]["bars_needed"] for t in (8.0, 7.0, 6.0, 5.0)]
    leg(seq == sorted(seq) and len(set(seq)) == len(seq), "L3 targets must be strictly monotone, got %r" % (seq,))

    # L4 a target looser than today is a zero wait, never negative
    loose = price_row(8.7389, 1662, 12.0, 252.0, 20, 0.0553, 0.077638, -0.013962, 0.0055)
    leg(loose["wait_bars"] == 0 and loose["wait_years"] == 0.0, "L4 loose target wait %r" % (loose,))

    # L5 arithmetic of the wait (both the bar count and the year count are published
    #    rounded, so the leg allows one rounding step of the year figure)
    leg(abs(rows[5.0]["wait_years"] - rows[5.0]["wait_bars"] / 252.0) <= 0.001 + 1e-9,
        "L5 wait years arithmetic, got %r vs %r" % (rows[5.0]["wait_years"],
                                                    rows[5.0]["wait_bars"] / 252.0))

    # L6 compounding, not simple multiplication
    yrs = rows[5.0]["wait_years"]
    simple = LENS_CNY * 0.077638 * yrs
    compound = LENS_CNY * ((1.077638 ** yrs) - 1)
    leg(abs(rows[5.0]["forgo_cny"] - compound) <= compound * 2e-4,
        "L6 forgo must compound, got %r vs compound %.0f (simple would be %.0f)" % (
            rows[5.0]["forgo_cny"], compound, simple))
    leg(rows[5.0]["forgo_cny"] > simple, "L6 compounding must exceed the simple product")

    # L7 the cost leg's sign is not flipped into a gain
    leg(0.0 < rows[5.0]["avoided_cny"] / d["rule"]["p_direction"] < 0.5 * LENS_CNY,
        "L7 avoided must be a small positive cost, got %r" % (rows[5.0]["avoided_cny"],))
    leg(abs(rows[5.0]["avoided_cny"] - d["rule"]["p_direction"] * LENS_CNY
            * (1 - (1 - 0.013962) ** yrs)) < 1.0, "L7 avoided arithmetic")

    # L8 ratio is forgo / avoided, and p* is forgo / unweighted cost
    #    (both sides of the division are published rounded, so the tolerance is relative)
    leg(abs(rows[5.0]["ratio"] - rows[5.0]["forgo_cny"] / rows[5.0]["avoided_cny"])
        <= rows[5.0]["ratio"] * 2e-3, "L8 ratio arithmetic, got %r vs %r" % (
            rows[5.0]["ratio"], rows[5.0]["forgo_cny"] / rows[5.0]["avoided_cny"]))
    pstar = rows[5.0]["forgo_cny"] / (rows[5.0]["avoided_cny"] / d["rule"]["p_direction"])
    leg(abs(rows[5.0]["p_star"] - pstar) <= pstar * 2e-3,
        "L8 p* arithmetic, got %r vs %r" % (rows[5.0]["p_star"], pstar))

    # L9 the verdict is a function of the ratio, in three directions
    leg(verdict_for(100.0) == "WAITING_COSTS_MORE_THAN_IT_INSURES", "L9 high ratio")
    leg(verdict_for(3.0) == "THE_TARGET_IS_A_FAIR_TRADE", "L9 middle ratio")
    leg(verdict_for(0.5) == "WAITING_IS_CHEAP", "L9 low ratio")
    leg(verdict_for(None) == "NO_VERDICT", "L9 no ratio must not read as cheap")

    # L10 control arm: at p == p* the two sides tie (ratio 1.0) -> FAIR, not COSTS_MORE
    tie = price_row(8.7389, 1662, 5.0, 252.0, 20, 0.0553, 0.077638, -0.013962,
                    rows[5.0]["p_star"])
    leg(abs(tie["ratio"] - 1.0) < 1e-3, "L10 at p=p* the ratio must be 1.0, got %r" % (tie["ratio"],))
    leg(tie["verdict"] == "THE_TARGET_IS_A_FAIR_TRADE", "L10 tie is a fair trade")

    # L11 a face with no 5-seat row is answered, not priced
    none_row = price({"rows": [{"n_hold": 2}]})
    leg(none_row["verdict"] == "NO_5_SEAT_ROW", "L11 missing row -> %r" % (none_row.get("verdict"),))
    leg("sentence" not in none_row, "L11 no row must not print a sentence")

    # L12 pp/fraction conversion is stated, and the money uses the fraction
    frac, unit = as_fraction(7.7638)
    leg(abs(frac - 0.077638) < 1e-12 and unit == "pp", "L12 pp conversion, got %r %r" % (frac, unit))
    frac2, unit2 = as_fraction(0.077638)
    leg(abs(frac2 - 0.077638) < 1e-12 and unit2 == "fraction", "L12 fraction passthrough")
    leg(d["rule"]["excess_unit_guess"] == "pp", "L12 the live receipt reads pp")

    # L13 a zero-cost book cannot be priced (an infinite ratio is not a verdict)
    zero = price_row(8.7389, 1662, 5.0, 252.0, 20, 0.0553, 0.077638, 0.0, 0.0055)
    leg(zero["avoided_cny"] == 0.0 and zero["ratio"] is None and zero["verdict"] == "NO_VERDICT",
        "L13 zero cost -> %r" % (zero,))

    # L14 the horizon ruler moves the other way: more bars, smaller MDE
    hs = d["horizons"]
    leg([h["bars"] for h in hs] == sorted(h["bars"] for h in hs), "L14 horizon bars ascending")
    leg(all(hs[i]["mde80_pp"] > hs[i + 1]["mde80_pp"] for i in range(len(hs) - 1)),
        "L14 horizon MDE must shrink with bars, got %r" % (hs,))
    leg(hs[-1]["mde80_pp"] > 5.0, "L14 ten years still cannot buy 5pp (the honest answer)")

    # L15 the sentence carries the years and answers the break-even rate either way
    leg(d["sentence"] and ("%.1f 年" % rows[5.0]["wait_years"]) in d["sentence"],
        "L15 sentence must state the years")
    if (rows[5.0]["p_star"] or 0) > 1.0:
        leg(d["sentence"] and ("高于 %.2f" % rows[5.0]["p_star"]) in d["sentence"],
            "L15 sentence must state p* as a rate above one")
    else:
        leg(d["sentence"] and ("%.0f%%" % (100 * rows[5.0]["p_star"])) in d["sentence"],
            "L15 sentence must state p* in percent")

    # L16 the receipt is quoted from one face and names it
    leg(d["input_face"] == SEAT_FACE and d["evidence_cutoff"] == "2026-11-13",
        "L16 provenance")

    print("[selftest] %d/%d PASS" % (16 - len(fails), 16))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


def run():
    face = _read_json(SEAT_FACE)
    if not face:
        raise SystemExit("[run] missing %s" % SEAT_FACE)
    d = price(face)
    d["script"] = "scripts/etf_book_target_price.py"
    return d


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    argv = ["check" if a == "--check" else "selftest" if a == "--selftest" else a for a in argv]
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    t0 = time.time()
    d = run()
    d["elapsed_sec"] = round(time.time() - t0, 1)
    d["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)) + "\n")
    print(json.dumps({k: d["verdict"].get(k) for k in
                      ("verdict", "target_pp", "wait_years", "forgo_cny", "avoided_cny",
                       "ratio", "p_star", "p_star_above_one")}, ensure_ascii=False, indent=1))
    return 0 if d["verdict"].get("verdict") not in ("IDENTITY_BROKEN", "NO_5_SEAT_ROW") else 1


if __name__ == "__main__":
    sys.exit(main())
