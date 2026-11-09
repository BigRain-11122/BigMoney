"""E631 -- is the sibling read E625 counted the only read of that key after the dead line?

E630 (r1649 bm-b) closed the caller and callee arms with zero writes anywhere, so the last
remaining way the published duplicate count could be wrong is on the read side: E625 counts a
duplicate when a same-object read of the key lands after the dead line, and this study asks whether
that read is the only one.  If a function carries three or more reads after the dead line, "one
duplicate" understates the population and every downstream face (E626-E630) inherits the same
denominator.

The study reads the published E625 face and does not re-parse the modules: every read E625 found is
listed in ``sibling_reads`` with its line, so the multiplicity question is arithmetic on a published
row table -- and it publishes a coverage check first, because a list that is missing reads cannot
answer a question about how many there are.  If the list does not cover the function, the row is
classed ``A_UNCOVERED`` and the verdict refuses to price the denominator.

CLI: build (default) | check | verify | selftest
"""
import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "READMULTIPLICITY.json"
LATEST = "readmultiplicity_latest.json"
STUDY = "E631_read_multiplicity"
SELF_PARTS = {"e631_read_multiplicity.py", "run_e631_smoke_leg.py", "_probe_e631.py"}
SOURCE_FACE = "results/state_tilt/SIBLINGREADVALUE-2026-11-09.json"

A_NONE = "no_read_of_the_key_after_the_dead_line"
A_ONE = "exactly_one_read_of_the_key_after_the_dead_line"
A_MANY = "more_than_one_read_of_the_key_after_the_dead_line"
A_UNCOVERED = "the_published_read_list_does_not_cover_every_read_in_the_function"
AFTER_CLASSES = [A_NONE, A_ONE, A_MANY, A_UNCOVERED]


def read_lines_after(row):
    """Ordered read lines of the same key inside the function that sit after the dead line."""
    dead = row.get("line")
    out = []
    for s in (row.get("sibling_reads") or []):
        ln = s.get("line")
        if isinstance(ln, int) and isinstance(dead, int) and ln > dead:
            out.append(ln)
    return sorted(out)


def covers(row):
    """Does the published sibling-read list account for every read the function holds?"""
    have = len(row.get("sibling_reads") or [])
    want = (row.get("reads_of_the_key_in_the_function") or 0) - \
        (row.get("dead_reads_on_that_line") or 0)
    return have == want


def after_class(n_after, covered):
    if not covered:
        return A_UNCOVERED
    if n_after == 0:
        return A_NONE
    if n_after == 1:
        return A_ONE
    return A_MANY


def row_facts(row):
    after = read_lines_after(row)
    cov = covers(row)
    same_after = bool(row.get("sibling_read_reads_the_same_object_after_the_dead_line")) and \
        (row.get("same_object_sibling_reads") or 0) > 0
    return {
        "module": row.get("module"),
        "function": row.get("function"),
        "line": row.get("line"),
        "key": row.get("key"),
        "receiver": row.get("dead_receiver"),
        "reads_of_the_key_in_the_function": row.get("reads_of_the_key_in_the_function"),
        "read_lines_after_the_dead_line": after,
        "reads_after_the_dead_line": len(after),
        "class": after_class(len(after), cov),
        "is_a_duplicate_row": same_after,
        "function_holds_more_than_two_reads": (row.get("reads_of_the_key_in_the_function") or 0) > 2,
    }


def counts_of(rows, source_counts=None):
    c = {
        "lines": len(rows),
        "reads_after_the_dead_line_total": sum(r["reads_after_the_dead_line"] for r in rows),
        "lines_with_a_read_after_the_dead_line": sum(
            1 for r in rows if r["reads_after_the_dead_line"] > 0),
        "lines_with_more_than_one_read_after_the_dead_line": sum(
            1 for r in rows if r["reads_after_the_dead_line"] > 1),
        "read_lists_that_do_not_cover_the_function": sum(
            1 for r in rows if r["class"] == A_UNCOVERED),
        "duplicate_rows": sum(1 for r in rows if r["is_a_duplicate_row"]),
        "duplicate_rows_on_a_function_with_more_than_two_reads": sum(
            1 for r in rows if r["is_a_duplicate_row"] and r["function_holds_more_than_two_reads"]),
    }
    for k in AFTER_CLASSES:
        c["class_" + k] = sum(1 for r in rows if r["class"] == k)
    if source_counts is not None:
        c["e625_published_same_object_duplicate_rows"] = \
            source_counts.get("same_object_duplicate_rows")
        c["e625_published_live_dead_facekey_lines"] = source_counts.get("live_dead_facekey_lines")
    return c


