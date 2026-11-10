"""E644 -- can a counted function write the counted key with a ONE-depth store the census cannot see?

E639/E640/E641 share one population: two-depth Subscript sites, i.e. positions where the same
(line, column) carries a subscript at two different depths.  That definition has a blind spot
built into it -- a store at a single depth (``P['days'] = x``) never produces two depths at one
position, so no site in the shared population can be it.  The counted read lines read
``P['days'][...]``; if the same function ever replaces ``P['days']`` wholesale, the mapping the
read line depends on is rewritten and every member of the counted population is silent about it.

For every counted function E640 attributes to E633's counted read lines this study:

  * collects every one-depth Subscript site in the function whose context is Store or Del (a plain
    store, an augmented store, a delete),
  * publishes that site's key (a literal spelling, or "computed" when the subscript is not a string
    constant), the container it writes through and that container's binding inside the function,
  * joins it to each counted read line of the same function: does the site name that line's key,
    and does it sit before / on / after that line,
  * and, for completeness of the "indexes into" half, re-reads E640's two-depth write sites whose
    depth-1 member names a counted key (a store *inside* the counted value rather than of it).

The population (which functions are counted, which lines they read, which keys they read) is
machine-read from E640's face; nothing here re-defines "counted line" or "two-depth site".
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
FACE = "ONEDEPTHWRITE.json"
LATEST = "onedepthwrite_latest.json"
STUDY = "E644_one_depth_write"
SOURCE_FACE = "results/state_tilt/WRITEREADCOLLIDE.json"

import e633_read_forms as e633  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e641_writer_receiver as e641  # noqa: E402

BINDINGS = ("parameter", "loop_target", "local_assignment", "module_scope", "unresolved")
OUTSIDE = ("parameter", "module_scope")
POSITIONS = ("before", "on", "after")

V_NAMES_THE_COUNTED_KEY = (
    "at_least_one_depth-1_store_or_delete_in_a_counted_function_names_the_key_a_counted_read_line_"
    "in_that_function_reads,_so_the_counted_mapping_is_replaced_whole_and_the_two-depth_census_"
    "cannot_see_it")
V_INDEXES_INTO_THE_COUNTED_KEY = (
    "no_depth-1_site_names_a_counted_row_key,_but_a_two-depth_store_indexes_into_one,_so_the_"
    "counted_value_is_mutated_one_level_below_its_root")
V_ONLY_OTHER_KEYS = (
    "the_counted_functions_carry_depth-1_store_or_delete_sites_but_none_names_or_indexes_into_the_"
    "key_a_counted_read_line_reads,_so_the_blind_spot_of_the_two-depth_census_is_empty_by_"
    "measurement")
V_NO_DEPTH1_SITE = (
    "no_counted_function_carries_a_depth-1_store_or_delete_site,_so_the_population_the_two-depth_"
    "census_cannot_see_does_not_exist_in_these_functions")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


# ---------------------------------------------------------------- ast helpers
def ctx_name(node):
    if isinstance(node.ctx, ast.Store):
        return "store"
    if isinstance(node.ctx, ast.Del):
        return "del"
    return None


def depth1_write_sites(tree):
    """One-depth Subscript sites in Store/Del context, one row per (line, column)."""
    groups = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if e638.subscript_depth(node) != 1:
            continue
        ctx = ctx_name(node)
        if ctx is None:
            continue
        row = groups.setdefault((node.lineno, node.col_offset),
                                {"ctxs": set(), "keys": set()})
        row["ctxs"].add(ctx)
        row["keys"].add(e633.const_str(node.slice))
    out = []
    for (line, col) in sorted(groups):
        keys = groups[(line, col)]["keys"]
        out.append({
            "line": line,
            "column": col,
            "ctxs": sorted(groups[(line, col)]["ctxs"]),
            "keys": sorted(k for k in keys if k is not None),
            "has_computed_key": None in keys,
        })
    return out


def site_node(tree, line, column):
    """The one-depth Store/Del Subscript at a published site."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if node.lineno != line or node.col_offset != column:
            continue
        if e638.subscript_depth(node) != 1 or ctx_name(node) is None:
            continue
        return node
    return None


def position_of(site_line, read_line):
    if read_line is None or site_line is None:
        return None
    if site_line < read_line:
        return "before"
    if site_line > read_line:
        return "after"
    return "on"


