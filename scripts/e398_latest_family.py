"""E398 -- does a reader of a ``latest.json`` pointer know which family wrote last?

E385 found that the largest merged published name is ``latest.json`` with 28 files under it: the
name is a pointer *convention*, not a face.  A reader that resolves ``latest.json`` without the
family directory in front of it is reading whichever family published last -- and every such
reader looks perfectly healthy, because the file it opens exists.

So the study is a reader census, not a name census.  Every call that opens a path whose last
component is a ``latest.json`` pointer is a site; each site is classified by *where its family
comes from*:

  CL_STATIC     the family is written at the site -- a literal with a directory in front of the
                filename, or a module constant that resolves (statically) to one;
  CL_SIGNATURE  the family is a parameter of the enclosing function: the site does not name a
                family, its callers do (and a constant default, when it has one, is published);
  CL_WRITTEN    the family comes from a path this same function just wrote (read-after-write of
                its own pointer);
  CL_UNSUPPLIED nothing in the file supplies it: the base is a free runtime name, so the site can
                land on any family whose directory the base happens to hold.

Only reads count as sites; a write of ``os.path.join(outdir, "latest.json")`` is a publisher and is
published separately, because a name match is not a reading (E392/E207 family).  For every
``CL_UNSUPPLIED`` site the face publishes the families it could land on, and the schema cost of
landing on the wrong one -- the 28 bare pointers do not share a top-level signature, so a wrong
landing is usually a different document, not the same document with other numbers.

Nothing is rewritten: no pointer is renamed, no reader is edited.  The bill is the site list plus
the sentence that says what such a reader would report if a different family wrote last.

Usage:
  python scripts/e398_latest_family.py run
  python scripts/e398_latest_family.py verify
  python scripts/e398_latest_family.py selftest
"""
from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TODAY = "2026-11-04"
FACE = "LATESTFAMILY-%s.json" % TODAY
LATEST = "latestfamily_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E398_latest_family"
SELF_REL = "scripts/e398_latest_family.py"

SKIP_DIRS = frozenset((".git", "__pycache__", "node_modules", "_quarantine", ".codely-cli",
                       "media"))
# The study's own files name the very pointers this census counts; leaving them in would let the
# mouth inflate its own tally the round it is published (E180/E207 family).
OWN_FILES = ("scripts/e398_latest_family.py", "scripts/run_e398_smoke_leg.py")

POINTER = "latest.json"

CL_STATIC = "family_stated_at_the_site"
CL_SIGNATURE = "family_required_by_the_signature"
CL_WRITTEN = "family_from_the_value_the_site_itself_wrote"
CL_UNSUPPLIED = "family_not_supplied_anywhere"
CLASSES = (CL_STATIC, CL_SIGNATURE, CL_WRITTEN, CL_UNSUPPLIED)

V_ALL_NAMED = ("every_latest_pointer_reader_names_its_family_at_the_site_or_in_its_signature_so_"
               "a_wrong_family_needs_a_wrong_caller_not_a_wrong_name")
V_MIXED = ("some_latest_pointer_readers_are_handed_their_family_and_some_take_whatever_the_base_"
           "holds_so_the_pointer_convention_is_safe_only_where_the_caller_is")
V_ALL_UNSUPPLIED = ("every_latest_pointer_reader_resolves_the_pointer_against_a_free_runtime_base_"
                    "so_each_one_reports_whichever_family_published_last_and_nothing_can_see_it")
V_NO_READS = "no_in_repo_call_opens_a_latest_pointer_so_the_convention_has_no_reader_to_misread_it"
VOCAB = frozenset({V_ALL_NAMED, V_MIXED, V_ALL_UNSUPPLIED, V_NO_READS})

READ_ATTRS = frozenset(("read_text", "read", "readlines", "load", "loads"))
WRITE_ATTRS = frozenset(("write_text", "write", "writelines", "dump", "dumps"))
PATH_ATTRS = frozenset(("join", "abspath", "normpath", "dirname", "basename", "resolve",
                        "expanduser", "realpath", "relpath"))


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- corpus

_WALK = None


def _walk():
    """Every ``.py`` file in the tree, minus the skip set and this study's own files."""
    global _WALK
    if _WALK is None:
        rows = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/")
                if rel in OWN_FILES:
                    continue
                rows.append(rel)
        _WALK = sorted(rows)
    return _WALK


def _read(rel):
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


_SRC = {}


def source(rel):
    if rel not in _SRC:
        _SRC[rel] = _read(rel)
    return _SRC[rel]


# --------------------------------------------------------------------------- pointer population

def pointer_files():
    """``(bare, named, other)``: the published pointer files as they stand on disk."""
    bare, named, other = [], [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith("latest.json"):
                continue
            if name in (FACE, LATEST):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/")
            if name == POINTER:
                bare.append(rel)
            elif name.endswith("_" + POINTER):
                named.append(rel)
            else:
                other.append(rel)
    return sorted(bare), sorted(named), sorted(other)


def top_keys(rel):
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict):
        return []
    return sorted(str(k) for k in doc)


def signature(keys):
    return "|".join(keys) if keys is not None else None


def family_of(rel):
    return os.path.dirname(rel) or "."


