"""E637 -- what does E633's "below the receiver" fold actually remove?

E633 classifies every access of a counted line's receiver and folds ``depth > 1`` into
``read_below_the_receiver``, which is published as "does not read this key" and so never enters the
same-key count.  E636 then reported that 4 of its 5 after-side unresolved locations DO read the
counted key -- one level below the receiver -- and read that as a population limit on E633.

Both sentences cannot be about the same set.  This study prices the fold on both populations at
once, re-derived from the tree rather than copied out of either published face:

  * on E633's own population (its counted read lines), every folded-out access is listed with its
    depth and its inner key, and the question is asked directly: does the inner key name the counted
    key of that row?
  * on E636's population (computed-key read sites), every location that E636 reports as reading the
    counted key below the receiver is joined to E633's row for the same (module, read line) and
    asked whether E633 counts a recognised read at that line.

Three outcomes are distinguished, because they are three different claims about the code:

  * the fold removes a read of the counted key           -> E632/E633 undercount, gate goes red
  * the fold removes other keys only                     -> the fold is free at its own population
  * and, separately, whether the *locations* E636 names are counted by E633 anyway -- if they are,
    the two instruments draw the word "below the receiver" at different depths and neither lost a
    read; if they are not, E636's number is a population limit and E633's is a census of a different
    population.

Usage:
  python scripts/e637_below_fold_price.py run       # build the face
  python scripts/e637_below_fold_price.py verify    # re-derive the counts from the face's rows
  python scripts/e637_below_fold_price.py selftest  # offline fixture legs
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "BELOWFOLDPRICE.json"
LATEST = "belowfoldprice_latest.json"
STUDY = "E637_below_fold_price"
SELF_PARTS = {"e637_below_fold_price.py", "run_e637_smoke_leg.py", "_probe_e637.py"}
SOURCE_FACES = ["results/state_tilt/READFORMGAP.json", "results/state_tilt/READBINDINGREACH.json"]

import e633_read_forms as e633  # noqa: E402
import e636_read_binding_reach as e636  # noqa: E402

R_BELOW = e633.R_BELOW
R_KEY = e633.R_KEY

V_HIDES_A_READ = ("the_fold_removes_N_accesses_of_which_M_name_the_counted_key_of_its_own_row_so_"
                  "the_same_key_count_E632_published_undercounts_the_reads_on_those_lines")
V_LABEL_ONLY = ("the_fold_removes_N_accesses_and_none_of_them_names_the_counted_key_of_its_own_row_"
                "so_it_hides_no_read;_but_K_of_the_locations_E636_reports_as_reading_the_counted_key_"
                "below_the_receiver_are_the_same_locations_where_E633_counts_a_recognised_read,_so_"
                "the_two_instruments_draw_the_boundary_at_different_depths_and_neither_lost_a_read")
V_FOLD_FREE = ("the_fold_removes_N_accesses_and_none_of_them_names_the_counted_key_of_its_own_row_"
               "and_no_E636_location_reports_the_counted_key_below_the_receiver_so_the_fold_is_free")
V_NO_FOLD = ("the_population_carries_no_read_below_a_receiver_so_the_fold_removes_nothing_and_"
             "E636's_below_the_receiver_number_is_about_a_different_population")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def inner_key_of(access):
    """The key a folded-out access names, or None when it names none."""
    k = access.get("key")
    return k if isinstance(k, str) else None


def measure(root=ROOT):
    """Re-derive both populations from the tree; neither upstream face is written."""
    f633 = e633.measure(root)
    f636 = e636.measure(root)
    below_below = below_rows(f633, f636)
    return {
        "rows": below_below,
        "unparsed": f633.get("unparsed", 0) + f636.get("unparsed", 0),
        "source_rows_633": len(f633.get("rows") or []),
        "source_rows_636": len(f636.get("rows") or []),
        "verdict_633": e633.face_from(f633)[0].get("verdict"),
        "verdict_636": e636.decide(e636.counts_of(f636["rows"])),
    }


def below_rows(f633, f636):
    """One row per counted read line of E633, joined to E636's below-the-receiver lists."""
    e636_by_line = {}
    for r in f636.get("rows") or []:
        k = (r.get("module"), r.get("line"))
        e636_by_line.setdefault(k, []).append(r)
    out = []
    for r in f633.get("rows") or []:
        accesses = [a for a in (r.get("accesses") or []) if a.get("form") == R_BELOW]
        key = r.get("key")
        below = []
        for a in accesses:
            ik = inner_key_of(a)
            below.append({"depth": a.get("depth"), "inner_key": ik,
                          "column": a.get("column"),
                          "names_the_counted_key": bool(ik is not None and ik == key)})
        twins = e636_by_line.get((r.get("module"), r.get("read_line")), [])
        listed = sorted({e for t in twins for e in (t.get("below_the_receiver_at_this_location") or [])
                         if isinstance(e, str)})
        out.append({
            "module": r.get("module"),
            "function": r.get("function"),
            "read_line": r.get("read_line"),
            "key": key,
            "receiver": r.get("receiver"),
            "recognised_reads_on_the_line": r.get("recognised_reads_on_the_line"),
            "below_accesses": below,
            "below_count": len(below),
            "below_naming_the_counted_key": sum(1 for b in below if b["names_the_counted_key"]),
            "e636_rows_at_this_line": len(twins),
            "e636_below_the_receiver_expressions": listed,
            "e636_lists_the_counted_key_below": bool(key is not None and key in listed),
        })
    return out


