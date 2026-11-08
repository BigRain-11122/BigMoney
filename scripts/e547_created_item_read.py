"""E547 -- does the item a store creates get read back, and on which container?

E544 (r1573) published 13 ``(store, later read)`` pairs over containers this
repo's interpreter can bind.  Eight of them are the other way round: the store
*creates* an item the fold never publishes (``out['verdict']``,
``rows['_GB_nan_skipped']``, ``art['trials_N']``, ...).  E544 named the
divergence; it said nothing about consequences.

The question E547 asks is narrower and harder: **a consumer that took the
fold's own container (the one without the created item) -- what happens?**
Three answers are possible and they are very different risks:

  * it raises ``KeyError`` -- an unguarded subscript read assumes the item;
  * it reads a default -- every read goes through ``.get`` / a membership test;
  * it never reaches the item -- no read of that key exists at all.

So every row is turned into a *read census*:

  * local reads of ``<name>[<path>]`` in the store's own module, classed
    ``subscript`` / ``get`` / ``membership`` / ``pop`` / ``setdefault`` and
    flagged with whether they sit after the last store and inside the storing
    function;
  * cross-module reads of the same key literal, split by whether the base is
    the SAME container (impossible across modules for a local, possible through
    a persisted face) or a DIFFERENT container whose name merely collides;
  * the persisted-face channel: if the storing function serialises the
    container to a module constant, that path is resolved and modules naming
    it are looked at for a read of the key.

The last point matters because the naive count is a trap: the key literal
``report_num_entries`` appears in 46 modules, and **every one of them writes it
into its own ``params`` dict going into the engine** -- not one reads it back
off the container E544 named.  A name census would have published 46
"consumers" for a key nobody reads.

    python scripts/e547_created_item_read.py build      # publish the face
    python scripts/e547_created_item_read.py check      # re-derive; problems must be []
    python scripts/e547_created_item_read.py verify     # two builds identical
    python scripts/e547_created_item_read.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import glob
import io
import json
import os
import sys
import textwrap
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
PARENT = os.path.join(STATE_TILT, "ITEMSTOREBETWEEN-2026-11-08.json")
FACE = os.path.join(STATE_TILT, "CREATEDITEMREAD-2026-11-08.json")
LATEST = os.path.join(STATE_TILT, "createditemread_latest.json")

STUDY = "E547"
CARD = ("E547-WHETHER-THE-EIGHT-CREATED-ITEMS-ARE-READ-BY-THE-CODE-THAT-"
        "THE-SAME-STATEMENT-FEEDS")
TITLE = "whether the eight created items are read back by any code, and behind which guard"
EVIDENCE_CUTOFF = "2026-11-08"

# The parent's own word for the rows this study consumes.
P_CREATED = "the_store_creates_an_item_the_fold_never_publishes"

# Read forms.
F_SUBSCRIPT = "subscript"
F_GET = "get"
F_MEMBERSHIP = "membership"
F_POP = "pop"
F_SETDEFAULT = "setdefault"
READ_FORMS = (F_SUBSCRIPT, F_GET, F_MEMBERSHIP, F_POP, F_SETDEFAULT)
GUARDED_FORMS = (F_GET, F_MEMBERSHIP, F_SETDEFAULT)
UNGUARDED_FORMS = (F_SUBSCRIPT, F_POP)

# One outcome per row.
O_KEYERROR = "a_consumer_that_took_the_folds_container_would_raise_key_error"
O_DEFAULT = "the_item_is_only_ever_read_through_a_guard_or_a_default"
O_NEVER = "no_read_of_the_item_exists_anywhere"
OUTCOME_VOCAB = (O_KEYERROR, O_DEFAULT, O_NEVER)

# Verdicts.
V_KEYERROR = ("the_items_these_stores_create_are_read_off_the_same_container_"
              "without_a_guard_so_the_store_is_load_bearing")
V_DEFAULT = "every_read_of_a_created_item_goes_through_a_guard_or_a_default"
V_MIXED = "some_created_items_are_read_unguarded_and_some_are_not"
V_NEVER = "no_code_reads_back_any_of_the_items_these_stores_create"
V_PRODUCER_ONLY = ("the_created_items_are_read_only_inside_the_module_that_creates_them_"
                   "and_never_through_a_persisted_face")

# Corpus roots, same shape the parent used.
CORPUS_GLOBS = ("scripts/*.py", "Tools/*.py", "firm/**/*.py", "live/*.py")


# ------------------------------------------------------------------ helpers
def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _dump_face(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def base_tokens(node):
    """(root name, [key tokens]) for ``name['a']['b']``, or None."""
    keys = []
    cur = node
    while isinstance(cur, ast.Subscript):
        k = _const_str(cur.slice)
        if k is None:
            return None
        keys.append(k)
        cur = cur.value
    if isinstance(cur, ast.Name):
        return cur.id, list(reversed(keys))
    return None


def _walk_tokens(node):
    """Every (name, path) pair a subscript chain expresses, longest first.

    ``a['x']['y']`` is two reads: ``a['x']`` and ``a['x']['y']``.
    """
    out = []
    cur = node
    while isinstance(cur, ast.Subscript):
        tok = base_tokens(cur)
        if tok is None:
            break
        out.append(tok)
        cur = cur.value
    return out


def uses_in_tree(tree):
    """All uses of a keyed container in one module.

    Returns a list of ``{line, name, path, form, after_store_probe}`` records.
    Dict literals are recorded as ``declare`` (they create the item, they do
    not read it) and kept out of the read forms.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            toks = _walk_tokens(node)
            if not toks:
                continue
            form = F_SUBSCRIPT if isinstance(node.ctx, ast.Load) else "store"
            name, path = toks[0]
            out.append({"line": node.lineno, "name": name, "path": path,
                        "form": form, "expr": _span(node)})
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr in ("get", "pop", "setdefault"):
                tok = base_tokens(fn.value) or (
                    (fn.value.id, []) if isinstance(fn.value, ast.Name) else None)
                if tok is None:
                    continue
                key = _const_str(node.args[0]) if node.args else None
                if key is None:
                    continue
                out.append({"line": node.lineno, "name": tok[0],
                            "path": tok[1] + [key], "form": fn.attr,
                            "expr": _span(node)})
        elif isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if not isinstance(op, (ast.In, ast.NotIn)):
                    continue
                key = _const_str(node.left) if i == 0 else _const_str(node.comparators[i - 1])
                right = node.comparators[i] if i == 0 else node.left
                tok = base_tokens(right) or (
                    (right.id, []) if isinstance(right, ast.Name) else None)
                if key is None or tok is None:
                    continue
                out.append({"line": node.lineno, "name": tok[0],
                            "path": tok[1] + [key], "form": F_MEMBERSHIP,
                            "expr": _span(node)})
    return out


