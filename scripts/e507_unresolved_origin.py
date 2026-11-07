"""E507 -- where the residual date symbols bind.

E504 priced 123 naming sites and left 169 (site, member) pairs unresolved plus 61 dated members
with no composing expression at all.  This study reads the residuals: for each unresolved date
symbol it finds the binding that fills it -- a local helper's return, a right-hand side in the same
module, an imported module attribute, an element of loaded data, a selftest fixture writing a
temporary path, or a one-off script that only git history still holds -- and publishes whether the
resulting name states the run clock or the data day, so a name-based rule stops having a bucket it
cannot read.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.

Reuse: the origin resolver, module binding walker and face IO of ``scripts/e504_name_compose.py``
are imported rather than copied (the population, the sites and their expressions come from E504's
own published face, never re-derived here).
"""
import ast
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e504_name_compose as base  # noqa: E402

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "unresolvedorigin_latest.json"
DATED_PREFIX = "UNRESOLVEDORIGIN"
DATE_STAMP = "2026-11-07"
CARD = "E507-WHERE-DOES-THE-DATE-COME-FROM-WHEN-THE-MODULE-NEVER-BINDS-IT"
STUDY = "E507_unresolved_origin"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "NAMECOMPOSE-2026-11-07.json")
POPULATION_SOURCE = "results/state_tilt/NAMECOMPOSE-2026-11-07.json rows with origin=unresolved"
SELF_EXCLUDED = ("e507_", "run_e507", "_e507")

# ---------------------------------------------------------------- vocabulary
R_SAME_MODULE = "same_module_binding_the_symbol_binds_here_and_its_right_hand_side_resolves"
R_LOCAL_HELPER = "local_helper_the_composition_calls_a_function_defined_in_the_same_module"
R_IMPORTED = "imported_binding_the_symbol_or_callee_comes_from_another_module"
R_SERIES = "series_element_the_date_is_an_element_of_loaded_data"
R_LITERAL = "frozen_literal_the_expression_states_the_date_itself"
R_FIXTURE = "selftest_fixture_the_site_writes_a_temporary_path_inside_a_test"
R_HISTORY = "history_only_the_symbol_binds_only_in_a_script_the_tree_no_longer_holds"
R_NOT_A_DATE = "not_a_date_the_matched_gap_carries_no_date_at_all"
R_CALLER = "caller_supplied_the_symbol_is_a_function_parameter"
R_UNREADABLE = "unreadable_no_binding_in_the_tree_or_the_scanned_history"
RES_VOCAB = (R_SAME_MODULE, R_LOCAL_HELPER, R_IMPORTED, R_SERIES, R_LITERAL,
             R_FIXTURE, R_HISTORY, R_NOT_A_DATE, R_CALLER, R_UNREADABLE)

T_CLOCK = "clock_the_name_states_the_run_day"
T_DATA = "data_the_name_states_the_data_day"
T_MIXED = "mixed_the_binding_carries_more_than_one_origin"
T_NEITHER = "neither_the_gap_carries_no_date"
T_UNKNOWN = "unknown_no_binding_could_be_read"
TRACK_VOCAB = (T_CLOCK, T_DATA, T_MIXED, T_NEITHER, T_UNKNOWN)

V_DATA = "every_residual_that_names_a_day_reads_the_data_so_the_bucket_states_the_data_day"
V_SPLIT = "the_residual_bucket_splits_between_the_run_clock_and_the_data"
V_CLOCK = "the_residual_bucket_reads_the_run_clock_so_those_names_state_the_write_day"
V_EMPTY = "no_residual_pair_carries_a_date_symbol_at_all"
VERDICT_VOCAB = (V_DATA, V_SPLIT, V_CLOCK, V_EMPTY)

N_HISTORY = "a_script_the_tree_no_longer_holds_names_this_family"
N_TREE_ONLY = "only_scripts_still_in_the_tree_name_this_family"
N_NOBODY = "no_script_in_the_tree_or_the_scanned_history_names_this_family"
NO_SITE_VOCAB = (N_HISTORY, N_TREE_ONLY, N_NOBODY)

DATE_WORDS = ("date", "cutoff", "asof", "as_of", "stamp", "day", "bar", "time", "ts")
SERIES_ATTRS = ("index", "indexes", "columns", "values", "iloc", "loc", "at")
LOADER_ATTRS = ("read_csv", "read_json", "loads", "load", "read", "read_sql", "json_load")
UNWRAP_ATTRS = ("strftime", "isoformat", "date", "replace", "strip", "str", "format",
                "to_pydatetime", "lower", "upper")
BUILTIN_WRAPPERS = ("str", "max", "min", "sorted", "next", "list", "tuple", "abs",
                    "float", "int", "round", "len")
SELFTEST_NAME_RE = re.compile(r"(^|_)(selftest|doctor|smoke)", re.I)
PREFIX_NOISE = ("-", "_")


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _mk(klass, tracks, binding="", expr="", chain=None, note=""):
    return {"class": klass, "tracks": tracks, "binding": binding,
            "resolved_expression": expr, "chain": list(chain or [])[:8], "note": note}


def _unify(results, fallback=R_SAME_MODULE):
    """One resolution from several candidates: tracks must agree or the answer is mixed."""
    results = [r for r in results if r]
    if not results:
        return _mk(R_UNREADABLE, T_UNKNOWN)
    seen_tracks = {r["tracks"] for r in results if r["tracks"] != T_UNKNOWN}
    if not seen_tracks:
        tracks = T_UNKNOWN
    elif seen_tracks == {T_CLOCK}:
        tracks = T_CLOCK
    elif seen_tracks == {T_DATA}:
        tracks = T_DATA
    elif seen_tracks == {T_NEITHER}:
        tracks = T_NEITHER
    elif T_CLOCK in seen_tracks and T_DATA in seen_tracks:
        tracks = T_MIXED
    else:
        tracks = T_MIXED
    classes = {r["class"] for r in results}
    klass = classes.pop() if len(classes) == 1 else fallback
    binding = " ; ".join([b for b in (r["binding"] for r in results) if b])[:240]
    chain = []
    for r in results:
        for c in r["chain"]:
            if c not in chain:
                chain.append(c)
    expr = next((r["resolved_expression"] for r in results if r["resolved_expression"]), "")
    note = " ; ".join([n for n in (r["note"] for r in results) if n])[:200]
    return _mk(klass, tracks, binding, expr, chain, note)


