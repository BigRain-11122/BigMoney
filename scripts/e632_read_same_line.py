"""E632 -- does one physical line carry two reads of the key E631 counted once?

E631 (r1650 bm-b) publishes its own limit: it counts read sites by line number, so two reads of the
same key on one physical line (``d[k] = d[k] + 1``) read as one site.  The question it could not
answer is whether any of the read lines it counted is such a line -- and if one is, the duplicate
denominator it left standing is one short.

This study re-parses the modules that hold the counted read lines and counts read *nodes* at column
level: ``ast.lineno`` is not enough, so each node's ``col_offset`` is published beside it.  Rows are
the counted read lines themselves, not the dead lines, because the line-level claim is about them.

CLI: build (default) | check | verify | selftest
"""
import argparse
import ast
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
FACE = "READSAMELINE.json"
LATEST = "readsameline_latest.json"
STUDY = "E632_read_same_line"
SELF_PARTS = {"e632_read_same_line.py", "run_e632_smoke_leg.py", "_probe_e632.py"}
SOURCE_FACE = "results/state_tilt/READMULTIPLICITY.json"

import e623_deadline_key_use as e623  # noqa: E402

L_SINGLE = "exactly_one_read_node_on_the_line"
L_MULTI = "more_than_one_read_node_on_the_line"
L_NONE = "no_read_node_resolves_at_the_line"
LINE_CLASSES = [L_SINGLE, L_MULTI, L_NONE]


def load_source(root=ROOT):
    path = os.path.join(root, SOURCE_FACE)
    doc = json.load(io.open(path, encoding="utf-8"))
    return doc


def counted_lines(source):
    """The read lines E631 counted, flattened out of its dead-line rows."""
    out = []
    for r in (source.get("rows") or []):
        for line in (r.get("read_lines_after_the_dead_line") or []):
            out.append({
                "module": r.get("module"),
                "function": r.get("function"),
                "dead_line": r.get("line"),
                "key": r.get("key"),
                "read_line": line,
                "is_a_duplicate_row": bool(r.get("is_a_duplicate_row")),
            })
    out.sort(key=lambda x: (x["module"] or "", x["read_line"], x["key"] or ""))
    return out


