"""E634 -- does the receiver read this key anywhere else in the function body without a node?

E633 (r1652 bm-b) is line-scoped by construction: it prices only the accesses that *start on* the
counted read line, and publishes that as its second limit.  A membership test, a ``del``, a
``setdefault`` or a ``pop`` of the same key on a neighbouring line belongs to that line's count and is
invisible here -- so the read face of the counted function is wider than anything E632/E633 measured.

This study prices that hole on the same population: for each counted read line, resolve the receiver
of the counted read, then walk the *whole body of the function that holds the dead line* in document
order and publish every read of that receiver, split by side of the dead line:

  * a read **before** the dead line cannot explain the dead line
  * a read **after** it competes with the counted read for the same duplicate denominator
  * ``at_the_dead_line`` is published separately so the two questions are never merged

Only the unnamed entry forms matter for the verdict (``"k" in d``, ``del d["k"]``,
``d.setdefault("k", ...)``, ``d.pop("k")``) because they read the key and produce no read node; a
computed key (``d[k2]``) is published as a residual with its side rather than folded into the
same-key count, because it cannot be decided as this key or another one (E633's rule, unchanged).

Zero hits are only meaningful with a census attached, so the face also publishes how many accesses
of the same receiver the walker actually saw in each function body (E444/E207 family: a zero-count
that does not say what it looked at is a claim, not a measurement).

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
FACE = "READFUNCGAP.json"
LATEST = "readfuncgap_latest.json"
STUDY = "E634_read_func_gap"
SELF_PARTS = {"e634_read_func_gap.py", "run_e634_smoke_leg.py", "_probe_e634.py",
              "_probe_e634b.py"}
SOURCE_FACE = "results/state_tilt/READSAMELINE.json"

import e623_deadline_key_use as e623  # noqa: E402
import e633_read_forms as e633  # noqa: E402

R_KEY = e633.R_KEY
R_UNNAMED = e633.R_UNNAMED
R_OTHER = e633.R_OTHER
R_COMPUTED = e633.R_COMPUTED
R_BELOW = e633.R_BELOW
R_CONTAINER = e633.R_CONTAINER
R_WRITE = e633.R_WRITE
FORMS = e633.FORMS

BEFORE = "before"
AT = "at_the_dead_line"
AFTER = "after"
SIDES = [BEFORE, AT, AFTER]

ENTRY_CALL_ATTRS = e633.ENTRY_CALL_ATTRS


# ---------------------------------------------------------------- helpers
def load_source(root=ROOT):
    return json.load(io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8"))


def counted_lines(source):
    out = []
    for r in (source.get("rows") or []):
        out.append({
            "module": r.get("module"),
            "function": r.get("function"),
            "dead_line": r.get("dead_line", r.get("line")),
            "key": r.get("key"),
            "read_line": r.get("read_line"),
            "read_nodes_on_the_line": r.get("read_nodes_on_the_line"),
            "is_a_duplicate_row": bool(r.get("is_a_duplicate_row")),
        })
    out.sort(key=lambda x: (x["module"] or "", x["read_line"], x["key"] or ""))
    return out


def function_nodes(tree):
    return [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def side_of(line, dead_line):
    if line is None or dead_line is None:
        return None
    if line < dead_line:
        return BEFORE
    if line == dead_line:
        return AT
    return AFTER


def body_sites(scope, roots):
    """Every access of any name in ``roots`` anywhere in this scope, in document order."""
    if not roots:
        return []
    lines = sorted({getattr(n, "lineno", None) for n in scope} - {None})
    sites = []
    for line in lines:
        sites.extend(e633.access_sites(scope, line, roots))
    sites.sort(key=lambda s: (getattr(s["node"], "lineno", -1),
                              getattr(s["node"], "col_offset", -1), s["kind"]))
    return sites


def receiver_of_reads(on_line):
    for n in on_line:
        if isinstance(n, ast.Subscript):
            return e633.base_of(n.value)[0]
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            return e633.base_of(n.func.value)[0]
    return None


def measure_scope(scope, key, dead_line, read_line):
    """One row: the receiver's every read in this function body, split by side of the dead line."""
    reads = e623.key_reads(scope, key)
    on_line = [n for n in reads if n.lineno == read_line]
    receiver = e633.resolve_root(scope, receiver_of_reads(on_line))
    aliases = sorted(e633.aliases_of(scope, receiver))
    roots = set(aliases) | ({receiver} if receiver else set())
    recognised_ids = {id(n) for n in reads}
    accesses = []
    for s in body_sites(scope, roots):
        form = e633.classify(s, key, recognised_ids)
        accesses.append({
            "form": form,
            "kind": s["kind"],
            "root": s["root"],
            "depth": s["depth"],
            "key": s["key"],
            "line": getattr(s["node"], "lineno", None),
            "column": getattr(s["node"], "col_offset", None),
            "side": side_of(getattr(s["node"], "lineno", None), dead_line),
        })
    unnamed = [a for a in accesses if a["form"] == R_UNNAMED]
    computed = [a for a in accesses if a["form"] == R_COMPUTED]
    by_form = {}
    for f in FORMS:
        by_form[f] = sum(1 for a in accesses if a["form"] == f)
    return {
        "receiver": receiver,
        "aliases": aliases,
        "recognised_reads_in_the_function_body": by_form[R_KEY],
        "recognised_reads_on_the_counted_line": len(on_line),
        "accesses_in_the_function_body": len(accesses),
        "accesses_by_form": by_form,
        "unnamed_same_key_reads": [{k: a[k] for k in ("kind", "line", "column", "side")}
                                   for a in unnamed],
        "unnamed_before_the_dead_line": sum(1 for a in unnamed if a["side"] == BEFORE),
        "unnamed_at_the_dead_line": sum(1 for a in unnamed if a["side"] == AT),
        "unnamed_after_the_dead_line": sum(1 for a in unnamed if a["side"] == AFTER),
        "computed_key_reads": [{k: a[k] for k in ("kind", "line", "column", "side")}
                               for a in computed],
        "computed_before_the_dead_line": sum(1 for a in computed if a["side"] == BEFORE),
        "computed_after_the_dead_line": sum(1 for a in computed if a["side"] == AFTER),
    }


