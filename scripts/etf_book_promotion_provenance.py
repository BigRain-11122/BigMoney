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
    * whether its name shares an arm with another promoted row (SAME_MECHANISM: one arm
      at several settings, e.g. one book with three cash sleeves),
    * whether the face publishes more than one promoted row (SWEEP_MEMBER: several rows
      at one face under different arms),
    * whether the row has a name at all (it may live at /arms/3, not at a book).

This second run descends one level.  r1841 could only say "these three rows live on one
face", which is a fact about publishing, not about mechanism.  The arm name is what the
publishing face chose to call the thing, so the mechanism judgement is taken from it:
the same arm prefix means one mechanism at several settings; two different arm names are
merged only when they print the same two numbers, and the contiguous token span their
names share is printed beside the merge as name evidence.  Rows whose faces never printed
a name cannot be merged at all and are reported as such instead of being quietly folded in.

The headline is three counts, deliberately: rows promoted, distinct things those rows
describe (number fingerprints), and mechanisms (named arms after merging).  It is not a
verdict about whether any of them should be on the supply list -- that decision belongs to
whoever owns the spec, and this face refuses to make it.

Rules this face inherits and enforces:
  * a missing number is not a small one (r1772): a row with no CAGR is UNMEASURED, never
    grouped with another row that is also missing its CAGR;
  * two faces publishing the same numbers is one arm counted twice, not corroboration
    (E-family: the same book is published by several faces);
  * the row path is printed with the face, because the vote's own note says 111 of 153
    readings have no name -- a census of names alone would omit most of the board;
  * a name is read, never guessed: the arm/sleeve split happens on the separator the
    publishing face used, and no name is assembled from substring similarity.

Usage: python scripts/etf_book_promotion_provenance.py [run|--check|selftest]
  run       read the vote face and publish results/etf_book_promotion_provenance.json
  --check   re-derive from the same two faces and compare with the published census
  selftest  offline legs on fixtures, no receipt files needed
