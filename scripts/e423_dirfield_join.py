"""E423 - which consumer joins a directory-named field that already holds a file path.

E422 found that 11 of E404's 18 rows publish a FILE path in a field named
`resolved_directory`, so a reader that joins that field with the row's own name composes
`<face>.json/<name>`. A field's name is a promise about its value; this study prices how far
the promise is consumed rather than assumed.

Three questions, all mechanical:

  1. what does the published corpus actually put in a directory-named field -- a directory or
     a file path (and how many rows would double if a join existed);
  2. which read sites in the python corpus read such a field, and what do they do with it
     (read it as a whole path, republish it, join it with a prefix, or join it with a NAME);
  3. of the joins, how many could exist against a value that is a file path.

The distinction that makes the count honest is (2): a field named `dir` being joined with
`face["name"]` is the hazard shape; a field being opened as-is is not a hazard at all, and
folding both into "N joins" would price the vocabulary rather than the defect.

Usage:
    python scripts/e423_dirfield_join.py run|verify|selftest
"""
from __future__ import annotations

import ast
import bisect
import collections
import io
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
OUTDIR = ST
E422 = os.path.join(ST, "basenamecensus_latest.json")

SELF_NAMES = ("e423_dirfield_join", "run_e423")

# The vocabulary is a name promise, not a substring test: 'direction' and 'dir_bindings' are
# not directories, and an endswith('dir') rule would swallow both.
DIR_KEYS = {
    "dir", "directory", "outdir", "out_dir", "parent_dir", "parent_directory",
    "dir_path", "directory_path", "directory_expression", "resolved_dir",
    "resolved_directory", "face_directory", "faces_dir", "output_dir",
}
NAME_KEYS = {
    "name", "file", "filename", "basename", "fragment", "face", "path", "stem",
    "file_name", "key",
}
FILE_EXTS = (".json", ".csv", ".md", ".parquet", ".txt", ".html", ".py", ".png", ".log")

# Read-site classes (frozen vocabulary; verify refuses anything else).
C_WHOLE = "reads_the_field_as_a_whole_path"
C_REPUBLISH = "republishes_the_field_without_joining_it"
C_PREFIX = "joins_the_field_with_a_prefix_or_root"
C_NAME = "joins_the_field_with_a_name"
C_WRITE = "writes_the_field"
CLASS_VOCAB = {C_WHOLE, C_REPUBLISH, C_PREFIX, C_NAME, C_WRITE}

# Value classes for a published field.
V_DIRECTORY = "value_is_a_directory"
V_FILE = "value_is_a_file_path"
V_OTHER = "value_is_neither"
VALUE_VOCAB = {V_DIRECTORY, V_FILE, V_OTHER}

VERDICT_VOCAB = {
    "a_consumer_joins_a_directory_named_field_with_a_name_and_published_rows_could_double",
    "a_consumer_joins_a_directory_named_field_with_a_name_but_no_published_row_could_double",
    "directory_named_fields_are_published_with_file_paths_and_no_consumer_joins_them",
    "no_directory_named_field_holds_a_file_path",
}

SKIP_DIRS = {
    ".git", "results", "data", "node_modules", "__pycache__", "media", "Money02", "legacy",
    ".codely-cli", "_quarantine",
}
CORPUS_ROOTS = ("scripts", "Tools", "monitor", "live", "firm", "engine", "content", ".")
FACE_MAX_BYTES = 3_000_000

POPULATION_KEYS = ("corpus_sources", "published_faces_scanned")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for root in CORPUS_ROOTS:
        base = os.path.join(ROOT, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("_q")]
            if root == "." and os.path.abspath(dirpath) != os.path.abspath(ROOT):
                # Root-level modules are in the census (smoke_test.py is a reader); a sibling
                # PROJECT tree under the repo root (Money0923/) is not part of this corpus.
                dirnames[:] = []
                continue
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                if any(fn.startswith(n) for n in SELF_NAMES):
                    continue
                abs_p = os.path.abspath(os.path.join(dirpath, fn))
                if abs_p in seen:
                    continue
                seen.add(abs_p)
                out.append(_rel(abs_p))
    return sorted(out)


# ---------------------------------------------------------------------------------------------
# (1) what the published corpus puts in a directory-named field
# ---------------------------------------------------------------------------------------------