def schema_cost(bare_rows):
    """How often two bare pointers that a reader could confuse are even the same document."""
    sigs = {}
    for row in bare_rows:
        sigs.setdefault(row["signature"], []).append(row["family"])
    pairs = 0
    same = 0
    families = [r["family"] for r in bare_rows]
    keysets = [set(r["keys"] or []) for r in bare_rows]
    for i in range(len(bare_rows)):
        for j in range(i + 1, len(bare_rows)):
            pairs += 1
            if keysets[i] == keysets[j]:
                same += 1
    largest = max((len(v) for v in sigs.values()), default=0)
    return {
        "families": len(bare_rows),
        "distinct_top_level_signatures": len(sigs),
        "families_sharing_the_largest_signature": largest,
        "pairs_compared": pairs,
        "pairs_with_the_same_top_level_keys": same,
        "share_of_confusable_pairs_that_are_the_same_document": (
            round(same / pairs, 4) if pairs else None),
        "signature_groups": [{"signature": [s[:8] for s in sig.split("|")] if sig else [],
                              "families": fams, "n_families": len(fams)}
                             for sig, fams in sorted(sigs.items(), key=lambda kv: -len(kv[1]))],
    }


# --------------------------------------------------------------------------- static path reading

def _names(node):
    return [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]


def _str_literals(node):
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _dir_literal(text):
    """The directory a literal claims, or ``None`` when the literal is a bare basename."""
    if not isinstance(text, str):
        return None
    norm = text.replace("\\", "/")
    if "/" not in norm:
        return None
    return norm.rsplit("/", 1)[0]


def module_constants(tree):
    """``{name: expr-source}`` for module-level simple assignments."""
    out = {}
    for node in tree.body:
        targets = []
        value = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None:
            continue
        text = ast.unparse(value)
        for target in targets:
            if isinstance(target, ast.Name):
                out.setdefault(target.id, text)
    return out


FILE_SUFFIX = (".json", ".jsonl", ".csv", ".parquet", ".md", ".py", ".txt", ".log", ".html",
               ".js", ".gz", ".zip", ".yaml", ".yml")


def _join_parts(node):
    """The ordered parts of a path join (``os.path.join`` or a ``/`` chain), else ``None``."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join":
        return list(node.args)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return [node.left, node.right]
    return None


def _literal_parts(node):
    """The string literals a pure-literal path expression is built from, in order."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    parts = _join_parts(node)
    if parts is None:
        return None
    out = []
    for part in parts:
        sub = _literal_parts(part)
        if sub is None:
            return None
        out.extend(sub)
    return out


def _dir_from_parts(lits):
    if not lits:
        return None
    joined = "/".join(piece.strip("/\\").replace("\\", "/") for piece in lits if piece)
    if "/" not in joined:
        return None
    if joined.lower().endswith(FILE_SUFFIX):
        return joined.rsplit("/", 1)[0] or None
    return joined


def _static_dir_of_expr_text(text, constants, depth=0):
    """Resolve an expression source to a directory string, or ``None``."""
    if depth > 4 or not text:
        return None
    try:
        node = ast.parse(text, mode="eval").body
    except SyntaxError:
        return _dir_literal(text.strip().strip("'\""))
    found = _dir_from_parts(_literal_parts(node))
    if found:
        return found
    found = _family_suffix(node)
    if found:
        return found
    direct = _dir_literal(text.strip().strip("'\""))
    if direct:
        return direct
    for name in _names(node):
        nxt = constants.get(name)
        if nxt and nxt != text:
            found = _static_dir_of_expr_text(nxt, constants, depth + 1)
            if found:
                return found
    return None


def _module_file_for(site_rel, module_name):
    """The in-tree file that defines ``module_name`` for this site (same dir first)."""
    site_dir = os.path.dirname(site_rel)
    for cand in ("%s.py" % module_name, "%s/__init__.py" % module_name):
        rel = (site_dir + "/" + cand) if site_dir else cand
        if os.path.exists(os.path.join(ROOT, rel.replace("/", os.sep))):
            return rel
        if os.path.exists(os.path.join(ROOT, cand.replace("/", os.sep))):
            return cand
    return None


