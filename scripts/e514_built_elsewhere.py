"""E514 -- where a value built by another module actually comes from.

E512 (r1540 bm-b) answered every one of its eight sites by reading its callee or its
argument, but it stopped at one label: ``a_value_built_by_a_call_into_another_module``.
Four sites carry that label and they are the same expression -- ``asof = str(slip.index[
-1].date())`` where ``slip`` comes out of ``BT.apply_overlay(...)`` -- so "built elsewhere"
is where the as-of day of a published ticket stops being readable.

E513 (r1541 bm-b) then published 23 bindings whose population is built by a call into
another in-repo module and stopped there as well ("the population lives in another module
and stops there").

This study opens exactly that hop.  Two arms, both taken from the published faces and
never re-derived from raw pairs:

  * arm ``the_surface_passes_a_constant_that_another_module_builds``: E513's rows whose
    origin is ``the_population_lives_in_another_module_and_stops_there``;
  * arm ``a_published_site_reads_a_value_that_another_module_builds``: E512's sites whose
    ``field_origin`` is ``a_value_built_by_a_call_into_another_module``.

Per row it publishes whether the callee is a definition in an in-repo module at all, every
``return`` path of that builder with the kind of value it hands over (a file on disk, the
git store at a commit, a scan of the working tree, a day carried by a loaded panel, the
run clock, a parameter of the builder, a literal, or still nothing readable), and a one-word
answer to the card's question.  A builder that is only ``os.path.join``/``basename`` is not
a builder: it constructs a name, and the published bucket said "another module".

Usage:
    python scripts/e514_built_elsewhere.py run
    python scripts/e514_built_elsewhere.py check
    python scripts/e514_built_elsewhere.py verify
    python scripts/e514_built_elsewhere.py selftest
"""

from __future__ import annotations

import ast
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e504_name_compose as base  # noqa: E402
import e507_unresolved_origin as e507  # noqa: E402
import e512_callee_return as e512  # noqa: E402
import e513_constant_origin as e513  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "builtelsewhere_latest.json"
DATED_PREFIX = "BUILTELSEWHERE"
DATE_STAMP = "2026-11-08"
CARD = "E514-WHERE-DOES-THE-VALUE-BUILT-BY-ANOTHER-MODULE-ACTUALLY-COME-FROM"
STUDY = "E514_built_elsewhere"
UPSTREAM_513 = os.path.join("results", "state_tilt", "CONSTANTORIGIN-2026-11-08.json")
UPSTREAM_512 = os.path.join("results", "state_tilt", "CALLEERETURN-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/CONSTANTORIGIN-2026-11-08.json rows whose origin is "
                     "the_population_lives_in_another_module_and_stops_there, plus "
                     "results/state_tilt/CALLEERETURN-2026-11-07.json sites whose field_origin is "
                     "a_value_built_by_a_call_into_another_module")
SELF_EXCLUDED = ("e514_", "run_e514", "_e514", "_r1542")

# ------------------------------------------------------------------ vocabulary
ARM_CONSTANT = "the_surface_passes_a_constant_that_another_module_builds"
ARM_SITE = "a_published_site_reads_a_value_that_another_module_builds"
ARM_VOCAB = (ARM_CONSTANT, ARM_SITE)

B_REPO = "the_builder_is_a_function_defined_in_an_in_repo_module"
B_READ_HERE = "the_value_is_read_at_the_site_itself"
B_LITERAL_HERE = "the_value_is_a_literal_written_at_the_site"
B_NAME_ONLY = "the_callee_only_constructs_a_name_or_a_path"
B_UNRESOLVED = "the_callee_could_not_be_resolved_to_a_definition"
BUILDER_VOCAB = (B_REPO, B_READ_HERE, B_LITERAL_HERE, B_NAME_ONLY, B_UNRESOLVED)

K_FILE = "a_value_read_from_a_file_on_disk"
K_STORE = "a_value_read_from_the_git_store_at_a_commit"
K_SCAN = "a_value_built_by_scanning_the_working_tree"
K_SERIES = "a_day_or_a_series_carried_by_a_loaded_panel"
K_CLOCK = "the_run_clock"
K_PARAM = "a_parameter_the_builder_hands_back"
K_LITERAL = "a_literal_written_in_the_builder"
K_OTHER = "still_no_readable_origin_after_one_hop"
KIND_VOCAB = (K_FILE, K_STORE, K_SCAN, K_SERIES, K_CLOCK, K_PARAM, K_LITERAL, K_OTHER)
READ_KINDS = (K_FILE, K_STORE, K_SCAN, K_SERIES)
READS = READ_KINDS

A_READ = "every_return_path_reads_a_file_a_store_or_the_tree"
A_CLOCK = "a_return_path_is_the_run_clock"
A_PARAM = "a_return_path_hands_back_a_parameter_of_the_builder"
A_MIXED = "the_builder_reads_something_and_also_hands_back_something_else"
A_OTHER = "no_return_path_is_readable_after_one_hop"
A_READ_HERE = "the_value_is_read_at_the_site_itself_so_no_other_module_builds_it"
A_LITERAL_HERE = "the_value_is_a_literal_written_at_the_site"
A_NAME_ONLY = "the_callee_only_constructs_a_name_or_a_path"
A_UNRESOLVED = "the_callee_could_not_be_resolved_so_the_value_stays_unread"
ANSWER_VOCAB = (A_READ, A_CLOCK, A_PARAM, A_MIXED, A_OTHER, A_READ_HERE, A_LITERAL_HERE,
                A_NAME_ONLY, A_UNRESOLVED)

V_READ = ("every_built_elsewhere_value_comes_out_of_an_in_repo_function_that_reads_a_file_a_"
          "store_or_the_tree")
V_PART = "some_built_elsewhere_values_are_read_from_a_file_and_some_are_still_other"
V_SPLIT = ("every_in_repo_builder_answers_its_return_paths_and_the_rest_of_the_bucket_is_not_"
           "a_builder_at_all")
V_NONE = "no_published_built_elsewhere_value_is_built_by_an_in_repo_function"
V_EMPTY = "the_two_published_upstream_faces_hold_no_built_elsewhere_value"
VERDICT_VOCAB = (V_READ, V_SPLIT, V_PART, V_NONE, V_EMPTY)

COERCIONS = frozenset(("str", "int", "float", "bool", "repr", "list", "tuple", "set"))
READ_WORDS = ("_read", "load", "read_", "readtext", "_load", "loads", "readlines", "read_csv",
              "read_json", "read_parquet", "iterrows", "DictReader", "open")
