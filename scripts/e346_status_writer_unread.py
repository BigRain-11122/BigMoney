"""E346 -- what a status writer writes that nobody reads.

E343 excluded ten `st['key'] = value` stores from its "bound read" count because they
write into the dict that was just loaded rather than reading the key back.  Those stores
are still statements a reader may trust: the writer files `expected_cutoff`, `mode`,
`last_attempt`, `no_op_reason` and friends into a status face that the fleet's heartbeat
and the ops pages read.

This census asks, mechanically:

  (a) for each status-writing producer, which keys does it store, and does ANY consumer
      in the tree read that key off the face it wrote;
  (b) split into no_reader / self_fed_only / read_by_someone;
  (c) for self_fed keys, does a wrong value written once change the writer's NEXT
      decision -- a state field nobody validates is a latch, not a record;
  (d) publish the unread set by name with the size of each face, and name the rows where
      a single hand-edited status file would change an operational decision.

Nothing is executed from the analysis: this is an AST/text census over the tree.

Usage:
  python scripts/e346_status_writer_unread.py verify     # re-derive + compare to face
  python scripts/e346_status_writer_unread.py build      # write the face
  python scripts/e346_status_writer_unread.py selftest   # offline fixture legs
"""
from __future__ import annotations

import ast
import json
import operator
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE_DIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "UNREADSTATUS-2026-11-01.json"
EVIDENCE_CUTOFF = "2026-11-01"

# Corpus of potential consumers.  Deliberately broad: a status face that no source outside
# its own writer names is exactly the shape this study is looking for.
CORPUS_DIRS = ["scripts", "monitor", "Tools", "firm", "live", "content"]
CORPUS_FILES = ["smoke_test.py"]

# Producers named by the card.  Discovery is by file, not by import, so a producer that is
# renamed disappears from the census loudly rather than silently.
PRODUCERS = [
    "scripts/update_futures.py",
    "scripts/update_etf_daily.py",
    "scripts/update_options.py",
    "scripts/update_repo.py",
    "scripts/update_astock_daily.py",
    "scripts/update_sina_mf.py",
    "scripts/update_moneyflow.py",
    "scripts/update_minute_feed.py",
    "scripts/update_daily.py",
    "monitor/build_status.py",
]

# A key read inside one of these AST parents is a DECISION (the writer's next run branches
# on it); anything else is an echo into the next face.
DECISION_PARENTS = (ast.If, ast.While, ast.Assert, ast.IfExp, ast.BoolOp)

# Reader tiers.  `monitor/build_status.py` renders the face for a human; the ~40
# `Tools/_r<N>*_merge|rebase|close*` scripts open it once inside a conflict resolution and
# never look at it again.  Neither is a consumer at decision time, so the classes split.
DISPLAY_READERS = {"monitor/build_status.py"}
ONEOFF_RE = re.compile(r"(^|/)_r\d+")

# How far a value travels from the key read to the branch that tests it
# (`last = rank.get("last_spawn_attempt")` -> `age = f(last)` -> `if age < MIN_SPAWN_S`).
CARRIER_HOPS = 3

_FOLD_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
             ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
             ast.Mod: operator.mod, ast.Pow: operator.pow}
# Throttle constants are written in mixed units (`MIN_SPAWN_S = 30 * 60`,
# `THROTTLE_MIN = 20`); rank them in seconds and say when the unit was assumed.
_UNIT_FACTORS = [("_MS", 0.001), ("_MIN", 60.0), ("_HOUR", 3600.0), ("_HRS", 3600.0),
                 ("_SEC", 1.0), ("_S", 1.0)]


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _corpus() -> list[str]:
    out = []
    for d in CORPUS_DIRS:
        base = os.path.join(ROOT, d)
        for dirpath, _dirnames, filenames in os.walk(base):
            if any(part in dirpath for part in ("__pycache__", ".git", "_quarantine")):
                continue
            for name in filenames:
                if name.endswith(".py"):
                    out.append(os.path.relpath(os.path.join(dirpath, name), ROOT).replace("\\", "/"))
    for name in CORPUS_FILES:
        if os.path.exists(os.path.join(ROOT, name)):
            out.append(name)
    return sorted(set(out))