# ---------------------------------------------------------------- measure
def load_source(root=ROOT):
    with io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8") as fh:
        return json.load(fh)


def measure(root=ROOT):
    src = load_source(root)
    rows = src.get("rows") or []
    functions = src.get("counted_functions") or []
    out = []
    for fn in functions:
        module = fn.get("module")
        span = {"qualname": fn.get("qualname"), "start": fn.get("start"), "end": fn.get("end")}
        fn_rows = [r for r in rows
                   if r.get("module") == module
                   and (r.get("function_span") or {}).get("qualname") == span["qualname"]]
        read_lines = sorted(
            [{"line": r.get("read_line"), "key": r.get("key"), "receiver": r.get("receiver"),
              "key_is_computed": bool(r.get("key_is_computed"))} for r in fn_rows],
            key=lambda r: r["line"] or 0)
        read_keys = sorted({r["key"] for r in read_lines
                            if r["key"] and not r["key_is_computed"]})
        entry = {
            "module": module,
            "function": span["qualname"],
            "start": span["start"], "end": span["end"],
            "read_lines": read_lines,
            "read_keys": read_keys,
            "e640_read_lines": fn.get("counted_read_lines"),
            "scope_problem": None,
            "depth1_sites": [],
            "depth2_stores_indexing_into_a_counted_key": [],
        }
        path = os.path.join(root, module)
        got, why = e638.file_sites(path)
        if got is None:
            entry["scope_problem"] = why
            out.append(entry)
            continue
        tree = e640.tree_of(path)
        if tree is None:
            entry["scope_problem"] = "does_not_parse"
            out.append(entry)
            continue
        fnode = e641.function_node(tree, span)
        if fnode is None:
            entry["scope_problem"] = "function_not_found"
            out.append(entry)
            continue
        index = e641.binding_index(fnode, tree)
        spans = e640.function_spans(path)
        for site in depth1_write_sites(tree):
            owner = e640.innermost_owner(spans, site["line"])
            if owner is None or owner["qualname"] != span["qualname"]:
                continue
            node = site_node(tree, site["line"], site["column"])
            container, chain = e641.container_chain(node) if node is not None else (None, [])
            info = index.get(container) if container else None
            binding = info["binding"] if info else "unresolved"
            named = [r for r in read_lines
                     if r["key"] and not r["key_is_computed"] and r["key"] in site["keys"]]
            per_line = []
            for r in read_lines:
                per_line.append({
                    "read_line": r["line"], "key": r["key"],
                    "names_this_lines_key": bool(
                        r["key"] and not r["key_is_computed"] and r["key"] in site["keys"]),
                    "position": position_of(site["line"], r["line"]),
                })
            entry["depth1_sites"].append({
                "line": site["line"], "column": site["column"],
                "ctxs": site["ctxs"],
                "keys": site["keys"],
                "has_computed_key": site["has_computed_key"],
                "container": container,
                "container_chain": chain,
                "binding": binding,
                "bound_from_outside_the_function": binding in OUTSIDE,
                "binding_line": info["line"] if info else None,
                "binding_rhs_kind": info["rhs_kind"] if info else None,
                "names_a_counted_row_key": bool(named),
                "named_read_lines": [r["line"] for r in named],
                "position_vs_the_named_line": (
                    position_of(site["line"], named[0]["line"]) if named else None),
                "per_read_line": per_line,
            })
        entry["depth1_sites"].sort(key=lambda s: (s["line"], s["column"]))
        for site in got["sites"]:
            owner = e640.innermost_owner(spans, site["line"])
            if owner is None or owner["qualname"] != span["qualname"]:
                continue
            row = e640.site_row(site)
            if not row["any_member_is_write"]:
                continue
            shallow = [m for m in site["members"] if m["depth"] == 1 and m["key"]]
            hit = [r for r in read_lines
                   if r["key"] and not r["key_is_computed"]
                   and any(m["key"] == r["key"] for m in shallow)]
            if not hit:
                continue
            entry["depth2_stores_indexing_into_a_counted_key"].append({
                "line": site["line"], "column": site["column"],
                "depth_pair": row["depth_pair"],
                "outer_key": row["outer_key"], "inner_key": row["inner_key"],
                "shallow_keys": sorted({m["key"] for m in shallow}),
                "names_a_counted_row_key": True,
                "named_read_lines": [r["line"] for r in hit],
            })
        entry["depth2_stores_indexing_into_a_counted_key"].sort(
            key=lambda s: (s["line"], s["column"]))
        out.append(entry)
    out.sort(key=lambda e: (e["module"], e["start"]))
    counts = counts_of(out)
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("for every one-depth Subscript site in Store/Del context inside one of E633's "
                   "counted functions, publish its key (literal or computed), the container it "
                   "writes through and that container's binding; join each site to every counted "
                   "read line of the same function to record whether it names that line's key and "
                   "whether it sits before/on/after it; plus a re-read of E640's two-depth write "
                   "sites whose depth-1 member names a counted key"),
        "population_source": ("%d counted function(s) machine-read from %s, %d counted read "
                              "line(s) among them" % (len(functions), SOURCE_FACE,
                                                      sum(len(f["read_lines"]) for f in out))),
        "counts": counts,
        "functions": out,
        "limits": [
            "a 'depth-1 site' is a Subscript whose depth from its leftmost name is 1 and whose "
            "context is Store or Del; a store through an attribute (d[k].x = v) is not one, "
            "because the subscript there is read, not written",
            "a store at two depths puts the Store context on the OUTER subscript and the inner one "
            "reads, so 'ctxs' on a site is the contexts of the depth-1 Subscript(s) at that "
            "position and a two-depth store cannot be counted here by construction -- that is the "
            "blind spot this study exists to price, not an omission",
            "'names a counted row key' is key equality against the counted read lines of the SAME "
            "function; a site with a computed subscript is published with has_computed_key and can "
            "never be counted as a name match",
            "22 of the 32 sites subscript with an expression rather than a string constant, so this "
            "face's 'no site names a counted key' is a statement about literal spellings only: a "
            "computed subscript could equal the counted key at run time and no reader of this face "
            "can see that (seeded as E645), which is why the count is published beside the verdict",
            "the container binding reuses E641's resolver (parameter > loop target > local "
            "assignment > module scope > unresolved) and is name equality, not an alias proof",
            "the population of counted functions and of their read lines is E640's, not re-derived "
            "here: a second definition of 'counted line' would be free to drift from the published "
            "one",
        ],
    }
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts, out)
    return doc