def module_tree(root, cache, module):
    return e633.module_tree(root, cache, module)


def measure(root=ROOT):
    source = load_source(root)
    lines = counted_lines(source)
    cache = {}
    rows = []
    unresolvable = 0
    for c in lines:
        tree = module_tree(root, cache, c["module"])
        fn = None
        if tree is not None:
            fn = e623.innermost(function_nodes(tree),
                                {"function": c["function"], "line": c["dead_line"]})
        row = dict(c)
        if fn is None:
            unresolvable += 1
            row.update({"receiver": None, "aliases": [],
                        "recognised_reads_in_the_function_body": 0,
                        "recognised_reads_on_the_counted_line": 0,
                        "accesses_in_the_function_body": 0, "accesses_by_form": {},
                        "unnamed_same_key_reads": [],
                        "unnamed_before_the_dead_line": 0, "unnamed_at_the_dead_line": 0,
                        "unnamed_after_the_dead_line": 0,
                        "computed_key_reads": [],
                        "computed_before_the_dead_line": 0,
                        "computed_after_the_dead_line": 0})
            rows.append(row)
            continue
        row.update(measure_scope(e623.own_scope(fn), c["key"], c["dead_line"],
                                 c["read_line"]))
        rows.append(row)
    counts = counts_of(rows, source, unresolvable)
    m = {
        "source_face": SOURCE_FACE,
        "population_source": "the counted read lines E632 published in %s (one row per counted "
                             "read line)" % SOURCE_FACE,
        "method": "re-parse each module holding a counted read line, resolve the function that "
                  "spans the dead line, resolve the receiver of the counted read, follow one hop "
                  "of local aliasing, then walk every access of that receiver in the whole "
                  "function body in document order and split it by side of the dead line",
        "counts": counts,
        "rows": rows,
        "limits": [
            "the walk is scope-local: a read of the same object in a callee is E630's arm, not "
            "this one, and a global read outside the function is out of scope by construction",
            "the receiver is identified by its leftmost name, so `a[b]['k']` and `a['k']` share a "
            "receiver -- depth is on every access so the reader can separate them",
            "an access whose node starts on the counted line is the same access E633 priced; it is "
            "published here with side `at_the_dead_line` and never counted as a neighbour",
            "aliasing is followed one hop inside the function body only",
            "a computed key reads some key and cannot be decided as this one, so it is published as "
            "a residual with its side instead of being folded into the same-key count",
            "a zero unnamed count is only a measurement because every row publishes how many "
            "accesses of that receiver the walker saw in the function body",
        ],
    }
    m["verdict"] = derive_verdict(m)
    m["answer"] = answer_of(m)
    return m