TREE_WORDS = ("walk", "listdir", "glob", "rglob", "iglob", "iterdir", "scandir")
CLOCK_WORDS = ("now", "today", "utcnow", "time", "monotonic", "perf_counter", "timestamp")
NAME_ONLY_MODULES = frozenset(("os", "posixpath", "ntpath", "pathlib", "glob"))
EXACT_READERS = frozenset(("read", "readline", "readlines", "read_text", "open", "load",
                           "loads"))

# ------------------------------------------------------------- binding machinery


def _assign_nodes(tree):
    """Every binding in a module: ``name = v``, ``a, b = f()`` and ``name[k] = v``.

    A tuple target fed by a single call is attributed to that call for *every* name: which
    element of the returned tuple a name holds is a different question, and refusing to
    answer any of them because the arity is unknown would hide the builder entirely.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            value = node.value
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out.append((target.id, value, node.lineno))
                elif isinstance(target, (ast.Tuple, ast.List)):
                    if isinstance(value, (ast.Tuple, ast.List)) \
                            and len(target.elts) == len(value.elts):
                        pairs = list(zip(target.elts, value.elts))
                    else:
                        pairs = [(tgt, value) for tgt in target.elts]
                    for tgt, val in pairs:
                        if isinstance(tgt, ast.Name):
                            out.append((tgt.id, val, node.lineno))
                elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    out.append((target.value.id, value, node.lineno))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.value is not None:
            out.append((node.target.id, node.value, node.lineno))
    return out


def _binding_at(tree, name, before, skip=frozenset()):
    """(value node, line) of the last write of ``name`` at or above ``before``."""
    best = None
    for got, value, line in _assign_nodes(tree):
        if got != name or line > before or line in skip:
            continue
        if best is None or line > best[0]:
            best = (line, value)
    return best


def _appends_to(tree, name):
    """Nodes that fill the container ``name``: append/add/update/setdefault and subscript writes."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("append", "add", "update", "setdefault"):
            receiver, hops = node.func.value, 0
            while isinstance(receiver, ast.Call) and hops < 4:
                receiver = receiver.func
                hops += 1
            while isinstance(receiver, ast.Attribute) and hops < 8:
                receiver = receiver.value
                hops += 1
            if isinstance(receiver, ast.Name) and receiver.id == name:
                if node.func.attr == "setdefault" and len(node.args) > 1:
                    out.append(node.args[1])
                elif node.args:
                    out.append(node.args[0])
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) \
                        and target.value.id == name:
                    out.append(node.value)
    return out


def _empty_container(node):
    return isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple)) and not list(
        ast.iter_child_nodes(node)) or (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                                        and node.func.id in ("list", "dict", "set", "tuple")
                                        and not node.args)


# ------------------------------------------------------------------- value trace


def _call_target(ctx, func):
    """``(root name id, dotted path, attribute)`` for a callee written as ``a.b.c``.

    ``datetime.datetime.now()`` and ``os.path.dirname()`` both root in an imported module,
    but only the last segment is an attribute of a Name; the chain has to be walked to the
    root or the callee reads as "something we cannot name".
    """
    parts = []
    node = func
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return "", "", ""
    parts.reverse()
    imports = ctx.get("imports") or {}
    dotted = imports.get(node.id) or ""
    if dotted:
        root = dotted.split(".")[0]
        rest = dotted.split(".")[1:]
        return node.id, ".".join([root] + rest + parts[:-1]), parts[-1]
    return node.id, ".".join(parts[:-1]), parts[-1]


def trace(ctx, node, depth=0, skip=frozenset(), params=frozenset()):
    """(kind, via) for what a value finally holds, one hop per call and per binding.

    ``params`` carries the parameter names of the function that owns this value.  It is
    passed in rather than read off the module context: ``e507.build_ctx`` publishes a
    module-level ``params`` map of a different meaning, and reading that one labelled
    ordinary locals as parameters (a container called ``out`` was published as "a parameter
    the builder hands back").
    """
    if node is None or depth > 30 or ctx is None:
        return K_OTHER, ""
    tree = ctx.get("tree")
    if isinstance(node, ast.Call):
        func = node.func
        resolved = _repo_function(ctx["root"], ctx, node) if ctx.get("root") else None
        if resolved is not None:
            return K_OTHER, (resolved.get("name") or "") + "()"
        if isinstance(func, ast.Name):
            low = func.id.lower()
            if func.id in CLOCK_WORDS or low in CLOCK_WORDS:
                return K_CLOCK, func.id
            if func.id in COERCIONS and node.args:
                return trace(ctx, node.args[0], depth + 1, skip, params)
            if func.id in EXACT_READERS:
                return K_FILE, func.id
            if any(w in low for w in READ_WORDS):
                return K_FILE, func.id
            if func.id in TREE_WORDS or low in TREE_WORDS:
                return K_SCAN, func.id
            return K_OTHER, func.id + "()"
        if isinstance(func, ast.Attribute):
            attr = func.attr
            low = attr.lower()
            head_id, head, _last = _call_target(ctx, func)
            root_pkg = head.split(".")[0] if head else ""
            if head_id:
                if root_pkg in ("json", "csv") and low in ("load", "loads", "dictreader"):
                    return K_FILE, head + "." + attr
                if root_pkg in ("time", "datetime") and low in CLOCK_WORDS:
                    return K_CLOCK, head + "." + attr
                if root_pkg == "subprocess" and low in ("run", "check_output", "popen"):
                    return K_STORE, head + "." + attr
            if low in ("date", "strftime", "isoformat", "to_pydatetime"):
                return trace(ctx, func.value, depth + 1, skip, params)
            if attr in EXACT_READERS:
                return K_FILE, attr
            if any(w in low for w in READ_WORDS):
                return K_FILE, attr
            if low in TREE_WORDS:
                return K_SCAN, attr
            # a library constructor (pd.Series, np.array) takes its index from an argument,
            # and that argument is where the day actually comes from
            for keyword in node.keywords:
                if keyword.arg in ("index", "data", "values"):
                    got = trace(ctx, keyword.value, depth + 1, skip, params)
                    if got[0] != K_OTHER:
                        return got
            # a method call hands back what its receiver holds (``live = applied.dropna()``,
            # ``idx = live.index``): the receiver is the author, not the method name and not
            # its first argument (``marks.shift(1)`` is not "the literal 1")
            return trace(ctx, func.value, depth + 1, skip, params)
        return K_OTHER, ""
    if isinstance(node, (ast.Subscript, ast.Attribute)):
        return trace(ctx, node.value, depth + 1, skip, params)
    if isinstance(node, ast.Name):
        if node.id in params:
            return K_PARAM, node.id
        bound = _binding_at(tree, node.id, getattr(node, "lineno", 10 ** 9), skip)
        if bound is not None:
            line, value = bound
            kind, via = trace(ctx, value, depth + 1, skip | {line}, params)
            if kind not in (K_OTHER, K_LITERAL):
                return kind, via
            # a container that is filled in loops has no expression of its own: the fills are
            # its authors, and a reader fill outranks a parameter or a literal one
            best = (kind, via)
            for filled in _appends_to(tree, node.id):
                got = trace(ctx, filled, depth + 1, skip | {line}, params)
                if got[0] in READ_KINDS:
                    return got
                if got[0] in (K_CLOCK, K_PARAM) and best[0] in (K_OTHER, K_LITERAL):
                    best = got
            if best[0] == K_LITERAL and _empty_container(value):
                # an empty container is a starting point, not an answer: leaving it as a
                # literal would publish "the value is {}" for a dict that the loop fills
                return K_OTHER, node.id
            return best
        return K_OTHER, node.id
    if isinstance(node, ast.Constant):
        return K_LITERAL, repr(node.value)[:30]
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        if not node.elts:
            return K_LITERAL, "[]"
        first = None
        for elt in node.elts:
            got = trace(ctx, elt, depth + 1, skip, params)
            if got[0] not in (K_OTHER, K_LITERAL):
                return got
            if first is None:
                first = got
        return first
    if isinstance(node, ast.Dict):
        if not node.values:
            return K_LITERAL, "{}"
        for value in node.values:
            got = trace(ctx, value, depth + 1, skip, params)
            if got[0] != K_OTHER:
                return got
        return K_LITERAL, "{}"
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return trace(ctx, node.generators[0].iter, depth + 1, skip, params)
    if isinstance(node, ast.Return):
        return trace(ctx, node.value, depth + 1, skip, params)
    for child in ast.iter_child_nodes(node):
        got = trace(ctx, child, depth + 1, skip, params)
        if got[0] != K_OTHER:
            return got
    return K_OTHER, ""


