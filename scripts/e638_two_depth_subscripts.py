"""E638 -- the two rulers on one expression, counted tree-wide instead of as one example.

E633 classifies an access of a counted line's receiver by *depth*: anything reached through two or
more subscripts is ``read_below_the_receiver`` and is published as "does not read this key".  E636
separately reports "a read of the counted key one level below the receiver" at the same
``(line, column)``.  Both can be right because a chained expression is *two AST nodes in one place*:

    sleeves[tid]["x1"]
    ^^^^^^^^^^^^^^^^  Subscript, depth 2, key "x1", col_offset = 8
    ^^^^^^^^^^^^      Subscript, depth 1, key tid-as-expression, col_offset = 8

E637 settled that on its own population.  This study asks the larger question E637 left as a
definition gap: how many ``(line, column)`` sites in the tree's Python corpus carry two Subscript
nodes at different depths at all, and on E633's counted read lines which member does each ruler
count.  Outcomes are kept apart because they are different claims about the code:

  * a deepest member that names the row's counted key  -> E633 folds out a same-key read (undercount)
  * both members counted by E633                       -> the rulers agree, drawn at different depths
  * no two-depth site on any counted line              -> the form lives off the counted population

Usage:
  python scripts/e638_two_depth_subscripts.py run       # build the face
  python scripts/e638_two_depth_subscripts.py verify    # re-derive the counts from the face's rows
  python scripts/e638_two_depth_subscripts.py check     # build + both gates in one pass
  python scripts/e638_two_depth_subscripts.py selftest  # offline fixture legs
"""
from __future__ import annotations

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
FACE = "TWODEPTHSUBS.json"
LATEST = "twodepthsubs_latest.json"
STUDY = "E638_two_depth_subscripts"
SELF_PARTS = ("e638_", "run_e638_", "_probe_e638", "_r1658")
SOURCE_FACE = "results/state_tilt/READFORMGAP.json"
MAX_BYTES = 1024 * 1024
MAX_EXAMPLES = 25

import e391_key_name_two_meanings as e391  # noqa: E402
import e633_read_forms as e633  # noqa: E402

R_KEY = e633.R_KEY
R_BELOW = e633.R_BELOW

V_READ_IS_FOLDED = (
    "two_Subscripts_at_different_depths_share_a_line_and_column_in_the_corpus_and_on_the_counted_"
    "read_lines_the_deepest_member_names_the_row's_counted_key_while_E633_publishes_it_as_read_"
    "below_the_receiver,_so_the_same_key_count_undercounts_on_those_lines")
V_RULERS_COINCIDE = (
    "the_two_depth_form_is_ordinary_in_the_corpus_and_on_the_counted_lines_E633_counts_the_deepest_"
    "member_as_a_recognised_read_at_those_sites,_so_the_two_rulers_are_the_same_expression_seen_at_"
    "two_depths_and_neither_lost_a_read")
V_FOLDED_OTHER_KEY = (
    "the_two_depth_form_is_ordinary_in_the_corpus_and_on_the_counted_lines_E633_folds_the_deepest_"
    "member_every_time_while_none_of_those_members_names_the_row's_counted_key,_so_the_fold_removes_"
    "no_same_key_read_and_the_line_level_coincidence_E637_reported_is_not_a_column_level_double_count")
V_OFF_POPULATION = (
    "the_two_depth_form_exists_in_the_corpus_but_no_counted_read_line_carries_one,_so_the_depth_"
    "argument_is_settled_off_the_population_that_E632_and_E633_count")
V_ABSENT = (
    "no_line_column_site_in_the_corpus_carries_two_Subscripts_at_different_depths,_so_the_two_"
    "rulers_cannot_disagree_about_one_expression_at_all")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    """The same Python corpus E391 walks, minus this study's own files and scratch patchers.

    The exclusion is by basename prefix, not by a fixed list: a census that counts its own
    scratch files publishes a number that moves whenever a neighbour writes a file (E180/E207).
    """
    out = []
    for p in e391.py_corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def subscript_depth(node):
    """Depth of a Subscript counted from its leftmost name, E633's own depth rule."""
    _, d = e633.base_of(node.value)
    return d + 1


