"""E490 -- the nine unfoldable write calls: is the directory a helper parameter?

E489 folded the write call's own path argument for 50 same-directory writers and 9 did
not fold.  A non-folding argument has two very different reasons, and E489 published
them as one class:

  * the write happens inside a helper that takes the directory as a parameter, and the
    module constant is handed in at the call site -- one more hop would reach the
    reader's directory, and the module does place the file where its reader looks;
  * the path genuinely comes from argv / the environment / a temp directory -- it is not
    reachable statically at all, so no hop budget will ever place it.

This face decides per site which of the two it is, and publishes, per row, the helper
(function + parameter) and the call site that supplies the directory together with the
value that call site folds to.

Classes (each row lands in exactly one, re-derived from published evidence):
  H_ONE_HOP     a call site of the helper folds the parameter to the reader's path
  H_DIR_ONLY    a call site folds the parameter, but under another basename in that dir
  H_ELSEWHERE   a call site folds the parameter, and it lands in another directory
  H_NO_FOLDING  the write is in a helper but no call site hands it a folding value
  H_RUNTIME     the path is supplied at run time (argv / env / tempfile), no hop helps
  H_NO_CALL     no write call is published at the recorded site
"""

import argparse
import ast
import io
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402
import e487_composed_writer as e487  # noqa: E402
import e488_writer_directory as e488  # noqa: E402
import e489_write_wire as e489  # noqa: E402
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "writehelper_latest.json"
DATED_PREFIX = "WRITEHELPER"
CARD = ("E490-FOR-THE-SAME-DIRECTORY-WRITERS-WHOSE-WRITE-CALL-DOES-NOT-FOLD-IS-THE-DIRECTORY-"
        "DELEGATED-TO-A-HELPER-PARAMETER")

PARENT_FACE = e489.FACE_NAME                               # E489 writewire_latest.json
POPULATION_WIRE_CLASS = e489.W_UNFOLDABLE
EXCLUDED_PREFIX = e489.EXCLUDED_PREFIX + ("e490_", "run_e490")
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_CALL_SITES = 16
MAX_PATHS = 8

RUNTIME_NAMES = ("argv", "environ", "getenv", "mkdtemp", "NamedTemporaryFile", "TemporaryDirectory")

H_ONE_HOP = "a_call_site_of_the_helper_folds_the_parameter_to_the_reader_path"
H_DIRECTORY_ONE_HOP = ("a_call_site_hands_the_helper_the_reader_directory_but_the_basename_is_"
                       "itself_a_parameter")
H_DIR_ONLY = "a_call_site_folds_the_parameter_under_another_basename_in_the_reader_directory"
H_ELSEWHERE = "a_call_site_folds_the_parameter_but_it_lands_in_another_directory"
H_NO_FOLDING = ("the_write_call_does_not_fold_and_no_call_site_in_the_module_supplies_a_"
                "folding_value")
H_RUNTIME = "the_path_is_supplied_at_run_time_by_argv_environment_or_a_temporary_directory"
H_NO_CALL = "no_write_call_is_published_at_the_recorded_site"
CLASSES = (H_ONE_HOP, H_DIRECTORY_ONE_HOP, H_DIR_ONLY, H_ELSEWHERE, H_NO_FOLDING, H_RUNTIME,
           H_NO_CALL)
DIRECTORY_JOINERS = ("join", "dirname", "abspath", "normpath", "realpath")


def _norm(text):
    return e488._norm(text)


def _clean(path):
    return e488._clean(path)


# ------------------------------------------------------------------ population