def _imports(tree):
    """``{local_name: (module, is_symbol)}`` for the file's imports."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out[alias.asname or alias.name.split(".")[0]] = (alias.name, False)
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                out[alias.asname or alias.name] = (node.module, True)
    return out


_IMPORTS = {}


def _imports_of(rel):
    if rel not in _IMPORTS:
        try:
            _IMPORTS[rel] = _imports(ast.parse(source(rel)))
        except SyntaxError:
            _IMPORTS[rel] = {}
    return _IMPORTS[rel]


def _class_consts(cls_node):
    out = {}
    for node in cls_node.body:
        if isinstance(node, ast.Assign):
            text = ast.unparse(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out.setdefault(target.id, text)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if isinstance(node.target, ast.Name):
                out.setdefault(node.target.id, ast.unparse(node.value))
    return out


def _find_def(tree, name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node
    return None


def _attr_chain(node):
    """``['D', 'LIVE_DIR']`` for ``D.LIVE_DIR``; ``None`` for anything else."""
    parts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return list(reversed(parts))
    return None


def _resolve_module_chain(site_rel, chain, depth=0):
    """Statically resolve ``a.b`` / ``a.b.c`` through in-tree imports, or ``None``."""
    if depth > 3 or not chain:
        return None
    head = chain[0]
    imported = _imports_of(site_rel).get(head)
    if not imported:
        return None
    module, is_symbol = imported
    rel = _module_file_for(site_rel, module)
    if not rel:
        return None
    try:
        tree = ast.parse(source(rel))
    except SyntaxError:
        return None
    consts = module_constants(tree)
    if is_symbol:
        attrs = chain[1:]
        if not attrs:
            return _static_dir_of_expr_text(consts.get(head) or "", consts)
        target = attrs[0]
        obj = _find_def(tree, head)
        if isinstance(obj, ast.ClassDef):
            body = _class_consts(obj)
            if target in body:
                return _static_dir_of_expr_text(body[target], dict(consts, **body))
        expr = consts.get(head)
        if expr:
            return _resolve_chain_text(site_rel, expr, attrs, depth + 1)
        return None
    attrs = chain[1:]
    if not attrs:
        return None
    first = attrs[0]
    if first in consts:
        merged = dict(consts)
        found = _static_dir_of_expr_text(consts[first], merged)
        if found and len(attrs) == 1:
            return found
    obj = _find_def(tree, first)
    if isinstance(obj, ast.ClassDef) and len(attrs) > 1:
        body = _class_consts(obj)
        if attrs[1] in body:
            return _static_dir_of_expr_text(body[attrs[1]], dict(consts, **body))
    return None


def _resolve_chain_text(site_rel, text, attrs, depth=0):
    """Resolve ``expr.attrs`` where ``expr`` is a source fragment."""
    if depth > 3:
        return None
    try:
        node = ast.parse(text, mode="eval").body
    except SyntaxError:
        return None
    if not attrs:
        return _static_dir_of_expr_text(text, module_constants(ast.parse(source(site_rel))))
    if isinstance(node, ast.Name):
        return _resolve_module_chain(site_rel, [node.id] + list(attrs), depth + 1)
    return None


def _attr_static_dir(site_rel, module_name, attr):
    return _resolve_module_chain(site_rel, [module_name, attr])


# --------------------------------------------------------------------------- site extraction

def _mode_of(call):
    mode = ""
    for i, arg in enumerate(call.args):
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            if i == 1 and isinstance(call.func, ast.Name):
                mode = arg.value
            elif i == 0 and isinstance(call.func, ast.Attribute) and call.func.attr == "open":
                mode = arg.value
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            mode = kw.value.value
    return mode


def _open_kind(call):
    """``read`` / ``write`` / ``None`` for a call that may open a file."""
    func = call.func
    if isinstance(func, ast.Name) and func.id == "open":
        mode = _mode_of(call)
        if any(ch in mode for ch in "wax"):
            return "write"
        return "read"
    if isinstance(func, ast.Attribute):
        if func.attr in READ_ATTRS:
            return "read"
        if func.attr in WRITE_ATTRS:
            return "write"
        if func.attr == "open" and isinstance(func.value, ast.Name):
            mode = _mode_of(call)
            return "write" if any(ch in mode for ch in "wax") else "read"
    return None


def _path_node(call):
    """The subexpression of ``call`` that names a ``latest.json`` path, if any."""
    parts = list(call.args) + [kw.value for kw in call.keywords]
    if isinstance(call.func, ast.Attribute):
        parts.append(call.func.value)
    best = None
    for part in parts:
        text = ast.unparse(part)
        if POINTER in text and (best is None or len(text) > len(ast.unparse(best))):
            best = part
    return best


def _haircut(node):
    """Strip read/write wrappers so the expression published is the path builder."""
    guard = 0
    while isinstance(node, ast.Call) and guard < 6:
        guard += 1
        kind = _open_kind(node)
        if kind is None:
            break
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith(("read", "write")):
            node = node.func.value
        elif node.args:
            node = node.args[0]
        else:
            break
    return node


def _enclosing_function(tree):
    """``{lineno: FunctionDef}`` for every function body line."""
    owner = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        start = min([node.lineno] + [d.lineno for d in node.decorator_list])
        end = getattr(node, "end_lineno", node.lineno)
        for line in range(start, end + 1):
            owner.setdefault(line, node)
    return owner


def _params(fnode):
    if fnode is None:
        return set()
    args = fnode.args
    names = {a.arg for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)}
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)
    return names


def _defaults(fnode):
    if fnode is None:
        return {}
    out = {}
    args = fnode.args
    positional = list(args.posonlyargs) + list(args.args)
    for name, default in zip(positional[len(positional) - len(args.defaults):], args.defaults):
        out[name.arg] = ast.unparse(default)
    for name, default in zip(args.kwonlyargs, args.kw_defaults):
        if default is not None:
            out[name.arg] = ast.unparse(default)
    return out


_BIND_CACHE = {}


def _fn_key(fnode):
    return (id(fnode), fnode.name, fnode.lineno, fnode.col_offset)


def _all_binds(fnode):
    """``[(lineno, name, expr)]`` for every simple assignment in the function, once."""
    key = _fn_key(fnode)
    if key not in _BIND_CACHE:
        rows = []
        for node in ast.walk(fnode):
            line = getattr(node, "lineno", None)
            if line is None:
                continue
            if isinstance(node, ast.Assign):
                text = ast.unparse(node.value)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        rows.append((line, target.id, text))
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                if isinstance(node.target, ast.Name):
                    rows.append((line, node.target.id, ast.unparse(node.value)))
        _BIND_CACHE[key] = rows
    return _BIND_CACHE[key]


def _local_binds(fnode, before_line):
    """``{name: expr-source}`` for assignments in the function above ``before_line``."""
    out = {}
    if fnode is None:
        return out
    for line, name, text in _all_binds(fnode):
        if line < before_line:
            out[name] = text
    return out


def _written_names(fnode):
    """Names bound to a path expression that this function opens for writing."""
    out = {}
    if fnode is None:
        return out
    bound = {}
    for node in ast.walk(fnode):
        if isinstance(node, ast.Assign):
            text = ast.unparse(node.value)
            if POINTER in text:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        bound[target.id] = text
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if isinstance(node.target, ast.Name):
                text = ast.unparse(node.value)
                if POINTER in text:
                    bound[node.target.id] = text
    if not bound:
        return out
    for node in ast.walk(fnode):
        if not isinstance(node, ast.Call) or _open_kind(node) != "write" or not node.args:
            continue
        target = ast.unparse(node.args[0])
        for name in _names(node.args[0]):
            if name in bound:
                out.setdefault(name, bound[name])
        for name in bound:
            if name in target:
                out.setdefault(name, bound[name])
    return out


def classify(node, site_rel, fnode, constants, carried=None):
    """Return ``(class, evidence)`` for the path expression ``node``."""
    text = ast.unparse(node)
    evidence = {"expr": text[:220]}
    if carried:
        evidence["carried_by"] = carried
        written = _written_names(fnode)
        if carried in written:
            return CL_WRITTEN, dict(evidence, how="carried from this function's own write",
                                    written_expr=written[carried][:200])

    # 1. the literals at the site build the directory: os.path.join('results', 'x', 'latest.json')
    built = _dir_from_parts(_literal_parts(node))
    if built:
        return CL_STATIC, dict(evidence, how="the literals at the site build the directory",
                               family_dir=built)

    # 2. a dotted module constant (``D.LIVE_DIR / 'latest.json'``, ``PATHS.results_dir``)
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute):
            chain = _attr_chain(sub)
            if chain and len(chain) > 1:
                found = _resolve_module_chain(site_rel, chain)
                if found:
                    return CL_STATIC, dict(evidence, how="an imported constant names the directory",
                                           family_dir=found, constant=".".join(chain))

    # 3. literal components that name the family suffix while the root is a runtime value:
    #    os.path.join(RUNTIME_ROOT, 'etf_book_production', 'latest.json')
    suffix = _family_suffix(node)
    if suffix:
        return CL_STATIC, dict(evidence, how="a literal component names the family directory",
                               family_suffix=suffix, root_from="a runtime value not resolvable here")

    params = _params(fnode)
    defaults = _defaults(fnode)
    binds = _local_binds(fnode, node.lineno if hasattr(node, "lineno") else 10 ** 9)
    written = _written_names(fnode)
    constants = constants or {}

    # 4. a module constant at module level of this file
    for name in _names(node):
        expr = constants.get(name)
        if expr:
            found = _static_dir_of_expr_text(expr, constants)
            if found:
                return CL_STATIC, dict(evidence, how="a module constant names the directory",
                                       family_dir=found, constant=name)

    # 5. the family is a parameter (directly, or through a local alias of one)
    for name in _names(node):
        if name in params:
            return CL_SIGNATURE, _signature_evidence(evidence, name, defaults, constants)
    for name in _names(node):
        expr = binds.get(name)
        if not expr:
            continue
        try:
            bound_names = _names(ast.parse(expr, mode="eval").body)
        except SyntaxError:
            continue
        for alias in bound_names:
            if alias in params:
                return CL_SIGNATURE, _signature_evidence(
                    dict(evidence, local_alias=name, local_expr=expr[:160]), alias, defaults,
                    constants)

    # 6. read-after-write of this function's own pointer
    for name in _names(node):
        if name in written:
            return CL_WRITTEN, dict(evidence, how="bound from this function's own write",
                                    written_expr=written[name][:200])

    # 7. a local binding that names the directory
    for name in _names(node):
        expr = binds.get(name)
        if expr:
            found = _static_dir_of_expr_text(expr, constants)
            if found:
                return CL_STATIC, dict(evidence, how="a local binding names the directory",
                                       family_dir=found, binding=name)
    return CL_UNSUPPLIED, dict(evidence, how="no literal, constant, parameter or prior write")


def _family_suffix(node):
    """The family directory the site's literals name, even when the root is a runtime value.

    ``os.path.join(ROOT, "results", "state_tilt", "x_latest.json")`` names ``results/state_tilt``
    as plainly as a single literal would; ``os.path.join(outdir, "x_latest.json")`` names nothing.
    The rule reads the trailing run of literal path components and stops at the first runtime one.
    """
    parts = _parts_seq(node)
    if parts is None:
        return None
    trailing = []
    for kind, text in reversed(parts):
        if kind in ("call", "other"):
            continue
        if kind != "lit":
            break
        if POINTER in text:
            continue
        piece = text.strip("/\\")
        if piece in ("", ".", "..") or "%" in piece or "{" in piece:
            continue
        if piece.lower().endswith(FILE_SUFFIX):
            continue
        trailing.append(piece)
    if not trailing:
        return None
    return "/".join(reversed(trailing))


def _parts_seq(node):
    """``[(kind, text)]`` for a path expression, in source order, or ``None``."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [("lit", node.value)]
    if isinstance(node, ast.Name):
        return [("name", node.id)]
    if isinstance(node, ast.IfExp):
        # the branch that actually carries the pointer is the path under question
        for branch in (node.body, node.orelse):
            if POINTER in ast.unparse(branch):
                parts = _parts_seq(branch)
                if parts is not None:
                    return parts
        return None
    parts = _join_parts(node)
    if parts is None:
        if isinstance(node, ast.Attribute):
            return [("attr", ast.unparse(node))]
        if isinstance(node, ast.Call):
            # a one-argument wrapper (``read(p)``, ``json.loads(p)``, ``Path(p)``) passes the
            # path through; anything wider is opaque
            if len(node.args) == 1 and not node.keywords:
                return _parts_seq(node.args[0])
            return [("call", ast.unparse(node))]
        return None
    out = []
    for part in parts:
        sub = _parts_seq(part)
        out.extend(sub if sub is not None else [("other", ast.unparse(part))])
    return out