def counts_of(rows):
    below = [b for r in rows for b in (r.get("below_accesses") or [])]
    both = [r for r in rows if r.get("e636_rows_at_this_line")]
    listed = [r for r in rows if r.get("e636_lists_the_counted_key_below")]
    depths = {}
    for b in below:
        depths[str(b.get("depth"))] = depths.get(str(b.get("depth")), 0) + 1
    return {
        "rows": len(rows),
        "rows_also_in_the_e636_population": len(both),
        "below_accesses": len(below),
        "below_with_a_literal_inner_key": sum(1 for b in below if b.get("inner_key") is not None),
        "below_with_no_inner_key": sum(1 for b in below if b.get("inner_key") is None),
        "below_naming_the_counted_key": sum(1 for b in below if b.get("names_the_counted_key")),
        "lines_carrying_a_below_access": sum(1 for r in rows if r.get("below_count")),
        "lines_whose_below_access_names_the_counted_key":
            sum(1 for r in rows if r.get("below_naming_the_counted_key")),
        "below_depth_histogram": dict(sorted(depths.items())),
        "rows_where_e636_lists_the_counted_key_below": len(listed),
        "rows_where_e636_lists_the_key_below_and_e633_counts_a_recognised_read":
            sum(1 for r in listed if (r.get("recognised_reads_on_the_line") or 0) > 0),
        "rows_where_e636_lists_the_key_below_and_e633_counts_nothing":
            sum(1 for r in listed if not (r.get("recognised_reads_on_the_line") or 0)),
        "e636_below_expressions_named": sorted(
            {e for r in rows for e in (r.get("e636_below_the_receiver_expressions") or [])}),
        "inner_keys_removed": sorted({b["inner_key"] for b in below if b.get("inner_key")}),
    }


def decide(c):
    if c["below_accesses"] == 0:
        return V_NO_FOLD
    if c["below_naming_the_counted_key"] > 0:
        return V_HIDES_A_READ
    if c["rows_where_e636_lists_the_counted_key_below"] > 0:
        return V_LABEL_ONLY
    return V_FOLD_FREE


def answer_of(c):
    return ("E633 folds %d access(es) out of the same-key census across %d of its %d counted read "
            "line(s) (depths %s).  %d of them name a literal key (%s) and %d name none; %d name the "
            "counted key of their own row.  %d of those line(s) also sit in E636's population, and "
            "on %d of them E636 reports the counted key itself as read below the receiver -- %d of "
            "which E633 simultaneously counts as a recognised read of that key on the same line, %d "
            "of which E633 counts nothing at all."
            % (c["below_accesses"], c["lines_carrying_a_below_access"], c["rows"],
               ", ".join("%s x%d" % (k, v) for k, v in c["below_depth_histogram"].items()) or "-",
               c["below_with_a_literal_inner_key"], ", ".join(c["inner_keys_removed"]) or "-",
               c["below_with_no_inner_key"], c["below_naming_the_counted_key"],
               c["rows_also_in_the_e636_population"],
               c["rows_where_e636_lists_the_counted_key_below"],
               c["rows_where_e636_lists_the_key_below_and_e633_counts_a_recognised_read"],
               c["rows_where_e636_lists_the_key_below_and_e633_counts_nothing"]))


