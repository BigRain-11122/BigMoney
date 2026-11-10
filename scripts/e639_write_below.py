"""E639 -- can the depth fold hide a write instead of a read?

E638 published the ctx of every member of the six two-depth sites on E633's counted read lines and
all six were loads.  That is a fact about six sites, not about the form: the same fold that hides a
read one level below the receiver would hide a store or a delete there too, and E632/E633's
"does this line read the counted key" question would then be sitting next to a line that WRITES it.
This study prices the other direction on both populations:

  * corpus-wide: how many of the two-depth (line, column) sites carry a store or a delete at any
    depth, and how many carry one at the deepest member (the member that receives the value in a
    chained assignment, e.g. ``a["k"]["j"] = 1`` or ``del a["k"]["j"]``);
  * on E633's counted read lines: whether any site stores or deletes the row's counted key at
    either depth, and whether the zero (if it is a zero) is a fact about the sites or a fact about
    the corpus -- the E444 family lesson: a zero that cannot say what it counted is a claim, so the
    corpus-level write totals are published beside the counted-line zero.

Everything is re-derived from the tree; the read-only reuse of ``e638.file_sites`` (site grouping +
member ctx) and ``e638.join_counted_lines`` (the (module, line) join to E633) is intentional -- the
site definition belongs to E638 and a second copy would be free to drift.
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
FACE = "WRITEBELOW.json"
LATEST = "writebelow_latest.json"
STUDY = "E639_write_below"
SELF_PARTS = ("e639_", "run_e639_", "_probe_e639", "_r1659")
SOURCE_FACE = "results/state_tilt/TWODEPTHSUBS.json"
MAX_EXAMPLES = 25

import e391_key_name_two_meanings as e391  # noqa: E402
import e633_read_forms as e633  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402

WRITE_CTX = ("store", "del")

V_WRITE_OF_THE_ROW_KEY_BELOW = (
    "two_depth_sites_on_counted_read_lines_carry_a_store_or_delete_and_at_least_one_of_them_"
    "stores_or_deletes_the_row's_counted_key_at_one_of_its_depths,_so_the_depth_fold_can_hide_a_"
    "write_of_the_key_the_line_is_counted_for_and_the_duplicate_read_test_must_not_treat_those_"
    "lines_as_pure_reads")
V_WRITE_OF_ANOTHER_KEY_BELOW = (
    "two_depth_sites_on_counted_read_lines_do_carry_a_store_or_delete,_but_none_of_them_names_the_"
    "row's_counted_key_at_either_depth,_so_the_fold_hides_writes_in_general_and_no_write_of_a_"
    "counted_key_today")
V_COUNTED_SITES_ARE_READ_ONLY = (
    "no_two_depth_site_on_a_counted_read_line_carries_a_store_or_delete_at_any_depth_while_the_"
    "corpus_does_carry_such_sites,_so_the_zero_is_a_property_of_these_lines_not_of_the_form")
V_NO_WRITE_ANYWHERE = (
    "no_two_depth_site_on_a_counted_read_line_carries_a_store_or_delete_and_the_corpus_carries_"
    "none_either,_so_the_site_form_never_holds_a_write_and_the_question_is_moot_at_this_population")
V_OFF_POPULATION = (
    "the_two_depth_form_exists_in_the_corpus_but_no_counted_read_line_carries_one,_so_the_write_"
    "question_is_settled_off_the_population_that_E632_and_E633_count")
V_ABSENT = (
    "no_line_column_site_in_the_corpus_carries_two_Subscripts_at_different_depths,_so_no_depth_"
    "fold_exists_to_hide_a_write")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    """The Python corpus E391 walks, minus this study's own files and scratch patchers.

    Exclusion is by basename prefix (E180/E207): a census that counts its own output publishes a
    number that moves whenever a neighbour writes a file.
    """
    out = []
    for p in e391.py_corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def is_write(ctx):
    return ctx in WRITE_CTX


def site_row(s):
    """One site, with the write question answered per site and per depth."""
    members = s.get("members") or []
    deepest = s.get("max_depth")
    deep = [m for m in members if m.get("depth") == deepest]
    ctxs = sorted({m.get("ctx") for m in members})
    return {
        "line": s.get("line"),
        "column": s.get("column"),
        "depth_pair": s.get("depth_pair"),
        "inner_key": s.get("inner_key"),
        "outer_key": s.get("outer_key"),
        "members": members,
        "member_ctx": ctxs,
        "any_member_is_write": any(is_write(m.get("ctx")) for m in members),
        "deepest_member_is_write": any(is_write(m.get("ctx")) for m in deep),
    }


def measure(root=ROOT):
    files = corpus(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    file_rows = []
    examples = []
    totals = {"subscript_nodes": 0, "sites": 0}
    for p in files:
        got, why = e638.file_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        totals["subscript_nodes"] += got["subscript_nodes"]
        if not got["sites"]:
            continue
        pairs = {}
        hist = {"load": 0, "store": 0, "del": 0}
        with_write = 0
        deepest_write = 0
        for s in got["sites"]:
            pairs[s["depth_pair"]] = pairs.get(s["depth_pair"], 0) + 1
            row = site_row(s)
            for m in s["members"]:
                hist[m.get("ctx")] = hist.get(m.get("ctx"), 0) + 1
            if row["any_member_is_write"]:
                with_write += 1
            if row["deepest_member_is_write"]:
                deepest_write += 1
        file_rows.append({
            "module": rel(p, root),
            "two_depth_sites": len(got["sites"]),
            "depth_pairs": pairs,
            "member_ctx_histogram": hist,
            "sites_with_a_write_at_any_depth": with_write,
            "sites_with_a_write_at_the_deepest_member": deepest_write,
        })
    file_rows.sort(key=lambda r: (-r["two_depth_sites"], r["module"]))
    totals["sites"] = sum(f["two_depth_sites"] for f in file_rows)

    for fr in file_rows:
        if len(examples) >= MAX_EXAMPLES:
            break
        if not fr["sites_with_a_write_at_any_depth"]:
            continue
        got, _why = e638.file_sites(os.path.join(root, fr["module"]))
        for s in (got or {}).get("sites", []):
            row = site_row(s)
            if not row["any_member_is_write"]:
                continue
            examples.append({"module": fr["module"], "line": row["line"],
                             "column": row["column"], "depth_pair": row["depth_pair"],
                             "inner_key": row["inner_key"], "outer_key": row["outer_key"],
                             "members": row["members"]})
            if len([e for e in examples if e["module"] == fr["module"]]) >= 2:
                break
    examples = examples[:MAX_EXAMPLES]

    rows = join_counted_lines(root)
    counts = counts_of(file_rows, rows, len(files), holes, totals["subscript_nodes"])
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every .py in the corpus E391 walks with E638's own site grouping "
                   "(Subscript nodes sharing a (lineno, col_offset) at two or more depths), then "
                   "publish the ctx of every member and ask two questions -- corpus-wide: how many "
                   "sites carry a store or delete at any depth / at the deepest member; and on "
                   "E633's counted read lines: whether any site stores or deletes the row's counted "
                   "key at either depth"),
        "population_source": ("%d Python files of the tree corpus, joined to the %d counted read "
                              "line(s) E633 publishes (via E638's join)"
                              % (len(files), len(rows))),
        "counts": counts,
        "rows": rows,
        "file_rows": file_rows,
        "examples": examples,
        "limits": [
            "a site is E638's unit: one (module, lineno, col_offset) group, so two physically "
            "different expressions starting at the same column are one site here",
            "ctx is the AST Subscript ctx; an augmented assignment such as a['k'] += 1 is a load "
            "plus a store in the same Subscript node and is published as store by ast",
            "a computed key is published as naming nothing, never as naming a different key, so a "
            "site on a row whose key is computed can never 'name the row key'",
            "the join to E633 is (module, line) level exactly as in E638; a counted line with two "
            "receivers shares this study's site list",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted separately",
            "the exclusion list drops only this study's own files, so E638's two scripts are inside "
            "this population while E638 itself dropped them: the scanned-file and Subscript-node "
            "totals are therefore larger than E638's by exactly those files (the two-depth site "
            "totals happen to coincide, which says those files carry no such site), and this "
            "difference is published rather than reconciled away",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def join_counted_lines(root=ROOT):
    """One row per E633 counted read line, with each site's write face answered."""
    out = []
    for r in e638.join_counted_lines(root):
        key = r.get("key")
        sites = []
        for s in r.get("two_depth_sites") or []:
            members = s.get("members") or []
            depths = sorted({m.get("depth") for m in members})
            deepest = depths[-1] if depths else None
            deep = [m for m in members if m.get("depth") == deepest]
            sites.append({
                "line": s.get("line"),
                "column": s.get("column"),
                "depth_pair": s.get("depth_pair"),
                "inner_key": s.get("inner_key"),
                "outer_key": s.get("outer_key"),
                "members": members,
                "member_ctx": sorted({m.get("ctx") for m in members}),
                "any_member_is_write": any(is_write(m.get("ctx")) for m in members),
                "deepest_member_is_write": any(is_write(m.get("ctx")) for m in deep),
                "any_member_names_the_row_key": bool(
                    key is not None and any(m.get("key") == key for m in members)),
                "any_member_writes_the_row_key": bool(
                    key is not None and any(is_write(m.get("ctx")) and m.get("key") == key
                                            for m in members)),
                "deepest_member_writes_the_row_key": bool(
                    key is not None and any(is_write(m.get("ctx")) and m.get("key") == key
                                            for m in deep)),
            })
        out.append({
            "module": r.get("module"),
            "function": r.get("function"),
            "read_line": r.get("read_line"),
            "key": key,
            "key_is_computed": key is None,
            "receiver": r.get("receiver"),
            "two_depth_sites": sites,
        })
    out.sort(key=lambda x: (x["module"] or "", x["read_line"] or 0))
    return out