def _repo_function(root, ctx, call):
    """Resolve a call's callee to an in-repo definition, both import shapes included.

    ``from scripts import mod as M`` puts the *module* in the import table
    (``M.x()`` -> ``scripts.mod``) while ``import a.b as M`` puts a dotted module there too;
    ``e512._callee`` splits the last segment off in both cases, so ``BT.apply_overlay``
    resolves to the package ``scripts`` and then falls through to the call's arguments --
    which is how a sibling argument (``k_schedule``) gets published as the builder.
    """
    func = call.func
    attr = None
    dotted = ""
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        attr = func.attr
        dotted = (ctx.get("imports") or {}).get(func.value.id) or ""
    elif isinstance(func, ast.Name):
        attr = func.id
        dotted = (ctx.get("imports") or {}).get(func.id) or ""
        if not dotted and attr in (ctx.get("funcs") or {}):
            return {"class": e512.CALLEE_SAME_MODULE, "name": attr, "rel": ctx.get("rel") or "",
                    "node": ctx["funcs"][attr], "line": ctx["funcs"][attr].lineno}
    if not dotted:
        return None
    for module in (dotted, dotted.rsplit(".", 1)[0]):
        path = e507._module_file(root, module)
        if path is None:
            continue
        rel = base._rel(path, root).replace("\\", "/")
        cctx = e507.ctx_of(root, rel)
        if cctx is None:
            continue
        node = (cctx.get("funcs") or {}).get(attr)
        if node is not None:
            return {"class": e512.CALLEE_IMPORTED, "name": attr, "rel": rel, "node": node,
                    "line": node.lineno}
    return None


