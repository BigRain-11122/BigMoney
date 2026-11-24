"""Where does the next 129,566 CNY go -- and what does the same 1,129,566 CNY earn in each book?

Three roads are already priced by their own faces, but never on one ruler for the capital this
account would actually have to commit:

  * the ETF composite book   (results/etf_nobond_vt.json, arm nobond_vt08, 8% vol target, no bonds)
  * one IC carry lot         (results/idx_fut_carry_open_capital.json, results/idx_fut_roll_cost.json,
                              results/idx_fut_carry_lend_breakeven.json)
  * cash                     (results/etf_book_cash_rate_flip.json, rate_now_pct)

The reading this face adds is the *marginal* one.  The ETF book is the richer book (11.11% a year
against 6.4-6.6% of notional for the carry lot), but at 1,000,000 CNY it already sits past its own
capacity line on 56 of the last 60 sessions, while the carry lot is capacity-rich and needs one
lumpy 12.96% step to open.  So the next yuan cannot earn the book average at any size, and the
step that would make it earn something new pays less than the book it leaves.

Read-only over six published faces: nothing here re-derives a backtest or re-decides a ticket.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = "results/capital_marginal_road.json"
PAGE = "research/CAPITAL_MARGINAL_ROAD.md"
MARK_BEGIN = "<!-- MARGINAL-ROAD:BEGIN -->"
MARK_END = "<!-- MARGINAL-ROAD:END -->"

INPUTS = [
    ("etf_book", "results/etf_nobond_vt.json"),
    ("etf_capacity", "results/etf_book_capacity_edge.json"),
    ("etf_ticket", "results/etf_book_ticket_floor.json"),
    ("carry_open", "results/idx_fut_carry_open_capital.json"),
    ("carry_notional", "results/idx_fut_carry_lend_breakeven.json"),
    ("carry_cost", "results/idx_fut_roll_cost.json"),
    ("cash_rate", "results/etf_book_cash_rate_flip.json"),
]

ETF_ARM = "nobond_vt08"
PRODUCT = "IC"


def _path(rel: str) -> str:
    return os.path.join(ROOT, rel)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_inputs() -> dict:
    out = {}
    for key, rel in INPUTS:
        with io.open(_path(rel), "rb") as fh:
            raw = fh.read()
        out[key] = {"path": rel, "sha256": _sha(raw), "json": json.loads(raw.decode("utf-8"))}
    return out


def inputs_digest(inputs: dict) -> str:
    parts = ["%s:%s" % (inputs[k]["path"], inputs[k]["sha256"]) for k in sorted(inputs)]
    return _sha("\n".join(parts).encode("utf-8"))


# --------------------------------------------------------------------------- pricing

def classify(carry_cny: float, etf_cny: float, cash_cny: float, over_line_cny: float) -> str:
    """The verdict is decided by two numbers, never by taste -- and every branch is reachable."""
    if max(carry_cny, etf_cny) <= cash_cny:
        return "CASH_MATCHES_THE_RICHER_BOOK"
    if carry_cny > etf_cny:
        return "THE_STEP_PAYS_MORE_THAN_THE_BOOK_IT_LEAVES"
    if over_line_cny > 0:
        return "THE_STEP_IS_PRICED_WORSE_AND_THE_RICHER_BOOK_HAS_NO_ROOM"
    return "THE_STEP_IS_PRICED_WORSE_BUT_THE_RICHER_BOOK_HAS_ROOM"


def price_roads(etf_ann_pct, etf_vol_pct, carry_pp_upper, carry_pp_tape, notional_cny,
                funding_cny, gap_cny, cash_pct, capital_at_line_cny, lens_cny,
                pass_sessions, n_sessions) -> dict:
    etf_ann = etf_ann_pct / 100.0
    carry_cny = carry_pp_upper / 100.0 * notional_cny
    carry_cny_tape = carry_pp_tape / 100.0 * notional_cny
    cash = cash_pct / 100.0
    capital = funding_cny  # the capital at which the carry road is actually reachable

    etf_cny = capital * etf_ann
    cash_cny = capital * cash
    over_line_cny = round(lens_cny + gap_cny - capital_at_line_cny, 2)

    return {
        "verdict": classify(carry_cny, etf_cny, cash_cny, over_line_cny),
        "books": {
            "etf": {"capital_cny": capital, "ann_pct": etf_ann_pct, "vol_pct": etf_vol_pct,
                    "income_cny": round(etf_cny, 2)},
            "carry": {"product": PRODUCT, "lots": 1, "capital_cny": funding_cny,
                      "notional_cny": notional_cny,
                      "carry_pp_upper": carry_pp_upper, "carry_pp_tape": carry_pp_tape,
                      "income_cny_upper": round(carry_cny, 2),
                      "income_cny_tape": round(carry_cny_tape, 2),
                      "return_on_capital_pct_upper": round(100.0 * carry_cny / funding_cny, 3),
                      "return_on_capital_pct_tape": round(100.0 * carry_cny_tape / funding_cny, 3)},
            "cash": {"capital_cny": capital, "rate_pct": cash_pct, "income_cny": round(cash_cny, 2)},
        },
        "gap": {
            "carry_minus_etf_cny": round(carry_cny - etf_cny, 2),
            "carry_tape_minus_etf_cny": round(carry_cny_tape - etf_cny, 2),
            "carry_minus_cash_cny": round(carry_cny - cash_cny, 2),
        },
        "capacity": {
            "lens_cny": lens_cny, "step_cny": gap_cny,
            "capital_after_step_cny": round(lens_cny + gap_cny, 2),
            "etf_capital_at_line_today_cny": capital_at_line_cny,
            "over_line_after_step_cny": over_line_cny,
            "etf_sessions_inside_line": pass_sessions,
            "etf_sessions_measured": n_sessions,
            "etf_pass_rate_pct": round(100.0 * pass_sessions / n_sessions, 2),
        },
        "marginal": {
            "step_cny": gap_cny,
            "etf_earn_cny": round(gap_cny * etf_ann, 2),
            "cash_earn_cny": round(gap_cny * cash, 2),
            "carry_note": "the step does not buy a fractional lot: it converts a 0-lot ticket into "
                          "1 lot, so its price is the whole gap, not a rate applied to 129,566",
        },
    }


# --------------------------------------------------------------------------- derive

def derive_facts(inputs: dict) -> dict:
    etf = inputs["etf_book"]["json"]
    cap = inputs["etf_capacity"]["json"]
    ticket = inputs["etf_ticket"]["json"]
    carry = inputs["carry_open"]["json"]
    nota = inputs["carry_notional"]["json"]
    cost = inputs["carry_cost"]["json"]
    cash = inputs["cash_rate"]["json"]

    arm = [r for r in etf["runs"] if r["label"] == ETF_ARM][0]
    ic = carry["accounts"][PRODUCT]
    tape = cost["products"][PRODUCT]

    priced = price_roads(
        etf_ann_pct=round(arm["cagr"] * 100.0, 2),
        etf_vol_pct=round(arm["vol"] * 100.0, 2),
        carry_pp_upper=float(nota["accounts"][PRODUCT]["long_carry_pp"]),
        carry_pp_tape=float(tape["net_ann_pct"]["at_measured_median"]),
        notional_cny=float(nota["accounts"][PRODUCT]["lot_notional_cny"]),
        funding_cny=float(ic["funding"]["first_rung_cny"]),
        gap_cny=float(ic["funding"]["gap_cny"]),
        cash_pct=float(cash["facts"]["rate_now_pct"]),
        capital_at_line_cny=float(cap["summary"]["capital_where_at_line_today_cny"]),
        lens_cny=float(ticket["capital_cny"]),
        pass_sessions=int(cap["summary"]["n_passes"]),
        n_sessions=int(cap["summary"]["n_sessions"]),
    )

    facts = {
        "artifact": "capital_marginal_road",
        "verdict": priced["verdict"],
        "lens_cny": float(ticket["capital_cny"]),
        "books": priced["books"],
        "gap": priced["gap"],
        "capacity": priced["capacity"],
        "marginal": priced["marginal"],
        "etf_detail": {
            "arm": ETF_ARM,
            "ann_pct": round(arm["cagr"] * 100.0, 2),
            "vol_pct": round(arm["vol"] * 100.0, 2),
            "sharpe": arm["sharpe"],
            "maxdd_pct": round(arm["maxdd"] * 100.0, 2),
            "worst_year_pct": round(arm["worst_year"] * 100.0, 2),
            "neg_years": arm["neg_years"],
            "turnover_per_year": arm["turnover"],
            "one_lot_floor_cny": float(ticket["floor"]["min_capital_cny"]),
            "capital_multiple_vs_floor": float(ticket["capital_multiple_vs_floor"]),
        },
        "carry_detail": {
            "product": PRODUCT,
            "roll_pp_per_year": round(float(tape["rolls_per_year"]) * float(tape["measured"]["median_bp"]) / 100.0, 3),
            "carry_gross_pp": float(tape["carry_gross_ann_pct"]),
            "carry_net_tape_pp": float(tape["net_ann_pct"]["at_measured_median"]),
            "carry_pp_basis_face": float(nota["accounts"][PRODUCT]["long_carry_pp"]),
            "funding_cny": float(ic["funding"]["first_rung_cny"]),
            "gap_cny": float(ic["funding"]["gap_cny"]),
            "gap_pct_of_capital": float(ic["funding"]["gap_pct_of_capital"]),
            "per_lot_vol_cny": float(ic["per_lot_vol_cny_hedged"]),
        },
        "face_provenance": {inputs[k]["path"]: {
            "generated": (inputs[k]["json"].get("generated") or inputs[k]["json"].get("published") or "-"),
            "evidence_cutoff": inputs[k]["json"].get("evidence_cutoff"),
            "sha256": inputs[k]["sha256"][:16]} for k in sorted(inputs)},
        "evidence_cutoff": min(str(inputs[k]["json"].get("evidence_cutoff") or "9999")
                               for k in ("etf_book", "carry_open", "carry_cost")),
        "caveats": [
            "The ETF book's 11.11% is net of its own 10bp-per-side cost assumption but assumes the "
            "capacity line does not bind; the capacity face says at 1,000,000 CNY that assumption "
            "holds on 4 of the last 60 sessions, so the marginal yuan is priced at a rate the book "
            "cannot currently execute.",
            "The carry lot's income is carry on one contract notional (1,211,600 CNY), not a return "
            "on margin; the return-on-capital line divides it by the 8%-vol-budget funding rung.",
            "Two independent carry readings are printed: the tape face's net-of-measured-roll "
            "figure (6.361pp) and the basis face's control-drift-adjusted figure (6.599pp). The "
            "verdict is decided on the upper one, i.e. the reading most favourable to the carry road.",
            "The 1% ADV capacity line is this repo's own criterion, not an exchange rule: it says "
            "how often this capital fits, not what it costs to push.",
            "The step is all-or-nothing: one lot is the smallest whole unit, so the marginal table "
            "shows what 129,566 earns in the two continuous books, not a pro-rata carry return.",
        ],
    }
    facts["facts_digest"] = facts_digest(facts)
    return facts


def facts_digest(facts: dict) -> str:
    body = {k: v for k, v in facts.items()
            if k not in ("facts_digest", "generated", "elapsed_sec", "inputs_digest",
                         "face_provenance")}
    return _sha(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8"))[:32]


# --------------------------------------------------------------------------- page

def render_page(facts: dict, inputs: dict) -> str:
    b, g, c, m = facts["books"], facts["gap"], facts["capacity"], facts["marginal"]
    d, cd = facts["etf_detail"], facts["carry_detail"]
    lines = [
        MARK_BEGIN,
        "generated %s  ·  evidence_cutoff %s  ·  read-only over %d published faces"
        % ("%(generated)s", facts["evidence_cutoff"], len(inputs)),
        "",
        "## Same %s CNY, three roads" % format(b["etf"]["capital_cny"], ",.0f"),
        "",
        "| road | what it earns in a year | on capital | note |",
        "|---|---|---|---|",
        "| ETF composite book (%s) | **%s** | %.2f%% | one-lot floor %s, %sx |"
        % (d["arm"], format(b["etf"]["income_cny"], ",.0f"), b["etf"]["ann_pct"],
           format(d["one_lot_floor_cny"], ",.2f"), d["capital_multiple_vs_floor"]),
        "| one %s carry lot (upper reading %spp) | **%s** | %.3f%% | tape reading %spp = %s |"
        % (cd["product"], cd["carry_pp_basis_face"], format(b["carry"]["income_cny_upper"], ",.0f"),
           b["carry"]["return_on_capital_pct_upper"], cd["carry_net_tape_pp"],
           format(b["carry"]["income_cny_tape"], ",.0f")),
        "| cash (idle slot rate %s%%) | **%s** | %.4f%% | the floor everyone forgets |"
        % (b["cash"]["rate_pct"], format(b["cash"]["income_cny"], ",.0f"), b["cash"]["rate_pct"]),
        "",
        "Carry minus ETF on the same capital: **%s CNY a year** (tape reading: %s)."
        % (format(g["carry_minus_etf_cny"], ",.0f"), format(g["carry_tape_minus_etf_cny"], ",.0f")),
        "",
        "## The next %s CNY" % format(m["step_cny"], ",.0f"),
        "",
        "| where it goes | what it earns | why it is or is not available |",
        "|---|---|---|",
        "| ETF book | %s a year | the capacity line sits at %s today; after the step the book is %s "
        "over it, and this capital fits on %d of the last %d sessions (%.2f%%) |"
        % (format(m["etf_earn_cny"], ",.0f"), format(c["etf_capital_at_line_today_cny"], ",.2f"),
           format(c["over_line_after_step_cny"], ",.2f"), c["etf_sessions_inside_line"],
           c["etf_sessions_measured"], c["etf_pass_rate_pct"]),
        "| %s carry lot | 0 until %s CNY, then %s a year on the whole rung | whole lots only: the step "
        "does not buy a fraction |"
        % (cd["product"], format(cd["funding_cny"], ",.0f"), format(b["carry"]["income_cny_upper"], ",.0f")),
        "| cash | %s a year | always available |" % format(m["cash_earn_cny"], ",.0f"),
        "",
        "## Verdict",
        "",
        "**%s**" % facts["verdict"],
        "",
        "%s" % sentence(facts),
        "",
        "## What this face does not say",
        "",
    ]
    for cav in facts["caveats"]:
        lines.append("* " + cav)
    lines.append("")
    lines.append(MARK_END)
    return "\n".join(lines)


def sentence(facts: dict) -> str:
    b, g = facts["books"], facts["gap"]
    f = lambda v: format(v, ",.0f")  # noqa: E731 - keeps the sentence readable
    return ("On the same %s CNY the ETF book prints %s a year against %s for one %s carry lot "
            "and %s for cash, so the step that unlocks the lot pays %s a year less than the book "
            "it leaves -- and the book it leaves is already %s CNY past its own capacity line on "
            "%d of the last %d sessions, which is the real reason the account has to look for a "
            "third road rather than a bigger one."
            % (f(b["etf"]["capital_cny"]), f(b["etf"]["income_cny"]),
               f(b["carry"]["income_cny_upper"]), facts["carry_detail"]["product"],
               f(b["cash"]["income_cny"]), f(-g["carry_minus_etf_cny"]),
               f(facts["capacity"]["over_line_after_step_cny"]),
               facts["capacity"]["etf_sessions_inside_line"],
               facts["capacity"]["etf_sessions_measured"]))


def page_block(text: str) -> str:
    i, j = text.find(MARK_BEGIN), text.find(MARK_END)
    if i < 0 or j < 0:
        return ""
    return text[i:j + len(MARK_END)]


# --------------------------------------------------------------------------- modes

def run() -> int:
    inputs = load_inputs()
    facts = derive_facts(inputs)
    facts["generated"] = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
    facts["inputs_digest"] = inputs_digest(inputs)

    with io.open(_path(FACE), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(facts, ensure_ascii=False, indent=1) + "\n")

    page_path = _path(PAGE)
    old = io.open(page_path, encoding="utf-8").read() if os.path.exists(page_path) else ""
    block = render_page(facts, inputs).replace("%(generated)s", facts["generated"])
    if MARK_BEGIN in old and MARK_END in old:
        i, j = old.index(MARK_BEGIN), old.index(MARK_END) + len(MARK_END)
        new = old[:i] + block + old[j:]
    else:
        new = "# Capital: where the next yuan goes\n\n" + block + "\n"
    with io.open(page_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)

    print("MARGINAL-ROAD %s" % facts["verdict"])
    print("  same capital %.0f: etf %.0f | carry %.0f (tape %.0f) | cash %.0f"
          % (facts["books"]["etf"]["capital_cny"], facts["books"]["etf"]["income_cny"],
             facts["books"]["carry"]["income_cny_upper"], facts["books"]["carry"]["income_cny_tape"],
             facts["books"]["cash"]["income_cny"]))
    print("  step %.2f: over the ETF capacity line by %.2f, inside on %d/%d sessions"
          % (facts["marginal"]["step_cny"], facts["capacity"]["over_line_after_step_cny"],
             facts["capacity"]["etf_sessions_inside_line"], facts["capacity"]["etf_sessions_measured"]))
    print("  -> %s   %s" % (FACE, PAGE))
    return 0


def _leaf_diffs(a, b, prefix="", out=None):
    """Name the leaves that disagree, so a red never says only 'books'."""
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k in b:
                _leaf_diffs(a[k], b[k], ("%s.%s" % (prefix, k)) if prefix else k, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(prefix + "[len]")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                _leaf_diffs(x, y, "%s[%d]" % (prefix, i), out)
    elif a != b:
        out.append(prefix)
    return out


def check() -> int:
    inputs = load_inputs()
    fresh = derive_facts(inputs)
    if not os.path.exists(_path(FACE)):
        print("STALE face missing: %s" % FACE)
        return 3
    published = json.loads(io.open(_path(FACE), encoding="utf-8").read())
    if facts_digest(published) != published.get("facts_digest"):
        print("CHECK FAILED the published face no longer hashes to its own facts_digest: %s"
              % ", ".join(_leaf_diffs(published, fresh)[:6] or ["digest only"]))
        return 3
    if published.get("inputs_digest") != inputs_digest(inputs):
        moved = []
        prov = published.get("face_provenance") or {}
        for key in sorted(inputs):
            spec = inputs[key]["path"]
            old = (prov.get(spec) or {}).get("sha256")
            if old is None or old != inputs[key]["sha256"][:16]:
                moved.append(spec)
        print("STALE inputs moved: %s" % ", ".join(moved))
        return 3
    if published.get("facts_digest") != fresh["facts_digest"]:
        diffs = [p for p in _leaf_diffs(published, fresh)
                 if not p.startswith(("generated", "inputs_digest", "face_provenance"))]
        print("CHECK FAILED facts disagree with the same inputs: %s" % (", ".join(diffs[:8]) or "digest only"))
        return 3
    if not os.path.exists(_path(PAGE)):
        print("STALE page missing: %s" % PAGE)
        return 3
    block = page_block(io.open(_path(PAGE), encoding="utf-8").read())
    if not block:
        print("CHECK FAILED page block markers unreadable in %s" % PAGE)
        return 3
    want = render_page(published, inputs).replace("%(generated)s", published.get("generated") or "")
    if block != want:
        print("CHECK FAILED page block differs from the face it publishes")
        return 3
    print("CHECK OK %s (verdict=%s, cutoff=%s)" % (FACE, published["verdict"], published["evidence_cutoff"]))
    return 0


def selftest() -> int:
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    base = price_roads(11.11, 10.51, 6.599, 6.361, 1211600.0, 1129565.88, 129565.88, 1.7708,
                       1043800.91, 1000000.0, 4, 60)
    # 1 arithmetic: carry income is carry-on-notional, not carry-on-capital
    leg("carry income = pp x notional", abs(base["books"]["carry"]["income_cny_upper"] - 79953.48) < 0.05)
    # 2 the tape reading is strictly the conservative one
    leg("tape reading < basis reading", base["books"]["carry"]["income_cny_tape"] < base["books"]["carry"]["income_cny_upper"])
    # 3 return on capital divides by the funding rung
    leg("return on capital", abs(base["books"]["carry"]["return_on_capital_pct_upper"] - 7.078) < 0.002)
    # 4 ranking is strict, not a tie
    leg("etf > carry > cash", base["books"]["etf"]["income_cny"] > base["books"]["carry"]["income_cny_upper"] > base["books"]["cash"]["income_cny"])
    # 5 over-line arithmetic
    leg("over line = lens + step - line", abs(base["capacity"]["over_line_after_step_cny"] - 85764.97) < 0.02)
    # 6 the verdict branch that fires today
    leg("verdict today", base["verdict"] == "THE_STEP_IS_PRICED_WORSE_AND_THE_RICHER_BOOK_HAS_NO_ROOM")
    # 7 a step that pays more flips the verdict
    rich = price_roads(2.0, 10.51, 6.599, 6.361, 1211600.0, 1129565.88, 129565.88, 1.7708,
                       1043800.91, 1000000.0, 4, 60)
    leg("verdict flips when the step pays more", rich["verdict"] == "THE_STEP_PAYS_MORE_THAN_THE_BOOK_IT_LEAVES")
    # 8 room in the richer book clears the capacity clause
    roomy = price_roads(11.11, 10.51, 6.599, 6.361, 1211600.0, 1129565.88, 129565.88, 1.7708,
                        2000000.0, 1000000.0, 60, 60)
    leg("verdict names room when the richer book has it", roomy["verdict"] == "THE_STEP_IS_PRICED_WORSE_BUT_THE_RICHER_BOOK_HAS_ROOM")
    # 9 cash beating both books is its own branch (and it is reachable)
    flat = price_roads(1.0, 10.51, 0.5, 0.5, 1211600.0, 1129565.88, 129565.88, 1.7708,
                       1043800.91, 1000000.0, 4, 60)
    leg("cash branch", flat["verdict"] == "CASH_MATCHES_THE_RICHER_BOOK")
    # 10 digest moves with one byte of one input
    inputs = load_inputs()
    d0 = inputs_digest(inputs)
    tampered = {k: dict(v) for k, v in inputs.items()}
    tampered["carry_cost"]["sha256"] = "0" * 64
    leg("inputs digest moves with one byte", inputs_digest(tampered) != d0)
    # 11 facts digest ignores runtime metadata but not numbers
    f0 = derive_facts(inputs)
    f1 = dict(f0)
    f1["generated"] = "1999-01-01T00:00:00+08:00"
    leg("facts digest ignores generated", facts_digest(f1) == f0["facts_digest"])
    f2 = json.loads(json.dumps(f0))
    f2["books"]["carry"]["income_cny_upper"] += 1.0
    leg("facts digest catches one number", facts_digest(f2) != f0["facts_digest"])
    # 12 the page block carries its own provenance and the verdict
    text = render_page(f0, inputs).replace("%(generated)s", "2026-01-01T00:00:00+08:00")
    blk = page_block(text)
    leg("page prints verdict and provenance",
        f0["verdict"] in blk and "generated 2026-01-01" in blk and f0["evidence_cutoff"] in blk)
    # 13 a page block that loses the sentence is detectable
    leg("page block round-trip", page_block(text.replace(MARK_END, "x")) == "")

    ok = sum(1 for _, passed in legs if passed)
    for name, passed in legs:
        print("  %s %s" % ("OK  " if passed else "FAIL", name))
    print("SELFTEST %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="recompute and compare with the published face/page")
    g.add_argument("--selftest", action="store_true", help="offline leg tests")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