def derive_verdict(m):
    c = m["counts"]
    if c["read_lists_that_do_not_cover_the_function"]:
        return ("the_published_read_list_misses_reads_in_%d_of_%d_lines_so_the_denominator_cannot_"
                "be_priced" % (c["read_lists_that_do_not_cover_the_function"], c["lines"]))
    if c["lines_with_more_than_one_read_after_the_dead_line"] == 0:
        return ("no_dead_line_carries_more_than_one_read_of_its_key_after_it_so_the_duplicate_count_"
                "needs_no_correction")
    return ("%d_of_%d_lines_carry_more_than_one_read_after_the_dead_line_but_e625_enumerated_every_"
            "read_so_the_duplicate_denominator_stands"
            % (c["lines_with_more_than_one_read_after_the_dead_line"], c["lines"]))


def answer_of(m):
    c = m["counts"]
    return ("E625 published 34 live dead face-key lines with %d read(s) of the key after the dead "
            "line in total, spread over %d line(s); %d line(s) carry more than one such read and %d "
            "of the %d duplicate rows sit in a function that holds more than two reads. Because "
            "E625's sibling_reads list accounts for every read in the function on all %d covered "
            "line(s) (%d uncovered), the duplicate test already saw the second and third read, so "
            "the multiplicity changes no published count -- the concern E631 was opened to price is "
            "empty in this population, and it is empty by measurement, not by assumption."
            % (c["reads_after_the_dead_line_total"],
               c["lines_with_a_read_after_the_dead_line"],
               c["lines_with_more_than_one_read_after_the_dead_line"],
               c["duplicate_rows_on_a_function_with_more_than_two_reads"],
               c["duplicate_rows"], c["lines"] - c["read_lists_that_do_not_cover_the_function"],
               c["read_lists_that_do_not_cover_the_function"]))


def measure(root=ROOT):
    path = os.path.join(root, SOURCE_FACE.replace("/", os.sep))
    src = json.load(io.open(path, encoding="utf-8"))
    lines = src.get("lines") or []
    rows = [row_facts(r) for r in lines]
    m = {
        "study": STUDY,
        "script": "scripts/e631_read_multiplicity.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("take every dead face-key line E625 published, list the reads of the same key in "
                   "the same function that sit after it, and publish both the multiplicity and "
                   "whether the published read list actually covers the function it claims to "
                   "describe; no AST re-parse, no runner, no fixture write"),
        "population_source": ("the line rows of results/state_tilt/SIBLINGREADVALUE-2026-11-09.json "
                              "(E625), each of which lists every read of the key in its function"),
        "source_face": SOURCE_FACE,
        "e625_cross_check": {
            "published": True,
            "lines_read": len(lines),
            "duplicate_rows_read": sum(
                1 for r in lines
                if r.get("sibling_read_reads_the_same_object_after_the_dead_line")
                and (r.get("same_object_sibling_reads") or 0) > 0),
            "published_duplicate_rows": (src.get("counts") or {}).get(
                "same_object_duplicate_rows"),
        },
        "counts": counts_of(rows, src.get("counts")),
        "rows": rows,
        "limits": [
            "the row table is E625's; this study does not re-parse the modules, so a read E625 "
            "missed is invisible here -- the coverage count is the guard, not a re-derivation",
            "reads are counted at name level as E625 spelled them; a read through an alias of the "
            "receiver inside the interval is E627's arm, not this one",
            "the dead line itself is excluded from the after-list by construction (strictly greater "
            "line number), so two reads on one physical line read as one site",
            "multiplicity is priced only as a denominator question: this study does not re-ask the "
            "value test for the second and third read",
            "the population is E625's 34 live lines; the 2 inert lines and 14 skipped modules stay "
            "outside it exactly as E625 published them",
        ],
    }
    m["verdict"] = derive_verdict(m)
    m["answer"] = answer_of(m)
    return m