# ---------------------------------------------------------------- face
def face_from(m):
    c = counts_of(m["rows"])
    return {
        "study": STUDY,
        "script": "scripts/e637_below_fold_price.py",
        "card": "E637",
        "evidence_cutoff": TODAY,
        "dept": "研究",
        "method": ("both upstream populations are re-derived from the tree (e633.measure and "
                   "e636.measure, neither face written): every 'read below the receiver' access of "
                   "E633's counted read lines is listed with its depth and inner key and compared "
                   "with the counted key of its own row, and E636's per-location below-the-receiver "
                   "key lists are joined to E633's rows on (module, read line)"),
        "population_source": ("%d counted read line(s) of %s joined to %d computed-key read site(s) "
                              "of %s"
                              % (m["source_rows_633"], SOURCE_FACES[0],
                                 m["source_rows_636"], SOURCE_FACES[1])),
        "source_faces": SOURCE_FACES,
        "source_verdicts": {"E633": m.get("verdict_633"), "E636": m.get("verdict_636")},
        "counts": c,
        "rows": m["rows"],
        "limits": [
            "the fold is priced only where a counted line resolves to a receiver; E633's own "
            "census already refuses to price a line that does not, and those lines are absent here",
            "an inner key is compared as a literal string only: a computed key below the receiver is "
            "published as naming nothing, never as naming a different key",
            "the join key is (module, read line), so two counted rows on one line share a row's "
            "E636 context; the population carries no such pair today and the count of joined rows "
            "is published so a future pair would show up",
            "this study rewrites neither upstream face and runs no runner",
        ],
        "verdict": decide(c),
        "answer": answer_of(c),
    }