def file_sites(path):
    """Two-depth sites of one file as (payload, None), or (None, why) when it cannot be measured.

    The reason is carried rather than folded into one "unreadable" count: "too big to parse",
    "cannot be read" and "does not parse" are three different holes in the population.
    """
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None, "over_the_size_cap"
        src = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None, "unreadable"
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None, "does_not_parse"
    groups = {}
    n_subscript = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        n_subscript += 1
        key = e633.const_str(node.slice)
        at = (node.lineno, node.col_offset)
        groups.setdefault(at, []).append({
            "depth": subscript_depth(node),
            "key": key,
            "ctx": ("store" if isinstance(node.ctx, ast.Store)
                    else "del" if isinstance(node.ctx, ast.Del) else "load"),
        })
    sites = []
    for (line, col) in sorted(groups):
        members = groups[(line, col)]
        depths = sorted({m["depth"] for m in members})
        if len(members) < 2 or len(depths) < 2:
            continue
        inner = next((m for m in members if m["depth"] == depths[0]), None)
        outer = next((m for m in members if m["depth"] == depths[-1]), None)
        sites.append({
            "line": line,
            "column": col,
            "members": members,
            "min_depth": depths[0],
            "max_depth": depths[-1],
            "depth_pair": "%d->%d" % (depths[0], depths[-1]),
            "inner_key": inner.get("key") if inner else None,
            "outer_key": outer.get("key") if outer else None,
        })
    return {"subscript_nodes": n_subscript, "sites": sites}, None


