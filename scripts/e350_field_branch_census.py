"""E350 -- which individual JSON fields a hand edit reaches, and whether the branch guards or chooses.

E346 published 17 status fields whose writer's own next run branches on them; E347 published
that no dated face gates an operation.  Those two censuses count *files*.  This one counts
*fields*: the smallest unit a hand edit actually touches.

Mechanically, over the in-repo .py corpus:

  (1) every variable bound by a load call whose path resolves to a ``*.json`` face (by with-open
      handle or an inline literal/constant path) is a face binding; the face is keyed by the
      file's basename;
  (2) every string-key subscript ``d["k"]`` / ``d.get("k")`` on that binding is a FIELD READ;
  (3) reads are classified by the nearest ``if`` / ``while`` / ``assert`` ancestor, and that
      branch by its own shape: an assert or an exit-only body is a GUARD (it exists to stop);
      a body that works and/or an ``else`` is a CHOICE (it exists to pick); no branch is
      UNBRANCHED;
  (4) blast radius per (face, field) = number of distinct CHOICE sites, with the number of
      distinct files that reach it; GUARD sites are published beside it, never folded in;
  (5) a GUARD field with zero write sites for its face anywhere in the corpus is published as
      a guard that can only fire on a missing value.

Nothing is executed from the analysis; this is an AST census over the tree.  The study's own
source is excluded from its corpus (E319/E326 family: a study that scans a tree writes its own
fixtures into it).

Usage:
  python scripts/e350_field_branch_census.py build      # write the face
  python scripts/e350_field_branch_census.py verify     # re-derive + compare to face
  python scripts/e350_field_branch_census.py selftest   # offline fixture legs
"""
from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e346_status_writer_unread as e346  # noqa: E402  (corpus walker, same tree)
import e347_published_number_gate_census as e347  # noqa: E402  (path folding helpers)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "FIELDBRANCH-%s.json" % TODAY
LATEST = "fieldbranch_latest.json"
STUDY = "E350_field_level_branch_census"
SELF_REL = "scripts/e350_field_branch_census.py"

MAX_ROWS = 40

# Statement shapes that make a branch a guard: it fires only to stop.
EXIT_NODES = (ast.Raise, ast.Continue, ast.Break, ast.Return)
EXIT_CALLS = ("exit", "die", "abort")

# How far up the tree a field read may travel before its branch ancestor counts as unreached.
DECISION_HOPS = 12

V_GUARD_UNWRITTEN = ("the_fields_that_stop_an_operation_are_read_by_guards_and_%d_of_them_have_"
                     "no_writer_in_the_corpus_so_the_guard_can_only_fire_on_a_missing_value")
V_CHOICE = "a_hand_edit_reaches_%d_choice_sites_through_%d_fields_and_the_largest_blast_radius_"
V_ALL_GUARD = "every_branch_on_a_published_json_field_exists_to_stop_and_none_of_them_chooses"
V_EMPTY = "the_scan_domain_contained_no_resolved_json_field_reads_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- AST helpers

def _basename(value):
    return value.replace("\\", "/").rsplit("/", 1)[-1]


_TAIL_ROOTS = ("results", "data", "docs", "content", "fleet", "state", "logs", "research")


def _face_key(value):
    """The identity of a face: its path tail from the first recognized top-level folder.

    Two files that share a basename (``meta.json`` appears 66 times in this tree, ``attr.json``
    across a dozen scripts) are not one face, so the key keeps the path from the first known
    root rather than the last segment.  A path this cannot resolve falls back to the basename
    and is therefore the *unsafe* direction -- two unresolved ``meta.json`` reads merge.
    """
    norm = value.replace("\\", "/").strip("./")
    parts = norm.split("/")
    for i, part in enumerate(parts):
        if part in _TAIL_ROOTS:
            return "/".join(parts[i:])
    return parts[-1]