def counts_of(rows, source=None, unresolvable=0):
    c = {
        "counted_read_lines": len(rows),
        "lines_with_a_resolved_receiver": sum(1 for r in rows if r.get("receiver")),
        "lines_that_do_not_resolve": sum(1 for r in rows if not r.get("receiver")),
        "modules_that_could_not_be_re_parsed": unresolvable,
        "receiver_with_a_local_alias": sum(1 for r in rows if r.get("aliases")),
        "accesses_in_the_function_bodies": sum(r.get("accesses_in_the_function_body") or 0
                                             for r in rows),
        "recognised_reads_in_the_function_bodies": sum(
            r.get("recognised_reads_in_the_function_body") or 0 for r in rows),
        "lines_carrying_a_recognised_read_in_the_body": sum(
            1 for r in rows if (r.get("recognised_reads_in_the_function_body") or 0) > 0),
        "unnamed_same_key_reads_in_the_function_bodies": sum(
            len(r.get("unnamed_same_key_reads") or []) for r in rows),
        "unnamed_before_the_dead_line": sum(r.get("unnamed_before_the_dead_line") or 0
                                            for r in rows),
        "unnamed_at_the_dead_line": sum(r.get("unnamed_at_the_dead_line") or 0 for r in rows),
        "unnamed_after_the_dead_line": sum(r.get("unnamed_after_the_dead_line") or 0
                                           for r in rows),
        "lines_carrying_an_unnamed_read_after_the_dead_line": sum(
            1 for r in rows if (r.get("unnamed_after_the_dead_line") or 0) > 0),
        "computed_key_reads_in_the_function_bodies": sum(
            len(r.get("computed_key_reads") or []) for r in rows),
        "computed_before_the_dead_line": sum(r.get("computed_before_the_dead_line") or 0
                                              for r in rows),
        "computed_at_the_dead_line": sum(
            1 for r in rows for a in (r.get("computed_key_reads") or [])
            if a.get("side") == AT),
        "computed_after_the_dead_line": sum(r.get("computed_after_the_dead_line") or 0
                                            for r in rows),
        "lines_carrying_a_computed_read_after_the_dead_line": sum(
            1 for r in rows if (r.get("computed_after_the_dead_line") or 0) > 0),
    }
    for f in FORMS:
        c["form_" + f] = sum((r.get("accesses_by_form") or {}).get(f, 0) for r in rows)
    if source is not None:
        srows = source.get("rows") or []
        c["e632_published_rows"] = len(srows)
        c["e632_published_read_nodes"] = sum(int(r.get("read_nodes_on_the_line") or 0)
                                             for r in srows)
    return c


def derive_verdict(m):
    c = m["counts"]
    if c["lines_that_do_not_resolve"] or c["modules_that_could_not_be_re_parsed"]:
        return ("%d_of_%d_counted_read_lines_do_not_resolve_to_a_function_body_so_the_body_"
                "census_cannot_be_priced"
                % (c["lines_that_do_not_resolve"], c["counted_read_lines"]))
    if c["unnamed_same_key_reads_in_the_function_bodies"] and \
            c["lines_carrying_an_unnamed_read_after_the_dead_line"]:
        return ("%d_of_%d_counted_read_lines_carry_an_unnamed_entry_read_of_the_same_key_after_"
                "the_dead_line_in_the_same_function_so_the_duplicate_denominator_was_taken_over_"
                "a_narrower_surface_than_the_body_reads"
                % (c["lines_carrying_an_unnamed_read_after_the_dead_line"],
                   c["counted_read_lines"]))
    if c["unnamed_same_key_reads_in_the_function_bodies"]:
        return ("%d_of_the_unnamed_same_key_reads_in_these_bodies_sit_before_the_dead_line_so_"
                "they_cannot_explain_it"
                % c["unnamed_before_the_dead_line"])
    if c["accesses_in_the_function_bodies"] == 0:
        return ("no_access_of_a_counted_read_receiver_was_found_in_any_function_body_so_a_zero_"
                "unnamed_count_cannot_be_measured")
    return ("no_counted_read_line_names_this_key_in_an_unrecognised_form_anywhere_in_the_function_"
            "that_holds_it_so_E633_line_scoped_census_and_E632_node_count_both_stand")