def _signature_evidence(evidence, name, defaults, constants):
    default = defaults.get(name)
    resolved = _static_dir_of_expr_text(default, constants) if default else None
    how = "signature parameter with a constant default" if resolved else "signature parameter"
    return dict(evidence, how=how, parameter=name, default_dir=resolved,
                default_expr=(default or "")[:120])


def scan_file(rel, with_nodes=False):
    """Every read and write site in ``rel`` whose expression names a ``latest.json``.

    A site carries its family through a local name as often as through a literal
    (``p = os.path.join(d, "latest.json")`` then ``json.load(open(p))``), so a name bound above the
    call to an expression containing the pointer is followed -- and the carried form is published,
    because a reader whose pointer is a variable is exactly the reader that looks safe.
    """
    src = source(rel)
    if POINTER not in src:
        return []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    owner = _enclosing_function(tree)
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kind = _open_kind(node)
        if kind is None:
            continue
        line = node.lineno
        fnode = owner.get(line)
        carried = None
        path = _path_node(node)
        if path is None:
            got = _carried_path(node, fnode)
            if got is None:
                continue
            path, carried = got
        core = _haircut(path)
        text = ast.unparse(core)
        key = (line, kind)
        # the outermost expression at a line wins: json.load(open(p)) is one site, not two
        if key in found and len(found[key]["expr"]) >= len(text):
            continue
        record = {
            "site": "%s:%d" % (rel, line),
            "file": rel,
            "line": line,
            "kind": kind,
            "expr": text[:240],
            "carried_by": carried,
            "function": (fnode.name if fnode is not None else "<module>"),
        }
        if with_nodes:
            record["_node"] = core
            record["_fnode"] = fnode
        found[key] = record
    return list(found.values())


