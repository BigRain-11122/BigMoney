#!/usr/bin/env python3
"""What would supply actually GAIN if the concentration check stopped vetoing?

`etf_book_year_gate_vote` priced three rules and reported that `R2_advisory` admits seven
readings the status quo does not.  Seven rows, though, is not seven things: five of them
live inside one knob face (`etf_book_gate_knobs`), i.e. one mechanism priced at five
configurations, and one of those five carries the *same* CAGR and the *same* top-2 share
as an arm published by a second face under a different name.  A supply list built from
that count would hold one arm twice and would read a parameter sweep as a family.

So this face answers a narrower question than the vote did, and it answers it without a
single opinion: for every reading the vote would promote, print

    * the face that published it and the row it sits at,
    * the two numbers the vote compared (CAGR, top-2 share) -- or UNMEASURED,
    * whether those two numbers appear again under another face (SAME_NUMBERS_TWICE),
    * whether the face publishes more than one promoted row (SWEEP_MEMBER: one
      mechanism at several settings, not several mechanisms),
    * whether the row has a name at all (UNNAMED: it lives at /arms/3, not at a book).

The headline is deliberately two numbers: rows promoted, and distinct things those rows
describe.  It is not a verdict about whether any of them should be on the supply list --
that decision belongs to whoever owns the spec, and this face refuses to make it.

Rules this face inherits and enforces:
  * a missing number is not a small one (r1772): a row with no CAGR is UNMEASURED, never
    grouped with another row that is also missing its CAGR;
  * two faces publishing the same numbers is one arm counted twice, not corroboration
    (E-family: the same book is published by several faces);
  * the row path is printed with the face, because the vote's own note says 111 of 153
    readings have no name -- a census of names alone would omit most of the board.

Usage: python scripts/etf_book_promotion_provenance.py [run|--check|selftest]
  run       read the vote face and publish results/etf_book_promotion_provenance.json
  --check   re-derive from the same two faces and compare with the published census
  selftest  offline legs on fixtures, no receipt files needed
"""

from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

CST = timezone(timedelta(hours=8))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTE = os.path.join(ROOT, "results", "etf_book_year_gate_vote.json")
OUT = os.path.join(ROOT, "results", "etf_book_promotion_provenance.json")

RULE = "R2_advisory"