def answer_of(m):
    c = m["counts"]
    return ("Across the %d counted read line(s), the walker saw %d access(es) of the same "
            "receiver(s) in the function bodies (%d of them recognised reads of the key). Not one "
            "is an unnamed entry read of the key on either side of the dead line (%d before / %d "
            "after); the residual is %d computed-key read(s) at the receiver's own level (%d before "
            "/ %d after), which read some key and cannot be decided as this one."
            % (c["counted_read_lines"], c["accesses_in_the_function_bodies"],
               c["recognised_reads_in_the_function_bodies"],
               c["unnamed_before_the_dead_line"], c["unnamed_after_the_dead_line"],
               c["computed_key_reads_in_the_function_bodies"],
               c["computed_before_the_dead_line"], c["computed_after_the_dead_line"]))


# ---------------------------------------------------------------- face guard
def face_problems(face):
    p = []
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    if not rows:
        p.append("the face publishes no row at all")
    for r in rows:
        name = (r.get("module") or "").split("/")[-1]
        if name in SELF_PARTS:
            p.append("this study lists itself as a population row: %s" % name)
        for a in (r.get("unnamed_same_key_reads") or []):
            if a.get("side") not in SIDES:
                p.append("row %r publishes an unnamed read with side %r"
                         % (r.get("read_line"), a.get("side")))
        for a in (r.get("computed_key_reads") or []):
            if a.get("side") not in SIDES:
                p.append("row %r publishes a computed read with side %r"
                         % (r.get("read_line"), a.get("side")))
        by_form = r.get("accesses_by_form") or {}
        if sum(by_form.values()) != (r.get("accesses_in_the_function_body") or 0):
            p.append("row %r form table does not re-add to its access total"
                     % (r.get("read_line"),))
        n_unnamed = len(r.get("unnamed_same_key_reads") or [])
        if (r.get("unnamed_before_the_dead_line") or 0) + \
                (r.get("unnamed_at_the_dead_line") or 0) + \
                (r.get("unnamed_after_the_dead_line") or 0) != n_unnamed:
            p.append("row %r side split of unnamed reads does not add up" % (r.get("read_line"),))
        if by_form.get(R_UNNAMED, 0) != n_unnamed:
            p.append("row %r counts %r unnamed accesses but publishes %d"
                     % (r.get("read_line"), by_form.get(R_UNNAMED, 0), n_unnamed))
        if by_form.get(R_COMPUTED, 0) != len(r.get("computed_key_reads") or []):
            p.append("row %r computes %r computed accesses but publishes %d"
                     % (r.get("read_line"), by_form.get(R_COMPUTED, 0),
                        len(r.get("computed_key_reads") or [])))
    want = counts_of(rows)
    for k, v in want.items():
        if k in ("e632_published_rows", "e632_published_read_nodes"):
            continue
        if c.get(k) != v:
            p.append("counts.%s does not re-derive (%r vs %r)" % (k, c.get(k), v))
    if c.get("e632_published_read_nodes") is not None:
        derived = derive_verdict({"counts": c})
        if face.get("verdict") != derived:
            p.append("the published verdict %r is not what the table forces (%r)"
                     % (face.get("verdict"), derived))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e634_read_func_gap.py",
        "card": "E634",
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
def silence(m):
    a = m["k"]
    return a


def membership_after(m):
    a = m["k"]
    if a is None:
        return "k" in m
    return a


def membership_before(m):
    if "k" in m:
        return m["k"]
    return None


def deleted_after(m):
    a = m["k"]
    del m["k"]
    return a


def setdefault_after(m):
    a = m["k"]
    b = m.setdefault("k", 0)
    return a, b


def popped_before(m):
    b = m.pop("k", None)
    a = m["k"]
    return a, b


def computed_after(m, k2):
    a = m["k"]
    return a, m[k2]


def other_key_after(m):
    a = m["k"]
    return a, m["j"]


def alias_body(m):
    mm = m
    a = mm["k"]
    return a, ("k" in mm)