def _span(node):
    try:
        seg = ast.unparse(node)
    except Exception:
        seg = ""
    return " ".join(seg.split())[:120]


def dict_literals(tree):
    """``{'k': ...}`` keys: declarations of the item, not reads."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                s = _const_str(k) if k is not None else None
                if s is not None:
                    out.append({"line": node.lineno, "key": s})
    return out


def functions_at(tree):
    """(function name, first line, last line) for every def in the module."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            hi = getattr(node, "end_lineno", None) or max(
                [node.lineno] + [getattr(n, "lineno", node.lineno)
                                 for n in ast.walk(node)])
            out.append((node.name, node.lineno, hi))
    return out


def enclosing_function(functions, line):
    best = None
    for name, lo, hi in functions:
        if lo <= line <= hi and (best is None or (hi - lo) < (best[2] - best[1])):
            best = (name, lo, hi)
    return best[0] if best else None


def _eval_path(node, consts, here):
    """Best-effort resolution of a module path constant to a string."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return consts.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        a, b = _eval_path(node.left, consts, here), _eval_path(node.right, consts, here)
        if a is not None and b is not None:
            return os.path.join(a, b)
        return None
    if isinstance(node, ast.Call):
        fn = node.func
        fname = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else "")
        parts = [_eval_path(a, consts, here) for a in node.args]
        if fname == "join" and parts and all(p is not None for p in parts):
            return os.path.join(*parts)
        if fname == "abspath" and len(parts) == 1:
            if isinstance(node.args[0], ast.Name) and node.args[0].id == "__file__":
                return here
            return parts[0]
        if fname == "dirname" and len(parts) == 1 and parts[0]:
            return os.path.dirname(parts[0])
        if fname == "Path" and len(parts) == 1:
            return parts[0]
        return None
    return None


def module_constants(tree, here=""):
    """name -> str for module-level path constants (plain strings and joins)."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name):
                v = _eval_path(node.value, out, here)
                if isinstance(v, str):
                    out[t.id] = v
    return out