def _carried_path(call, fnode):
    """``(node, name)`` when an argument is a local name bound to a pointer expression."""
    if fnode is None:
        return None
    binds = _local_binds(fnode, call.lineno)
    for arg in list(call.args) + [kw.value for kw in call.keywords]:
        for name in _names(arg):
            expr = binds.get(name)
            if expr and POINTER in expr:
                try:
                    return ast.parse(expr, mode="eval").body, name
                except SyntaxError:
                    return None
    return None


def read_sites():
    reads, writes = [], []
    for rel in _walk():
        for site in scan_file(rel):
            target = reads if site["kind"] == "read" else writes
            target.append(site)
    return reads, writes


def classify_sites(sites):
    """Attach a class and evidence to each site by re-walking its own file once."""
    by_file = {}
    for site in sites:
        by_file.setdefault(site["file"], []).append(site)
    for rel, rows in by_file.items():
        try:
            tree = ast.parse(source(rel))
        except SyntaxError:
            tree = None
        if tree is None:
            for site in rows:
                site["class"] = CL_UNSUPPLIED
                site["evidence"] = {"expr": site["expr"], "how": "file does not parse"}
            continue
        constants = module_constants(tree)
        nodes = {(rec["site"], rec["kind"]): rec
                 for rec in scan_file(rel, with_nodes=True)}
        for site in rows:
            rec = nodes.get((site["site"], site["kind"]))
            if rec is None:
                site["class"] = CL_UNSUPPLIED
                site["evidence"] = {"expr": site["expr"], "how": "site not found on re-walk"}
                continue
            node = rec["_node"]
            klass, evidence = classify(node, rel, rec["_fnode"], constants,
                                       carried=rec.get("carried_by"))
            site["class"] = klass
            site["evidence"] = evidence
    return sites


def candidates(site, bare_rows):
    """The families a ``CL_UNSUPPLIED`` site could land on, from its literal hints."""
    hints = [lit for lit in _str_literals(ast.parse(site["expr"], mode="eval").body)
             if "/" in lit.replace("\\", "/")] if site["expr"] else []
    if hints:
        prefix = hints[0].replace("\\", "/").rsplit("/", 1)[0]
        pool = [r for r in bare_rows if r["family"].startswith(prefix)]
    else:
        pool = list(bare_rows)
    return {
        "n_candidate_families": len(pool),
        "candidate_families": [r["family"] for r in pool],
        "n_distinct_signatures_among_candidates": len({r["signature"] for r in pool}),
    }


# --------------------------------------------------------------------------- verdict