def counts_of(file_rows, rows, files_scanned=0, holes=None, subscript_nodes=0):
    holes = holes or {}
    pairs = {}
    hist = {"load": 0, "store": 0, "del": 0}
    any_write = 0
    deepest_write = 0
    for f in file_rows:
        for pair, n in (f.get("depth_pairs") or {}).items():
            pairs[pair] = pairs.get(pair, 0) + n
        for ctx, n in (f.get("member_ctx_histogram") or {}).items():
            hist[ctx] = hist.get(ctx, 0) + n
        any_write += f.get("sites_with_a_write_at_any_depth") or 0
        deepest_write += f.get("sites_with_a_write_at_the_deepest_member") or 0
    sites = [s for r in rows for s in r["two_depth_sites"]]
    members = [m for s in sites for m in s["members"]]
    sites_ctx = {"load": 0, "store": 0, "del": 0}
    for m in members:
        sites_ctx[m.get("ctx")] = sites_ctx.get(m.get("ctx"), 0) + 1
    modules_in_join = {r["module"] for r in rows}
    modules_in_census = {f["module"] for f in file_rows}
    return {
        "python_files_scanned": files_scanned,
        "python_files_over_the_size_cap": int(holes.get("over_the_size_cap") or 0),
        "python_files_unreadable": int(holes.get("unreadable") or 0),
        "python_files_that_do_not_parse": int(holes.get("does_not_parse") or 0),
        "subscript_nodes_in_the_corpus": subscript_nodes,
        "files_carrying_a_two_depth_site": len(file_rows),
        "two_depth_sites": sum(f["two_depth_sites"] for f in file_rows),
        "depth_pair_histogram": dict(sorted(pairs.items())),
        "corpus_member_ctx_histogram": dict(sorted(hist.items())),
        "corpus_sites_with_a_write_at_any_depth": any_write,
        "corpus_sites_with_a_write_at_the_deepest_member": deepest_write,
        "counted_read_lines": len(rows),
        "counted_lines_with_a_computed_key": sum(1 for r in rows if r.get("key_is_computed")),
        "counted_lines_carrying_a_two_depth_site": sum(1 for r in rows if r["two_depth_sites"]),
        "two_depth_sites_on_counted_lines": len(sites),
        "counted_site_member_ctx_histogram": dict(sorted(sites_ctx.items())),
        "counted_sites_with_a_write_at_any_depth": sum(1 for s in sites
                                                       if s["any_member_is_write"]),
        "counted_sites_with_a_write_at_the_deepest_member": sum(
            1 for s in sites if s["deepest_member_is_write"]),
        "counted_sites_where_a_member_names_the_row_key": sum(
            1 for s in sites if s["any_member_names_the_row_key"]),
        "counted_sites_where_a_member_writes_the_row_key": sum(
            1 for s in sites if s["any_member_writes_the_row_key"]),
        "counted_sites_where_the_deepest_member_writes_the_row_key": sum(
            1 for s in sites if s["deepest_member_writes_the_row_key"]),
        "counted_lines_where_a_site_writes_the_row_key": sum(
            1 for r in rows if any(s["any_member_writes_the_row_key"]
                                   for s in r["two_depth_sites"])),
        "counted_lines_with_no_census_row": len(modules_in_join - modules_in_census),
    }