def repo_call(ctx, node, depth=0, skip=frozenset(), seen=frozenset()):
    """The first call inside a value that resolves to an in-repo function definition."""
    if node is None or ctx is None or depth > 12:
        return None
    root = ROOT_OF(ctx)
    if isinstance(node, ast.Call):
        got = _repo_function(root, ctx, node)
        if got is not None:
            key = (got.get("rel") or "", got.get("name") or "")
            if key not in seen:
                return node, got
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            found = repo_call(ctx, arg, depth + 1, skip, seen)
            if found:
                return found
        if isinstance(node.func, ast.Attribute):
            return repo_call(ctx, node.func.value, depth + 1, skip, seen)
        return None
    if isinstance(node, ast.Name):
        bound = _binding_at(ctx.get("tree"), node.id, getattr(node, "lineno", 10 ** 9), skip)
        if bound is None:
            return None
        return repo_call(ctx, bound[1], depth + 1, skip | {bound[0]}, seen)
    if isinstance(node, (ast.Subscript, ast.Attribute)):
        return repo_call(ctx, node.value, depth + 1, skip, seen)
    if isinstance(node, (ast.Tuple, ast.List, ast.Dict, ast.IfExp, ast.JoinedStr,
                         ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        for child in ast.iter_child_nodes(node):
            found = repo_call(ctx, child, depth + 1, skip, seen)
            if found:
                return found
    return None


def ROOT_OF(ctx):
    return ctx.get("root") or ROOT


def builder_kinds(got, root, depth=0, seen=frozenset()):
    """Every return path of one builder, with the kind of value it hands over."""
    key = (got.get("rel") or "", got.get("name") or "")
    if key in seen or depth > 2:
        return []
    seen = seen | {key}
    cctx = e507.ctx_of(root, got["rel"])
    if cctx is None:
        return []
    cctx = dict(cctx, root=root)
    func = got["node"]
    paths, _nested = e512.return_paths(func)
    params = frozenset(e512.argument_names(func))
    out = []
    for path in paths:
        node = None
        for ret in ast.walk(func):
            if isinstance(ret, ast.Return) and ret.lineno == path["line"]:
                node = ret.value
                break
        kind, via = trace(cctx, node, params=params)
        chain = ""
        # a return path that names nothing gets exactly one more author: the builder called
        # inside it, or -- for a container filled in a loop -- the reads of the body.  A
        # literal return is *not* upgraded: 'return {}' is a real empty answer.
        if kind == K_OTHER and node is not None:
            inner = repo_call(cctx, node, seen=seen)
            if inner and (inner[1].get("rel"), inner[1].get("name")) != key:
                deeper = builder_kinds(inner[1], root, depth + 1, seen)
                kinds = [k for k, _v in deeper if k not in (K_OTHER, K_LITERAL)]
                if kinds:
                    kind = kinds[0]
                    chain = inner[1]["rel"] + ":" + inner[1]["name"]
        if kind == K_OTHER:
            body_kind, body_via = _body_fill_kind(cctx, func, params)
            if body_kind is not None:
                kind, via, chain = body_kind, body_via, "body:" + body_via
        out.append({"line": path["line"], "kind": kind, "via": via, "through": chain,
                    "expr": path.get("expr") or ""})
    return out


def _body_fill_kind(cctx, func, params=frozenset()):
    """What the builder's own body reads, when the returned container names nothing itself.

    A return of a list that is filled in a loop (``out = []`` ... ``out.append(...)``) has no
    expression to read; the *fill* is the author.  This looks at the reader and tree-walk
    calls of the body once, and only after the return expression failed, so it can never
    upgrade a return that already names something.
    """
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            kind, via = trace(cctx, node, params=params)
            if kind in READ_KINDS:
                return kind, via
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            inner = repo_call(cctx, node)
            if inner:
                deeper = builder_kinds(inner[1], ctx_root(cctx))
                kinds = [p["kind"] for p in deeper if p["kind"] in READ_KINDS]
                if kinds:
                    return kinds[0], inner[1].get("name") or ""
    return None, ""


def ctx_root(ctx):
    return ctx.get("root") or ROOT


def _param_order(func):
    """Parameter names in call order, so an argument position can name its parameter."""
    args = getattr(func, "args", None)
    if args is None:
        return []
    return [a.arg for a in list(getattr(args, "posonlyargs", []) or []) + list(args.args)]


def parameter_feed(ctx, root, call, got, paths):
    """Where the parameter the builder hands back is fed from at this call site.

    ``apply_overlay`` hands back a series indexed by its ``rp`` parameter, and ``rp`` is not
    a file: it is whatever the caller passed.  Naming the parameter without naming its feed
    would be a half answer, so the argument at that position is traced in the site's own
    module -- and, when that argument is itself another module's call, one hop into it.
    """
    order = _param_order(got["node"])
    feed = []
    for path in paths:
        if path["kind"] != K_PARAM:
            continue
        name = path.get("via") or ""
        argument = None
        position = order.index(name) if name in order else -1
        if 0 <= position < len(call.args):
            argument = call.args[position]
        else:
            for keyword in call.keywords:
                if keyword.arg == name:
                    argument = keyword.value
        entry = {"parameter": name, "fed_by_kind": "", "fed_by_via": "", "fed_by_through": ""}
        if argument is None:
            entry["fed_by_kind"] = "the_site_leaves_the_parameter_to_the_builder_default"
            feed.append(entry)
            continue
        kind, via = trace(ctx, argument, params=e512.params_visible(ctx["tree"],
                                                                   call.lineno))
        through = ""
        if kind in (K_OTHER, K_LITERAL):
            inner = repo_call(ctx, argument)
            if inner is not None:
                deeper = builder_kinds(inner[1], root)
                reads = [d["kind"] for d in deeper if d["kind"] in READ_KINDS]
                params = [d for d in deeper if d["kind"] == K_PARAM]
                if reads:
                    kind, via = reads[0], inner[1].get("name") or ""
                elif params:
                    kind, via = K_PARAM, params[0].get("via") or ""
                through = (inner[1].get("rel") or "") + ":" + (inner[1].get("name") or "")
        entry.update({"fed_by_kind": kind, "fed_by_via": via, "fed_by_through": through})
        feed.append(entry)
    return feed


def _builder_class(root, ctx, value):
    """(class, record, callee) for the value, deciding "read here" before "built elsewhere"."""
    if ctx is not None:
        value_kind, value_via = trace(ctx, value)
        if value_kind in READ_KINDS:
            return B_READ_HERE, {"name": value_via, "rel": "", "line": 0,
                                 "call": e512._excerpt(value, 90)}, None
        if value_kind == K_LITERAL:
            return B_LITERAL_HERE, {"name": "", "rel": "", "line": 0,
                                    "call": e512._excerpt(value, 90)}, None
    found = repo_call(ctx, value) if ctx is not None else None
    if found:
        call, got = found
        return B_REPO, {"name": got.get("name") or "", "rel": got.get("rel") or "",
                        "line": got.get("line") or 0,
                        "call": e512._excerpt(call, 90)}, got
    first = None
    for node in ast.walk(value) if value is not None else []:
        if isinstance(node, ast.Call):
            first = node
            break
    if first is None:
        return B_NAME_ONLY, {"name": "", "rel": "", "line": 0, "call": ""}, None
    callee = e512._callee(root, ctx, first) if ctx is not None else {"class": ""}
    detail = {"name": e512._excerpt(first.func, 60) or "", "rel": "", "line": first.lineno,
              "call": e512._excerpt(first, 90)}
    if callee.get("class") == e512.CALLEE_BUILTIN:
        return B_NAME_ONLY, detail, None
    dotted = ""
    if isinstance(first.func, ast.Attribute):
        _head_id, dotted, _last = _call_target(ctx, first.func)
    if dotted and dotted.split(".")[0] in NAME_ONLY_MODULES:
        return B_NAME_ONLY, detail, None
    if isinstance(first.func, ast.Name) and first.func.id in NAME_ONLY_MODULES:
        return B_NAME_ONLY, detail, None
    return B_UNRESOLVED, detail, None


# -------------------------------------------------------------------- population


def _face(root, rel):
    return base._load_json(os.path.join(root, rel))


def population(root=None, up513=None, up512=None):
    root = root or ROOT
    rows = []
    face513 = up513 if up513 is not None else _face(root, UPSTREAM_513)
    for row in face513.get("rows") or []:
        if row.get("origin_kind") != e513.OR_OTHER_MODULE:
            continue
        rows.append({"arm": ARM_CONSTANT, "site_module": row.get("site_module") or "",
                     "source": (row.get("source") or "").replace("\\", "/"),
                     "symbol": row.get("constant") or "",
                     "line": row.get("binding_line") or 0,
                     "sites": row.get("sites") or 0,
                     "surfaces": row.get("surfaces") or []})
    face512 = up512 if up512 is not None else _face(root, UPSTREAM_512)
    for site in face512.get("sites") or []:
        if site.get("field_origin") != e512.O_BUILT_BY_A_CALL:
            continue
        rows.append({"arm": ARM_SITE,
                     "site_module": os.path.splitext(os.path.basename(site.get("source") or ""))[0],
                     "source": (site.get("source") or "").replace("\\", "/"),
                     "symbol": site.get("symbol") or "",
                     "line": site.get("line") or 0, "sites": 1, "surfaces": []})
    return sorted(rows, key=lambda r: (r["arm"], r["source"], r["line"], r["symbol"]))


def _value_of(root, row):
    """The expression the published row binds, read out of the source it names."""
    if not row["source"]:
        return None, None
    ctx = e507.ctx_of(root, row["source"])
    if ctx is None:
        return None, None
    ctx = dict(ctx, root=root)
    bound = None
    if row["arm"] == ARM_CONSTANT:
        bound = _binding_at(ctx["tree"], row["symbol"], row["line"] or 10 ** 9)
        if bound is None:
            for line, value in [(l, v) for n, v, l in _assign_nodes(ctx["tree"]) if n == row["symbol"]]:
                bound = (line, value)
    else:
        func = e512._enclosing_def(ctx["tree"], row["line"])
        node = e512._binding_value(ctx, func, row["symbol"], row["line"]) if func else None
        if node is not None:
            bound = (getattr(node, "lineno", row["line"]), node)
    return ctx, (bound[1] if bound else None)


def analyse(root=None, up513=None, up512=None):
    root = root or ROOT
    out = []
    for row in population(root, up513=up513, up512=up512):
        ctx, value = _value_of(root, row)
        rec = dict(row)
        rec.update({"builder_class": B_UNRESOLVED, "builder": {}, "return_paths": [],
                    "path_kinds": {}, "answer": A_UNRESOLVED, "parameter_feed": [],
                    "hands_over_a_read": False, "hands_over_the_clock": False,
                    "hands_over_a_parameter": False, "still_unreadable": False,
                    "value_expression": e512._excerpt(value, 90) if value is not None else ""})
        if ctx is None or value is None:
            rec["answer"] = A_OTHER
            rec["still_unreadable"] = True
            out.append(rec)
            continue
        klass, builder, got = _builder_class(root, ctx, value)
        rec["builder_class"] = klass
        rec["builder"] = builder
        if klass != B_REPO:
            rec["answer"] = _answer_for(klass, {})
            out.append(rec)
            continue
        paths = builder_kinds(got, root)
        kinds = {}
        for path in paths:
            kinds[path["kind"]] = kinds.get(path["kind"], 0) + 1
        rec["return_paths"] = paths
        rec["path_kinds"] = kinds
        rec["hands_over_a_read"] = any(k in READ_KINDS for k in kinds)
        rec["hands_over_the_clock"] = K_CLOCK in kinds
        rec["hands_over_a_parameter"] = K_PARAM in kinds
        rec["still_unreadable"] = K_OTHER in kinds
        rec["answer"] = _answer_for(klass, kinds)
        if K_PARAM in kinds:
            found_call = repo_call(ctx, value)
            if found_call is not None:
                rec["parameter_feed"] = parameter_feed(ctx, root, found_call[0], found_call[1],
                                                       paths)
        out.append(rec)
    return out


def _answer_for(builder_class, kinds):
    """The card's question, decided from the class and the published kinds alone.

    The gate re-runs this: a row's answer is never read as prose, it is re-derived.  The
    precedence is published rather than implied: a clock outranks everything (a value that
    may be "now" cannot be reproduced later), a mix of a read and a parameter is published
    as a mix instead of picking the more reassuring half, and a literal fallback beside a
    read is a mix too -- "every path reads" must stay true when it is said.
    """
    if builder_class == B_READ_HERE:
        return A_READ_HERE
    if builder_class == B_LITERAL_HERE:
        return A_LITERAL_HERE
    if builder_class == B_NAME_ONLY:
        return A_NAME_ONLY
    if builder_class != B_REPO:
        return A_UNRESOLVED
    if not kinds:
        return A_OTHER
    reads = [k for k in kinds if k in READ_KINDS]
    if K_CLOCK in kinds:
        return A_CLOCK
    if reads and K_PARAM in kinds:
        return A_MIXED
    if K_PARAM in kinds:
        return A_PARAM
    if reads and len(reads) == len(kinds):
        return A_READ
    if reads:
        return A_MIXED
    return A_OTHER


# ---------------------------------------------------------------- summary/verdict


def _count(records, key, vocab):
    counts = {k: 0 for k in vocab}
    for rec in records:
        counts[rec.get(key)] = counts.get(rec.get(key), 0) + 1
    return counts


def _summary(rows, modules_scanned):
    answers = _count(rows, "answer", ANSWER_VOCAB)
    builders = _count(rows, "builder_class", BUILDER_VOCAB)
    arms = _count(rows, "arm", ARM_VOCAB)
    kinds = {}
    for row in rows:
        for kind in (row.get("path_kinds") or {}):
            kinds[kind] = kinds.get(kind, 0) + row["path_kinds"][kind]
    repo = [r for r in rows if r["builder_class"] == B_REPO]
    return {
        "rows_in_the_built_elsewhere_bucket": len(rows),
        "rows_by_arm": arms,
        "rows_by_builder_class": builders,
        "rows_by_answer": answers,
        "return_path_kinds": dict(sorted(kinds.items())),
        "rows_built_by_an_in_repo_function": len(repo),
        "rows_whose_value_is_read_at_the_site": builders[B_READ_HERE],
        "rows_whose_value_is_a_literal_written_at_the_site": builders[B_LITERAL_HERE],
        "rows_whose_callee_only_constructs_a_name": builders[B_NAME_ONLY],
        "rows_whose_callee_could_not_be_resolved": builders[B_UNRESOLVED],
        "in_repo_builders_that_read_a_file_a_store_or_the_tree": sum(
            1 for r in repo if r["answer"] == A_READ),
        "in_repo_builders_that_hand_back_the_run_clock": sum(
            1 for r in repo if r["answer"] == A_CLOCK),
        "in_repo_builders_that_hand_back_a_parameter": sum(
            1 for r in repo if r["answer"] == A_PARAM),
        "in_repo_builders_with_a_path_that_stays_unreadable": sum(
            1 for r in repo if r["still_unreadable"]),
        "distinct_in_repo_builders": len({(r["builder"].get("rel"), r["builder"].get("name"))
                                          for r in repo}),
        "rows_with_a_parameter_feed": sum(1 for r in rows if r.get("parameter_feed")),
        "supplied_parameters_fed_by_a_read_at_the_call_site": sum(
            1 for r in rows for f in (r.get("parameter_feed") or []) if f["fed_by_kind"] in READS),
        "supplied_parameters_fed_by_another_module_call": sum(
            1 for r in rows for f in (r.get("parameter_feed") or [])
            if f["fed_by_through"]),
        "supplied_parameters_fed_by_a_caller_parameter": sum(
            1 for r in rows for f in (r.get("parameter_feed") or [])
            if f["fed_by_kind"] == K_PARAM),
        "supplied_parameters_left_to_the_builder_default": sum(
            1 for r in rows for f in (r.get("parameter_feed") or [])
            if f["fed_by_kind"].startswith("the_site_leaves")),
        "supplied_parameters_still_unread": sum(
            1 for r in rows for f in (r.get("parameter_feed") or [])
            if f["fed_by_kind"] in (K_OTHER, K_LITERAL, "")),
        "sites_that_ride_on_a_built_elsewhere_value": sum(
            r.get("sites") or 0 for r in repo),
        "modules_scanned": modules_scanned,
    }


def _verdict(summary):
    total = summary["rows_in_the_built_elsewhere_bucket"]
    repo = summary["rows_built_by_an_in_repo_function"]
    if not total:
        return V_EMPTY
    if not repo:
        return V_NONE
    if summary["in_repo_builders_with_a_path_that_stays_unreadable"] \
            or summary["in_repo_builders_that_hand_back_the_run_clock"]:
        return V_PART
    if repo == total \
            and summary["in_repo_builders_that_read_a_file_a_store_or_the_tree"] == repo:
        return V_READ
    return V_SPLIT


def _answers(summary):
    return {
        "how_many_rows_are_in_the_built_elsewhere_bucket": summary[
            "rows_in_the_built_elsewhere_bucket"],
        "how_many_are_built_by_a_function_defined_in_an_in_repo_module": summary[
            "rows_built_by_an_in_repo_function"],
        "how_many_are_read_at_the_site_so_nothing_else_builds_them": summary[
            "rows_whose_value_is_read_at_the_site"],
        "how_many_are_a_literal_written_where_the_site_stands": summary[
            "rows_whose_value_is_a_literal_written_at_the_site"],
        "how_many_callees_only_construct_a_path_or_a_name": summary[
            "rows_whose_callee_only_constructs_a_name"],
        "how_many_callees_could_not_be_resolved": summary["rows_whose_callee_could_not_be_resolved"],
        "how_many_in_repo_builders_read_a_file_a_store_or_the_tree": summary[
            "in_repo_builders_that_read_a_file_a_store_or_the_tree"],
        "how_many_in_repo_builders_hand_back_the_run_clock": summary[
            "in_repo_builders_that_hand_back_the_run_clock"],
        "how_many_in_repo_builders_hand_back_a_parameter": summary[
            "in_repo_builders_that_hand_back_a_parameter"],
        "how_many_in_repo_builders_keep_a_path_unreadable": summary[
            "in_repo_builders_with_a_path_that_stays_unreadable"],
        "how_many_distinct_in_repo_builders_are_involved": summary["distinct_in_repo_builders"],
        "how_many_rows_publish_where_a_parameter_is_fed_from": summary[
            "rows_with_a_parameter_feed"],
        "how_many_supplied_parameters_are_a_read_at_the_call_site": summary[
            "supplied_parameters_fed_by_a_read_at_the_call_site"],
        "how_many_supplied_parameters_come_from_another_module_call": summary[
            "supplied_parameters_fed_by_another_module_call"],
        "how_many_supplied_parameters_are_another_caller_parameter": summary[
            "supplied_parameters_fed_by_a_caller_parameter"],
        "how_many_supplied_parameters_are_left_to_the_builder_default": summary[
            "supplied_parameters_left_to_the_builder_default"],
        "how_many_supplied_parameters_are_still_unread": summary[
            "supplied_parameters_still_unread"],
    }


def build(root=None, write=True, up513=None, up512=None):
    root = root or ROOT
    rows = analyse(root, up513=up513, up512=up512)
    summary = _summary(rows, len(e513.Corpus(root).by_module))
    face = {
        "card": CARD,
        "study": STUDY,
        "title": "Where does the value built by another module actually come from",
        "kind": "static_read_of_the_repo_plus_its_own_published_upstream_faces",
        "evidence_cutoff": DATE_STAMP,
        "generated": base._now(),
        "population_source": POPULATION_SOURCE,
        "arm_vocab": list(ARM_VOCAB),
        "builder_vocab": list(BUILDER_VOCAB),
        "kind_vocab": list(KIND_VOCAB),
        "answer_vocab": list(ANSWER_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "answers": _answers(summary),
        "verdict": _verdict(summary),
        "rows": rows,
        "method_limits": [
            ("one hop, and at most one nested builder inside it: a builder that hands its "
             "value to a third module is published as still_no_readable_origin rather than "
             "followed to the end"),
            ("the two upstream faces' own labels are taken as given; this study does not "
             "re-derive whether a row really is built by another module"),
            ("a binding is read at or above the published line, so a name rebound after the "
             "call site is not part of the value the site saw"),
            ("a tuple-unpacked binding is followed element by element, which is how "
             "'strat, bench, kk = BT.apply_overlay(...)' is readable at all"),
            ("the value kinds describe the builder's own return statements; whether the "
             "site reads the day out of that value is E512's question, not repeated here"),
        ],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in ("%s-%s.json" % (DATED_PREFIX, DATE_STAMP), FACE_NAME):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return face


def load_face(root=None):
    root = root or ROOT
    return base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))


def check(face=None, root=None):
    """Re-derive every published number, and every answer from its own path kinds."""
    root = root or ROOT
    face = face or load_face(root)
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if len(rows) != summary.get("rows_in_the_built_elsewhere_bucket"):
        problems.append("row count %d != summary bucket %r"
                        % (len(rows), summary.get("rows_in_the_built_elsewhere_bucket")))
    for key, field in (("rows_by_arm", "arm"), ("rows_by_builder_class", "builder_class"),
                       ("rows_by_answer", "answer")):
        vocab = {"arm": ARM_VOCAB, "builder_class": BUILDER_VOCAB, "answer": ANSWER_VOCAB}[field]
        if _count(rows, field, vocab) != summary.get(key):
            problems.append("%s counts do not re-derive" % key)
    kinds = {}
    for row in rows:
        for kind, count in (row.get("path_kinds") or {}).items():
            kinds[kind] = kinds.get(kind, 0) + count
        for kind in (row.get("path_kinds") or {}):
            if kind not in KIND_VOCAB:
                problems.append("%s:%s path kind %r outside the vocabulary"
                                % (row.get("source"), row.get("symbol"), kind))
        if row.get("answer") not in ANSWER_VOCAB:
            problems.append("%s:%s answer outside the vocabulary"
                            % (row.get("source"), row.get("symbol")))
        if row.get("builder_class") not in BUILDER_VOCAB:
            problems.append("%s:%s builder class outside the vocabulary"
                            % (row.get("source"), row.get("symbol")))
        if row.get("builder_class") != B_REPO:
            if row.get("answer") != _answer_for(row.get("builder_class"), {}):
                problems.append("%s:%s is not a repo builder but answers %r"
                                % (row.get("source"), row.get("symbol"), row.get("answer")))
            continue
        expected = _answer_for(row.get("builder_class"), row.get("path_kinds") or {})
        if row.get("answer") != expected:
            problems.append("%s:%s answer %r does not re-derive from its path kinds (got %r)"
                            % (row.get("source"), row.get("symbol"), row.get("answer"),
                               expected))
        if len(row.get("return_paths") or []) != sum((row.get("path_kinds") or {}).values()):
            problems.append("%s:%s return paths and path kinds disagree in count"
                            % (row.get("source"), row.get("symbol")))
    if dict(sorted(kinds.items())) != summary.get("return_path_kinds"):
        problems.append("return path kinds do not re-derive")
    repo = [r for r in rows if r["builder_class"] == B_REPO]
    if len(repo) != summary.get("rows_built_by_an_in_repo_function"):
        problems.append("repo-builder count does not re-derive")
    if sum(1 for r in repo if r["answer"] == A_READ) != summary.get(
            "in_repo_builders_that_read_a_file_a_store_or_the_tree"):
        problems.append("read answer count does not re-derive")
    if sum(1 for r in repo if r["still_unreadable"]) != summary.get(
            "in_repo_builders_with_a_path_that_stays_unreadable"):
        problems.append("unreadable-path count does not re-derive")
    if len({(r["builder"].get("rel"), r["builder"].get("name")) for r in repo}) != summary.get(
            "distinct_in_repo_builders"):
        problems.append("distinct builder count does not re-derive")
    if sum(r.get("sites") or 0 for r in repo) != summary.get(
            "sites_that_ride_on_a_built_elsewhere_value"):
        problems.append("site total does not re-derive")
    feeds = [f for r in rows for f in (r.get("parameter_feed") or [])]
    if len(feeds) != summary.get("rows_with_a_parameter_feed") and not feeds:
        problems.append("parameter feed count does not re-derive")
    for field, test in (
            ("supplied_parameters_fed_by_a_read_at_the_call_site",
             lambda f: f.get("fed_by_kind") in READS),
            ("supplied_parameters_fed_by_another_module_call",
             lambda f: bool(f.get("fed_by_through"))),
            ("supplied_parameters_fed_by_a_caller_parameter",
             lambda f: f.get("fed_by_kind") == K_PARAM),
            ("supplied_parameters_left_to_the_builder_default",
             lambda f: str(f.get("fed_by_kind") or "").startswith("the_site_leaves")),
            ("supplied_parameters_still_unread",
             lambda f: f.get("fed_by_kind") in (K_OTHER, K_LITERAL, ""))):
        if sum(1 for f in feeds if test(f)) != summary.get(field):
            problems.append("%s does not re-derive" % field)
    for row in rows:
        for feed in row.get("parameter_feed") or []:
            if not feed.get("parameter"):
                problems.append("%s:%s publishes a feed with no parameter name"
                                % (row.get("source"), row.get("symbol")))
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face.get("answers") != _answers(summary):
        problems.append("answers do not re-derive from the summary")
    return problems


def verify(root=None):
    """Rebuild from the tree and compare with the published file."""
    root = root or ROOT
    face = load_face(root)
    rebuilt = build(root, write=False)
    problems = []
    for key in ("summary", "answers", "verdict", "arm_vocab", "builder_vocab", "kind_vocab",
                "answer_vocab", "rows"):
        if face.get(key) != rebuilt.get(key):
            problems.append("%s differs from a fresh build" % key)
    return problems


# ---------------------------------------------------------------- selftest fixture
HELPER_FILE = """\
import json
import os
import datetime


def load_panel(path="panel.json"):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def stamp():
    return datetime.datetime.now()


def names_from(src):
    return [n for n in src]


def mystery():
    return sorted(_cache)


_cache = ("alpha",)
"""

FIX_FILE = """\
import helper
NAMES = helper.load_panel()
def surface(groups=()):
    return groups
def go():
    return surface(NAMES)
"""

FIX_CLOCK = """\
import helper
NAMES = helper.stamp()
def surface(groups=()):
    return groups
def go():
    return surface(NAMES)
"""

FIX_PARAM = """\
import helper
SOURCE = ("alpha",)
NAMES = helper.names_from(SOURCE)
def surface(groups=()):
    return groups
def go():
    return surface(NAMES)
"""

FIX_NAME_ONLY = """\
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
def surface(groups=(ROOT,)):
    return groups
def go():
    return surface(ROOT)
"""

FIX_OTHER = """\
import helper
NAMES = helper.mystery()
def surface(groups=()):
    return groups
def go():
    return surface(NAMES)
"""

FIX_TUPLE = """\
import helper

def ticket():
    first, second = helper.load_panel(), helper.stamp()
    asof = str(second)
    return asof


def go():
    return ticket()
"""

FIX_READ_HERE = """\
with open("panel.json", "r", encoding="utf-8") as fh:
    NAMES = fh.read()


def surface(groups=(NAMES,)):
    return groups


def go():
    return surface(NAMES)
"""

FIX_LITERAL_HERE = """\
NAMES = "\\n".join(["alpha", "beta"])


def surface(groups=(NAMES,)):
    return groups


def go():
    return surface(NAMES)
"""


def _fixture_upstream():
    rows = []
    for module, symbol, line in (("fix_file", "NAMES", 2), ("fix_clock", "NAMES", 2),
                                 ("fix_param", "NAMES", 3), ("fix_name_only", "ROOT", 2),
                                 ("fix_other", "NAMES", 2), ("fix_read_here", "NAMES", 2),
                                 ("fix_literal_here", "NAMES", 1)):
        rows.append({"module": module, "site_module": module,
                     "source": "scripts/%s.py" % module, "surface": "surface",
                     "constant": symbol, "binding_line": line, "sites": 1,
                     "surfaces": ["surface"],
                     "origin_kind": e513.OR_OTHER_MODULE,
                     "hops": [{"module": module, "name": symbol,
                               "kind": e513.HP_OTHER_MODULE_CALL, "detail": {}}]})
    return {"rows": rows}


def _write_fixture(root):
    files = {"scripts/helper.py": HELPER_FILE, "scripts/fix_file.py": FIX_FILE,
             "scripts/fix_clock.py": FIX_CLOCK, "scripts/fix_param.py": FIX_PARAM,
             "scripts/fix_name_only.py": FIX_NAME_ONLY, "scripts/fix_other.py": FIX_OTHER,
             "scripts/fix_read_here.py": FIX_READ_HERE,
             "scripts/fix_literal_here.py": FIX_LITERAL_HERE}
    for rel, text in files.items():
        path = os.path.join(root, rel)
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return files


def selftest():
    bad = []

    def expect(cond, label):
        if not cond:
            bad.append(label)

    tmp = tempfile.mkdtemp(prefix="e514_fixture_")
    try:
        _write_fixture(tmp)
        upstream = _fixture_upstream()
        rows = analyse(tmp, up513=upstream, up512={"sites": []})
        by_name = {r["symbol"] + "@" + r["site_module"]: r for r in rows}
        expect(len(rows) == 7, "population is %d rows, expected 7" % len(rows))

        file_row = by_name["NAMES@fix_file"]
        expect(file_row["builder_class"] == B_REPO,
               "file fixture builder class is %r" % (file_row["builder_class"],))
        expect(file_row["answer"] == A_READ, "file fixture answers %r" % (file_row["answer"],))
        expect(file_row["path_kinds"].get(K_FILE) == 1,
               "file fixture kinds are %r" % (file_row["path_kinds"],))

        clock_row = by_name["NAMES@fix_clock"]
        expect(clock_row["answer"] == A_CLOCK,
               "clock fixture answers %r" % (clock_row["answer"],))

        param_row = by_name["NAMES@fix_param"]
        expect(param_row["answer"] == A_PARAM,
               "parameter fixture answers %r" % (param_row["answer"],))

        name_row = by_name["ROOT@fix_name_only"]
        expect(name_row["builder_class"] == B_NAME_ONLY,
               "path constructor is classified %r" % (name_row["builder_class"],))
        expect(name_row["answer"] == A_NAME_ONLY,
               "path constructor answers %r" % (name_row["answer"],))

        other_row = by_name["NAMES@fix_other"]
        expect(other_row["builder_class"] == B_REPO,
               "mystery fixture builder class is %r" % (other_row["builder_class"],))
        expect(other_row["still_unreadable"] is True,
               "mystery fixture must keep an unreadable path")
        expect(other_row["answer"] in (A_OTHER, A_MIXED),
               "mystery fixture answers %r" % (other_row["answer"],))

        read_here = by_name["NAMES@fix_read_here"]
        expect(read_here["builder_class"] == B_READ_HERE,
               "read-at-the-site fixture is classified %r" % (read_here["builder_class"],))
        expect(read_here["answer"] == A_READ_HERE,
               "read-at-the-site fixture answers %r" % (read_here["answer"],))

        literal_here = by_name["NAMES@fix_literal_here"]
        expect(literal_here["builder_class"] == B_LITERAL_HERE,
               "literal-at-the-site fixture is classified %r" % (literal_here["builder_class"],))
        expect(literal_here["answer"] == A_LITERAL_HERE,
               "literal-at-the-site fixture answers %r" % (literal_here["answer"],))

        # tuple unpacking: a builder reached only through 'a, b = f(), g()'
        with io.open(os.path.join(tmp, "scripts", "fix_tuple.py"), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(FIX_TUPLE)
        ctx = e507.ctx_of(tmp, "scripts/fix_tuple.py")
        ctx = dict(ctx, root=tmp)
        value = e512._binding_value(ctx, e512._enclosing_def(ctx["tree"], 12), "second", 12)
        got = repo_call(ctx, value)
        expect(got is not None and got[1]["name"] == "stamp",
               "tuple-unpacked builder resolved to %r"
               % ((got[1]["name"],) if got else (None,)))

        summary = _summary(rows, 2)
        face = {"rows": rows, "summary": summary, "answers": _answers(summary),
                "verdict": _verdict(summary)}
        expect(check(face, tmp) == [], "check() on the fixture must be clean: %r"
               % (check(face, tmp),))

        doctored = json.loads(json.dumps(face))
        doctored["verdict"] = V_READ
        expect(check(doctored, tmp) != [], "a hand-written verdict must be refused")
        doctored = json.loads(json.dumps(face))
        for row in doctored["rows"]:
            if row["symbol"] == "NAMES" and row["site_module"] == "fix_file":
                row["answer"] = A_OTHER
                row["path_kinds"] = {K_FILE: 1}
        expect(check(doctored, tmp) != [], "an answer that contradicts its own path kinds must "
                                           "be refused")
        doctored = json.loads(json.dumps(face))
        doctored["rows"][0]["path_kinds"] = {"a_kind_that_is_not_in_the_vocabulary": 1}
        expect(check(doctored, tmp) != [], "a path kind outside the vocabulary must be refused")
        doctored = json.loads(json.dumps(face))
        doctored["summary"]["rows_built_by_an_in_repo_function"] += 1
        expect(check(doctored, tmp) != [], "an inflated builder count must be refused")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"face": FACE_NAME, "card": face["card"], "verdict": face["verdict"],
                          "rows": face["summary"]["rows_in_the_built_elsewhere_bucket"],
                          "answers": face["answers"]}, ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        problems = check()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        bad = selftest()
        print(json.dumps({"selftest": len(bad), "bad": bad}, ensure_ascii=False))
        return 0 if not bad else 1
    print("usage: run | check | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())