def counts_of(functions):
    sites = [s for f in functions for s in f["depth1_sites"]]
    ctx_hist = {"del": 0, "store": 0}
    for s in sites:
        for c in s["ctxs"]:
            ctx_hist[c] = ctx_hist.get(c, 0) + 1
    bind_hist = {b: 0 for b in BINDINGS}
    for s in sites:
        bind_hist[s["binding"]] = bind_hist.get(s["binding"], 0) + 1
    named = [s for s in sites if s["names_a_counted_row_key"]]
    named_lines = {line for s in named for line in s["named_read_lines"]}
    indexing = [s for f in functions for s in f["depth2_stores_indexing_into_a_counted_key"]]
    by_position = {p: 0 for p in POSITIONS}
    for s in named:
        p = s["position_vs_the_named_line"]
        if p in by_position:
            by_position[p] += 1
    return {
        "counted_functions": len(functions),
        "counted_functions_with_a_scope_problem": sum(
            1 for f in functions if f.get("scope_problem")),
        "counted_read_lines": sum(len(f["read_lines"]) for f in functions),
        "counted_read_keys": len({k for f in functions for k in f["read_keys"]}),
        "depth1_write_sites": len(sites),
        "depth1_site_ctx_histogram": dict(sorted(ctx_hist.items())),
        "depth1_sites_with_a_computed_key": sum(1 for s in sites if s["has_computed_key"]),
        "depth1_sites_with_no_literal_key": sum(1 for s in sites if not s["keys"]),
        "depth1_container_binding_histogram": dict(sorted(bind_hist.items())),
        "depth1_sites_bound_from_outside_the_function": sum(
            1 for s in sites if s["bound_from_outside_the_function"]),
        "depth1_sites_bound_inside_the_function": sum(
            1 for s in sites if s["binding"] in ("loop_target", "local_assignment")),
        "depth1_sites_with_an_unresolved_container": sum(
            1 for s in sites if s["binding"] == "unresolved"),
        "distinct_depth1_containers": len({s["container"] for s in sites if s["container"]}),
        "functions_carrying_a_depth1_write_site": sum(
            1 for f in functions if f["depth1_sites"]),
        "depth1_sites_naming_a_counted_row_key": len(named),
        "counted_lines_whose_key_a_depth1_site_names": len(named_lines),
        "functions_whose_depth1_site_names_a_counted_key": sum(
            1 for f in functions
            if any(s["names_a_counted_row_key"] for s in f["depth1_sites"])),
        "depth1_named_sites_before_the_read_line": by_position["before"],
        "depth1_named_sites_on_the_read_line": by_position["on"],
        "depth1_named_sites_after_the_read_line": by_position["after"],
        "depth2_stores_indexing_into_a_counted_key": len(indexing),
        "counted_functions_with_no_site_at_all": sum(
            1 for f in functions if not f["depth1_sites"]
            and not f["depth2_stores_indexing_into_a_counted_key"]),
    }