def decide(c):
    if not c.get("two_depth_sites"):
        return V_ABSENT
    if not c.get("counted_read_lines") or not c.get("counted_lines_carrying_a_two_depth_site"):
        return V_OFF_POPULATION
    if c.get("counted_sites_where_a_member_writes_the_row_key"):
        return V_WRITE_OF_THE_ROW_KEY_BELOW
    if c.get("counted_sites_with_a_write_at_any_depth"):
        return V_WRITE_OF_ANOTHER_KEY_BELOW
    if (c.get("corpus_sites_with_a_write_at_any_depth") or 0) > 0:
        return V_COUNTED_SITES_ARE_READ_ONLY
    return V_NO_WRITE_ANYWHERE


def answer_of(c):
    return ("%d two-depth site(s) in %d file(s); corpus writes: %d site(s) with a store/delete at "
            "any depth and %d at the deepest member (member ctx %s); E633's %d counted read "
            "line(s): %d carry a site, %d site(s) carry a write at any depth, %d store/delete the "
            "row's counted key at any depth and %d at the deepest member"
            % (c.get("two_depth_sites"), c.get("files_carrying_a_two_depth_site"),
               c.get("corpus_sites_with_a_write_at_any_depth"),
               c.get("corpus_sites_with_a_write_at_the_deepest_member"),
               json.dumps(c.get("corpus_member_ctx_histogram") or {}, sort_keys=True),
               c.get("counted_read_lines"),
               c.get("counted_lines_carrying_a_two_depth_site"),
               c.get("counted_sites_with_a_write_at_any_depth"),
               c.get("counted_sites_where_a_member_writes_the_row_key"),
               c.get("counted_sites_where_the_deepest_member_writes_the_row_key")))


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
                "corpus_member_ctx_histogram",
                "corpus_sites_with_a_write_at_any_depth",
                "corpus_sites_with_a_write_at_the_deepest_member",
                "counted_read_lines", "counted_lines_with_a_computed_key",
                "counted_lines_carrying_a_two_depth_site", "two_depth_sites_on_counted_lines",
                "counted_site_member_ctx_histogram",
                "counted_sites_with_a_write_at_any_depth",
                "counted_sites_with_a_write_at_the_deepest_member",
                "counted_sites_where_a_member_names_the_row_key",
                "counted_sites_where_a_member_writes_the_row_key",
                "counted_sites_where_the_deepest_member_writes_the_row_key",
                "counted_lines_where_a_site_writes_the_row_key"):
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for f in files:
        if sum((f.get("member_ctx_histogram") or {}).values()) < 2 * f.get("two_depth_sites", 0):
            problems.append("file row %s publishes fewer member ctx slots than its sites need"
                            % f.get("module"))
            break
        if sum((f.get("depth_pairs") or {}).values()) != f.get("two_depth_sites"):
            problems.append("file row %s has a depth histogram that is not its site count"
                            % f.get("module"))
            break
        if (f.get("sites_with_a_write_at_any_depth") or 0) > f.get("two_depth_sites", 0):
            problems.append("file row %s writes at more sites than it has" % f.get("module"))
            break
        if (f.get("sites_with_a_write_at_the_deepest_member") or 0) > (
                f.get("sites_with_a_write_at_any_depth") or 0):
            problems.append("file row %s writes deeper at more sites than it writes at all"
                            % f.get("module"))
            break
    for r in rows:
        for s in r.get("two_depth_sites") or []:
            if s.get("deepest_member_writes_the_row_key") and r.get("key_is_computed"):
                problems.append("a site claims a write of the row key on a row whose key is computed")
                break
            if s.get("deepest_member_writes_the_row_key") and not s.get(
                    "any_member_writes_the_row_key"):
                problems.append("a site claims a deepest-member write without any member writing")
                break
            if s.get("any_member_writes_the_row_key") and not any(
                    is_write(m.get("ctx")) for m in (s.get("members") or [])):
                problems.append("a site claims a write while none of its members is a write")
                break
            if s.get("any_member_is_write") != any(
                    is_write(m.get("ctx")) for m in (s.get("members") or [])):
                problems.append("a site's write flag disagrees with its members")
                break
    if face.get("verdict") == V_WRITE_OF_THE_ROW_KEY_BELOW \
            and c.get("counted_sites_where_a_member_writes_the_row_key", 0) == 0:
        problems.append("the verdict reports a write of the row key the rows do not carry")
    if face.get("verdict") == V_WRITE_OF_ANOTHER_KEY_BELOW \
            and (c.get("counted_sites_with_a_write_at_any_depth", 0) == 0
                 or c.get("counted_sites_where_a_member_writes_the_row_key", 0) > 0):
        problems.append("the verdict says writes sit below without the row key while a count "
                        "says otherwise")
    if face.get("verdict") == V_COUNTED_SITES_ARE_READ_ONLY \
            and (c.get("counted_sites_with_a_write_at_any_depth", 0) > 0
                 or c.get("corpus_sites_with_a_write_at_any_depth", 0) == 0):
        problems.append("the read-only verdict is not the one its own totals force")
    if face.get("verdict") == V_NO_WRITE_ANYWHERE \
            and c.get("corpus_sites_with_a_write_at_any_depth", 0) > 0:
        problems.append("the verdict says the form never holds a write while the corpus does")
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
    say("run: files=%d sites=%d corpus_writes=%d corpus_deepest_writes=%d counted_lines=%d "
        "counted_with_site=%d counted_site_writes=%d counted_writes_row_key=%d"
        % (c["python_files_scanned"], c["two_depth_sites"],
           c["corpus_sites_with_a_write_at_any_depth"],
           c["corpus_sites_with_a_write_at_the_deepest_member"],
           c["counted_read_lines"], c["counted_lines_carrying_a_two_depth_site"],
           c["counted_sites_with_a_write_at_any_depth"],
           c["counted_sites_where_a_member_writes_the_row_key"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_FILES = [
    {"module": "a.py", "two_depth_sites": 2, "depth_pairs": {"1->2": 2},
     "member_ctx_histogram": {"load": 3, "store": 1},
     "sites_with_a_write_at_any_depth": 1,
     "sites_with_a_write_at_the_deepest_member": 1},
    {"module": "b.py", "two_depth_sites": 1, "depth_pairs": {"1->3": 1},
     "member_ctx_histogram": {"load": 2},
     "sites_with_a_write_at_any_depth": 0,
     "sites_with_a_write_at_the_deepest_member": 0},
]

FIXTURE_SITE_WRITE = [
    {"module": "a.py", "function": "f", "read_line": 10, "key": "x1", "key_is_computed": False,
     "receiver": "sleeves",
     "two_depth_sites": [{
         "line": 10, "column": 4, "depth_pair": "1->2", "inner_key": None, "outer_key": "x1",
         "members": [{"depth": 1, "key": None, "ctx": "load"},
                     {"depth": 2, "key": "x1", "ctx": "store"}],
         "member_ctx": ["load", "store"], "any_member_is_write": True,
         "deepest_member_is_write": True, "any_member_names_the_row_key": True,
         "any_member_writes_the_row_key": True, "deepest_member_writes_the_row_key": True}]},
]

FIXTURE_SITE_OTHER_KEY = [
    {"module": "a.py", "function": "f", "read_line": 10, "key": "x1", "key_is_computed": False,
     "receiver": "sleeves",
     "two_depth_sites": [{
         "line": 10, "column": 4, "depth_pair": "1->2", "inner_key": None, "outer_key": "y",
         "members": [{"depth": 1, "key": None, "ctx": "load"},
                     {"depth": 2, "key": "y", "ctx": "del"}],
         "member_ctx": ["del", "load"], "any_member_is_write": True,
         "deepest_member_is_write": True, "any_member_names_the_row_key": False,
         "any_member_writes_the_row_key": False, "deepest_member_writes_the_row_key": False}]},
]

FIXTURE_SITE_READ_ONLY = [
    {"module": "b.py", "function": "g", "read_line": 20, "key": "days", "key_is_computed": False,
     "receiver": "P",
     "two_depth_sites": [{
         "line": 20, "column": 4, "depth_pair": "1->3", "inner_key": None, "outer_key": "days",
         "members": [{"depth": 1, "key": None, "ctx": "load"},
                     {"depth": 3, "key": "days", "ctx": "load"}],
         "member_ctx": ["load"], "any_member_is_write": False,
         "deepest_member_is_write": False, "any_member_names_the_row_key": True,
         "any_member_writes_the_row_key": False,
         "deepest_member_writes_the_row_key": False}]},
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

    def store_ctx_is_seen_at_the_deepest_member():
        got, why = _fixture_sites('a["k"]["j"] = 1\n')
        assert why is None, why
        row, = [site_row(s) for s in got["sites"]]
        assert row["any_member_is_write"] and row["deepest_member_is_write"], row
        assert [m["ctx"] for m in row["members"]] == ["store", "load"], row["members"]

    def del_ctx_is_seen_at_the_deepest_member():
        got, why = _fixture_sites('del a["k"]["j"]\n')
        assert why is None, why
        row, = [site_row(s) for s in got["sites"]]
        assert row["deepest_member_is_write"], row

    def read_only_site_is_not_a_write():
        got, why = _fixture_sites('v = a["k"]["j"]\n')
        assert why is None, why
        row, = [site_row(s) for s in got["sites"]]
        assert not row["any_member_is_write"], row

    def counts_add_up():
        c = counts_of(FIXTURE_FILES, FIXTURE_SITE_WRITE + FIXTURE_SITE_READ_ONLY, 2, 0, 8)
        assert c["files_carrying_a_two_depth_site"] == 2, c
        assert c["two_depth_sites"] == 3, c
        assert c["depth_pair_histogram"] == {"1->2": 2, "1->3": 1}, c["depth_pair_histogram"]
        assert c["corpus_member_ctx_histogram"] == {"del": 0, "load": 5, "store": 1}, \
            c["corpus_member_ctx_histogram"]
        assert c["corpus_sites_with_a_write_at_any_depth"] == 1, c
        assert c["counted_read_lines"] == 2, c
        assert c["two_depth_sites_on_counted_lines"] == 2, c

    def write_of_the_row_key_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_SITE_WRITE, 2, 0, 8)
        assert c["counted_sites_where_a_member_writes_the_row_key"] == 1, c
        assert decide(c) == V_WRITE_OF_THE_ROW_KEY_BELOW

    def write_of_another_key_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_SITE_OTHER_KEY, 2, 0, 8)
        assert c["counted_sites_with_a_write_at_any_depth"] == 1, c
        assert c["counted_sites_where_a_member_writes_the_row_key"] == 0, c
        assert decide(c) == V_WRITE_OF_ANOTHER_KEY_BELOW

    def read_only_sites_are_explained_by_the_corpus():
        c = counts_of(FIXTURE_FILES, FIXTURE_SITE_READ_ONLY, 2, 0, 8)
        assert c["counted_sites_with_a_write_at_any_depth"] == 0, c
        assert c["corpus_sites_with_a_write_at_any_depth"] == 1, c
        assert decide(c) == V_COUNTED_SITES_ARE_READ_ONLY

    def no_write_anywhere_is_reachable():
        files = [dict(FIXTURE_FILES[1])]
        c = counts_of(files, FIXTURE_SITE_READ_ONLY, 2, 0, 8)
        assert c["corpus_sites_with_a_write_at_any_depth"] == 0, c
        assert decide(c) == V_NO_WRITE_ANYWHERE

    def off_population_is_reachable():
        rows = [dict(FIXTURE_SITE_WRITE[0], two_depth_sites=[])]
        c = counts_of(FIXTURE_FILES, rows, 2, 0, 8)
        assert decide(c) == V_OFF_POPULATION

    def absent_is_reachable():
        c = counts_of([], FIXTURE_SITE_WRITE, 2, 0, 0)
        assert decide(c) == V_ABSENT

    def computed_key_can_never_name_the_row_key():
        row = dict(FIXTURE_SITE_WRITE[0], key=None, key_is_computed=True)
        site = dict(row["two_depth_sites"][0], any_member_names_the_row_key=False,
                    any_member_writes_the_row_key=False,
                    deepest_member_writes_the_row_key=False)
        c = counts_of(FIXTURE_FILES, [dict(row, two_depth_sites=[site])], 2, 0, 8)
        assert c["counted_lines_with_a_computed_key"] == 1, c
        assert c["counted_sites_where_a_member_writes_the_row_key"] == 0, c
        assert decide(c) == V_WRITE_OF_ANOTHER_KEY_BELOW

    def face_problems_accepts_a_sound_face():
        for rows in (FIXTURE_SITE_WRITE, FIXTURE_SITE_OTHER_KEY, FIXTURE_SITE_READ_ONLY):
            c = counts_of(FIXTURE_FILES, rows, 2, 0, 8)
            face = {"file_rows": FIXTURE_FILES, "rows": rows, "counts": c,
                    "verdict": decide(c)}
            assert not face_problems(face), (rows[0]["key"], face_problems(face))

    def face_problems_catches_a_wrong_verdict():
        c = counts_of(FIXTURE_FILES, FIXTURE_SITE_WRITE, 2, 0, 8)
        face = {"file_rows": FIXTURE_FILES, "rows": FIXTURE_SITE_WRITE, "counts": c,
                "verdict": V_COUNTED_SITES_ARE_READ_ONLY}
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_write_flag_that_lies():
        row = json.loads(json.dumps(FIXTURE_SITE_READ_ONLY[0]))
        row["two_depth_sites"][0]["any_member_is_write"] = True
        c = counts_of(FIXTURE_FILES, [row], 2, 0, 8)
        face = {"file_rows": FIXTURE_FILES, "rows": [row], "counts": c,
                "verdict": V_WRITE_OF_ANOTHER_KEY_BELOW}
        assert any("write flag" in p or "write while" in p for p in face_problems(face)), \
            face_problems(face)

    def face_problems_catches_a_deepest_write_without_any_write():
        row = json.loads(json.dumps(FIXTURE_SITE_OTHER_KEY[0]))
        site = row["two_depth_sites"][0]
        site["any_member_is_write"] = False
        site["any_member_writes_the_row_key"] = False
        site["deepest_member_writes_the_row_key"] = True
        c = counts_of(FIXTURE_FILES, [row], 2, 0, 8)
        face = {"file_rows": FIXTURE_FILES, "rows": [row], "counts": c,
                "verdict": V_WRITE_OF_ANOTHER_KEY_BELOW}
        assert any("deepest-member write" in p or "write while none" in p
                   for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_bad_file_histogram():
        bad = [dict(FIXTURE_FILES[0], depth_pairs={"1->9": 1})]
        c = counts_of(FIXTURE_FILES, FIXTURE_SITE_WRITE, 2, 0, 8)
        face = {"file_rows": bad, "rows": FIXTURE_SITE_WRITE, "counts": c,
                "verdict": V_WRITE_OF_THE_ROW_KEY_BELOW}
        assert any("histogram" in p for p in face_problems(face)), face_problems(face)

    def answer_names_the_numbers():
        a = answer_of(counts_of(FIXTURE_FILES, FIXTURE_SITE_WRITE, 2, 0, 8))
        assert "3 two-depth" in a and "corpus writes: 1" in a, a

    for name, fn in [
        ("store_ctx_is_seen_at_the_deepest_member", store_ctx_is_seen_at_the_deepest_member),
        ("del_ctx_is_seen_at_the_deepest_member", del_ctx_is_seen_at_the_deepest_member),
        ("read_only_site_is_not_a_write", read_only_site_is_not_a_write),
        ("counts_add_up", counts_add_up),
        ("write_of_the_row_key_is_reachable", write_of_the_row_key_is_reachable),
        ("write_of_another_key_is_reachable", write_of_another_key_is_reachable),
        ("read_only_sites_are_explained_by_the_corpus", read_only_sites_are_explained_by_the_corpus),
        ("no_write_anywhere_is_reachable", no_write_anywhere_is_reachable),
        ("off_population_is_reachable", off_population_is_reachable),
        ("absent_is_reachable", absent_is_reachable),
        ("computed_key_can_never_name_the_row_key", computed_key_can_never_name_the_row_key),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_write_flag_that_lies", face_problems_catches_a_write_flag_that_lies),
        ("face_problems_catches_a_deepest_write_without_any_write",
         face_problems_catches_a_deepest_write_without_any_write),
        ("face_problems_catches_a_bad_file_histogram", face_problems_catches_a_bad_file_histogram),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _fixture_sites(source):
    """Run E638's own site grouping over a source string (no file needed)."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    try:
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(source)
        return e638.file_sites(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


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