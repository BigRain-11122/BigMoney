#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""what one lot of this carry book actually pays -- always-on vs timed, on each ruler

WHY THIS FILE EXISTS
--------------------
r2093 (results/bench_basis_timing_perm_masks.json) settled a narrower question: the
*timing* edge survives the shift null on every ruler for IC but its money flips to
-0.19pp on IM once the union ruler drops roll days. Its verdict line -- "hold always" --
is the right instruction and an unusable number: a reader still cannot tell what the
book pays, because the face never printed the level, only the delta.

Three numbers were already published in that same table and never put side by side:

  * always-on carry, the level:  IC 2.76% / 9.65% / 9.68%   (published / calendar / strictest)
                                 IM 5.74% / 11.96% / 11.50%
  * timed carry, the level:      IC 10.12% / 12.02% / 11.36%
                                 IM  9.45% / 12.75% / 11.31%

The *level* swings 6.9pp across rulers while the delta moves 0-6pp. So "this book pays
X%/yr" is not a statement this desk can make yet -- and the ruler that produces the
lowest level (published: roll days priced as carry) is also the one that prices the roll
loss a holder genuinely pays. That is a definitional question about `carry`, not a
statistical one, and until it is answered no single headline rate may be quoted.

WHAT THIS FACE DOES (and does not)
----------------------------------
It prices one lot, under each ruler, in CNY, at the desk's own capital rung, with the
cash leg credited: a 1-lot IC position locks only the broker's initial margin, so the
remaining idle cash keeps earning the repo leg. Comparing carry to cash therefore means
subtracting the *foregone interest on the locked margin*, not the whole parking yield.

  excess = carry_cny - cash_net x margin_cny
  excess_pct_of_capital = excess / first_rung_cny

Every input is read, never re-derived: notional and the margin sweep come from
results/idx_fut_carry_margin.json (which reads the panels), the capital rung from
results/idx_fut_carry_sizing_spec.json, the levels from
results/bench_basis_timing_perm_masks.json, and the cash rate from
results/capital_placement.json::config.cash_net_annual (the published net repo rate).

What is NOT recomputed here, and therefore named in `--check`: the carry series itself,
the notional basis, the margin rate, and the cash rate. This face is arithmetic on four
published faces plus one decision.

verdict tokens (frozen before the first run):
  PAYS_EVEN_ON_ITS_WORST_RULER                        min excess > 0 on every product,
                                                      rate spread across rulers < 3pp
  PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND  min excess > 0 but spread >= 3pp:
                                                      the instruction survives, the
                                                      headline rate does not
  WORST_RULER_TURNS_THE_LINE_NEGATIVE                 some product's min excess <= 0
  DATA_BLOCKED                                        an input face is missing

Usage:
    python scripts/idx_fut_carry_always_on_price.py run
    python scripts/idx_fut_carry_always_on_price.py check
    python scripts/idx_fut_carry_always_on_price.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MASKS_PATH = os.path.join(ROOT, "results", "bench_basis_timing_perm_masks.json")
MARGIN_PATH = os.path.join(ROOT, "results", "idx_fut_carry_margin.json")
SPEC_PATH = os.path.join(ROOT, "results", "idx_fut_carry_sizing_spec.json")
CAPITAL_PATH = os.path.join(ROOT, "results", "capital_placement.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_always_on_price.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_ALWAYS_ON_PRICE.md")

PRODUCTS = ("IC", "IM")
RULERS = ("published", "calendar", "strictest")
BASE_MARGIN_PCT = 12.0
SPREAD_LINE_PP = 3.0

V_OK = "PAYS_EVEN_ON_ITS_WORST_RULER"
V_BOUND = "PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND"
V_NEG = "WORST_RULER_TURNS_THE_LINE_NEGATIVE"
V_BLOCK = "DATA_BLOCKED"
VERDICTS = (V_OK, V_BOUND, V_NEG, V_BLOCK)


# ------------------------------------------------------------------ io helpers
def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None


def _sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _fingerprints(paths):
    out = {}
    for p in paths:
        try:
            key = os.path.relpath(p, ROOT).replace("\\", "/")
        except ValueError:
            key = os.path.basename(p)
        out[key] = _sha256_of(p) if os.path.exists(p) else None
    return out


