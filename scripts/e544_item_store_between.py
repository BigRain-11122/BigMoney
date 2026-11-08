"""E544 -- which item store between a binding and a site changes the value the fold publishes?

E536 (results/state_tilt/INLINEDFOLD-2026-11-08.json) folded one site's argument through one binding
hop and published a value, then found -- in its own window, on its own witness -- that a store sits
between the binding and the site:

    scripts/e285_interrange_gap_ceiling.py:503   off = _fixture_arm()
    scripts/e285_interrange_gap_ceiling.py:504   off["rows"][1]["tight"] = _td(0.9, 1.2)
    scripts/e285_interrange_gap_ceiling.py:505   ranges_are_row_identical(off["rows"], "tight", interval(off["rows"], "tight"))

The fold publishes the hull the container held when it was bound (lo=1.0).  The assertion consumes the
hull the store left behind (lo=0.9).  E536 published that mismatch as a limit and as the next card.

This study prices the pattern instead of the one witness.  It scans every module in ``scripts/`` and,
for each function, replays its statements in line order over a literal interpreter of the same
whitelist E536 uses (constants, containers, subscripts, arithmetic, a fixed builtin set, and repo
functions whose body is a supported statement chain).  On that replay it records three kinds of event:

  * **bind**  -- ``NAME = <expr>`` that the interpreter can evaluate;
  * **store** -- an assignment whose target is a subscript path rooted at a bound name
                 (``NAME[k] = v`` and ``NAME[k1][k2] = v`` alike);
  * **read**  -- a loaded subscript path rooted at a bound name.

A row exists only where a store and a later read address the *same path on the same name*: that is the
population the card names.  Every such row is classified by what a consumer of the fold would
observe, not by what the source looks like:

  * ``R_CHANGED`` -- the value at the path right after the binding differs from the value the read
    receives; the fold would publish the first and the site consumes the second.
  * ``R_CREATED`` -- the path does not exist right after the binding; the store creates it.  The fold
    publishes no item at all, so a consumer reading the published container sees a missing key.
  * ``R_SAME``    -- the store writes back the same value (an idempotent store); the fold's value is
    what the site reads.

Nothing in this repository is executed.  The tree is read as text and evaluated by this module's own
interpreter; no source is rewritten and no module of the corpus is imported.

    python scripts/e544_item_store_between.py build     # write the face
    python scripts/e544_item_store_between.py check     # gate the published face (fast)
    python scripts/e544_item_store_between.py verify    # re-derive from the tree and gate
    python scripts/e544_item_store_between.py selftest  # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e533_call_pure_arm as e533  # noqa: E402  (_fold: the one-hop literal fold)
import e536_inlined_fold as e536  # noqa: E402  (ev/call_function: the literal interpreter)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E544-WHICH-ITEM-STORE-BETWEEN-A-BINDING-AND-A-SITE-CHANGES-THE-VALUE-THE-FOLD-PUBLISHES")
STUDY = "E544_item_store_between"
DATE_STAMP = "2026-11-08"
FACE_NAME = "itemstorebetween_latest.json"
DATED_PREFIX = "ITEMSTOREBETWEEN"
PARENT_FACE = "INLINEDFOLD-2026-11-08.json"
WITNESS = "scripts/e285_interrange_gap_ceiling.py"

# a scan that reads the tree must not read its own output or its own predecessors
SELF_EXCLUDED = ("e544_", "run_e544", "_e544", "ITEMSTOREBETWEEN", "itemstorebetween_")

R_CHANGED = "the_value_the_site_reads_differs_from_the_one_the_fold_publishes"
R_CREATED = "the_store_creates_an_item_the_fold_never_publishes"
R_SAME = "the_store_leaves_the_value_the_site_reads_unchanged"
ROW_VOCAB = (R_CHANGED, R_CREATED, R_SAME)

_MISSING = object()
MAX_ROWS = 8000
MAX_STEPS_PER_FILE = 200000


def _now():
    return "%sT%s" % (DATE_STAMP, "00:00:00+08:00")


def _is_self(name):
    low = name.lower()
    return any(tok.lower() in low for tok in SELF_EXCLUDED)


# ------------------------------------------------------------------ the corpus
def corpus_files(root=None):
    root = root or ROOT
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "scripts")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for name in sorted(files):
            if name.endswith(".py") and not _is_self(name):
                out.append(os.path.join(base, name))
    return out


def _rel(root, path):
    return os.path.relpath(path, root).replace("\\", "/")


# ------------------------------------------------------------------ the statement walk
def _visit(node):
    """Yield nodes of one function body, never descending into nested defs/classes."""
    yield node
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield from _visit(ch)


def _sub_path(node):
    """(base name, [index expressions]) for a subscript path rooted at a bare name, else (None, None)."""
    parts = []
    cur = node
    while isinstance(cur, ast.Subscript):
        parts.append(cur.slice)
        cur = cur.value
    if isinstance(cur, ast.Name):
        return cur.id, list(reversed(parts))
    return None, None


def _eval(node, env, root):
    try:
        return e533._fold(node)
    except e533._Stop:
        pass
    except Exception:
        pass
    try:
        return e536.ev(node, env, root)
    except Exception:
        return _MISSING


def _eval_keys(path, env, root):
    keys = []
    for node in path:
        v = _eval(node, env, root)
        if v is _MISSING:
            return None
        try:
            hash(v)
        except TypeError:
            return None
        keys.append(v)
    return keys


def _get_path(cur, keys):
    for k in keys:
        try:
            cur = cur[k]
        except Exception:
            return _MISSING
    return cur


def _set_path(cur, keys, value):
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = value


def _text(value):
    if value is _MISSING:
        return None
    try:
        return e533._text(value)
    except Exception:
        return repr(value)[:120]


def _target_nodes(fn):
    """Ids of every node inside an assignment target -- an inner subscript of a store target carries
    Load context in the AST, so without this a store would be read as a read at its own line."""
    out = set()
    for node in _visit(fn):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        for tgt in targets:
            for inner in ast.walk(tgt):
                out.add(id(inner))
    return out


def _walk_with_stmt(body):
    """(node, enclosing statement) for every node of one function body, nested defs excluded."""
    def descend(node, root):
        yield node, root
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            yield from descend(ch, root)
    for stmt in body:
        yield from descend(stmt, stmt)


def _events(fn):
    """Events sorted in evaluation order: a statement's own reads happen before its binding/store."""
    out = []
    target_ids = _target_nodes(fn)
    for node, stmt in _walk_with_stmt(fn.body):
        head = (getattr(stmt, "lineno", 0), getattr(stmt, "col_offset", 0))
        if node is stmt:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
                if isinstance(tgt, ast.Name):
                    out.append((head, 1, 0, "bind", node))
                elif isinstance(tgt, ast.Subscript):
                    base, path = _sub_path(tgt)
                    if base:
                        out.append((head, 1, 0, "store", node))
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
                out.append((head, 1, 0, "bind", node))
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
            if id(node) in target_ids:
                continue
            base, path = _sub_path(node)
            if base:
                out.append((head, 0, (getattr(node, "lineno", 0), getattr(node, "col_offset", 0)),
                            "read", node))
    out.sort(key=lambda e: (e[0], e[1], e[2]))
    return [(e[0][0], e[3], e[4]) for e in out]