def decide(summary):
    reads = summary.get("read_sites_total") or 0
    if not reads:
        return V_NO_READS
    named = (summary.get("sites_that_name_their_family_at_the_site") or 0) + (
        summary.get("sites_handed_their_family_by_the_signature") or 0) + (
        summary.get("sites_that_read_the_pointer_they_just_wrote") or 0)
    if named == reads:
        return V_ALL_NAMED
    if named == 0:
        return V_ALL_UNSUPPLIED
    return V_MIXED


REPORT_IF_OTHER_FAMILY_WROTE_LAST = (
    "A reader whose base is a free runtime name opens whichever family last wrote that directory's "
    "latest.json, so on a night when a different family published last it reports that family's "
    "document under its own heading: the numbers, the evidence_cutoff and the verdict all change, "
    "and nothing in the read itself can tell -- the file exists, it parses, and every key the "
    "reader asks for may even be present. The mistake is silent in the healthy direction, which is "
    "why a pointer convention needs the family in the path, not in the caller's head.")


# --------------------------------------------------------------------------- build

def tier_of(rel):
    """Which kind of reader a site belongs to -- a test harness reads differently than a tool."""
    base = os.path.basename(rel)
    if base == "smoke_test.py" or (base.startswith("run_e") and "smoke_leg" in base):
        return "smoke_harness"
    if rel.startswith("results/") or base.startswith("_") or "/_" in rel:
        return "scratch_or_estate"
    return "live_tooling"


def build(write=True):
    bare, named, other = pointer_files()
    bare_rows = []
    for rel in bare:
        keys = top_keys(rel)
        bare_rows.append({
            "family": family_of(rel),
            "path": rel,
            "keys": keys,
            "n_keys": len(keys) if keys is not None else None,
            "signature": signature(keys),
            "readable": keys is not None,
        })
    reads, writes = read_sites()
    classify_sites(reads)
    classify_sites(writes)
    for site in reads:
        site["tier"] = tier_of(site["file"])
        if site["class"] == CL_UNSUPPLIED:
            site.update(candidates(site, bare_rows))

    by_class = {}
    for site in reads:
        by_class[site["class"]] = by_class.get(site["class"], 0) + 1
    for klass in CLASSES:
        by_class.setdefault(klass, 0)

    by_tier = {}
    for site in reads:
        row = by_tier.setdefault(site["tier"], {"total": 0})
        row["total"] += 1
        row[site["class"]] = row.get(site["class"], 0) + 1
    for row in by_tier.values():
        for klass in CLASSES:
            row.setdefault(klass, 0)

    live = by_tier.get("live_tooling") or {}
    live_summary = {
        "read_sites": live.get("total", 0),
        "named": (live.get(CL_STATIC, 0) + live.get(CL_SIGNATURE, 0) + live.get(CL_WRITTEN, 0)),
        "unsupplied": live.get(CL_UNSUPPLIED, 0),
    }
    live_summary["verdict"] = decide({
        "read_sites_total": live_summary["read_sites"],
        "sites_that_name_their_family_at_the_site": live.get(CL_STATIC, 0),
        "sites_handed_their_family_by_the_signature": live.get(CL_SIGNATURE, 0),
        "sites_that_read_the_pointer_they_just_wrote": live.get(CL_WRITTEN, 0),
        "sites_whose_family_is_not_supplied_anywhere": live.get(CL_UNSUPPLIED, 0),
    })

    write_by_class = {}
    for site in writes:
        write_by_class[site["class"]] = write_by_class.get(site["class"], 0) + 1

    unsupplied = [s for s in reads if s["class"] == CL_UNSUPPLIED]
    fanout = [s.get("n_candidate_families") or 0 for s in unsupplied]

    cost = schema_cost([r for r in bare_rows if r["readable"]])
    summary = {
        "pointer_files_named_latest_json": len(bare),
        "pointer_files_named_<family>_latest_json": len(named),
        "pointer_files_with_another_latest_shape": len(other),
        "families_publishing_a_bare_latest_json": len({r["family"] for r in bare_rows}),
        "read_sites_total": len(reads),
        "read_sites_in_files": len({s["file"] for s in reads}),
        "write_sites_total": len(writes),
        "sites_that_name_their_family_at_the_site": by_class[CL_STATIC],
        "sites_handed_their_family_by_the_signature": by_class[CL_SIGNATURE],
        "sites_that_read_the_pointer_they_just_wrote": by_class[CL_WRITTEN],
        "sites_whose_family_is_not_supplied_anywhere": by_class[CL_UNSUPPLIED],
        "by_class": by_class,
        "by_tier": by_tier,
        "live_tooling_only": live_summary,
        "classes_sum_to_the_read_sites": sum(by_class.values()) == len(reads),
        "write_sites_by_class": write_by_class,
        "unsupplied_sites_could_land_on_this_many_families": fanout,
        "max_families_a_single_unsupplied_reader_could_land_on": max(fanout) if fanout else 0,
        "schema_cost_of_a_wrong_landing": cost,
        "files_with_a_read_site": sorted({s["file"] for s in reads}),
        "stone": None,
    }
    summary["verdict"] = decide(summary)

    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "question": ("does a reader of a latest.json pointer know which family wrote last, and "
                     "what does it report when a different one did"),
        "classes": list(CLASSES),
        "summary": summary,
        "verdict": summary["verdict"],
        "report_if_a_different_family_wrote_last": REPORT_IF_OTHER_FAMILY_WROTE_LAST,
        "families": bare_rows,
        "read_sites": [dict(s, evidence=s.get("evidence")) for s in reads],
        "write_sites": [dict(s, evidence=s.get("evidence")) for s in writes],
        "bounds": {
            "measured": ("every in-repo call that opens a path ending in latest.json, classified by "
                         "the static origin of its family directory (literal, resolvable module "
                         "constant, function parameter, read-after-write of the same function's "
                         "pointer, or a free runtime name); the 28 bare pointers' top-level "
                         "signatures; the fan-out each unsupplied reader could reach"),
            "not_measured": ("callers of a CL_SIGNATURE site (the family is a call-site fact, so "
                             "whether every caller passes the right one is a separate census); "
                             "paths assembled from a name bound in another module and never "
                             "resolvable in-tree; dynamic getattr-style opens"),
            "no_rewrites": "no pointer, reader or face is edited here",
            "self_excluded": list(OWN_FILES),
        },
    }
    say("read_sites=%d write_sites=%d bare_pointers=%d named_pointers=%d"
        % (len(reads), len(writes), len(bare), len(named)))
    for klass in CLASSES:
        say("  %-52s %d" % (klass, by_class[klass]))
    say("verdict: %s" % summary["verdict"])
    if unsupplied:
        say("unsupplied fan-out: %s (max %d families)"
            % (fanout, summary["max_families_a_single_unsupplied_reader_could_land_on"]))
    return face


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