def function_nodes(tree):
    return [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def module_read_nodes(root, cache, module, function, dead_line, key):
    """Read nodes of ``key`` in the function that spans ``dead_line``, or None if the module is gone."""
    if module not in cache:
        path = os.path.join(root, module)
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
            cache[module] = ast.parse(src)
        except (SyntaxError, ValueError, OSError):
            cache[module] = None
    tree = cache[module]
    if tree is None:
        return None
    fn = e623.innermost(function_nodes(tree), {"function": function, "line": dead_line})
    if fn is None:
        return None
    return e623.key_reads(e623.own_scope(fn), key)


def measure(root=ROOT):
    source = load_source(root)
    lines = counted_lines(source)
    cache = {}
    rows = []
    unresolvable = 0
    for c in lines:
        nodes = module_read_nodes(root, cache, c["module"], c["function"],
                                  c["dead_line"], c["key"])
        if nodes is None:
            unresolvable += 1
            cols = None
            hit = []
        else:
            hit = [n for n in nodes if n.lineno == c["read_line"]]
            cols = sorted({getattr(n, "col_offset", -1) for n in hit})
        if cols is None:
            cls = L_NONE
        elif len(hit) == 0:
            cls = L_NONE
        elif len(hit) == 1:
            cls = L_SINGLE
        else:
            cls = L_MULTI
        r = dict(c)
        r["read_nodes_on_the_line"] = len(hit)
        r["columns"] = cols
        r["class"] = cls
        rows.append(r)
    counts = counts_of(rows, source, unresolvable)
    m = {
        "source_face": SOURCE_FACE,
        "population_source": "the read lines E631 published in %s (one row per counted read "
                             "line, not per dead line)" % SOURCE_FACE,
        "method": "re-parse each module that holds a counted read line, resolve the function that "
                  "spans the dead line, count read nodes of the key on the counted line and publish "
                  "each node's column offset",
        "counts": counts,
        "rows": rows,
        "limits": [
            "the read-node class comes from the same classifier E623 used to build E625's list, so a "
            "read form that classifier does not recognise is invisible here as well",
            "only the lines E631 counted are re-read; a line E631 never listed cannot appear, so this "
            "study prices the denominator it was handed and not the population behind it",
            "a read inside a lambda or comprehension on the same physical line is counted as a node of "
            "that line, which is the strict reading of 'one physical line'",
            "column offsets are published so the count can be re-derived by hand; indentation-shifted "
            "files would keep node counts equal but move the columns",
        ],
    }
    m["verdict"] = derive_verdict(m)
    m["answer"] = answer_of(m)
    return m


def counts_of(rows, source=None, unresolvable=0):
    c = {
        "counted_read_lines": len(rows),
        "read_nodes_on_the_counted_lines_total": sum(r["read_nodes_on_the_line"] for r in rows),
        "lines_carrying_more_than_one_read_node": sum(1 for r in rows if r["class"] == L_MULTI),
        "lines_carrying_exactly_one_read_node": sum(1 for r in rows if r["class"] == L_SINGLE),
        "lines_that_do_not_resolve_to_a_read_node": sum(1 for r in rows if r["class"] == L_NONE),
        "modules_that_could_not_be_re_parsed": unresolvable,
        "duplicate_rows_whose_denominator_would_move": sum(
            1 for r in rows if r["is_a_duplicate_row"] and r["class"] == L_MULTI),
    }
    for k in LINE_CLASSES:
        c["class_" + k] = sum(1 for r in rows if r["class"] == k)
    if source is not None:
        c["e631_published_rows"] = len(source.get("rows") or [])
        c["e631_published_duplicate_rows"] = sum(
            1 for r in (source.get("rows") or []) if r.get("is_a_duplicate_row"))
    return c


def derive_verdict(m):
    c = m["counts"]
    if c["modules_that_could_not_be_re_parsed"] or c["lines_that_do_not_resolve_to_a_read_node"]:
        return ("%d_of_%d_counted_read_lines_do_not_resolve_to_a_read_node_so_the_node_count_cannot_"
                "be_priced" % (c["lines_that_do_not_resolve_to_a_read_node"], c["counted_read_lines"]))
    if c["lines_carrying_more_than_one_read_node"] == 0:
        return ("no_counted_read_line_carries_two_read_nodes_so_on_this_population_the_line_level_"
                "count_equals_the_node_level_count")
    return ("%d_of_%d_counted_read_lines_carry_more_than_one_read_node_so_E631_undercounts_the_read_"
            "nodes_by_%d"
            % (c["lines_carrying_more_than_one_read_node"], c["counted_read_lines"],
               c["read_nodes_on_the_counted_lines_total"] - c["counted_read_lines"]))


def answer_of(m):
    c = m["counts"]
    return ("E631 counted %d read line(s) across %d dead-line row(s); re-parsing those modules at "
            "node level finds %d read node(s) on those lines, %d line(s) carry exactly one node and %d "
            "carry more than one. %d of the %d duplicate row(s) sit on a line that would move the "
            "denominator if it carried two."
            % (c["counted_read_lines"], c["e631_published_rows"],
               c["read_nodes_on_the_counted_lines_total"],
               c["lines_carrying_exactly_one_read_node"],
               c["lines_carrying_more_than_one_read_node"],
               c["duplicate_rows_whose_denominator_would_move"],
               c["e631_published_duplicate_rows"]))


# ---------------------------------------------------------------- face guard
def face_problems(face):
    p = []
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    seen = {k: 0 for k in LINE_CLASSES}
    for r in rows:
        cls = r.get("class")
        if cls not in LINE_CLASSES:
            p.append("row %r publishes an unknown class %r" % (r.get("read_line"), cls))
            continue
        seen[cls] += 1
        n = r.get("read_nodes_on_the_line")
        if cls == L_MULTI and (not isinstance(n, int) or n < 2):
            p.append("row %r says multi with %r node(s)" % (r.get("read_line"), n))
        if cls == L_SINGLE and n != 1:
            p.append("row %r says single with %r node(s)" % (r.get("read_line"), n))
        if cls == L_NONE and n not in (0, None):
            p.append("row %r says none with %r node(s)" % (r.get("read_line"), n))
        cols = r.get("columns")
        if isinstance(cols, list):
            if len(cols) != len(set(cols)):
                p.append("row %r publishes duplicate columns" % (r.get("read_line"),))
            if cls == L_MULTI and len(cols) != n:
                p.append("row %r publishes %d column(s) for %r node(s)"
                         % (r.get("read_line"), len(cols), n))
        name = (r.get("module") or "").split("/")[-1]
        if name in SELF_PARTS:
            p.append("this study lists itself as a population row: %s" % name)
    for k in LINE_CLASSES:
        if c.get("class_" + k) != seen[k]:
            p.append("counts.class_%s does not re-derive (%r vs %d)"
                     % (k, c.get("class_" + k), seen[k]))
    if sum(seen.values()) != c.get("counted_read_lines"):
        p.append("counts.counted_read_lines=%r but %d row(s) publish a class"
                 % (c.get("counted_read_lines"), sum(seen.values())))
    want = counts_of(rows)
    for k, v in want.items():
        if c.get(k) != v:
            p.append("counts.%s does not re-derive (%r vs %r)" % (k, c.get(k), v))
    derived = derive_verdict({"counts": c})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the row table forces (%r)"
                 % (face.get("verdict"), derived))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e632_read_same_line.py",
        "card": "E632",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": m["method"],
        "population_source": m["population_source"],
        "source_face": m["source_face"],
        "counts": m["counts"],
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
FIXTURE = '''\
def solo(m):
    x = m["k"]
    return x


def twice(m):
    x = m["k"] + m["k"]
    if x:
        y = m["k"]
    return x


def spaced(m):
    a = m["k"]
    b = m["k"]
    return a + b
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    fns = function_nodes(tree)
    solo_hits = e623.key_reads(
        e623.own_scope(e623.innermost(fns, {"function": "solo", "line": 2})), "k")
    per_solo = {}
    for n in solo_hits:
        per_solo.setdefault(n.lineno, []).append(n)
    hits = e623.key_reads(e623.own_scope(e623.innermost(fns, {"function": "twice", "line": 6})), "k")
    per_line = {}
    for n in hits:
        per_line.setdefault(n.lineno, []).append(n)
    legs.append(("the fixture's single-read function holds one node on its read line",
                 len(per_solo.get(2, [])) == 1 and len(per_solo) == 1))
    legs.append(("the fixture's two-read line carries two nodes", len(per_line.get(7, [])) == 2))
    legs.append(("the two nodes on that line sit at different columns",
                 len({n.col_offset for n in per_line.get(7, [])}) == 2))
    legs.append(("a read on a later line is a separate line's node", len(per_line.get(9, [])) == 1))
    rows = [
        {"module": "scripts/fx.py", "function": "twice", "dead_line": 2, "key": "k",
         "read_line": 3, "is_a_duplicate_row": True, "read_nodes_on_the_line": 1,
         "columns": [8], "class": L_SINGLE},
        {"module": "scripts/fx.py", "function": "twice", "dead_line": 2, "key": "k",
         "read_line": 7, "is_a_duplicate_row": True, "read_nodes_on_the_line": 2,
         "columns": [8, 20], "class": L_MULTI},
        {"module": "scripts/fx.py", "function": "space", "dead_line": 2, "key": "k",
         "read_line": 14, "is_a_duplicate_row": False, "read_nodes_on_the_line": 1,
         "columns": [8], "class": L_SINGLE},
    ]
    c = counts_of(rows)
    legs.append(("counts.counted_read_lines", c["counted_read_lines"] == 3))
    legs.append(("counts.read_nodes_total", c["read_nodes_on_the_counted_lines_total"] == 4))
    legs.append(("counts.multi lines", c["lines_carrying_more_than_one_read_node"] == 1))
    legs.append(("counts.single lines", c["lines_carrying_exactly_one_read_node"] == 2))
    legs.append(("counts.duplicate rows that would move", c["duplicate_rows_whose_denominator_would_move"] == 1))
    v = derive_verdict({"counts": c})
    legs.append(("verdict names the undercount when a line carries two",
                 "undercounts_the_read_nodes_by_1" in v))
    c2 = dict(c)
    c2["lines_carrying_more_than_one_read_node"] = 0
    c2["class_" + L_MULTI] = 0
    c2["class_" + L_SINGLE] = 3
    c2["duplicate_rows_whose_denominator_would_move"] = 0
    legs.append(("verdict clears the count when every line is single",
                 "equals_the_node_level_count" in derive_verdict({"counts": c2})))
    c3 = dict(c2)
    c3["lines_that_do_not_resolve_to_a_read_node"] = 1
    legs.append(("verdict refuses to price a line that does not resolve",
                 "cannot_be_priced" in derive_verdict({"counts": c3})))

    face = {"study": STUDY, "rows": rows, "counts": c, "verdict": v}
    legs.append(("face_problems accepts the fixture", face_problems(face) == []))
    bad = json.loads(json.dumps(face))
    bad["counts"]["class_" + L_MULTI] = 0
    legs.append(("face_problems catches a tampered class count", bool(face_problems(bad))))
    bad2 = json.loads(json.dumps(face))
    bad2["rows"][1]["read_nodes_on_the_line"] = 1
    legs.append(("face_problems catches a multi row with one node", bool(face_problems(bad2))))
    bad3 = json.loads(json.dumps(face))
    bad3["rows"][1]["columns"] = [8]
    legs.append(("face_problems catches columns that do not match the node count",
                 bool(face_problems(bad3))))
    bad4 = json.loads(json.dumps(face))
    bad4["verdict"] = "other"
    legs.append(("face_problems catches a verdict the table does not force",
                 bool(face_problems(bad4))))
    bad5 = json.loads(json.dumps(face))
    bad5["rows"][0]["module"] = "scripts/e632_read_same_line.py"
    legs.append(("face_problems catches this study listing itself", bool(face_problems(bad5))))

    # the live arms
    try:
        face_live, problems = build(root=ROOT)
        legs.append(("the published face builds with no problems", problems == []))
        legs.append(("the population is the lines E631 counted",
                     face_live["counts"]["counted_read_lines"] ==
                     sum(len(r.get("read_lines_after_the_dead_line") or [])
                         for r in (load_source(ROOT).get("rows") or []))))
        legs.append(("no counted line fails to resolve",
                     face_live["counts"]["lines_that_do_not_resolve_to_a_read_node"] == 0
                     and face_live["counts"]["modules_that_could_not_be_re_parsed"] == 0))
        legs.append(("the node total is at least the line total",
                     face_live["counts"]["read_nodes_on_the_counted_lines_total"] >=
                     face_live["counts"]["counted_read_lines"]))
        face2, problems2 = build(root=ROOT)
        legs.append(("the build is deterministic",
                     json.dumps(face_live, sort_keys=True) == json.dumps(face2, sort_keys=True)
                     and problems2 == problems))
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
    print("counted_read_lines=%d nodes=%d single=%d multi=%d none=%d dup_rows_that_move=%d"
          % (c["counted_read_lines"], c["read_nodes_on_the_counted_lines_total"],
             c["lines_carrying_exactly_one_read_node"],
             c["lines_carrying_more_than_one_read_node"],
             c["lines_that_do_not_resolve_to_a_read_node"],
             c["duplicate_rows_whose_denominator_would_move"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))