def _face_paths(tree: ast.AST, source: str) -> list[str]:
    """String constants in the producer that name its status face."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if value.endswith(".json") and ("status" in os.path.basename(value)):
                found.append(os.path.basename(value))
    # A producer may compose the filename; fall back to a literal search.
    if not found:
        for line in source.splitlines():
            if "_status.json" in line or "status.json" in line:
                start = line.find('"')
                if start >= 0:
                    tail = line[start:].split('"')
                    if len(tail) > 1 and tail[1].endswith(".json"):
                        found.append(os.path.basename(tail[1]))
    return sorted(set(found))


def _key_accesses(tree: ast.AST, keys: set[str]) -> dict[str, list[dict]]:
    """Every access to one of `keys` in this tree, with write/read and decision context."""
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent

    result: dict[str, list[dict]] = {k: [] for k in keys}

    def _key_of(node: ast.AST) -> str | None:
        # d["key"]  /  d.get("key")
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if isinstance(node.slice.value, str) and node.slice.value in keys:
                return node.slice.value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in keys:
                return node.args[0].value
        return None

    for node in ast.walk(tree):
        key = _key_of(node)
        if key is None:
            continue
        parent = parents.get(id(node))
        is_write = isinstance(parent, ast.Assign) and parent.targets and parent.targets[0] is node
        if isinstance(parent, ast.AugAssign) and parent.target is node:
            is_write = True
        if is_write:
            result[key].append({
                "kind": "write",
                "line": getattr(node, "lineno", 0),
                "base": getattr(node.value, "id", None) if isinstance(node, ast.Subscript) else None,
            })
            continue
        # walk up: is the value consumed by a branch?  A bare comparison that does not feed
        # a branch (`print(d["x"] == 1)`) is not a decision, so keep walking past Compare.
        decision = None
        cursor = node
        for _ in range(8):
            cursor = parents.get(id(cursor))
            if cursor is None:
                break
            if isinstance(cursor, DECISION_PARENTS):
                decision = type(cursor).__name__
                break
        result[key].append({
            "kind": "read",
            "line": getattr(node, "lineno", 0),
            "in_decision": decision,
        })
    return result


def census(producers: list[str] | None = None, corpus: list[str] | None = None) -> dict:
    producers = producers if producers is not None else PRODUCERS
    corpus = corpus if corpus is not None else _corpus()

    faces: list[dict] = []
    for rel in producers:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            faces.append({"producer": rel, "present": False})
            continue
        source = _read(path)
        tree = ast.parse(source)
        face_files = _face_paths(tree, source)
        bases = _status_bases(tree)
        literal = _dict_literal_keys(tree, bases)
        literal_bases: dict[str, list[str]] = {}
        for base, bkeys in literal.items():
            for k in bkeys:
                literal_bases.setdefault(k, []).append(base)
        keys = set(literal_bases)
        for key, events in _key_accesses(tree, _all_status_keys(tree)).items():
            if any(e["kind"] == "write" and e.get("base") in bases for e in events):
                keys.add(key)
        accesses = _key_accesses(tree, keys)
        other_dict_keys = sorted({
            e.get("base") for key in _all_status_keys(tree) - keys
            for e in _key_accesses(tree, {key})[key]
            if e["kind"] == "write" and e.get("base")
        })

        # Who else names this face at all?
        face_readers: list[str] = []
        for name in face_files:
            for rel_other in corpus:
                if rel_other == rel:
                    continue
                try:
                    other = _read(os.path.join(ROOT, rel_other))
                except OSError:
                    continue
                if name in other:
                    face_readers.append(rel_other)
        face_readers = sorted(set(face_readers))

        rows = []
        consts = _module_consts(tree)
        for key in sorted(keys):
            events = accesses[key]
            writes = [e for e in events if e["kind"] == "write"]
            reads = [e for e in events if e["kind"] == "read"]
            decision_reads = [e for e in reads if e["in_decision"]]
            external = []
            for rel_other in face_readers:
                try:
                    other_tree = ast.parse(_read(os.path.join(ROOT, rel_other)))
                except (OSError, SyntaxError):
                    continue
                # A reader must ACCESS the key (`d["key"]` / `d.get("key")`), not merely
                # carry the string: the ~40 Tools/_r* conflict resolvers name the face path
                # inside a conflicted-paths list and would otherwise look like consumers.
                if key in _all_status_keys(other_tree):
                    external.append(rel_other)
            if external:
                cls = "read_by_someone"
            elif reads:
                cls = "self_fed_only"
            else:
                cls = "no_reader"
            bound = _latch_bound(tree, consts, key) if cls == "self_fed_only" else None
            latch = bool(cls == "self_fed_only" and (decision_reads or bound))
            contexts = {e["in_decision"] for e in decision_reads if e["in_decision"]}
            if latch and bound:
                contexts.add(bound["context"])
            rows.append({
                "key": key,
                "writes": len(writes) + (1 if key in literal_bases else 0),
                "write_bases": sorted({w.get("base") for w in writes if w.get("base")} | set(literal_bases.get(key, []))),
                "declared_in_literal": bool(key in literal_bases),
                "self_reads": len(reads),
                "self_decision_reads": len(decision_reads),
                "decision_contexts": sorted(contexts),
                "external_readers": external,
                "class": cls,
                "reader_tier": _reader_tier(cls, external),
                # A latch is state the writer's next run branches on.  Reading the field
                # inside the branch is one shape; carrying it through a local expression is
                # the other, and that one is invisible to a text-only rule.
                "latch": latch,
                "bound": bound,
            })
        faces.append({
            "producer": rel,
            "present": True,
            "faces": face_files,
            "face_readers": face_readers,
            "keys": len(rows),
            "rows": rows,
            "classes": _tally(rows),
            "base_origins": dict(sorted(bases.items())),
            # An empty extraction is a measurement gap, not a finding of "nothing": name it
            # instead of letting key=0 read as a clean producer (r1286 lesson).
            "extraction_empty": not rows,
            "excluded_data_column_keys": other_dict_keys[:20],
        })

    all_rows = [(f["producer"], r) for f in faces if f.get("present") for r in f["rows"]]
    latches = [{"producer": p, "key": r["key"], "contexts": r["decision_contexts"]}
               for p, r in all_rows if r["latch"]]
    face_of = {f["producer"]: f.get("faces", []) for f in faces if f.get("present")}

    # A threshold that branches on a stored value is the row where one hand-edited status
    # file changes an operational decision.  Ranked in seconds so the two units the corpus
    # uses (`_S`, `_MIN`) are comparable; the longest throttle is the quietest edit.
    bounded = [{"producer": p, "key": r["key"], "faces": face_of.get(p, []),
                "external_readers": r["external_readers"], **r["bound"]}
               for p, r in all_rows if r["latch"] and r.get("bound")]
    bounded_seconds = [b for b in bounded if b["seconds"] is not None]
    named = None
    tied = []
    if bounded_seconds:
        longest = max(b["seconds"] for b in bounded_seconds)
        tied = sorted([b for b in bounded_seconds if b["seconds"] == longest],
                      key=lambda b: (b["producer"], b["key"]))
        first = tied[0]
        named = dict(first, tied_count=len(tied),
                     tied_rows=[{"producer": b["producer"], "key": b["key"], "faces": b["faces"]}
                                for b in tied],
                     why=(
                         "a single hand-edited %s would silence %s for %ss and nothing outside the writer "
                         "reads the field, so nothing can catch it%s"
                         % (first["key"], first["producer"], int(first["seconds"]),
                            "" if len(tied) == 1 else
                            " -- and the same field with the same bound exists in %d collectors, "
                            "so the edit is available in each of them" % len(tied))))

    return {
        "study": "E346-what-a-status-writer-writes-that-nobody-reads",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "generated": EVIDENCE_CUTOFF,
        "corpus_files": len(corpus),
        "producers": faces,
        "summary": {
            "producers": len([f for f in faces if f.get("present")]),
            "keys": len(all_rows),
            "by_class": _tally([r for _p, r in all_rows]),
            # The class split says a reader exists; the tier says what kind of reader it is.
            "by_reader_tier": _tally([{"class": r["reader_tier"]} for _p, r in all_rows]),
            "tier_rule": {"live": "at least one reader that is neither the dashboard nor a one-off _r<N> resolver",
                          "display_only": "every reader is monitor/build_status.py",
                          "merge_only": "every reader is a one-off Tools/_r<N>* merge/rebase/close script",
                          "precedence": "live > display_only > merge_only"},
            "display_only_keys": sorted({r["key"] for _p, r in all_rows if r["reader_tier"] == "display_only"}),
            "live_consumer_keys": sorted({r["key"] for _p, r in all_rows if r["reader_tier"] == "live"}),
            "merge_only_keys": sorted({r["key"] for _p, r in all_rows if r["reader_tier"] == "merge_only"}),
            "unread_keys": sorted({r["key"] for _p, r in all_rows if r["class"] == "no_reader"}),
            "latches": latches,
            "latch_bounds": bounded,
            "latch_bounds_unit_assumed": sorted({b["key"] for b in bounded if b["unit_assumed"]}),
            "named_operational_row": named,
            "faces_with_no_external_reader": [
                f["producer"] for f in faces if f.get("present") and not f["face_readers"]
            ],
            "face_sizes": {f["producer"]: f.get("keys") for f in faces if f.get("present")},
        },
    }


def _status_bases(tree: ast.AST) -> dict[str, str]:
    """Names bound to a status payload, with the reason each one qualified.

    Four shapes appear in this corpus, so four rules; each row publishes which one fired
    (`base_origins`), because the population is the argument:

      call    `st = load_status()` / `st = _check_status(...)`  (call text names status)
      named   `STATUS` -- an identifier that says status
      param   a parameter of a function that calls a status writer
      passed  a name handed to a call whose function name says status (`write_status(st)`)

    The first draft also accepted every dict literal bound to a local name, which made
    `HEADERS`, `TIER` and `RANK_FIELD_MAP` status payloads and put "User-Agent" in the
    unread-key list (548 keys).  Precision over recall here: a key only counts if the
    name it is stored on can reach a status writer.
    """
    bases: dict[str, str] = {}
    writer_funcs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    fname = inner.func.id if isinstance(inner.func, ast.Name) else (
                        inner.func.attr if isinstance(inner.func, ast.Attribute) else "")
                    if "status" in fname.lower():
                        writer_funcs.add(node.name)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in writer_funcs:
                for arg in list(node.args.args) + list(node.args.kwonlyargs):
                    if arg.arg not in ("self", "cls"):
                        bases.setdefault(arg.arg, "param")
        if isinstance(node, ast.Call):
            fname = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if "status" in fname.lower():
                for arg in list(node.args) + [kw.value for kw in node.keywords]:
                    if isinstance(arg, ast.Name):
                        bases.setdefault(arg.id, "passed")
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                name = target.id
                if "status" in name.lower():
                    bases.setdefault(name, "named")
                    continue
                value = node.value
                if isinstance(value, (ast.Dict, ast.Call)):
                    try:
                        text = ast.unparse(value)
                    except Exception:  # pragma: no cover - defensive
                        continue
                    if isinstance(value, ast.Call) and "status" in text.lower():
                        bases.setdefault(name, "call")
    return bases


def _dict_literal_keys(tree: ast.AST, bases: dict[str, str]) -> dict[str, set[str]]:
    """Keys declared inline in a dict literal that is bound to a status name."""
    out: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in bases and isinstance(node.value, ast.Dict):
                keys = {k.value for k in node.value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                if keys:
                    out.setdefault(target.id, set()).update(keys)
    return out


def _all_status_keys(tree: ast.AST) -> set[str]:
    """Every string constant used as a subscript key anywhere in the producer."""
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if isinstance(node.slice.value, str):
                keys.add(node.slice.value)
    return keys


def _keys_mentioned(tree: ast.AST) -> set[str]:
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            keys.add(node.value)
    return keys


def _fold(node: ast.AST):
    """Fold a numeric constant expression.  `30 * 60` is a BinOp, not a Constant: a plain
    constant reader misses exactly the throttles that were written as arithmetic."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _FOLD_OPS:
        left, right = _fold(node.left), _fold(node.right)
        if left is not None and right is not None:
            return _FOLD_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _fold(node.operand)
        return None if inner is None else -inner
    return None