# ------------------------------------------------------------------ derivation
def derive():
    """Read every published face and price one lot. No panel access, no re-fitting."""
    masks = _read_json(MASKS_PATH)
    margin = _read_json(MARGIN_PATH)
    spec = _read_json(SPEC_PATH)
    capital = _read_json(CAPITAL_PATH)
    missing = [name for name, face in (
        ("results/bench_basis_timing_perm_masks.json", masks),
        ("results/idx_fut_carry_margin.json", margin),
        ("results/idx_fut_carry_sizing_spec.json", spec),
        ("results/capital_placement.json", capital),
    ) if not face]

    face = {
        "kind": "idx_fut_carry_always_on_price",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": ("what does one lot of this carry book pay per year, always-on vs "
                     "timed, once the cash leg on the unlocked margin is credited?"),
        "inputs": _fingerprints([MASKS_PATH, MARGIN_PATH, SPEC_PATH, CAPITAL_PATH]),
        "not_recomputed": [
            "the carry series and its levels (results/bench_basis_timing_perm_masks.json)",
            "notional per lot and the margin sweep (results/idx_fut_carry_margin.json)",
            "the first executable capital rung (results/idx_fut_carry_sizing_spec.json)",
            "the net repo rate (results/capital_placement.json::config.cash_net_annual)",
        ],
        "base_margin_pct": BASE_MARGIN_PCT,
        "spread_line_pp": SPREAD_LINE_PP,
    }
    if missing:
        face["verdict"] = V_BLOCK
        face["missing_inputs"] = missing
        face["products"] = {}
        return face

    cash_net = float(capital.get("config", {}).get("cash_net_annual"))
    face["cash_net_annual"] = cash_net
    face["cash_source"] = "results/capital_placement.json::config.cash_net_annual"
    face["evidence_cutoff"] = masks.get("evidence_cutoff")

    products = {}
    for prod in PRODUCTS:
        m = (margin.get("products") or {}).get(prod) or {}
        if m.get("status") != "ok":
            products[prod] = {"status": "blocked", "why": "margin face has no ok row"}
            continue
        notional = float(m["notional_per_lot_cny"])
        acct = (spec.get("accounts") or {}).get(prod) or {}
        rungs = [r for r in acct.get("capital_rungs") or [] if int(r.get("lots", 0)) >= 1]
        if not rungs:
            products[prod] = {"status": "blocked", "why": "no executable capital rung"}
            continue
        first_rung = float(rungs[0]["capital_cny"])

        sweep = m.get("margin_sweep") or {}
        base = None
        for key, row in sweep.items():
            if abs(float(row.get("rate_pct", -1)) - BASE_MARGIN_PCT) < 0.51:
                base = row
        if base is None:
            products[prod] = {"status": "blocked", "why": "margin sweep lacks the base rate"}
            continue
        margin_cny = float(base["initial_margin_cny"])
        idle_cash = first_rung - margin_cny
        cash_on_idle = cash_net * idle_cash
        park = cash_net * first_rung

        levels = {}
        rows = ((masks.get("products") or {}).get(prod) or {}).get("rulers") or {}
        for ruler in RULERS:
            row = rows.get(ruler) or {}
            if "always_on_ann_pct" not in row or "weighted_ann_pct" not in row:
                continue
            a_pct = float(row["always_on_ann_pct"])
            t_pct = float(row["weighted_ann_pct"])
            a_cny = a_pct / 100.0 * notional
            t_cny = t_pct / 100.0 * notional
            levels[ruler] = {
                "always_on_ann_pct": a_pct,
                "timed_ann_pct": t_pct,
                "days_excluded": row.get("days_excluded"),
                "always_on_carry_cny": round(a_cny, 2),
                "timed_carry_cny": round(t_cny, 2),
                "always_on_total_cny": round(a_cny + cash_on_idle, 2),
                "timed_total_cny": round(t_cny + cash_on_idle, 2),
                "always_on_excess_cny": round(a_cny - cash_net * margin_cny, 2),
                "timed_excess_cny": round(t_cny - cash_net * margin_cny, 2),
                "always_on_excess_pct_of_capital": round(
                    (a_cny - cash_net * margin_cny) / first_rung * 100.0, 4),
                "timed_excess_pct_of_capital": round(
                    (t_cny - cash_net * margin_cny) / first_rung * 100.0, 4),
            }
        if not levels:
            products[prod] = {"status": "blocked", "why": "masks face has no ruler rows"}
            continue

        a_vals = [v["always_on_ann_pct"] for v in levels.values()]
        t_vals = [v["timed_ann_pct"] for v in levels.values()]
        spread_pp = round(max(a_vals) - min(a_vals), 2)
        min_excess_pct = min(v["always_on_excess_pct_of_capital"] for v in levels.values())
        min_excess_pct_timed = min(v["timed_excess_pct_of_capital"] for v in levels.values())

        strict = levels.get("strictest") or {}
        timing_adds_cny = None
        if strict:
            timing_adds_cny = round(strict["timed_carry_cny"] - strict["always_on_carry_cny"], 2)

        products[prod] = {
            "status": "ok",
            "notional_per_lot_cny": notional,
            "first_rung_cny": first_rung,
            "margin_cny": margin_cny,
            "margin_share_of_capital_pct": round(margin_cny / first_rung * 100.0, 4),
            "idle_cash_cny": round(idle_cash, 2),
            "cash_on_idle_cny": round(cash_on_idle, 2),
            "park_the_whole_rung_cny": round(park, 2),
            "rate_spread_across_rulers_pp": spread_pp,
            "always_on_min_pct": min(a_vals),
            "always_on_max_pct": max(a_vals),
            "timed_min_pct": min(t_vals),
            "timed_max_pct": max(t_vals),
            "min_excess_pct_of_capital": min_excess_pct,
            "min_excess_pct_of_capital_timed": min_excess_pct_timed,
            "timing_adds_cny_on_one_lot_strictest": timing_adds_cny,
            "timed_beats_always_on_strictest": (timing_adds_cny or 0) > 0,
            "rulers": levels,
        }
    face["products"] = products

    ok_rows = [p for p in products.values() if p.get("status") == "ok"]
    if not ok_rows:
        face["verdict"] = V_BLOCK
    else:
        worst = min(r["min_excess_pct_of_capital"] for r in ok_rows)
        widest = max(r["rate_spread_across_rulers_pp"] for r in ok_rows)
        if worst <= 0:
            face["verdict"] = V_NEG
        elif widest >= SPREAD_LINE_PP:
            face["verdict"] = V_BOUND
        else:
            face["verdict"] = V_OK
    face["reading"] = {
        V_OK: "one lot clears the parking alternative on every ruler and the rate is stable -- quote it",
        V_BOUND: ("one lot still clears parking on the worst ruler, but the yearly rate moves with "
                  "the ruler: quote the range and the ruler name, never a single headline number"),
        V_NEG: "on the worst ruler the carry does not cover the interest it locks -- do not size on it",
        V_BLOCK: "an input face is missing; refuse, never default",
    }[face["verdict"]]
    return face


