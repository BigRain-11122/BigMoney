"""E403 -- a reader that takes its family as a parameter is only safe if every caller passes it.

E398 (r1421) classified 190 read sites of a `latest.json` pointer and found 17 whose family is
not stated at the site but **required by the signature**: ``os.path.join(outdir,
'starself_latest.json')``. The face name is a literal there, so the census stopped at "somebody
must pass the directory", and the callers were never measured. That is the gap this closes.

For each of those readers it asks, statically and without rewriting anything:

  1. which directory does each in-repo call actually pass -- the module's own family, a scratch
     directory the caller just wrote into, its own caller's parameter (forwarded), a module
     constant naming a *different* family, or a value no static read can resolve;
  2. what does the reader do when the argument is omitted (`param or DEFAULT` -- measured off the
     body, not assumed);
  3. which published family directories that set of calls can actually reach;
  4. which reader is therefore one call away from reading a family it did not mean.

The bill is the per-reader call list plus that sentence. No caller is edited -- a caller that
passes the wrong family is a separate card, and the value of this face is that it names it.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from datetime import datetime, timezone

import population_keys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
PANEL = os.path.join(ROOT, "data", "daily", "sh510300.csv")
SEED_FACE = os.path.join(OUT_DIR, "latestfamily_latest.json")
SELF = os.path.relpath(os.path.abspath(__file__), ROOT).replace(os.sep, "/")

SKIP_DIRS = {".git", ".codely-cli", "__pycache__", "node_modules", "legacy", "Money02"}
# A caller has to be importable to reach a reader, and only scripts/, Tools/ and the repo root
# are on the chain's sys.path. results/ holds 8600 artefacts (fixture copies, scratch probes),
# not modules, and parsing them cost 70 of this leg's 77 seconds.
PYCORPUS_SKIP = {"results", "logs"}

# The 17 signature-parameter read sites E398 published, frozen here as the seed population so
# this face re-derives without E398's face file being present. When the face is on disk the
# build re-reads it and publishes any delta instead of trusting the copy.
SEED_READERS = [
    ("scripts/e252_star_prices_itself.py", "verify", "outdir", 2),
    ("scripts/e253_self_row_resolution.py", "verify", "outdir", 1),
    ("scripts/e254_band_exponent_inside_cell.py", "verify", "outdir", 1),
    ("scripts/e255_band_draw_starvation.py", "verify", "outdir", 1),
    ("scripts/e257_band_at_top_flips.py", "_write", "outdir", 1),
    ("scripts/e258_band_multiplier_per_window.py", "_write", "outdir", 1),
    ("scripts/e259_band_multiplier_distribution.py", "_write", "outdir", 1),
    ("scripts/e260_band_endpoint_arrival.py", "_write", "outdir", 1),
    ("scripts/e261_degenerate_seeds_leave_one_bucket.py", "_write", "outdir", 1),
    ("scripts/e263_arrival_vs_cell_size.py", "_write", "outdir", 1),
    ("scripts/etf_book_bakeoff.py", "published_control_cagr", "path", 1),
    ("scripts/etf_book_tsmom.py", "published_control_cagr", "path", 1),
    ("scripts/etf_book_order.py", "card_width", "card_dir", 1),
    ("scripts/etf_book_order.py", "card_book", "card_dir", 1),
    ("scripts/etf_book_order.py", "card_rule", "card_dir", 1),
    ("scripts/etf_book_order.py", "_read_card", "card_dir", 1),
]

# Counts of the corpus this study scanned. They move whenever a .py file appears or is deleted,
# so they are declared (and published) instead of sitting in a leg's equality gate -- see
# scripts/population_keys.py for the r1441 recurrence that made this a mechanism.
POPULATION_KEYS = ("corpus_py_files",)

CLASSES = [
    "default_uses_the_module_family",
    "own_family_literal",
    "scratch_directory_of_the_caller",
    "forwarded_parameter",
    "loop_binding",
    "module_constant_family",
    "runtime_value",
    "starred_arguments",
]


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _panel_cutoff(root: str) -> str:
    """Last complete bar on the local daily panel -- the clock the rest of the chain uses."""
    try:
        with open(os.path.join(root, "data", "daily", "sh510300.csv"), encoding="utf-8") as fh:
            rows = [ln.strip() for ln in fh if ln.strip()]
        last = rows[-1].split(",")[0]
        return last[:10] if re.match(r"\d{4}-\d{2}-\d{2}", last) else ""
    except Exception:  # noqa: BLE001
        return ""


def _py_files(root: str) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and d not in PYCORPUS_SKIP
                             and not d.startswith("."))
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            if rel == SELF or "/_smoke" in rel or rel.startswith("results/_smoke"):
                continue
            out.append(rel)
    return out


def _module_name(rel: str) -> str:
    """Import name a file is reachable under: scripts/ and the repo root are on sys.path."""
    stem = os.path.splitext(rel)[0]
    if rel.startswith("scripts/") or "/" not in rel:
        return os.path.basename(stem)
    return stem.replace("/", ".")


def _parse(root: str, rel: str) -> ast.Module | None:
    try:
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        return ast.parse(src, filename=rel)
    except Exception:  # noqa: BLE001 - an unparseable file is reported, not guessed
        return None


def _module_consts(tree: ast.Module) -> dict:
    """Module-level `NAME = <expr>` (single target). Value is the node, resolved lazily."""
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            consts[node.targets[0].id] = node.value
    return consts


def _is_rootish(node) -> bool:
    """A name/expression that stands for the repository root by convention.

    These modules write `ROOT = os.path.dirname(HERE)` and then `os.path.join(ROOT,
    "results", "state_tilt")`. Evaluating ROOT would mean executing the module, so the
    resolver names the convention instead: the leading part is dropped and the literal
    remainder is read as a repo-relative directory. The row records which duty it dropped.
    """
    if isinstance(node, ast.Name):
        return bool(re.search(r"(ROOT|HERE|BASE|HOME)$", node.id.upper()))
    if isinstance(node, ast.Attribute):
        return bool(re.search(r"(ROOT|HERE|BASE|HOME)$", node.attr.upper()))
    if isinstance(node, ast.Call):
        src = ast.unparse(node)
        return "__file__" in src or "dirname" in src
    return False


def _eval_dir(node, consts: dict, root: str, depth: int = 0) -> str | None:
    """Best-effort static directory value. None means 'not resolvable here', never a guess."""
    if depth > 6 or node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _norm_dir(node.value, root)
    if isinstance(node, ast.Attribute) and node.attr == "results_dir":
        return "results"
    if isinstance(node, ast.Name):
        if node.id in consts:
            return _eval_dir(consts[node.id], consts, root, depth + 1)
        return None
    if isinstance(node, ast.Call):
        fn = node.func
        name = None
        if isinstance(fn, ast.Attribute):
            name = fn.attr
        elif isinstance(fn, ast.Name):
            name = fn.id
        if name in ("join", "Path", "PurePath"):
            parts = [_eval_dir(a, consts, root, depth + 1) for a in node.args]
            if parts and parts[0] is None and _is_rootish(node.args[0]):
                parts = parts[1:]
            if not parts or any(p is None for p in parts):
                if len(parts) == 1:
                    return _norm_dir(parts[0], root) if parts[0] else None
                return None
            return _norm_dir(os.path.join(*parts), root)
        if name in ("dirname", "parent"):
            if node.args:
                inner = _eval_dir(node.args[0], consts, root, depth + 1)
                if inner:
                    return _norm_dir(os.path.dirname(inner), root)
                if _is_rootish(node.args[0]):
                    return ""
            return None
        if name in ("abspath", "resolve", "str", "normpath") and node.args:
            return _eval_dir(node.args[0], consts, root, depth + 1)
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        lv = _eval_dir(node.left, consts, root, depth + 1)
        rv = _eval_dir(node.right, consts, root, depth + 1)
        if lv is None and _is_rootish(node.left):
            lv = ""
        if lv is None or rv is None:
            return None
        return _norm_dir(os.path.join(lv, rv), root)
    return None


def _as_dir(value: str | None) -> str | None:
    """A family is a directory; a resolved 'results/x/latest.json' lands in 'results/x'."""
    if not value:
        return value
    if re.search(r"\.(json|csv|parquet|md|txt)$", value):
        return os.path.dirname(value).replace(os.sep, "/") or "."
    return value


def _norm_dir(value: str, root: str) -> str | None:
    if not value:
        return None
    if os.path.isabs(value):
        try:
            rel = os.path.relpath(value, root)
        except Exception:  # noqa: BLE001
            return value
        return None if rel.startswith("..") else rel.replace(os.sep, "/")
    v = value.replace("\\", "/")
    while v.startswith("./"):
        v = v[2:]
    return v.rstrip("/")


def _func_index(tree: ast.Module) -> dict:
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _enclosing(tree: ast.Module) -> dict:
    """line -> innermost FunctionDef name (module level reported as '<module>')."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    out[child.lineno] = node.name
    return out