# ------------------------------------------------------------------ module ctx
_CTX_CACHE = {}
_RETURN_CACHE = {}
_RES_CACHE = {}


def ctx_of(root, rel):
    """Parse each module once: the resolver revisits the same imports from many symbols."""
    key = (root, rel)
    if key not in _CTX_CACHE:
        try:
            _CTX_CACHE[key] = build_ctx(root, rel)
        except (SyntaxError, OSError):
            _CTX_CACHE[key] = None
    return _CTX_CACHE[key]


def build_ctx(root, rel):
    path = os.path.join(root, rel)
    tree = ast.parse(base._read_text(path))
    assigns, params = base.module_assigns(tree)
    funcs = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.setdefault(node.name, node)
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                imports[alias.asname or alias.name] = node.module + "." + alias.name
    return {"rel": rel.rstrip("/"), "tree": tree, "assigns": assigns, "params": params,
            "funcs": funcs, "imports": imports}


def enclosing_func_name(tree, lineno):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", None) or (node.lineno + 10 ** 6)
            if node.lineno <= lineno <= end:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best.name if best else ""


def _module_file(root, dotted):
    parts = [p for p in dotted.split(".") if p]
    if not parts:
        return None
    tail = parts[-1]
    candidates = []
    for depth in range(len(parts) - 1, -1, -1):
        stem = os.path.join(*parts[depth:])
        candidates += [os.path.join(root, "scripts", stem + ".py"),
                       os.path.join(root, stem + ".py"),
                       os.path.join(root, "Tools", stem + ".py"),
                       os.path.join(root, "scripts", stem, "__init__.py")]
    candidates.append(os.path.join(root, "scripts", tail + ".py"))
    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    return None


def _imported_resolution(root, dotted, attr, depth, hist, seen):
    """Resolve ``module.attr`` (or a symbol imported from ``module``) in its own module."""
    if depth > 8:
        return _mk(R_IMPORTED, T_UNKNOWN, chain=["import_depth_cap"])
    target = dotted if not attr else dotted + "." + attr
    path = _module_file(root, dotted)
    if path is None:
        return _mk(R_IMPORTED, T_UNKNOWN, chain=["import:" + target + ":no_file"])
    rel = base._rel(path, root)
    ctx = ctx_of(root, rel)
    if ctx is None:
        return _mk(R_IMPORTED, T_UNKNOWN, chain=["import:" + target + ":unparseable"])
    binding = "%s:1" % rel
    if attr and attr in ctx["funcs"]:
        got = dict(_returns(ctx["funcs"][attr], ctx, root, hist, depth + 1, seen))
        got["class"] = R_IMPORTED
        got["binding"] = got["binding"] or "%s:%d" % (
            rel, ctx["funcs"][attr].lineno)
        return got
    if attr and attr in ctx["assigns"]:
        parts = [_res(rhs, ctx, root, hist, depth + 1, seen) for rhs in ctx["assigns"][attr]]
        got = _unify(parts, fallback=R_IMPORTED)
        got["class"] = R_IMPORTED
        got["binding"] = got["binding"] or binding
        return got
    # a bare ``import x`` followed by ``x.NAME`` on a module that only re-exports it
    if attr and "." in attr:
        return _imported_resolution(root, dotted, None, depth + 1, hist, seen)
    return _mk(R_IMPORTED, T_UNKNOWN, binding=binding, chain=["import:" + target + ":no_binding"])


def _returns(fn, ctx, root, hist, depth, seen):
    values = [n.value for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None]
    if not values:
        return _mk(R_LOCAL_HELPER, T_UNKNOWN,
                   binding="%s:%d" % (ctx["rel"], fn.lineno),
                   chain=["helper:%s:no_return" % fn.name])
    parts = [_res(v, ctx, root, hist, depth + 1, seen) | {"chain": [fn.name + "()"]}
             for v in values]
    got = _unify(parts, fallback=R_LOCAL_HELPER)
    if got["tracks"] == T_UNKNOWN:
        body = ast.unparse(fn)
        if any(marker in body for marker in ("open(", "read_csv", "DictReader", "json.load",
                                            "read_text", "iterrows", "to_parquet", "read_parquet")):
            got = dict(got)
            got["tracks"] = T_DATA
            got["chain"] = [fn.name + "()", "helper_reads_a_file"] + got["chain"][:6]
    got["class"] = R_LOCAL_HELPER
    got["binding"] = got["binding"] or "%s:%d" % (ctx["rel"], fn.lineno)
    return got


def _is_date_word(text):
    low = str(text).lower()
    return any(w in low for w in DATE_WORDS)


def _history_lookup(symbol, hist):
    if not hist or not hist.get("texts"):
        return None
    pat = re.compile(r"\b%s\b" % re.escape(symbol))
    hits = []
    for sha, (path, text) in hist["texts"].items():
        m = pat.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            snippet = text.splitlines()[line - 1][:160] if text.splitlines() else ""
            hits.append({"path": path, "line": line, "snippet": snippet, "blob": sha[:12]})
            if len(hits) >= 3:
                break
    return hits


def _res(node, ctx, root, hist, depth=0, seen=frozenset()):
    """Memoised front for the resolver.

    A 28k-line module binds the same symbol in dozens of places, so re-walking those subtrees
    from every residual row multiplies out: the cache is keyed on the module, the node position
    and the cycle guard, never on the caller, so the answer stays deterministic.
    """
    if node is None:
        return _mk(R_UNREADABLE, T_UNKNOWN, chain=["no_node"])
    key = (root, ctx.get("rel"), getattr(node, "lineno", -1),
           getattr(node, "col_offset", -1), type(node).__name__,
           tuple(sorted(seen))[:6], depth)
    cached = _RES_CACHE.get(key)
    if cached is not None:
        return dict(cached)
    got = _res_uncached(node, ctx, root, hist, depth, seen)
    _RES_CACHE[key] = got
    return dict(got)