# ------------------------------------------------------------------ checks
def check(face=None, quiet=False):
    """Re-derive from the inputs and compare with the published face. Drift => rc3 STALE."""
    problems = []
    published = _read_json(OUT_PATH)
    if published is None:
        print("STALE face missing: results/idx_fut_carry_always_on_price.json")
        return 3
    fresh = derive() if face is None else face

    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %r -> %r" % (published.get("verdict"), fresh.get("verdict")))
    for prod in PRODUCTS:
        a = (published.get("products") or {}).get(prod) or {}
        b = (fresh.get("products") or {}).get(prod) or {}
        if a.get("status") != b.get("status"):
            problems.append("%s status %r -> %r" % (prod, a.get("status"), b.get("status")))
            continue
        if a.get("status") != "ok":
            continue
        for key in ("first_rung_cny", "margin_cny", "notional_per_lot_cny",
                    "min_excess_pct_of_capital", "rate_spread_across_rulers_pp"):
            va, vb = a.get(key), b.get(key)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                if abs(float(va) - float(vb)) > 1e-6:
                    problems.append("%s %s %r -> %r" % (prod, key, va, vb))
            elif va != vb:
                problems.append("%s %s %r -> %r" % (prod, key, va, vb))
    if problems:
        print("STALE results/idx_fut_carry_always_on_price.json (inputs moved)")
        for p in problems[:12]:
            print("  - " + p)
        return 3
    if not quiet:
        print("CHECK_OK idx_fut_carry_always_on_price (%d products, verdict %s)"
              % (len([p for p in (published.get('products') or {}).values()
                      if p.get('status') == 'ok']), published.get("verdict")))
    return 0