def measure(root=ROOT):
    """Census the corpus, then join the sites to E633's counted read lines."""
    files = corpus(root)
    unreadable = 0
    file_rows = []
    examples = []
    totals = {"subscript_nodes": 0, "sites": 0}
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    for p in files:
        got, why = file_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        totals["subscript_nodes"] += got["subscript_nodes"]
        if not got["sites"]:
            continue
        pairs = {}
        for s in got["sites"]:
            pairs[s["depth_pair"]] = pairs.get(s["depth_pair"], 0) + 1
        file_rows.append({
            "module": rel(p, root),
            "two_depth_sites": len(got["sites"]),
            "depth_pairs": pairs,
        })
        totals["sites"] += len(got["sites"])
    file_rows.sort(key=lambda r: (-r["two_depth_sites"], r["module"]))
    for fr in file_rows[:12]:
        got, _why = file_sites(os.path.join(root, fr["module"]))
        for s in (got or {}).get("sites", [])[:2]:
            examples.append({"module": fr["module"], "line": s["line"],
                             "column": s["column"], "depth_pair": s["depth_pair"],
                             "inner_key": s["inner_key"], "outer_key": s["outer_key"]})
    examples = examples[:MAX_EXAMPLES]

    joined = join_counted_lines(root, file_rows)
    counts = counts_of(file_rows, joined, len(files), holes,
                       totals["subscript_nodes"])
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every .py in the corpus E391 walks, group its Subscript nodes by "
                   "(lineno, col_offset) -- a chained expression is one column and several nodes "
                   "-- keep the groups whose members sit at two or more depths, then join those "
                   "sites to E633's counted read lines by (module, line) and ask which member each "
                   "ruler counts"),
        "population_source": ("%d Python files of the tree corpus, joined to the %d counted read "
                              "line(s) E633 publishes in %s"
                              % (len(files), len(joined), SOURCE_FACE)),
        "counts": counts,
        "rows": joined,
        "file_rows": file_rows,
        "examples": examples,
        "limits": [
            "a site is identified by (module, lineno, col_offset) only: two physically different "
            "expressions that start at the same column of the same line are one site here, exactly "
            "as they are one entry in E636's chained-subscript note",
            "depth is measured from the leftmost name of the expression (E633's rule); an "
            "expression whose base is a call or an attribute chain is measured through it",
            "the join to E633 is (module, line) level, so a counted line with two receivers shares "
            "this study's site list; the count of such lines is published and is zero today",
            "files over 1MB are skipped rather than parsed (E391's own cap) and are counted",
            "a computed key is published as naming nothing, never as naming a different key",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def join_counted_lines(root=ROOT, file_rows=None):
    """One row per E633 counted read line, with the two-depth sites on that line."""
    f633 = e633.measure(root)
    out = []
    for r in f633.get("rows") or []:
        module = (r.get("module") or "").replace("\\", "/")
        line = r.get("read_line")
        key = r.get("key")
        sites = []
        # the examples list is truncated in the face, so the join re-reads the file
        got, _why = file_sites(os.path.join(root, module)) if module else (None, None)
        if got:
            for s in got["sites"]:
                if s["line"] != line:
                    continue
                recognised = [a for a in (r.get("accesses") or [])
                              if a.get("form") == R_KEY and a.get("column") == s["column"]
                              and a.get("depth") == s["max_depth"]]
                folded = [a for a in (r.get("accesses") or [])
                          if a.get("form") == R_BELOW and a.get("column") == s["column"]
                          and a.get("depth") == s["max_depth"]]
                sites.append({
                    "line": s["line"],
                    "column": s["column"],
                    "depth_pair": s["depth_pair"],
                    "inner_key": s["inner_key"],
                    "outer_key": s["outer_key"],
                    "members": s["members"],
                    "outer_names_the_row_key": bool(s["outer_key"] is not None
                                                    and s["outer_key"] == key),
                    "inner_names_the_row_key": bool(s["inner_key"] is not None
                                                    and s["inner_key"] == key),
                    "e633_counts_the_deepest_member": bool(recognised),
                    "e633_folds_the_deepest_member": bool(folded),
                })
        out.append({
            "module": module,
            "function": r.get("function"),
            "read_line": line,
            "key": key,
            "receiver": r.get("receiver"),
            "two_depth_sites": sites,
        })
    out.sort(key=lambda x: (x["module"] or "", x["read_line"] or 0, x["key"] or ""))
    return out


def counts_of(file_rows, rows, files_scanned=0, holes=None, subscript_nodes=0):
    holes = holes or {}
    pairs = {}
    for f in file_rows:
        for pair, n in (f.get("depth_pairs") or {}).items():
            pairs[pair] = pairs.get(pair, 0) + n
    sites = [s for r in rows for s in r["two_depth_sites"]]
    modules_in_join = {r["module"] for r in rows}
    modules_not_in_census = sorted(m for m in modules_in_join
                                  if m not in {f["module"] for f in file_rows})
    return {
        "python_files_scanned": files_scanned,
        "python_files_over_the_size_cap": int(holes.get("over_the_size_cap") or 0),
        "python_files_unreadable": int(holes.get("unreadable") or 0),
        "python_files_that_do_not_parse": int(holes.get("does_not_parse") or 0),
        "subscript_nodes_in_the_corpus": subscript_nodes,
        "files_carrying_a_two_depth_site": len(file_rows),
        "two_depth_sites": sum(f["two_depth_sites"] for f in file_rows),
        "depth_pair_histogram": dict(sorted(pairs.items())),
        "counted_read_lines": len(rows),
        "counted_lines_carrying_a_two_depth_site": sum(1 for r in rows if r["two_depth_sites"]),
        "two_depth_sites_on_counted_lines": len(sites),
        "counted_lines_where_the_deepest_member_names_the_row_key": sum(
            1 for r in rows if any(s["outer_names_the_row_key"] for s in r["two_depth_sites"])),
        "counted_lines_where_the_depth_1_member_names_the_row_key": sum(
            1 for r in rows if any(s["inner_names_the_row_key"] for s in r["two_depth_sites"])),
        "counted_sites_e633_folds_the_deepest_member": sum(
            1 for s in sites if s["e633_folds_the_deepest_member"]),
        "counted_sites_e633_counts_the_deepest_member": sum(
            1 for s in sites if s["e633_counts_the_deepest_member"]),
        "counted_lines_with_no_census_row": len(modules_not_in_census),
    }


def decide(c):
    if not c.get("two_depth_sites"):
        return V_ABSENT
    if not c.get("counted_read_lines"):
        return V_OFF_POPULATION
    if not c.get("counted_lines_carrying_a_two_depth_site"):
        return V_OFF_POPULATION
    if c.get("counted_lines_where_the_deepest_member_names_the_row_key"):
        return V_READ_IS_FOLDED
    if c.get("counted_sites_e633_counts_the_deepest_member"):
        return V_RULERS_COINCIDE
    return V_FOLDED_OTHER_KEY


def answer_of(c):
    return ("%d two-depth (line, column) site(s) in %d of %d Python file(s), depth pairs %s; "
            "E633's %d counted read line(s): %d carry one, %d with the deepest member naming the "
            "row's counted key, %d with E633 counting that member and %d folding it"
            % (c.get("two_depth_sites"), c.get("files_carrying_a_two_depth_site"),
               c.get("python_files_scanned"),
               json.dumps(c.get("depth_pair_histogram") or {}, sort_keys=True),
               c.get("counted_read_lines"), c.get("counted_lines_carrying_a_two_depth_site"),
               c.get("counted_lines_where_the_deepest_member_names_the_row_key"),
               c.get("counted_sites_e633_counts_the_deepest_member"),
               c.get("counted_sites_e633_folds_the_deepest_member")))


def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "counts": m["counts"],
        "rows": m["rows"],
        "file_rows": m["file_rows"],
        "examples": m["examples"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    files = face.get("file_rows") or []
    c = face.get("counts") or {}
    live = counts_of(files, rows, c.get("python_files_scanned"),
                     {"over_the_size_cap": c.get("python_files_over_the_size_cap"),
                      "unreadable": c.get("python_files_unreadable"),
                      "does_not_parse": c.get("python_files_that_do_not_parse")},
                     c.get("subscript_nodes_in_the_corpus"))
    for key in ("files_carrying_a_two_depth_site", "two_depth_sites", "depth_pair_histogram",
                "python_files_unreadable", "python_files_over_the_size_cap",
                "python_files_that_do_not_parse",
                "counted_read_lines", "counted_lines_carrying_a_two_depth_site",
                "two_depth_sites_on_counted_lines",
                "counted_lines_where_the_deepest_member_names_the_row_key",
                "counted_lines_where_the_depth_1_member_names_the_row_key",
                "counted_sites_e633_folds_the_deepest_member",
                "counted_sites_e633_counts_the_deepest_member"):
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for f in files:
        if f.get("two_depth_sites", 0) < 1:
            problems.append("file row %s is published with no site" % f.get("module"))
            break
        if sum((f.get("depth_pairs") or {}).values()) != f.get("two_depth_sites"):
            problems.append("file row %s has a depth histogram that is not its site count"
                            % f.get("module"))
            break
    for r in rows:
        if r.get("two_depth_sites") and not r.get("module"):
            problems.append("a counted row carries sites but no module")
            break
        for s in r.get("two_depth_sites") or []:
            if s.get("inner_names_the_row_key") and s.get("outer_names_the_row_key") \
                    and s.get("inner_key") != s.get("outer_key"):
                problems.append("a site claims both members name the row key with different keys")
                break
    if face.get("verdict") == V_READ_IS_FOLDED \
            and c.get("counted_lines_where_the_deepest_member_names_the_row_key", 0) == 0:
        problems.append("the verdict reports a folded same-key read the rows do not carry")
    if face.get("verdict") == V_RULERS_COINCIDE \
            and c.get("counted_sites_e633_counts_the_deepest_member", 0) == 0:
        problems.append("the verdict has E633 counting a member that no site counts")
    if face.get("verdict") == V_FOLDED_OTHER_KEY \
            and (c.get("counted_lines_where_the_deepest_member_names_the_row_key", 0)
                 or c.get("counted_sites_e633_counts_the_deepest_member", 0)):
        problems.append("the verdict says the fold removes no same-key read while a count says it does")
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
    say("run: files=%d sites=%d files_with_sites=%d counted_lines=%d counted_with_site=%d "
        "depth2_names_key=%d both=%d folded=%d"
        % (c["python_files_scanned"], c["two_depth_sites"], c["files_carrying_a_two_depth_site"],
           c["counted_read_lines"], c["counted_lines_carrying_a_two_depth_site"],
           c["counted_lines_where_the_deepest_member_names_the_row_key"],
           c["counted_sites_e633_counts_the_deepest_member"],
           c["counted_sites_e633_folds_the_deepest_member"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_FILES = [
    {"module": "a.py", "subscript_nodes": 3, "two_depth_sites": 1,
     "depth_pairs": {"1->2": 1},
     "examples": [{"line": 10, "column": 4, "depth_pair": "1->2", "inner_key": None,
                   "outer_key": "x1"}]},
    {"module": "b.py", "subscript_nodes": 5, "two_depth_sites": 2,
     "depth_pairs": {"1->3": 1, "1->2": 1},
     "examples": []},
]

FIXTURE_ROWS = [
    {"module": "a.py", "function": "f", "read_line": 10, "key": "x1", "receiver": "sleeves",
     "two_depth_sites": [{"line": 10, "column": 4, "depth_pair": "1->2", "inner_key": None,
                          "outer_key": "x1", "members": [], "outer_names_the_row_key": True,
                          "inner_names_the_row_key": False,
                          "e633_counts_the_deepest_member": False,
                          "e633_folds_the_deepest_member": True}]},
    {"module": "b.py", "function": "g", "read_line": 20, "key": "days", "receiver": "P",
     "two_depth_sites": []},
]

FIXTURE_COINCIDE = [
    {"module": "a.py", "function": "f", "read_line": 10, "key": "x1", "receiver": "sleeves",
     "two_depth_sites": [{"line": 10, "column": 4, "depth_pair": "1->2", "inner_key": None,
                          "outer_key": "y", "members": [], "outer_names_the_row_key": False,
                          "inner_names_the_row_key": False,
                          "e633_counts_the_deepest_member": True,
                          "e633_folds_the_deepest_member": True}]},
]


FIXTURE_FOLD_OTHER = [
    {"module": "a.py", "function": "f", "read_line": 10, "key": "x1", "receiver": "sleeves",
     "two_depth_sites": [{"line": 10, "column": 4, "depth_pair": "1->2", "inner_key": None,
                          "outer_key": "y", "members": [], "outer_names_the_row_key": False,
                          "inner_names_the_row_key": False,
                          "e633_counts_the_deepest_member": False,
                          "e633_folds_the_deepest_member": True}]},
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

    def chained_expression_is_one_site():
        tree = ast.parse('v = sleeves[tid]["x1"]\n')
        groups = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                groups.setdefault((node.lineno, node.col_offset), []).append(
                    subscript_depth(node))
        assert len(groups) == 1, groups
        (at, depths), = groups.items()
        assert sorted(depths) == [1, 2], depths

    def siblings_on_one_line_are_not_one_site():
        tree = ast.parse('v = a["k"] + a["j"]\n')
        cols = {n.col_offset for n in ast.walk(tree) if isinstance(n, ast.Subscript)}
        assert len(cols) == 2, cols

    def counts_add_up():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8)
        assert c["files_carrying_a_two_depth_site"] == 2, c
        assert c["two_depth_sites"] == 3, c
        assert c["depth_pair_histogram"] == {"1->2": 2, "1->3": 1}, c["depth_pair_histogram"]
        assert c["counted_read_lines"] == 2, c
        assert c["counted_lines_carrying_a_two_depth_site"] == 1, c
        assert c["two_depth_sites_on_counted_lines"] == 1, c

    def folded_read_names_the_key():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8)
        assert c["counted_lines_where_the_deepest_member_names_the_row_key"] == 1, c
        assert c["counted_sites_e633_folds_the_deepest_member"] == 1, c
        assert decide(c) == V_READ_IS_FOLDED

    def coincidence_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_COINCIDE, 2, 0, 8)
        assert c["counted_lines_where_the_deepest_member_names_the_row_key"] == 0, c
        assert c["counted_sites_e633_counts_the_deepest_member"] == 1, c
        assert decide(c) == V_RULERS_COINCIDE

    def fold_of_another_key_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_FOLD_OTHER, 2, 0, 8)
        assert c["counted_lines_where_the_deepest_member_names_the_row_key"] == 0, c
        assert c["counted_sites_e633_folds_the_deepest_member"] == 1, c
        assert decide(c) == V_FOLDED_OTHER_KEY

    def off_population_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROWS[1:], 2, 0, 8)
        assert decide(c) == V_OFF_POPULATION

    def absent_is_reachable():
        c = counts_of([], FIXTURE_ROWS, 2, 0, 0)
        assert decide(c) == V_ABSENT

    def face_problems_accepts_a_sound_face():
        face = {"file_rows": FIXTURE_FILES, "rows": FIXTURE_ROWS,
                "counts": counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8),
                "verdict": decide(counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8))}
        assert not face_problems(face), face_problems(face)

    def face_problems_catches_a_wrong_verdict():
        face = {"file_rows": FIXTURE_FILES, "rows": FIXTURE_ROWS,
                "counts": counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8),
                "verdict": V_RULERS_COINCIDE}
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_bad_file_histogram():
        bad = [dict(FIXTURE_FILES[0], depth_pairs={"1->9": 1})]
        face = {"file_rows": bad, "rows": FIXTURE_ROWS,
                "counts": counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8),
                "verdict": V_RULERS_COINCIDE}
        assert any("histogram" in p for p in face_problems(face)), face_problems(face)

    def answer_names_the_numbers():
        a = answer_of(counts_of(FIXTURE_FILES, FIXTURE_ROWS, 2, 0, 8))
        assert "3 two-depth" in a and "x1" not in a, a

    for name, fn in [
        ("chained_expression_is_one_site", chained_expression_is_one_site),
        ("siblings_on_one_line_are_not_one_site", siblings_on_one_line_are_not_one_site),
        ("counts_add_up", counts_add_up),
        ("folded_read_names_the_key", folded_read_names_the_key),
        ("coincidence_is_reachable", coincidence_is_reachable),
        ("fold_of_another_key_is_reachable", fold_of_another_key_is_reachable),
        ("off_population_is_reachable", off_population_is_reachable),
        ("absent_is_reachable", absent_is_reachable),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_bad_file_histogram",
         face_problems_catches_a_bad_file_histogram),
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