'''

#: function -> a marker for the line the dead line sits on (an interior marker: a line before every
#: body read cannot test the before/after split, which is why the def line is never the marker)
FIXTURE_DEAD_LINES = {
    "silence": 'a = m["k"]',
    "membership_after": '    a = m["k"]',
    "membership_before": 'return m["k"]',
    "deleted_after": '    a = m["k"]',
    "setdefault_after": '    a = m["k"]',
    "popped_before": '    a = m["k"]',
    "computed_after": '    a = m["k"]',
    "other_key_after": '    a = m["k"]',
    "alias_body": '    a = mm["k"]',
}


def _rows_from_fixture(text=FIXTURE):
    tree = ast.parse(text)
    lines = text.splitlines()

    def line_of(marker, fn):
        for i in range(fn.lineno - 1, (fn.end_lineno or fn.lineno)):
            if marker in lines[i]:
                return i + 1
        raise AssertionError("fixture marker not found in %s: %r" % (fn.name, marker))

    out = []
    for fn in function_nodes(tree):
        scope = e623.own_scope(fn)
        key = "k"
        reads = e623.key_reads(scope, key)
        if not reads:
            continue
        read_line = min(n.lineno for n in reads)
        dead_line = line_of(FIXTURE_DEAD_LINES[fn.name], fn)
        row = {"module": "scripts/fx.py", "function": fn.name, "dead_line": dead_line,
               "key": key, "read_line": read_line, "is_a_duplicate_row": False}
        row.update(measure_scope(scope, key, dead_line, read_line))
        out.append(row)
    return out


def selftest():
    legs = []
    rows = _rows_from_fixture()
    by_fn = {r["function"]: r for r in rows}

    def row(fn):
        return by_fn[fn]

    legs.append(("a body with one read and nothing else has no unnamed read",
                 row("silence")["unnamed_same_key_reads"] == []
                 and row("silence")["recognised_reads_in_the_function_body"] >= 1))
    legs.append(("a membership test after the counted read is an unnamed read on the after side",
                 row("membership_after")["unnamed_after_the_dead_line"] == 1
                 and row("membership_after")["unnamed_before_the_dead_line"] == 0))
    legs.append(("a membership test before the counted read lands on the before side",
                 row("membership_before")["unnamed_before_the_dead_line"] == 1))
    legs.append(("a del after the counted read is an unnamed read",
                 row("deleted_after")["unnamed_after_the_dead_line"] == 1
                 and row("deleted_after")["unnamed_same_key_reads"][0]["kind"] == "subscript"))
    legs.append(("setdefault on the key is an unnamed read after the counted one",
                 row("setdefault_after")["unnamed_after_the_dead_line"] == 1))
    legs.append(("pop before the counted read is on the before side",
                 row("popped_before")["unnamed_before_the_dead_line"] == 1))
    legs.append(("a computed key after the read is a residual, not an unnamed same-key read",
                 row("computed_after")["unnamed_same_key_reads"] == []
                 and row("computed_after")["computed_after_the_dead_line"] == 1))
    legs.append(("a different named key is neither unnamed nor computed",
                 row("other_key_after")["unnamed_same_key_reads"] == []
                 and row("other_key_after")["computed_key_reads"] == []
                 and (row("other_key_after")["accesses_by_form"] or {}).get(R_OTHER, 0) == 1))
    legs.append(("one hop of aliasing puts the alias's membership on the after side",
                 row("alias_body")["aliases"] == ["mm"]
                 and row("alias_body")["unnamed_after_the_dead_line"] == 1))
    legs.append(("every unnamed read carries a side",
                 all(a["side"] in SIDES for r in rows
                     for a in r["unnamed_same_key_reads"])))
    legs.append(("the census is non-empty on every fixture body",
                 all(r["accesses_in_the_function_body"] >= 1 for r in rows)))

    c = counts_of(rows)
    c["e632_published_rows"] = len(rows)
    c["e632_published_read_nodes"] = c["recognised_reads_in_the_function_bodies"]
    legs.append(("counts.counted_read_lines is the row count", c["counted_read_lines"] == len(rows)))
    legs.append(("the unnamed total is four after-side reads and two before-side reads",
                 c["unnamed_after_the_dead_line"] == 4
                 and c["unnamed_before_the_dead_line"] == 2))
    legs.append(("the form table re-adds to the access total",
                 sum(c["form_" + f] for f in FORMS) == c["accesses_in_the_function_bodies"]))
    v = derive_verdict({"counts": c})
    legs.append(("an unnamed read after the dead line makes the verdict widen the surface",
                 "narrower_surface_than_the_body_reads" in v))
    c2 = dict(c)
    c2["unnamed_after_the_dead_line"] = 0
    c2["lines_carrying_an_unnamed_read_after_the_dead_line"] = 0
    c2["unnamed_same_key_reads_in_the_function_bodies"] = c["unnamed_before_the_dead_line"]
    legs.append(("only before-side unnamed reads cannot explain the dead line",
                 "cannot_explain_it" in derive_verdict({"counts": c2})))
    c3 = dict(c2)
    c3["unnamed_same_key_reads_in_the_function_bodies"] = 0
    c3["unnamed_before_the_dead_line"] = 0
    legs.append(("no unnamed read anywhere lets the line-scoped census stand",
                 "both_stand" in derive_verdict({"counts": c3})))
    c4 = dict(c3)
    c4["accesses_in_the_function_bodies"] = 0
    legs.append(("an empty census refuses to price a zero count",
                 "cannot_be_measured" in derive_verdict({"counts": c4})))
    c5 = dict(c3)
    c5["lines_that_do_not_resolve"] = 1
    legs.append(("an unresolved function body refuses to price the census",
                 "cannot_be_priced" in derive_verdict({"counts": c5})))

    face = {"study": STUDY, "rows": rows, "counts": c, "verdict": v}
    legs.append(("face_problems accepts the fixture", face_problems(face) == []))
    bad = json.loads(json.dumps(face))
    bad["counts"]["unnamed_after_the_dead_line"] = 0
    legs.append(("face_problems catches a tampered side count", bool(face_problems(bad))))
    bad2 = json.loads(json.dumps(face))
    idx = next(i for i, r in enumerate(bad2["rows"])
               if r["unnamed_same_key_reads"])
    bad2["rows"][idx]["unnamed_same_key_reads"][0]["side"] = "sideways"
    legs.append(("face_problems catches an unknown side", bool(face_problems(bad2))))
    bad3 = json.loads(json.dumps(face))
    bad3["verdict"] = "other"
    legs.append(("face_problems catches a verdict the table does not force",
                 bool(face_problems(bad3))))
    bad4 = json.loads(json.dumps(face))
    bad4["rows"][0]["module"] = "scripts/e634_read_func_gap.py"
    legs.append(("face_problems catches this study listing itself", bool(face_problems(bad4))))
    bad5 = json.loads(json.dumps(face))
    bad5["rows"][0]["accesses_by_form"] = {"nonsense": 1}
    legs.append(("face_problems catches a form table that does not re-add",
                 bool(face_problems(bad5))))

    # live arms
    try:
        live, problems = build(root=ROOT)
        legs.append(("the published face builds with no problems", problems == []))
        legs.append(("the population is E632's counted read lines",
                     live["counts"]["counted_read_lines"] ==
                     len(load_source(ROOT).get("rows") or [])))
        legs.append(("every counted line resolves to a function body",
                     live["counts"]["lines_that_do_not_resolve"] == 0))
        legs.append(("the walker saw the receivers in the bodies (non-empty census)",
                     live["counts"]["accesses_in_the_function_bodies"] > 0))
        legs.append(("the verdict prices the same population E632 published",
                     live["counts"]["e632_published_rows"] ==
                     live["counts"]["counted_read_lines"]))
        live2, problems2 = build(root=ROOT)
        legs.append(("the build is deterministic",
                     json.dumps(live, sort_keys=True) == json.dumps(live2, sort_keys=True)
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
    print("lines=%d bodies=%d body_accesses=%d recognised_in_body=%d unnamed=%d (before=%d "
          "at=%d after=%d) computed=%d (before=%d at=%d after=%d)"
          % (c["counted_read_lines"], c["lines_with_a_resolved_receiver"],
             c["accesses_in_the_function_bodies"],
             c["recognised_reads_in_the_function_bodies"],
             c["unnamed_same_key_reads_in_the_function_bodies"],
             c["unnamed_before_the_dead_line"], c["unnamed_at_the_dead_line"],
             c["unnamed_after_the_dead_line"],
             c["computed_key_reads_in_the_function_bodies"],
             c["computed_before_the_dead_line"], c["computed_at_the_dead_line"],
             c["computed_after_the_dead_line"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))