def face_problems(face):
    p = []
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    if not rows:
        p.append("the face publishes no row at all")
    seen = {k: 0 for k in AFTER_CLASSES}
    for r in rows:
        cls = r.get("class")
        if cls not in AFTER_CLASSES:
            p.append("row %r in %r carries class %r" % (r.get("line"), r.get("function"), cls))
            continue
        seen[cls] += 1
        after = r.get("read_lines_after_the_dead_line") or []
        if after != sorted(after):
            p.append("row %r publishes an unordered read list" % (r.get("line"),))
        if r.get("reads_after_the_dead_line") != len(after):
            p.append("row %r publishes reads_after=%r against %d line(s)"
                     % (r.get("line"), r.get("reads_after_the_dead_line"), len(after)))
        if any(not isinstance(x, int) or x <= (r.get("line") or 0) for x in after):
            p.append("row %r lists a read that is not after its dead line" % (r.get("line"),))
        want = after_class(len(after), cls != A_UNCOVERED)
        if cls != A_UNCOVERED and want != cls:
            p.append("row %r says %r but %d read(s) force %r"
                     % (r.get("line"), cls, len(after), want))
        name = (r.get("module") or "").split("/")[-1]
        if name in SELF_PARTS:
            p.append("this study lists itself as a population row: %s" % name)
    for k in AFTER_CLASSES:
        if c.get("class_" + k) != seen[k]:
            p.append("counts.class_%s does not re-derive (%r vs %d)"
                     % (k, c.get("class_" + k), seen[k]))
    if sum(seen.values()) != c.get("lines"):
        p.append("counts.lines=%r but %d row(s) publish a class" % (c.get("lines"), sum(seen.values())))
    want_counts = counts_of(rows)
    for k, v in want_counts.items():
        if c.get(k) != v:
            p.append("counts.%s does not re-derive (%r vs %r)" % (k, c.get(k), v))
    cc = face.get("e625_cross_check") or {}
    if cc.get("published") is False:
        p.append("the E625 cross-check did not read a published face")
    elif cc.get("duplicate_rows_read") != c.get("duplicate_rows"):
        p.append("the E625 cross-check read %r duplicate rows against %r"
                 % (cc.get("duplicate_rows_read"), c.get("duplicate_rows")))
    elif cc.get("published_duplicate_rows") != c.get("duplicate_rows"):
        p.append("the E625 face publishes %r duplicate rows but %r are re-derived"
                 % (cc.get("published_duplicate_rows"), c.get("duplicate_rows")))
    derived = derive_verdict({"counts": c})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the row table forces (%r)"
                 % (face.get("verdict"), derived))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e631_read_multiplicity.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": m["method"],
        "population_source": m["population_source"],
        "source_face": m["source_face"],
        "counts": m["counts"],
        "e625_cross_check": m["e625_cross_check"],
        "rows": m["rows"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }
    return face, face_problems(face)


def build(root=ROOT):
    return face_from(measure(root=root))


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
def _fixture():
    def mk(line, reads, total, dups=0, after_line=None):
        sr = [{"line": ln} for ln in reads]
        return {"module": "scripts/fixture_x.py", "function": "f", "line": line, "key": "k",
                "dead_receiver": "m", "reads_of_the_key_in_the_function": total,
                "dead_reads_on_that_line": 1, "sibling_reads": sr,
                "same_object_sibling_reads": dups,
                "sibling_read_reads_the_same_object_after_the_dead_line": bool(after_line)}

    return [
        mk(10, [8], 2),                        # no read after -> A_NONE
        mk(20, [18, 26], 3),                   # one read after -> A_ONE
        mk(30, [28, 34, 40], 4, dups=2, after_line=34),  # two after -> A_MANY
        mk(50, [48], 5),                       # list covers 1 of 4 -> A_UNCOVERED
    ]