def decide(c):
    if not c.get("depth1_write_sites"):
        return V_NO_DEPTH1_SITE
    if c.get("depth1_sites_naming_a_counted_row_key"):
        return V_NAMES_THE_COUNTED_KEY
    if c.get("depth2_stores_indexing_into_a_counted_key"):
        return V_INDEXES_INTO_THE_COUNTED_KEY
    return V_ONLY_OTHER_KEYS


def answer_of(c, functions):
    parts = []
    for f in functions:
        if not f["depth1_sites"]:
            continue
        spelled = ", ".join(
            "%s:%s" % (
                "/".join(s["keys"]) if s["keys"] else "computed",
                "names" if s["names_a_counted_row_key"] else s["binding"])
            for s in f["depth1_sites"])
        parts.append("%s:%s(%d depth-1 site(s), reads %s -> %s)"
                     % (f["module"], f["function"], len(f["depth1_sites"]),
                        ",".join(str(r["key"]) for r in f["read_lines"]) or "-", spelled))
    return ("%d counted function(s), %d carrying a depth-1 store/delete site, %d site(s) total "
            "(ctx %s); containers bind as %s; %d name a counted row key, %d counted line(s) "
            "affected, positions before/on/after %d/%d/%d; %d two-depth store(s) index into a "
            "counted key. %s"
            % (c.get("counted_functions"), c.get("functions_carrying_a_depth1_write_site"),
               c.get("depth1_write_sites"),
               json.dumps(c.get("depth1_site_ctx_histogram") or {}, sort_keys=True),
               json.dumps(c.get("depth1_container_binding_histogram") or {}, sort_keys=True),
               c.get("depth1_sites_naming_a_counted_row_key"),
               c.get("counted_lines_whose_key_a_depth1_site_names"),
               c.get("depth1_named_sites_before_the_read_line"),
               c.get("depth1_named_sites_on_the_read_line"),
               c.get("depth1_named_sites_after_the_read_line"),
               c.get("depth2_stores_indexing_into_a_counted_key"),
               " | ".join(parts)))


COUNT_KEYS = (
    "counted_functions", "counted_functions_with_a_scope_problem", "counted_read_lines",
    "counted_read_keys", "depth1_write_sites", "depth1_site_ctx_histogram",
    "depth1_sites_with_a_computed_key", "depth1_sites_with_no_literal_key",
    "depth1_container_binding_histogram",
    "depth1_sites_bound_from_outside_the_function",
    "depth1_sites_bound_inside_the_function", "depth1_sites_with_an_unresolved_container",
    "distinct_depth1_containers", "functions_carrying_a_depth1_write_site",
    "depth1_sites_naming_a_counted_row_key", "counted_lines_whose_key_a_depth1_site_names",
    "functions_whose_depth1_site_names_a_counted_key",
    "depth1_named_sites_before_the_read_line", "depth1_named_sites_on_the_read_line",
    "depth1_named_sites_after_the_read_line", "depth2_stores_indexing_into_a_counted_key",
    "counted_functions_with_no_site_at_all",
)