# --------------------------------------------------------------------------- verify

def verify():
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    summary = face.get("summary") or {}
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    by_class = summary.get("by_class") or {}
    if set(by_class) - set(CLASSES):
        problems.append("classes outside the frozen set: %s" % sorted(set(by_class) - set(CLASSES)))
    if sum(by_class.values()) != (summary.get("read_sites_total") or 0):
        problems.append("classes sum to %d but the read sites total is %s"
                        % (sum(by_class.values()), summary.get("read_sites_total")))
    if decide(summary) != summary.get("verdict"):
        problems.append("verdict does not re-derive from the summary")

    bare, named, other = pointer_files()
    if len(bare) != summary.get("pointer_files_named_latest_json"):
        problems.append("bare pointer count moved: %d vs %s"
                        % (len(bare), summary.get("pointer_files_named_latest_json")))
    if len(named) != summary.get("pointer_files_named_<family>_latest_json"):
        problems.append("family-named pointer count moved: %d vs %s"
                        % (len(named), summary.get("pointer_files_named_<family>_latest_json")))

    # re-derive every published read site from the tree as it stands
    live_reads, live_writes = {}, {}
    for rel in _walk():
        for site in scan_file(rel):
            (live_reads if site["kind"] == "read" else live_writes)[site["site"]] = site
    for row in face.get("read_sites") or []:
        live = live_reads.get(row["site"])
        if live is None:
            problems.append("%s: the site is gone" % row["site"])
            continue
        if live["expr"] != row["expr"]:
            problems.append("%s: the expression moved" % row["site"])
            continue
        again = classify_sites([dict(live)] + [])[0]
        if again["class"] != row["class"]:
            problems.append("%s: class %r re-derives %r"
                            % (row["site"], row["class"], again["class"]))
    for row in face.get("write_sites") or []:
        if row["site"] not in live_writes:
            problems.append("%s: the write site is gone" % row["site"])
    for row in face.get("families") or []:
        keys = top_keys(row["path"])
        if keys != row["keys"]:
            problems.append("%s: top-level keys moved" % row["path"])

    say("verify problems=%s" % json.dumps(problems[:10], ensure_ascii=False))
    return problems