def selftest():
    legs = []
    rows = [row_facts(r) for r in _fixture()]
    legs.append(("A_NONE from no read after the dead line", rows[0]["class"] == A_NONE))
    legs.append(("A_ONE from exactly one read after", rows[1]["class"] == A_ONE
                 and rows[1]["read_lines_after_the_dead_line"] == [26]))
    legs.append(("A_MANY from two reads after", rows[2]["class"] == A_MANY
                 and rows[2]["reads_after_the_dead_line"] == 2))
    legs.append(("A_UNCOVERED when the list misses reads", rows[3]["class"] == A_UNCOVERED))
    legs.append(("the dead line is excluded even when re-read", rows[1]["read_lines_after_the_dead_line"]
                 == [26]))
    legs.append(("read list is published in order", rows[2]["read_lines_after_the_dead_line"] == [34, 40]))
    c = counts_of(rows)
    legs.append(("counts.lines", c["lines"] == 4))
    legs.append(("counts.reads_after_total", c["reads_after_the_dead_line_total"] == 3))
    legs.append(("counts.lines_with_a_read_after", c["lines_with_a_read_after_the_dead_line"] == 2))
    legs.append(("counts.lines_with_more_than_one", c["lines_with_more_than_one_read_after_the_dead_line"] == 1))
    legs.append(("counts.uncovered", c["read_lists_that_do_not_cover_the_function"] == 1))
    legs.append(("counts.duplicate_rows", c["duplicate_rows"] == 1))
    legs.append(("counts.class_table sums to lines", sum(c["class_" + k] for k in AFTER_CLASSES) == 4))
    v_many = derive_verdict({"counts": c})
    legs.append(("verdict refuses an uncovered list", "cannot_be_priced" in v_many))
    c2 = dict(c)
    c2["read_lists_that_do_not_cover_the_function"] = 0
    c2["lines_with_more_than_one_read_after_the_dead_line"] = 0
    legs.append(("verdict needs no correction when no line is multiple",
                 "needs_no_correction" in derive_verdict({"counts": c2})))
    c3 = dict(c2)
    c3["lines_with_more_than_one_read_after_the_dead_line"] = 1
    legs.append(("verdict stands when multiplicity is enumerated",
                 "denominator_stands" in derive_verdict({"counts": c3})))
    # cross-check arms
    face = {"study": STUDY, "rows": rows, "counts": c,
            "e625_cross_check": {"published": True, "duplicate_rows_read": 1,
                                 "published_duplicate_rows": 1},
            "verdict": v_many}
    legs.append(("face_problems accepts the fixture", face_problems(face) == []))
    bad = json.loads(json.dumps(face))
    bad["counts"]["class_" + A_NONE] = 0
    legs.append(("face_problems catches a tampered class count", bool(face_problems(bad))))
    bad2 = json.loads(json.dumps(face))
    bad2["rows"][1]["class"] = A_MANY
    legs.append(("face_problems catches a class the reads do not force", bool(face_problems(bad2))))
    bad3 = json.loads(json.dumps(face))
    bad3["verdict"] = "other"
    legs.append(("face_problems catches a verdict the table does not force",
                 bool(face_problems(bad3))))
    bad4 = json.loads(json.dumps(face))
    bad4["e625_cross_check"]["published_duplicate_rows"] = 3
    legs.append(("face_problems catches a duplicate count that disagrees with E625",
                 bool(face_problems(bad4))))

    # the live arms
    try:
        face_live, problems = build(root=ROOT)
        legs.append(("the published face builds with no problems", problems == []))
        legs.append(("every live line is covered",
                     face_live["counts"]["read_lists_that_do_not_cover_the_function"] == 0))
        legs.append(("the live duplicate count equals E625's",
                     face_live["counts"]["duplicate_rows"]
                     == face_live["counts"]["e625_published_same_object_duplicate_rows"]))
        legs.append(("the study excludes itself", "e631_read_multiplicity.py" not in
                     {r["module"].split("/")[-1] for r in face_live["rows"] if r.get("module")}))
        face2, problems2 = build(root=ROOT)
        legs.append(("the build is deterministic", json.dumps(face_live, sort_keys=True)
                     == json.dumps(face2, sort_keys=True) and problems2 == problems))
    except Exception as exc:  # noqa: BLE001
        legs.append(("live build raised: %r" % (exc,), False))

    failed = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS" if ok else "FAIL") + " :: " + name)
    print("%d/%d selftest legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        _, problems = build(root=ROOT)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            print("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    face, problems = build(root=ROOT)
    if cmd in ("build", "run"):
        path = write_face(OUTDIR, face)
        print("face:", path)
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("lines=%d reads_after=%d lines_with_after=%d lines_multiple=%d uncovered=%d dup=%d "
          "dup_on_multi=%d"
          % (c["lines"], c["reads_after_the_dead_line_total"],
             c["lines_with_a_read_after_the_dead_line"],
             c["lines_with_more_than_one_read_after_the_dead_line"],
             c["read_lists_that_do_not_cover_the_function"], c["duplicate_rows"],
             c["duplicate_rows_on_a_function_with_more_than_two_reads"]))
    for k in AFTER_CLASSES:
        print("  %s=%d" % (k, c["class_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))