def _is_prefix(short, long):
    """True when `short` addresses an item that contains the item `long` addresses (or the same one)."""
    return len(short) <= len(long) and tuple(long[:len(short)]) == tuple(short)


def scan_function(fn, root, rel, fn_map=None):
    # the interpreter resolves a repo call by name only through this map (e536._resolve_fn)
    env = {"_fn_map": dict(fn_map or {})}
    pristine = {}
    bound_line = {}
    stores = {}
    rows = []
    for line, kind, node in _events(fn):
        if kind == "bind":
            name = node.target.id if isinstance(node, ast.AnnAssign) else node.targets[0].id
            value = _eval(node.value, env, root)
            if value is _MISSING:
                env.pop(name, None)
                pristine.pop(name, None)
                bound_line.pop(name, None)
                continue
            env[name] = copy.deepcopy(value)
            pristine[name] = copy.deepcopy(value)
            bound_line[name] = line
            stores.pop(name, None)
            continue
        if kind == "store":
            base, path = _sub_path(node.targets[0])
            if not base or base not in env:
                continue
            keys = _eval_keys(path, env, root)
            if keys is None:
                continue
            value = _eval(node.value, env, root)
            if value is _MISSING:
                continue
            try:
                _set_path(env[base], keys, value)
            except Exception:
                continue
            stores.setdefault(base, []).append({
                "keys": tuple(keys),
                "line": line,
                "target": ast.unparse(node.targets[0])[:90],
                "value_text": _text(value),
            })
            continue
        # read
        base, path = _sub_path(node)
        if not base or base not in env:
            continue
        keys = _eval_keys(path, env, root)
        if keys is None:
            continue
        # a store below this path changes the item the read receives, not just a store on the same path
        related = [s for s in stores.get(base, ())
                   if _is_prefix(keys, s["keys"]) or _is_prefix(s["keys"], keys)]
        if not related:
            continue
        cur = _get_path(env[base], keys)
        if cur is _MISSING:
            continue
        pre = _get_path(pristine[base], keys) if base in pristine else _MISSING
        if pre is _MISSING:
            row_class = R_CREATED
            pre_text = None
        elif e536._same(pre, cur):
            row_class = R_SAME
            pre_text = _text(pre)
        else:
            row_class = R_CHANGED
            pre_text = _text(pre)
        rows.append({
            "source": rel,
            "function": getattr(fn, "name", "<module>"),
            "name": base,
            "path": [_text(k) for k in keys],
            "binding_line": bound_line.get(base),
            "store_lines": sorted({s["line"] for s in related}),
            "store_targets": [s["target"] for s in related],
            "read_line": line,
            "row_class": row_class,
            "fold_value": pre_text,
            "site_value": _text(cur),
        })
    return rows