def _module_consts(tree: ast.AST) -> dict[str, float]:
    out: dict[str, float] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            value = _fold(node.value)
            if value is not None:
                out[node.targets[0].id] = value
    return out


def _name_refs(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _carriers(tree: ast.AST, key: str) -> set[str]:
    """Names whose value derives from a read of `key` (bounded single-assignment walk)."""
    names: set[str] = set()
    for _ in range(CARRIER_HOPS):
        grew = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target = node.targets[0].id
                if target in names:
                    continue
                mentions = any(isinstance(c, ast.Constant) and c.value == key for c in ast.walk(node.value))
                if mentions or (_name_refs(node.value) & names):
                    names.add(target)
                    grew = True
        if not grew:
            break
    return names


def _unit_seconds(constant: str, value: float):
    upper = constant.upper()
    for suffix, factor in _UNIT_FACTORS:
        if upper.endswith(suffix):
            return value * factor, False
    return None, True


def _latch_bound(tree: ast.AST, consts: dict[str, float], key: str) -> dict | None:
    """The numeric module constant the writer branches on for this latch, if one exists.

    Two shapes both count, because the corpus uses both:
      direct   `if st["last_attempt"] and ...`   -- the key is in the test itself
      carried  `last = st["..."]` -> `age = f(last)` -> `if age < MIN_SPAWN_S`
    The carried shape is the one whose branch text never mentions the field, so a
    text-only reader would call the field unread by its own writer.
    """
    carriers = _carriers(tree, key)
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.If, ast.While)):
            continue
        test = node.test
        direct = any(isinstance(c, ast.Constant) and c.value == key for c in ast.walk(test))
        if not (direct or (_name_refs(test) & carriers)):
            continue
        used = sorted(_name_refs(test) & set(consts))
        if used:
            hits.append((node.lineno, used, "direct" if direct else "carried", type(node).__name__))
    if not hits:
        return None
    hits.sort()
    line, used, shape, kind = hits[0]
    constant = used[0]
    seconds, assumed = _unit_seconds(constant, consts[constant])
    return {
        "constant": constant,
        "value": consts[constant],
        "unit_assumed": assumed,
        "seconds": seconds,
        "bound_line": line,
        "test_lines": [h[0] for h in hits],
        "shape": shape,
        # The branch the value is tested in.  A carried latch has no read inside the branch,
        # so without this its `decision_contexts` would be empty while it plainly decides.
        "context": kind,
    }