def face_problems(face):
    problems = []
    if not face:
        return ["face is absent or empty"]
    functions = face.get("functions") or []
    c = face.get("counts") or {}
    live = counts_of(functions)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the functions" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for f in functions:
        expected = f.get("e640_read_lines")
        if expected is not None and expected != len(f["read_lines"]):
            problems.append("%s:%s publishes %d read lines where E640 publishes %d"
                            % (f["module"], f["function"], len(f["read_lines"]), expected))
            break
        for s in f["depth1_sites"]:
            if not (f["start"] <= s["line"] <= f["end"]):
                problems.append("%s:%s publishes a depth-1 site outside its own span"
                                % (f["module"], f["function"]))
                break
            if s["binding"] not in BINDINGS:
                problems.append("%s:%s has an unknown binding %r"
                                % (f["module"], f["function"], s["binding"]))
                break
            if not s["ctxs"] or set(s["ctxs"]) - {"store", "del"}:
                problems.append("%s:%s has a context outside the vocabulary"
                                % (f["module"], f["function"]))
                break
            if s["bound_from_outside_the_function"] != (s["binding"] in OUTSIDE):
                problems.append("%s:%s has an outside flag its binding contradicts"
                                % (f["module"], f["function"]))
                break
            if s["names_a_counted_row_key"] and not set(s["keys"]) & set(f["read_keys"]):
                problems.append("%s:%s claims a row-key name its keys do not carry"
                                % (f["module"], f["function"]))
                break
            if s["has_computed_key"] and s["names_a_counted_row_key"] and not s["keys"]:
                problems.append("%s:%s names a key through a computed subscript"
                                % (f["module"], f["function"]))
                break
            positions = [r["position"] for r in s["per_read_line"]]
            if any(p not in POSITIONS for p in positions):
                problems.append("%s:%s publishes a position outside the vocabulary"
                                % (f["module"], f["function"]))
                break
            if len(s["per_read_line"]) != len(f["read_lines"]):
                problems.append("%s:%s does not join every read line"
                                % (f["module"], f["function"]))
                break
    if face.get("verdict") == V_NAMES_THE_COUNTED_KEY \
            and not c.get("depth1_sites_naming_a_counted_row_key"):
        problems.append("the naming verdict is not the one its counts force")
    if face.get("verdict") == V_ONLY_OTHER_KEYS and (
            c.get("depth1_sites_naming_a_counted_row_key")
            or c.get("depth2_stores_indexing_into_a_counted_key")):
        problems.append("the other-keys verdict hides a naming or indexing site")
    if face.get("verdict") == V_NO_DEPTH1_SITE and c.get("depth1_write_sites"):
        problems.append("the verdict says no depth-1 site while the face carries them")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: functions=%d with_depth1=%d sites=%d named=%d lines_named=%d indexing=%d"
        % (c["counted_functions"], c["functions_carrying_a_depth1_write_site"],
           c["depth1_write_sites"], c["depth1_sites_naming_a_counted_row_key"],
           c["counted_lines_whose_key_a_depth1_site_names"],
           c["depth2_stores_indexing_into_a_counted_key"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


def verify(face=None, out_dir=None):
    face = face or json.load(io.open(os.path.join(out_dir or OUTDIR, FACE), encoding="utf-8"))
    return face_problems(face)


# ---------------------------------------------------------------- selftest
def _sites(src):
    return depth1_write_sites(ast.parse(src))


def _classify(src, line, column, fn_line=1):
    tree = ast.parse(src)
    fnode = e641.function_node(tree, {"qualname": "f", "start": fn_line})
    assert fnode is not None, "fixture function not found"
    index = e641.binding_index(fnode, tree)
    node = site_node(tree, line, column)
    assert node is not None, "fixture site not found"
    container, chain = e641.container_chain(node)
    info = index.get(container) if container else None
    return container, chain, (info or {}).get("binding", "unresolved"), (info or {})


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

    def a_one_depth_store_is_a_site():
        got = _sites("P['days'] = 1\n")
        assert len(got) == 1, got
        assert got[0]["keys"] == ["days"], got
        assert got[0]["ctxs"] == ["store"], got

    def a_one_depth_delete_is_a_site():
        got = _sites("del P['days']\n")
        assert len(got) == 1 and got[0]["ctxs"] == ["del"], got

    def an_augmented_store_counts_as_a_store():
        got = _sites("P['days'] += 1\n")
        assert len(got) == 1 and got[0]["ctxs"] == ["store"], got

    def a_two_depth_store_is_not_a_one_depth_site():
        got = _sites("P['days']['x'] = 1\n")
        assert got == [], got

    def a_one_depth_load_is_not_a_site():
        got = _sites("v = P['days']\n")
        assert got == [], got

    def a_computed_key_is_published_as_computed():
        got = _sites("P[k] = 1\n")
        assert len(got) == 1, got
        assert got[0]["has_computed_key"] is True, got
        assert got[0]["keys"] == [], got

    def a_parameter_container_is_a_parameter():
        c, chain, b, _ = _classify("def f(P):\n    P['days'] = 1\n", 2, 4)
        assert (c, b) == ("P", "parameter"), (c, b)

    def a_local_dict_container_is_a_local_assignment():
        c, chain, b, info = _classify("def f():\n    d = {}\n    d['days'] = 1\n", 3, 4)
        assert (c, b) == ("d", "local_assignment"), (c, b)
        assert info["rhs_kind"] == "dict_literal", info

    def positions_are_before_on_and_after():
        assert position_of(3, 5) == "before"
        assert position_of(5, 5) == "on"
        assert position_of(7, 5) == "after"

    def counts_add_up():
        functions = [{
            "module": "a.py", "function": "f", "start": 1, "end": 9,
            "read_lines": [{"line": 5, "key": "days", "receiver": "P",
                            "key_is_computed": False}],
            "read_keys": ["days"], "e640_read_lines": 1, "scope_problem": None,
            "depth1_sites": [{
                "line": 3, "column": 4, "ctxs": ["store"], "keys": ["days"],
                "has_computed_key": False, "container": "P", "container_chain": [],
                "binding": "parameter", "bound_from_outside_the_function": True,
                "binding_line": 1, "binding_rhs_kind": None,
                "names_a_counted_row_key": True, "named_read_lines": [5],
                "position_vs_the_named_line": "before",
                "per_read_line": [{"read_line": 5, "key": "days",
                                   "names_this_lines_key": True, "position": "before"}],
            }],
            "depth2_stores_indexing_into_a_counted_key": [],
        }]
        c = counts_of(functions)
        assert c["counted_functions"] == 1, c
        assert c["counted_read_lines"] == 1, c
        assert c["depth1_write_sites"] == 1, c
        assert c["depth1_site_ctx_histogram"] == {"del": 0, "store": 1}, c
        assert c["depth1_sites_naming_a_counted_row_key"] == 1, c
        assert c["counted_lines_whose_key_a_depth1_site_names"] == 1, c
        assert c["depth1_named_sites_before_the_read_line"] == 1, c
        assert c["functions_carrying_a_depth1_write_site"] == 1, c
        assert decide(c) == V_NAMES_THE_COUNTED_KEY, decide(c)

    def the_indexing_verdict_needs_a_two_depth_store():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [{"line": 5, "key": "days", "receiver": "P",
                                      "key_is_computed": False}],
                      "read_keys": ["days"], "e640_read_lines": 1, "scope_problem": None,
                      "depth1_sites": [{"line": 3, "column": 4, "ctxs": ["store"],
                                        "keys": ["other"], "has_computed_key": False,
                                        "container": "P", "container_chain": [],
                                        "binding": "parameter",
                                        "bound_from_outside_the_function": True,
                                        "binding_line": 1, "binding_rhs_kind": None,
                                        "names_a_counted_row_key": False,
                                        "named_read_lines": [],
                                        "position_vs_the_named_line": None,
                                        "per_read_line": [{"read_line": 5, "key": "days",
                                                           "names_this_lines_key": False,
                                                           "position": "before"}]}],
                      "depth2_stores_indexing_into_a_counted_key": [
                          {"line": 7, "column": 4, "names_a_counted_row_key": True,
                           "named_read_lines": [5]}]}]
        c = counts_of(functions)
        assert decide(c) == V_INDEXES_INTO_THE_COUNTED_KEY, decide(c)

    def the_other_keys_verdict_is_reachable():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [{"line": 5, "key": "days", "receiver": "P",
                                      "key_is_computed": False}],
                      "read_keys": ["days"], "e640_read_lines": 1, "scope_problem": None,
                      "depth1_sites": [{"line": 3, "column": 4, "ctxs": ["store"],
                                        "keys": ["other"], "has_computed_key": False,
                                        "container": "P", "container_chain": [],
                                        "binding": "local_assignment",
                                        "bound_from_outside_the_function": False,
                                        "binding_line": 2, "binding_rhs_kind": "dict_literal",
                                        "names_a_counted_row_key": False,
                                        "named_read_lines": [],
                                        "position_vs_the_named_line": None,
                                        "per_read_line": [{"read_line": 5, "key": "days",
                                                           "names_this_lines_key": False,
                                                           "position": "before"}]}],
                      "depth2_stores_indexing_into_a_counted_key": []}]
        c = counts_of(functions)
        assert decide(c) == V_ONLY_OTHER_KEYS, decide(c)
        assert face_problems({"functions": functions, "counts": c,
                              "verdict": V_ONLY_OTHER_KEYS}) == []

    def the_empty_verdict_is_reachable():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [{"line": 5, "key": "days", "receiver": "P",
                                      "key_is_computed": False}],
                      "read_keys": ["days"], "e640_read_lines": 1, "scope_problem": None,
                      "depth1_sites": [],
                      "depth2_stores_indexing_into_a_counted_key": []}]
        c = counts_of(functions)
        assert decide(c) == V_NO_DEPTH1_SITE, decide(c)
        assert c["counted_functions_with_no_site_at_all"] == 1, c

    def a_tampered_count_is_refused():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [{"line": 5, "key": "days", "receiver": "P",
                                      "key_is_computed": False}],
                      "read_keys": ["days"], "e640_read_lines": 1, "scope_problem": None,
                      "depth1_sites": [],
                      "depth2_stores_indexing_into_a_counted_key": []}]
        face = {"functions": functions, "counts": counts_of(functions),
                "verdict": V_NO_DEPTH1_SITE}
        face["counts"]["depth1_write_sites"] = 7
        problems = face_problems(face)
        assert problems and "counts.depth1_write_sites" in problems[0], problems

    def a_site_outside_its_span_is_refused():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 4,
                      "read_lines": [{"line": 3, "key": "days", "receiver": "P",
                                      "key_is_computed": False}],
                      "read_keys": ["days"], "e640_read_lines": 1, "scope_problem": None,
                      "depth1_sites": [{"line": 9, "column": 4, "ctxs": ["store"],
                                        "keys": ["days"], "has_computed_key": False,
                                        "container": "P", "container_chain": [],
                                        "binding": "parameter",
                                        "bound_from_outside_the_function": True,
                                        "binding_line": 1, "binding_rhs_kind": None,
                                        "names_a_counted_row_key": True,
                                        "named_read_lines": [3],
                                        "position_vs_the_named_line": "after",
                                        "per_read_line": [{"read_line": 3, "key": "days",
                                                           "names_this_lines_key": True,
                                                           "position": "after"}]}],
                      "depth2_stores_indexing_into_a_counted_key": []}]
        problems = face_problems({"functions": functions, "counts": counts_of(functions),
                                  "verdict": V_NAMES_THE_COUNTED_KEY})
        assert any("outside its own span" in p for p in problems), problems

    def the_published_face_re_derives():
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("SKIP :: the published face is absent")
            return
        face = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(face)
        assert not problems, problems[:3]

    for name, fn in [
        ("a one-depth store is a site", a_one_depth_store_is_a_site),
        ("a one-depth delete is a site", a_one_depth_delete_is_a_site),
        ("an augmented store counts as a store", an_augmented_store_counts_as_a_store),
        ("a two-depth store is not a one-depth site",
         a_two_depth_store_is_not_a_one_depth_site),
        ("a one-depth load is not a site", a_one_depth_load_is_not_a_site),
        ("a computed key is published as computed", a_computed_key_is_published_as_computed),
        ("a parameter container is a parameter", a_parameter_container_is_a_parameter),
        ("a local dict container is a local assignment",
         a_local_dict_container_is_a_local_assignment),
        ("positions are before, on and after", positions_are_before_on_and_after),
        ("counts add up", counts_add_up),
        ("the indexing verdict needs a two-depth store",
         the_indexing_verdict_needs_a_two_depth_store),
        ("the other-keys verdict is reachable", the_other_keys_verdict_is_reachable),
        ("the empty verdict is reachable", the_empty_verdict_is_reachable),
        ("a tampered count is refused", a_tampered_count_is_refused),
        ("a site outside its own span is refused", a_site_outside_its_span_is_refused),
        ("the published face re-derives", the_published_face_re_derives),
    ]:
        leg(name, fn)

    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "verify":
        problems = verify()
        for p in problems:
            say("verify: " + p)
        say("verify: problems=%d" % len(problems))
        return 0 if not problems else 1
    doc, _ = build()
    if args.mode == "check":
        problems = face_problems(doc)
        for p in problems:
            say("check: " + p)
        say("check: problems=%d" % len(problems))
        return 0 if not problems else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())