def value_class(value: str) -> str:
    """Grade a published field value by its shape, never by the key that carries it."""
    v = (value or "").strip()
    if not v:
        return V_OTHER
    if v.endswith(("/", "\\")):
        return V_DIRECTORY
    low = v.lower()
    if low.endswith(FILE_EXTS):
        return V_FILE
    if os.sep in v or "/" in v:
        # A path with no extension is a directory only if it has no dot in its last segment.
        last = v.replace("\\", "/").rstrip("/").split("/")[-1]
        return V_DIRECTORY if "." not in last else V_FILE
    return V_OTHER


def _basename(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").split("/")[-1]


def scan_faces(root: str | None = None) -> dict:
    """Every dict in the published JSON corpus that carries a directory-named key.

    The row's own name fields are kept beside the value so the doubling counterfactual can be
    priced at the row rather than at the key: a join exists only if the row offers a name.
    """
    root = root or ROOT
    faces_scanned = 0
    fields: list[dict] = []
    rows_with_a_file_valued_field: list[dict] = []
    results = os.path.join(root, "results")
    for dirpath, dirnames, filenames in os.walk(results):
        dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
        for fn in sorted(filenames):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(path) > FACE_MAX_BYTES:
                    continue
                payload = json.load(io.open(path, encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            faces_scanned += 1
            stack = [payload]
            while stack:
                obj = stack.pop()
                if isinstance(obj, dict):
                    dir_keys = [k for k in obj if isinstance(k, str) and k in DIR_KEYS
                                and isinstance(obj[k], str) and obj[k]]
                    names = {k: obj[k] for k in obj if isinstance(k, str) and k in NAME_KEYS
                             and isinstance(obj[k], str) and obj[k]}
                    for k in dir_keys:
                        v = obj[k]
                        cls = value_class(v)
                        row = {
                            "face": os.path.relpath(path, root).replace("\\", "/"),
                            "key": k,
                            "value": v if len(v) <= 160 else v[:157] + "...",
                            "value_class": cls,
                            "name_fields_in_the_same_row": sorted(names),
                        }
                        if cls == V_FILE:
                            base = _basename(v)
                            # A join can exist only if the row offers a name to join onto the
                            # field. Without one the value is a file path with no consumer, and
                            # publishing it as "could double" would price the key, not the row.
                            row["names_equal_to_the_value_basename"] = sorted(
                                nk for nk, nv in names.items() if _basename(nv) == base)
                            row["could_compose_a_doubled_name"] = bool(names)
                        fields.append(row)
                    stack.extend(v2 for v2 in obj.values()
                                 if isinstance(v2, (dict, list)))
                    if dir_keys and any(value_class(obj[k]) == V_FILE for k in dir_keys):
                        rows_with_a_file_valued_field.append({
                            "face": os.path.relpath(path, root).replace("\\", "/"),
                            "keys": sorted(dir_keys),
                        })
                elif isinstance(obj, list):
                    stack.extend(obj[:200])
    by_key: dict[str, dict] = {}
    for f in fields:
        slot = by_key.setdefault(f["key"], {"fields": 0, "file_paths": 0})
        slot["fields"] += 1
        if f["value_class"] == V_FILE:
            slot["file_paths"] += 1
    return {
        "published_faces_scanned": faces_scanned,
        "fields": fields,
        "by_key": by_key,
        "rows_with_a_file_valued_field": rows_with_a_file_valued_field,
    }


# ---------------------------------------------------------------------------------------------
# (2) what readers do with the field
# ---------------------------------------------------------------------------------------------

JOIN_FUNCS = {"join", "joinpath", "path_join"}


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _key_read(node: ast.AST) -> str | None:
    """The literal key this node reads from a mapping, if it reads one."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr in ("get", "pop", "setdefault") and node.args:
        a = node.args[0]
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            return a.value
    elif isinstance(node, ast.Subscript):
        s = node.slice
        if isinstance(s, ast.Constant) and isinstance(s.value, str):
            return s.value
        if type(s).__name__ == "Index":  # py<3.9
            inner = getattr(s, "value", None)
            if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                return inner.value
    return None


def _parents(tree: ast.AST) -> dict[int, list[ast.AST]]:
    table: dict[int, list[ast.AST]] = collections.defaultdict(list)
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            table[id(child)].append(parent)
    return table


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        fn = _dotted(node.func)
        return fn + "()"
    if isinstance(node, ast.Subscript):
        return _dotted(node.value) + "[]"
    return ""


def _is_filename_constant(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        v = node.value.strip()
        return bool(v) and "/" not in v and "\\" not in v and "." in v
    return False


FILE_HINT_KEYS = set()


def _sibling_names_in_join(call_or_binop: ast.AST, self_node: ast.AST) -> list[str]:
    """The name-vocab reads joined alongside `self_node` inside one join expression."""
    out: list[str] = []
    for sub in ast.walk(call_or_binop):
        if sub is self_node:
            continue
        if id(sub) == id(self_node):
            continue
        key = _key_read(sub)
        if key and (key in NAME_KEYS or key in DIR_KEYS):
            out.append(key)
        elif _is_filename_constant(sub):
            out.append("<literal-filename>")
    return out


RECEIVER_METHODS = {"rstrip", "lstrip", "strip", "lower", "upper", "replace", "format",
                    "resolve", "expanduser", "absolute", "as_posix", "joinpath", "__str__",
                    "removesuffix", "removelast"}


def _contains(outer: ast.AST, node: ast.AST, parents: dict[int, list[ast.AST]] | None = None) -> bool:
    """Is `node` inside `outer`? Walk up from the node when the parent table is available:
    a containment test that re-walks the outer subtree is quadratic on a 230k-node file."""
    if parents is None:
        return any(sub is node for sub in ast.walk(outer))
    cur: ast.AST = node
    while True:
        if cur is outer:
            return True
        ups = parents.get(id(cur)) or []
        if not ups:
            return False
        cur = ups[0]


def _join_context(node: ast.AST, parents: dict[int, list[ast.AST]]) -> ast.AST | None:
    """The join expression this read participates in, if any (walking through the receiver chain)."""
    cur = node
    for _ in range(6):
        ups = parents.get(id(cur)) or []
        if not ups:
            return None
        up = ups[0]
        if isinstance(up, ast.Call) and _call_name(up) in JOIN_FUNCS:
            return up
        if isinstance(up, ast.BinOp) and isinstance(up.op, (ast.Add, ast.Div)):
            # `a + "/" + b` nests two BinOps; the claim is about the WHOLE join, so climb to the
            # outermost one instead of stopping at the inner literal-only join.
            nxt = (parents.get(id(up)) or [None])[0]
            if isinstance(nxt, ast.BinOp) and isinstance(nxt.op, (ast.Add, ast.Div)):
                cur = up
                continue
            if isinstance(nxt, ast.Call) and _call_name(nxt) in JOIN_FUNCS:
                cur = up
                continue
            return up
        if isinstance(up, ast.JoinedStr):
            return up
        if isinstance(up, ast.Call):
            # `face["dir"].rstrip("/") + "/" + face["name"]`: the read is the RECEIVER of a
            # string/path method, so the join sits further up. A read handed in as an ARGUMENT
            # is consumed there and is not part of the join (it would be a different claim).
            if isinstance(up.func, ast.Attribute) and _contains(up.func, cur, parents):
                if up.func.attr in RECEIVER_METHODS:
                    cur = up
                    continue
            return None
        if isinstance(up, ast.Assign):
            return ("bound", up)
        if isinstance(up, (ast.Expr, ast.Return, ast.If, ast.Compare, ast.Dict,
                           ast.List, ast.Tuple, ast.BoolOp, ast.AugAssign)):
            return None
        cur = up
    return None


def _assigned_value_container(assign: ast.Assign, target_value: ast.AST) -> str | None:
    return _dotted(assign.targets[0]) if assign.targets else None


def read_sites(path: str) -> list[dict]:
    try:
        src = io.open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    parents = _parents(tree)
    funcs: list[tuple[ast.AST, int, int]] = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append((n, n.lineno, getattr(n, "end_lineno", 10 ** 9)))
    # Interval index for `enclosing`: the innermost function is the smallest span containing the
    # line, so only candidates whose start is <= the line are walked, and each line is resolved
    # once (`_enclosing_cache`). The previous form scanned all 566 defs for each of 7430 reads.
    funcs.sort(key=lambda f: f[1])
    _starts = [f[1] for f in funcs]
    _enclosing_cache: dict[int, str] = {}

    def enclosing(lineno: int) -> str:
        hit = _enclosing_cache.get(lineno)
        if hit is not None:
            return hit
        best = (10 ** 9, "<module>")
        i = bisect.bisect_right(_starts, lineno) - 1
        while i >= 0:
            node, start, end = funcs[i]
            if end >= lineno:
                span = end - start
                if span < best[0]:
                    best = (span, node.name)
            i -= 1
        _enclosing_cache[lineno] = best[1]
        return best[1]

    # Every ast.Name by identifier, built once. The one-hop rebinding question used to re-walk
    # the whole tree per bound read, which is what made the leg unusable on this corpus.
    names_by_id: dict[str, list[ast.Name]] = collections.defaultdict(list)
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            names_by_id[n.id].append(n)

    sites: list[dict] = []
    for node in ast.walk(tree):
        key = _key_read(node)
        if key is None:
            continue
        line = getattr(node, "lineno", 0)
        func = enclosing(line)
        row = {"file": path, "line": line, "function": func, "key": key}

        # A read that sits in a Dict literal under a directory-named key is a REPUBLICATION,
        # not a use: the value is copied into a face and nobody has resolved anything yet.
        ctx = _join_context(node, parents)
        if isinstance(ctx, tuple) and ctx[0] == "bound":
            assign = ctx[1]
            target = _dotted(assign.targets[0]) if assign.targets else ""
            # One hop: is the bound name later joined with a name?
            hops = []
            for sub in names_by_id.get(target, []):
                ctx2 = _join_context(sub, parents)
                if ctx2 is None or isinstance(ctx2, tuple):
                    continue
                hops.append(_sibling_names_in_join(ctx2, sub))
            if not hops and key in DIR_KEYS and False:
                pass
            if hops:
                joined = [h for h in hops if any(x in NAME_KEYS for x in h)]
                others = [x for h in hops for x in h]
                row["class"] = C_NAME if joined else C_PREFIX
                row["joined_siblings"] = sorted(set(others))
                row["binding"] = target
                sites.append(row)
                continue
            row["class"] = C_WHOLE
            row["binding"] = target
            sites.append(row)
            continue
        if ctx is not None and not isinstance(ctx, tuple):
            sibs = _sibling_names_in_join(ctx, node)
            row["joined_siblings"] = sorted(set(sibs))
            if any(s in NAME_KEYS for s in sibs):
                row["class"] = C_NAME
            else:
                row["class"] = C_PREFIX
            sites.append(row)
            continue
        # Dict-literal context: the read is copied into a payload.
        ups = parents.get(id(node)) or []
        if ups and isinstance(ups[0], ast.Dict):
            keys = [k.value for k in ups[0].keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            if any(k in DIR_KEYS for k in keys):
                row["class"] = C_REPUBLISH
                sites.append(row)
                continue
        row["class"] = C_WHOLE
        sites.append(row)
    sites.sort(key=lambda r: (r["file"], r["line"]))
    return sites


# ---------------------------------------------------------------------------------------------
# build / verify / selftest
# ---------------------------------------------------------------------------------------------

def build(cutoff: str | None = None) -> dict:
    faces = scan_faces()
    cut = cutoff or date.today().isoformat()
    try:
        cut = _load(E422)["evidence_cutoff"]
    except (OSError, ValueError, KeyError):
        pass
    sites: list[dict] = []
    index = {}
    for p in corpus():
        src = io.open(os.path.join(ROOT, p), encoding="utf-8", errors="replace").read()
        index[p] = src
        sites.extend(read_sites(os.path.join(ROOT, p)))
    # Only read sites of directory-named keys are in the population; a name-key read is context.
    sites = [s for s in sites if s["key"] in DIR_KEYS]
    by_class: dict[str, int] = {}
    for s in sites:
        by_class[s["class"]] = by_class.get(s["class"], 0) + 1
    file_rows = [f for f in faces["fields"] if f["value_class"] == V_FILE]
    name_joins = [s for s in sites if s["class"] == C_NAME]
    # A join can double only against a face row whose field value is a file path, and only if
    # that row also carries a name. Counted per published row, not per consumer.
    doubling_rows = [f for f in file_rows if f.get("could_compose_a_doubled_name")]
    join_keys = sorted({s["key"] for s in name_joins})
    doubling_keys = sorted({f["key"] for f in doubling_rows})
    join_can_double = sorted(set(join_keys) & set(doubling_keys))
    summary = {
        "published_faces_scanned": faces["published_faces_scanned"],
        "directory_named_fields": len(faces["fields"]),
        "directory_named_fields_holding_a_file_path": len(file_rows),
        "faces_carrying_a_file_valued_directory_field": len(
            {r["face"] for r in faces["rows_with_a_file_valued_field"]}),
        "corpus_sources": len(index),
        "read_sites": len(sites),
        "by_class": by_class,
        "join_sites": len(name_joins),
        "join_keys": join_keys,
        "keys_that_double": doubling_keys,
        "doubling_rows_by_key": dict(collections.Counter(f["key"] for f in doubling_rows)),
        "published_rows_where_a_join_could_double": len(doubling_rows),
        "joins_that_can_double": join_can_double,
    }
    if name_joins and join_can_double:
        verdict = "a_consumer_joins_a_directory_named_field_with_a_name_and_published_rows_could_double"
    elif name_joins:
        verdict = "a_consumer_joins_a_directory_named_field_with_a_name_but_no_published_row_could_double"
    elif file_rows:
        verdict = "directory_named_fields_are_published_with_file_paths_and_no_consumer_joins_them"
    else:
        verdict = "no_directory_named_field_holds_a_file_path"
    return {
        "study": "E423_which_consumer_joins_a_directory_named_field_that_holds_a_file_path",
        "card": "E423-WHICH-CONSUMER-JOINS-A-DIRECTORY-FIELD-THAT-HOLDS-A-FILE-PATH",
        "title": "price whether any consumer joins a directory-named field with a row name, and "
                 "how many published rows would compose a doubled name if one did",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict,
        "summary": summary,
        "population_keys": list(POPULATION_KEYS),
        "read_sites": sites,
        "published_fields_holding_a_file_path": file_rows,
        "fields_by_key": faces["by_key"],
        "rows_with_a_file_valued_field": faces["rows_with_a_file_valued_field"],
        "method_limits": [
            "a read is classified by the expression it sits in (one hop through a bound name); "
            "a value stored on an object attribute and joined two functions later is out of "
            "reach and would be graded reads_the_field_as_a_whole_path",
            "the doubling counterfactual is priced at the row (a name field beside the value), "
            "not proven at a call site: no consumer may ever be handed such a row",
            "faces larger than 3 MB are not scanned, so a big census that carries such a field "
            "is outside this population",
        ],
    }


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, "dirfield_latest.json"))
    problems: list[str] = []
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append(f"verdict outside the frozen vocabulary: {face.get('verdict')!r}")
    tally: dict[str, int] = {}
    for s in face["read_sites"]:
        if s["class"] not in CLASS_VOCAB:
            problems.append(f"{s['file']}:{s['line']} class outside the vocabulary {s['class']!r}")
        tally[s["class"]] = tally.get(s["class"], 0) + 1
    if tally != face["summary"]["by_class"]:
        problems.append(f"by_class does not re-derive: published={face['summary']['by_class']} derived={tally}")
    joins = [s for s in face["read_sites"] if s["class"] == C_NAME]
    if len(joins) != face["summary"]["join_sites"]:
        problems.append("join_sites does not re-add")
    for s in joins:
        if not any(x in NAME_KEYS for x in s.get("joined_siblings") or []):
            problems.append(f"{s['file']}:{s['line']} graded a name-join without a name sibling")
    for f in face["published_fields_holding_a_file_path"]:
        if f["value_class"] != V_FILE:
            problems.append(f"{f['face']}:{f['key']} published as a file path but graded {f['value_class']}")
        # Re-derive the shape from the stored value with the SAME grader the build used. Testing
        # it against a private extension list made verify red on .jsonl/.tmp spellings that the
        # build had correctly graded as file paths -- a second copy of the gate, disagreeing.
        if value_class(str(f["value"])) != V_FILE:
            problems.append(f"{f['face']}:{f['key']} value is not a file path anymore: {f['value']!r}")
    # The counterfactual must re-derive from the published row, not from a stored flag.
    can = sorted({f["key"] for f in face["published_fields_holding_a_file_path"]
                  if f.get("name_fields_in_the_same_row")})
    if can != face["summary"]["keys_that_double"]:
        problems.append(f"keys_that_double does not re-derive: {face['summary']['keys_that_double']} vs {can}")
    could = [f for f in face["published_fields_holding_a_file_path"]
             if f.get("name_fields_in_the_same_row")]
    if len(could) != face["summary"].get("published_rows_where_a_join_could_double"):
        problems.append("published_rows_where_a_join_could_double does not re-derive")
    by_key = collections.Counter(f["key"] for f in could)
    if dict(by_key) != (face["summary"].get("doubling_rows_by_key") or {}):
        problems.append("doubling_rows_by_key does not re-derive")
    for f in face["published_fields_holding_a_file_path"]:
        if bool(f.get("could_compose_a_doubled_name")) != bool(f.get("name_fields_in_the_same_row")):
            problems.append(f"{f['face']}:{f['key']} publishes a doubling flag that disagrees with its row")
            break
    expected_joinable = sorted(set(face["summary"]["join_keys"]) & set(can))
    if expected_joinable != face["summary"]["joins_that_can_double"]:
        problems.append("joins_that_can_double does not re-derive")
    for f in face["published_fields_holding_a_file_path"]:
        path = os.path.join(ROOT, f["face"])
        if not os.path.exists(path):
            problems.append(f"face {f['face']} named in the population no longer exists")
            break
    # The read sites are a measurement of the corpus, so verify re-derives them from the live
    # tree: a consumer that started joining such a field with a row name must refuse the chain
    # rather than leave a stale reading in place.
    live: dict[str, int] = {}
    for p in corpus():
        for s in read_sites(os.path.join(ROOT, p)):
            if s["key"] in DIR_KEYS:
                live[s["class"]] = live.get(s["class"], 0) + 1
    if live != face["summary"]["by_class"]:
        problems.append(f"the live read-site classes do not re-derive: published="
                        f"{face['summary']['by_class']} live={live}")
    if tally != face["summary"]["by_class"]:
        problems.append("by_class drifted during verify")
    return problems


def _fixture_face(root: str) -> str:
    st = os.path.join(root, "results", "state_tilt")
    os.makedirs(st, exist_ok=True)
    face = {
        "study": "fixture",
        "rows": [
            {"fragment": "a.json", "resolved_directory": "C:/x/a.json"},
            {"fragment": "b.json", "resolved_directory": "C:/x/dir"},
            {"name": "c.json", "dir": "results/x"},
        ],
    }
    path = os.path.join(st, "FIXTURE.json")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh)
    return path


def selftest() -> int:
    import shutil
    import tempfile
    bad = 0
    total = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal bad, total
        total += 1
        if cond:
            print(f"[PASS] {name}")
        else:
            bad += 1
            print(f"[FAIL] {name} {detail}")

    check("a value ending in .json is a file path", value_class("C:/x/a.json") == V_FILE)
    check("a value ending in a separator is a directory", value_class("C:/x/") == V_DIRECTORY)
    check("a bare name is neither", value_class("state_tilt") == V_OTHER)
    check("a dotted last segment is a file path", value_class("results/x/latest.parquet") == V_FILE)
    check("a keyword that merely contains 'dir' is not in the vocabulary",
          "direction" not in DIR_KEYS and "dir" in DIR_KEYS)

    tmp = tempfile.mkdtemp(prefix="e423_")
    try:
        _fixture_face(tmp)
        got = scan_faces(tmp)
        file_rows = [f for f in got["fields"] if f["value_class"] == V_FILE]
        check("a published row holding a file path in a directory-named field is priced",
              len(file_rows) == 1, [f["value"] for f in file_rows])
        check("the doubling counterfactual names the row's own name field",
              file_rows and file_rows[0]["names_equal_to_the_value_basename"] == ["fragment"],
              file_rows[0] if file_rows else None)
        check("a row whose directory field is a directory is not priced as doubling",
              not any(f["value_class"] == V_FILE and f["value"] == "results/x"
                      for f in got["fields"]))

        src = os.path.join(tmp, "scripts")
        os.makedirs(src, exist_ok=True)

        def sites_for(name: str, body: str) -> list[dict]:
            p = os.path.join(src, name)
            io.open(p, "w", encoding="utf-8", newline="\n").write(body)
            return read_sites(p)

        joined = sites_for("joined.py",
                           "def f(rows):\n"
                           "    out = []\n"
                           "    for face in rows:\n"
                           "        p = face.get('path') or (face['dir'].rstrip('/') + '/' + "
                           "face['name'])\n"
                           "        out.append(p)\n"
                           "    return out\n")
        check("the hazard shape -- dir joined with the row's name -- is graded a name join",
              [s["class"] for s in joined if s["key"] in DIR_KEYS] == [C_NAME], joined)

        prefixed = sites_for("prefixed.py",
                             "import os\n"
                             "ROOT = '.'\n"
                             "def f(cfg):\n"
                             "    return os.path.join(ROOT, cfg['out_dir'])\n")
        check("a directory field joined only with a root prefix is a prefix join",
              [s["class"] for s in prefixed if s["key"] in DIR_KEYS] == [C_PREFIX], prefixed)

        whole = sites_for("whole.py",
                          "def f(row):\n"
                          "    return shown(row.get('resolved_directory'))\n")
        check("a directory field handed whole to a consumer is not a join",
              [s["class"] for s in whole if s["key"] in DIR_KEYS] == [C_WHOLE], whole)

        repub = sites_for("repub.py",
                          "def f(item):\n"
                          "    return {'directory_expression': item['directory_expression']}\n")
        check("copying the field into a face is a republication, not a use",
              [s["class"] for s in repub if s["key"] in DIR_KEYS] == [C_REPUBLISH], repub)

        bound = sites_for("bound.py",
                          "import os\n"
                          "def f(row):\n"
                          "    d = row.get('resolved_dir')\n"
                          "    return os.path.join(d, row['file'])\n")
        check("a read bound to a name and joined one hop later is still a name join",
              [s["class"] for s in bound if s["key"] in DIR_KEYS] == [C_NAME], bound)

        arg = sites_for("arg.py",
                        "def f(rows):\n"
                        "    return [check(row['dir']) for row in rows]\n")
        check("a directory field passed as an argument is not joined inside that call",
              [s["class"] for s in arg if s["key"] in DIR_KEYS] == [C_WHOLE], arg)

        check("the corpus scanner does not count itself",
              not any("e423_dirfield_join" in p for p in corpus()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # verify must refuse a face whose class tally does not re-derive from its own rows.
    doctored = {
        "verdict": sorted(VERDICT_VOCAB)[0],
        "read_sites": [{"file": "scripts/x.py", "line": 1, "key": "dir", "class": C_PREFIX,
                        "joined_siblings": ["ROOT"]}],
        "summary": {"by_class": {C_NAME: 1}, "join_sites": 0, "join_keys": [],
                    "keys_that_double": [], "joins_that_can_double": []},
        "published_fields_holding_a_file_path": [],
    }
    problems = verify(doctored)
    check("verify refuses a by_class that does not re-derive", any("by_class" in p for p in problems),
          problems)

    doctored2 = {
        "verdict": sorted(VERDICT_VOCAB)[0],
        "read_sites": [{"file": "scripts/x.py", "line": 1, "key": "dir", "class": C_NAME,
                        "joined_siblings": ["ROOT"]}],
        "summary": {"by_class": {C_NAME: 1}, "join_sites": 1, "join_keys": ["dir"],
                    "keys_that_double": [], "joins_that_can_double": []},
        "published_fields_holding_a_file_path": [],
    }
    problems = verify(doctored2)
    check("verify refuses a name join with no name sibling", any("name sibling" in p for p in problems),
          problems)

    print(f"selftest {'PASS' if not bad else 'FAIL'} {total - bad}/{total}")
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print(f"verify problems={len(problems)}")
        return 0 if not problems else 1
    face = build()
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"DIRFIELD-{face['evidence_cutoff']}.json")
    for target in (out, os.path.join(OUTDIR, "dirfield_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print(f"faces={s['published_faces_scanned']} dir_fields={s['directory_named_fields']} "
          f"file_valued={s['directory_named_fields_holding_a_file_path']} read_sites={s['read_sites']}")
    print(f"by_class={s['by_class']}")
    print(f"join_keys={s['join_keys']} keys_that_double={s['keys_that_double']}")
    print(f"verdict={face['verdict']}")
    print(f"face={_rel(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))