def face_problems(face):
    """Everything the smoke leg refuses, derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    live = counts_of(rows)
    for key in ("rows", "below_accesses", "below_with_a_literal_inner_key",
                "below_with_no_inner_key", "below_naming_the_counted_key",
                "lines_carrying_a_below_access", "lines_whose_below_access_names_the_counted_key",
                "rows_where_e636_lists_the_counted_key_below",
                "rows_where_e636_lists_the_key_below_and_e633_counts_a_recognised_read",
                "rows_where_e636_lists_the_key_below_and_e633_counts_nothing"):
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for r in rows:
        if r.get("below_count") != len(r.get("below_accesses") or []):
            problems.append("row %s:%s carries a below_count that is not its access list"
                            % (r.get("module"), r.get("read_line")))
            break
        if r.get("below_naming_the_counted_key") != sum(
                1 for b in (r.get("below_accesses") or []) if b.get("names_the_counted_key")):
            problems.append("row %s:%s carries a counting-keys number that is not its accesses"
                            % (r.get("module"), r.get("read_line")))
            break
        if r.get("e636_lists_the_counted_key_below") and not r.get("e636_rows_at_this_line"):
            problems.append("row %s:%s claims an E636 list with no E636 row joined"
                            % (r.get("module"), r.get("read_line")))
            break
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = face_from(measure(root))
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: rows=%d below=%d literal=%d named_key=%d e636_locations=%d both_counted=%d"
        % (c["rows"], c["below_accesses"], c["below_with_a_literal_inner_key"],
           c["below_naming_the_counted_key"], c["rows_where_e636_lists_the_counted_key_below"],
           c["rows_where_e636_lists_the_key_below_and_e633_counts_a_recognised_read"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_ROWS = [
    {"module": "a.py", "function": "f", "read_line": 10, "key": "x1", "receiver": "sleeves",
     "recognised_reads_on_the_line": 1,
     "below_accesses": [{"depth": 3, "inner_key": "cutoff", "column": 45,
                         "names_the_counted_key": False}],
     "below_count": 1, "below_naming_the_counted_key": 0,
     "e636_rows_at_this_line": 1,
     "e636_below_the_receiver_expressions": ["cutoff", "x1"],
     "e636_lists_the_counted_key_below": True},
    {"module": "b.py", "function": "g", "read_line": 20, "key": "days", "receiver": "P",
     "recognised_reads_on_the_line": 1,
     "below_accesses": [{"depth": 2, "inner_key": None, "column": 39,
                         "names_the_counted_key": False}],
     "below_count": 1, "below_naming_the_counted_key": 0,
     "e636_rows_at_this_line": 0,
     "e636_below_the_receiver_expressions": [],
     "e636_lists_the_counted_key_below": False},
]

FIXTURE_HIDES = [
    {"module": "c.py", "function": "h", "read_line": 30, "key": "x1", "receiver": "m",
     "recognised_reads_on_the_line": 1,
     "below_accesses": [{"depth": 2, "inner_key": "x1", "column": 7,
                         "names_the_counted_key": True}],
     "below_count": 1, "below_naming_the_counted_key": 1,
     "e636_rows_at_this_line": 0,
     "e636_below_the_receiver_expressions": [],
     "e636_lists_the_counted_key_below": False},
]


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
            say("PASS :: " + name)
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL :: %s :: %s" % (name, exc))

    def counts_add_up():
        c = counts_of(FIXTURE_ROWS)
        assert c["below_accesses"] == 2, c
        assert c["below_with_a_literal_inner_key"] == 1, c
        assert c["below_with_no_inner_key"] == 1, c
        assert c["below_naming_the_counted_key"] == 0, c
        assert c["rows_where_e636_lists_the_counted_key_below"] == 1, c
        assert c["rows_where_e636_lists_the_key_below_and_e633_counts_a_recognised_read"] == 1, c
        assert c["rows_where_e636_lists_the_key_below_and_e633_counts_nothing"] == 0, c

    def depth_histogram():
        c = counts_of(FIXTURE_ROWS)
        assert c["below_depth_histogram"] == {"2": 1, "3": 1}, c["below_depth_histogram"]

    def label_only_is_reachable():
        assert decide(counts_of(FIXTURE_ROWS)) == V_LABEL_ONLY

    def hides_is_reachable():
        assert decide(counts_of(FIXTURE_HIDES)) == V_HIDES_A_READ

    def empty_population_is_no_fold():
        assert decide(counts_of([])) == V_NO_FOLD

    def fold_free_when_nobody_reports_the_key_below():
        rows = [dict(FIXTURE_ROWS[1])]
        assert decide(counts_of(rows)) == V_FOLD_FREE

    def face_problems_catches_a_wrong_verdict():
        face = {"rows": FIXTURE_ROWS, "counts": counts_of(FIXTURE_ROWS),
                "verdict": V_FOLD_FREE}
        assert face_problems(face), "a wrong verdict was accepted"

    def face_problems_catches_a_short_below_count():
        bad = [dict(FIXTURE_ROWS[0])]
        bad[0]["below_count"] = 0
        face = {"rows": bad, "counts": counts_of(bad), "verdict": decide(counts_of(bad))}
        assert any("below_count" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_an_uncounted_key_claim():
        bad = [dict(FIXTURE_ROWS[0])]
        bad[0]["below_naming_the_counted_key"] = 1
        face = {"rows": bad, "counts": counts_of(bad), "verdict": decide(counts_of(bad))}
        assert face_problems(face), "a counting-keys mismatch was accepted"

    def answer_names_the_numbers():
        c = counts_of(FIXTURE_ROWS)
        a = answer_of(c)
        assert "2" in a and "x1" in a, a

    for name, fn in [
        ("counts_add_up", counts_add_up),
        ("depth_histogram", depth_histogram),
        ("label_only_is_reachable", label_only_is_reachable),
        ("hides_is_reachable", hides_is_reachable),
        ("empty_population_is_no_fold", empty_population_is_no_fold),
        ("fold_free_when_nobody_reports_the_key_below",
         fold_free_when_nobody_reports_the_key_below),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_short_below_count", face_problems_catches_a_short_below_count),
        ("face_problems_catches_an_uncounted_key_claim",
         face_problems_catches_an_uncounted_key_claim),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc, problems = build(root=ROOT)
        problems = problems + face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    doc, problems = build(root=ROOT)
    problems = problems + face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))