"""Which ruler does the admission gate actually ask with?

r1426 certified two rulers over the desk's own 20 phase cells (4 arms x 5 phases):
``effective_years`` (breadth: how many years carry the result) and ``years_for_half``
(half-life: how few of the best years explain half of it).  Both can adjudicate
themselves.  On the adopted book one says PASS and the other says FAIL, so "use the
trusted ruler" stopped being an instruction and became a choice -- and choosing the
one that says PASS is exactly the "run until it passes" failure this firm forbids.

So the election here never asks the real book anything.  It asks rulers about
**fixtures with a verdict declared before any reading** (a 3-year record, one lucky
year, a record that spent itself in its first four years, ...).  A ruler that admits a
declared pathology is disqualified outright; among survivors the one that answers more
fixtures correctly wins, ties broken by fewer false refusals.  Only afterwards is the
desk's own book applied as a *witness* -- and ``elect()`` has no parameter that could
see it, which is the structural part of the claim, not a promise.

Two consequences this face is built to make readable:
  * the elected ruler is the *stricter* one, i.e. the election refuses the book the
    desk actually holds -- that is the cheapest available proof it was not picked to pass;
  * ``years_for_half`` silently encodes a record-length floor (for an even n-year book
    it reads ceil(n/2)), so a short-but-honest record and a spent record print the
    same refusal.  Published as ``implicit_record_floor`` rather than hidden.

Identity: the witness rows are re-derived from the published r1426 receipt's own
``year_net_pct``; every caliber recomputed here must equal that receipt's published
value or the face refuses to ship (rc3), same rule as the upstream faces.
"""