def face_paths(tree, constants, store_lines):
    """Path constants the storing function hands to a writer.

    Returns ``{"paths": [...], "unresolved": [...]}`` -- an expression that
    could not be resolved is published rather than silently dropped.
    """
    paths, unresolved = set(), set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else "")
        writer = name in ("dump", "write_text", "write", "open", "_dump",
                          "save_json", "write_json")
        if not writer:
            continue
        if not any(abs(node.lineno - ln) <= 12 for ln in store_lines):
            continue
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            tok = arg.id if isinstance(arg, ast.Name) else None
            if tok and tok in constants:
                paths.add(constants[tok])
            elif isinstance(arg, (ast.Name, ast.Subscript, ast.Attribute)):
                unresolved.add(" ".join(ast.unparse(arg).split())[:80])
    return {"paths": sorted(paths), "unresolved": sorted(unresolved)}


def face_bound_names(tree, basenames):
    """Names in this module bound from a load of one of the face files.

    A face read must be *proved*: naming the same basename is not enough, the
    reader has to bind a local from that file.  Without this rule the three
    ``alphagen_beam_w1x`` probes read each other's ``out['verdict']`` -- they
    share the file name ``probe_latest.json`` and their own local is also
    called ``out``, which is a name collision, not a channel.
    """
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        try:
            text = ast.unparse(node.value)
        except Exception:
            continue
        if not any(b in text for b in basenames):
            continue
        loader = any(isinstance(n, ast.Call) and (
            (isinstance(n.func, ast.Attribute) and n.func.attr in
             ("load", "loads", "read_text", "read"))
            or (isinstance(n.func, ast.Name) and n.func.id in ("load", "loads")))
            for n in ast.walk(node.value))
        if not loader:
            continue
        for t in node.targets:
            if isinstance(t, ast.Name):
                out.add(t.id)
    return out


def _corpus(root=ROOT):
    files = []
    for pat in CORPUS_GLOBS:
        files.extend(glob.glob(os.path.join(root, pat), recursive=True))
    return sorted(set(os.path.normpath(f) for f in files))


def _rel(path, root=ROOT):
    return os.path.relpath(path, root).replace("\\", "/")


def _parse_uses(path):
    try:
        return uses_in_tree(ast.parse(_read(path)))
    except SyntaxError:
        return []


# ---------------------------------------------------------------- the study
def _unquote(tok):
    """The parent publishes key tokens with their Python quotes attached."""
    s = str(tok).strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        try:
            v = ast.literal_eval(s)
            return v if isinstance(v, str) else s
        except Exception:
            return s[1:-1]
    return s


def parent_rows():
    face = json.load(io.open(PARENT, encoding="utf-8"))
    rows = [r for r in face.get("rows") or [] if r.get("row_class") == P_CREATED]
    for r in rows:
        r["path"] = [_unquote(t) for t in r["path"]]
    rows.sort(key=lambda r: (r["source"], r["function"], r["name"], r["path"]))
    return face, rows