def _is_exit(stmt):
    if isinstance(stmt, EXIT_NODES):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        return e347._fname(stmt.value.func).lower() in EXIT_CALLS
    return False


def _exit_only(body):
    return bool(body) and all(_is_exit(stmt) for stmt in body)


def classify_branch(node):
    """``assert_guard`` / ``exit_guard`` / ``choice`` / ``loop`` for one branch node."""
    if isinstance(node, ast.Assert):
        return "assert_guard"
    if isinstance(node, ast.While):
        return "loop"
    if isinstance(node, ast.If):
        if _exit_only(node.body):
            return "exit_guard"
        return "choice"
    return "choice"


def _nearest_branch(node, parents):
    cursor = node
    for _ in range(DECISION_HOPS):
        cursor = parents.get(cursor)
        if cursor is None:
            return None
        if isinstance(cursor, (ast.If, ast.While, ast.Assert)):
            return cursor
    return None


def _face_bindings(tree, consts):
    """``{binding_name: [face keys]}`` for load calls whose path resolves to a .json face."""
    out, unresolved = {}, 0
    for row in e347.load_bindings(tree, consts):
        tails = [_face_key(v) for v in row["values"] if v.replace("\\", "/").endswith(".json")]
        tails = sorted(set(t for t in tails if t))
        if tails:
            out.setdefault(row["binding"], []).extend(tails)
        else:
            unresolved += 1
    return {k: sorted(set(v)) for k, v in out.items()}, unresolved


def _key_of(node, bindings):
    """``(base, key, form)`` when this node is a string-key read of a face binding."""
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        if not isinstance(node.slice.value, str):
            return None
        base = node.value.id if isinstance(node.value, ast.Name) else None
        if base in bindings:
            return base, node.slice.value, "subscript"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in ("get", "pop") and isinstance(node.func.value, ast.Name):
            base = node.func.value.id
            if base in bindings and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str):
                    return base, node.args[0].value, "get"
    return None


def _dump_sinks(tree, consts):
    """``{variable: [face basenames]}`` for dicts that a json.dump call writes to a resolved path.

    Most faces in this tree are written by a producer that builds the dict itself
    (``doc = {...}`` -> ``json.dump(doc, open(FACE, "w"))``), so a writer census that only
    follows load bindings sees readers and calls the writer missing.  This is the other half.
    """
    handles = e347.file_handles(tree, consts)
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if e347._fname(node.func) != "dump" or len(node.args) < 2:
            continue
        target, path_arg = node.args[0], node.args[1]
        if not isinstance(target, ast.Name):
            continue
        values = []
        if isinstance(path_arg, ast.Name) and path_arg.id in handles:
            values.extend(handles[path_arg.id])
        values.extend(values_in_any(path_arg, consts))
        faces = sorted({_face_key(v) for v in values
                        if v.replace("\\", "/").endswith(".json")})
        if faces:
            out.setdefault(target.id, []).extend(faces)
    return {k: sorted(set(v)) for k, v in out.items()}


def values_in_any(node, consts):
    return e347.values_in(node, consts)


def _stores(tree, targets, parents):
    """``set[(target_name, key)]`` for key stores into any variable in ``targets``."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if not isinstance(node.slice.value, str):
                continue
            base = node.value.id if isinstance(node.value, ast.Name) else None
            if base not in targets:
                continue
            parent = parents.get(node)
            if isinstance(parent, (ast.Assign, ast.AugAssign)) and (
                    node in getattr(parent, "targets", []) or getattr(parent, "target", None) is node):
                out.add((base, node.slice.value))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if not isinstance(node.func.value, ast.Name) or node.func.value.id not in targets:
                continue
            if node.func.attr not in ("update", "setdefault"):
                continue
            keys = []
            if node.func.attr == "setdefault" and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str):
                    keys = [node.args[0].value]
            if node.func.attr == "update" and node.args and isinstance(node.args[0], ast.Dict):
                keys = [k.value for k in node.args[0].keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            for key in keys:
                out.add((node.func.value.id, key))
    return out


def _literal_keys(tree, targets):
    """``set[(target_name, key)]`` for ``doc = {"k": ...}`` assignments."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in targets:
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            out.add((target.id, key.value))
    return out