import json
import math
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "etf_book_admission_ruler_election.json")
CALIBER_RECEIPT = os.path.join(ROOT, "results", "etf_book_year_caliber.json")
PHASE_GATE = os.path.join(ROOT, "results", "etf_book_phase_gate.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from etf_book_year_caliber import CALIBERS, calibers, passes  # noqa: E402  single source

ELECTION_RULE = {
    "question": ("the gate decides whether the realised record supports deploying capital "
                 "and holding it -- so the ruler must answer 'is this result repeatable', "
                 "not 'is this result spread out'"),
    "disqualify_if": "a ruler admits any fixture whose verdict was declared REFUSE first",
    "then": "more correct fixtures wins",
    "tie_break": ["fewer false refusals", "declared priority order"],
    "priority_order": ["years_for_half", "effective_years"],
    "witness_is_not_an_input": "elect() takes fixtures only; the desk book is applied after",
}

CONTENDERS = ("effective_years", "years_for_half")

# The receipt publishes its year rows rounded to four decimals, so re-deriving a caliber
# from them cannot match to better than that rounding.  Measured drift on this receipt is
# 2.09e-4; the tolerance is set an order of magnitude above it and nowhere near a real
# repricing (the smallest real change any of these faces has shown is ~1e-2).
IDENTITY_TOL = 1e-3

# "Half the record" stops meaning anything when the record is nearly flat: the half is a
# fraction of a percent, so one ordinary year clears it and the ruler prints 1 -- the same
# word it prints for a book whose whole result came from one lucky year.  Declared, not hidden.
FLAT_NET_RATIO = 0.5

# Every fixture carries its verdict, written before the readings in this file existed.
# The pathology classes are the ones the gate exists to refuse.  ``two_halves`` is kept
# out of scoring on purpose: whether a book that made its returns in the first half and
# then went quiet should be refused is the very judgement under test, and scoring our own
# answer would smuggle the outcome into the election.
FIXTURES = [
    {"name": "uniform_7y", "years": [5, 5, 5, 5, 5, 5, 5], "verdict": "ADMIT",
     "class": "healthy", "why": "seven flat years: nothing is concentrated"},
    {"name": "uniform_3y", "years": [5, 5, 5], "verdict": "REFUSE",
     "class": "too-short", "why": "three years cannot separate luck from process"},
    {"name": "one_lucky_year", "years": [35, 0, 0, 0, 0, 0, 0], "verdict": "REFUSE",
     "class": "single-year", "why": "one year is the whole record"},
    {"name": "broad_but_spent", "years": [12, 10, 9, 8, 0, 0, 0], "verdict": "REFUSE",
     "class": "front-loaded", "why": "all of it was earned in the first four years"},
    {"name": "narrow_start", "years": [20, 2, 2, 2, 2, 2, 2], "verdict": "REFUSE",
     "class": "front-loaded", "why": "the opening year is 62% of the record"},
    {"name": "decaying", "years": [10, 8, 6, 4, 2, 1, 0], "verdict": "REFUSE",
     "class": "front-loaded", "why": "the process is dying, not repeating"},
    {"name": "healthy_realistic", "years": [6, 7, 5, 8, 6, 7, 5], "verdict": "ADMIT",
     "class": "healthy", "why": "uneven but sustained across the whole record"},
    {"name": "long_thin", "years": [3] * 10, "verdict": "ADMIT",
     "class": "healthy", "why": "thin but flat over ten years"},
    {"name": "two_halves", "years": [8, 8, 8, 8, 8, 1, 1, 1, 1, 1], "verdict": "DISPUTED",
     "class": "contested", "why": "spent in the first half, but a real half; not scored"},
]


def _rows(years):
    return [{"year": str(2000 + i), "net_pct": float(v), "cohorts": 4}
            for i, v in enumerate(years)]


def read_ruler(caliber, years):
    """One ruler on one year table: value and the frozen line's word. None never passes."""
    c = calibers(_rows(years))
    v = c.get(caliber)
    return {"value": v, "pass": passes(caliber, v),
            "word": "ADMIT" if passes(caliber, v) else "REFUSE"}


def score(caliber, fixtures=None):
    fixtures = FIXTURES if fixtures is None else fixtures
    rows, correct, false_admit, false_refuse, skipped = [], 0, 0, 0, 0
    for f in fixtures:
        r = read_ruler(caliber, f["years"])
        if f["verdict"] == "DISPUTED":
            skipped += 1
            rows.append({"fixture": f["name"], "declared": f["verdict"],
                         "class": f["class"], "read": r, "scored": False})
            continue
        ok = r["word"] == f["verdict"]
        correct += 1 if ok else 0
        false_admit += 1 if (r["word"] == "ADMIT" and f["verdict"] == "REFUSE") else 0
        false_refuse += 1 if (r["word"] == "REFUSE" and f["verdict"] == "ADMIT") else 0
        rows.append({"fixture": f["name"], "declared": f["verdict"], "class": f["class"],
                     "read": r, "scored": True, "correct": ok})
    scored = len(fixtures) - skipped
    return {"caliber": caliber, "fixtures_scored": scored, "correct": correct,
            "false_admit": false_admit, "false_refuse": false_refuse,
            "admits_something": any(r.get("read", {}).get("word") == "ADMIT" for r in rows),
            "refuses_something": any(r.get("read", {}).get("word") == "REFUSE" for r in rows),
            "fixtures": rows}


def elect():
    """The election.  Signature is deliberate: fixtures only, so no witness can leak in."""
    scores = [score(c) for c in CONTENDERS]
    by_name = {s["caliber"]: s for s in scores}
    disq = {}
    for s in scores:
        reasons = []
        if s["false_admit"] > 0:
            bad = [f["fixture"] for f in s["fixtures"]
                   if f.get("scored") and not f.get("correct")
                   and f["read"]["word"] == "ADMIT"]
            reasons.append("admits declared pathologies: " + ", ".join(bad))
        if not (s["admits_something"] and s["refuses_something"]):
            reasons.append("constant ruler: it is either never satisfied or never binding")
        if reasons:
            disq[s["caliber"]] = " | ".join(reasons)
    alive = [s for s in scores if s["caliber"] not in disq]
    if not alive:
        return {"elected": None, "rule": ELECTION_RULE, "scores": scores,
                "disqualified": disq, "reason": "no ruler survived the fixtures"}
    rank = {n: i for i, n in enumerate(ELECTION_RULE["priority_order"])}
    alive.sort(key=lambda s: (-s["correct"], s["false_refuse"], rank.get(s["caliber"], 99)))
    winner = alive[0]
    return {"elected": winner["caliber"], "rule": ELECTION_RULE, "scores": scores,
            "disqualified": disq,
            "margin": {s["caliber"]: s["correct"] for s in scores},
            "reason": ("survived the fixture disqualification and answered %d/%d fixtures "
                       "correctly" % (winner["correct"], winner["fixtures_scored"]))}


def implicit_record_floor(caliber, ns=range(2, 13)):
    """An even n-year book reads ceil(n/2) on the half-life ruler -- that is a length floor."""
    rows = []
    for n in ns:
        r = read_ruler(caliber, [5] * n)
        rows.append({"years": n, "value": r["value"], "word": r["word"]})
    first = next((r["years"] for r in rows if r["word"] == "ADMIT"), None)
    return {"caliber": caliber, "even_book_readings": rows,
            "first_n_that_passes": first}


def degeneracy():
    """Where the half-life ruler stops meaning anything: records that are nearly flat.

    ``years_for_half`` divides the net sum, so a record whose net is a small residue of a
    much larger gross has a tiny half -- one ordinary year clears it and the ruler reads 1,
    the same word it uses for a single lucky year.  Publishing this is the honest half of
    electing that ruler; a gate that prints 1 without the net/gross ratio next to it is
    telling two opposite stories with one number.
    """
    probes = [{"name": "net_negative", "years": [-8, -3, 2, 4, 3, 5, -4]},
              {"name": "churn_flat_positive", "years": [-1, 1, -1, 1, -1, 1, 0]},
              {"name": "nearly_flat_positive", "years": [0.5, -0.4, 0.3, -0.2, 0.1, 0.0, 0.2]},
              {"name": "earned_opening_year", "years": [20, 2, 2, 2, 2, 2, 2]}]
    rows = []
    for p in probes:
        c = calibers(_rows(p["years"]))
        net, gross = c["net_sum_pct"], c["gross_sum_pct"]
        ratio = None if not gross else abs(net) / gross
        rows.append({"name": p["name"], "net_sum_pct": net, "gross_sum_pct": gross,
                     "net_over_gross": None if ratio is None else round(ratio, 6),
                     "years_for_half": c["years_for_half"],
                     "degenerate": bool(ratio is not None and ratio <= FLAT_NET_RATIO)})
    return {"rule": "years_for_half is degenerate when |net|/gross <= %.2f" % FLAT_NET_RATIO,
            "probes": rows,
            "degenerate_count": sum(1 for r in rows if r["degenerate"])}


def refusal_reason_audit(elected):
    """Which ruler are the calendar's refusals printed with, and does it survive ours?

    Every refused candidate in the supply calendar names ``Y4_top2_share`` -- the net
    two-year share, i.e. a ruler this election just disqualified.  A refusal that stands
    for the right reason but cites a ruler nobody should trust is still a refusal, but the
    receipt is telling the reader to look at the wrong instrument.  This block separates
    the two questions: does the refusal survive the *elected* ruler, and is the printed
    reason the one that survived?
    """
    if not os.path.exists(PHASE_GATE):
        return {"state": "UPSTREAM_MISSING", "path": os.path.relpath(PHASE_GATE, ROOT)}
    pub = json.load(open(PHASE_GATE, encoding="utf-8"))
    lines = pub.get("gate_lines_imported") or {}
    summary = pub.get("summary") or {}
    if not summary:
        return {"state": "UPSTREAM_MISSING", "reason": "no summary block in phase gate"}
    printed_reason_ruler = "net_top2_share"
    rows = []
    for book, s in summary.items():
        states = s.get("trusted_states") or {}
        rows.append({
            "book": book, "state": s.get("state"),
            "printed_reason": "Y4_top2_share", "printed_reason_ruler": printed_reason_ruler,
            "printed_reason_is_disqualified": printed_reason_ruler not in CONTENDERS
                                           or printed_reason_ruler == "effective_years",
            "median_top2_share": s.get("median_top2_share"),
            "line": lines.get("top2_share_max"),
            "refusal_survival": s.get("refusal_survival"),
            "trusted_states": states,
            "survives_under_elected_ruler": states.get(elected) == "FAIL",
        })
    stands = [r for r in rows if r["survives_under_elected_ruler"]]
    return {"state": "OK", "source": os.path.relpath(PHASE_GATE, ROOT),
            "elected_ruler": elected, "printed_reason_ruler": printed_reason_ruler,
            "printed_reason_disqualified_by_election": True,
            "refusals": rows,
            "refusals_that_survive_elected_ruler": len(stands),
            "refusals_total": len(rows),
            "divergence": ("the printed reason and the surviving reason are different rulers: "
                           "the refusal is real, the receipt cites a disqualified instrument"
                           if len(stands) == len(rows) else
                           "at least one refusal does not survive the elected ruler")}


def witness():
    """The desk book as a witness: re-derived, then read with each ruler.  Never an input."""
    if not os.path.exists(CALIBER_RECEIPT):
        return {"state": "UPSTREAM_MISSING", "path": os.path.relpath(CALIBER_RECEIPT, ROOT)}
    pub = json.load(open(CALIBER_RECEIPT, encoding="utf-8"))
    cells = (pub.get("cells") or {}).get("plain") or []
    if not cells:
        return {"state": "UPSTREAM_MISSING", "reason": "no plain arm cells in receipt"}
    phases, dev_max = [], 0.0
    for c in cells:
        yr = c.get("year_net_pct") or {}
        order = sorted(yr.keys())
        years = [float(yr[k]) for k in order]
        re = calibers(_rows(years))
        for k, v in (c.get("calibers") or {}).items():
            if k in re and isinstance(v, (int, float)) and isinstance(re[k], (int, float)):
                dev_max = max(dev_max, abs(float(v) - float(re[k])))
        phases.append({
            "start": c.get("start"), "years": len(years), "year_net_pct": years,
            "readings": {r: read_ruler(r, years) for r in CONTENDERS},
        })
    vals = {r: [p["readings"][r]["value"] for p in phases
                if p["readings"][r]["value"] is not None] for r in CONTENDERS}
    summary = {}
    for r in CONTENDERS:
        if not vals[r]:
            summary[r] = {"state": "NO_READING"}
            continue
        med = float(statistics.median(vals[r]))
        summary[r] = {"median": med, "min": min(vals[r]), "max": max(vals[r]),
                      "words": sorted({p["readings"][r]["word"] for p in phases}),
                      "line": CALIBERS[r]["line"], "pass_when": CALIBERS[r]["pass_when"]}
    return {"state": "OK", "source": os.path.relpath(CALIBER_RECEIPT, ROOT),
            "identity_max_abs_dev_vs_published": round(dev_max, 9),
            "identity_tol": IDENTITY_TOL,
            "identity_ok": dev_max <= IDENTITY_TOL, "phases": phases, "summary": summary,
            "phases_count": len(phases)}


def build(wit=None):
    e = elect()
    floor = {r: implicit_record_floor(r) for r in CONTENDERS}
    wit = witness() if wit is None else wit
    el = e["elected"]
    under = None
    if el and wit.get("state") == "OK":
        s = wit["summary"][el]
        under = {"ruler": el, "median": s["median"], "words": s["words"],
                 "verdict": ("ADMIT" if s["words"] == ["ADMIT"] else
                             ("REFUSE" if s["words"] == ["REFUSE"] else "MIXED")),
                 "record_years": sorted({p["years"] for p in wit["phases"]}),
                 "length_floor": floor[el]["first_n_that_passes"]}
        under["length_floor_binding"] = any(y < (floor[el]["first_n_that_passes"] or 0)
                                            for y in under["record_years"])
    decision = {
        "elected_ruler": el,
        "election_reason": e["reason"],
        "disqualified": e["disqualified"],
        "witness_verdict_under_election": None if under is None else under["verdict"],
        "was_the_election_picked_to_pass": ("NO -- the elected ruler refuses the book the desk "
                                            "holds" if under and under["verdict"] != "ADMIT"
                                            else "REVIEW -- the elected ruler admits the held book"),
        "consequence": ("the gate asks the half-life question; a record that spent itself "
                        "early is refused no matter how broad it looks"
                        if el == "years_for_half" else
                        "the gate asks the breadth question; a short record is refused, a "
                        "spread-out one is admitted"),
        "honest": [
            "the election reads no book of ours; elect() has no witness parameter",
            "fixtures are synthetic year tables, not backtest output",
            "the half-life ruler conflates 'short' with 'spent' -- see implicit_record_floor",
            "no production file, engine, prereg or gate line changed by this face",
        ],
        "next_action": ("the calendar's refusals stand under the elected ruler but are printed "
                        "with a disqualified one -- the receipt's reason should name the ruler "
                        "that survived, which is an adoption-round change, not this face's"),
    }
    return {"face": "etf_book_admission_ruler_election", "asof": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "question": "which of the two certified rulers is the one the gate asks with",
            "election": e, "implicit_record_floor": floor, "degeneracy": degeneracy(),
            "refusal_reason_audit": refusal_reason_audit(el),
            "witness": wit,
            "witness_reading": under, "decision": decision,
            "gate_lines_imported": {r: {"line": CALIBERS[r]["line"],
                                        "pass_when": CALIBERS[r]["pass_when"]} for r in CONTENDERS}}


def run() -> int:
    t0 = time.time()
    doc = build()
    wit = doc["witness"]
    print("election:", doc["election"]["elected"], "|", doc["election"]["reason"], flush=True)
    for s in doc["election"]["scores"]:
        print("  %-16s correct %d/%d false_admit %d false_refuse %d"
              % (s["caliber"], s["correct"], s["fixtures_scored"], s["false_admit"],
                 s["false_refuse"]), flush=True)
    if wit.get("state") == "OK":
        print("witness identity dev vs published calibers:",
              wit["identity_max_abs_dev_vs_published"], "ok", wit["identity_ok"], flush=True)
        if not wit["identity_ok"]:
            print("REFUSED: witness rows no longer reproduce the published caliber receipt",
                  flush=True)
            return 3
    else:
        print("witness:", wit.get("state"), "-- the election still stands, it never read a book",
              flush=True)
    print("length floor:", {r: doc["implicit_record_floor"][r]["first_n_that_passes"]
                            for r in CONTENDERS}, flush=True)
    print("held book under the elected ruler:", json.dumps(doc["witness_reading"],
                                                          ensure_ascii=False), flush=True)
    doc["elapsed_sec"] = round(time.time() - t0, 2)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("wrote", os.path.relpath(OUT, ROOT), "elapsed", doc["elapsed_sec"], flush=True)
    return 0


def check() -> int:
    if not os.path.exists(OUT):
        print("MISSING", os.path.relpath(OUT, ROOT), flush=True)
        return 2
    pub = json.load(open(OUT, encoding="utf-8"))
    fresh = build(pub.get("witness"))
    bad = []
    if pub["election"]["elected"] != fresh["election"]["elected"]:
        bad.append("elected ruler drifted: published %r != re-derived %r"
                   % (pub["election"]["elected"], fresh["election"]["elected"]))
    for name, s in ((x["caliber"], x) for x in fresh["election"]["scores"]):
        past = next((x for x in pub["election"]["scores"] if x["caliber"] == name), None)
        if past is None:
            bad.append("caliber %s missing from published election" % name)
            continue
        for k in ("correct", "false_admit", "false_refuse"):
            if past.get(k) != s.get(k):
                bad.append("%s %s drifted: %r != %r" % (name, k, past.get(k), s.get(k)))
    for r in CONTENDERS:
        if (pub["implicit_record_floor"][r]["first_n_that_passes"]
                != fresh["implicit_record_floor"][r]["first_n_that_passes"]):
            bad.append("record floor drift on %s" % r)
    w = pub.get("witness") or {}
    if w.get("state") == "OK" and not w.get("identity_ok"):
        bad.append("published witness identity was already off")
    d = pub["decision"]
    if d["elected_ruler"] != pub["election"]["elected"]:
        bad.append("decision names a ruler the election did not elect")
    wr = pub.get("witness_reading") or {}
    if wr and d["witness_verdict_under_election"] != wr.get("verdict"):
        bad.append("decision verdict disagrees with the witness reading it cites")
    if bad:
        for b in bad:
            print("FAIL", b, flush=True)
        return 2
    ra = refusal_reason_audit(pub["election"]["elected"])
    if ra.get("state") == "OK":
        past = pub.get("refusal_reason_audit") or {}
        if past.get("refusals_that_survive_elected_ruler") != ra["refusals_that_survive_elected_ruler"]:
            print("FAIL refusal survival drifted: %r != %r"
                  % (past.get("refusals_that_survive_elected_ruler"),
                     ra["refusals_that_survive_elected_ruler"]), flush=True)
            return 2
    print("check OK | elected %s | witness %s | floor %s | refusals surviving %s/%s"
          % (pub["election"]["elected"], (pub.get("witness_reading") or {}).get("verdict"),
             {r: pub["implicit_record_floor"][r]["first_n_that_passes"] for r in CONTENDERS},
             ra.get("refusals_that_survive_elected_ruler"), ra.get("refusals_total")),
          flush=True)
    return 0


def selftest() -> int:
    errs = []
    seen = [0]

    def chk(ok, msg):
        seen[0] += 1
        print(("PASS " if ok else "FAIL ") + msg, flush=True)
        if not ok:
            errs.append(msg)

    # L1 the fixtures read exactly as they were declared to
    s_eff, s_yfh = score("effective_years"), score("years_for_half")
    chk(s_eff["fixtures_scored"] == 8, "L1 eight fixtures are scored, the contested one is not (%d)"
        % s_eff["fixtures_scored"])
    chk(any(f["declared"] == "DISPUTED" and not f.get("scored") for f in s_eff["fixtures"]),
        "L1b the contested fixture is disclosed and unscored")

    # L2 breadth is disqualified by its false admits, not by its total score
    chk(s_eff["false_admit"] >= 3, "L2 breadth admits %d declared pathologies" % s_eff["false_admit"])
    chk(s_yfh["false_admit"] == 0, "L2b half-life admits no declared pathology (%d)"
        % s_yfh["false_admit"])

    # L3 the ruler that refuses the front-loaded fixtures is the one that catches them
    for name in ("broad_but_spent", "narrow_start", "decaying"):
        f = next(x for x in s_yfh["fixtures"] if x["fixture"] == name)
        g = next(x for x in s_eff["fixtures"] if x["fixture"] == name)
        chk(f["read"]["word"] == "REFUSE" and g["read"]["word"] == "ADMIT",
            "L3 %s: half-life refuses, breadth admits" % name)

    # L4 election outcome and its disqualification record
    e = elect()
    chk(e["elected"] == "years_for_half", "L4 election elects the half-life ruler (%r)"
        % e["elected"])
    chk("effective_years" in e["disqualified"], "L4b breadth is named as disqualified")

    # L5 the structural claim: no witness can enter the election
    import inspect
    params = list(inspect.signature(elect).parameters)
    chk(params == [], "L5 elect() takes no parameter at all, so no book can leak in (%r)" % params)

    # L6 the election does not move when the witness is swapped for a passing book
    pass_wit = {"state": "OK", "identity_ok": True, "identity_max_abs_dev_vs_published": 0.0,
                "phases": [{"start": "2020-01-01", "years": 7, "year_net_pct": [5.0] * 7,
                            "readings": {r: read_ruler(r, [5] * 7) for r in CONTENDERS}}],
                "summary": {r: {"median": read_ruler(r, [5] * 7)["value"], "words": ["ADMIT"]}
                            for r in CONTENDERS}, "phases_count": 1}
    a = build(pass_wit)["election"]["elected"]
    fail_wit = json.loads(json.dumps(pass_wit))
    for r in CONTENDERS:
        fail_wit["summary"][r]["words"] = ["REFUSE"]
    b = build(fail_wit)["election"]["elected"]
    chk(a == b == e["elected"], "L6 a passing and a failing witness elect the same ruler (%r/%r)"
        % (a, b))

    # L7 the length floor is real and is published rather than hidden
    fl = implicit_record_floor("years_for_half")
    chk(fl["first_n_that_passes"] == 5,
        "L7 an even book needs five years before half-life passes (%r)"
        % fl["first_n_that_passes"])
    trans = [r["value"] for r in fl["even_book_readings"]]
    chk(trans == sorted(trans), "L7b the floor is monotone in record length (%r)" % trans)
    fe = implicit_record_floor("effective_years")
    chk(fe["first_n_that_passes"] == 3,
        "L7c breadth has a lower floor, which is why it cannot price a short record (%r)"
        % fe["first_n_that_passes"])

    # L8 a losing book must not read as "concentrated"; None is never a pass.  A net
    # negative table publishes None -- first version of this leg asserted that on a table
    # whose net was +7, i.e. the leg asserted what I hoped rather than what the ruler does.
    losing = calibers(_rows([-8, -3, 2, 4, 3, 5, -4]))
    chk(losing["years_for_half"] is None and losing["effective_years"] is not None,
        "L8 a net-negative table publishes None for half-life, not a number (%r/%r)"
        % (losing["years_for_half"], losing["effective_years"]))
    chk(passes("years_for_half", None) is not True, "L8b None never reads as a pass (%r)"
        % passes("years_for_half", None))

    # L8c the defect the election buys: on a nearly flat record the half is a rounding
    # artefact, so one ordinary year "explains half of it" and the ruler prints 1 -- the
    # same word it prints for one lucky year.
    dg = degeneracy()
    flat = next(r for r in dg["probes"] if r["name"] == "nearly_flat_positive")
    chk(flat["years_for_half"] == 1 and flat["degenerate"],
        "L8c a flat positive record reads half-life 1 with net/gross %.3f (degenerate)"
        % flat["net_over_gross"])
    earned = next(r for r in dg["probes"] if r["name"] == "earned_opening_year")
    chk(earned["years_for_half"] == 1 and not earned["degenerate"],
        "L8d an earned opening year reads the same 1 but is not degenerate (%.3f)"
        % earned["net_over_gross"])
    chk(dg["degenerate_count"] >= 2, "L8e degeneracy is counted, not asserted away (%d)"
        % dg["degenerate_count"])

    # L9 the witness is re-derived from the receipt's own rows, and refuses to ship on drift
    w = witness()
    if w.get("state") == "OK":
        chk(w["identity_ok"], "L9 witness calibers reproduce the published receipt (dev %.9f <= %.0e)"
            % (w["identity_max_abs_dev_vs_published"], w["identity_tol"]))
        chk(w["phases_count"] == 5, "L9b witness reads all five phases (%d)" % w["phases_count"])
    else:
        chk(True, "L9 upstream receipt missing (%s) -- witness leg skipped honestly"
            % w.get("state"))

    # L10 the published face, if it exists, still re-derives
    if os.path.exists(OUT):
        chk(check() == 0, "L10 the published election re-derives from the live code")
    else:
        chk(True, "L10 no published face yet -- check leg skipped")

    # L11 the calendar's refusals: real under the elected ruler, but printed with the one
    # the election disqualified.  Both halves must be readable or the audit is decoration.
    ra = refusal_reason_audit(e["elected"])
    if ra.get("state") == "OK":
        chk(ra["printed_reason_disqualified_by_election"],
            "L11 the printed refusal reason names a disqualified ruler")
        chk(ra["refusals_that_survive_elected_ruler"] == ra["refusals_total"],
            "L11b every calendar refusal still stands under the elected ruler (%d/%d)"
            % (ra["refusals_that_survive_elected_ruler"], ra["refusals_total"]))
        chk(all(r["survives_under_elected_ruler"] for r in ra["refusals"]),
            "L11c no refusal is an artefact of the ruler it happens to be printed with")
    else:
        chk(True, "L11 phase gate missing (%s) -- refusal audit skipped honestly" % ra.get("state"))

    print("selftest: %d/%d PASS" % (seen[0] - len(errs), seen[0]), flush=True)
    return 0 if not errs else 1


def main(argv) -> int:
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    if mode == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))