def _load(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _num(v):
    """Round a published number to its printed precision, or None if absent."""
    if v is None or isinstance(v, bool):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fingerprint(row):
    """The two numbers the vote compared, as one key.  None when neither is published.

    A row with only one of the two numbers keeps the half it has plus an explicit `~`
    marker, so (cagr=10.0, top2=None) can never collide with (cagr=10.0, top2=0.70).
    """
    cagr, top2 = _num(row.get("cagr_pct")), _num(row.get("top2_share"))
    if cagr is None and top2 is None:
        return None
    return ("%.4f" % cagr if cagr is not None else "~",
            "%.6f" % top2 if top2 is not None else "~")


def classify(rows):
    """Per-row verdicts plus the headline counts.  Pure function, no disk, no clock."""
    fps = {}
    face_rows = {}
    for r in rows:
        fp = fingerprint(r)
        face = r.get("face")
        face_rows[face] = face_rows.get(face, 0) + 1
        if fp is not None:
            fps.setdefault(fp, set()).add(face)

    out = []
    distinct = set()
    for r in rows:
        fp = fingerprint(r)
        face = r.get("face")
        flags = []
        if fp is None:
            verdict = "UNMEASURED"
        else:
            same = fps.get(fp) or set()
            if len(same) > 1:
                verdict = "SAME_NUMBERS_TWICE"
                flags.append(sorted(same))
            elif face_rows.get(face, 0) > 1:
                verdict = "SWEEP_MEMBER"
            else:
                verdict = "SINGLE"
            distinct.add(fp)
        if fp is None:
            # an unmeasured row is its own thing: two blank rows are not one arm
            distinct.add(("unmeasured", face, r.get("at")))
        out.append({
            "face": face,
            "at": r.get("at"),
            "book": r.get("book"),
            "from": r.get("from"),
            "to": r.get("to"),
            "cagr_pct": r.get("cagr_pct"),
            "top2_share": r.get("top2_share"),
            "fingerprint": None if fp is None else "%s/%s" % fp,
            "verdict": verdict,
            "also_published_by": flags[0] if flags else [],
        })
    return {
        "n_promoted_rows": len(rows),
        "n_distinct_things": len(distinct),
        "n_distinct_numbers": len(fps),
        "n_faces": len(face_rows),
        "n_named": sum(1 for r in rows if isinstance(r.get("book"), str) and r["book"]),
        "n_unmeasured": sum(1 for r in rows if fingerprint(r) is None),
        "rows_per_face": {k: v for k, v in sorted(face_rows.items())},
        "rows": out,
    }


def build(vote=None):
    vote = _load(VOTE) if vote is None else vote
    if not vote:
        return {"face": "etf_book_promotion_provenance", "status": "NO_VOTE_FACE"}
    rules = vote.get("rules") or {}
    block = rules.get(RULE) or {}
    rows = block.get("changed") or []
    body = classify(rows)
    body.update({
        "face": "etf_book_promotion_provenance",
        "generated": datetime.now(CST).replace(microsecond=0).isoformat(),
        "question": ("if the concentration check stopped vetoing, how many of the seven "
                     "readings it would promote are distinct things?"),
        "source_faces": [_rel(VOTE)],
        "evidence_cutoff": vote.get("evidence_cutoff"),
        "rule_read": _rel(VOTE) + "::rules." + RULE + ".changed",
        "honest": [
            ("SAME_NUMBERS_TWICE is a claim about the two published numbers only: two rows "
             "that agree on CAGR and top-2 share may still differ in cost, window or "
             "capacity, and this face does not read those."),
            ("SWEEP_MEMBER says the face publishes several promoted rows, not that those "
             "rows measure the same thing -- the knob face's own question is printed "
             "verbatim so the reader can judge it."),
            ("distinct things is a lower bound: two rows with different numbers can still "
             "be one mechanism, and this face has no way to see that."),
            ("nothing here changes the vote, the gate, or the supply list; it counts what "
             "the vote already said."),
        ],
    })
    return body


def cmd_run():
    body = build()
    if body.get("status") == "NO_VOTE_FACE":
        print("CHECK_FAIL no published vote face at %s -- run the vote first" % _rel(VOTE))
        return 2
    body["elapsed_sec"] = 0.0
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("rows=%d distinct=%d numbers=%d faces=%d named=%d unmeasured=%d"
          % (body["n_promoted_rows"], body["n_distinct_things"],
             body["n_distinct_numbers"], body["n_faces"], body["n_named"],
             body["n_unmeasured"]))
    print("-> %s" % _rel(OUT))
    return 0


def _strip(doc):
    return {k: v for k, v in doc.items() if k not in ("generated", "elapsed_sec")}


def cmd_check():
    pub = _load(OUT)
    if not pub:
        print("NO_PUBLISHED_FACE: run first")
        return 1
    fresh = _strip(build())
    a = _strip(pub)
    if a != fresh:
        moved = sorted(k for k in set(a) | set(fresh) if a.get(k) != fresh.get(k))
        print("CHECK_FAIL drift in: " + ", ".join(moved))
        for k in moved[:20]:
            print("  %s: %r -> %r" % (k, a.get(k), fresh.get(k)))
        return 1
    print("CHECK_OK %d promoted rows, %d distinct things, re-derived from %s"
          % (fresh["n_promoted_rows"], fresh["n_distinct_things"], _rel(VOTE)))
    return 0


# ---------------------------------------------------------------- selftest
def _row(face, at, book, cagr, top2):
    return {"face": face, "at": at, "book": book, "cagr_pct": cagr,
            "top2_share": top2, "from": "CONDITIONAL", "to": "ADMIT"}


def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    # L1: the same two numbers under two faces is one arm counted twice
    rows = [_row("F1.json", "/arms/0", "cash_zero", 11.55, 0.7039),
            _row("F2.json", "/arms/0", "cash_zero_control", 11.55, 0.7039)]
    c = classify(rows)
    leg("L1 same numbers across faces -> SAME_NUMBERS_TWICE on both",
        [r["verdict"] for r in c["rows"]] == ["SAME_NUMBERS_TWICE", "SAME_NUMBERS_TWICE"]
        and c["n_distinct_things"] == 1)
    leg("L1b the second face is named as the co-publisher",
        c["rows"][0]["also_published_by"] == ["F1.json", "F2.json"])

    # L2: several promoted rows inside one face is a sweep, not a family
    rows = [_row("K.json", "/arms/0", "a", 10.0, 0.70),
            _row("K.json", "/arms/1", "b", 10.1, 0.71),
            _row("K.json", "/arms/2", "c", 10.2, 0.72)]
    c = classify(rows)
    leg("L2 one face, three configurations -> SWEEP_MEMBER, three distinct things",
        [r["verdict"] for r in c["rows"]] == ["SWEEP_MEMBER"] * 3
        and c["n_distinct_things"] == 3 and c["n_faces"] == 1)

    # L3: a missing number is not a small one -- blanks never group with each other
    rows = [_row("F.json", "/rows/5/calibers/P", None, None, None),
            _row("F.json", "/rows/5/calibers/B", None, None, None)]
    c = classify(rows)
    leg("L3 two unmeasured rows are two things, not one",
        [r["verdict"] for r in c["rows"]] == ["UNMEASURED", "UNMEASURED"]
        and c["n_distinct_things"] == 2 and c["n_distinct_numbers"] == 0)

    # L4: half a number cannot collide with a full one or with a different half
    rows = [_row("F.json", "/a", "x", 10.0, None),
            _row("G.json", "/a", "y", 10.0, 0.70)]
    c = classify(rows)
    leg("L4 a row with only CAGR does not collide with a full row",
        c["n_distinct_things"] == 2
        and c["rows"][0]["verdict"] == "SINGLE"
        and c["rows"][0]["fingerprint"] == "10.0000/~")

    # L5: unnamed rows are counted, not silently dropped
    rows = [_row("F.json", "/arms/3", None, 9.59, 0.7524)]
    c = classify(rows)
    leg("L5 an unnamed row keeps its path and its numbers",
        c["n_named"] == 0 and c["rows"][0]["at"] == "/arms/3"
        and c["rows"][0]["verdict"] == "SINGLE")

    # L6: no promotions is a valid answer, not a crash
    c = classify([])
    leg("L6 zero promoted rows -> zeroes, no exception",
        c["n_promoted_rows"] == 0 and c["n_distinct_things"] == 0
        and c["rows_per_face"] == {})

    # L7: the headline distinguishes rows from things (the whole point)
    rows = [_row("K.json", "/arms/0", "a", 10.0, 0.70),
            _row("K.json", "/arms/1", "b", 10.1, 0.71),
            _row("K.json", "/arms/2", "c", 10.2, 0.72),
            _row("I.json", "/arms/0", "a", 10.0, 0.70),
            _row("C.json", "/rows/5/calibers/P", None, None, None)]
    c = classify(rows)
    leg("L7 5 rows / 4 things / 3 numbers / 3 faces is reported as such",
        c["n_promoted_rows"] == 5 and c["n_distinct_things"] == 4
        and c["n_distinct_numbers"] == 3 and c["n_faces"] == 3
        and c["n_named"] == 4 and c["n_unmeasured"] == 1)

    # L8: build() on an absent vote face says so instead of publishing zeroes
    leg("L8 no vote face -> status NO_VOTE_FACE",
        build({}).get("status") == "NO_VOTE_FACE")

    # L9: build() reads the rule block it claims to read, nothing else
    vote = {"evidence_cutoff": "2026-11-18",
            "rules": {"R0_status_quo": {"changed": []},
                      "R2_advisory": {"changed": [_row("F.json", "/arms/3", "z",
                                                       9.59, 0.7524)]}}}
    body = build(vote)
    leg("L9 build reads R2_advisory only and carries the cutoff",
        body["n_promoted_rows"] == 1 and body["evidence_cutoff"] == "2026-11-18")

    passed = sum(1 for _, v in ok if v)
    for name, v in ok:
        print("%s %s" % ("PASS" if v else "FAIL", name))
    print("selftest %d/%d" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd in ("--check", "check"):
        return cmd_check()
    if cmd == "selftest":
        return selftest()
    print(__doc__.strip().splitlines()[-1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
