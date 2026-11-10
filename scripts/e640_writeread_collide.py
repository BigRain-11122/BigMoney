"""E640 -- can a corpus write site sit *next to* the reads E632/E633 count, in the same function?

E639 priced the write population (5,513 of 45,391 two-depth sites carry a store or delete, all at
the deepest member) but joined it to nothing: it only looked at the sites physically on a counted
read line, where it found 18 members and 18 loads.  That is a fact about six lines, not about the
functions that hold them.  The question a duplicate-read test actually has to answer is whether the
key a counted line reads can be written *anywhere in that function* -- if it can, the "this line
reads k twice" claim is standing next to a write of k and the read/write distinction matters; if it
cannot, the counted read is the only access to that key in its scope.

For each of E633's counted read lines this study:

  * resolves the read line to its innermost enclosing function (name-matched first, then innermost),
  * publishes every two-depth site whose innermost owner *is that function*, with the write face
    (store/delete at any depth, at the deepest member) and whether any member names the row's key,
  * splits those sites by position -- before the read line, on it, after it -- because "a write sits
    next to the read" is a claim about order, not only about presence,
  * publishes a corpus denominator: how many functions carry a two-depth site at all and how many
    carry a two-depth *write* site, so a zero on the counted functions says what it counted
    (E444 family: a zero that cannot say what it counted is a claim).

Everything is re-derived from the tree.  E638's site grouping and E633's row list are imported, not
copied: a second definition of "two-depth site" would be free to drift away from the published one.
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
FACE = "WRITEREADCOLLIDE.json"
LATEST = "writereadcollide_latest.json"
STUDY = "E640_write_read_collide"
SELF_PARTS = ("e640_", "run_e640_", "_probe_e640", "_r1660")
SOURCE_FACE = "results/state_tilt/WRITEBELOW.json"
MAX_BYTES = 1024 * 1024
MAX_EXAMPLES = 25

import e391_key_name_two_meanings as e391  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402

WRITE_CTX = ("store", "del")

V_WRITE_OF_THE_ROW_KEY_IN_THE_FUNCTION = (
    "at_least_one_counted_read_line_sits_in_a_function_that_carries_a_two_depth_write_site_"
    "naming_the_row's_counted_key,_so_the_read_is_not_the_only_access_to_that_key_in_its_scope")
V_WRITE_OF_ANOTHER_KEY_IN_THE_FUNCTION = (
    "the_counted_read_lines'_functions_do_carry_two_depth_write_sites_but_none_of_them_names_the_"
    "row's_counted_key_at_either_depth,_so_writes_can_sit_next_to_these_reads_only_of_other_keys")
V_NO_WRITE_IN_THE_COUNTED_FUNCTIONS = (
    "no_counted_read_line's_function_carries_a_two_depth_write_site_while_the_corpus_does_carry_"
    "them,_so_the_zero_is_a_property_of_these_thirteen_functions_not_of_the_form")
V_NO_TWO_DEPTH_WRITE_ANYWHERE = (
    "no_function_in_the_corpus_carries_a_two_depth_write_site,_so_no_write_of_any_key_can_sit_"
    "next_to_these_reads_and_the_question_is_moot_at_this_population")
V_OFF_POPULATION = (
    "the_two_depth_form_and_its_write_sites_exist_in_the_corpus_but_no_counted_read_line_"
    "resolves_to_a_function_that_carries_one,_so_the_question_is_settled_off_the_population_that_"
    "E632_and_E633_count")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    """The Python corpus E391 walks, minus this study's own files and scratch patchers."""
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


_TREE_CACHE = {}