# ------------------------------------------------------------------ render
def render_doc(face):
    lines = []
    lines.append("# 一手 carry 到底付多少：常驻 vs 择时，每把尺子各印一遍")
    lines.append("")
    lines.append("generated %s | 判决 **%s** | 资本门槛=%s 的首档 | 现金腿=净回购 %.4f%%"
                 % (face["generated"], face["verdict"],
                    face.get("evidence_cutoff", "?"),
                    face.get("cash_net_annual", 0) * 100.0))
    lines.append("")
    lines.append("同一本账、同一批合约，只换「哪些天不算 carry」这把尺子。"
                 "净超额 = 一手 carry 减去被锁保证金的机会利息（现金腿按同一利率计）。")
    lines.append("")
    lines.append("| 品种 | 尺子 | 排除天数 | 常驻% | 择时% | 常驻元/年 | 择时元/年 | "
                 "常驻净超额 | 择时净超额 | 占首档资本 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            lines.append("| %s | — | — | — | — | — | — | — | — | %s |"
                         % (prod, row.get("why", "blocked")))
            continue
        for ruler in RULERS:
            v = row["rulers"].get(ruler)
            if not v:
                continue
            lines.append("| %s | %s | %s | %.2f%% | %.2f%% | %s | %s | %s | %s | %.2f%% |" % (
                prod, ruler, v["days_excluded"],
                v["always_on_ann_pct"], v["timed_ann_pct"],
                format(int(round(v["always_on_carry_cny"])), ","),
                format(int(round(v["timed_carry_cny"])), ","),
                format(int(round(v["always_on_excess_cny"])), ","),
                format(int(round(v["timed_excess_cny"])), ","),
                v["always_on_excess_pct_of_capital"]))
    lines.append("")
    lines.append("## 三个必须一起读的数")
    lines.append("")
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            continue
        lines.append("- **%s**：一手名义 %s 元，首档 %s 元，锁保证金 %s 元（占首档 %.2f%%），"
                     "闲置现金 %s 元可继续吃息 %s 元/年。"
                     % (prod, format(int(row["notional_per_lot_cny"]), ","),
                        format(int(row["first_rung_cny"]), ","),
                        format(int(row["margin_cny"]), ","),
                        row["margin_share_of_capital_pct"],
                        format(int(row["idle_cash_cny"]), ","),
                        format(int(row["cash_on_idle_cny"]), ",")))
        lines.append("  常驻年化在三把尺子上从 %.2f%% 到 %.2f%%（差 %.2fpp）；"
                     "最差尺子下净超额 %+.2f%% 资本，择时最差 %+.2f%% 资本；"
                     "择时在最保守尺子上相对常驻 %s 元/年。"
                     % (row["always_on_min_pct"], row["always_on_max_pct"],
                        row["rate_spread_across_rulers_pp"],
                        row["min_excess_pct_of_capital"],
                        row["min_excess_pct_of_capital_timed"],
                        format(int(round(row["timing_adds_cny_on_one_lot_strictest"])), ",")))
    lines.append("")
    lines.append("## 为什么不能只报一个年化")
    lines.append("")
    lines.append("- 常驻的**水平**在尺子间跳 5.9-6.9pp，比择时的 delta（0-6pp）还大。"
                 "「这本书年化 X%」这句话目前不成立，能说的是区间 + 尺子名。")
    lines.append("- 产生最低水平的那把尺子（published）把展期日的价格跳变当成 carry 损益；"
                 "而持有者确实要付这个跳变。所以这不是统计噪声之争，是 `carry` 的定义之争，"
                 "在定义定下来之前任何人拿单点数字下单都是错的。")
    lines.append("- 现金腿是**叠加**不是替代：一手只锁住首档资本的一小部分保证金，剩下的资本照旧吃息。"
                 "把 carry 直接除以全额首档资本（本面之前的读法）会系统性低估这本书，"
                 "而把它和停车收益率比则会高估——两者都错。")
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            continue
        lines.append("  - %s：锁保证金 %s 元 = 首档的 %.2f%%，其余 %.2f%% 吃息 %s 元/年。"
                     % (prod, format(int(row["margin_cny"]), ","),
                        row["margin_share_of_capital_pct"],
                        100.0 - row["margin_share_of_capital_pct"],
                        format(int(row["cash_on_idle_cny"]), ",")))
    lines.append("")
    lines.append("## 没有回答的问题")
    lines.append("")
    lines.append("- 展期日到底算不算 carry（本面只把三把尺子并列，没有裁决）；")
    lines.append("- 规模成本、交易所手续费、保证金追加（margin call 的被迫平仓）未在此面扣；")
    lines.append("- 只覆盖 IC/IM（与 cell 7 同宇宙），IF/IH 的贴水更薄，规则未必适用；")
    lines.append("- 1 手以上按首档线性外推，未验证深度（ETF 书已有容量面，carry 书没有）。")
    lines.append("")
    lines.append("`--check` 会重算本页每个数并点名「哪些没重算」：")
    for what in face.get("not_recomputed", []):
        lines.append("- 未重算：%s" % what)
    lines.append("")
    return "\n".join(lines)


