"""What it costs to open the four-arm basis-carry book.

Round 1999 priced four basis-carry arms as one book (7.94%/yr, Sharpe 3.41) and the
capital line that exists (`idx_fut_carry_open_capital`) covers only the two hedged
arms, IC and IM.  So the newest and best headline in the shop has no answer to the
question every reader asks next: with the 1,000,000 CNY book, can I actually hold it?

This face answers only what can be answered from published numbers, and says so:

  * measured arms (IC, IM) -> each needs its published first rung, and neither fits
    inside book capital, so each is 0 lots today;
  * a FLOOR on the four-arm opening cost = the sum of the measured arms' first rungs;
  * the arms with no capital line (IF, IH) are named as unmeasured.  The floor is not
    the total, and this face refuses to print it as one (r98: a missing face must not
    be printed as a zero).

Everything borrowed carries its own generated/cutoff on the page (r1781), so a reader
can see this face is one chain step behind the numbers it quotes.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORTFOLIO = os.path.join(ROOT, "results", "idx_fut_carry_portfolio.json")
SPEC = os.path.join(ROOT, "results", "idx_fut_carry_sizing_spec.json")
OUT = os.path.join(ROOT, "results", "idx_fut_carry_portfolio_capital.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_PORTFOLIO_CAPITAL.md")

KIND = "idx_fut_carry_portfolio_capital"


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def read_inputs(portfolio, spec):
    """Pull only what the two published faces actually say."""
    arms = sorted(portfolio.get("members", {}).keys())
    accounts = spec.get("accounts", {})
    measured = {}
    for arm in arms:
        acc = accounts.get(arm)
        if not acc:
            continue
        measured[arm] = {
            "capital_cny": acc.get("capital_cny"),
            "target_pct": acc.get("target_pct"),
            "first_rung_cny": acc.get("first_executable_capital_cny"),
            "admissible_lots": acc.get("admissible_lots"),
            "budget_cny_at_target": acc.get("budget_cny_at_target"),
            "per_lot_vol_cny": acc.get("per_lot_vol_cny_hedged"),
        }
    unmeasured = [a for a in arms if a not in measured]
    return {
        "arms": arms,
        "measured": measured,
        "unmeasured": unmeasured,
        "spec_generated": spec.get("generated"),
        "spec_cutoff": spec.get("evidence_cutoff"),
        "portfolio_generated": portfolio.get("generated"),
        "portfolio_cutoff": portfolio.get("evidence_cutoff"),
        "portfolio_headline": {
            "ann_pct": (portfolio.get("equal_weight_full") or {}).get("ann_pct"),
            "sharpe": (portfolio.get("equal_weight_full") or {}).get("sharpe"),
            "vol_pct": (portfolio.get("equal_weight_full") or {}).get("vol_pct"),
            "mdd_pct": (portfolio.get("equal_weight_full") or {}).get("mdd_pct"),
        },
        "verdict_line": portfolio.get("verdict"),
    }


def build(inputs):
    """Arithmetic only: sums of published rungs, and the lot counts those imply."""
    measured = inputs["measured"]
    unmeasured = inputs["unmeasured"]
    book_capital = sorted({m["capital_cny"] for m in measured.values() if m["capital_cny"]})
    if len(book_capital) != 1:
        state, why = "blocked", "measured arms disagree about the book's capital; cannot state a floor"
        book = None
    else:
        book = book_capital[0]
        state, why = "ok", None

    floor_cny = None
    if state == "ok" and measured and all(m["first_rung_cny"] for m in measured.values()):
        floor_cny = round(sum(m["first_rung_cny"] for m in measured.values()), 2)

    per_arm = {}
    for arm, m in sorted(measured.items()):
        gap = None
        if m["first_rung_cny"] is not None and book is not None:
            gap = round(m["first_rung_cny"] - book, 2)
        per_arm[arm] = {
            "first_rung_cny": m["first_rung_cny"],
            "capital_cny": m["capital_cny"],
            "admissible_lots_at_book_capital": m["admissible_lots"],
            "gap_to_first_lot_cny": gap,
            "target_pct": m["target_pct"],
        }

    checks = {}
    checks["C1_measured_arms_cannot_even_hold_one_lot"] = bool(
        per_arm and all(v["admissible_lots_at_book_capital"] == 0 for v in per_arm.values())
    )
    checks["C2_every_measured_arm_has_a_rung"] = bool(
        per_arm and all(v["first_rung_cny"] for v in per_arm.values())
    )
    checks["C3_floor_is_not_printed_as_the_total"] = bool(unmeasured) and floor_cny is not None
    checks["C4_floor_exceeds_book_capital"] = bool(floor_cny is not None and book and floor_cny > book)

    if state != "ok":
        verdict = "BLOCKED"
    elif checks["C1_measured_arms_cannot_even_hold_one_lot"] and checks["C4_floor_exceeds_book_capital"]:
        verdict = "FOUR_ARM_BOOK_NOT_OPENABLE_AT_BOOK_CAPITAL"
    elif all(v["admissible_lots_at_book_capital"] and v["admissible_lots_at_book_capital"] > 0
             for v in per_arm.values()):
        verdict = "FOUR_ARM_BOOK_OPENABLE_ON_MEASURED_ARMS"
    else:
        verdict = "MIXED_MEASURED_ARMS"

    headline = inputs["portfolio_headline"]
    sentence = (
        "The four-arm book is priced at {ann}%/yr, Sharpe {sr} on {vol}% vol, and it cannot be "
        "opened on the {book} CNY book: {arms_short}. Holding one lot of every measured arm "
        "needs at least {floor} CNY, so this book is a number about a larger account until the "
        "capital arrives. {unmeasured_note}"
    ).format(
        ann=headline.get("ann_pct"),
        sr=headline.get("sharpe"),
        vol=headline.get("vol_pct"),
        book=_fmt(book),
        arms_short="; ".join(
            "{0} is {1} CNY short of its first lot (target {2}%)".format(
                a, _fmt(v["gap_to_first_lot_cny"]), v["target_pct"])
            for a, v in sorted(per_arm.items())
        ) or "no arm had a rung to compare",
        floor=_fmt(floor_cny),
        unmeasured_note=(
            "That floor covers only the arms with a capital line ({0}); {1} have none, so the "
            "true opening cost is higher and this face will not guess it.".format(
                ", ".join(sorted(per_arm)) or "none",
                ", ".join(unmeasured) if unmeasured else "no other arms")
        ),
    )

    return {
        "kind": KIND,
        "state": state,
        "state_why": why,
        "evidence_cutoff": inputs["portfolio_cutoff"] or inputs["spec_cutoff"],
        "book_capital_cny": book,
        "measured_arms": per_arm,
        "unmeasured_arms": unmeasured,
        "floor_to_open_measured_arms_cny": floor_cny,
        "floor_multiple_of_book": (round(floor_cny / book, 4) if floor_cny and book else None),
        "headline_it_is_not_yet": headline,
        "upstream": {
            "portfolio_face": "results/idx_fut_carry_portfolio.json",
            "portfolio_generated": inputs["portfolio_generated"],
            "portfolio_cutoff": inputs["portfolio_cutoff"],
            "portfolio_verdict": inputs["verdict_line"],
            "capital_face": "results/idx_fut_carry_sizing_spec.json",
            "capital_generated": inputs["spec_generated"],
            "capital_cutoff": inputs["spec_cutoff"],
        },
        "checks": checks,
        "verdict": verdict,
        "sentence": sentence,
        "next_work": (
            "Give IF and IH the same capital line the hedged arms have (per-lot vol at the "
            "8% target): only then can the four-arm opening cost be stated instead of floored."
            if unmeasured else "all arms measured"
        ),
    }


def _fmt(v):
    return "{:,.0f}".format(v) if isinstance(v, (int, float)) else "n/a"


def write_doc(face):
    u = face["upstream"]
    rows = "\n".join(
        "| {0} | {1} | {2} | {3} | {4} |".format(
            arm,
            _fmt(v["first_rung_cny"]),
            _fmt(v["capital_cny"]),
            v["admissible_lots_at_book_capital"],
            _fmt(v["gap_to_first_lot_cny"]),
        )
        for arm, v in sorted(face["measured_arms"].items())
    )
    lines = [
        "# 开这本书要多少钱——四臂基差 carry 组合的资金线",
        "",
        "generated {0} | cutoff {1} | verdict **{2}**".format(
            face.get("generated", ""), face.get("evidence_cutoff", ""), face["verdict"]),
        "",
        face["sentence"],
        "",
        "## 已测臂（有资金线的两臂）",
        "",
        "| 臂 | 开一手所需（元） | 本书资金（元） | 本书资金下可下单手数 | 差额（元） |",
        "|---|---|---|---|---|",
        rows,
        "",
        "组合面出处：`{0}`（generated {1}，cutoff {2}，判词 {3}）。".format(
            u["portfolio_face"], u["portfolio_generated"], u["portfolio_cutoff"],
            u["portfolio_verdict"]),
        "资金面出处：`{0}`（generated {1}，cutoff {2}）。".format(
            u["capital_face"], u["capital_generated"], u["capital_cutoff"]),
        "上面两行是各自面自带的时点，本节不重算它们——本面比它们晚一趟。",
        "",
        "## 未测臂（名字要点出来）",
        "",
        "无资金线的臂：**{0}**。所以「开仓下限 {1} 元」只是已测臂之和，不是这本书的总成本；"
        "缺面不许印成 0。".format(
            ", ".join(face["unmeasured_arms"]) or "无",
            _fmt(face["floor_to_open_measured_arms_cny"])),
        "",
        "## 下一步",
        "",
        face["next_work"],
        "",
        "## 账",
        "",
        "```",
    ]
    for k, v in sorted(face["checks"].items()):
        lines.append("{0}: {1}".format(k, v))
    lines.append("```")
    lines.append("")
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def run():
    face = build(read_inputs(_load(PORTFOLIO), _load(SPEC)))
    import datetime
    face["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    _dump(OUT, face)
    write_doc(face)
    print("{0} | {1} | floor {2} vs book {3}".format(
        face["verdict"], face["state"], _fmt(face["floor_to_open_measured_arms_cny"]),
        _fmt(face["book_capital_cny"])))
    return 0 if face["state"] == "ok" else 2


def selftest():
    """A check that can only ever say 'no' proves nothing (r1850/r1935)."""
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    portfolio = {"members": {"IC": {}, "IM": {}, "IF": {}, "IH": {}},
                 "equal_weight_full": {"ann_pct": 7.938, "sharpe": 3.412, "vol_pct": 2.246, "mdd_pct": -1.657},
                 "evidence_cutoff": "2026-11-20", "generated": "g", "verdict": "FOUR_ARMS_DO_DISPERSIFY"}
    spec_shut = {"accounts": {
        "IC": {"capital_cny": 1000000, "target_pct": 8.0, "first_executable_capital_cny": 1124479,
               "admissible_lots": 0, "budget_cny_at_target": 80000, "per_lot_vol_cny_hedged": 89958.32},
        "IM": {"capital_cny": 1000000, "target_pct": 8.0, "first_executable_capital_cny": 1152596,
               "admissible_lots": 0, "budget_cny_at_target": 80000, "per_lot_vol_cny_hedged": 92207.68}},
        "generated": "g2", "evidence_cutoff": "2026-11-20"}

    f = build(read_inputs(portfolio, spec_shut))
    leg("shut arms -> NOT_OPENABLE", f["verdict"] == "FOUR_ARM_BOOK_NOT_OPENABLE_AT_BOOK_CAPITAL")
    leg("floor is the sum of rungs", f["floor_to_open_measured_arms_cny"] == 2277075.0)
    leg("unmeasured arms named", f["unmeasured_arms"] == ["IF", "IH"])
    leg("floor not printed as total", f["checks"]["C3_floor_is_not_printed_as_the_total"] is True)
    leg("sentence says which arms are missing", "IF, IH" in f["sentence"])

    # positive control: make the account big enough and the verdict must flip
    spec_open = json.loads(json.dumps(spec_shut))
    for acc in spec_open["accounts"].values():
        acc["capital_cny"] = 5000000
        acc["admissible_lots"] = 3
    f2 = build(read_inputs(portfolio, spec_open))
    leg("rich account -> OPENABLE", f2["verdict"] == "FOUR_ARM_BOOK_OPENABLE_ON_MEASURED_ARMS")
    leg("rich account -> no floor > book check", f2["checks"]["C4_floor_exceeds_book_capital"] is False)

    # disagreement between arms must block, not average
    spec_bad = json.loads(json.dumps(spec_shut))
    spec_bad["accounts"]["IM"]["capital_cny"] = 2000000
    leg("disagreeing capital -> BLOCKED", build(read_inputs(portfolio, spec_bad))["verdict"] == "BLOCKED")

    # a missing rung must not be silently summed as zero
    spec_gap = json.loads(json.dumps(spec_shut))
    spec_gap["accounts"]["IM"]["first_executable_capital_cny"] = None
    f4 = build(read_inputs(portfolio, spec_gap))
    leg("missing rung -> floor not fabricated", f4["floor_to_open_measured_arms_cny"] is None)

    for name, ok in legs:
        print(("PASS " if ok else "FAIL ") + name)
    print("{0}/{1} legs".format(sum(1 for _, ok in legs if ok), len(legs)))
    return 0 if all(ok for _, ok in legs) else 3


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    if cmd == "show":
        print(json.dumps(_load(OUT), ensure_ascii=False, indent=1))
        return 0
    print("usage: idx_fut_carry_portfolio_capital.py [run|selftest|show]")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