def _params(fn: ast.FunctionDef) -> list[str]:
    a = fn.args
    return [p.arg for p in (list(getattr(a, "posonlyargs", [])) + list(a.args))]


def _import_map(tree: ast.Module) -> dict:
    """alias -> module name, for `import X as Y` and `from X import a as b`."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out[a.asname or a.name.split(".")[0]] = a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            if node.level or not node.module:
                continue
            for a in node.names:
                out[a.asname or a.name] = node.module.split(".")[0]
                out.setdefault("%s.%s" % (node.module.split(".")[0], a.name),
                               a.name)
    return out


def _symbol_map(tree: ast.Module) -> dict:
    """alias -> (module, original name or None). None means 'the attribute names it'."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out[a.asname or a.name.split(".")[0]] = (a.name.split(".")[0], None)
        elif isinstance(node, ast.ImportFrom):
            if node.level or not node.module:
                continue
            mod = node.module.split(".")[0]
            for a in node.names:
                out[a.asname or a.name] = (mod, a.name)
    return out


def _call_index(trees: dict, consts: dict) -> dict:
    """(module, function) -> [call nodes] built in ONE pass over every AST.

    E403's first draft re-walked the whole corpus once per reader (16 x 11856 files) and did
    not finish in five minutes; one pass is the whole cost of the census.
    """
    index = {}
    for rel, tree in trees.items():
        this_mod = _module_name(rel)
        syms = _symbol_map(tree)
        refs = _module_refs(tree, consts[rel])
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            key = None
            if isinstance(f, ast.Name):
                if f.id in syms and syms[f.id][1] in (None, f.id):
                    key = (syms[f.id][0], f.id)
                elif f.id in syms:
                    key = (syms[f.id][0], syms[f.id][1])
                else:
                    key = (this_mod, f.id)
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                alias = f.value.id
                if alias in syms:
                    key = (syms[alias][0], f.attr)
                elif alias in refs:
                    key = (alias, f.attr)
            if key:
                index.setdefault(key, []).append((rel, node))
    return index


