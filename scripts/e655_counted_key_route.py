"""E655 -- E652's single loader route: does it read or write the counted key it spells?

E652 published 23 modules that spell a counted read module, 14 of them also carrying a counted row
key, and exactly one that reaches its module through a string a loader consumes.  "Carries the key"
is a file-level fact: it says the key is spelled somewhere, not what that site does with it and not
whether the object it writes is the object the imported module's counted read line reads.

Three arms are published separately so each can be re-derived on its own:

  static  -- every string constant equal to a counted key, with the syntactic role of its parent; for
             a dict-literal key the root of the assignment target and that root's own definition are
             published, so "the write reaches the reader's container" is a claim with a printed bridge
  call    -- the loader's measured string, every attribute called on the handle it binds, and the
             counted read lines that live inside those attributes
  runtime -- the speller is executed twice (plain and ``--doctor``) under a line tracer scoped to the
             imported module; a counted read line counts as hit when an executed line falls inside the
             statement span it belongs to, because a multi-line call reports only its first line

  python scripts/e655_counted_key_route.py            # rebuild the face
  python scripts/e655_counted_key_route.py check      # rebuild + gate
  python scripts/e655_counted_key_route.py verify     # gate the published face
  python scripts/e655_counted_key_route.py selftest
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "STRINGROUTEKEY.json"
LATEST = "stringroutekey_latest.json"
STUDY = "E655_string_route_key"
SOURCE_FACE = "results/state_tilt/STRINGARMCENSUS.json"
SELF_PARTS = ("e655_", "run_e655_", "_r1673")
MAX_SITES_PER_ROUTE = 24
SOURCE_TRUNC = 200

import e647_string_reach as e647  # noqa: E402
import e648_keygenericity as e648  # noqa: E402
import e652_string_arm_census as e652  # noqa: E402

LOADER_NAMES = {"import_module", "load_module", "__import__", "run_path",
                "spec_from_file_location", "exec_module"}
ROLE_ORDER = ("dict_literal_key", "subscript_key", "call_argument", "comparison",
              "string_constant", "other_string")

V_NO_ROUTE = (
    "E652_publishes_no_loader_reached_speller,_so_the_route_this_study_was_written_to_price_does_"
    "not_exist_on_the_current_tree")
V_NO_READ_LINE = (
    "the_route_names_a_module_that_carries_no_counted_read_line_in_the_population_E638_joins,_so_"
    "there_is_no_reader_for_a_key_to_reach")
V_DOES_NOT_EXECUTE = (
    "the_route_binds_the_module_and_calls_into_it,_but_no_counted_read_line_of_the_named_module_is_"
    "reached_in_either_arm,_so_the_string_route_ends_before_the_read")
V_ANOTHER_OBJECT = (
    "the_route_does_execute_a_counted_read_line,_but_no_key_the_speller_writes_is_the_container_that_"
    "line_reads,_so_the_same_key_name_is_present_on_two_different_objects")
V_FLAG_BRANCH = (
    "the_route_executes_the_counted_read_line_and_the_dict_key_the_speller_writes_is_the_container_"
    "that_line_reads,_but_the_write_sits_behind_a_branch_only_taken_when_the_doctor_flag_is_set,_so_"
    "the_invisible_arm_carries_a_key_that_is_both_written_and_read_inside_one_call_chain_and_the_"
    "write_is_diagnostic_only")
V_DEFAULT_PATH = (
    "the_route_executes_the_counted_read_line_and_the_dict_key_the_speller_writes_is_the_container_"
    "that_line_reads_on_the_default_path,_so_the_invisible_arm_carries_a_key_that_is_both_written_"
    "and_read_inside_one_call_chain")

WRAPPER = r'''
import json, os, runpy, sys

speller, marker, out = sys.argv[1], sys.argv[2], sys.argv[3]
targets = {os.path.abspath(p) for p in sys.argv[4:]}
hits = {}

def _tracer(frame, event, arg):
    name = frame.f_code.co_filename or ""
    path = os.path.abspath(name) if name else ""
    if path in targets:
        if event == "line":
            hits.setdefault(path, set()).add(frame.f_lineno)
        return _tracer
    return None

sys.settrace(_tracer)
sys.argv = [speller] + ([marker] if marker else [])
rc = 0
try:
    runpy.run_path(speller, run_name="__main__")
except SystemExit as exc:
    code = exc.code
    rc = int(code) if isinstance(code, int) else (0 if code is None else 1)
except BaseException:
    rc = -1
finally:
    sys.settrace(None)
payload = {"rc": rc, "hits": {k: sorted(v) for k, v in hits.items()}}
with open(out, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(payload))
'''


def say(line):
    sys.stdout.write(line + "\n")


# ---------------------------------------------------------------- ast helpers
def _line_source(lines, node):
    start = max(0, (node.lineno or 1) - 1)
    end = node.end_lineno or node.lineno or (start + 1)
    return " ".join(ln.strip() for ln in lines[start:end])[:SOURCE_TRUNC]


def _leftmost_name(node):
    while isinstance(node, (ast.Subscript, ast.Attribute, ast.Starred)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return ("%s.%s" % (base, node.attr)) if base else node.attr
    return None


def role_of(parent, node):
    if isinstance(parent, ast.Dict) and any(node is k for k in parent.keys):
        return "dict_literal_key"
    if isinstance(parent, ast.Subscript) and node is parent.slice:
        return "subscript_key"
    if isinstance(parent, ast.Call) and any(node is a for a in parent.args):
        return "call_argument"
    if isinstance(parent, ast.Compare):
        return "comparison"
    if isinstance(parent, (ast.Assign, ast.AnnAssign)):
        return "string_constant"
    return "other_string"


def assign_root(parents, node):
    """(root name, Assign node) for the statement a dict literal is written into."""
    cur = node
    while cur is not None and cur in parents:
        par = parents[cur]
        if isinstance(par, ast.Assign):
            return _leftmost_name(par.targets[0]), par
        if isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module,
                            ast.Lambda)):
            return None, None
        cur = par
    return None, None


def gate_of(parents, node):
    """'doctor_gated' when any enclosing If tests the doctor flag, else 'ungated'."""
    cur, seen = node, []
    while cur is not None and cur in parents:
        par = parents[cur]
        if isinstance(par, ast.If):
            seen.append("doctor" in ast.dump(par.test))
        if isinstance(par, (ast.FunctionDef, ast.Lambda, ast.Module)):
            break
        cur = par
    return "doctor_gated" if any(seen) else "ungated"


def name_definitions(tree, lines):
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            out.setdefault(node.targets[0].id, _line_source(lines, node))
    return out


def enclosing_call(parents, node, limit=8):
    cur, depth = node, 0
    while cur is not None and cur in parents and depth < limit:
        par = parents[cur]
        if isinstance(par, ast.Call) and any(cur is a for a in par.args):
            return par
        cur, depth = par, depth + 1
    return None


def loader_bindings(tree, lines):
    """name -> the measured string a loader was handed when that name was bound."""
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, value = node.targets[0], node.value
        if not (isinstance(target, ast.Name) and isinstance(value, ast.Call)):
            continue
        name = _call_name(value.func) or ""
        if name.split(".")[-1] not in LOADER_NAMES:
            continue
        if not (value.args and isinstance(value.args[0], ast.Constant)
                and isinstance(value.args[0].value, str)):
            continue
        out[target.id] = {"loader": name, "dotted": value.args[0].value,
                          "line": node.lineno, "source": _line_source(lines, node)}
    return out


def call_sites(tree, bound, lines):
    """attribute name -> the call sites on that handle, with the names their arguments carry."""
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                and func.value.id == bound):
            continue
        names = sorted({n.id for a in node.args for n in ast.walk(a) if isinstance(n, ast.Name)})
        out.setdefault(func.attr, []).append({
            "line": node.lineno, "call": _line_source(lines, node), "argument_names": names})
    return out


def key_sites(tree, parents, keys, lines, unresolved_spans=None):
    """Every string constant equal to a counted key, with the role its parent gives it."""
    defs = name_definitions(tree, lines)
    spans = unresolved_spans or []
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if node.value not in keys:
            continue
        parent = parents.get(node)
        site = {"key": node.value, "line": node.lineno, "column": node.col_offset,
                "role": role_of(parent, node), "source": _line_source(lines, node),
                "inside_an_unresolved_string":
                    any(start <= node.lineno <= end for start, end in spans)}
        if site["role"] == "dict_literal_key":
            root, _assign = assign_root(parents, parent)
            site["dict_root"] = root
            site["dict_root_definition"] = defs.get(root) if root else None
            site["branch"] = gate_of(parents, parent)
        elif site["role"] == "call_argument":
            call = enclosing_call(parents, node)
            if call is not None and isinstance(call.func, ast.Attribute):
                base = call.func.value
                names = sorted({n.id for n in ast.walk(base) if isinstance(n, ast.Name)})
                site["receiver_names"] = names
                site["receiver_definitions"] = [defs[n] for n in names if n in defs]
        out.append(site)
    out.sort(key=lambda s: (s["line"], s["column"]))
    return out


# ---------------------------------------------------------------- runtime arm
def statement_span(path, line):
    try:
        tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
    except (OSError, SyntaxError):
        return line, line
    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue
        end = node.end_lineno or node.lineno
        if node.lineno <= line <= end:
            width = end - node.lineno
            if best is None or width < best[2]:
                best = (node.lineno, end, width)
    return (best[0], best[1]) if best else (line, line)


def run_traced(speller_abs, target_paths, extra, root):
    """Execute the speller under a line tracer scoped to target_paths; hits come back as line sets."""
    fd, out = tempfile.mkstemp(prefix="e655_trace_", suffix=".json")
    os.close(fd)
    try:
        env = dict(os.environ)
        env["PYTHONPATH"] = (os.path.join(root, "scripts") + os.pathsep
                             + env.get("PYTHONPATH", ""))
        cmd = [sys.executable, "-c", WRAPPER, speller_abs,
               (extra[0] if extra else ""), out] + list(target_paths)
        try:
            proc = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True,
                                  timeout=240)
        except subprocess.TimeoutExpired:
            return {"rc": None, "hits": {}, "error": "timeout", "stdout_tail": "",
                    "stderr_tail": ""}
        try:
            got = json.load(io.open(out, encoding="utf-8"))
        except (OSError, ValueError):
            got = {"rc": None, "hits": {}, "error": (proc.stderr or "")[-400:]}
        got["stdout_tail"] = (proc.stdout or "")[-200:]
        got["stderr_tail"] = (proc.stderr or "")[-400:]
        return got
    finally:
        try:
            os.remove(out)
        except OSError:
            pass


# ---------------------------------------------------------------- one route
def analyse(root, row, reads, keys, runtime=True):
    speller_rel = row.get("module") or ""
    speller_abs = os.path.join(root, speller_rel)
    src = io.open(speller_abs, encoding="utf-8", errors="replace").read()
    lines = src.splitlines()
    tree = ast.parse(src)
    parents = e647.parents_of(tree)

    unresolved = e647.collect_strings(tree)[1] or []
    sites = key_sites(tree, parents, keys, lines,
                      unresolved_spans=[statement_span(speller_abs, u["line"])
                                        for u in unresolved if u.get("line")])
    bindings = loader_bindings(tree, lines)
    calls = {}
    for bound in sorted(bindings):
        for attr, got in call_sites(tree, bound, lines).items():
            calls.setdefault(attr, []).extend(got)

    read_modules = sorted({rm for rm in (row.get("read_modules") or [])})
    held = {rm: [r for r in reads if r.get("module") == rm] for rm in read_modules}
    held = {rm: got for rm, got in held.items() if got}

    called_attrs = set(calls)
    read_lines = []
    for rm, got in sorted(held.items()):
        path = os.path.join(root, rm)
        for r in got:
            span = statement_span(path, r["line"])
            read_lines.append({
                "module": rm, "line": r["line"], "function": r.get("function"),
                "key": r.get("key"), "receiver": r.get("receiver"),
                "span": list(span),
                "inside_a_called_attribute": (r.get("function") in called_attrs),
            })

    runtime_arms = {}
    if runtime and read_lines:
        targets = [os.path.join(root, rm) for rm in sorted(held)]
        for arm, extra in (("plain", []), ("doctor", ["--doctor"])):
            got = run_traced(speller_abs, targets, extra, root)
            hits = {}
            for path, rows in (got.get("hits") or {}).items():
                hits[os.path.relpath(path, root).replace("\\", "/")] = rows
            runtime_arms[arm] = {"rc": got.get("rc"), "hits": hits,
                                 "error": got.get("error"),
                                 "stderr_tail": got.get("stderr_tail")
                                 if got.get("rc") not in (0, 1) else ""}
        for r in read_lines:
            rm_hits = runtime_arms.get("plain", {}).get("hits", {}).get(r["module"]) or []
            dm_hits = runtime_arms.get("doctor", {}).get("hits", {}).get(r["module"]) or []
            start, end = r["span"]
            r["hit_plain"] = any(start <= ln <= end for ln in rm_hits)
            r["hit_doctor"] = any(start <= ln <= end for ln in dm_hits)

    read_fn_names = {r["function"] for r in read_lines if r.get("function")}
    reader_args = set()
    for attr in sorted(read_fn_names & called_attrs):
        for site in calls.get(attr) or []:
            reader_args.update(site.get("argument_names") or [])

    bridges = []
    for site in sites:
        if site["role"] != "dict_literal_key":
            continue
        root_name = site.get("dict_root")
        definition = site.get("dict_root_definition") or ""
        definition_names = set()
        if definition:
            try:
                definition_names = {n.id for n in ast.walk(ast.parse(definition))
                                    if isinstance(n, ast.Name)}
            except SyntaxError:
                definition_names = set()
        reaches = bool(root_name and (root_name in reader_args
                                      or (definition_names & reader_args)))
        bridges.append({
            "key": site["key"],
            "line": site["line"],
            "dict_root": root_name,
            "dict_root_definition": definition,
            "reader_arguments": sorted(reader_args),
            "reaches_the_reader_container": reaches,
            "branch": site.get("branch"),
            "source": site["source"],
        })

    role_hist = _hist([s["role"] for s in sites])
    published = sites[:MAX_SITES_PER_ROUTE]
    return {
        "speller": speller_rel,
        "module_class": e652.e646.module_class(speller_rel),
        "read_modules": read_modules,
        "loader_bindings": [bindings[b] for b in sorted(bindings)],
        "call_attributes": sorted(calls),
        "call_sites": {k: calls[k][:6] for k in sorted(calls)},
        "carried_keys": sorted({s["key"] for s in sites}),
        "key_site_count": len(sites),
        "sites_by_role": {k: role_hist[k] for k in ROLE_ORDER if k in role_hist},
        "sites": published,
        "sites_elided": max(0, len(sites) - len(published)),
        "counted_read_lines": read_lines,
        "counted_read_lines_inside_a_called_attribute":
            sum(1 for r in read_lines if r["inside_a_called_attribute"]),
        "runtime": runtime_arms,
        "read_lines_executed_plain": sum(1 for r in read_lines if r.get("hit_plain")),
        "read_lines_executed_doctor": sum(1 for r in read_lines if r.get("hit_doctor")),
        "bridges": bridges,
        "writes_that_reach_the_reader_container":
            sum(1 for b in bridges if b["reaches_the_reader_container"]),
        "writes_on_a_doctor_gated_branch":
            sum(1 for b in bridges if b["branch"] == "doctor_gated"),
        "e652_row_reproduced": _reproduce(sites, row),
    }


def _hist(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return {k: out[k] for k in sorted(out)}


def _reproduce(sites, row):
    """E652's file-level key list against this walk.

    This walk reads every string constant; E652 reads E647's collect_strings, which hands back a
    percent-formatted expression as one unresolved handle and therefore cannot see a constant that
    sits inside that subtree.  A key this walk finds and E652 does not is accepted only when every
    site of it falls on a line E647 published as unresolved; a key E652 published that this walk
    cannot find is a real disagreement and is never explained away.
    """
    theirs = sorted(row.get("counted_keys_named") or [])
    mine = sorted({s["key"] for s in sites})
    missing = [k for k in theirs if k not in mine]
    extra = [k for k in mine if k not in theirs]
    explained = {}
    unexplained = []
    for key in extra:
        lines = sorted({s["line"] for s in sites if s["key"] == key})
        if lines and all(s["inside_an_unresolved_string"] for s in sites if s["key"] == key):
            explained[key] = lines
        else:
            unexplained.append(key)
    return {
        "counted_keys_named": theirs,
        "recomputed": mine,
        "missing_from_this_walk": missing,
        "extra_in_this_walk": extra,
        "extra_explained_by_e647s_unresolved_handle": explained,
        "extra_unexplained": unexplained,
        "agrees": not missing and not unexplained,
    }


# ---------------------------------------------------------------- measure
def measure(root=ROOT, strict=None, reads=None, runtime=True):
    reads = e648.read_population() if reads is None else reads
    keys = sorted({r["key"] for r in reads if r.get("key")})
    if strict is None:
        strict = _strict_rows(root)
    routes = [analyse(root, row, reads, keys, runtime=runtime) for row in strict]
    routes.sort(key=lambda r: r["speller"])

    counts = {
        "routes_measured": len(routes),
        "counted_read_lines_in_the_route":
            sum(len(r["counted_read_lines"]) for r in routes),
        "counted_read_lines_inside_a_called_attribute":
            sum(r["counted_read_lines_inside_a_called_attribute"] for r in routes),
        "routes_that_call_the_reader": sum(1 for r in routes if r["call_attributes"]),
        "read_lines_executed_plain": sum(r["read_lines_executed_plain"] for r in routes),
        "read_lines_executed_doctor": sum(r["read_lines_executed_doctor"] for r in routes),
        "routes_that_execute_a_counted_read_line":
            sum(1 for r in routes if r["read_lines_executed_plain"]
                or r["read_lines_executed_doctor"]),
        "carried_keys": len({k for r in routes for k in r["carried_keys"]}),
        "key_sites": sum(r["key_site_count"] for r in routes),
        "sites_by_role": _merge([r["sites_by_role"] for r in routes]),
        "writes_that_reach_the_reader_container":
            sum(r["writes_that_reach_the_reader_container"] for r in routes),
        "writes_on_a_doctor_gated_branch":
            sum(r["writes_on_a_doctor_gated_branch"] for r in routes),
        "routes_where_e652s_key_list_reproduces":
            sum(1 for r in routes if r["e652_row_reproduced"]["agrees"]),
        "keys_found_outside_e652s_list":
            sum(len(r["e652_row_reproduced"]["extra_in_this_walk"]) for r in routes),
    }
    volume = {
        "counted_read_lines": len(reads),
        "counted_read_modules": len({r["module"] for r in reads if r.get("module")}),
        "counted_row_keys": len(keys),
        "routes_from_e652": len(strict),
    }
    m = {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "method": (
            "for every speller E652 published as reaching its read module through a loader-consumed "
            "string, walk to each string constant equal to a counted key and classify the syntactic "
            "role of its parent; for a dict-literal key publish the root of the assignment target and "
            "that root's own definition; then bind the loader's measured string to the handle it "
            "binds, collect every attribute called on that handle, and keep the counted read lines "
            "that live inside those attributes; finally execute the speller twice (plain and "
            "--doctor) under a tracer scoped to the read module and price each counted read line as "
            "hit when an executed line falls inside its statement span"),
        "population_source": (
            "%d counted read line(s) in %d module(s) over %d key(s) from E638's join; %d loader-"
            "reached speller row(s) from E652"
            % (len(reads), volume["counted_read_modules"], volume["counted_row_keys"],
               len(strict))),
        "volume": volume,
        "counts": counts,
        "routes": routes,
        "limits": [
            "the bridge is one hop of index arithmetic: the dict's assignment root and that root's "
            "own definition are published, not a full data-flow proof, so a key written into a "
            "container built two or more hops away would be published as not reaching",
            "runtime hits are statement spans, not line numbers: CPython reports the first line of a "
            "multi-line call, so an un-span'd comparison would read three published read lines as "
            "two misses",
            "the doctor arm runs the speller with --doctor, which is a diagnostic mode; a write that "
            "only exists there is published as doctor_gated and is not a production write",
            "the route set is E652's and is re-derived by re-running its face, not re-censused here; "
            "e652_row_reproduced publishes whether this study's own key walk agrees with E652's "
            "file-level list, and a disagreement moves this face without moving E652's",
            "a key spelled inside a longer string (E652's token_contains_stem class) is not a key "
            "site here, because the site question is about container access and not about text",
            "E652's per-file key list comes from E647's collect_strings, which hands a "
            "percent-formatted expression back as one unresolved handle and cannot see a constant "
            "inside that subtree; this walk reads every constant, so a key it finds and E652 does "
            "not is published in extra_in_this_walk and accepted only when every one of its sites "
            "sits on a line E647 published as unresolved (keys_found_outside_e652s_list counts "
            "them). A key E652 published that this walk cannot find is a disagreement and gates red",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts, volume, routes)
    return m


def _merge(dicts):
    out = {}
    for d in dicts:
        for k, v in (d or {}).items():
            out[k] = out.get(k, 0) + v
    return {k: out[k] for k in ROLE_ORDER if k in out}


def _strict_rows(root=ROOT):
    path = os.path.join(root, SOURCE_FACE.replace("/", os.sep))
    if not os.path.exists(path):
        return []
    face = json.load(io.open(path, encoding="utf-8"))
    return [r for r in (face.get("rows") or []) if r.get("reach") in e652.LOADER_REACH]


def decide(c):
    if not c.get("routes_measured"):
        return V_NO_ROUTE
    if not c.get("counted_read_lines_in_the_route"):
        return V_NO_READ_LINE
    if not c.get("routes_that_execute_a_counted_read_line"):
        return V_DOES_NOT_EXECUTE
    if not c.get("writes_that_reach_the_reader_container"):
        return V_ANOTHER_OBJECT
    if c.get("writes_on_a_doctor_gated_branch"):
        return V_FLAG_BRANCH
    return V_DEFAULT_PATH


def answer_of(c, volume, routes):
    parts = []
    for r in routes:
        read_desc = ", ".join("line %d (%s, key %r) %s/%s"
                              % (x["line"], x["function"], x["key"],
                                 "hit" if x.get("hit_plain") else "miss",
                                 "hit" if x.get("hit_doctor") else "miss")
                              for x in r["counted_read_lines"])
        wrote = ", ".join("%r at line %d from %r%s"
                          % (b["key"], b["line"], b["dict_root"],
                             " (reaches the reader)" if b["reaches_the_reader_container"] else "")
                          for b in r["bridges"]) or "nothing"
        parts.append("%s: loads %s, calls %s, writes %s, reads %s"
                     % (r["speller"],
                        ", ".join(b["dotted"] for b in r["loader_bindings"]) or "no module",
                        ", ".join(r["call_attributes"]) or "no attribute",
                        wrote, read_desc or "no counted read line"))
    return ("%d loader route(s) over %d counted read line(s) / %d key(s); %d key site(s) by role %s; "
            "%d write(s) reach the reader's container; %d read line(s) hit on the plain arm and %d on "
            "the doctor arm; %s"
            % (c["routes_measured"], volume["counted_read_lines"], volume["counted_row_keys"],
               c["key_sites"], json.dumps(c["sites_by_role"], sort_keys=True),
               c["writes_that_reach_the_reader_container"], c["read_lines_executed_plain"],
               c["read_lines_executed_doctor"], " | ".join(parts)))


# ---------------------------------------------------------------- gate
def face_from(m):
    return {
        "study": m["study"],
        "date": m["date"],
        "evidence_cutoff": m["evidence_cutoff"],
        "source_face": m["source_face"],
        "method": m["method"],
        "population_source": m["population_source"],
        "volume": m["volume"],
        "counts": m["counts"],
        "routes": m["routes"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "routes_measured", "counted_read_lines_in_the_route",
    "counted_read_lines_inside_a_called_attribute", "routes_that_call_the_reader",
    "read_lines_executed_plain", "read_lines_executed_doctor",
    "routes_that_execute_a_counted_read_line", "carried_keys", "key_sites",
    "writes_that_reach_the_reader_container", "writes_on_a_doctor_gated_branch",
    "routes_where_e652s_key_list_reproduces", "keys_found_outside_e652s_list",
)


def live_counts(routes):
    return {
        "routes_measured": len(routes),
        "counted_read_lines_in_the_route": sum(len(r.get("counted_read_lines") or [])
                                               for r in routes),
        "counted_read_lines_inside_a_called_attribute":
            sum(r.get("counted_read_lines_inside_a_called_attribute") or 0 for r in routes),
        "routes_that_call_the_reader": sum(1 for r in routes if r.get("call_attributes")),
        "read_lines_executed_plain": sum(r.get("read_lines_executed_plain") or 0 for r in routes),
        "read_lines_executed_doctor": sum(r.get("read_lines_executed_doctor") or 0 for r in routes),
        "routes_that_execute_a_counted_read_line":
            sum(1 for r in routes if (r.get("read_lines_executed_plain") or 0)
                or (r.get("read_lines_executed_doctor") or 0)),
        "carried_keys": len({k for r in routes for k in (r.get("carried_keys") or [])}),
        "key_sites": sum(r.get("key_site_count") or 0 for r in routes),
        "sites_by_role": _merge([r.get("sites_by_role") or {} for r in routes]),
        "writes_that_reach_the_reader_container":
            sum(r.get("writes_that_reach_the_reader_container") or 0 for r in routes),
        "writes_on_a_doctor_gated_branch":
            sum(r.get("writes_on_a_doctor_gated_branch") or 0 for r in routes),
        "routes_where_e652s_key_list_reproduces":
            sum(1 for r in routes if (r.get("e652_row_reproduced") or {}).get("agrees")),
        "keys_found_outside_e652s_list":
            sum(len((r.get("e652_row_reproduced") or {}).get("extra_in_this_walk") or [])
                for r in routes),
    }


def face_problems(face):
    problems = []
    if not face:
        return ["face is absent or empty"]
    routes = face.get("routes") or []
    c = face.get("counts") or {}
    live = live_counts(routes)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s is not the route-derived value (%r vs %r)"
                            % (key, c.get(key), live.get(key)))
    if (c.get("sites_by_role") or {}) != (live.get("sites_by_role") or {}):
        problems.append("counts.sites_by_role is not the aggregate its routes force")
    if sum((c.get("sites_by_role") or {}).values()) != c.get("key_sites"):
        problems.append("the role histogram does not add up to the key sites")
    if (c.get("writes_that_reach_the_reader_container") or 0) > (
            c.get("sites_by_role", {}).get("dict_literal_key") or 0):
        problems.append("more writes reach the reader than there are dict-literal key sites")
    for r in routes:
        role_sum = sum((r.get("sites_by_role") or {}).values())
        if role_sum != r.get("key_site_count"):
            problems.append("route %r publishes a role histogram that does not add up"
                            % r.get("speller"))
            break
        if len(r.get("sites") or []) + (r.get("sites_elided") or 0) != r.get("key_site_count"):
            problems.append("route %r publishes %d site(s) + %r elided for %r site(s)"
                            % (r.get("speller"), len(r.get("sites") or []),
                               r.get("sites_elided"), r.get("key_site_count")))
            break
        reached = sum(1 for b in (r.get("bridges") or [])
                      if b.get("reaches_the_reader_container"))
        if reached != (r.get("writes_that_reach_the_reader_container") or 0):
            problems.append("route %r publishes a reach count its own bridges do not force"
                            % r.get("speller"))
            break
        gated = sum(1 for b in (r.get("bridges") or []) if b.get("branch") == "doctor_gated")
        if gated != (r.get("writes_on_a_doctor_gated_branch") or 0):
            problems.append("route %r publishes a doctor-gated count its own bridges do not force"
                            % r.get("speller"))
            break
        named = [x for x in (r.get("counted_read_lines") or []) if x.get("hit_plain")]
        if len(named) != (r.get("read_lines_executed_plain") or 0):
            problems.append("route %r publishes a plain hit count its own lines do not force"
                            % r.get("speller"))
            break
        namedd = [x for x in (r.get("counted_read_lines") or []) if x.get("hit_doctor")]
        if len(namedd) != (r.get("read_lines_executed_doctor") or 0):
            problems.append("route %r publishes a doctor hit count its own lines do not force"
                            % r.get("speller"))
            break
        if not (r.get("e652_row_reproduced") or {}).get("agrees"):
            reproduced = r.get("e652_row_reproduced") or {}
            problems.append("route %r does not reproduce E652's key list (missing %r, unexplained "
                            "%r)" % (r.get("speller"),
                                     reproduced.get("missing_from_this_walk"),
                                     reproduced.get("extra_unexplained")))
            break
        for site in (r.get("sites") or []):
            if site.get("role") not in ROLE_ORDER:
                problems.append("route %r publishes a role outside the frozen vocabulary: %r"
                                % (r.get("speller"), site.get("role")))
                break
    if decide(c) != face.get("verdict"):
        problems.append("the published verdict is not the one its own counts force")
    if face.get("verdict") == V_NO_ROUTE and routes:
        problems.append("the no-route verdict is published with route rows")
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
    say("run: routes=%d read_lines=%d key_sites=%d reach=%d plain_hits=%d doctor_hits=%d"
        % (c["routes_measured"], c["counted_read_lines_in_the_route"], c["key_sites"],
           c["writes_that_reach_the_reader_container"], c["read_lines_executed_plain"],
           c["read_lines_executed_doctor"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _fixture_root(files):
    root = tempfile.mkdtemp(prefix="e655_")
    for name, body in files.items():
        path = os.path.join(root, name)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return root


def _reads(line=4, key="verdict", module="scripts/read_mod.py", function="check"):
    return [{"module": module, "line": line, "function": function, "key": key, "receiver": "D"}]


def _row(speller="scripts/run_leg.py", read_module="scripts/read_mod.py", keys=("verdict",)):
    return {"module": speller, "reach": "import_string_reach", "read_modules": [read_module],
            "carries_a_counted_row_key": True, "counted_keys_named": list(keys)}


READ_MOD = ('def check(D):\n'
            '    rows = D.get("rows") or []\n'
            '    for r in rows:\n'
            '        if r["verdict"] != "ok":\n'
            '            return False\n'
            '    return True\n')

SAME_OBJECT = ('import importlib\n'
               'm = importlib.import_module("read_mod")\n'
               '\n'
               'def main():\n'
               '    doc = {"rows": [{"verdict": "ok"}]}\n'
               '    return m.check(doc)\n'
               '\n'
               'if __name__ == "__main__":\n'
               '    main()\n')


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL %s: %s" % (name, exc))

    def a_dict_key_is_a_write_site_with_its_root():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        got = analyse(root, _row(), _reads(), ["verdict"], runtime=False)
        writes = [s for s in got["sites"] if s["role"] == "dict_literal_key"]
        assert len(writes) == 1, writes
        assert writes[0]["dict_root"] == "doc", writes[0]
        assert "doc" in (writes[0]["dict_root_definition"] or ""), writes[0]

    def a_call_argument_is_not_a_write():
        body = ('import importlib\n'
                'm = importlib.import_module("read_mod")\n'
                'def main():\n'
                '    doc = {}\n'
                '    return (doc.get("rows") or {})\n')
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": body})
        got = analyse(root, _row(), _reads(), ["rows"], runtime=False)
        roles = [s["role"] for s in got["sites"]]
        assert roles == ["call_argument"], roles

    def the_write_reaches_the_reader_when_the_root_is_an_argument():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        got = analyse(root, _row(), _reads(), ["verdict"], runtime=False)
        assert got["writes_that_reach_the_reader_container"] == 1, got["bridges"]

    def another_object_is_not_the_reader_container():
        body = ('import importlib\n'
                'm = importlib.import_module("read_mod")\n'
                'def main():\n'
                '    other = {"rows": [{"verdict": "ok"}]}\n'
                '    doc = {"rows": []}\n'
                '    return m.check(doc)\n')
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": body})
        got = analyse(root, _row(), _reads(), ["verdict"], runtime=False)
        assert got["writes_that_reach_the_reader_container"] == 0, got["bridges"]

    def a_doctor_gated_write_is_published_as_gated():
        body = ('import importlib, sys\n'
                'm = importlib.import_module("read_mod")\n'
                'def main():\n'
                '    doc = {"rows": []}\n'
                '    if "--doctor" in sys.argv[1:]:\n'
                '        blk = doc["rows"]\n'
                '        blk.append({"verdict": "ok"})\n'
                '    return m.check(doc)\n')
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": body})
        got = analyse(root, _row(), _reads(), ["verdict"], runtime=False)
        assert got["writes_on_a_doctor_gated_branch"] == 1, got["bridges"]

    def the_runtime_arm_hits_the_read_line():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        got = analyse(root, _row(), _reads(), ["verdict"], runtime=True)
        assert got["read_lines_executed_plain"] == 1, (got["counted_read_lines"],
                                                      got["runtime"])

    def a_line_outside_the_span_is_not_a_hit():
        assert statement_span(os.path.join(ROOT, "scripts", "e647_string_reach.py"), 1)[0] >= 1
        start, end = statement_span(os.path.join(HERE, "e655_counted_key_route.py"), 100)
        assert start <= 100 <= end, (start, end)

    def a_reader_without_a_read_line_has_no_target():
        root = _fixture_root({"scripts/empty_mod.py": "X = 1\n",
                              "scripts/run_leg.py": 'import importlib\n'
                                                    'm = importlib.import_module("empty_mod")\n'})
        got = analyse(root, _row(read_module="scripts/empty_mod.py", keys=("verdict",)),
                      [], ["verdict"], runtime=False)
        assert got["counted_read_lines"] == [], got["counted_read_lines"]

    def the_empty_route_set_is_a_verdict():
        m = measure(strict=[], reads=_reads(), runtime=False)
        assert m["verdict"] == V_NO_ROUTE, m["verdict"]

    def the_face_re_adds_from_its_own_routes():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        doc = face_from(measure(root, strict=[_row()], reads=_reads(), runtime=True))
        assert face_problems(doc) == [], face_problems(doc)

    def a_tampered_count_is_refused():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        doc = face_from(measure(root, strict=[_row()], reads=_reads(), runtime=True))
        doc["counts"]["key_sites"] = 9
        assert any("key_sites" in p for p in face_problems(doc)), face_problems(doc)

    def a_tampered_verdict_is_refused():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        doc = face_from(measure(root, strict=[_row()], reads=_reads(), runtime=True))
        doc["verdict"] = V_ANOTHER_OBJECT
        assert any("verdict" in p for p in face_problems(doc)), face_problems(doc)

    def a_tampered_role_is_refused():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        doc = face_from(measure(root, strict=[_row()], reads=_reads(), runtime=True))
        doc["routes"][0]["sites"][0]["role"] = "not_a_role"
        assert any("role" in p for p in face_problems(doc)), face_problems(doc)

    def a_key_the_speller_does_not_spell_breaks_reproduction():
        root = _fixture_root({"scripts/read_mod.py": READ_MOD, "scripts/run_leg.py": SAME_OBJECT})
        m = measure(root, strict=[_row(keys=("verdict", "rows"))], reads=_reads(), runtime=False)
        assert m["counts"]["routes_where_e652s_key_list_reproduces"] == 0, m["counts"]

    leg("a dict key is a write site with its assignment root",
        a_dict_key_is_a_write_site_with_its_root)
    leg("a call argument is not a write", a_call_argument_is_not_a_write)
    leg("the write reaches the reader when the root is an argument",
        the_write_reaches_the_reader_when_the_root_is_an_argument)
    leg("another object is not the reader container", another_object_is_not_the_reader_container)
    leg("a doctor-gated write is published as gated", a_doctor_gated_write_is_published_as_gated)
    leg("the runtime arm hits the read line", the_runtime_arm_hits_the_read_line)
    leg("a line outside the statement span is not a hit", a_line_outside_the_span_is_not_a_hit)
    leg("a reader without a read line has no target", a_reader_without_a_read_line_has_no_target)
    leg("the empty route set is a verdict", the_empty_route_set_is_a_verdict)
    leg("the face re-adds from its own routes", the_face_re_adds_from_its_own_routes)
    leg("a tampered count is refused", a_tampered_count_is_refused)
    leg("a tampered verdict is refused", a_tampered_verdict_is_refused)
    leg("a tampered role is refused", a_tampered_role_is_refused)
    leg("a key the speller never spells breaks reproduction",
        a_key_the_speller_does_not_spell_breaks_reproduction)
    failed = [n for n, ok in legs if not ok]
    say("selftest: %d/%d green" % (len(legs) - len(failed), len(legs)))
    if failed:
        say("selftest: failing legs -> " + "; ".join(failed))
    return 0 if not failed else 1


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