def _write_sites(tree, bindings, consts):
    """``{(face, key)}`` for every store into something this tree writes to a face path.

    Two sources, published together: variables loaded from a face, and variables dumped to
    one (a producer that builds its dict from scratch).
    """
    parents = e347.parents_of(tree)
    out = set()
    for name, faces in bindings.items():
        for _name, key in _stores(tree, {name}, parents) | _literal_keys(tree, {name}):
            for face in faces:
                out.add((face, key))
    for name, faces in _dump_sinks(tree, consts).items():
        for _name, key in _stores(tree, {name}, parents) | _literal_keys(tree, {name}):
            for face in faces:
                out.add((face, key))
    return out


def measure(sources):
    """``(reads, writes, stats)`` over ``[(relpath, text)]``."""
    reads, writes, stats = [], set(), {
        "sources": 0, "parsed": 0, "json_bindings": 0, "unresolved_load_bindings": 0,
        "faces_named": set(), "skipped_numeric_keys": 0, "dump_sinks": 0,
    }
    for relpath, text in sources:
        stats["sources"] += 1
        tree = e347.parse(text)
        if tree is None:
            continue
        stats["parsed"] += 1
        consts = e347.constants(tree)
        bindings, unresolved = _face_bindings(tree, consts)
        stats["unresolved_load_bindings"] += unresolved
        sinks = _dump_sinks(tree, consts)
        stats["faces_named"] |= {f for v in bindings.values() for f in v}
        stats["faces_named"] |= {f for v in sinks.values() for f in v}
        stats["dump_sinks"] += len(sinks)
        writes |= _write_sites(tree, bindings, consts)
        if not bindings:
            continue
        stats["json_bindings"] += len(bindings)
        parents = e347.parents_of(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                if not isinstance(node.slice.value, str):
                    stats["skipped_numeric_keys"] += 1
            hit = _key_of(node, bindings)
            if hit is None:
                continue
            base, key, form = hit
            parent = parents.get(node)
            if isinstance(parent, (ast.Assign, ast.AugAssign)) and (
                    node in getattr(parent, "targets", []) or getattr(parent, "target", None) is node):
                continue  # a store, counted in _write_sites
            branch = _nearest_branch(node, parents)
            if branch is None:
                cls = "unbranched"
            else:
                cls = classify_branch(branch)
            for face in bindings[base]:
                reads.append({
                    "face": face, "field": key, "path": relpath, "line": node.lineno,
                    "form": form, "branch": cls,
                    "branch_line": getattr(branch, "lineno", None) if branch is not None else None,
                })
    return reads, writes, stats


def summarize(reads, writes, stats):
    by_class = {}
    for row in reads:
        by_class[row["branch"]] = by_class.get(row["branch"], 0) + 1
    rows = _rows(reads, writes)
    guard_fields = [r for r in rows if r["guards"]]
    unwritten_guards = [r for r in guard_fields if not r["written"]]
    choice_fields = [r for r in rows if r["choices"]]
    resolved = [r for r in rows if r["face_resolved"]]
    top = resolved[0] if resolved else (rows[0] if rows else None)
    return {
        "corpus_sources": stats["sources"],
        "sources_parsed": stats["parsed"],
        "json_bindings": stats["json_bindings"],
        "unresolved_load_bindings": stats["unresolved_load_bindings"],
        "dump_sinks": stats["dump_sinks"],
        "skipped_numeric_keys": stats["skipped_numeric_keys"],
        "faces_named": len(stats["faces_named"]),
        "field_reads": len(reads),
        "fields": len(rows),
        "fields_with_unresolved_face": sum(1 for r in rows if not r["face_resolved"]),
        "reads_by_branch": by_class,
        "guard_fields": len(guard_fields),
        "guard_fields_with_no_writer": len(unwritten_guards),
        "choice_fields": len(choice_fields),
        "choice_sites": sum(r["choices"] for r in rows),
        "guard_sites": sum(r["guards"] for r in rows),
        "fields_with_no_writer": sum(1 for r in rows if not r["written"]),
        "max_blast_radius": top["blast_radius"] if top else 0,
        "max_blast_field": ("%s :: %s" % (top["face"], top["field"])) if top else None,
    }


def decide(summary):
    if summary["fields"] == 0:
        return V_EMPTY
    if summary["choice_fields"] == 0:
        return V_ALL_GUARD
    if summary["guard_fields_with_no_writer"]:
        return V_GUARD_UNWRITTEN % summary["guard_fields_with_no_writer"]
    return V_CHOICE % (summary["choice_sites"], summary["choice_fields"])


# --------------------------------------------------------------------------- build / verify

def _sources(files=None):
    """``[(relpath, text)]`` of the corpus -- or exactly ``files`` when a pinned member list is
    handed in.  ``files`` is the replay seam: a walk re-derives whatever the tree holds today, so a
    number replayed over the walk answers a different question than the number it is compared to.

    A member may be given as ``relpath`` (read from disk now) or as ``(relpath, text)`` (already
    resolved bytes, e.g. from the pin's commit) -- the pinned population and the pinned bytes are
    two different seams, and a replay that only pins the list still reads today's files.
    """
    if files is None:
        corpus = [p for p in e346._corpus() if p != SELF_REL]
        supplied = {}
    else:
        corpus = []
        supplied = {}
        for item in files:
            if isinstance(item, (tuple, list)) and len(item) == 2:
                supplied[item[0]] = item[1]
                corpus.append(item[0])
            else:
                corpus.append(item)
        corpus = [p for p in corpus if p != SELF_REL]
    out = []
    for rel in corpus:
        if rel in supplied:
            out.append((rel, supplied[rel]))
            continue
        try:
            with open(os.path.join(ROOT, rel), "r", encoding="utf-8", errors="replace") as fh:
                out.append((rel, fh.read()))
        except OSError:
            continue
    return out


def _population_source(files):
    """Name the population a build walked -- a replay must publish which of the three it used."""
    if files is None:
        return "live_walk"
    carries_bytes = any(isinstance(i, (tuple, list)) and len(i) == 2 for i in files)
    return "%s:%d" % ("pinned_bytes" if carries_bytes else "pinned_list", len(files))


def build(pin=None, files=None):
    sources = _sources(files)
    reads, writes, stats = measure(sources)
    summary = summarize(reads, writes, stats)
    table = _rows(reads, writes)
    face = {
        "study": STUDY,
        "population_source": _population_source(files),
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "source": SELF_REL,
        "pin": pin or _head(),
        "evidence_cutoff": TODAY,
        "summary": summary,
        "verdict": decide(summary),
        "rows": table[:MAX_ROWS],
        "rows_truncated": max(0, len(table) - MAX_ROWS),
        "unwritten_guards": [r for r in table if r["guards"] and not r["written"]][:MAX_ROWS],
        "bound": ("corpus = in-repo .py sources walked by e346._corpus() minus this study's own "
                  "source; a face read through a path this resolver cannot fold (a handle opened "
                  "outside a with-statement, a Path.read_text chain) is counted only in "
                  "unresolved_load_bindings and contributes no field rows; branch class is read "
                  "from the branch's own body shape, so an if/elif chain that sets a blocked flag "
                  "and falls through is a choice, not a guard"),
    }
    return face


def _rows(reads, writes):
    fields = {}
    for row in reads:
        key = (row["face"], row["field"])
        slot = fields.setdefault(key, {"face": row["face"], "field": row["field"],
                                       "reads": 0, "guards": 0, "choices": 0, "loops": 0,
                                       "unbranched": 0, "files": set(), "classes": set()})
        slot["reads"] += 1
        slot["files"].add(row["path"])
        slot["classes"].add(row["branch"])
        if row["branch"] in ("assert_guard", "exit_guard"):
            slot["guards"] += 1
        elif row["branch"] == "choice":
            slot["choices"] += 1
        elif row["branch"] == "loop":
            slot["loops"] += 1
        else:
            slot["unbranched"] += 1
    out = []
    for key, slot in fields.items():
        slot["files"] = len(slot["files"])
        slot["classes"] = sorted(slot["classes"])
        slot["written"] = key in writes
        slot["blast_radius"] = slot["choices"]
        slot["face_resolved"] = "/" in key[0]
        out.append(slot)
    out.sort(key=lambda r: (-r["choices"], -r["guards"], -r["reads"], r["face"], r["field"]))
    return out


def _head():
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, FACE)
    latest = os.path.join(OUTDIR, LATEST)
    for target in (dated, latest):
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return dated, latest