def _module_refs(tree: ast.Module, consts: dict) -> set:
    """Module names the file can reach: imports plus importlib.import_module("name")."""
    names = set(_import_map(tree).values())
    for v in consts.values():
        for n in ast.walk(v) if isinstance(v, ast.AST) else []:
            if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                    and re.match(r"^[A-Za-z_][\w]*$", n.value):
                names.add(n.value)
    return names


SCRATCH_WORDS = ("mkdtemp", "TemporaryDirectory", "tmpdir", "tmp_path", "tmpdir_path")


def _mentions(expr: str, names: set) -> bool:
    return any(re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(n), expr)
               for n in names)


PATH_CALLS = ("join", "Path", "PurePath", "str", "normpath", "abspath", "dirname", "resolve")


def _path_shaped(value) -> bool:
    """A value that produces a path: Name, join/Path/str(...), or a / b."""
    if isinstance(value, ast.Name):
        return True
    if isinstance(value, ast.Call):
        fn = value.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        return name in PATH_CALLS
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Div):
        return True
    return False


def _scratch_names(fn: ast.FunctionDef | None) -> set:
    """Locals of this function that hold a directory it created (transitively).

    `cd = os.path.join(td, "prod")` after `with tempfile.TemporaryDirectory() as td` is a
    scratch directory: the first draft only looked for the literal mkdtemp words in an
    assignment and read this as a runtime value, which is how a fixture directory can
    masquerade as an unresolvable family. Propagation is limited to path-shaped values --
    a name whose value is `len(x)` or `rc` is not a directory.
    """
    names = set()
    if fn is None:
        return names
    assigns, args_bindings = [], []
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            assigns.append(node)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                src = ast.unparse(item.context_expr)
                if any(w in src for w in SCRATCH_WORDS) and item.optional_vars is not None:
                    args_bindings.append(item.optional_vars)
    for t in args_bindings:
        if isinstance(t, ast.Name):
            names.add(t.id)
    for node in assigns:
        src = ast.unparse(node.value)
        if any(w in src for w in SCRATCH_WORDS):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
    for _pass in range(3):
        for node in assigns:
            if not _path_shaped(node.value):
                continue
            src = ast.unparse(node.value)
            if _mentions(src, names):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
    names.discard("self")
    return names


def _local_assigns(fn: ast.FunctionDef) -> dict:
    out = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out.setdefault(t.id, []).append((node.lineno, node.value))
    return out