"""

from __future__ import annotations

import io
import json
import os
import re
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


def split_name(book):
    """(arm, sleeve) as the publishing face wrote them; (None, None) when unnamed.

    The split happens on the first '/', which is the separator the faces use
    ('n12_forward_arm/ladder3').  A name without a separator is an arm with no sleeve.
    """
    if not isinstance(book, str) or not book.strip():
        return None, None
    s = book.strip()
    if "/" in s:
        arm, sleeve = s.split("/", 1)
        return (arm or None), (sleeve or None)
    return s, None


def name_tokens(book):
    """Lower-cased tokens of a published name; [] when the row has no name."""
    if not isinstance(book, str) or not book.strip():
        return []
    return [t for t in re.split(r"[/_\s]+", book.strip().lower()) if t]


def shared_name_span(a, b):
    """Longest contiguous token span (>=2 tokens) the two names share, else None."""
    ta, tb = name_tokens(a), name_tokens(b)
    best = None
    for i in range(len(ta)):
        for j in range(len(tb)):
            k = 0
            while i + k < len(ta) and j + k < len(tb) and ta[i + k] == tb[j + k]:
                k += 1
            if k >= 2 and (best is None or k > len(best)):
                best = ta[i:i + k]
    return best


def _mechanisms(named, fps):
    """Union named rows into mechanisms: same arm, or same published numbers.

    Returns {arm: group_id}.  Two different arm names merge only when they carry the
    same fingerprint (the same claim SAME_NUMBERS_TWICE already makes); the shared token
    span, when there is one, is reported beside the row rather than used as the merge key.
    """
    parent = {a for a, _ in named}
    parent = {a: a for a in parent}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[sorted([rx, ry])[0]] = sorted([rx, ry])[1]

    # merge arms that publish identical numbers
    fp_owner = {}
    for arm, fp in named:
        if fp is None:
            continue
        if fp in fp_owner:
            union(arm, fp_owner[fp])
        else:
            fp_owner[fp] = arm
    # collapse to dense ids ordered by first appearance
    ids = {}
    for arm, _ in named:
        root = find(arm)
        if root not in ids:
            ids[root] = len(ids)
    return {arm: ids[find(arm)] for arm, _ in named}


def classify(rows):
    """Per-row verdicts plus the headline counts.  Pure function, no disk, no clock."""
    fps = {}
    face_rows = {}
    arm_rows = {}
    for r in rows:
        fp = fingerprint(r)
        face = r.get("face")
        arm, _ = split_name(r.get("book"))
        face_rows[face] = face_rows.get(face, 0) + 1
        if fp is not None:
            fps.setdefault(fp, set()).add(face)
        if arm:
            arm_rows[arm] = arm_rows.get(arm, 0) + 1

    named = [(split_name(r.get("book"))[0], fingerprint(r))
             for r in rows if split_name(r.get("book"))[0]]
    mech_id = _mechanisms(named, fps)

    out = []
    distinct = set()
    for r in rows:
        fp = fingerprint(r)
        face = r.get("face")
        arm, sleeve = split_name(r.get("book"))
        flags = []
        span = None
        settings = None
        if fp is None:
            verdict = "UNMEASURED"
        else:
            same = fps.get(fp) or set()
            if len(same) > 1:
                verdict = "SAME_NUMBERS_TWICE"
                flags.append(sorted(same))
                partners = [o for o in rows
                            if o is not r and fingerprint(o) == fp
                            and isinstance(o.get("book"), str)]
                spans = [shared_name_span(r.get("book"), o.get("book")) for o in partners]
                spans = [s for s in spans if s]
                if spans:
                    span = max(spans, key=len)
            elif arm and arm_rows.get(arm, 0) > 1:
                verdict = "SAME_MECHANISM"
                settings = sorted({(split_name(o.get("book"))[1] or "(no sleeve)")
                                   for o in rows
                                   if split_name(o.get("book"))[0] == arm})
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
            "mechanism": arm,
            "sleeve": sleeve,
            "mechanism_rows": arm_rows.get(arm, 0) if arm else 0,
            "settings": settings,
            "from": r.get("from"),
            "to": r.get("to"),
            "cagr_pct": r.get("cagr_pct"),
            "top2_share": r.get("top2_share"),
            "fingerprint": None if fp is None else "%s/%s" % fp,
            "verdict": verdict,
            "also_published_by": flags[0] if flags else [],
            "shared_name_span": span,
        })
    # one group per mechanism, so the answer can be read without walking the rows
    groups = {}
    for r in rows:
        arm, sleeve = split_name(r.get("book"))
        if not arm:
            continue
        g = groups.setdefault(mech_id[arm], {"arms": [], "n_rows": 0,
                                             "settings": [], "numbers": []})
        if arm not in g["arms"]:
            g["arms"].append(arm)
        g["n_rows"] += 1
        s = sleeve or "(no sleeve)"
        if s not in g["settings"]:
            g["settings"].append(s)
        fp = fingerprint(r)
        if fp is not None:
            k = "%s/%s" % fp
            if k not in g["numbers"]:
                g["numbers"].append(k)
    mechanism_groups = [{"arms": sorted(g["arms"]), "n_rows": g["n_rows"],
                         "settings": sorted(g["settings"]),
                         "numbers": sorted(g["numbers"])}
                        for _, g in sorted(groups.items())]
    return {
        "n_promoted_rows": len(rows),
        "n_distinct_things": len(distinct),
        "n_distinct_numbers": len(fps),
        "n_mechanisms": len({v for v in mech_id.values()}) if mech_id else 0,
        "n_rows_without_name": sum(1 for r in rows if not split_name(r.get("book"))[0]),
        "n_faces": len(face_rows),
        "n_named": sum(1 for r in rows if isinstance(r.get("book"), str) and r["book"]),
        "n_unmeasured": sum(1 for r in rows if fingerprint(r) is None),
        "rows_per_face": {k: v for k, v in sorted(face_rows.items())},
        "mechanisms": sorted(arm_rows),
        "mechanism_groups": mechanism_groups,
        "rows": out,
    }


def summarise(c):
    """One sentence built only from the counts above.  No hand-typed numbers."""
    bits = ["%d promoted reading(s) carry %d distinct pair(s) of the two published numbers"
            % (c["n_promoted_rows"], c["n_distinct_numbers"])]
    multi = [g for g in c.get("mechanism_groups") or [] if g["n_rows"] > 1]
    for g in multi:
        if len(g["arms"]) > 1:
            bits.append("%s carry the same two numbers and are one mechanism"
                        % " and ".join(g["arms"]))
        else:
            bits.append("%s is one mechanism at %d settings (%s)"
                        % (g["arms"][0], g["n_rows"], "/".join(g["settings"])))
    if c["n_rows_without_name"]:
        bits.append("%d row(s) carry no name at all and sit in no mechanism"
                    % c["n_rows_without_name"])
    return "; ".join(bits) + "."


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
        "sentence": summarise(body),
        "question": ("if the concentration check stopped vetoing, how many of the seven "
                     "readings it would promote are distinct things -- and how many of "
                     "those are the same mechanism under a published name?"),
        "source_faces": [_rel(VOTE)],
        "evidence_cutoff": vote.get("evidence_cutoff"),
        "rule_read": _rel(VOTE) + "::rules." + RULE + ".changed",
        "honest": [
            ("SAME_MECHANISM is read off the name the publishing face chose, not off a "
             "rerun: two rows sharing an arm prefix are reported as one mechanism at "
             "several settings, and neither setting is re-measured here."),
            ("SAME_NUMBERS_TWICE is a claim about the two published numbers only: two rows "
             "that agree on CAGR and top-2 share may still differ in cost, window or "
             "capacity, and this face does not read those."),
            ("when two rows share those numbers their names are also compared: a shared "
             "contiguous token span is printed as name evidence, and its absence is left "
             "as null -- the merge then rests on the numbers alone, which is the weaker "
             "claim this face has always made."),
            ("mechanisms count only rows whose faces printed a name; rows published at "
             "/arms/N are counted in rows_without_name and are never folded into a named "
             "mechanism."),
            ("distinct things is still a lower bound for unnamed rows, and it does not "
             "merge named arms whose numbers differ -- two sleeves of one book that print "
             "different CAGRs stay two things here even though they are one mechanism."),
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
    print("rows=%d distinct=%d numbers=%d mechanisms=%d no_name=%d faces=%d named=%d "
          "unmeasured=%d"
          % (body["n_promoted_rows"], body["n_distinct_things"],
             body["n_distinct_numbers"], body["n_mechanisms"],
             body["n_rows_without_name"], body["n_faces"], body["n_named"],
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
    print("CHECK_OK %d promoted rows, %d distinct things, %d mechanisms, re-derived from %s"
          % (fresh["n_promoted_rows"], fresh["n_distinct_things"],
             fresh["n_mechanisms"], _rel(VOTE)))
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
    leg("L2 one face, three configurations, three arms -> SWEEP_MEMBER, three things",
        [r["verdict"] for r in c["rows"]] == ["SWEEP_MEMBER"] * 3
        and c["n_distinct_things"] == 3 and c["n_mechanisms"] == 3)

    # L3: a missing number is not a small one -- blanks never group with each other
    rows = [_row("F.json", "/rows/5/calibers/P", None, None, None),
            _row("F.json", "/rows/5/calibers/B", None, None, None)]
    c = classify(rows)
    leg("L3 two unmeasured rows are two things, not one",
        [r["verdict"] for r in c["rows"]] == ["UNMEASURED", "UNMEASURED"]
        and c["n_distinct_things"] == 2 and c["n_distinct_numbers"] == 0
        and c["n_mechanisms"] == 0 and c["n_rows_without_name"] == 2)

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
        and c["rows"][0]["verdict"] == "SINGLE"
        and c["rows"][0]["mechanism"] is None and c["n_mechanisms"] == 0
        and c["n_rows_without_name"] == 1)

    # L6: no promotions is a valid answer, not a crash
    c = classify([])
    leg("L6 zero promoted rows -> zeroes, no exception",
        c["n_promoted_rows"] == 0 and c["n_distinct_things"] == 0
        and c["rows_per_face"] == {} and c["n_mechanisms"] == 0
        and c["mechanisms"] == [])

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
    leg("L7b the same arm under two faces is one mechanism, not two",
        c["n_mechanisms"] == 3 and c["n_rows_without_name"] == 1)

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

    # L10: one arm at three settings is one mechanism, and the settings are named
    rows = [_row("K.json", "/arms/5", "n12_forward_arm/ladder3", 10.19, 0.7253),
            _row("K.json", "/arms/4", "n12_forward_arm/gc001_roll", 10.15, 0.7273),
            _row("K.json", "/arms/3", "n12_forward_arm/cash_zero", 9.59, 0.7524)]
    c = classify(rows)
    leg("L10 three settings of one arm -> SAME_MECHANISM, one mechanism, three things",
        [r["verdict"] for r in c["rows"]] == ["SAME_MECHANISM"] * 3
        and c["n_mechanisms"] == 1 and c["n_distinct_things"] == 3)
    leg("L10b the three settings are listed by name",
        c["rows"][0]["settings"] == ["cash_zero", "gc001_roll", "ladder3"]
        and c["rows"][0]["mechanism"] == "n12_forward_arm"
        and c["rows"][0]["sleeve"] == "ladder3")

    # L11: identical numbers under two arm names merge, and the shared span is printed
    rows = [_row("K.json", "/arms/0", "n5_gate_arm/cash_zero", 11.55, 0.7039),
            _row("I.json", "/arms/0", "cash_zero_control", 11.55, 0.7039)]
    c = classify(rows)
    leg("L11 two arm names, same numbers, shared tokens -> one mechanism with the span",
        c["n_mechanisms"] == 1
        and c["rows"][0]["shared_name_span"] == ["cash", "zero"]
        and [r["verdict"] for r in c["rows"]] == ["SAME_NUMBERS_TWICE"] * 2)

    # L11b: one shared token is not a shared name -- the span stays null
    rows = [_row("K.json", "/arms/0", "cash_a", 11.55, 0.7039),
            _row("I.json", "/arms/0", "cash_b", 11.55, 0.7039)]
    c = classify(rows)
    leg("L11b a single shared token is not a shared span",
        c["rows"][0]["shared_name_span"] is None
        and c["rows"][1]["shared_name_span"] is None
        and c["n_mechanisms"] == 1)

    # L12: identical numbers with no shared name tokens merge on the numbers alone
    rows = [_row("K.json", "/arms/0", "alpha/beta", 8.0, 0.60),
            _row("I.json", "/arms/0", "gamma/delta", 8.0, 0.60)]
    c = classify(rows)
    leg("L12 merge without name evidence keeps its span null",
        c["n_mechanisms"] == 1 and c["rows"][0]["shared_name_span"] is None
        and c["rows"][0]["verdict"] == "SAME_NUMBERS_TWICE")

    # L13: one named row on one face is SINGLE and is its own mechanism
    rows = [_row("F.json", "/arms/0", "only_arm", 7.0, 0.5)]
    c = classify(rows)
    leg("L13 a lone named row -> SINGLE, mechanism equals its arm",
        c["rows"][0]["verdict"] == "SINGLE" and c["n_mechanisms"] == 1
        and c["rows"][0]["mechanism"] == "only_arm"
        and c["rows"][0]["mechanism_rows"] == 1)

    # L14: unnamed rows never join a named mechanism, even at the same numbers
    rows = [_row("F.json", "/arms/0", "arm_x", 9.0, 0.65),
            _row("F.json", "/arms/1", None, 9.0, 0.65)]
    c = classify(rows)
    leg("L14 an unnamed row is not folded into the named mechanism",
        c["n_mechanisms"] == 1 and c["n_rows_without_name"] == 1
        and c["rows"][1]["mechanism"] is None)

    # L15: the split reads the separator the face used and does not invent one
    leg("L15 split_name keeps a name without '/' as an arm with no sleeve",
        split_name("n12_forward_arm") == ("n12_forward_arm", None)
        and split_name("a/b/c") == ("a", "b/c")
        and split_name("") == (None, None) and split_name(None) == (None, None))

    # L16: the sentence is built from the counts, and it names the mechanisms
    rows = [_row("K.json", "/arms/5", "n12_forward_arm/ladder3", 10.19, 0.7253),
            _row("K.json", "/arms/4", "n12_forward_arm/gc001_roll", 10.15, 0.7273),
            _row("K.json", "/arms/3", "n12_forward_arm/cash_zero", 9.59, 0.7524),
            _row("K.json", "/arms/0", "n5_gate_arm/cash_zero", 11.55, 0.7039),
            _row("I.json", "/arms/0", "cash_zero_control", 11.55, 0.7039),
            _row("C.json", "/rows/5/calibers/P", None, None, None)]
    c = classify(rows)
    s = summarise(c)
    leg("L16 the sentence carries its own counts and both mechanisms",
        s.startswith("6 promoted reading(s) carry 4 distinct pair(s)")
        and "n12_forward_arm is one mechanism at 3 settings (cash_zero/gc001_roll/ladder3)"
        in s
        and "cash_zero_control and n5_gate_arm carry the same two numbers" in s
        and "1 row(s) carry no name at all" in s)
    leg("L16b the sentence never calls rows candidates and never invents a count",
        "candidate" not in s and s.count("promoted reading(s)") == 1)

    # L16c: with nothing to merge the sentence says only what it counted
    c = classify([_row("F.json", "/arms/0", "only_arm", 7.0, 0.5)])
    leg("L16c single row -> one clause, no merge claim, no nameless clause",
        summarise(c) == "1 promoted reading(s) carry 1 distinct pair(s) of the two "
                        "published numbers.")

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