def census_for(row, corpus_uses, root=ROOT):
    """Build the read census for one created item."""
    src_path = os.path.join(root, row["source"])
    tree = ast.parse(_read(src_path))
    fns = functions_at(tree)
    constants = module_constants(tree, here=os.path.dirname(os.path.abspath(src_path)))
    name, path = row["name"], list(row["path"])
    stores = [ln for ln in row["store_lines"]]

    local = []
    for u in uses_in_tree(tree):
        if u["name"] != name:
            continue
        # a read of the exact created path, or of a prefix of it
        if u["path"] == path:
            relation = "the_created_item"
        elif path[:len(u["path"])] == u["path"]:
            relation = "the_container_above_the_item"
        else:
            continue
        if u["form"] == "store":
            continue
        local.append({
            "line": u["line"], "form": u["form"], "relation": relation,
            "function": enclosing_function(fns, u["line"]),
            "in_the_storing_function": enclosing_function(fns, u["line"]) == row["function"],
            "after_the_last_store": u["line"] > max(stores),
            "expr": u["expr"],
        })

    key = path[-1]
    cross, other_container = [], []
    for src, uses in corpus_uses:
        if src == row["source"]:
            continue
        for u in uses:
            if u["path"] != path:
                continue
            if u["name"] == name:
                # same variable name in a different module is a different object
                other_container.append({
                    "module": src, "line": u["line"], "form": u["form"],
                    "container": u["name"], "expr": u["expr"]})
            elif u["path"][-1] == key:
                other_container.append({
                    "module": src, "line": u["line"], "form": u["form"],
                    "container": u["name"], "expr": u["expr"]})
            else:
                cross.append({"module": src, "line": u["line"], "form": u["form"]})

    # every read of the key literal anywhere, regardless of container shape
    key_sites = []
    for src, uses in corpus_uses:
        for u in uses:
            if u["path"] and u["path"][-1] == key:
                key_sites.append({"module": src, "line": u["line"],
                                  "form": u["form"], "container": u["name"]})

    faces = face_paths(tree, constants, stores)
    face_basenames = sorted({os.path.basename(f) for f in faces["paths"]})
    face_readers = []
    modules_naming_the_face = []
    if face_basenames:
        for src, uses in corpus_uses:
            if src == row["source"]:
                continue
            text = _read(os.path.join(root, src))
            if not any(b in text for b in face_basenames):
                continue
            modules_naming_the_face.append(src)
            try:
                ctree = ast.parse(text)
            except SyntaxError:
                continue
            bound = face_bound_names(ctree, face_basenames)
            if not bound:
                continue
            for u in uses:
                if u["form"] == "store" or not u["path"] or u["path"][-1] != key:
                    continue
                if u["name"] not in bound:
                    continue
                face_readers.append({"module": src, "line": u["line"],
                                     "form": u["form"], "container": u["name"],
                                     "bound_from_the_face": True})

    exact = [r for r in local if r["relation"] == "the_created_item"]
    decisive = exact + face_readers
    unguarded = [r for r in decisive if r["form"] in UNGUARDED_FORMS]
    guarded = [r for r in decisive if r["form"] in GUARDED_FORMS]
    if unguarded:
        outcome = O_KEYERROR
    elif guarded:
        outcome = O_DEFAULT
    else:
        outcome = O_NEVER

    # is the item also written on another path (so it exists even when this
    # store does not run)?  Scope the count to the storing function and publish
    # the module-wide writing paths separately.
    all_stores = [u["line"] for u in uses_in_tree(tree)
                  if u["name"] == name and u["path"] == path and u["form"] == "store"]
    in_fn_stores = [ln for ln in all_stores
                    if enclosing_function(fns, ln) == row["function"]]
    face_paths_rel = []
    for f in faces["paths"]:
        try:
            rel = os.path.relpath(f, root).replace("\\", "/")
        except ValueError:
            rel = f
        face_paths_rel.append(rel if not rel.startswith("..") else f)

    return {
        "source": row["source"],
        "function": row["function"],
        "container": name,
        "key_path": path,
        "parent_read_line": row.get("read_line"),
        "store_lines": sorted(set(stores)),
        "stores_of_this_path_in_the_storing_function": sorted(set(in_fn_stores)),
        "stores_of_this_path_in_the_module": sorted(set(all_stores)),
        "outcome": outcome,
        "reads_of_the_created_item": len(exact),
        "unguarded_reads": len(unguarded),
        "guarded_reads": len(guarded),
        "reads_of_the_container_above_the_item": sum(
            1 for r in local if r["relation"] == "the_container_above_the_item"),
        "reads_after_the_last_store": sum(1 for r in exact if r["after_the_last_store"]),
        "reads_in_the_storing_function": sum(1 for r in exact if r["in_the_storing_function"]),
        "read_sites": exact,
        "persisted_face_paths": face_paths_rel,
        "persisted_face_basenames": face_basenames,
        "persisted_face_expressions_this_scan_could_not_resolve": faces["unresolved"],
        "face_channel_readers": face_readers,
        "modules_that_name_the_face_but_bind_nothing_from_it": sorted(
            set(modules_naming_the_face) - {r["module"] for r in face_readers}),
        "modules_naming_the_key_anywhere": sorted({s["module"] for s in key_sites}),
        "key_sites_anywhere": len(key_sites),
        "key_sites_on_another_container": len(other_container),
        "key_sites_on_another_container_sample": other_container[:6],
        "key_sites_matching_the_shape_but_another_container": len(cross),
    }