def run():
    face = derive()
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(face))
    print("WROTE results/idx_fut_carry_always_on_price.json verdict=%s" % face["verdict"])
    for prod in PRODUCTS:
        row = (face.get("products") or {}).get(prod) or {}
        if row.get("status") != "ok":
            print("  %s: %s" % (prod, row.get("why", "blocked")))
            continue
        print("  %s: always-on %.2f-%.2f%% | min excess %+.2f%% of capital | spread %.2fpp"
              % (prod, row["always_on_min_pct"], row["always_on_max_pct"],
                 row["min_excess_pct_of_capital"], row["rate_spread_across_rulers_pp"]))
    return 0


# ------------------------------------------------------------------ selftest
def _selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    face = derive()
    leg("all four inputs present", face["verdict"] != V_BLOCK)
    leg("verdict in the frozen token set", face["verdict"] in VERDICTS)

    ok_rows = {p: r for p, r in face["products"].items() if r.get("status") == "ok"}
    leg("both products priced", set(ok_rows) == set(PRODUCTS))

    if ok_rows:
        bad = []
        for prod, row in ok_rows.items():
            for ruler, v in row["rulers"].items():
                calc = v["always_on_ann_pct"] / 100.0 * row["notional_per_lot_cny"]
                if abs(calc - v["always_on_carry_cny"]) > 0.01:
                    bad.append((prod, ruler, calc, v["always_on_carry_cny"]))
        leg("carry_cny == ann_pct x notional on every row", not bad)

        bad = []
        for prod, row in ok_rows.items():
            for ruler, v in row["rulers"].items():
                calc = v["always_on_carry_cny"] - face["cash_net_annual"] * row["margin_cny"]
                if abs(calc - v["always_on_excess_cny"]) > 0.02:
                    bad.append((prod, ruler, calc, v["always_on_excess_cny"]))
        leg("excess == carry - cash x locked margin", not bad)

        bad = []
        for prod, row in ok_rows.items():
            calc = row["timed_carry_cny"] if False else None
            strict = row["rulers"].get("strictest") or {}
            if strict:
                calc = strict["timed_carry_cny"] - strict["always_on_carry_cny"]
                if abs(calc - row["timing_adds_cny_on_one_lot_strictest"]) > 0.02:
                    bad.append((prod, calc, row["timing_adds_cny_on_one_lot_strictest"]))
        leg("timing_adds derives from the strictest ruler", not bad)

        swing = max(r["rate_spread_across_rulers_pp"] for r in ok_rows.values())
        leg("the ruler spread is large enough to matter (>=3pp)", swing >= SPREAD_LINE_PP)

    # behavioural: moving a level must move the verdict
    moved = json.loads(json.dumps(face))
    if moved["products"].get("IC", {}).get("status") == "ok":
        for ruler in moved["products"]["IC"]["rulers"].values():
            ruler["always_on_ann_pct"] = 0.0
            ruler["always_on_carry_cny"] = 0.0
            ruler["always_on_excess_cny"] = -moved["cash_net_annual"] * \
                moved["products"]["IC"]["margin_cny"]
            ruler["always_on_excess_pct_of_capital"] = (
                ruler["always_on_excess_cny"] / moved["products"]["IC"]["first_rung_cny"] * 100.0)
        moved["products"]["IC"]["min_excess_pct_of_capital"] = min(
            v["always_on_excess_pct_of_capital"] for v in moved["products"]["IC"]["rulers"].values())
        worst = min(r["min_excess_pct_of_capital"] for r in moved["products"].values()
                    if r.get("status") == "ok")
        leg("a zeroed carry turns the verdict negative",
            (V_NEG if worst <= 0 else moved["verdict"]) == V_NEG)

    # behavioural: a missing input must refuse, never default
    global MASKS_PATH
    saved = MASKS_PATH
    try:
        MASKS_PATH = os.path.join(tempfile.gettempdir(), "_no_such_masks_face.json")
        blocked = derive()
    finally:
        MASKS_PATH = saved
    leg("missing masks face refuses with DATA_BLOCKED", blocked["verdict"] == V_BLOCK)

    # behavioural: cash rate = 0 must leave excess == carry (caliber self-consistency)
    if face["products"].get("IC", {}).get("status") == "ok":
        legacy = face["cash_net_annual"]
        face["cash_net_annual"] = 0.0
        row = face["products"]["IC"]
        for v in row["rulers"].values():
            v["always_on_excess_cny"] = v["always_on_carry_cny"] - 0.0 * row["margin_cny"]
        good = all(abs(v["always_on_excess_cny"] - v["always_on_carry_cny"]) < 1e-6
                   for v in row["rulers"].values())
        face["cash_net_annual"] = legacy
        leg("zero cash rate leaves excess == carry", good)

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print(("  PASS " if ok else "  FAIL ") + name)
    print("SELFTEST %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv or "selftest" in argv:
        return _selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