# --------------------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1. the directory test: a bare basename claims no family
    leg("dir literal: a bare basename names no directory", _dir_literal("latest.json") is None)
    leg("dir literal: a slash names one", _dir_literal("results/x/latest.json") == "results/x")
    leg("dir literal: backslashes normalise", _dir_literal("results\\x\\latest.json") == "results/x")

    # 2. static constant resolution through a join
    src = ('import os\nD = os.path.join("results", "state_tilt")\nF = os.path.join(D, "x.json")\n')
    tree = ast.parse(src)
    consts = module_constants(tree)
    leg("constants: a join of literals resolves to its directory",
        _static_dir_of_expr_text(consts["F"], consts) == "results/state_tilt")
    leg("constants: a bare filename resolves to nothing",
        _static_dir_of_expr_text('"unresolved_latest.json"', consts) is None)

    # 3. site extraction: a write is not a read, and json.load(open(...)) is one site
    tree = ast.parse(
        'import json, os\n'
        'def f(outdir):\n'
        '    with open(os.path.join(outdir, "latest.json"), "w") as fh:\n'
        '        fh.write("x")\n'
        'def g(p):\n'
        '    return json.load(open(os.path.join(p, "latest.json"), encoding="utf-8"))\n')
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _open_kind(node):
            path = _path_node(node)
            if path is not None:
                found.setdefault((node.lineno, _open_kind(node)),
                                 ast.unparse(_haircut(path)))
    leg("sites: the write at line 3 is a write, not a read",
        (3, "write") in found and (3, "read") not in found)
    leg("sites: json.load(open(p)) collapses to one read expression",
        (6, "read") in found and found[(6, "read")].startswith("os.path.join"))

    # 4. classification of the four families of supply
    tmpl = ast.parse(
        'def by_const():\n'
        '    return open(os.path.join(DIR, "latest.json"), encoding="utf-8")\n'
        'def by_param(d):\n'
        '    return open(os.path.join(d, "latest.json"), encoding="utf-8")\n'
        'def free():\n'
        '    return open(os.path.join(BASE_FROM_SOMEWHERE, "latest.json"), encoding="utf-8")\n')
    fns = {n.name: n for n in tmpl.body if isinstance(n, ast.FunctionDef)}
    dirs = {"DIR": '"results/state_tilt"'}

    def first_path(fn):
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and _open_kind(node) == "read":
                return _haircut(_path_node(node))
        raise AssertionError("no site")

    leg("class: a module constant names the family",
        classify(first_path(fns["by_const"]), "scripts/x.py", fns["by_const"], dirs)[0] == CL_STATIC)
    leg("class: a parameter is the signature's business",
        classify(first_path(fns["by_param"]), "scripts/x.py", fns["by_param"], {})[0]
        == CL_SIGNATURE)
    leg("class: a free base supplies nothing",
        classify(first_path(fns["free"]), "scripts/x.py", fns["free"], {})[0] == CL_UNSUPPLIED)

    # 5. read-after-write in one function
    tree = ast.parse(
        'import json, os\n'
        'def f(outdir):\n'
        '    p = os.path.join(outdir, "latest.json")\n'
        '    json.dump({}, open(p, "w"))\n'
        '    return json.load(open(p))\n')
    fn = tree.body[1]
    site = None
    carried = None
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and _open_kind(node) == "read":
            got = _carried_path(node, fn)
            if got is not None:
                site, carried = got
    leg("class: reading the name this function just wrote is its own class",
        site is not None and classify(site, "scripts/x.py", fn, {}, carried=carried)[0]
        == CL_WRITTEN)

    # 6. parameter default resolution is published, not assumed
    tree = ast.parse(
        'def f(d="results/x"):\n'
        '    return open(os.path.join(d, "latest.json"), encoding="utf-8")\n')
    fn = tree.body[0]
    path_node = None
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and _open_kind(node) == "read":
            path_node = _haircut(_path_node(node))
    klass, ev = classify(path_node, "scripts/x.py", fn, {})
    leg("class: a signature default is published as a directory",
        klass == CL_SIGNATURE and ev.get("default_dir") == "results/x")

    # 7. a one-argument wrapper and an if-expression both pass the path through
    wrapped = ast.parse('read(os.path.join(ROOT, "results", "vol_gate", "latest.json"))',
                        mode="eval").body
    leg("parts: a one-arg wrapper passes the path through",
        _family_suffix(wrapped) == "results/vol_gate")
    branchy = ast.parse('a if a else os.path.join("results", "state_tilt", "x_latest.json")',
                        mode="eval").body
    leg("parts: an if-expression is read through the branch that carries the pointer",
        _family_suffix(branchy) == "results/state_tilt")
    leg("parts: a bare pointer with no other literal names no family",
        _family_suffix(ast.parse('os.path.join(base, "latest.json")', mode="eval").body) is None)

    # 8. verdict recomputation
    leg("verdict: all named",
        decide({"read_sites_total": 2, "sites_that_name_their_family_at_the_site": 1,
                "sites_handed_their_family_by_the_signature": 1,
                "sites_that_read_the_pointer_they_just_wrote": 0,
                "sites_whose_family_is_not_supplied_anywhere": 0}) == V_ALL_NAMED)
    leg("verdict: none named",
        decide({"read_sites_total": 2, "sites_that_name_their_family_at_the_site": 0,
                "sites_handed_their_family_by_the_signature": 0,
                "sites_that_read_the_pointer_they_just_wrote": 0,
                "sites_whose_family_is_not_supplied_anywhere": 2}) == V_ALL_UNSUPPLIED)
    leg("verdict: mixed",
        decide({"read_sites_total": 2, "sites_that_name_their_family_at_the_site": 1,
                "sites_handed_their_family_by_the_signature": 0,
                "sites_that_read_the_pointer_they_just_wrote": 0,
                "sites_whose_family_is_not_supplied_anywhere": 1}) == V_MIXED)
    leg("verdict: no reads",
        decide({"read_sites_total": 0}) == V_NO_READS)
    leg("verdict: four verdicts, no duplicates",
        len(VOCAB) == 4 and len(CLASSES) == 4)

    # 8. schema cost is arithmetic over the published rows, not a slogan
    rows = [{"family": "a", "signature": "x|y", "keys": ["x", "y"]},
            {"family": "b", "signature": "x|y", "keys": ["x", "y"]},
            {"family": "c", "signature": "x|z", "keys": ["x", "z"]}]
    cost = schema_cost(rows)
    leg("schema: pairs are counted, not sampled",
        cost["pairs_compared"] == 3 and cost["pairs_with_the_same_top_level_keys"] == 1)
    leg("schema: the largest group is the largest group",
        cost["families_sharing_the_largest_signature"] == 2
        and cost["distinct_top_level_signatures"] == 2)

    # 9. ownership: the study does not scan itself
    leg("self: own files are excluded from the corpus",
        all(rel not in _walk() for rel in OWN_FILES))

    bad = [l for l in legs if not l[1]]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if detail else ""))
    say("%d/%d legs passed" % (len(legs) - len(bad), len(legs)))
    return 1 if bad else 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        face = build(True)
        _write(face)
        return 0
    if cmd == "verify":
        return 1 if verify() else 0
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))