def build(write=True):
    parent, rows = parent_rows()
    corpus_uses = [(_rel(p), _parse_uses(p)) for p in _corpus()]
    out_rows = [census_for(r, corpus_uses) for r in rows]

    by_outcome = {o: 0 for o in OUTCOME_VOCAB}
    for r in out_rows:
        by_outcome[r["outcome"]] += 1
    by_form = {f: 0 for f in READ_FORMS}
    for r in out_rows:
        for s in r["read_sites"]:
            if s["form"] in by_form:
                by_form[s["form"]] += 1

    keys = sorted({r["key_path"][-1] for r in out_rows})
    naming_modules = sorted({m for r in out_rows for m in r["modules_naming_the_key_anywhere"]})
    producer_only = [
        r for r in out_rows
        if r["reads_in_the_storing_function"] == r["reads_of_the_created_item"]
        and r["reads_of_the_created_item"] > 0
        and not r["face_channel_readers"]]
    summary = {
        "parent_rows_published_as_created": len(rows),
        "distinct_created_keys": len(keys),
        "created_keys": keys,
        "distinct_storing_modules": len({r["source"] for r in out_rows}),
        "by_outcome": by_outcome,
        "reads_of_the_created_item_total": sum(r["reads_of_the_created_item"] for r in out_rows),
        "unguarded_reads_total": sum(r["unguarded_reads"] for r in out_rows),
        "guarded_reads_total": sum(r["guarded_reads"] for r in out_rows),
        "read_forms_on_the_created_item": by_form,
        "rows_whose_read_is_in_the_storing_function":
            sum(1 for r in out_rows if r["reads_in_the_storing_function"]),
        "rows_whose_every_read_sits_in_the_storing_function_after_the_store":
            len(producer_only),
        "rows_read_by_a_different_module_through_a_persisted_face":
            sum(1 for r in out_rows if r["face_channel_readers"]),
        "rows_that_persist_the_container_at_all":
            sum(1 for r in out_rows if r["persisted_face_paths"]),
        "rows_with_a_persisted_path_this_scan_could_not_resolve":
            sum(1 for r in out_rows
                if r["persisted_face_expressions_this_scan_could_not_resolve"]),
        "key_reads_anywhere_total": sum(r["key_sites_anywhere"] for r in out_rows),
        "key_reads_on_another_container_total":
            sum(r["key_sites_on_another_container"] for r in out_rows),
        "modules_naming_any_of_the_keys": len(naming_modules),
        "modules_naming_any_of_the_keys_sample": naming_modules[:25],
        "rows_whose_item_is_written_more_than_once_in_the_storing_function":
            sum(1 for r in out_rows
                if len(r["stores_of_this_path_in_the_storing_function"]) > 1),
        "corpus_modules_scanned": len(corpus_uses),
    }
    summary["modules_naming_anything_that_is_not_a_read"] = summary["modules_naming_any_of_the_keys"]
    summary["share_of_key_reads_that_are_on_a_colliding_container"] = (
        round(summary["key_reads_on_another_container_total"] /
              summary["key_reads_anywhere_total"], 4)
        if summary["key_reads_anywhere_total"] else None)

    # second dimension: WHO reads the created item.  A producer reading its own
    # print is a different risk from a downstream module reading a persisted
    # face, and only the second one can break a consumer.
    if not summary["reads_of_the_created_item_total"]:
        read_scope = "nothing_reads_them"
    elif summary["rows_read_by_a_different_module_through_a_persisted_face"]:
        read_scope = "at_least_one_row_is_read_through_a_persisted_face"
    elif len(producer_only) == len(out_rows):
        read_scope = "the_storing_function_itself_and_nothing_outside_it"
    else:
        read_scope = "inside_the_producing_module_only"

    if by_outcome[O_KEYERROR] == len(out_rows):
        verdict = (V_PRODUCER_ONLY if read_scope in (
            "the_storing_function_itself_and_nothing_outside_it",
            "inside_the_producing_module_only") else V_KEYERROR)
    elif by_outcome[O_KEYERROR] == 0 and by_outcome[O_DEFAULT] == 0:
        verdict = V_NEVER
    elif by_outcome[O_KEYERROR] == 0:
        verdict = V_DEFAULT
    else:
        verdict = V_MIXED

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "date": EVIDENCE_CUTOFF,
        "evidence_cutoff": EVIDENCE_CUTOFF + " (corpus read from the working tree at build time)",
        "parent_face": os.path.basename(PARENT),
        "outcome_vocab": list(OUTCOME_VOCAB),
        "read_form_vocab": list(READ_FORMS),
        "limits": [
            "the population is the parent's own eight 'creates an item' rows (machine-read, never hand-listed); a store the parent did not publish is not in this census and is not counted as clean",
            "the cross-module channel is a key-literal census: a module that reads 'key' off its OWN container of the same name is published as a colliding container, not as a consumer of this face -- two different dicts can share a key name",
            "the persisted-face channel only fires where the storing function hands a module string constant to a dump/open within 12 lines of the store; a face written through a computed path is not resolved and is disclosed as unresolved rather than counted as unread",
            "reads are static from the AST: a subscript inside a try/except KeyError is counted as an unguarded read, because the guard is at the caller and not at the site",
        ],
        "summary": summary,
        "read_scope": read_scope,
        "verdict": verdict,
        "rows": out_rows,
    }
    if write:
        _dump_face(face, FACE)
        _dump_face(face, LATEST)
    return face