def _reader_tier(cls: str, external: list[str]) -> str:
    """live > display_only > merge_only, and the non-reader classes pass through."""
    if cls != "read_by_someone":
        return cls
    live = [r for r in external if r not in DISPLAY_READERS and not ONEOFF_RE.search(r)]
    if live:
        return "live"
    if any(r in DISPLAY_READERS for r in external):
        return "display_only"
    return "merge_only"


def _tally(rows: list[dict]) -> dict:
    out: dict[str, int] = {}
    for r in rows:
        out[r["class"]] = out.get(r["class"], 0) + 1
    return dict(sorted(out.items()))


def _summary_block(face: dict) -> dict:
    """The re-derivable slice `verify` compares (no paths, no timestamps)."""
    return {
        "evidence_cutoff": face["evidence_cutoff"],
        "corpus_files": face["corpus_files"],
        "summary": face["summary"],
        "producers": [
            {
                "producer": f.get("producer"),
                "present": f.get("present"),
                "faces": f.get("faces"),
                "face_readers": f.get("face_readers"),
                "keys": f.get("keys"),
                "classes": f.get("classes"),
                "base_origins": f.get("base_origins"),
                "extraction_empty": f.get("extraction_empty"),
                "rows": [
                    {k: r[k] for k in ("key", "writes", "self_reads", "self_decision_reads", "class",
                                       "reader_tier", "latch", "bound")}
                    for r in f.get("rows", [])
                ],
            }
            for f in face["producers"]
        ],
    }