def _functions(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(node)
    return out


def scan_file(root, rel):
    path = os.path.join(root, rel)
    try:
        src = open(path, "rb").read().decode("utf-8", "replace")
        tree = ast.parse(src, rel)
    except Exception:
        return []
    e536.MAX_STEPS = MAX_STEPS_PER_FILE
    e536._STEPS[0] = 0
    fn_map = {node.name: node for node in tree.body
              if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    # a callee only reaches its own module's functions when it carries the module it came from
    for node in fn_map.values():
        node._e536_rel = rel
    rows = []
    for fn in _functions(tree):
        fn._e536_rel = rel
        try:
            rows.extend(scan_function(fn, root, rel, fn_map))
        except RecursionError:
            continue
    return rows


# ------------------------------------------------------------------ face
def _count(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def _summary(rows, sources):
    changed = [r for r in rows if r["row_class"] == R_CHANGED]
    created = [r for r in rows if r["row_class"] == R_CREATED]
    same = [r for r in rows if r["row_class"] == R_SAME]
    by_source = {}
    for r in changed:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    witness = [r for r in rows if r["source"] == WITNESS]
    return {
        "sources_scanned": len(sources),
        "rows": len(rows),
        "changed": len(changed),
        "created": len(created),
        "same": len(same),
        "sources_with_a_changed_row": len(by_source),
        "witness_rows": len(witness),
        "witness_rows_changed": len([r for r in witness if r["row_class"] == R_CHANGED]),
        "by_row_class": _count(rows, "row_class"),
        "top_sources_by_changed": sorted(by_source.items(), key=lambda kv: -kv[1])[:10],
    }


def _verdict(summary):
    total = summary["rows"]
    if total == 0:
        return ("no_item_store_sits_between_a_binding_and_a_site_that_reads_the_same_item")
    moved = summary["changed"] + summary["created"]
    if moved == 0:
        return ("every_item_store_between_a_binding_and_its_site_leaves_the_value_the_fold_publishes_unchanged")
    if summary["changed"] and summary["created"] == 0:
        return ("item_stores_between_a_binding_and_its_site_do_change_the_value_the_fold_publishes")
    if summary["created"] and summary["changed"] == 0:
        return ("item_stores_between_a_binding_and_its_site_publish_items_the_fold_never_sees")
    return ("item_stores_between_a_binding_and_its_site_both_change_published_values_and_publish_items_the_fold_never_sees")


def build(root=None, write=True):
    root = root or ROOT
    files = corpus_files(root)
    sources = [_rel(root, p) for p in files]
    rows = []
    for rel in sources:
        rows.extend(scan_file(root, rel))
        if len(rows) > MAX_ROWS:
            rows = rows[:MAX_ROWS]
            break
    rows.sort(key=lambda r: (r["source"], r["read_line"], r["name"], r["path"]))
    summary = _summary(rows, sources)
    face = {
        "study": STUDY,
        "card": CARD,
        "date": DATE_STAMP,
        "evidence_cutoff": "%s (corpus read from the working tree at build time)" % DATE_STAMP,
        "parent_face": PARENT_FACE,
        "witness": WITNESS,
        "row_vocab": list(ROW_VOCAB),
        "limits": [
            "the_population_is_only_the_containers_this_interpreter_can_bind: a name bound to a literal "
            "container, or to a repo function whose body is a supported statement chain -- a container "
            "built from a tree read is not in the population and is not counted as clean",
            "a store whose value the interpreter cannot evaluate is skipped rather than priced",
            "a row is a (store, later read) pair on one name where one path contains the other, not a "
            "statement that only one consumer sees: two reads of the same container on one line publish "
            "two rows",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "rows": rows,
    }
    if write:
        write_face(face, root)
    return face


def face_path(root=None):
    root = root or ROOT
    return os.path.join(root, "results", "state_tilt", "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))


def latest_path(root=None):
    root = root or ROOT
    return os.path.join(root, "results", "state_tilt", FACE_NAME)


def write_face(face, root=None):
    root = root or ROOT
    os.makedirs(os.path.join(root, "results", "state_tilt"), exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False)
    with open(face_path(root), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    with open(latest_path(root), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")


def load_face(root=None):
    path = latest_path(root)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face):
    problems = []
    for key in ("study", "card", "date", "evidence_cutoff", "summary", "verdict", "rows", "row_vocab"):
        if key not in face:
            problems.append("face_is_missing_%s" % key)
    if problems:
        return problems
    rows = face["rows"]
    summary = face["summary"]
    recomputed = _summary(rows, [""] * summary.get("sources_scanned", 0))
    if json.dumps(summary, sort_keys=True) != json.dumps(recomputed, sort_keys=True):
        problems.append("summary_does_not_re_derive_from_the_published_rows")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict_is_not_the_one_this_summary_derives")
    unknown = sorted({r["row_class"] for r in rows} - set(ROW_VOCAB))
    if unknown:
        problems.append("rows_carry_a_class_outside_the_vocabulary:%s" % ",".join(unknown))
    for i, r in enumerate(rows):
        if not r.get("store_lines"):
            problems.append("row_%d_has_no_store" % i)
            break
        if not r.get("binding_line") or min(r["store_lines"]) <= r["binding_line"]:
            problems.append("row_%d_stores_before_its_binding" % i)
            break
        if r["binding_line"] > r["read_line"] or max(r["store_lines"]) >= r["read_line"]:
            problems.append("row_%d_reads_before_its_store" % i)
            break
        if r["row_class"] == R_CHANGED and r["fold_value"] == r["site_value"]:
            problems.append("row_%d_is_classed_changed_but_publishes_one_value" % i)
            break
        if r["row_class"] == R_SAME and r["fold_value"] != r["site_value"]:
            problems.append("row_%d_is_classed_same_but_publishes_two_values" % i)
            break
        if r["row_class"] == R_CREATED and r["fold_value"] is not None:
            problems.append("row_%d_is_classed_created_but_publishes_a_fold_value" % i)
            break
    if face["verdict"].startswith("every_item_store") and (summary["changed"] or summary["created"]):
        problems.append("the_face_claims_every_store_is_harmless_while_publishing_moved_values")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = face_problems(face)
    for p in problems:
        print("PROBLEM " + p)
    print("CHECK %s problems=%d rows=%d" % (("OK" if not problems else "FAIL"),
                                            len(problems), len(face.get("rows") or [])))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    published = load_face(root)
    rebuilt = build(root, write=False)
    problems = face_problems(published)
    for key in ("summary", "verdict", "rows"):
        if json.dumps(published.get(key), sort_keys=True) != json.dumps(rebuilt.get(key), sort_keys=True):
            problems.append("rebuild_does_not_reproduce_%s" % key)
    for p in problems:
        print("PROBLEM " + p)
    print("VERIFY %s problems=%d rows=%d summary_identical=%s"
          % (("OK" if not problems else "FAIL"), len(problems), len(published.get("rows") or []),
             json.dumps(published.get("summary"), sort_keys=True)
             == json.dumps(rebuilt.get("summary"), sort_keys=True)))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
def changed():
    box = {"rows": [{"tight": (1.0, 1.1)}, {"tight": (1.0, 1.2)}]}
    box["rows"][1]["tight"] = (0.9, 1.2)
    return box["rows"][1]["tight"]


def created():
    box = {"rows": [{}]}
    box["rows"][0]["tight"] = (0.9, 1.2)
    return box["rows"][0]["tight"]


def same_value():
    box = {"n": 3}
    box["n"] = 3
    return box["n"]


def read_before_the_store():
    box = {"n": 3}
    first = box["n"]
    box["n"] = 9
    return first


def not_folded():
    box = build_it()
    box["n"] = 9
    return box["n"]
'''


def _fixture_rows():
    tmp = tempfile.mkdtemp(prefix="e544_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
        with open(os.path.join(tmp, "scripts", "fixture.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        return scan_file(tmp, "scripts/fixture.py")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def selftest():
    fails = []

    def check_one(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
        if not ok:
            fails.append(name)

    rows = _fixture_rows()
    by_fn = {}
    for r in rows:
        by_fn.setdefault(r["function"], []).append(r)

    def at(fn_name, path):
        return [r for r in by_fn.get(fn_name, []) if r["path"] == path]

    changed_deep = at("changed", ["'rows'", "1", "'tight'"])
    changed_wide = at("changed", ["'rows'", "1"])
    check_one("fixture: the mutated item is published as changed",
              bool(changed_deep) and all(r["row_class"] == R_CHANGED for r in changed_deep),
              repr([[r["row_class"], r["fold_value"], r["site_value"]] for r in changed_deep]))
    check_one("fixture: the container that holds the mutated item is published as changed too",
              bool(changed_wide) and all(r["row_class"] == R_CHANGED for r in changed_wide),
              repr([[r["row_class"]] for r in changed_wide]))
    check_one("fixture: the changed row publishes the two values the fold and the site see",
              changed_deep and changed_deep[0]["fold_value"] != changed_deep[0]["site_value"],
              repr([(r["fold_value"], r["site_value"]) for r in changed_deep]))
    check_one("fixture: a store that creates the item is published as created",
              any(r["row_class"] == R_CREATED and r["fold_value"] is None
                  for r in at("created", ["'rows'", "0", "'tight'"])),
              repr([[r["row_class"], r["fold_value"]] for r in at("created", ["'rows'", "0", "'tight'"])]))
    check_one("fixture: an idempotent store is published as same",
              [r["row_class"] for r in by_fn.get("same_value", [])] == [R_SAME],
              repr([r["row_class"] for r in by_fn.get("same_value", [])]))
    check_one("fixture: a read before the store is not a row",
              by_fn.get("read_before_the_store") is None,
              repr([(r["read_line"], r["store_lines"]) for r in by_fn.get("read_before_the_store", [])]))
    check_one("fixture: a container the interpreter cannot bind is not a row",
              by_fn.get("not_folded") is None,
              repr([r["name"] for r in by_fn.get("not_folded", [])]))
    check_one("fixture: every row stores after its binding and before its read",
              all(min(r["store_lines"]) > r["binding_line"] and max(r["store_lines"]) < r["read_line"]
                  for r in rows),
              repr([(r["binding_line"], r["store_lines"], r["read_line"]) for r in rows
                    if not (min(r["store_lines"]) > r["binding_line"]
                            and max(r["store_lines"]) < r["read_line"])]))

    # the face gates must be able to go red on a doctored face
    face = {
        "study": STUDY, "card": CARD, "date": DATE_STAMP,
        "evidence_cutoff": DATE_STAMP,
        "summary": _summary(rows, ["scripts/fixture.py"]),
        "verdict": _verdict(_summary(rows, ["scripts/fixture.py"])),
        "rows": rows, "row_vocab": list(ROW_VOCAB),
        "parent_face": PARENT_FACE, "witness": WITNESS,
    }
    check_one("gate: the clean fixture face passes", face_problems(face) == [], repr(face_problems(face)[:3]))

    def doctored(mutator):
        doc = copy.deepcopy(face)
        mutator(doc)
        return face_problems(doc)

    def flip_class(doc):
        for r in doc["rows"]:
            if r["row_class"] == R_CHANGED:
                r["row_class"] = R_SAME
                return

    def handwrite_verdict(doc):
        doc["verdict"] = "a_verdict_this_study_never_publishes"

    def drop_store(doc):
        for r in doc["rows"]:
            r["store_lines"] = []
            return

    def move_store_before_binding(doc):
        for r in doc["rows"]:
            r["store_lines"] = [0]
            return

    def claim_harmless(doc):
        # the verdict that says every store is harmless, kept while the moved rows are still published
        doc["verdict"] = ("every_item_store_between_a_binding_and_its_site_leaves_the_value_the_fold_"
                          "publishes_unchanged")

    def dropped_rows(doc):
        doc["rows"] = [r for r in doc["rows"] if r["row_class"] == R_SAME]

    for name, mut in (("flipped row class", flip_class),
                      ("hand-written verdict", handwrite_verdict),
                      ("row without a store", drop_store),
                      ("store before the binding", move_store_before_binding),
                      ("verdict that calls every store harmless", claim_harmless),
                      ("summary that outlives its rows", dropped_rows)):
        problems = doctored(mut)
        check_one("gate: refuses a face with a %s" % name, bool(problems), repr(problems[:2]))

    check_one("gate: a missing evidence_cutoff is refused",
              "face_is_missing_evidence_cutoff" in doctored(lambda d: d.pop("evidence_cutoff")),
              "")

    print("SELFTEST %s arms=%d fails=%d" % ("OK" if not fails else "FAIL", 13, len(fails)))
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "build"
    if mode == "build":
        face = build()
        print("BUILD rows=%d changed=%d created=%d same=%d verdict=%s"
              % (face["summary"]["rows"], face["summary"]["changed"], face["summary"]["created"],
                 face["summary"]["same"], face["verdict"]))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())