# --------------------------------------------------------------- face gates
def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        problems.append("the face publishes no rows")
    if s.get("parent_rows_published_as_created") != len(rows):
        problems.append("the published row count is not the parent's own count")
    by = {o: 0 for o in OUTCOME_VOCAB}
    for r in rows:
        if r.get("outcome") not in OUTCOME_VOCAB:
            problems.append("a row carries an outcome outside the vocabulary: %r" % (r.get("outcome"),))
        else:
            by[r["outcome"]] += 1
        # the outcome must be re-derivable from the row's own read list
        decisive = list(r.get("read_sites") or []) + list(r.get("face_channel_readers") or [])
        ung = sum(1 for x in decisive if x.get("form") in UNGUARDED_FORMS)
        gd = sum(1 for x in decisive if x.get("form") in GUARDED_FORMS)
        want = O_KEYERROR if ung else (O_DEFAULT if gd else O_NEVER)
        if want != r.get("outcome"):
            problems.append("row outcome does not re-derive from its own reads: %s:%s"
                            % (r.get("source"), r.get("key_path")))
        if r.get("unguarded_reads") != ung:
            problems.append("the published unguarded count is not the row's own: %s:%s"
                            % (r.get("source"), r.get("key_path")))
        if r.get("guarded_reads") != gd:
            problems.append("the published guarded count is not the row's own: %s:%s"
                            % (r.get("source"), r.get("key_path")))
        if r.get("reads_of_the_created_item") != len(r.get("read_sites") or []):
            problems.append("the published read count is not the row's own list: %s:%s"
                            % (r.get("source"), r.get("key_path")))
    if (s.get("by_outcome") or {}) != by:
        problems.append("the summary outcome table is not its rows'")
    if sum(by.values()) != len(rows):
        problems.append("the outcome table does not cover every row")
    # a keyerror verdict may not sit beside zero unguarded reads, and a "never"
    # verdict may not sit beside a read of the item
    v = face.get("verdict")
    if v not in (V_KEYERROR, V_DEFAULT, V_MIXED, V_NEVER, V_PRODUCER_ONLY):
        problems.append("the verdict is outside the vocabulary this study publishes: %r" % (v,))
    if v in (V_KEYERROR, V_MIXED) and s.get("unguarded_reads_total", 0) == 0:
        problems.append("a verdict of load-bearing sits beside zero unguarded reads")
    if v == V_NEVER and s.get("reads_of_the_created_item_total", 0) != 0:
        problems.append("a verdict of never-read sits beside reads of the item")
    if v == V_PRODUCER_ONLY and s.get("rows_read_by_a_different_module_through_a_persisted_face", 0) != 0:
        problems.append("a producer-only verdict sits beside a read proved through a persisted face")
    if s.get("modules_naming_any_of_the_keys") != len(
            {m for r in rows for m in (r.get("modules_naming_the_key_anywhere") or [])}):
        problems.append("the key-naming module count is not the union of its rows' lists")
    if s.get("rows_whose_every_read_sits_in_the_storing_function_after_the_store", 0) > len(rows):
        problems.append("the producer-only row count exceeds the population")
    return problems


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if json.dumps(fresh, sort_keys=True) != json.dumps(pub, sort_keys=True):
        problems.append("the published face is not what the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or [])}, ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    problems = [] if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else \
        ["two builds of the same sources differ"]
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ------------------------------------------------------------------ selftest
FIX_UNGARDLESS = """
import json
FACE = "results/fixture_a.json"

def run():
    out = {"checks": {}}
    out["verdict"] = "PASS" if True else "FAIL"
    json.dump(out, open(FACE, "w"))
    print("verdict:", out["verdict"])
"""

FIX_GUARDED = """
def run():
    art = {}
    art["trials_N"] = {"a": 0}
    print(art.get("trials_N", {}))
    if "trials_N" in art:
        pass
"""

FIX_NEVER = """
def run():
    art = {}
    art["trials_N"] = {"a": 0}
    return art
"""

FIX_OTHER_CONTAINER = """
def run(params):
    params["trials_N"] = 1
    return params["trials_N"]
"""


def _fixture_row(source, name, path, store_line):
    return {"source": source, "function": "run", "name": name, "path": list(path),
            "binding_line": 1, "store_lines": [store_line], "read_line": store_line + 1}


def selftest():
    import tempfile
    from contextlib import contextmanager

    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "results"))
        files = {"a.py": FIX_UNGARDLESS, "b.py": FIX_GUARDED,
                 "c.py": FIX_NEVER, "d.py": FIX_OTHER_CONTAINER}
        for fn, body in files.items():
            with io.open(os.path.join(td, fn), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(textwrap.dedent(body))

        corpus = [(_rel(p, td), _parse_uses(p)) for p in
                  sorted(glob.glob(os.path.join(td, "*.py")))]

        ra = census_for(_fixture_row("a.py", "out", ["verdict"], 6), corpus, root=td)
        ck("an unguarded subscript read after the store is the load-bearing class",
           ra["outcome"] == O_KEYERROR)
        ck("the read is recorded as inside the storing function and after the store",
           ra["reads_in_the_storing_function"] == 1 and ra["reads_after_the_last_store"] == 1)
        ck("the persisted face path is resolved from the dump argument",
           ra["persisted_face_paths"] == ["results/fixture_a.json"])

        rb = census_for(_fixture_row("b.py", "art", ["trials_N"], 3), corpus, root=td)
        ck("a get on the item is the guarded class", rb["outcome"] == O_DEFAULT)
        ck("a membership test is counted as a guarded read and not as a subscript",
           rb["guarded_reads"] == 2 and rb["unguarded_reads"] == 0)

        rc = census_for(_fixture_row("c.py", "art", ["trials_N"], 3), corpus, root=td)
        ck("no read at all is the never class", rc["outcome"] == O_NEVER)
        ck("a module that reads the same key off a different container is not a read of the item",
           rc["outcome"] == O_NEVER and rc["key_sites_on_another_container"] >= 1)
        ck("the colliding-container reads are published, not dropped",
           rc["key_sites_on_another_container"] >= 2
           and any(s["container"] == "params" for s in rc["key_sites_on_another_container_sample"]))
        ck("a same-named container in ANOTHER module is also another container",
           any(s["container"] == "art" for s in rc["key_sites_on_another_container_sample"]))

        rd = census_for(_fixture_row("d.py", "params", ["trials_N"], 2), corpus, root=td)
        ck("a store plus a subscript read in the defining module is the load-bearing class",
           rd["outcome"] == O_KEYERROR)

        # gates
        face = {"rows": [{"source": "x.py", "key_path": ["k"], "outcome": O_KEYERROR,
                          "unguarded_reads": 1, "guarded_reads": 0,
                          "reads_of_the_created_item": 1,
                          "read_sites": [{"form": F_SUBSCRIPT}],
                          "face_channel_readers": [],
                          "modules_naming_the_key_anywhere": ["y.py"]}],
                "summary": {"parent_rows_published_as_created": 1,
                            "by_outcome": {O_KEYERROR: 1, O_DEFAULT: 0, O_NEVER: 0},
                            "unguarded_reads_total": 1,
                            "reads_of_the_created_item_total": 1,
                            "modules_naming_any_of_the_keys": 1,
                            "rows_whose_every_read_sits_in_the_storing_function_after_the_store": 1,
                            "rows_read_by_a_different_module_through_a_persisted_face": 0},
                "verdict": V_KEYERROR}
        ck("a consistent face raises no problems", face_problems(face) == [])

        bad = json.loads(json.dumps(face))
        bad["rows"][0]["outcome"] = O_NEVER
        ck("a flipped outcome is refused", any("re-derive" in p for p in face_problems(bad)))

        bad2 = json.loads(json.dumps(face))
        bad2["rows"][0]["unguarded_reads"] = 3
        ck("a published count that is not the row list's is refused",
           any("unguarded count" in p for p in face_problems(bad2)))

        bad3 = json.loads(json.dumps(face))
        bad3["summary"]["by_outcome"] = {O_KEYERROR: 0, O_DEFAULT: 1, O_NEVER: 0}
        ck("a summary table that is not the rows' is refused",
           any("outcome table" in p for p in face_problems(bad3)))

        bad4 = json.loads(json.dumps(face))
        bad4["verdict"] = V_NEVER
        ck("a never-verdict beside a read of the item is refused",
           any("never-read" in p for p in face_problems(bad4)))

        bad5 = {"rows": [], "summary": {}, "verdict": V_NEVER}
        ck("an empty face is refused", any("no rows" in p for p in face_problems(bad5)))

    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        print(("PASS " if c else "FAIL ") + name)
    print(json.dumps({"passed": ok, "total": len(checks)}, ensure_ascii=False))
    return 0 if ok == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        s = face["summary"]
        print(json.dumps({
            "rows": len(face["rows"]),
            "parent_rows": s["parent_rows_published_as_created"],
            "by_outcome": s["by_outcome"],
            "unguarded": s["unguarded_reads_total"],
            "guarded": s["guarded_reads_total"],
            "key_reads_on_another_container": s["key_reads_on_another_container_total"],
            "verdict": face["verdict"],
        }, ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s (build|check|verify|selftest)" % cmd)


if __name__ == "__main__":
    sys.exit(main())