def _res_uncached(node, ctx, root, hist, depth=0, seen=frozenset(), scope=None):
    """Resolve one expression node to (class, tracks, binding)."""
    if node is None:
        return _mk(R_UNREADABLE, T_UNKNOWN, chain=["no_node"])
    if depth > 10:
        return _mk(R_UNREADABLE, T_UNKNOWN, chain=["depth_cap"])
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            if base.ISO_DATE_RE.search(node.value) or base.COMPACT_DATE_RE.search(node.value):
                return _mk(R_LITERAL, T_DATA, expr=node.value[:40], chain=["literal"])
            return _mk(R_NOT_A_DATE, T_NEITHER, expr=repr(node.value)[:40], chain=["literal_tag"])
        return _mk(R_NOT_A_DATE, T_NEITHER, expr=ast.unparse(node)[:40], chain=["literal_number"])
    if isinstance(node, ast.Name):
        name = node.id
        if name in seen:
            return _mk(R_UNREADABLE, T_UNKNOWN, chain=["cycle:" + name])
        if name in ctx["assigns"]:
            parts = [_res(rhs, ctx, root, hist, depth + 1, seen | {name})
                     for rhs in ctx["assigns"][name]]
            got = _unify(parts, fallback=R_SAME_MODULE)
            if all(p["class"] == R_UNREADABLE for p in parts):
                got["class"] = R_SAME_MODULE
            got["binding"] = got["binding"] or "%s:%s" % (ctx["rel"], name)
            got["chain"] = [name] + got["chain"]
            got["resolved_expression"] = got["resolved_expression"] or name
            return got
        if name in ctx["params"]:
            return _mk(R_CALLER, T_UNKNOWN, binding="%s:param:%s" % (ctx["rel"], name),
                       chain=[name, "function_parameter"])
        if name in ctx["imports"]:
            return _imported_resolution(root, ctx["imports"][name], None, depth, hist, seen)
        hits = _history_lookup(name, hist)
        if hits:
            return _mk(R_HISTORY, T_UNKNOWN, binding=hits[0]["path"] + ":" + str(hits[0]["line"]),
                       expr=hits[0]["snippet"][:120], chain=[name, "history_only"])
        return _mk(R_UNREADABLE, T_UNKNOWN, chain=[name, "not_bound"])
    if isinstance(node, ast.Attribute):
        if node.attr in ("now", "today", "utcnow"):
            return _mk(R_SAME_MODULE, T_CLOCK, expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(node)[:60]])
        if _is_date_word(node.attr):
            return _mk(R_SAME_MODULE, T_DATA, expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(node)[:60], "date_named_attribute"])
        if node.attr in SERIES_ATTRS:
            return _mk(R_SERIES, T_DATA, expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(node)[:60], "series_attribute"])
        got = _res(node.value, ctx, root, hist, depth + 1, seen)
        if got["tracks"] != T_UNKNOWN:
            got = dict(got)
            got["resolved_expression"] = got["resolved_expression"] or ast.unparse(node)[:60]
        return got
    if isinstance(node, ast.Subscript):
        key = node.slice
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            if key.value in base.DATE_FIELDS or _is_date_word(key.value):
                return _mk(R_SAME_MODULE, T_DATA, expr=ast.unparse(node)[:60],
                           chain=[ast.unparse(node)[:60], "payload_field"])
            return _mk(R_NOT_A_DATE, T_NEITHER, expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(node)[:60], "non_date_field"])
        if isinstance(node.value, ast.Attribute) and node.value.attr in SERIES_ATTRS:
            return _mk(R_SERIES, T_DATA, expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(node.value)[:40], "element_of_loaded_series"])
        inner = _res(node.value, ctx, root, hist, depth + 1, seen)
        if inner["tracks"] in (T_DATA, T_CLOCK, T_MIXED):
            return _mk(R_SERIES, inner["tracks"], binding=inner["binding"],
                       expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(node)[:40]] + inner["chain"])
        return _mk(R_UNREADABLE, T_UNKNOWN, expr=ast.unparse(node)[:60],
                   chain=[ast.unparse(node)[:40], "subscript_base_unreadable"])
    if isinstance(node, ast.IfExp):
        return _unify([_res(node.body, ctx, root, hist, depth + 1, seen),
                       _res(node.orelse, ctx, root, hist, depth + 1, seen)])
    if isinstance(node, (ast.BoolOp,)):
        return _unify([_res(v, ctx, root, hist, depth + 1, seen) for v in node.values])
    if isinstance(node, ast.BinOp):
        return _unify([_res(node.left, ctx, root, hist, depth + 1, seen),
                       _res(node.right, ctx, root, hist, depth + 1, seen)])
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return _unify([_res(v, ctx, root, hist, depth + 1, seen) for v in node.elts])
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        shadow = set()
        for gen in node.generators:
            for sub in ast.walk(gen.target):
                if isinstance(sub, ast.Name):
                    shadow.add(sub.id)
        parts = [_res(node.elt, ctx, root, hist, depth + 1, seen | shadow)]
        parts += [_res(g.iter, ctx, root, hist, depth + 1, seen) for g in node.generators]
        return _unify(parts)
    if isinstance(node, ast.JoinedStr):
        parts = [_res(v.value if isinstance(v, ast.FormattedValue) else v,
                      ctx, root, hist, depth + 1, seen) for v in node.values]
        return _unify(parts)
    if isinstance(node, ast.FormattedValue):
        inner = _res(node.value, ctx, root, hist, depth + 1, seen)
        if inner["tracks"] != T_UNKNOWN:
            return inner
        return _mk(R_NOT_A_DATE, T_NEITHER, expr=ast.unparse(node.value)[:40],
                   chain=[ast.unparse(node.value)[:40], "format_gap"])
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            name = func.id
            if name in ("datetime", "date", "time") and not node.args:
                return _mk(R_LOCAL_HELPER, T_CLOCK, expr=ast.unparse(node)[:60], chain=[name])
            if name in ctx["funcs"]:
                got = _returns(ctx["funcs"][name], ctx, root, hist, depth, seen)
                return got
            if name in ctx["imports"]:
                return _imported_resolution(root, ctx["imports"][name], None, depth, hist, seen)
            if name in BUILTIN_WRAPPERS and node.args:
                return _res(node.args[0], ctx, root, hist, depth + 1, seen)
            if name in ctx["assigns"]:
                return _res(ast.Name(id=name), ctx, root, hist, depth + 1, seen)
            if node.args:
                got = _res(node.args[0], ctx, root, hist, depth + 1, seen)
                if got["tracks"] != T_UNKNOWN:
                    return got
            hits = _history_lookup(name, hist)
            if hits:
                return _mk(R_HISTORY, T_UNKNOWN,
                           binding=hits[0]["path"] + ":" + str(hits[0]["line"]),
                           expr=hits[0]["snippet"][:120], chain=[name, "history_only"])
            return _mk(R_UNREADABLE, T_UNKNOWN, expr=ast.unparse(node)[:60],
                       chain=[name + "()", "callee_unbound"])
        if isinstance(func, ast.Attribute):
            attr = func.attr
            owner = func.value
            if attr in LOADER_ATTRS:
                return _mk(R_SAME_MODULE, T_DATA, expr=ast.unparse(node)[:60],
                           chain=[ast.unparse(func)[:50], "data_loader"])
            if attr in ("DatetimeIndex", "to_datetime", "date_range", "Timestamp"):
                return _mk(R_IMPORTED, T_DATA, expr=ast.unparse(node)[:60],
                           chain=[ast.unparse(func)[:50], "date_index_constructor"])
            if isinstance(owner, ast.Name) and owner.id in ctx["imports"]:
                dotted = ctx["imports"][owner.id]
                return _imported_resolution(root, dotted, attr, depth, hist, seen)
            if attr in ("now", "today", "utcnow"):
                return _mk(R_SAME_MODULE, T_CLOCK, expr=ast.unparse(node)[:60],
                           chain=[ast.unparse(func)[:50]])
            if attr == "get":
                if node.args and isinstance(node.args[0], ast.Constant) \
                        and (node.args[0].value in base.DATE_FIELDS
                             or _is_date_word(node.args[0].value)):
                    return _mk(R_SAME_MODULE, T_DATA, expr=ast.unparse(node)[:60],
                               chain=[ast.unparse(node)[:50], "payload_field"])
                return _res(owner, ctx, root, hist, depth + 1, seen)
            if attr in ("strftime", "isoformat", "date", "replace", "strip", "to_pydatetime"):
                return _res(owner, ctx, root, hist, depth + 1, seen)
            if attr in ("index", "columns", "values", "iloc", "loc"):
                return _mk(R_SERIES, T_DATA, expr=ast.unparse(node)[:60],
                           chain=[ast.unparse(func)[:50], "series_access"])
            got = _res(owner, ctx, root, hist, depth + 1, seen)
            if got["tracks"] != T_UNKNOWN:
                return got
            return _mk(R_UNREADABLE, T_UNKNOWN, expr=ast.unparse(node)[:60],
                       chain=[ast.unparse(func)[:50], "method_unbound"])
        return _mk(R_UNREADABLE, T_UNKNOWN, expr=ast.unparse(node)[:60],
                   chain=["call_shape"])
    return _mk(R_UNREADABLE, T_UNKNOWN, expr=ast.unparse(node)[:60],
               chain=["node:" + type(node).__name__])