def _classify(node, caller_fn: ast.FunctionDef | None, consts: dict, root: str,
              scratch: set | None = None) -> dict:
    """What does this argument expression resolve to?"""
    scratch = scratch if scratch is not None else _scratch_names(caller_fn)
    expr = ast.unparse(node) if node is not None else ""
    if isinstance(node, ast.Starred):
        return {"class": "starred_arguments", "expr": expr, "resolved_dir": None,
                "detail": "a *args call cannot be matched to a parameter statically"}
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        d = _eval_dir(node, consts, root)
        return {"class": "own_family_literal", "expr": expr, "resolved_dir": d,
                "detail": "a literal path"}
    if isinstance(node, ast.Name):
        if node.id in scratch:
            return {"class": "scratch_directory_of_the_caller", "expr": expr,
                    "resolved_dir": None, "detail": "a directory this caller created"}
        if caller_fn is not None:
            params = _params(caller_fn)
            if node.id in params:
                fb = _fallback_dir(caller_fn, node.id, consts, root)
                return {"class": "forwarded_parameter", "expr": expr, "resolved_dir": None,
                        "forwarded_default_dir": fb.get("dir"),
                        "forwarded_default_expr": fb.get("expr"),
                        "detail": "the caller's own parameter %r (%s)%s" % (
                            node.id, caller_fn.name,
                            "" if not fb.get("found")
                            else "; it defaults to %s" % fb.get("expr"))}
            assigns = _local_assigns(caller_fn).get(node.id) or []
            for line, value in assigns:
                if line > node.lineno:
                    continue
                if isinstance(value, ast.BoolOp) and isinstance(value.op, ast.Or):
                    inner = [_classify(v, caller_fn, consts, root, scratch) for v in value.values]
                    fallback = inner[-1]
                    return {"class": fallback["class"], "expr": expr,
                            "resolved_dir": fallback["resolved_dir"],
                            "detail": "%r = %s -> %s" % (node.id, ast.unparse(value)[:80],
                                                         fallback["detail"])}
                src = ast.unparse(value)
                if _mentions(src, scratch) or any(w in src for w in SCRATCH_WORDS):
                    return {"class": "scratch_directory_of_the_caller", "expr": expr,
                            "resolved_dir": None, "detail": "written by %s" % src[:80]}
                if isinstance(value, ast.Name) and value.id in params:
                    fb = _fallback_dir(caller_fn, value.id, consts, root)
                    return {"class": "forwarded_parameter", "expr": expr, "resolved_dir": None,
                            "forwarded_default_dir": fb.get("dir"),
                            "forwarded_default_expr": fb.get("expr"),
                            "detail": "%r = the caller's parameter %r" % (node.id, value.id)}
                d = _eval_dir(value, consts, root)
                if d:
                    return {"class": "module_constant_family", "expr": expr, "resolved_dir": d,
                            "detail": "%r = %s" % (node.id, ast.unparse(value)[:80])}
        if node.id in consts:
            d = _eval_dir(node, consts, root)
            return {"class": "module_constant_family", "expr": expr, "resolved_dir": d,
                    "detail": "module constant"}
        return {"class": "runtime_value", "expr": expr, "resolved_dir": None,
                "detail": "a free runtime name"}
    d = _eval_dir(node, consts, root)
    if d:
        return {"class": "module_constant_family", "expr": expr, "resolved_dir": d,
                "detail": "a resolved path expression"}
    if _mentions(expr, scratch) or any(w in expr for w in SCRATCH_WORDS):
        return {"class": "scratch_directory_of_the_caller", "expr": expr, "resolved_dir": None,
                "detail": "created inline"}
    return {"class": "runtime_value", "expr": expr, "resolved_dir": None,
            "detail": "not resolvable statically"}


def _fallback_dir(fn: ast.FunctionDef, param: str, consts: dict, root: str) -> dict:
    """`param = param or DEFAULT` / `d = param or DEFAULT` -- measured, not assumed."""
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.BoolOp):
            continue
        if not isinstance(node.value.op, ast.Or):
            continue
        if not any(isinstance(v, ast.Name) and v.id == param for v in node.value.values):
            continue
        default = node.value.values[-1]
        d = _eval_dir(default, consts, root)
        return {"found": True, "expr": ast.unparse(default)[:120], "dir": d}
    return {"found": False, "expr": None, "dir": None}


def _faces_by_basename(root: str) -> dict:
    out = {}
    for sub in ("results", "docs", "data"):
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(".json"):
                    rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
                    out.setdefault(fn, set()).add(rel)
    return out


def _family_dirs(root: str) -> set:
    """Published family directories: every directory that holds a *latest.json pointer."""
    fams = set()
    for sub in ("results", "docs", "data"):
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith("latest.json") or re.match(r"^.*_latest\.json$", fn):
                    fams.add(os.path.relpath(dirpath, root).replace(os.sep, "/"))
    return fams