def tree_of(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        src = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    if path in _TREE_CACHE:
        return _TREE_CACHE[path]
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        tree = None
    _TREE_CACHE[path] = tree
    return tree


def _last_line(node):
    end = getattr(node, "end_lineno", None)
    if end:
        return end
    best = getattr(node, "lineno", 0) or 0
    for child in ast.walk(node):
        ln = getattr(child, "lineno", None) or 0
        if ln > best:
            best = ln
    return best


def function_spans(path):
    """Every FunctionDef/AsyncFunctionDef as {name, qualname, start, end} -- lexical extent."""
    tree = tree_of(path)
    if tree is None:
        return None
    out = []

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = prefix + child.name
                out.append({"name": child.name, "qualname": qual,
                            "start": child.lineno, "end": _last_line(child)})
                walk(child, qual + ".")
            elif isinstance(child, ast.ClassDef):
                walk(child, prefix + child.name + ".")
            else:
                walk(child, prefix)
    walk(tree, "")
    out.sort(key=lambda s: (s["start"], -(s["end"])))
    return out


def innermost_owner(spans, line, name=None):
    """The smallest span containing ``line``; a name match is preferred when one is given."""
    cands = [s for s in spans if s["start"] <= line <= s["end"]]
    if name:
        named = [s for s in cands if s["name"] == name]
        if named:
            cands = named
    if not cands:
        return None
    return min(cands, key=lambda s: (s["end"] - s["start"], -s["start"]))


def site_row(s):
    """One site with the write face answered per site and per depth."""
    members = s.get("members") or []
    deepest = s.get("max_depth")
    if deepest is None:
        depths = sorted({m.get("depth") for m in members})
        deepest = depths[-1] if depths else None
    deep = [m for m in members if m.get("depth") == deepest]
    return {
        "line": s.get("line"),
        "column": s.get("column"),
        "depth_pair": s.get("depth_pair"),
        "inner_key": s.get("inner_key"),
        "outer_key": s.get("outer_key"),
        "members": members,
        "member_ctx": sorted({m.get("ctx") for m in members}),
        "any_member_is_write": any(is_write(m.get("ctx")) for m in members),
        "deepest_member_is_write": any(is_write(m.get("ctx")) for m in deep),
    }


def site_names(site, key):
    return bool(key is not None and any(m.get("key") == key for m in site.get("members") or []))


def site_writes(site, key):
    return bool(key is not None and any(is_write(m.get("ctx")) and m.get("key") == key
                                       for m in site.get("members") or []))


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    files = corpus(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    file_rows = []
    totals = {"subscript_nodes": 0, "sites": 0}
    for p in files:
        got, why = e638.file_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        totals["subscript_nodes"] += got["subscript_nodes"]
        if not got["sites"]:
            continue
        spans = function_spans(p)
        if spans is None:
            holes["does_not_parse"] = holes.get("does_not_parse", 0) + 1
            continue
        owners = {}
        write_owners = {}
        write_sites = 0
        write_sites_all = 0
        for s in got["sites"]:
            row = site_row(s)
            if row["any_member_is_write"]:
                write_sites_all += 1
            owner = innermost_owner(spans, s["line"])
            if owner is None:
                continue
            tag = owner["qualname"]
            owners[tag] = owners.get(tag, 0) + 1
            if row["any_member_is_write"]:
                write_sites += 1
                write_owners[tag] = write_owners.get(tag, 0) + 1
        totals["sites"] += len(got["sites"])
        file_rows.append({
            "module": rel(p, root),
            "two_depth_sites": len(got["sites"]),
            "sites_with_an_owner_function": sum(owners.values()),
            "functions_carrying_a_two_depth_site": len(owners),
            "two_depth_write_sites": write_sites,
            "two_depth_write_sites_all_owners": write_sites_all,
            "functions_carrying_a_two_depth_write_site": len(write_owners),
        })
    file_rows.sort(key=lambda r: (-r["two_depth_sites"], r["module"]))

    rows = join_counted_lines(root)
    counts = counts_of(file_rows, rows, len(files), holes, totals["subscript_nodes"])
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every .py in the corpus E391 walks with E638's own two-depth site "
                   "grouping, resolve each site's innermost enclosing function, and for E633's "
                   "counted read lines publish every two-depth site owned by the read line's own "
                   "function -- its write face, whether any member names the row's key, and where "
                   "it sits relative to the read line -- beside a corpus denominator of functions "
                   "carrying a two-depth site and functions carrying a two-depth write"),
        "population_source": ("%d Python files of the tree corpus, joined to the %d counted read "
                              "line(s) E633 publishes (via E638's join)"
                              % (len(files), len(rows))),
        "counts": counts,
        "rows": rows,
        "counted_functions": counted_functions(rows),
        "file_rows": file_rows,
        "examples": examples_of(rows),
        "limits": [
            "'in the same function' means the site's innermost enclosing function is the read "
            "line's innermost enclosing function, so a site inside a nested def is attributed to "
            "the nested function and not to the outer one",
            "the read line's function is matched by name first and then by innermost containment, "
            "so a name that appears twice in one module still resolves to the smallest span that "
            "holds the line",
            "ctx is the AST Subscript ctx: an augmented assignment a['k'] += 1 is a load plus a "
            "store in one node and is published as store by ast, so it counts as a write here",
            "a computed key names nothing, so a site or read whose key is computed can never "
            "'name the row key'; those rows keep their sites but are excluded from the key match",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted separately",
            "the exclusion list drops only this study's own files, so E638's and E639's scripts are "
            "inside this population while each study dropped its own: the file and site totals are "
            "therefore slightly larger than theirs, and the difference is published rather than "
            "reconciled away",
            "a site outside every function (module-level code) has no owner, so it is not 'in the "
            "same function' as any read line; those sites are published separately as "
            "corpus_write_sites_without_an_owner_function and the all-owner total is what E639's "
            "corpus write count should be read against -- the two numbers differ by exactly that "
            "population, not by a disagreement about what a write site is",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def join_counted_lines(root=ROOT):
    """One row per E633 counted read line, with every two-depth site owned by its function."""
    cache = {}
    out = []
    for r in e638.join_counted_lines(root):
        module = r.get("module")
        line = r.get("read_line")
        key = r.get("key")
        function = r.get("function")
        owner = None
        sites = []
        spans_n = 0
        got, why = (None, "no_module") if not module else e638.file_sites(
            os.path.join(root, module))
        if got is not None:
            spans = cache.get(module)
            if spans is None:
                spans = function_spans(os.path.join(root, module))
                cache[module] = spans
            if spans is None:
                why = "does_not_parse"
            else:
                spans_n = len(spans)
                owner = innermost_owner(spans, line, function) if line else None
                if owner is not None:
                    for s in got["sites"]:
                        holder = innermost_owner(spans, s["line"])
                        if holder is None or holder["qualname"] != owner["qualname"]:
                            continue
                        row = site_row(s)
                        row["names_the_row_key"] = site_names(row, key)
                        row["writes_the_row_key"] = site_writes(row, key)
                        row["position"] = ("before" if s["line"] < line
                                           else "after" if s["line"] > line else "at")
                        sites.append(row)
        sites.sort(key=lambda s: (s["line"], s["column"]))
        out.append({
            "module": module,
            "function": function,
            "read_line": line,
            "key": key,
            "key_is_computed": key is None,
            "receiver": r.get("receiver"),
            "scope_problem": (None if owner is not None else (why or "no_function_holds_the_line")),
            "function_span": ({"qualname": owner["qualname"], "start": owner["start"],
                               "end": owner["end"]} if owner else None),
            "functions_in_module": spans_n,
            "sites_in_the_function": sites,
        })
    out.sort(key=lambda x: (x["module"] or "", x["read_line"] or 0, x["key"] or ""))
    return out


def counted_functions(rows):
    """Distinct functions among the counted rows -- two reads in one function count once here."""
    seen = {}
    for r in rows:
        span = r.get("function_span")
        if not span:
            continue
        tag = (r["module"], span["qualname"], span["start"], span["end"])
        rec = seen.get(tag)
        if rec is None:
            seen[tag] = {"module": r["module"], "qualname": span["qualname"],
                         "start": span["start"], "end": span["end"],
                         "counted_read_lines": 1,
                         "sites_in_the_function": len(r["sites_in_the_function"]),
                         "write_sites_in_the_function": sum(
                             1 for s in r["sites_in_the_function"] if s["any_member_is_write"]),
                         "read_lines": [r["read_line"]]}
        else:
            rec["counted_read_lines"] += 1
            rec["read_lines"].append(r["read_line"])
    out = sorted(seen.values(), key=lambda x: (x["module"], x["start"]))
    for rec in out:
        rec["read_lines"].sort()
    return out


def examples_of(rows):
    out = []
    for r in rows:
        for s in r["sites_in_the_function"]:
            if not s["any_member_is_write"]:
                continue
            out.append({"module": r["module"], "function": r["function"],
                        "read_line": r["read_line"], "key": r["key"],
                        "site_line": s["line"], "site_column": s["column"],
                        "position": s["position"], "depth_pair": s["depth_pair"],
                        "members": s["members"],
                        "names_the_row_key": s["names_the_row_key"],
                        "writes_the_row_key": s["writes_the_row_key"]})
            if len(out) >= MAX_EXAMPLES:
                return out
    return out


def counts_of(file_rows, rows, files_scanned=0, holes=None, subscript_nodes=0):
    holes = holes or {}
    sites = [s for r in rows for s in r["sites_in_the_function"]]
    members = [m for s in sites for m in (s.get("members") or [])]
    ctx = {"load": 0, "store": 0, "del": 0}
    for m in members:
        ctx[m.get("ctx")] = ctx.get(m.get("ctx"), 0) + 1
    distinct = counted_functions(rows)
    return {
        "python_files_scanned": files_scanned,
        "python_files_over_the_size_cap": int(holes.get("over_the_size_cap") or 0),
        "python_files_unreadable": int(holes.get("unreadable") or 0),
        "python_files_that_do_not_parse": int(holes.get("does_not_parse") or 0),
        "subscript_nodes_in_the_corpus": subscript_nodes,
        "files_carrying_a_two_depth_site": len(file_rows),
        "two_depth_sites": sum(f["two_depth_sites"] for f in file_rows),
        "two_depth_sites_with_an_owner_function": sum(
            f["sites_with_an_owner_function"] for f in file_rows),
        "functions_carrying_a_two_depth_site": sum(
            f["functions_carrying_a_two_depth_site"] for f in file_rows),
        "corpus_two_depth_write_sites": sum(f["two_depth_write_sites"] for f in file_rows),
        "corpus_two_depth_write_sites_all_owners": sum(
            (f.get("two_depth_write_sites_all_owners") or 0) for f in file_rows),
        "corpus_write_sites_without_an_owner_function": sum(
            (f.get("two_depth_write_sites_all_owners") or 0)
            - (f.get("two_depth_write_sites") or 0) for f in file_rows),
        "functions_carrying_a_two_depth_write_site": sum(
            f["functions_carrying_a_two_depth_write_site"] for f in file_rows),
        "counted_read_lines": len(rows),
        "counted_lines_with_a_computed_key": sum(1 for r in rows if r.get("key_is_computed")),
        "counted_lines_that_resolve_to_a_function": sum(
            1 for r in rows if r.get("function_span")),
        "counted_lines_scope_problems": sum(1 for r in rows if r.get("scope_problem")),
        "counted_functions": len(distinct),
        "counted_functions_with_a_two_depth_site": sum(
            1 for f in distinct if f["sites_in_the_function"]),
        "counted_functions_with_a_two_depth_write_site": sum(
            1 for f in distinct if f["write_sites_in_the_function"]),
        "sites_in_the_counted_functions": len(sites),
        "site_member_ctx_histogram": dict(sorted(ctx.items())),
        "write_sites_in_the_counted_functions": sum(
            1 for s in sites if s["any_member_is_write"]),
        "write_sites_at_the_deepest_member": sum(
            1 for s in sites if s["deepest_member_is_write"]),
        "sites_naming_the_row_key": sum(1 for s in sites if s["names_the_row_key"]),
        "write_sites_naming_the_row_key": sum(1 for s in sites if s["writes_the_row_key"]),
        "deepest_write_sites_naming_the_row_key": sum(
            1 for s in sites if s["writes_the_row_key"] and s["deepest_member_is_write"]),
        "counted_lines_whose_function_holds_a_two_depth_site": sum(
            1 for r in rows if r["sites_in_the_function"]),
        "counted_lines_whose_function_holds_a_two_depth_write_site": sum(
            1 for r in rows if any(s["any_member_is_write"] for s in r["sites_in_the_function"])),
        "counted_lines_whose_function_writes_the_row_key": sum(
            1 for r in rows if any(s["writes_the_row_key"] for s in r["sites_in_the_function"])),
        "write_sites_before_the_read_line": sum(
            1 for s in sites if s["any_member_is_write"] and s["position"] == "before"),
        "write_sites_on_the_read_line": sum(
            1 for s in sites if s["any_member_is_write"] and s["position"] == "at"),
        "write_sites_after_the_read_line": sum(
            1 for s in sites if s["any_member_is_write"] and s["position"] == "after"),
        "counted_functions_with_no_site_at_all": sum(
            1 for f in distinct if not f["sites_in_the_function"]),
    }


def decide(c):
    if not c.get("corpus_two_depth_write_sites"):
        return V_NO_TWO_DEPTH_WRITE_ANYWHERE
    if not c.get("counted_read_lines") or not (
            c.get("counted_lines_whose_function_holds_a_two_depth_site")
            or c.get("counted_lines_that_resolve_to_a_function")):
        return V_OFF_POPULATION
    if c.get("counted_lines_whose_function_writes_the_row_key"):
        return V_WRITE_OF_THE_ROW_KEY_IN_THE_FUNCTION
    if c.get("write_sites_in_the_counted_functions"):
        return V_WRITE_OF_ANOTHER_KEY_IN_THE_FUNCTION
    return V_NO_WRITE_IN_THE_COUNTED_FUNCTIONS


def answer_of(c):
    return ("%d files, %d two-depth sites of which %d sit inside a function (%d function(s)); corpus "
            "write face: %d site(s) with a store/delete inside a function, %d counting every owner "
            "(%d of them at module level); E633's %d counted read line(s) resolve to %d "
            "function(s), of which %d carry a two-depth site and %d carry a write: %d site(s) / %d "
            "write site(s) in those scopes (member ctx %s), %d naming the row's key and %d writing "
            "it; writes sit %d before / %d on / %d after the read line"
            % (c.get("python_files_scanned"), c.get("two_depth_sites"),
               c.get("two_depth_sites_with_an_owner_function"),
               c.get("functions_carrying_a_two_depth_site"),
               c.get("corpus_two_depth_write_sites"),
               c.get("corpus_two_depth_write_sites_all_owners"),
               c.get("corpus_write_sites_without_an_owner_function"),
               c.get("counted_read_lines"), c.get("counted_functions"),
               c.get("counted_functions_with_a_two_depth_site"),
               c.get("counted_functions_with_a_two_depth_write_site"),
               c.get("sites_in_the_counted_functions"),
               c.get("write_sites_in_the_counted_functions"),
               json.dumps(c.get("site_member_ctx_histogram") or {}, sort_keys=True),
               c.get("sites_naming_the_row_key"), c.get("write_sites_naming_the_row_key"),
               c.get("write_sites_before_the_read_line"),
               c.get("write_sites_on_the_read_line"),
               c.get("write_sites_after_the_read_line")))


def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "counts": m["counts"],
        "rows": m["rows"],
        "counted_functions": m["counted_functions"],
        "file_rows": m["file_rows"],
        "examples": m["examples"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "files_carrying_a_two_depth_site", "two_depth_sites",
    "two_depth_sites_with_an_owner_function", "functions_carrying_a_two_depth_site",
    "corpus_two_depth_write_sites", "corpus_two_depth_write_sites_all_owners",
    "corpus_write_sites_without_an_owner_function",
    "functions_carrying_a_two_depth_write_site",
    "counted_read_lines", "counted_lines_with_a_computed_key",
    "counted_lines_that_resolve_to_a_function", "counted_lines_scope_problems",
    "counted_functions", "counted_functions_with_a_two_depth_site",
    "counted_functions_with_a_two_depth_write_site", "sites_in_the_counted_functions",
    "site_member_ctx_histogram", "write_sites_in_the_counted_functions",
    "write_sites_at_the_deepest_member", "sites_naming_the_row_key",
    "write_sites_naming_the_row_key", "deepest_write_sites_naming_the_row_key",
    "counted_lines_whose_function_holds_a_two_depth_site",
    "counted_lines_whose_function_holds_a_two_depth_write_site",
    "counted_lines_whose_function_writes_the_row_key",
    "write_sites_before_the_read_line", "write_sites_on_the_read_line",
    "write_sites_after_the_read_line", "counted_functions_with_no_site_at_all",
)


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
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    if face.get("counted_functions") != counted_functions(rows):
        problems.append("the counted function list is not the one the rows carry")
    for f in files:
        if (f.get("sites_with_an_owner_function") or 0) > f.get("two_depth_sites", 0):
            problems.append("file row %s owns more sites than it has" % f.get("module"))
            break
        if (f.get("two_depth_write_sites") or 0) > (f.get("sites_with_an_owner_function") or 0):
            problems.append("file row %s has more writes than owned sites" % f.get("module"))
            break
        if (f.get("two_depth_write_sites_all_owners") or 0) < (f.get("two_depth_write_sites") or 0):
            problems.append("file row %s owns more write sites than it has"
                            % f.get("module"))
            break
        if (f.get("functions_carrying_a_two_depth_write_site") or 0) > (
                f.get("functions_carrying_a_two_depth_site") or 0):
            problems.append("file row %s has more writing functions than functions"
                            % f.get("module"))
            break
    for r in rows:
        sites = r.get("sites_in_the_function") or []
        span = r.get("function_span")
        if span is None and sites:
            problems.append("row %s:%s carries sites without a function"
                            % (r.get("module"), r.get("read_line")))
            break
        if span is not None:
            outside = [s for s in sites
                       if not (span["start"] <= s["line"] <= span["end"])]
            if outside:
                problems.append("row %s:%s publishes a site outside its function span"
                                % (r.get("module"), r.get("read_line")))
                break
        for s in sites:
            member_ctxs = [m.get("ctx") for m in (s.get("members") or [])]
            if s.get("any_member_is_write") != any(ctx in WRITE_CTX for ctx in member_ctxs):
                problems.append("row %s:%s has a write flag its members do not carry"
                                % (r.get("module"), r.get("read_line")))
                break
            if s.get("writes_the_row_key") and not s.get("any_member_is_write"):
                problems.append("row %s:%s writes the row key while none of its members is a write"
                                % (r.get("module"), r.get("read_line")))
                break
            if not r.get("key") and (s.get("names_the_row_key") or s.get("writes_the_row_key")):
                problems.append("row %s:%s names a key it does not have"
                                % (r.get("module"), r.get("read_line")))
                break
        writes = [s for s in sites if s.get("any_member_is_write")]
        if (sum(1 for s in writes if s["position"] == "before")
                + sum(1 for s in writes if s["position"] == "at")
                + sum(1 for s in writes if s["position"] == "after")) != len(writes):
            problems.append("row %s:%s has a write site with no position"
                            % (r.get("module"), r.get("read_line")))
            break
    if face.get("verdict") == V_WRITE_OF_THE_ROW_KEY_IN_THE_FUNCTION \
            and c.get("counted_lines_whose_function_writes_the_row_key", 0) == 0:
        problems.append("the verdict reports a write of the row key the rows do not carry")
    if face.get("verdict") == V_WRITE_OF_ANOTHER_KEY_IN_THE_FUNCTION \
            and (c.get("write_sites_in_the_counted_functions", 0) == 0
                 or c.get("counted_lines_whose_function_writes_the_row_key", 0) > 0):
        problems.append("the verdict says writes sit beside the reads without the row key while "
                        "a count says otherwise")
    if face.get("verdict") == V_NO_WRITE_IN_THE_COUNTED_FUNCTIONS \
            and (c.get("write_sites_in_the_counted_functions", 0) > 0
                 or c.get("corpus_two_depth_write_sites", 0) == 0):
        problems.append("the zero-functions verdict is not the one its own totals force")
    if face.get("verdict") == V_NO_TWO_DEPTH_WRITE_ANYWHERE \
            and c.get("corpus_two_depth_write_sites", 0) > 0:
        problems.append("the verdict says no function carries a write while the corpus does")
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
    say("run: files=%d sites=%d functions=%d corpus_write_sites=%d corpus_write_functions=%d "
        "counted_lines=%d counted_functions=%d with_site=%d with_write=%d write_sites=%d "
        "writes_row_key=%d"
        % (c["python_files_scanned"], c["two_depth_sites"],
           c["functions_carrying_a_two_depth_site"], c["corpus_two_depth_write_sites"],
           c["functions_carrying_a_two_depth_write_site"], c["counted_read_lines"],
           c["counted_functions"], c["counted_functions_with_a_two_depth_site"],
           c["counted_functions_with_a_two_depth_write_site"],
           c["write_sites_in_the_counted_functions"],
           c["counted_lines_whose_function_writes_the_row_key"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_FILES = [
    {"module": "a.py", "two_depth_sites": 3, "sites_with_an_owner_function": 3,
     "functions_carrying_a_two_depth_site": 2, "two_depth_write_sites": 1,
     "two_depth_write_sites_all_owners": 2,
     "functions_carrying_a_two_depth_write_site": 1},
    {"module": "b.py", "two_depth_sites": 1, "sites_with_an_owner_function": 1,
     "functions_carrying_a_two_depth_site": 1, "two_depth_write_sites": 0,
     "two_depth_write_sites_all_owners": 0,
     "functions_carrying_a_two_depth_write_site": 0},
]

FIXTURE_SPAN = {"qualname": "f", "start": 5, "end": 30}


def _site(line, column, members, names=False, writes=False, position="before"):
    return {"line": line, "column": column, "depth_pair": "1->2", "inner_key": None,
            "outer_key": "x1", "members": members, "member_ctx": ["load"],
            "any_member_is_write": any(m["ctx"] in WRITE_CTX for m in members),
            "deepest_member_is_write": any(m["ctx"] in WRITE_CTX
                                           for m in members if m["depth"] == 2),
            "names_the_row_key": names, "writes_the_row_key": writes,
            "position": position}


FIXTURE_ROW_WRITE_KEY = [{
    "module": "a.py", "function": "f", "read_line": 10, "key": "x1", "key_is_computed": False,
    "receiver": "sleeves", "scope_problem": None, "function_span": FIXTURE_SPAN,
    "functions_in_module": 2,
    "sites_in_the_function": [
        _site(8, 4, [{"depth": 1, "key": None, "ctx": "load"},
                     {"depth": 2, "key": "x1", "ctx": "store"}], names=True, writes=True),
        _site(10, 8, [{"depth": 1, "key": None, "ctx": "load"},
                      {"depth": 2, "key": "x1", "ctx": "load"}],
              names=True, writes=False, position="at"),
    ]}]

FIXTURE_ROW_OTHER_KEY = [{
    "module": "a.py", "function": "f", "read_line": 10, "key": "x1", "key_is_computed": False,
    "receiver": "sleeves", "scope_problem": None, "function_span": FIXTURE_SPAN,
    "functions_in_module": 2,
    "sites_in_the_function": [
        _site(12, 4, [{"depth": 1, "key": None, "ctx": "load"},
                      {"depth": 2, "key": "y", "ctx": "del"}], position="after")]}]

FIXTURE_ROW_READ_ONLY = [{
    "module": "b.py", "function": "g", "read_line": 20, "key": "days",
    "key_is_computed": False, "receiver": "P", "scope_problem": None,
    "function_span": {"qualname": "g", "start": 15, "end": 40}, "functions_in_module": 1,
    "sites_in_the_function": [
        _site(20, 4, [{"depth": 1, "key": None, "ctx": "load"},
                      {"depth": 2, "key": "days", "ctx": "load"}], names=True,
              position="at")]}]


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

    def a_write_site_in_the_function_is_found():
        got, why = _fixture_sites('def f():\n    a["k"]["j"] = 1\n')
        assert why is None, why
        spans = _fixture_spans('def f():\n    a["k"]["j"] = 1\n')
        site, = got["sites"]
        owner = innermost_owner(spans, site["line"])
        assert owner and owner["qualname"] == "f", (owner, spans)
        assert site_row(site)["any_member_is_write"], site

    def a_nested_def_owns_its_own_sites():
        src = ('def f():\n    def g():\n        a["k"]["j"] = 1\n    return 1\n')
        got, why = _fixture_sites(src)
        assert why is None, why
        spans = _fixture_spans(src)
        site, = got["sites"]
        assert innermost_owner(spans, site["line"])["qualname"] == "f.g", spans

    def the_name_match_beats_the_outer_span():
        src = 'def f():\n    pass\n\ndef f():\n    a["k"]["j"] = 1\n'
        spans = _fixture_spans(src)
        owner = innermost_owner(spans, 5, "f")
        assert (owner["start"], owner["end"]) == (4, 5), owner

    def counts_add_up():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_WRITE_KEY + FIXTURE_ROW_READ_ONLY, 2, 0, 9)
        assert c["files_carrying_a_two_depth_site"] == 2, c
        assert c["two_depth_sites"] == 4, c
        assert c["functions_carrying_a_two_depth_site"] == 3, c
        assert c["corpus_two_depth_write_sites"] == 1, c
        assert c["counted_read_lines"] == 2, c
        assert c["counted_functions"] == 2, c
        assert c["sites_in_the_counted_functions"] == 3, c
        assert c["write_sites_in_the_counted_functions"] == 1, c
        assert c["site_member_ctx_histogram"] == {"del": 0, "load": 5, "store": 1}, \
            c["site_member_ctx_histogram"]

    def write_of_the_row_key_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_WRITE_KEY, 2, 0, 9)
        assert c["counted_lines_whose_function_writes_the_row_key"] == 1, c
        assert decide(c) == V_WRITE_OF_THE_ROW_KEY_IN_THE_FUNCTION

    def write_of_another_key_is_reachable():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_OTHER_KEY, 2, 0, 9)
        assert c["write_sites_in_the_counted_functions"] == 1, c
        assert c["counted_lines_whose_function_writes_the_row_key"] == 0, c
        assert decide(c) == V_WRITE_OF_ANOTHER_KEY_IN_THE_FUNCTION

    def read_only_functions_are_explained_by_the_corpus():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_READ_ONLY, 2, 0, 9)
        assert c["write_sites_in_the_counted_functions"] == 0, c
        assert c["corpus_two_depth_write_sites"] == 1, c
        assert decide(c) == V_NO_WRITE_IN_THE_COUNTED_FUNCTIONS

    def no_write_anywhere_is_reachable():
        files = [dict(FIXTURE_FILES[1])]
        c = counts_of(files, FIXTURE_ROW_READ_ONLY, 2, 0, 9)
        assert c["corpus_two_depth_write_sites"] == 0, c
        assert decide(c) == V_NO_TWO_DEPTH_WRITE_ANYWHERE

    def off_population_is_reachable():
        row = dict(FIXTURE_ROW_WRITE_KEY[0], function_span=None, sites_in_the_function=[],
                   scope_problem="no_function_holds_the_line")
        c = counts_of(FIXTURE_FILES, [row], 2, 0, 9)
        assert decide(c) == V_OFF_POPULATION

    def positions_split_the_writes():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_WRITE_KEY + FIXTURE_ROW_OTHER_KEY, 2, 0, 9)
        assert c["write_sites_before_the_read_line"] == 1, c
        assert c["write_sites_on_the_read_line"] == 0, c
        assert c["write_sites_after_the_read_line"] == 1, c

    def a_computed_key_can_never_name_the_row_key():
        row = dict(FIXTURE_ROW_WRITE_KEY[0], key=None, key_is_computed=True)
        sites = [dict(s, names_the_row_key=False, writes_the_row_key=False)
                 for s in row["sites_in_the_function"]]
        c = counts_of(FIXTURE_FILES, [dict(row, sites_in_the_function=sites)], 2, 0, 9)
        assert c["counted_lines_with_a_computed_key"] == 1, c
        assert c["sites_naming_the_row_key"] == 0, c
        assert decide(c) == V_WRITE_OF_ANOTHER_KEY_IN_THE_FUNCTION

    def counted_functions_are_distinct():
        twin = dict(FIXTURE_ROW_WRITE_KEY[0], read_line=14)
        rows = [FIXTURE_ROW_WRITE_KEY[0], twin]
        distinct = counted_functions(rows)
        assert len(distinct) == 1 and distinct[0]["counted_read_lines"] == 2, distinct
        c = counts_of(FIXTURE_FILES, rows, 2, 0, 9)
        assert c["counted_functions"] == 1, c

    def face_problems_accepts_a_sound_face():
        for rows in (FIXTURE_ROW_WRITE_KEY, FIXTURE_ROW_OTHER_KEY, FIXTURE_ROW_READ_ONLY):
            c = counts_of(FIXTURE_FILES, rows, 2, 0, 9)
            face = {"file_rows": FIXTURE_FILES, "rows": rows, "counts": c,
                    "verdict": decide(c), "counted_functions": counted_functions(rows)}
            assert not face_problems(face), (rows[0]["module"], face_problems(face))

    def face_problems_catches_a_wrong_verdict():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_WRITE_KEY, 2, 0, 9)
        face = {"file_rows": FIXTURE_FILES, "rows": FIXTURE_ROW_WRITE_KEY, "counts": c,
                "verdict": V_NO_WRITE_IN_THE_COUNTED_FUNCTIONS,
                "counted_functions": counted_functions(FIXTURE_ROW_WRITE_KEY)}
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_write_flag_that_lies():
        row = json.loads(json.dumps(FIXTURE_ROW_WRITE_KEY[0]))
        # the second site is two loads, so a True flag here is a flag its members do not carry
        row["sites_in_the_function"][1]["any_member_is_write"] = True
        c = counts_of(FIXTURE_FILES, [row], 2, 0, 9)
        face = {"file_rows": FIXTURE_FILES, "rows": [row], "counts": c,
                "verdict": V_WRITE_OF_ANOTHER_KEY_IN_THE_FUNCTION,
                "counted_functions": counted_functions([row])}
        assert any("write flag" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_site_outside_its_span():
        row = json.loads(json.dumps(FIXTURE_ROW_OTHER_KEY[0]))
        row["sites_in_the_function"][0]["line"] = 99
        c = counts_of(FIXTURE_FILES, [row], 2, 0, 9)
        face = {"file_rows": FIXTURE_FILES, "rows": [row], "counts": c,
                "verdict": decide(c), "counted_functions": counted_functions([row])}
        assert any("outside its function" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_key_on_a_computed_row():
        row = json.loads(json.dumps(FIXTURE_ROW_WRITE_KEY[0]))
        row["key"] = None
        c = counts_of(FIXTURE_FILES, [row], 2, 0, 9)
        face = {"file_rows": FIXTURE_FILES, "rows": [row], "counts": c,
                "verdict": decide(c), "counted_functions": counted_functions([row])}
        assert any("names a key it does not have" in p for p in face_problems(face)), \
            face_problems(face)

    def the_owner_split_reconciles_with_the_all_owner_total():
        c = counts_of(FIXTURE_FILES, FIXTURE_ROW_WRITE_KEY, 2, 0, 9)
        assert c["corpus_two_depth_write_sites"] == 1, c
        assert c["corpus_two_depth_write_sites_all_owners"] == 2, c
        assert c["corpus_write_sites_without_an_owner_function"] == 1, c
        assert (c["corpus_two_depth_write_sites_all_owners"]
                - c["corpus_two_depth_write_sites"]) == \
            c["corpus_write_sites_without_an_owner_function"], c

    def answer_names_the_numbers():
        a = answer_of(counts_of(FIXTURE_FILES, FIXTURE_ROW_WRITE_KEY, 2, 0, 9))
        assert "4 two-depth" in a and "corpus write face: 1" in a, a

    for name, fn in [
        ("a_write_site_in_the_function_is_found", a_write_site_in_the_function_is_found),
        ("a_nested_def_owns_its_own_sites", a_nested_def_owns_its_own_sites),
        ("the_name_match_beats_the_outer_span", the_name_match_beats_the_outer_span),
        ("counts_add_up", counts_add_up),
        ("write_of_the_row_key_is_reachable", write_of_the_row_key_is_reachable),
        ("write_of_another_key_is_reachable", write_of_another_key_is_reachable),
        ("read_only_functions_are_explained_by_the_corpus",
         read_only_functions_are_explained_by_the_corpus),
        ("no_write_anywhere_is_reachable", no_write_anywhere_is_reachable),
        ("off_population_is_reachable", off_population_is_reachable),
        ("positions_split_the_writes", positions_split_the_writes),
        ("a_computed_key_can_never_name_the_row_key", a_computed_key_can_never_name_the_row_key),
        ("counted_functions_are_distinct", counted_functions_are_distinct),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_write_flag_that_lies",
         face_problems_catches_a_write_flag_that_lies),
        ("face_problems_catches_a_site_outside_its_span",
         face_problems_catches_a_site_outside_its_span),
        ("face_problems_catches_a_key_on_a_computed_row",
         face_problems_catches_a_key_on_a_computed_row),
        ("the_owner_split_reconciles_with_the_all_owner_total",
         the_owner_split_reconciles_with_the_all_owner_total),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _fixture_path(source):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(source)
    return path


def _fixture_sites(source):
    path = _fixture_path(source)
    try:
        return e638.file_sites(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _fixture_spans(source):
    path = _fixture_path(source)
    try:
        return function_spans(path)
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