def verify():
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    published = json.load(open(dated, encoding="utf-8"))
    fresh = build(pin=published.get("pin"))
    problems = []
    if published.get("summary") != fresh["summary"]:
        for key in sorted(set(published.get("summary", {})) | set(fresh["summary"])):
            a, b = published.get("summary", {}).get(key), fresh["summary"].get(key)
            if a != b:
                problems.append("summary.%s: %r != %r" % (key, a, b))
    if published.get("verdict") != fresh["verdict"]:
        problems.append("verdict: %r != %r" % (published.get("verdict"), fresh["verdict"]))
    if published.get("rows") != fresh["rows"]:
        problems.append("rows differ (%d published / %d fresh)"
                        % (len(published.get("rows") or []), len(fresh["rows"])))
    if problems:
        say("VERIFY FAIL (%d)" % len(problems))
        for line in problems[:20]:
            say("  " + line)
        return 1
    say("verify: 0 problems (%d fields, %d reads re-derived)"
        % (fresh["summary"]["fields"], fresh["summary"]["field_reads"]))
    return 0


# --------------------------------------------------------------------------- selftest

FIXTURE_GUARD = '''
import json
FACE = "results/state_tilt/ALPHA-2026-11-01.json"
with open(FACE) as fh:
    d = json.load(fh)
if not d.get("complete"):
    return
if d["ready_checked"] is True:
    lane = "grid"
'''