def _seed_delta(root: str) -> dict:
    """Compare the frozen seed table with E398's published face when it is on disk."""
    if not os.path.exists(SEED_FACE):
        return {"face_present": False, "delta": None,
                "note": "E398's face is not on disk; the frozen table is the seed"}
    try:
        doc = json.load(open(SEED_FACE, encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"face_present": True, "delta": None, "error": repr(exc)[:160]}
    live = {}
    for s in doc.get("read_sites") or []:
        if s.get("class") != "family_required_by_the_signature":
            continue
        ev = s.get("evidence") or {}
        key = (str(s.get("file")), str(s.get("function")), str(ev.get("parameter")))
        live[key] = live.get(key, 0) + 1
    frozen = {(f, fn, p): n for f, fn, p, n in SEED_READERS}
    added = sorted(k for k in live if k not in frozen)
    dropped = sorted(k for k in frozen if k not in live)
    moved = sorted(k for k in live if k in frozen and live[k] != frozen[k])
    return {"face_present": True, "live_sites": sum(live.values()),
            "frozen_sites": sum(frozen.values()),
            "delta": {"added": added, "dropped": dropped, "count_moved": moved}}


def build(write: bool = True, root: str | None = None,
          readers: list | None = None, now: datetime | None = None) -> dict:
    root = root or ROOT
    now = now or datetime.now().astimezone()
    seeds = readers if readers is not None else SEED_READERS

    files = _py_files(root)
    # A caller outside the reader's own file must import it, so its source has to contain the
    # module stem. That text filter cuts the parse set from 3337 files to the few that can
    # possibly call a reader; the reader files themselves are always parsed.
    stems = {os.path.splitext(os.path.basename(rel))[0] for rel, _fn, _p, _n in seeds}
    candidates = {rel for rel, _fn, _p, _n in seeds}
    for rel in files:
        if rel in candidates:
            continue
        try:
            with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception:  # noqa: BLE001
            continue
        if any(stem in text for stem in stems):
            candidates.add(rel)
    trees = {rel: t for rel in sorted(candidates) for t in [_parse(root, rel)] if t is not None}
    modules = {}
    for rel, tree in trees.items():
        modules.setdefault(_module_name(rel), []).append(rel)
    consts = {rel: _module_consts(t) for rel, t in trees.items()}
    faces = _faces_by_basename(root)
    families = _family_dirs(root)
    index = _call_index(trees, consts)
    enc_cache = {}
    fn_cache = {}

    wanted = {}
    for rel, fn_name, param, sites in seeds:
        wanted.setdefault((rel, fn_name), {"parameter": param, "seed_sites": sites})

    ledger = []
    for (rel, fn_name), meta in sorted(wanted.items()):
        tree = trees.get(rel)
        entry = {
            "reader": "%s:%s" % (rel, fn_name),
            "file": rel,
            "function": fn_name,
            "parameter": meta["parameter"],
            "seed_sites": meta["seed_sites"],
            "found_in_tree": tree is not None,
            "signature_has_the_parameter": None,
            "fallback": None,
            "own_family_dir": None,
            "calls": [],
            "reachable_dirs": [],
            "reachable_families": [],
            "calls_that_omit_the_argument": 0,
            "calls_passing_a_foreign_family": [],
            "calls_through_a_forwarded_parameter": [],
            "verdict": None,
        }
        if tree is None:
            entry["verdict"] = "file_not_in_tree"
            ledger.append(entry)
            continue
        fn = _func_index(tree).get(fn_name)
        if fn is None:
            entry["verdict"] = "function_not_found"
            ledger.append(entry)
            continue
        entry["signature_has_the_parameter"] = meta["parameter"] in _params(fn)
        entry["fallback"] = _fallback_dir(fn, meta["parameter"], consts[rel], root)

        # what shape is the parameter: a directory the reader joins with a face name, or a
        # whole file path the reader opens directly
        shape = "path_like"
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "join" and node.args:
                if ast.unparse(node.args[0]) == meta["parameter"]:
                    shape = "directory"
                    break
        entry["parameter_shape"] = shape

        # the face basename this reader opens with that parameter
        basenames = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "join" and len(node.args) == 2 \
                    and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                basenames.append(node.args[1].value)
        base = basenames[0] if basenames else None
        entry["face_basename"] = base
        if base and base in faces:
            dirs = sorted(faces[base])
            entry["own_family_dir"] = dirs[0] if len(dirs) == 1 else dirs

        reader_mod = _module_name(rel)
        for caller_rel, node in index.get((reader_mod, fn_name), []):
            ctree = trees.get(caller_rel)
            if ctree is None:
                continue
            cconsts = consts[caller_rel]
            if caller_rel not in enc_cache:
                enc_cache[caller_rel] = _enclosing(ctree)
                fn_cache[caller_rel] = _func_index(ctree)
            params = _params(fn)
            pos = [a for a in node.args if not isinstance(a, ast.Starred)]
            arg_node = None
            how = None
            for kw in node.keywords:
                if kw.arg == meta["parameter"]:
                    arg_node, how = kw.value, "keyword"
                    break
            if arg_node is None and meta["parameter"] in params:
                idx = params.index(meta["parameter"])
                if any(isinstance(a, ast.Starred) for a in node.args):
                    arg_node, how = node.args[0], "starred"
                elif idx < len(pos):
                    arg_node, how = pos[idx], "positional"
            caller_name = enc_cache[caller_rel].get(node.lineno, "<module>")
            caller_fn = fn_cache[caller_rel].get(caller_name)
            if arg_node is None:
                cls = {"class": "default_uses_the_module_family", "expr": None,
                       "resolved_dir": entry["fallback"]["dir"],
                       "detail": "argument omitted -> %s" % (entry["fallback"]["expr"],)}
                how = how or "omitted"
            else:
                cls = _classify(arg_node, caller_fn, cconsts, root,
                                _scratch_names(caller_fn))
            entry["calls"].append({
                "caller": "%s:%s:%d" % (caller_rel, caller_name, node.lineno),
                "caller_file": caller_rel,
                "caller_function": caller_name,
                "line": node.lineno,
                "bound_by": how,
                "expr": cls.get("expr"),
                "class": cls["class"],
                "resolved_dir": cls.get("resolved_dir"),
                "forwarded_default_dir": cls.get("forwarded_default_dir"),
                "detail": cls.get("detail"),
            })

        reach = set()
        by_default = set()
        for c in entry["calls"]:
            if c["class"] == "default_uses_the_module_family":
                entry["calls_that_omit_the_argument"] += 1
            if c["class"] == "forwarded_parameter":
                entry["calls_through_a_forwarded_parameter"].append(c["caller"])
                if c.get("forwarded_default_dir"):
                    by_default.add(_as_dir(c["forwarded_default_dir"]))
            d = c.get("resolved_dir")
            fam = _as_dir(d)
            c["resolved_family_dir"] = fam
            if fam:
                reach.add(fam)
                c["resolved_family"] = fam in families
                own = entry["own_family_dir"]
                own_list = own if isinstance(own, list) else ([own] if own else [])
                if own_list and fam not in own_list:
                    entry["calls_passing_a_foreign_family"].append({
                        "call": c["caller"], "dir": fam, "own_family_dir": own})
            elif c["class"] == "scratch_directory_of_the_caller":
                reach.add("<scratch: a directory the caller just wrote>")
        entry["reachable_dirs"] = sorted(reach)
        entry["reachable_dirs_if_callers_default"] = sorted(d for d in by_default if d)
        entry["reachable_families"] = sorted(d for d in reach if d in families)
        entry["reachable_families_if_callers_default"] = sorted(
            d for d in by_default if d in families)

        if entry["calls_passing_a_foreign_family"]:
            entry["verdict"] = "a_caller_passes_a_different_family"
        elif not entry["calls"]:
            entry["verdict"] = "no_in_repo_call"
        elif entry["calls_through_a_forwarded_parameter"]:
            entry["verdict"] = "safe_here_but_its_own_caller_decides"
        elif entry["reachable_dirs"]:
            entry["verdict"] = "every_call_passes_the_family_or_a_scratch_dir"
        else:
            entry["verdict"] = "unresolved_at_static_time"
        ledger.append(entry)

    by_class = {}
    for e in ledger:
        for c in e["calls"]:
            by_class[c["class"]] = by_class.get(c["class"], 0) + 1
    summary = {
        "readers": len(ledger),
        "reader_sites_in_the_seed": sum(e["seed_sites"] for e in ledger),
        "call_sites": sum(len(e["calls"]) for e in ledger),
        "by_class": by_class,
        "readers_found_in_tree": sum(1 for e in ledger if e["found_in_tree"]),
        "readers_whose_signature_has_the_parameter":
            sum(1 for e in ledger if e["signature_has_the_parameter"]),
        "readers_with_a_measured_fallback":
            sum(1 for e in ledger if (e["fallback"] or {}).get("found")),
        "readers_with_a_fallback_dir": sum(1 for e in ledger
                                           if (e["fallback"] or {}).get("dir")),
        "readers_with_no_in_repo_call": sum(1 for e in ledger if e["verdict"] == "no_in_repo_call"),
        "readers_where_a_caller_passes_a_different_family":
            sum(1 for e in ledger if e["calls_passing_a_foreign_family"]),
        "readers_depending_on_their_own_caller":
            sum(1 for e in ledger if e["calls_through_a_forwarded_parameter"]),
        "calls_that_omit_the_argument": sum(e["calls_that_omit_the_argument"] for e in ledger),
        "calls_resolving_to_a_published_family": sum(
            1 for e in ledger for c in e["calls"]
            if c.get("resolved_family_dir") and c["resolved_family_dir"] in families),
        "readers_with_a_directory_parameter":
            sum(1 for e in ledger if e.get("parameter_shape") == "directory"),
        "readers_with_a_file_path_parameter":
            sum(1 for e in ledger if e.get("parameter_shape") == "path_like"),
        "readers_reaching_a_published_family": sum(
            1 for e in ledger
            if any(d in families for d in e["reachable_dirs"])),
        "readers_whose_forwarded_parameter_has_a_known_default": sum(
            1 for e in ledger if e.get("reachable_dirs_if_callers_default")),
        "readers_reaching_a_published_family_if_their_callers_default": sum(
            1 for e in ledger
            if any(d in families for d in e.get("reachable_dirs_if_callers_default") or [])),
        "calls_landing_on_a_scratch_directory": sum(
            1 for e in ledger for c in e["calls"]
            if c["class"] == "scratch_directory_of_the_caller"),
        "families_in_the_tree": len(families),
        "corpus_py_files": len(files),
        "corpus_files_parsed": len(trees),
        "corpus_excludes": sorted(PYCORPUS_SKIP | SKIP_DIRS),
        "faces_whose_basename_is_ambiguous": sum(
            1 for e in ledger if isinstance(e.get("own_family_dir"), list)),
        "panel_cutoff": _panel_cutoff(root),
    }

    foreign = [e["reader"] for e in ledger if e["calls_passing_a_foreign_family"]]
    forwarded = [e["reader"] for e in ledger if e["calls_through_a_forwarded_parameter"]]
    if foreign:
        verdict = "at_least_one_family_parameter_reader_is_called_with_a_different_family"
        reason = ("%d of %d readers receive a directory that is not their own family: %s"
                  % (len(foreign), len(ledger), ", ".join(foreign[:4])))
    elif forwarded:
        verdict = ("every_measured_family_is_passed_or_omitted_but_some_readers_inherit_their_"
                   "family_from_their_own_caller")
        reason = ("0 call passes a foreign family; %d of %d readers are reached through a "
                  "forwarded parameter, so their safety is a property of the caller one level "
                  "up: %s" % (len(forwarded), len(ledger), ", ".join(forwarded[:4])))
    elif summary["call_sites"] == 0:
        verdict = "no_in_repo_call_reaches_a_signature_parameter_reader"
        reason = "the parameter is never supplied in the tree; every path uses the fallback"
    else:
        verdict = "every_call_of_a_family_parameter_reader_passes_its_own_family_or_a_scratch_dir"
        reason = "0 foreign families across %d call sites" % summary["call_sites"]

    result = {
        "study": "E403_family_parameter_callers",
        "question": ("does every caller of a family-parameter reader pass the family the reader "
                     "means, or can one of them land on a different published family"),
        "title": "call-site census of the 17 read sites whose family is a function parameter",
        "evidence_cutoff": summary["panel_cutoff"] or now.strftime("%Y-%m-%d"),
        "generated": now.isoformat(timespec="seconds"),
        "verdict": verdict,
        "verdict_reason": reason,
        "seed": {
            "source": "scripts/e398_latest_family.py (E398 read_sites class "
                      "family_required_by_the_signature)",
            "frozen_readers": len(SEED_READERS),
            "frozen_sites": sum(n for *_x, n in SEED_READERS),
            "delta_vs_the_published_face": _seed_delta(root),
        },
        "summary": summary,
        "population_keys": list(POPULATION_KEYS),
        "readers": ledger,
        "method_limits": [
            "static only: a call reached through getattr/setattr, a dict of callables, or a "
            "subprocess command line is not a call site here. The S6 chain invokes these "
            "scripts as CLIs, which lands on the in-file `main()` call and is counted.",
            "a forwarded parameter is traced one level (the caller's own parameter is named); "
            "it is not chased to the top, so 'safe here' means 'the caller decides'.",
            "scratch directories are recognised from the assignment that created them "
            "(mkdtemp / TemporaryDirectory / a *_tmp* name); a scratch dir passed under "
            "another spelling reads as runtime_value rather than being assumed safe.",
            "the family universe is every directory under results/, docs/ and data/ that holds "
            "a *latest.json pointer today; a family that publishes no pointer is not a family "
            "for this census.",
            "corpus = %d python files under scripts/, Tools/ and the repo root; results/ and "
            "logs/ are excluded because they hold artefacts, not importable modules (excluding "
            "them moved 0 of the call sites). Only files whose text mentions a reader module "
            "stem are parsed, so a caller that reaches a reader through a name built at runtime "
            "is not in this census." % len(files),
        ],
    }
    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        cut = result["evidence_cutoff"]
        path = os.path.join(OUT_DIR, "FAMILYARG-%s.json" % cut.replace("-", ""))
        for p in (path, os.path.join(OUT_DIR, "familyarg_latest.json")):
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(result, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        result["_path"] = os.path.relpath(path, ROOT).replace(os.sep, "/")
    return result


def verify() -> list[str]:
    """Re-derive the published face and refuse one that no longer matches the tree."""
    problems = []
    published = os.path.join(OUT_DIR, "familyarg_latest.json")
    if not os.path.exists(published):
        return ["no published face at results/state_tilt/familyarg_latest.json"]
    old = json.load(open(published, encoding="utf-8"))
    new = build(write=False)
    if old.get("evidence_cutoff") != new["evidence_cutoff"]:
        problems.append("cutoff moved: %r vs %r"
                        % (old.get("evidence_cutoff"), new["evidence_cutoff"]))
    if old.get("verdict") != new["verdict"]:
        problems.append("verdict moved: %r vs %r" % (old.get("verdict"), new["verdict"]))
    keys, kproblems = population_keys.keys_of(old, sys.modules[__name__])
    problems.extend(kproblems)
    problems.extend(population_keys.compare(old.get("summary") or {}, new["summary"], keys))
    delta = (new["seed"].get("delta_vs_the_published_face") or {}).get("delta")
    if delta and (delta.get("added") or delta.get("dropped") or delta.get("count_moved")):
        problems.append("the seed population moved against E398's face: %r" % (delta,))
    for e in new["readers"]:
        if not e["found_in_tree"]:
            problems.append("reader file missing: %s" % e["file"])
        elif not e["signature_has_the_parameter"]:
            problems.append("reader %s no longer takes %r" % (e["reader"], e["parameter"]))
        if not e["calls"]:
            problems.append("reader %s has no in-repo call and no published reason"
                            % e["reader"])
        for c in e["calls"]:
            if c["class"] not in CLASSES:
                problems.append("call %s has unknown class %r" % (c["caller"], c["class"]))
            if c["class"] == "module_constant_family" and not c.get("resolved_dir"):
                problems.append("call %s claims a module constant but resolved no directory"
                                % c["caller"])
        # a reader whose fallback is measured must name where the omitted argument lands
        if (e["fallback"] or {}).get("found") and e["calls_that_omit_the_argument"] \
                and not e["fallback"].get("dir"):
            problems.append("reader %s omits the argument but its fallback resolved nowhere"
                            % e["reader"])
        # reachability must be recomputable from the published calls
        reach = sorted({c["resolved_family_dir"] for c in e["calls"]
                        if c.get("resolved_family_dir")}
                       | {"<scratch: a directory the caller just wrote>"
                          for c in e["calls"]
                          if c["class"] == "scratch_directory_of_the_caller"})
        if reach != e["reachable_dirs"]:
            problems.append("reader %s reachable_dirs do not re-derive: %r vs %r"
                            % (e["reader"], e["reachable_dirs"], reach))
    return problems


def selftest() -> int:
    import tempfile
    fails = []

    def ok(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + ("" if cond else " :: " + str(detail)))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        def w(rel, text):
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(p) else None
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        w("data/daily/sh510300.csv", "2026-11-04,1,2,3,4,5\n")
        w("results/homie/homie_latest.json", '{"a": 1}\n')
        w("results/other/other_latest.json", '{"a": 2}\n')
        w("scripts/reader_mod.py", "\n".join([
            "import os",
            'OUTDIR = os.path.join("results", "homie")',
            "def verify(outdir=None):",
            "    outdir = outdir or OUTDIR",
            "    with open(os.path.join(outdir, 'homie_latest.json')) as fh:",
            "        return fh.read()",
            "def main():",
            "    a = verify()",
            "    return a",
            "",
        ]))
        w("scripts/callers.py", "\n".join([
            "import os, tempfile",
            "from reader_mod import verify",
            "def leg():",
            "    td = tempfile.mkdtemp()",
            "    verify(outdir=td)",
            "def forward(outdir=None):",
            "    verify(outdir)",
            "def wrong():",
            '    verify(outdir=os.path.join("results", "other"))',
            "",
        ]))
        readers = [("scripts/reader_mod.py", "verify", "outdir", 1)]
        res = build(write=False, root=tmp, readers=readers,
                    now=datetime(2026, 11, 4, 9, 0).astimezone())
        cls = {c["caller_function"] + ":" + str(c["line"]): c for c in res["readers"][0]["calls"]}
        kinds = sorted(c["class"] for c in res["readers"][0]["calls"])
        ok("a tempfile argument is a scratch directory, not a family",
           "scratch_directory_of_the_caller" in kinds, kinds)
        ok("the caller's own parameter is published as forwarded, not as safe",
           "forwarded_parameter" in kinds, kinds)
        ok("omitting the argument resolves to the measured module family",
           res["readers"][0]["calls_that_omit_the_argument"] == 1
           and "results/homie" in res["readers"][0]["reachable_dirs"],
           res["readers"][0]["reachable_dirs"])
        ok("a call into another published family is named as a defect",
           len(res["readers"][0]["calls_passing_a_foreign_family"]) == 1,
           res["readers"][0]["calls_passing_a_foreign_family"])
        ok("the fixture's own family is resolved from the basename",
           res["readers"][0]["own_family_dir"] == "results/homie",
           res["readers"][0]["own_family_dir"])
        ok("a foreign call outranks a forwarded one in the verdict",
           res["verdict"] == "at_least_one_family_parameter_reader_is_called_with_a_different_family",
           res["verdict"])
        ok("classes are all from the published vocabulary",
           all(c["class"] in CLASSES for c in res["readers"][0]["calls"]), kinds)
        ok("the reader is not rewritten by the build",
           open(os.path.join(tmp, "scripts/reader_mod.py"), encoding="utf-8").read().count(
               "verify(outdir=None)") == 1)

        # drop the wrong call: the verdict must move to the forwarded clause, not to "clean"
        w("scripts/callers.py", "\n".join([
            "import os, tempfile",
            "from reader_mod import verify",
            "def leg():",
            "    td = tempfile.mkdtemp()",
            "    verify(outdir=td)",
            "def forward(outdir=None):",
            "    verify(outdir)",
            "",
        ]))
        res2 = build(write=False, root=tmp, readers=readers,
                     now=datetime(2026, 11, 4, 9, 0).astimezone())
        ok("without the foreign call the verdict names the forwarded parameter",
           res2["verdict"].startswith("every_measured_family_is_passed_or_omitted"),
           res2["verdict"])

        # a reader nobody calls must be published as such, not silently passed
        readers2 = [("scripts/reader_mod.py", "main", "outdir", 1)]
        res3 = build(write=False, root=tmp, readers=readers2,
                     now=datetime(2026, 11, 4, 9, 0).astimezone())
        ok("a reader with no call is published, not dropped",
           res3["readers"][0]["verdict"] in ("no_in_repo_call", "file_not_in_tree",
                                             "function_not_found"),
           res3["readers"][0]["verdict"])

        # a file that is not valid python must not be guessed at
        w("scripts/broken.py", "def oops(:\n")
        res4 = build(write=False, root=tmp, readers=readers,
                     now=datetime(2026, 11, 4, 9, 0).astimezone())
        ok("an unparseable file does not stop the census",
           res4["readers"][0]["calls"] and res4["summary"]["readers"] == 1)

    total = 11
    print("\nselftest %d/%d" % (total - len(fails), total))
    return 0 if not fails else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        res = build()
        print(json.dumps({k: res[k] for k in ("evidence_cutoff", "verdict", "summary")},
                         ensure_ascii=False, indent=1))
        print("written:", res.get("_path"))
        for e in res["readers"]:
            print("  %-58s calls=%-2d omit=%-2d reach=%s  %s" % (
                e["reader"], len(e["calls"]), e["calls_that_omit_the_argument"],
                ",".join(e["reachable_dirs"])[:40] or "-", e["verdict"]))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e403_family_arg.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))