def population(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    face = json.load(io.open(path, "r", encoding="utf-8"))
    summary = face.get("summary") or {}
    rows = [r for r in face.get("rows") or []
            if r.get("wire_class") == POPULATION_WIRE_CLASS]
    published = summary.get("spellings_whose_write_call_cannot_be_folded")
    parent = {
        "face": PARENT_FACE,
        "face_verdict": face.get("verdict"),
        "face_evidence_cutoff": face.get("evidence_cutoff"),
        "parent_wire_class_counts": summary.get("wire_class_counts"),
        "parent_unfoldable_spellings": published,
        "population_rows_agree_with_the_parent_tally": published == len(rows),
        "population_definition": "rows of E489 whose wire_class is the unfoldable class "
                                 "(a write call is present but its path argument folds to "
                                 "nothing)",
        "excluded_source_prefixes": list(EXCLUDED_PREFIX),
    }
    return rows, parent


# ------------------------------------------------------------------ structure helpers


def enclosing_functions(tree, line):
    """Functions whose body covers ``line``, outermost first."""
    found = []

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = getattr(child, "lineno", 0)
                end = getattr(child, "end_lineno", start) or start
                if start <= line <= end:
                    found.append(child)
                    walk(child)
            else:
                walk(child)

    walk(tree)
    return found


def parameter_names(func):
    args = func.args
    names = [a.arg for a in args.posonlyargs] + [a.arg for a in args.args]
    if args.vararg:
        names.append(args.vararg.arg)
    names += [a.arg for a in args.kwonlyargs]
    if args.kwarg:
        names.append(args.kwarg.arg)
    return names


def call_sites_of(tree, func_name):
    """Calls of ``func_name`` by bare name, with the node that encloses each call."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == func_name:
            out.append(node)
    out.sort(key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))
    return out[:MAX_CALL_SITES]


def free_names(node):
    return sorted({n.id for n in ast.walk(node) if isinstance(n, ast.Name)})


def runtime_markers(node):
    """Where the expression visibly reaches run-time supply."""
    marks = []
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute):
            if child.attr in RUNTIME_NAMES:
                marks.append("attribute:%s" % child.attr)
            if isinstance(child.value, ast.Name) and child.value.id in ("sys", "os", "tempfile"):
                if child.attr in RUNTIME_NAMES:
                    marks.append("%s.%s" % (child.value.id, child.attr))
        elif isinstance(child, ast.Call):
            name = child.func.id if isinstance(child.func, ast.Name) else (
                child.func.attr if isinstance(child.func, ast.Attribute) else "")
            if name in RUNTIME_NAMES:
                marks.append("call:%s" % name)
    return sorted(set(marks))


def directory_positions(node, needed):
    """Which delegated names sit in a directory position of the write expression.

    ``os.path.join(outdir, name)`` delegates the directory (``outdir``, a joined
    component) while ``name`` is a basename; a bare ``open(path)`` delegates the whole
    path.  Keeping the two apart is the point of this face: the directory can be one hop
    away even when the basename is still a parameter.
    """
    out = {}
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and child.args:
            fname = (child.func.attr if isinstance(child.func, ast.Attribute) else
                     (child.func.id if isinstance(child.func, ast.Name) else ""))
            if fname in DIRECTORY_JOINERS and isinstance(child.args[0], ast.Name) \
                    and child.args[0].id in needed:
                out.setdefault(child.args[0].id, "joined_component")
    if isinstance(node, ast.Name) and node.id in needed:
        out[node.id] = "full_path"
    return out


def reachable_bindings(node, names, depth=0, seen=None):
    """Every name the expression reaches through its local bindings, and the nodes bound.

    ``for p in (path, latest)`` reaches ``path``/``latest`` and through them the helper's
    ``outdir``: the parameter is two name-hops away from the write call, and that is
    exactly the hop this face is about.
    """
    if seen is None:
        seen = set()
    if depth > 8:
        return [], []
    names_out = []
    nodes_out = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Name):
            continue
        if child.id in seen:
            continue
        seen.add(child.id)
        names_out.append(child.id)
        bound = names.get(child.id)
        if bound is not None:
            nodes_out.append(bound)
            sub_names, sub_nodes = reachable_bindings(bound, names, depth + 1, seen)
            names_out.extend(sub_names)
            nodes_out.extend(sub_nodes)
    return names_out, nodes_out


def _bindings_at(folder, line):
    names = dict(folder.module_bindings)
    names.update(folder.function_bindings(line))
    names.update(folder.for_bindings(line))
    return names


def _values_for(folder, tree, root, rel, cnode, value, depth=0):
    """Fold a call-site argument, following the caller's own parameter chain one hop at a time.

    ``_write(out, outdir)`` inside a function whose ``outdir`` is itself a parameter folds
    only if the caller's caller supplies it; the hop is reported, never silently given up.
    """
    line = getattr(cnode, "lineno", 0)
    names = _bindings_at(folder, line)
    vals = _fold_values(folder, value, names)
    hop = {"call_line": line, "expression": _expression_of(root, rel, cnode), "folded": vals}
    if vals or depth >= 3:
        return vals, [hop]
    funcs = enclosing_functions(tree, line)
    if not funcs:
        return vals, [hop]
    inner = funcs[-1]
    pos = parameter_names(inner)
    reach, _reach_nodes = reachable_bindings(value, names)
    free = [n for n in sorted(set(reach)) if n in pos and n not in names]
    if not free:
        return vals, [hop]
    defaults = _defaults_of(inner)
    collected = []
    hops = [hop]
    for caller in call_sites_of(tree, inner.name):
        if caller is cnode:
            continue
        sub = dict(names)
        ok = True
        pending = []
        for name in free:
            arg = None
            for pname, node in zip(pos, caller.args):
                if pname == name:
                    arg = node
            for kw in caller.keywords:
                if kw.arg == name:
                    arg = kw.value
            if arg is None:
                arg = defaults.get(name)
            if arg is None:
                ok = False
                break
            pending.append((name, arg))
        if ok:
            for name, arg in pending:
                sub_vals, sub_hops = _values_for(folder, tree, root, rel, caller, arg, depth + 1)
                hops.extend(sub_hops)
                if not sub_vals:
                    ok = False
                    break
                sub[name] = ast.Constant(value=sub_vals[0])
        if not ok:
            continue
        got = _fold_values(folder, value, sub)
        if got:
            collected.extend(got)
            hops.append({"call_line": getattr(caller, "lineno", 0),
                         "expression": _expression_of(root, rel, caller),
                         "folded": got})
    return sorted(set(collected))[:MAX_PATHS], hops


def _defaults_of(func):
    out = {}
    pos = parameter_names(func)
    defaults = list(func.args.defaults)
    if defaults:
        for name, node in zip(pos[len(pos) - len(defaults):], defaults):
            out[name] = node
    for name, node in zip([a.arg for a in func.args.kwonlyargs],
                          func.args.kw_defaults or []):
        if node is not None:
            out[name] = node
    return out


def _fold_values(folder, node, names):
    try:
        paths, _unresolved = folder.fold(node, names, 0)
    except Exception:
        return []
    cleaned = []
    for p in paths:
        c = _clean(p)
        if c and c not in cleaned:
            cleaned.append(c)
    return cleaned[:MAX_PATHS]


def _expression_of(root, rel, node):
    try:
        src = io.open(os.path.join(root, rel), "r", encoding="utf-8", errors="replace").read()
        return (ast.get_source_segment(src, node) or "").strip()[:200]
    except (OSError, SyntaxError):
        return ""


def _classify_folded(expected, folded):
    if not folded:
        return None
    for p in folded:
        if p in expected:
            return H_ONE_HOP
    for p in folded:
        for e in expected:
            if os.path.dirname(p) == os.path.dirname(e):
                return H_DIR_ONLY
    return H_ELSEWHERE


# ------------------------------------------------------------------ one write site


def site_resolution(root, rel, line, expected):
    """Resolve one recorded write site: helper parameter or run-time supply?"""
    path = os.path.join(root, rel)
    site = {
        "source": rel,
        "line": line,
        "call_found_at": None,
        "callee": "",
        "expression": "",
        "enclosing_functions": [],
        "parameters_needed": [],
        "reachable_names": [],
        "runtime_markers": [],
        "call_sites": [],
        "resolution_class": H_NO_CALL,
    }
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            site["note"] = "the_source_is_larger_than_the_read_cap"
            return site
        tree = ast.parse(e451.read_text(path))
    except (OSError, SyntaxError):
        site["note"] = "the_source_cannot_be_parsed"
        return site
    call, how = e489.write_call_at(tree, line)
    if call is None:
        return site
    site["call_found_at"] = how
    site["callee"] = (call.func.id if isinstance(call.func, ast.Name) else
                      (call.func.attr if isinstance(call.func, ast.Attribute) else ""))
    arg = call.args[0] if call.args else None
    if arg is None:
        site["note"] = "the_write_call_carries_no_positional_path_argument"
        site["resolution_class"] = H_NO_FOLDING
        return site
    site["expression"] = _expression_of(root, rel, call)
    funcs = enclosing_functions(tree, line)
    site["enclosing_functions"] = [f.name for f in funcs]
    folder = e489.FolderEx(rel, tree, root)
    names_here = _bindings_at(folder, line)
    names_used, bound_nodes = reachable_bindings(arg, names_here)
    names_used = sorted(set(names_used))
    site["reachable_names"] = names_used
    marks = set(runtime_markers(arg))
    for bound in bound_nodes:
        marks.update(runtime_markers(bound))
    site["runtime_markers"] = sorted(marks)
    params = {}
    for func in funcs:
        for name in parameter_names(func):
            params[name] = func
    needed = [n for n in names_used if n in params and n not in names_here]
    if not needed:
        # Nothing is delegated: either run time supplies it, or a local name does not fold.
        if site["runtime_markers"]:
            site["resolution_class"] = H_RUNTIME
        else:
            site["resolution_class"] = H_NO_FOLDING
        return site
    site["parameters_needed"] = needed
    helper = params[needed[0]]
    site["helper"] = helper.name
    dir_positions = directory_positions(arg, needed)
    for bound in bound_nodes:
        for name, kind in directory_positions(bound, needed).items():
            dir_positions.setdefault(name, kind)
    site["directory_parameters"] = sorted(dir_positions)
    reader_dirs = sorted({os.path.dirname(e) for e in expected if e})
    classes = []
    for cnode in call_sites_of(tree, helper.name):
        call_names = _bindings_at(folder, getattr(cnode, "lineno", 0))
        mapped = {}
        supplied = {}
        defaults = _defaults_of(helper)
        pos = parameter_names(helper)
        for name, value in zip(pos, cnode.args):
            if name in needed:
                mapped[name] = value
                supplied[name] = "positional"
        for kw in cnode.keywords:
            if kw.arg in needed:
                mapped[kw.arg] = kw.value
                supplied[kw.arg] = "keyword"
        for name in needed:
            if name not in mapped and name in defaults:
                mapped[name] = defaults[name]
                supplied[name] = "default"
        entry = {
            "line": getattr(cnode, "lineno", 0),
            "expression": _expression_of(root, rel, cnode),
            "supplies": sorted(mapped),
            "supplied": supplied,
            "folded": [],
            "mapped": {},
            "hops": {},
            "runtime_markers": runtime_markers(cnode),
            "directory_values": [],
        }
        if set(mapped) >= set(needed):
            sub = dict(names_here)
            for name, value in mapped.items():
                vals, hops = _values_for(folder, tree, root, rel, cnode, value)
                entry["mapped"][name] = vals
                entry["hops"][name] = hops
                sub[name] = ast.Constant(value=vals[0]) if vals else value
            folded = _fold_values(folder, arg, sub)
            entry["folded"] = folded
            dirs = []
            for name, kind in dir_positions.items():
                for value in entry["mapped"].get(name) or []:
                    dirs.append(value if kind == "joined_component"
                                else os.path.dirname(value))
            entry["directory_values"] = sorted({d for d in dirs if d})
            klass = _classify_folded(expected, folded)
            if not klass and entry["directory_values"]:
                klass = (H_ELSEWHERE if not any(d in reader_dirs
                                                for d in entry["directory_values"])
                         else None)
            if entry["directory_values"] and any(d in reader_dirs
                                                 for d in entry["directory_values"]):
                klass = H_ONE_HOP if folded else H_DIRECTORY_ONE_HOP
            if klass:
                classes.append(klass)
                entry["resolution_class"] = klass
        site["call_sites"].append(entry)
    if not site["call_sites"]:
        site["resolution_class"] = H_NO_FOLDING if not site["runtime_markers"] else H_RUNTIME
    elif classes:
        for want in (H_ONE_HOP, H_DIRECTORY_ONE_HOP, H_DIR_ONLY, H_ELSEWHERE):
            if want in classes:
                site["resolution_class"] = want
                break
    elif site["runtime_markers"] or any(cs.get("runtime_markers")
                                        for cs in site["call_sites"]):
        site["resolution_class"] = H_RUNTIME
    else:
        site["resolution_class"] = H_NO_FOLDING
    return site


# ------------------------------------------------------------------ aggregate


ROW_ONE_HOP = "one_more_hop_reaches_the_reader_directory"
ROW_DIRECTORY_ONE_HOP = ("one_more_hop_reaches_the_reader_directory_and_the_basename_is_its_own_"
                         "parameter")
ROW_DIR_ONLY = "one_more_hop_reaches_the_reader_directory_under_another_basename"
ROW_ELSEWHERE = "one_more_hop_reaches_a_different_directory"
ROW_IN_HELPER_NO_FOLD = ("not_reachable_statically_the_write_call_does_not_fold_and_no_call_"
                         "site_supplies_a_folding_value")
ROW_RUNTIME = "not_reachable_statically_the_path_is_supplied_at_run_time"
ROW_NO_CALL = "no_write_call_is_published_at_the_recorded_site"
ROW_CLASSES = (ROW_ONE_HOP, ROW_DIRECTORY_ONE_HOP, ROW_DIR_ONLY, ROW_ELSEWHERE,
               ROW_IN_HELPER_NO_FOLD, ROW_RUNTIME, ROW_NO_CALL)

SITE_TO_ROW = {
    H_ONE_HOP: ROW_ONE_HOP,
    H_DIRECTORY_ONE_HOP: ROW_DIRECTORY_ONE_HOP,
    H_DIR_ONLY: ROW_DIR_ONLY,
    H_ELSEWHERE: ROW_ELSEWHERE,
    H_NO_FOLDING: ROW_IN_HELPER_NO_FOLD,
    H_RUNTIME: ROW_RUNTIME,
    H_NO_CALL: ROW_NO_CALL,
}
ROW_PRIORITY = (ROW_ONE_HOP, ROW_DIRECTORY_ONE_HOP, ROW_DIR_ONLY, ROW_ELSEWHERE,
                ROW_RUNTIME, ROW_IN_HELPER_NO_FOLD, ROW_NO_CALL)


def row_class(sites):
    classes = [SITE_TO_ROW.get(s.get("resolution_class"), ROW_NO_CALL) for s in sites]
    if not classes:
        return ROW_NO_CALL
    for want in ROW_PRIORITY:
        if want in classes:
            return want
    return ROW_NO_CALL


def classify(root=None, rows_input=None):
    rows_in, parent = rows_input if rows_input else population(root)
    rows = []
    for row in sorted(rows_in, key=lambda r: str(r.get("spelling"))):
        spelling = row.get("spelling")
        readers = [_clean(d) for d in (row.get("reader_directories")
                                       or row.get("resolved_directories") or [])]
        expected = ["%s/%s" % (d, spelling) for d in readers if d]
        sites = []
        for src in (row.get("write_sites") or []):
            rel = _norm(src.get("source"))
            line = src.get("line")
            if not rel or not line:
                continue
            sites.append(site_resolution(root or ROOT, rel, line, expected))
        helpers = sorted({s.get("helper") for s in sites if s.get("helper")})
        supplying = []
        for s in sites:
            for cs in s.get("call_sites") or []:
                if cs.get("folded") or cs.get("directory_values"):
                    supplying.append({"source": s.get("source"),
                                      "write_line": s.get("line"),
                                      "helper": s.get("helper"),
                                      "directory_parameters": s.get("directory_parameters"),
                                      "call_line": cs.get("line"),
                                      "call_expression": cs.get("expression"),
                                      "directory_values": cs.get("directory_values"),
                                      "folded": cs.get("folded")})
        rows.append({
            "spelling": spelling,
            "expected_reader_paths": expected,
            "reader_directories": readers,
            "parent_directory_class": row.get("directory_class"),
            "parent_wire_class": row.get("wire_class"),
            "write_sites": sites,
            "helpers": helpers,
            "call_sites_that_fold_the_directory": supplying,
            "row_class": row_class(sites),
        })
    return rows, parent


def _recompute(face):
    rows = face.get("rows") or []
    counts = {k: 0 for k in ROW_CLASSES}
    for row in rows:
        if row.get("row_class") in counts:
            counts[row["row_class"]] += 1
    return {
        "population_spellings": len(rows),
        "population_write_sites": len({(s.get("source"), s.get("line")) for r in rows
                                       for s in (r.get("write_sites") or [])}),
        "row_class_counts": counts,
        "spellings_a_hop_reaches_the_reader_directory": counts[ROW_ONE_HOP],
        "spellings_a_hop_reaches_the_reader_directory_with_a_parameter_basename": (
            counts[ROW_DIRECTORY_ONE_HOP]),
        "spellings_a_hop_reaches_the_reader_directory_under_another_basename": (
            counts[ROW_DIR_ONLY]),
        "spellings_whose_helper_call_site_folds_the_directory": len(
            [r for r in rows if r.get("call_sites_that_fold_the_directory")]),
        "spellings_not_reachable_statically": (
            counts[ROW_RUNTIME] + counts[ROW_NO_CALL] + counts[ROW_IN_HELPER_NO_FOLD]),
        "write_sites_whose_expression_is_a_helper_parameter": len(
            [s for r in rows for s in (r.get("write_sites") or [])
             if s.get("parameters_needed")]),
        "write_sites_whose_expression_reaches_run_time": len(
            [s for r in rows for s in (r.get("write_sites") or [])
             if s.get("runtime_markers")]),
    }


V_EMPTY = "the_parent_published_no_unfoldable_spelling"
V_ALL_HOP = "every_unfoldable_write_is_one_hop_from_the_reader_directory"
V_MOST_HOP = "most_unfoldable_writes_are_one_hop_from_the_reader_directory"
V_MINORITY_HOP = "a_minority_of_unfoldable_writes_is_one_hop_from_the_reader_directory"
V_NONE_HOP = "no_unfoldable_write_is_reachable_from_a_call_site_it_is_all_run_time_supply"
VERDICT_VOCAB = (V_EMPTY, V_ALL_HOP, V_MOST_HOP, V_MINORITY_HOP, V_NONE_HOP)


def _verdict(summary):
    total = int(summary.get("population_spellings") or 0)
    if not total:
        return V_EMPTY
    reach = int(summary.get("spellings_whose_helper_call_site_folds_the_directory") or 0)
    if reach == 0:
        return V_NONE_HOP
    if reach == total:
        return V_ALL_HOP
    return V_MOST_HOP if reach * 2 >= total else V_MINORITY_HOP


# ------------------------------------------------------------------ build / write


def build(root=None, write=True):
    root = root or ROOT
    rows, parent = classify(root)
    summary = _recompute({"rows": rows})
    summary["parent_unfoldable_spellings"] = parent["parent_unfoldable_spellings"]
    summary["population_reproduced"] = parent["population_rows_agree_with_the_parent_tally"]
    face = {
        "card": CARD,
        "study": "E490_for_the_unfoldable_write_calls_is_the_directory_a_helper_parameter",
        "title": "for the same-directory writers whose write call does not fold, does a helper "
                 "take the directory as a parameter that a call site supplies?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": parent,
        "fold_rule": {
            "parameter": "a name that is a parameter of the enclosing function and is not "
                         "bound in the function body is delegated to the caller",
            "call_site": "each bare-name call of that helper in the same module is mapped "
                         "positionally and by keyword onto the parameter list",
            "fold": "the write expression is re-folded with the call-site expressions "
                    "substituted for the delegated parameters, using E489's folder",
            "runtime": "sys.argv / os.environ / os.getenv / tempfile factory names are "
                       "published as run-time supply, never as a folded hop",
        },
        "class_definition": {
            ROW_ONE_HOP: "a call site of the helper folds the parameter to "
                         "<reader directory>/<spelling>",
            ROW_DIR_ONLY: "a call site folds the parameter into the reader's directory under "
                          "another basename",
            ROW_ELSEWHERE: "a call site folds the parameter, and it lands in another directory",
            ROW_IN_HELPER_NO_FOLD: "the write is in a helper but no call site hands it a "
                                   "folding value (or no call site is found in the module)",
            ROW_RUNTIME: "the path is supplied at run time by argv / environment / a "
                         "temporary directory",
            ROW_NO_CALL: "no write call is found at or within %d lines of the recorded site"
                         % e489.SEARCH_LINES,
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "the population is E489's unfoldable arm kept byte-for-byte; this face adds the "
            "hop question and does not re-open E487/E488/E489's class questions",
            "a call site outside the same module is not resolved, so a helper called only "
            "from another module is published as H_NO_FOLDING rather than guessed",
            "a folded value says the composed string equals the reader path; it does not "
            "claim the file exists at run time or that the branch executes",
            "a helper that forwards its parameter to a second helper is one hop; this face "
            "does not chase the second hop",
        ],
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(outdir, FACE_NAME)
    body = json.dumps(face, indent=1, ensure_ascii=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return dated, latest


# ------------------------------------------------------------------ check / verify


def row_problems(face):
    problems = []
    summary = face.get("summary") or {}
    derived = _recompute(face)
    for key, value in derived.items():
        if summary.get(key) != value:
            problems.append("%s: published %r, re-derives %r" % (key, summary.get(key), value))
    seen = set()
    for row in face.get("rows") or []:
        spelling = row.get("spelling")
        if spelling in seen:
            problems.append("%s: duplicated row" % (spelling,))
        seen.add(spelling)
        if row.get("row_class") not in ROW_CLASSES:
            problems.append("%s: unknown class %r" % (spelling, row.get("row_class")))
        expected = row_class(row.get("write_sites") or [])
        if row.get("row_class") != expected:
            problems.append("%s: class %r does not re-derive as %r"
                            % (spelling, row.get("row_class"), expected))
        if row.get("parent_wire_class") != POPULATION_WIRE_CLASS:
            problems.append("%s: row is not from the parent's unfoldable arm" % (spelling,))
        if not row.get("expected_reader_paths"):
            problems.append("%s: an unfoldable row publishes no reader path" % (spelling,))
        for site in row.get("write_sites") or []:
            rc = site.get("resolution_class")
            if rc not in CLASSES:
                problems.append("%s: unknown site class %r" % (spelling, rc))
            if rc in (H_ONE_HOP, H_DIR_ONLY, H_ELSEWHERE) and not any(
                    cs.get("folded") for cs in site.get("call_sites") or []):
                problems.append("%s: site at %s claims a hop but publishes no folded value"
                                % (spelling, site.get("line")))
            if rc == H_RUNTIME and not site.get("runtime_markers"):
                problems.append("%s: site at %s claims run-time supply with no marker"
                                % (spelling, site.get("line")))
    if _verdict({k: summary.get(k) for k in derived}) != face.get("verdict"):
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"),
                           _verdict({k: summary.get(k) for k in derived})))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e490 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    s = face.get("summary") or {}
    c = s.get("row_class_counts") or {}
    print("population=%d one_hop=%d dir_only=%d elsewhere=%d in_helper_no_fold=%d "
          "runtime=%d no_call=%d"
          % (s.get("population_spellings") or 0, c.get(ROW_ONE_HOP, 0),
             c.get(ROW_DIR_ONLY, 0), c.get(ROW_ELSEWHERE, 0),
             c.get(ROW_IN_HELPER_NO_FOLD, 0), c.get(ROW_RUNTIME, 0), c.get(ROW_NO_CALL, 0)))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build(root, write=False)
    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved")
    a = {r["spelling"]: r for r in published.get("rows") or []}
    b = {r["spelling"]: r for r in fresh.get("rows") or []}
    if set(a) != set(b):
        problems.append("population moved: +%d -%d" % (len(set(b) - set(a)),
                                                       len(set(a) - set(b))))
    for spelling in sorted(set(a) & set(b)):
        if a[spelling].get("row_class") != b[spelling].get("row_class"):
            problems.append("%s: class moved %r -> %r" % (spelling,
                                                          a[spelling].get("row_class"),
                                                          b[spelling].get("row_class")))
    problems.extend(row_problems(fresh))
    print("e490 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir)
    os.makedirs(os.path.join(root, "scripts"))

    def row(spelling, source, line, directory="results/state_tilt"):
        return {"spelling": spelling, "stem": spelling.replace("_latest.json", ""),
                "parent_class": e487.C_DIRECT, "parent_route": "direct",
                "directory_class": e488.K_SAME, "wire_class": POPULATION_WIRE_CLASS,
                "resolved_directories": [directory],
                "write_sites": [{"source": source,
                                 "line": line,
                                 "route": "direct",
                                 "call_found_at": "exact_line"}]}

    rows = [
        row("helped_latest.json", "scripts/w_helped.py", 7),
        row("runtime_latest.json", "scripts/w_runtime.py", 4),
        row("nocall_latest.json", "scripts/w_nocall.py", 3),
    ]
    parent = {
        "verdict": e489.V_MOST,
        "evidence_cutoff": "2026-11-07",
        "summary": {"wire_class_counts": {POPULATION_WIRE_CLASS: len(rows),
                                          e489.W_WIRED: 39},
                    "spellings_whose_write_call_cannot_be_folded": len(rows)},
        "rows": rows,
        "verdict_vocab": list(e489.VERDICT_VOCAB),
    }
    io.open(os.path.join(outdir, PARENT_FACE), "w", encoding="utf-8",
            newline="\n").write(json.dumps(parent))
    io.open(os.path.join(root, "scripts", "w_helped.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n"
        "\n"
        "\n"
        "def _write(face, outdir):\n"
        "    with open(os.path.join(outdir, 'helped_latest.json'), 'w') as fh:\n"
        "        fh.write(face)\n"
        "\n"
        "\n"
        "def run():\n"
        "    _write('{}', OUTDIR)\n")
    io.open(os.path.join(root, "scripts", "w_runtime.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import sys\n"
        "PATH = sys.argv[1]\n"
        "with open(PATH, 'w') as fh:\n"
        "    fh.write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_nocall.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n")
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e490_")
    root = _fixture(tmp)
    rows_in, parent = population(root)
    leg("the parent's unfoldable arm is the population", len(rows_in) == 3)
    leg("the parent's tally is reproduced", parent["population_rows_agree_with_the_parent_tally"])
    leg("the parent count is carried", parent["parent_unfoldable_spellings"] == 3)
    expected = ["results/state_tilt/helped_latest.json"]
    site = site_resolution(root, "scripts/w_helped.py", 7, expected)
    leg("the write is found", site["call_found_at"] == "exact_line")
    leg("the helper is named", site.get("helper") == "_write")
    leg("the delegated parameter is named", site["parameters_needed"] == ["outdir"])
    leg("the call site is found", [c["line"] for c in site["call_sites"]] == [12])
    leg("the call site folds to the reader path",
        site["call_sites"][0]["mapped"].get("outdir") == ["results/state_tilt"])
    leg("the site is one hop", site["resolution_class"] == H_ONE_HOP)
    runtime = site_resolution(root, "scripts/w_runtime.py", 4,
                              ["results/state_tilt/runtime_latest.json"])
    leg("an argv path is run-time supply", runtime["resolution_class"] == H_RUNTIME)
    leg("the argv marker is published",
        any("attribute:argv" in m for m in runtime["runtime_markers"]))
    nocall = site_resolution(root, "scripts/w_nocall.py", 3,
                             ["results/state_tilt/nocall_latest.json"])
    leg("a module with no write call is H_NO_CALL", nocall["resolution_class"] == H_NO_CALL)
    rows, _ = classify(root)
    by = {r["spelling"]: r for r in rows}
    leg("one hop is the row class",
        by["helped_latest.json"]["row_class"] == ROW_ONE_HOP)
    leg("run-time supply is its own row class",
        by["runtime_latest.json"]["row_class"] == ROW_RUNTIME)
    leg("the row carries the supplying call site",
        by["helped_latest.json"]["call_sites_that_fold_the_directory"][0]["call_line"] == 12)
    face = {"rows": rows, "evidence_cutoff": "2026-11-07"}
    summary = _recompute(face)
    face["summary"] = summary
    face["verdict"] = _verdict(summary)
    leg("the tallies re-derive", summary["population_spellings"] == len(rows))
    leg("every row lands in exactly one class",
        sum(summary["row_class_counts"].values()) == len(rows))
    leg("the one-hop count is the headline",
        summary["spellings_whose_helper_call_site_folds_the_directory"] == 1)
    leg("the fixture has no row problems", row_problems(face) == [])
    broken = json.loads(json.dumps(face))
    next(r for r in broken["rows"] if r["row_class"] == ROW_ONE_HOP)["row_class"] = ROW_RUNTIME
    leg("a class that does not re-derive is refused", row_problems(broken))
    broken2 = json.loads(json.dumps(face))
    broken2["verdict"] = V_ALL_HOP
    leg("a verdict that does not re-derive is refused", row_problems(broken2))
    broken3 = json.loads(json.dumps(face))
    one = next(r for r in broken3["rows"] if r["row_class"] == ROW_ONE_HOP)
    one["write_sites"][0]["call_sites"] = []
    leg("a claimed hop with no folded value is refused", row_problems(broken3))
    broken4 = json.loads(json.dumps(face))
    rt = next(r for r in broken4["rows"] if r["row_class"] == ROW_RUNTIME)
    rt["write_sites"][0]["runtime_markers"] = []
    leg("a claimed run-time supply with no marker is refused", row_problems(broken4))
    leg("write leaves both faces on disk",
        all(os.path.exists(p) for p in _write(face, root)))
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def run(root=None):
    root = root or ROOT
    face = build(root, write=True)
    s = face["summary"]
    c = s["row_class_counts"]
    print("e490 run verdict=%s" % face["verdict"])
    print("population=%d one_hop=%d dir_only=%d elsewhere=%d in_helper_no_fold=%d "
          "runtime=%d no_call=%d reproduced=%s"
          % (s["population_spellings"], c[ROW_ONE_HOP], c[ROW_DIR_ONLY],
             c[ROW_ELSEWHERE], c[ROW_IN_HELPER_NO_FOLD], c[ROW_RUNTIME], c[ROW_NO_CALL],
             s.get("population_reproduced")))
    for row in face["rows"]:
        print("  %-24s %s" % (row["spelling"], row["row_class"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E490 is the unfoldable write's directory a helper param")
    ap.add_argument("mode", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.mode == "check":
        return check()
    if args.mode == "verify":
        return verify()
    if args.mode == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())