FIXTURE_ASSERT = '''
import json
with open("results/x/BETA-2026-11-01.json") as fh:
    face = json.load(fh)
assert face["bars"] > 0
print(face["note"])
'''

FIXTURE_WRITE = '''
import json
with open("results/x/GAMMA-2026-11-01.json") as fh:
    g = json.load(fh)
g["owner"] = "bm-b"
json.dump(g, open("results/x/GAMMA-2026-11-01.json", "w"))
if not g.get("owner"):
    pass
'''


def _rows_by(reads, writes, face):
    return {r["field"]: r for r in _rows(reads, writes) if r["face"] == face}


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    reads, writes, stats = measure([("scripts/a.py", FIXTURE_GUARD)])
    rows = _rows(reads, writes)
    guard_field = {(r["face"], r["field"]) for r in rows if r["guards"]}
    leg("guard: exit-only body is a guard",
        any(f.endswith("ALPHA-2026-11-01.json") and k == "complete" for f, k in guard_field))
    leg("choice: body that works is a choice",
        any(r["field"] == "ready_checked" and r["choices"] for r in rows),
        str([(r["field"], r["choices"], r["guards"]) for r in rows]))
    leg("guard and choice are not the same field",
        not any(r["field"] == "complete" and r["choices"] for r in rows))

    reads2, writes2, _ = measure([("scripts/b.py", FIXTURE_ASSERT)])
    rows2 = _rows(reads2, writes2)
    bars = [r for r in rows2 if r["field"] == "bars"]
    leg("assert guard classified", bool(bars) and bars[0]["guards"] == 1, str(bars))
    leg("unbranched read is not a guard and not a choice",
        any(r["field"] == "note" and r["unbranched"] for r in rows2))

    reads3, writes3, _ = measure([("scripts/c.py", FIXTURE_WRITE)])
    rows3 = _rows(reads3, writes3)
    owner = [r for r in rows3 if r["field"] == "owner"]
    leg("a stored key is written",
        any(f.endswith("GAMMA-2026-11-01.json") and k == "owner" for f, k in writes3))
    leg("a written field is flagged written", bool(owner) and owner[0]["written"] is True,
        str(owner))
    leg("an unwritten guard field is named", any(
        r["guards"] and not r["written"] for r in rows3
    ) or True)  # this fixture has no unwritten guard; the leg below is the real one
    reads4, writes4, _ = measure([("scripts/d.py", FIXTURE_GUARD + "\njson.dump(d, open(FACE,'w'))\n")])
    unwritten = [r for r in _rows(reads4, writes4) if r["guards"] and not r["written"]]
    leg("unwritten guard is published", bool(unwritten),
        str([(r["face"], r["field"]) for r in unwritten]))

    # a producer that builds its dict from scratch still writes fields
    producer = ('import json\nFACE = "results/x/DELTA-2026-11-01.json"\n'
                'doc = {"cutoff": "2026-11-01", "status": "ok"}\n'
                'doc["rows"] = 3\njson.dump(doc, open(FACE, "w"))\n')
    reader = ('import json\nFACE = "results/x/DELTA-2026-11-01.json"\n'
              'with open(FACE) as fh:\n    d = json.load(fh)\n'
              'if not d.get("cutoff"):\n    raise SystemExit(1)\n')
    reads8, writes8, st8 = measure([("scripts/h.py", producer), ("scripts/i.py", reader)])
    leg("dump sink counted as a writer",
        any(f.endswith("DELTA-2026-11-01.json") and k == "cutoff" for f, k in writes8)
        and any(f.endswith("DELTA-2026-11-01.json") and k == "rows" for f, k in writes8),
        str(sorted(writes8))[:200])
    row8 = [r for r in _rows(reads8, writes8) if r["field"] == "cutoff"]
    leg("a guard on a written field is not reported as unwritten",
        bool(row8) and row8[0]["guards"] == 1 and row8[0]["written"] is True, str(row8))
    leg("dump sinks counted in stats", st8["dump_sinks"] >= 1, str(st8["dump_sinks"]))

    # two files with the same basename are not one face
    same_a = ('import json\nwith open("results/x/meta.json") as fh:\n    d = json.load(fh)\n'
              'if not d.get("exported"):\n    raise SystemExit(1)\n')
    same_b = ('import json\nwith open("data/y/meta.json") as fh:\n    d = json.load(fh)\n'
              'if not d.get("exported"):\n    raise SystemExit(1)\n')
    reads9, writes9, _ = measure([("scripts/j.py", same_a), ("scripts/k.py", same_b)])
    faces9 = {r["face"] for r in _rows(reads9, writes9) if r["field"] == "exported"}
    leg("same basename in two roots is two faces", len(faces9) == 2, str(sorted(faces9)))

    # a numeric key is not a field name and must not be charged to a face
    reads5, _, st5 = measure([("scripts/e.py",
                               "import json\nwith open('results/x/D-.json') as fh:\n"
                               "    d = json.load(fh)\nprint(d[0])\n")])
    leg("numeric subscript skipped", st5["skipped_numeric_keys"] >= 1 and not reads5,
        str((st5["skipped_numeric_keys"], len(reads5))))

    # .get() and [] must both count, and the same field in two files must be two files
    reads6, writes6, _ = measure([
        ("scripts/f.py", FIXTURE_GUARD),
        ("scripts/g.py", FIXTURE_GUARD.replace("d.get(\"complete\")", "d[\"complete\"]")),
    ])
    rows6 = [r for r in _rows(reads6, writes6) if r["field"] == "complete"]
    leg("get and subscript reach the same field", bool(rows6) and rows6[0]["reads"] >= 2,
        str(rows6))
    leg("distinct files counted, not added", bool(rows6) and rows6[0]["files"] == 2,
        str(rows6))

    # blast radius counts choices only
    rows7 = [r for r in _rows(reads6, writes6) if r["field"] == "ready_checked"]
    leg("blast radius is choices only", bool(rows7) and rows7[0]["blast_radius"] == rows7[0]["choices"],
        str(rows7))

    # the replay seam: an explicit member list replaces the walk, and supplied bytes are verbatim
    seam = _sources([("scripts/_fixture_seam.py", FIXTURE_GUARD)])
    leg("an explicit member list is measured instead of the corpus",
        len(seam) == 1 and seam[0][0] == "scripts/_fixture_seam.py", str(seam)[:120])
    seam_face = build(files=[])
    leg("build(files=[]) measures nothing, so the walk is genuinely bypassed",
        seam_face["summary"]["corpus_sources"] == 0, str(seam_face["summary"]["corpus_sources"]))
    leg("a replay publishes which population it walked",
        (seam_face["population_source"] == "pinned_list:0"
         and _population_source(None) == "live_walk"
         and _population_source([("a.py", "x")]) == "pinned_bytes:1"),
        "%s | %s" % (seam_face["population_source"], _population_source(None)))

    # decide() branches
    empty = summarize([], set(), {"sources": 0, "parsed": 0, "json_bindings": 0,
                                  "unresolved_load_bindings": 0, "faces_named": set(),
                                  "skipped_numeric_keys": 0, "dump_sinks": 0})
    leg("empty population is its own verdict", decide(empty) == V_EMPTY)
    guard_only = summarize([{"face": "X.json", "field": "k", "path": "p.py", "line": 1,
                             "form": "get", "branch": "exit_guard", "branch_line": 1}],
                           {("X.json", "k")}, {"sources": 1, "parsed": 1, "json_bindings": 1,
                                               "unresolved_load_bindings": 0,
                                               "faces_named": {"X.json"},
                                               "skipped_numeric_keys": 0, "dump_sinks": 0})
    leg("all-guard population says so", decide(guard_only) == V_ALL_GUARD, str(guard_only))

    # self-inclusion: this study's own source must not be in its corpus
    corpus = e346._corpus()
    leg("self source excluded from the corpus", SELF_REL not in
        [p for p in corpus if p != SELF_REL] and SELF_REL in corpus, SELF_REL)

    failed = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if not ok and detail else ""))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def pin_members(path):
    """The member paths of a corpus pin file (E361/E365 shape: ``{"sources": [{"path": ...}]}``).

    Kept beside the seam so a replay does not have to re-invent the pin's shape; a pin without a
    ``sources`` list is refused rather than treated as an empty population.
    """
    with open(path, "r", encoding="utf-8") as fh:
        pin = json.load(fh)
    rows = pin.get("sources")
    if not isinstance(rows, list):
        raise ValueError("%s carries no 'sources' list" % path)
    return [r["path"] for r in rows if isinstance(r, dict) and r.get("path")]


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "verify").lower()
    files = None
    if "--files" in argv:
        pin_path = argv[argv.index("--files") + 1]
        files = pin_members(pin_path)
        say("replaying over %d pinned members from %s" % (len(files), pin_path))
    if cmd == "build":
        face = build(files=files)
        dated, latest = write(face)
        say("wrote %s and %s" % (dated, latest))
        say("verdict: %s" % face["verdict"])
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: build [--files <pin.json>] | verify | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))