def build() -> int:
    face = census()
    os.makedirs(FACE_DIR, exist_ok=True)
    out = os.path.join(FACE_DIR, FACE_NAME)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    latest = os.path.join(FACE_DIR, "unreadstatus_latest.json")
    with open(latest, "w", encoding="utf-8") as fh:
        json.dump(_summary_block(face), fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    s = face["summary"]
    print(f"E346 face written: {out}")
    print(f"producers={s['producers']} keys={s['keys']} classes={s['by_class']} latches={len(s['latches'])}")
    return 0


def verify() -> int:
    out = os.path.join(FACE_DIR, FACE_NAME)
    if not os.path.exists(out):
        print(f"E346 verify: face missing -> {out}")
        return 1
    with open(out, "r", encoding="utf-8") as fh:
        published = json.load(fh)
    fresh = _summary_block(census())
    old = _summary_block(published)
    problems = []
    if old != fresh:
        for key in ("corpus_files", "summary"):
            if old.get(key) != fresh.get(key):
                problems.append(key)
        if old.get("producers") != fresh.get("producers"):
            problems.append("producers")
    if problems:
        print(f"E346 verify: summary does not re-derive ({problems})")
        return 1
    print(f"E346 verify: {len(fresh['producers'])} producers, {fresh['summary']['keys']} keys, "
          f"latches={len(fresh['summary']['latches'])} -- 0 problems")
    return 0


def selftest() -> int:
    import tempfile

    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    tmp = tempfile.mkdtemp(prefix="e346_")
    writer = os.path.join(tmp, "writer_x.py")
    reader = os.path.join(tmp, "reader_y.py")
    with open(writer, "w", encoding="utf-8") as fh:
        fh.write(
            'import json\nSTATUS = "results/lonely_status.json"\n'
            "def go():\n"
            "    st = json.load(open(STATUS))\n"
            '    st["mode"] = "x"\n'
            '    st["latchy"] = 1\n'
            '    st["orphan"] = 2\n'
            "    if st[\"latchy\"] > 0:\n"
            "        return 1\n"
            '    print(st["mode"])\n'
            "    return 0\n"
        )
    with open(reader, "w", encoding="utf-8") as fh:
        fh.write('import json\nd = json.load(open("results/lonely_status.json"))\nprint(d["mode"])\n')

    orig_root, orig_corpus, orig_producers = ROOT, _corpus, PRODUCERS
    try:
        globals()["ROOT"] = tmp
        face = census(producers=["writer_x.py"], corpus=["writer_x.py", "reader_y.py"])
    finally:
        globals()["ROOT"] = orig_root
    rows = {r["key"]: r for r in face["producers"][0]["rows"]}

    check("face path discovered from a composed constant", face["producers"][0]["faces"] == ["lonely_status.json"],
          str(face["producers"][0]["faces"]))
    check("reader of the face names the producer's face", face["producers"][0]["face_readers"] == ["reader_y.py"],
          str(face["producers"][0]["face_readers"]))
    check("a key the external reader takes is read_by_someone", rows["mode"]["class"] == "read_by_someone",
          rows["mode"]["class"])
    check("a self-fed key used in a branch is a latch",
          rows["latchy"]["class"] == "self_fed_only" and rows["latchy"]["latch"] is True,
          f'{rows["latchy"]["class"]}/{rows["latchy"]["latch"]}')
    check("a write-only key is no_reader", rows["orphan"]["class"] == "no_reader", rows["orphan"]["class"])
    check("store is not counted as a self read", rows["orphan"]["self_reads"] == 0, str(rows["orphan"]["self_reads"]))
    check("decision context is named", rows["latchy"]["decision_contexts"] == ["If"],
          str(rows["latchy"]["decision_contexts"]))
    check("summary carries the latch list",
          [l["key"] for l in face["summary"]["latches"]] == ["latchy"], str(face["summary"]["latches"]))
    check("class tally covers all three classes",
          set(face["producers"][0]["classes"]) == {"read_by_someone", "self_fed_only", "no_reader"},
          str(face["producers"][0]["classes"]))
    check("a face with no external reader is listed",
          face["summary"]["faces_with_no_external_reader"] == [], str(face["summary"]["faces_with_no_external_reader"]))

    # second fixture: nobody reads the face at all
    tmp2 = tempfile.mkdtemp(prefix="e346b_")
    with open(os.path.join(tmp2, "solo_w.py"), "w", encoding="utf-8") as fh:
        fh.write('import json\nS = "results/solo_status.json"\nst = json.load(open(S))\nst["mode"] = "y"\n')
    try:
        globals()["ROOT"] = tmp2
        face2 = census(producers=["solo_w.py"], corpus=["solo_w.py"])
    finally:
        globals()["ROOT"] = orig_root
    check("an unread face is named",
          face2["summary"]["faces_with_no_external_reader"] == ["solo_w.py"],
          str(face2["summary"]["faces_with_no_external_reader"]))

    # third fixture: a throttle whose key never appears in the branch that tests it
    tmp3 = tempfile.mkdtemp(prefix="e346c_")
    os.makedirs(os.path.join(tmp3, "Tools"), exist_ok=True)
    os.makedirs(os.path.join(tmp3, "monitor"), exist_ok=True)
    with open(os.path.join(tmp3, "w_thr.py"), "w", encoding="utf-8") as fh:
        fh.write(
            'import json\nSTATUS = "results/throttle_status.json"\nMIN_SPAWN_S = 30 * 60\n'
            "def go(now):\n"
            "    st = json.load(open(STATUS))\n"
            '    last = st["last_attempt"]\n'
            "    age = None if not last else 7\n"
            "    if age is not None and age < MIN_SPAWN_S:\n"
            "        return 0\n"
            '    st["last_attempt"] = str(now)\n'
            '    st["mode"] = "spawn"\n'
            "    return 1\n"
        )
    with open(os.path.join(tmp3, "w_thr2.py"), "w", encoding="utf-8") as fh:
        fh.write(
            'import json\nSTATUS = "results/throttle2_status.json"\nTHROTTLE_MIN = 20\n'
            "def go(now):\n"
            "    st = json.load(open(STATUS))\n"
            '    last = st["last_ok"]\n'
            "    age = 9 if last else None\n"
            "    if age is not None and age < THROTTLE_MIN:\n"
            "        return 0\n"
            '    st["last_ok"] = str(now)\n'
            "    return 1\n"
        )
    with open(os.path.join(tmp3, "Tools", "_r999_merge_resolve.py"), "w", encoding="utf-8") as fh:
        fh.write('import json\nx = json.load(open("results/throttle2_status.json"))\nprint(x["last_ok"])\n')
    with open(os.path.join(tmp3, "monitor", "build_status.py"), "w", encoding="utf-8") as fh:
        fh.write('import json\nd = json.load(open("results/throttle_status.json"))\nprint(d["mode"])\n')
    try:
        globals()["ROOT"] = tmp3
        face3 = census(producers=["w_thr.py", "w_thr2.py"],
                       corpus=["w_thr.py", "w_thr2.py", "Tools/_r999_merge_resolve.py",
                               "monitor/build_status.py"])
    finally:
        globals()["ROOT"] = orig_root
    rows3 = {r["key"]: r for f in face3["producers"] for r in f["rows"]}
    s3 = face3["summary"]

    check("a constant written as arithmetic is folded", _fold(ast.parse("X = 30 * 60").body[0].value) == 1800.0,
          str(_fold(ast.parse("X = 30 * 60").body[0].value)))
    check("a unit suffix is priced and an unknown unit is flagged",
          _unit_seconds("MIN_SPAWN_S", 1800) == (1800.0, False) and _unit_seconds("THROTTLE", 20)[1] is True,
          str((_unit_seconds("MIN_SPAWN_S", 1800), _unit_seconds("THROTTLE", 20))))
    check("a key that never appears in the branch still resolves to its bound",
          rows3["last_attempt"]["bound"]["constant"] == "MIN_SPAWN_S",
          str(rows3["last_attempt"]["bound"]))
    check("a merge-only reader is not a consumer at decision time",
          rows3["last_ok"]["reader_tier"] == "merge_only", rows3["last_ok"]["reader_tier"])
    check("a dashboard-only reader is display_only",
          rows3["mode"]["class"] == "read_by_someone" and rows3["mode"]["reader_tier"] == "display_only",
          f'{rows3["mode"]["class"]}/{rows3["mode"]["reader_tier"]}')
    check("the named operational row is the longest throttle, in seconds",
          s3["named_operational_row"]["constant"] == "MIN_SPAWN_S"
          and s3["named_operational_row"]["seconds"] == 1800.0,
          str(s3["named_operational_row"]))
    check("the named row carries the reason a hand edit is invisible",
          "nothing outside the writer" in (s3["named_operational_row"] or {}).get("why", ""),
          str(s3["named_operational_row"]))
    check("only bounded latches are ranked",
          all(b.get("constant") for b in s3["latch_bounds"]), str(s3["latch_bounds"]))
    check("a carried latch publishes the context of the branch it decides",
          rows3["last_attempt"]["latch"] is True
          and rows3["last_attempt"]["decision_contexts"] == ["If"]
          and rows3["last_attempt"]["bound"]["shape"] == "carried",
          f'{rows3["last_attempt"]["latch"]}/{rows3["last_attempt"]["decision_contexts"]}'
          f'/{rows3["last_attempt"]["bound"]["shape"]}')
    check("the top throttle is disclosed with its ties, not silently picked",
          s3["named_operational_row"]["tied_count"] == len(s3["named_operational_row"]["tied_rows"])
          and s3["named_operational_row"]["tied_count"] >= 1,
          str(s3["named_operational_row"].get("tied_count")))

    checks.append(("GLOBALS_RESTORED", ROOT == orig_root and _corpus is orig_corpus and PRODUCERS is orig_producers, ""))

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if not ok and detail else ""))
    print(f"e346 selftest {len(checks) - len(failed)}/{len(checks)}")
    return 0 if not failed else 1


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "verify"
    if mode == "build":
        return build()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    if mode == "show":
        face = census()
        print(json.dumps(face["summary"], ensure_ascii=False, indent=2)[:4000])
        return 0
    print(f"unknown mode: {mode}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))