# --------------------------------------------------------------- history arm
def build_history(root, cap=2500, timeout=240):
    """Texts of python files reachable from HEAD that the working tree no longer holds."""
    info = {"ok": False, "blobs_indexed": 0, "deleted_paths": 0, "capped": False,
            "cap": cap, "error": "", "git_seconds": 0.0, "texts": {}}
    t0 = time.time()
    print("history: rev-list ...", flush=True)
    try:
        proc = subprocess.run(["git", "-C", root, "rev-list", "--objects", "HEAD", "--", "*.py"],
                              capture_output=True, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        info["error"] = repr(exc)[:160]
        return info
    print("history: rev-list rc=%d in %.1fs" % (proc.returncode, time.time() - t0), flush=True)
    if proc.returncode != 0:
        info["error"] = "rev-list rc=%d %s" % (proc.returncode,
                                               proc.stderr.decode("utf-8", "replace")[:120])
        return info
    seen, order = set(), []
    for line in proc.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2 or not parts[1].endswith(".py"):
            continue
        sha, path = parts
        if os.path.exists(os.path.join(root, path)):
            continue
        info["deleted_paths"] += 1
        if sha in seen:
            continue
        seen.add(sha)
        order.append((sha, path))
    if len(order) > cap:
        info["capped"] = True
        order = order[:cap]
    if not order:
        info["ok"] = True
        info["git_seconds"] = round(time.time() - t0, 2)
        return info
    env = dict(os.environ)
    env["GIT_NO_LAZY_FETCH"] = "1"
    print("history: cat-file batch on %d blobs ..." % len(order), flush=True)
    try:
        batch = subprocess.run(["git", "-C", root, "cat-file", "--batch"],
                               input=("\n".join(s for s, _ in order) + "\n").encode(),
                               capture_output=True, timeout=timeout, env=env)
    except Exception as exc:  # noqa: BLE001
        info["error"] = repr(exc)[:160]
        return info
    data = batch.stdout
    print("history: cat-file returned %d bytes in %.1fs"
          % (len(data), time.time() - t0), flush=True)
    i, by_sha, missing = 0, {}, 0
    while i < len(data):
        nl = data.find(b"\n", i)
        if nl < 0:
            break
        header = data[i:nl].decode("utf-8", "replace").split()
        if len(header) != 3 or header[1] != "blob":
            missing += 1
            i = nl + 1
            continue
        size = int(header[2])
        body = data[nl + 1:nl + 1 + size]
        by_sha[header[0]] = body
        i = nl + 1 + size + 1
    for sha, path in order:
        body = by_sha.get(sha)
        if not body or len(body) > 400000:
            continue
        info["texts"][sha] = (path, body.decode("utf-8", "replace")[:120000])
    info["blobs_indexed"] = len(info["texts"])
    info["ok"] = True
    info["git_seconds"] = round(time.time() - t0, 2)
    return info


def _stem_of(basename, date_text):
    idx = basename.find(date_text)
    stem = basename[:idx] if idx > 0 else basename
    return stem.strip("".join(PREFIX_NOISE)) or basename


def _no_site_arm(face, hist):
    rows = face.get("rows") or []
    named = {r.get("path") for r in rows}
    out, counts = [], {k: 0 for k in NO_SITE_VOCAB}
    for mem in face.get("members") or []:
        path = mem.get("path")
        if not path or path in named:
            continue
        base_name = os.path.basename(path)
        date_text = mem.get("name_date") or ""
        stem = _stem_of(base_name, date_text)
        hits = []
        if hist and hist.get("texts") and stem:
            for sha, (hpath, text) in hist["texts"].items():
                if stem in text:
                    pos = text.find(stem)
                    line = text.count("\n", 0, pos) + 1
                    lines = text.splitlines()
                    hits.append({"path": hpath, "line": line,
                                 "snippet": (lines[line - 1][:160] if line - 1 < len(lines)
                                             else ""),
                                 "blob": sha[:12]})
                    if len(hits) >= 3:
                        break
        klass = N_HISTORY if hits else N_NOBODY
        counts[klass] += 1
        out.append({"path": path, "basename": base_name, "stem": stem,
                    "name_date": date_text, "class": klass, "history_hits": hits})
    return out, counts


# ------------------------------------------------------------------ the study
def analyse(root=None, upstream=None, history=None):
    root = root or ROOT
    up = upstream if upstream is not None else base._load_json(os.path.join(root, UPSTREAM_FACE))
    hist = history if history is not None else build_history(root)
    sites = {s["site"]: s for s in (up.get("sites") or [])}
    residual = [r for r in (up.get("rows") or []) if r.get("origin") == base.C_UNRESOLVED]

    ctx_cache, rows, by_symbol = {}, [], {}
    print("analyse: %d residual rows" % len(residual), flush=True)
    for index, row in enumerate(residual):
        if index and index % 20 == 0:
            print("analyse: %d/%d rows" % (index, len(residual)), flush=True)
        site = sites.get(row.get("site")) or {}
        src = site.get("source") or ""
        expr_text = row.get("date_expression") or site.get("date_expression") or ""
        if src not in ctx_cache:
            ctx_cache[src] = ctx_of(root, src)
        ctx = ctx_cache[src]
        t_row = time.time()
        if ctx is None:
            got = _mk(R_UNREADABLE, T_UNKNOWN, chain=["source_unparseable"])
        else:
            try:
                node = ast.parse(expr_text, mode="eval").body
            except SyntaxError:
                node = None
            got = _res(node, ctx, root, hist) if node is not None else _mk(
                R_UNREADABLE, T_UNKNOWN, chain=["expression_unparseable"])
            func_name = enclosing_func_name(ctx["tree"], site.get("line") or 0)
            if func_name and SELFTEST_NAME_RE.search(func_name):
                got = dict(got)
                got["class"] = R_FIXTURE
                got["note"] = ("the naming site lives inside %s(); the path it composes is a "
                               "test fixture, not a published face" % func_name)[:200]
        record = {
            "path": row.get("path"),
            "site": row.get("site"),
            "source": src,
            "line": site.get("line"),
            "date_expression": expr_text,
            "upstream_chain": (row.get("symbol_chain") or [])[:8],
            "residual_class": got["class"],
            "tracks": got["tracks"],
            "binding": got["binding"],
            "resolved_expression": got["resolved_expression"][:160],
            "resolution_chain": got["chain"],
            "note": got.get("note") or "",
        }
        rows.append(record)
        spent = time.time() - t_row
        if spent > 3.0:
            print("analyse: slow row %.1fs %s:%s" % (spent, src, expr_text[:60]), flush=True)
        key = (src, expr_text)
        sym = by_symbol.setdefault(key, {
            "source": src, "line": site.get("line"), "date_expression": expr_text,
            "symbols": (row.get("symbol_chain") or [])[:6],
            "pairs": 0, "residual_class": got["class"], "tracks": got["tracks"],
            "binding": got["binding"],
            "resolved_expression": got["resolved_expression"][:160],
            "resolution_chain": got["chain"], "note": got.get("note") or "",
        })
        sym["pairs"] += 1

    no_site, no_site_counts = _no_site_arm(up, hist)
    summary = _summary(rows, residual, up, by_symbol, no_site, no_site_counts, hist)
    return {"rows": rows, "symbols": sorted(by_symbol.values(),
                                            key=lambda s: (-s["pairs"], s["source"])),
            "no_site": no_site, "summary": summary, "upstream": up,
            "history": {"ok": hist.get("ok"), "blobs_indexed": hist.get("blobs_indexed"),
                        "deleted_paths": hist.get("deleted_paths"),
                        "capped": hist.get("capped"), "cap": hist.get("cap"),
                        "git_seconds": hist.get("git_seconds"),
                        "error": hist.get("error", "")}}


def _count(rows, key, vocab):
    out = {k: 0 for k in vocab}
    for row in rows:
        if row.get(key) in out:
            out[row[key]] += 1
    return out


def _summary(rows, residual, up, by_symbol, no_site, no_site_counts, hist):
    member_sets = {}
    for row in rows:
        member_sets.setdefault(row["path"], set()).add(row["tracks"])
    by_tracks_members = {k: 0 for k in TRACK_VOCAB}
    for tracks in member_sets.values():
        if len(tracks) > 1:
            by_tracks_members[T_MIXED] += 1
        else:
            by_tracks_members[next(iter(tracks))] += 1
    unreadable = [r for r in rows if r["residual_class"] == R_UNREADABLE]
    readable = len(rows) - len(unreadable)
    tracks = _count(rows, "tracks", TRACK_VOCAB)
    return {
        "evidence_cutoff": up.get("evidence_cutoff") or DATE_STAMP,
        "upstream_pairs": (up.get("summary") or {}).get("site_member_pairs"),
        "upstream_members": (up.get("summary") or {}).get("members_with_no_site"),
        "residual_pairs": len(rows),
        "residual_members": len(member_sets),
        "residual_sites": len(by_symbol),
        "residual_share_of_upstream_pairs": (
            round(len(rows) / float(up["summary"]["site_member_pairs"]), 4)
            if (up.get("summary") or {}).get("site_member_pairs") else None),
        "pairs_by_residual_class": _count(rows, "residual_class", RES_VOCAB),
        "pairs_by_tracks": tracks,
        "members_by_tracks": by_tracks_members,
        "readable_pairs": readable,
        "unreadable_pairs": len(unreadable),
        "readable_share": round(readable / float(len(rows)), 4) if rows else None,
        "attributable_pairs": tracks.get(T_CLOCK, 0) + tracks.get(T_DATA, 0),
        "ambiguous_pairs": tracks.get(T_MIXED, 0),
        "pairs_with_a_binding": readable,
        "clock_pairs": tracks.get(T_CLOCK, 0),
        "data_pairs": tracks.get(T_DATA, 0),
        "fixture_pairs": sum(1 for r in rows if r["residual_class"] == R_FIXTURE),
        "history_only_pairs": sum(1 for r in rows if r["residual_class"] == R_HISTORY),
        "no_site_members": len(no_site),
        "no_site_by_class": no_site_counts,
        "no_site_with_history_hit": sum(1 for r in no_site if r["history_hits"]),
        "history_arm": {"blobs_indexed": hist.get("blobs_indexed"),
                        "deleted_paths": hist.get("deleted_paths"),
                        "capped": hist.get("capped"), "cap": hist.get("cap"),
                        "ok": hist.get("ok")},
    }


def _verdict(summary):
    if not summary.get("residual_pairs"):
        return V_EMPTY
    clock = summary.get("clock_pairs") or 0
    data = summary.get("data_pairs") or 0
    if clock and data:
        return V_SPLIT
    if clock:
        return V_CLOCK
    if data:
        return V_DATA
    return V_SPLIT


def _answers(summary, symbols):
    top = [{"source": s["source"], "line": s["line"], "date_expression": s["date_expression"],
            "pairs": s["pairs"], "class": s["residual_class"], "tracks": s["tracks"],
            "binding": s["binding"]} for s in symbols[:14]]
    return {
        "how_many_pairs_were_unreadable": summary["unreadable_pairs"],
        "how_many_now_read": summary["readable_pairs"],
        "how_many_are_attributable_to_one_origin": summary["attributable_pairs"],
        "how_many_are_ambiguous_because_the_symbol_is_reused": summary["ambiguous_pairs"],
        "of_which_clock": summary["clock_pairs"],
        "of_which_data": summary["data_pairs"],
        "fixture_pairs": summary["fixture_pairs"],
        "history_only_pairs": summary["history_only_pairs"],
        "largest_residual_symbols": top,
        "no_site_members": summary["no_site_members"],
        "no_site_with_a_history_hit": summary["no_site_with_history_hit"],
        "rule_reading": ("a name-based rule can find a binding for %s of %s residual pairs; %s of those "
                         "name exactly one origin (clock %s / data %s), %s are ambiguous because "
                         "the symbol is reused in the same module, %s are selftest fixtures and %s "
                         "carry no date at all"
                         % (summary["pairs_with_a_binding"], summary["residual_pairs"],
                            summary["attributable_pairs"], summary["clock_pairs"],
                            summary["data_pairs"], summary["ambiguous_pairs"],
                            summary["fixture_pairs"],
                            summary["pairs_by_tracks"].get(T_NEITHER, 0))),
    }


def build(root=None, write=True, upstream=None, history=None):
    root = root or ROOT
    got = analyse(root, upstream=upstream, history=history)
    up = got["upstream"]
    summary = got["summary"]
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("For each date symbol E504 left unresolved: which binding fills it anywhere in "
                  "the tree or the scanned history, and does the resulting name state the run "
                  "clock or the data day?"),
        "evidence_cutoff": summary["evidence_cutoff"],
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "residual_class_vocab": list(RES_VOCAB),
        "tracks_vocab": list(TRACK_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "no_site_vocab": list(NO_SITE_VOCAB),
        "method_limits": [
            "the population is E504's residual rows (origin=unresolved) and the members it "
            "published without a composing site; both come from its face, never re-derived here",
            "resolution is static and single-repository: a symbol is read in the module that "
            "names it, then in the module it is imported from (one import hop per level, depth "
            "capped at 8), then in the history blob index",
            "the history arm covers python files reachable from HEAD and absent from the working "
            "tree, capped at %s blobs, fetched with lazy fetching disabled; a blob that is not "
            "present locally is skipped rather than fetched, so a hit of zero is a statement about "
            "this clone, not about the remote" % (got["history"].get("cap"),),
            "the history arm is a snapshot: its counts are published, but the gate cannot "
            "re-derive them without re-reading every blob, so it is labelled, not re-derived",
            "a track of 'unknown' means the binding says nothing about the day (a caller-supplied "
            "parameter, a name bound nowhere); it is never folded into clock or data",
            "selftest fixtures are labelled by the enclosing function name; a fixture that writes "
            "outside a test function would be read as a production site",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary, got["symbols"]),
        "history_arm": got["history"],
        "symbols": got["symbols"],
        "rows": got["rows"],
        "no_site_members": got["no_site"],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


# ---------------------------------------------------------------------- gate
def summary_problems(summary, rows, no_site):
    problems = []
    if summary.get("residual_pairs") != len(rows):
        problems.append("summary.residual_pairs=%r is not the row count %d"
                        % (summary.get("residual_pairs"), len(rows)))
    if summary.get("pairs_by_residual_class") != _count(rows, "residual_class", RES_VOCAB):
        problems.append("pairs_by_residual_class does not re-derive from the rows")
    if summary.get("pairs_by_tracks") != _count(rows, "tracks", TRACK_VOCAB):
        problems.append("pairs_by_tracks does not re-derive from the rows")
    if summary.get("residual_members") != len({r["path"] for r in rows}):
        problems.append("residual_members is not the distinct member count")
    tracks = _count(rows, "tracks", TRACK_VOCAB)
    if summary.get("clock_pairs") != tracks.get(T_CLOCK):
        problems.append("clock_pairs is not the row count")
    if summary.get("data_pairs") != tracks.get(T_DATA):
        problems.append("data_pairs is not the row count")
    if summary.get("unreadable_pairs") != sum(1 for r in rows
                                             if r["residual_class"] == R_UNREADABLE):
        problems.append("unreadable_pairs is not the row count")
    if summary.get("attributable_pairs") != (tracks.get(T_CLOCK, 0) + tracks.get(T_DATA, 0)):
        problems.append("attributable_pairs is not the clock+data row count")
    if summary.get("ambiguous_pairs") != tracks.get(T_MIXED, 0):
        problems.append("ambiguous_pairs is not the mixed row count")
    if summary.get("fixture_pairs") != sum(1 for r in rows if r["residual_class"] == R_FIXTURE):
        problems.append("fixture_pairs is not the row count")
    if summary.get("no_site_by_class") != {k: sum(1 for r in no_site if r["class"] == k)
                                           for k in NO_SITE_VOCAB}:
        problems.append("no_site_by_class does not re-derive from the no-site table")
    if summary.get("no_site_members") != len(no_site):
        problems.append("no_site_members is not the no-site table length")
    if summary.get("no_site_with_history_hit") != sum(1 for r in no_site if r["history_hits"]):
        problems.append("no_site_with_history_hit is not the hit count")
    return problems


def row_problems(face):
    problems = list(summary_problems(face.get("summary") or {}, face.get("rows") or [],
                                     face.get("no_site_members") or []))
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    for row in rows:
        if row.get("residual_class") not in RES_VOCAB:
            problems.append("%s: residual class %r outside the vocabulary"
                            % (row.get("path"), row.get("residual_class")))
        if row.get("tracks") not in TRACK_VOCAB:
            problems.append("%s: tracks %r outside the vocabulary"
                            % (row.get("path"), row.get("tracks")))
        if not row.get("date_expression"):
            problems.append("%s: row publishes no date expression" % (row.get("path"),))
        if not row.get("site"):
            problems.append("%s: row names no site" % (row.get("path"),))
    for sym in face.get("symbols") or []:
        if sym.get("residual_class") not in RES_VOCAB:
            problems.append("%s:%r: symbol class outside the vocabulary"
                            % (sym.get("source"), sym.get("date_expression")))
        if not sym.get("pairs"):
            problems.append("%s:%r: symbol names no pair"
                            % (sym.get("source"), sym.get("date_expression")))
    for rec in face.get("no_site_members") or []:
        if rec.get("class") not in NO_SITE_VOCAB:
            problems.append("%s: no-site class outside the vocabulary" % (rec.get("path"),))
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict=%r does not re-derive from the summary (%r)"
                        % (face.get("verdict"), _verdict(summary)))
    if (face.get("answers") or {}).get("how_many_now_read") != summary.get("readable_pairs"):
        problems.append("answers.how_many_now_read is not the readable pair count")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
ALPHA = '''import datetime


def _now():
    return datetime.datetime.now()


def _selftest():
    for dig in ("20261019",):
        p = "marks-%s.jsonl" % dig
    return p


def build():
    return "STATE-%s.json" % _now().strftime("%Y%m%d")
'''

BETA = '''def build(face):
    cutoff = face["evidence_cutoff"]
    return "SLICE-%s.json" % cutoff
'''

GAMMA = '''import json


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def build():
    bench = _load("data/bench.json")
    cutoff = bench[-1][0]
    return "REGIME5-%s.json" % cutoff
'''

EPSILON = '''def build():
    return "OLD-%s.json" % _gone_stamp
'''

ZETA = '''def _compose(mode):
    tag = "-X3" if mode else ""
    return "COST-%s%s.json" % ("2026-11-07", tag)
'''


def _fixture_upstream():
    def site(sid, source, line, expr, members, origin=base.C_UNRESOLVED):
        return ({"site": sid, "source": source, "line": line, "expression": expr,
                 "date_expression": expr, "origin": origin, "members_named": len(members),
                 "members": members},
                [{"path": p, "site": sid, "origin": origin, "spelling": "compact",
                  "date_expression": expr, "gap": 0, "symbol_chain": []} for p in members])

    sites, rows = [], []
    for sid, source, line, expr, members in (
            ("S0001", "scripts/alpha.py", 12, "_now().strftime('%Y%m%d')",
             ["results/state_tilt/STATE-20261019.json"]),
            ("S0002", "scripts/beta.py", 3, "cutoff",
             ["results/state_tilt/SLICE-2026-10-19.json"]),
            ("S0003", "scripts/gamma.py", 10, "cutoff",
             ["results/state_tilt/REGIME5-2026-10-19.json"]),
            ("S0004", "scripts/alpha.py", 8, "dig",
             ["results/state_tilt/marks-20261019.jsonl"]),
            ("S0005", "scripts/epsilon.py", 2, "_gone_stamp",
             ["results/state_tilt/OLD-2026-10-19.json"]),
            ("S0006", "scripts/zeta.py", 3, "tag",
             ["results/state_tilt/COST-2026-11-07X3.json"])):
        site_row, site_rows = site(sid, source, line, expr, members)
        sites.append(site_row)
        rows.extend(site_rows)
    members = [
        {"path": "results/state_tilt/STATE-20261019.json", "spelling": "compact",
         "name_date": "20261019"},
        {"path": "results/state_tilt/SLICE-2026-10-19.json", "spelling": "iso",
         "name_date": "2026-10-19"},
        {"path": "results/state_tilt/REGIME5-2026-10-19.json", "spelling": "iso",
         "name_date": "2026-10-19"},
        {"path": "results/state_tilt/marks-20261019.jsonl", "spelling": "compact",
         "name_date": "20261019"},
        {"path": "results/state_tilt/OLD-2026-10-19.json", "spelling": "iso",
         "name_date": "2026-10-19"},
        {"path": "results/state_tilt/COST-2026-11-07X3.json", "spelling": "iso",
         "name_date": "2026-11-07"},
        {"path": "results/state_tilt/NOBODY-2026-10-19.json", "spelling": "iso",
         "name_date": "2026-10-19"},
        {"path": "results/state_tilt/GHOSTED-2026-10-19.json", "spelling": "iso",
         "name_date": "2026-10-19"},
    ]
    return {"study": "fixture", "card": "fixture", "evidence_cutoff": "2026-10-19",
            "sites": sites, "rows": rows, "members": members,
            "summary": {"site_member_pairs": len(rows), "members_with_no_site": 2}}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e507_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        for name, body in (("alpha.py", ALPHA), ("beta.py", BETA), ("gamma.py", GAMMA),
                           ("epsilon.py", EPSILON), ("zeta.py", ZETA)):
            with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
        up = _fixture_upstream()
        up_path = os.path.join(tmp, "results", "state_tilt", "NAMECOMPOSE-FIX.json")
        with io.open(up_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(up, fh)
        hist = {"ok": True, "blobs_indexed": 1, "deleted_paths": 1, "capped": False,
                "cap": 10, "git_seconds": 0.0, "error": "",
                "texts": {"deadbeef": ("scripts/_r9_ghost.py",
                                      "_gone_stamp = '2026-10-19'\n"
                                      "NAME = 'GHOSTED-%s.json' % _gone_stamp\n")}}
        face = build(root=tmp, write=False, upstream=up, history=hist)
        by_source = {}
        for row in face["rows"]:
            by_source.setdefault(row["source"], []).append(row)
        ok("every residual row got a record", len(face["rows"]) == 6, len(face["rows"]))
        ok("a local helper that returns the clock is priced as clock",
           any(r["tracks"] == T_CLOCK and r["residual_class"] == R_LOCAL_HELPER
               for r in by_source.get("scripts/alpha.py", [])
               if r["date_expression"].startswith("_now")),
           by_source.get("scripts/alpha.py"))
        ok("a same-module payload binding is priced as data",
           any(r["tracks"] == T_DATA and r["residual_class"] == R_SAME_MODULE
               for r in by_source.get("scripts/beta.py", [])),
           by_source.get("scripts/beta.py"))
        ok("a loaded-series element is priced as data",
           any(r["tracks"] == T_DATA and r["residual_class"] in (R_SERIES, R_SAME_MODULE)
               for r in by_source.get("scripts/gamma.py", [])),
           by_source.get("scripts/gamma.py"))
        ok("a selftest site is labelled a fixture",
           any(r["residual_class"] == R_FIXTURE
               for r in by_source.get("scripts/alpha.py", [])
               if r["date_expression"] == "dig"),
           by_source.get("scripts/alpha.py"))
        ok("a symbol that only history holds is labelled history-only",
           any(r["residual_class"] == R_HISTORY
               for r in by_source.get("scripts/epsilon.py", [])),
           by_source.get("scripts/epsilon.py"))
        ok("a cost tag is not read as a date",
           any(r["tracks"] == T_NEITHER and r["residual_class"] == R_NOT_A_DATE
               for r in by_source.get("scripts/zeta.py", [])),
           by_source.get("scripts/zeta.py"))
        ok("the fixture verdict splits clock and data",
           face["verdict"] == V_SPLIT, face["verdict"])
        ok("gate passes on the built fixture", row_problems(face) == [], row_problems(face))
        ok("no-site members are counted", face["summary"]["no_site_members"] == 2,
           face["summary"]["no_site_members"])
        ok("a no-site member whose family only history names is labelled",
           any(r["class"] == N_HISTORY for r in face["no_site_members"]),
           face["no_site_members"])
        ok("a no-site member nobody names is labelled honestly",
           any(r["class"] == N_NOBODY for r in face["no_site_members"]),
           face["no_site_members"])

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["unreadable_pairs"] += 1
        ok("gate refuses a hand-written unreadable count", row_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["verdict"] = V_CLOCK
        ok("gate refuses a hand-written verdict", row_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        doctored3["rows"][0]["residual_class"] = "guessed"
        ok("gate refuses a class outside the vocabulary", row_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        doctored4["summary"]["clock_pairs"] = 0
        ok("gate refuses a clock count the rows contradict", row_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        doctored5["no_site_members"][0]["class"] = N_HISTORY
        doctored5["no_site_members"] = [r for r in doctored5["no_site_members"]
                                        if r["class"] == N_HISTORY] + [
            {"path": "results/state_tilt/EXTRA-2026-10-19.json", "class": N_NOBODY,
             "history_hits": [], "stem": "EXTRA"}]
        ok("gate refuses a no-site table that disagrees with its own counts",
           row_problems(doctored5) != [])
        ok("history arm reports what it scanned",
           face["history_arm"].get("blobs_indexed") == 1, face["history_arm"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks - len(failures), checks))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())