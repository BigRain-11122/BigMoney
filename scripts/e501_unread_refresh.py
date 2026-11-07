"""E501 (r1528 bm-b) -- is the unread face still being refreshed, or is it a leftover?

E495 published 8 faces that a producer writes and no consumer reads (2,781,043 B).  "Nobody
reads it" and "nothing refreshes it" are different sentences: only the second one makes a
face retirable without breaking a producer's work.  This study prices the second sentence
for each of the 8 faces, statically, with no network and nothing mutated.

Three arms per face:

  A. writer reachability -- can the writing function be reached from its own module entry
     (``if __name__ == '__main__'`` body or a module-level dispatch table)?  A writer that
     only exists as an importable helper cannot refresh anything on its own.
  B. callers in the tree -- who names that module, and *how*?  A chain step that runs
     ``... e443_bare_call_resolve.py check`` executes the script but never writes the face;
     an importer that calls ``mod.write_face()`` does write it; a report line does neither.
     Lumping those three together would be the same mistake as calling a face "unread"
     because a harness touched it.
  C. payload age from the payload itself -- ``generated`` / ``evidence_cutoff`` read out of
     the face, not ``st_mtime``: this tree materialises every file at checkout (E453), so an
     mtime age is a floor, not evidence.  The floor is measured and published alongside.

The verdict is computed by a gate from the summary counts, never written by hand.
"""

import ast
import datetime
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

FACE_NAME = "unreadrefresh_latest.json"
DATED_PREFIX = "UNREADREFRESH"
DATE_STAMP = "2026-11-07"
CARD = "E501-WHICH-OF-THE-EIGHT-WRITTEN-BUT-UNREAD-FACES-IS-STILL-BEING-REFRESHED"
STUDY = "E501_unreadrefresh"
POPULATION_SOURCE = "results/state_tilt/doctorpub_latest.json (E495) rows whose reader_class is C_NONE"
SELF_EXCLUDED = ("e501_", "run_e501", "_e501")

# arm A -- writer reachability
W_ENTRY = "the_writing_function_is_reachable_from_its_own_module_entry"
W_NOT_VISIBLE = "no_function_in_the_module_visibly_names_the_face_and_writes"
W_IMPORT_ONLY = "the_module_defines_a_writer_but_no_entry_path_reaches_it"
W_ABSENT = "the_writer_source_is_absent_or_does_not_parse"
WRITER_VOCAB = (W_ENTRY, W_NOT_VISIBLE, W_IMPORT_ONLY, W_ABSENT)

# arm B -- how the tree names that module
K_RUN = "a_file_launches_the_module_as_a_command_in_a_writing_mode"
K_IMPORT_WRITER = "another_module_imports_it_and_calls_the_function_that_writes_the_face"
K_CHECK_ONLY = "every_command_site_asks_for_a_read_only_mode_so_the_face_is_never_rewritten"
K_IMPORT_OTHER = "another_module_imports_it_but_never_calls_the_writer"
K_REPORT = "only_reports_and_ledgers_mention_the_name_and_they_call_nothing"
K_NONE = "no_other_file_in_the_scan_names_the_module_at_all"
CALLER_VOCAB = (K_RUN, K_IMPORT_WRITER, K_CHECK_ONLY, K_IMPORT_OTHER, K_REPORT, K_NONE)
CALLER_RANK = {klass: i for i, klass in enumerate(CALLER_VOCAB)}
REFRESH_KINDS = (K_RUN, K_IMPORT_WRITER)
READ_ONLY_MODES = ("check", "verify", "selftest", "status", "probe", "scan", "doctor")

# per-face verdict
F_LIVE = "a_writing_mode_caller_still_reaches_the_writer_so_the_face_is_live"
F_PINNED = "no_writing_mode_caller_exists_but_a_read_only_chain_step_requires_the_face"
F_UNCALLED = "the_writer_is_reachable_only_by_hand_and_nothing_in_the_tree_names_it"
F_LEFT = "no_entry_path_reaches_the_writer_so_the_face_is_a_leftover"
F_UNMEASURABLE = "the_writer_source_cannot_be_read_so_refresh_cannot_be_priced"
FACE_VOCAB = (F_LIVE, F_PINNED, F_UNCALLED, F_LEFT, F_UNMEASURABLE)

# study verdict
V_LIVE = ("at_least_one_unread_face_is_rewritten_by_a_writing_mode_path_and_the_rest_split_"
          "between_chain_pinned_and_writer_free")
V_NONE_LIVE = ("no_unread_face_has_a_writing_mode_caller_and_the_population_is_held_only_by_"
               "read_only_chain_steps_or_a_hand_run")
V_LEFTOVER = ("every_unread_face_either_has_no_entry_path_to_its_writer_or_is_named_by_nothing_"
              "so_the_population_is_retirable")
V_EMPTY = "no_unread_face_was_found_in_the_parent_face"
VERDICT_VOCAB = (V_LIVE, V_NONE_LIVE, V_LEFTOVER, V_EMPTY)

SCAN_DIRS = ("scripts", "Tools", "docs", "research")
SCAN_ROOT_FILES = ("README.md", "PLAN.md", "HANDOVER.md", "HQ-FEEDBACK.md", "CODELY.md")
CALLER_SUFFIXES = (".py", ".ps1", ".cmd", ".bat", ".md")
LAUNCHER_MARKERS = ("subprocess", "os.system", "Start-Process", "Popen", "&&", "python scripts/")


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _rel(path, root=None):
    root = root or ROOT
    return os.path.relpath(path, root).replace("\\", "/")


def _read_text(path):
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _parse(path):
    try:
        return ast.parse(_read_text(path))
    except SyntaxError:
        return None


# ---------------------------------------------------------------- arm A: reachability

def entry_functions(tree):
    """Names the module invokes as an entry: ``__main__`` body calls and dispatch tables."""
    entries = set()
    for node in tree.body:
        if isinstance(node, ast.If) and "__main__" in ast.dump(node.test):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                    entries.add(sub.func.id)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for value in node.value.values:
                if isinstance(value, ast.Name):
                    entries.add(value.id)
    return entries


def call_graph(tree):
    graph = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            called = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                    called.add(sub.func.id)
                elif isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                    called.add(sub.func.attr)
            graph[node.name] = called
    return graph


def reachable_from_entries(tree, depth=8):
    starts = entry_functions(tree)
    graph = call_graph(tree)
    seen = set()
    frontier = list(starts)
    for _ in range(depth):
        nxt = []
        for name in frontier:
            if name in seen:
                continue
            seen.add(name)
            for callee in graph.get(name, ()):  # only functions this module defines
                if callee in graph and callee not in seen:
                    nxt.append(callee)
        frontier = nxt
        if not frontier:
            break
    return seen, graph, starts


def enclosing_functions(tree):
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append((node.lineno, getattr(node, "end_lineno", node.lineno) or node.lineno,
                          node.name))
    return funcs


def function_at(funcs, lineno):
    best = None
    for start, end, name in funcs:
        if start <= lineno <= end:
            if best is None or start > best[0]:
                best = (start, name)
    return best[1] if best else None


def _writes_in(node):
    """Does this function body contain a write-style opener or a serialiser call?"""
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
        if name in ("write_text", "write_bytes", "dump", "write"):
            return True
        if name == "open":
            args = list(sub.args) + [kw.value for kw in sub.keywords]
            for arg in args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if any(ch in arg.value for ch in ("w", "a", "x", "+")):
                        return True
    return False


def module_writer_functions(tree, face_basename):
    """Functions connected to this face: a namer that opens for write, or calls one.

    A generic write-opener in the module (a cache helper, a temp-file helper) is *not* a
    writer of this face: an importer calling it does not rewrite the published file.  Only
    a function that both names the face and opens for write -- or a caller of such a
    function -- counts.
    """
    constants = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str) and node.value.value == face_basename:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        constants.add(target.id)
    defs = {}
    nodes = {}
    namers = set()
    openers = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        nodes[node.name] = node
        called = set()
        names_face = False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name):
                    called.add(sub.func.id)
                elif isinstance(sub.func, ast.Attribute):
                    called.add(sub.func.attr)
            if isinstance(sub, ast.Constant) and sub.value == face_basename:
                names_face = True
            if isinstance(sub, ast.Name) and sub.id in constants:
                names_face = True
        defs[node.name] = called
        if names_face:
            namers.add(node.name)
        if _writes_in(node):
            openers.add(node.name)
    # a writer is an opener that names the face itself, or an opener a namer hands the face
    # name to (write_face(os.path.join(OUTDIR, FACE_NAME), face)) -- not any module opener.
    writers = set(namers & openers)
    for namer in namers:
        node = nodes.get(namer)
        if node is None:
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            callee = sub.func.id if isinstance(sub.func, ast.Name) else getattr(sub.func, "attr", "")
            if callee not in openers:
                continue
            arg_names = set()
            for arg in list(sub.args) + [kw.value for kw in sub.keywords]:
                for inner in ast.walk(arg):
                    if isinstance(inner, ast.Name):
                        arg_names.add(inner.id)
                    if isinstance(inner, ast.Constant) and inner.value == face_basename:
                        arg_names.add(face_basename)
            if arg_names & (constants | {face_basename}):
                writers.add(callee)
    # which functions, when called, end up writing? (local call closure)
    reaching = set(writers)
    changed = True
    while changed:
        changed = False
        for name, called in defs.items():
            if name in reaching:
                continue
            if called & reaching:
                reaching.add(name)
                changed = True
    return sorted(writers), sorted(constants), sorted(reaching)


def measure_reachability(source_rel, face_basename, hint_lines, root=None):
    root = root or ROOT
    path = os.path.join(root, source_rel.replace("/", os.sep))
    if not os.path.exists(path):
        return {"source": source_rel, "class": W_ABSENT, "note": "source_missing",
                "writer_functions": [], "reached_functions": []}
    tree = _parse(path)
    if tree is None:
        return {"source": source_rel, "class": W_ABSENT, "note": "source_does_not_parse",
                "writer_functions": [], "reached_functions": []}
    reached, graph, starts = reachable_from_entries(tree)
    funcs = enclosing_functions(tree)
    writers, constants, reaching = module_writer_functions(tree, face_basename)
    hinted = sorted({function_at(funcs, ln) for ln in hint_lines
                     if function_at(funcs, ln) is not None})
    candidates = sorted(set(writers) | set(hinted))
    hit = [name for name in candidates if name in reached]
    if not candidates:
        klass = W_NOT_VISIBLE
    elif hit:
        klass = W_ENTRY
    else:
        klass = W_IMPORT_ONLY
    return {"source": source_rel, "class": klass, "writer_functions": candidates,
            "writer_reaching": sorted(set(reaching) | set(hinted)),
            "reached_functions": hit, "module_entries": sorted(starts),
            "name_constants": constants,
            "note": "writers_are_openers_tied_to_the_face_name_not_every_opener_in_the_module"}


# ---------------------------------------------------------------- arm B: callers

def scan_caller_files(root=None):
    root = root or ROOT
    files = []
    for rel_dir in SCAN_DIRS:
        base = os.path.join(root, rel_dir)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
            for name in filenames:
                if name.lower().endswith(CALLER_SUFFIXES):
                    files.append(os.path.join(dirpath, name))
    for name in SCAN_ROOT_FILES:
        path = os.path.join(root, name)
        if os.path.exists(path):
            files.append(path)
    return files


def command_modes(text, stem, base):
    """Modes requested at every command site that names this module."""
    modes = []
    patterns = [
        r"scripts[\\/]" + re.escape(base) + r"[\"']?\s*,\s*[\"']([A-Za-z_-]+)[\"']",
        re.escape(base) + r"\s+([A-Za-z_-]+)\s*$",
        re.escape(stem) + r"\.py[\"']?\s*,\s*[\"']([A-Za-z_-]+)[\"']",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.M):
            modes.append(match.group(1).lower())
    return modes


def import_sites(tree, stem, writer_fns):
    """Does this module import the target, and does it call the writer function?"""
    aliases = set()
    from_import_writer = False
    imported = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == stem:
                    imported = True
                    aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "") == stem:
                imported = True
                for alias in node.names:
                    if alias.name in writer_fns:
                        from_import_writer = True
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name) and func.value.id in aliases:
                    if func.attr in writer_fns:
                        from_import_writer = True
                elif isinstance(func.value, ast.Call):
                    # e432.main(...) or imported-module factory
                    inner = func.value.func
                    if isinstance(inner, ast.Attribute) and inner.attr in writer_fns:
                        from_import_writer = True
    return imported, from_import_writer


def classify_callers(module_rel, writer_fns, files, root=None):
    """Who names this module, and does the naming site rewrite the face?"""
    root = root or ROOT
    base = os.path.basename(module_rel)
    stem = base[:-3] if base.endswith(".py") else base
    sites = []
    best = K_NONE
    for path in files:
        rel = _rel(path, root)
        if rel == module_rel:
            continue
        if os.path.basename(rel).lower().startswith(SELF_EXCLUDED):
            continue
        text = _read_text(path)
        if stem not in text and base not in text:
            continue
        low = rel.lower()
        kind = K_REPORT
        mode = None
        if low.endswith(".py"):
            tree = _parse(path)
            imported, calls_writer = (False, False)
            if tree is not None:
                imported, calls_writer = import_sites(tree, stem, set(writer_fns or ()))
            launches = any(marker in text for marker in LAUNCHER_MARKERS)
            modes = command_modes(text, stem, base) if launches else []
            writes_mode = [m for m in modes if m not in READ_ONLY_MODES]
            if writes_mode:
                kind, mode = K_RUN, writes_mode[0]
            elif modes:
                kind, mode = K_CHECK_ONLY, modes[0]
            elif calls_writer:
                kind = K_IMPORT_WRITER
            elif imported:
                kind = K_IMPORT_OTHER
            else:
                kind = K_REPORT
        elif low.endswith((".ps1", ".cmd", ".bat")):
            modes = command_modes(text, stem, base)
            writes_mode = [m for m in modes if m not in READ_ONLY_MODES]
            if writes_mode:
                kind, mode = K_RUN, writes_mode[0]
            elif modes:
                kind, mode = K_CHECK_ONLY, modes[0]
            elif "python" in text:
                kind = K_RUN
            else:
                kind = K_REPORT
        elif low.endswith(".md"):
            kind = K_REPORT
        sites.append({"source": rel, "kind": kind, "mode": mode, "names": base})
        if CALLER_RANK[kind] < CALLER_RANK[best]:
            best = kind
    return best, sites


# ---------------------------------------------------------------- arm C: payload age

def _date_of(text):
    text = (text or "").strip()
    for fmt, size in (("%Y-%m-%d", 10), ("%Y/%m/%d", 10), ("%Y%m%d", 8)):
        chunk = text[:size]
        try:
            return datetime.datetime.strptime(chunk, fmt).date()
        except ValueError:
            continue
    return None


def payload_age(face_rel, root=None, cutoff=None):
    root = root or ROOT
    path = os.path.join(root, face_rel.replace("/", os.sep))
    cutoff_date = _date_of(cutoff or DATE_STAMP)
    if not os.path.exists(path):
        return {"exists": False}
    try:
        payload = _load_json(path)
    except (ValueError, OSError):
        payload = None
    declared = None
    witness = None
    if isinstance(payload, dict):
        for key in ("generated", "ts", "evidence_cutoff", "date"):
            stamp = _date_of(str(payload.get(key, "")))
            if stamp is not None and (declared is None or stamp > declared):
                declared = stamp
        if payload.get("generated"):
            witness = "generated"
        elif payload.get("evidence_cutoff"):
            witness = "evidence_cutoff"
    age_days = None
    if declared is not None and cutoff_date is not None:
        age_days = (cutoff_date - declared).days
    return {"exists": True, "bytes": os.path.getsize(path),
            "declared_date": declared.isoformat() if declared else None,
            "witness_field": witness, "age_days": age_days,
            "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")}


def mtime_floor_days(root=None, sample=400):
    """E453: checkout materialises mtimes, so measure the floor before pricing any age."""
    root = root or ROOT
    seen = []
    for rel_dir in ("scripts", "results", "docs", "Tools"):
        base = os.path.join(root, rel_dir)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for name in filenames:
                if len(seen) >= sample:
                    break
                path = os.path.join(dirpath, name)
                try:
                    seen.append(datetime.datetime.fromtimestamp(os.path.getmtime(path)).date())
                except OSError:
                    continue
    if not seen:
        return None
    return (datetime.date.today() - min(seen)).days


def git_last_date(rel_path, root=None):
    root = root or ROOT
    try:
        out = subprocess.run(["git", "-C", root, "log", "-1", "--format=%cI", "--", rel_path],
                             capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    text = out.stdout.decode("utf-8", "replace").strip()
    return text[:10] if text else None


# ---------------------------------------------------------------- population + build

def population(root=None):
    root = root or ROOT
    face = _load_json(os.path.join(root, "results", "state_tilt", "doctorpub_latest.json"))
    rows = []
    for row in face.get("rows", []):
        if row.get("reader_class") != "nothing_in_the_scan_opens_the_file_for_read":
            continue
        sources = {}
        for key in ("constant_writers_other_than_the_harness",
                    "composed_writers_other_than_the_harness"):
            for entry in row.get(key) or []:
                source = entry.get("source")
                if not source or entry.get("role") == "a_doctor_harness":
                    continue
                sources.setdefault(source, set()).add(entry.get("line"))
        rows.append({"face": row.get("published_path"),
                     "producer_sources": sorted(sources),
                     "hint_lines": {k: sorted(v for v in vals if v) for k, vals in sources.items()},
                     "payload_from_parent": row.get("payload") or {}})
    return rows


def measure_face(row, files, root=None, cutoff=None):
    root = root or ROOT
    face_rel = row["face"]
    basename = os.path.basename(face_rel)
    reach = []
    caller_classes = {}
    caller_sites = []
    for source in row["producer_sources"]:
        hints = row["hint_lines"].get(source, [])
        item = measure_reachability(source, basename, hints, root)
        reach.append(item)
        klass, sites = classify_callers(source, item["writer_reaching"], files, root)
        caller_classes[source] = klass
        caller_sites.extend(sites)
    payload = payload_age(face_rel, root, cutoff)
    live = [item["source"] for item in reach
            if item["class"] == W_ENTRY and caller_classes.get(item["source"]) in REFRESH_KINDS]
    pinned_sources = [item["source"] for item in reach
                      if caller_classes.get(item["source"]) == K_CHECK_ONLY]
    hand = [item["source"] for item in reach if item["class"] == W_ENTRY]
    writable_any = any(item["class"] in (W_ENTRY, W_NOT_VISIBLE) for item in reach)
    if not reach or all(item["class"] == W_ABSENT for item in reach):
        face_class = F_UNMEASURABLE
    elif live:
        face_class = F_LIVE
    elif pinned_sources:
        face_class = F_PINNED
    elif writable_any and hand:
        face_class = F_UNCALLED
    else:
        face_class = F_LEFT
    return {"face": face_rel, "bytes": payload.get("bytes"),
            "producer_sources": row["producer_sources"],
            "writer_reach": reach,
            "caller_class_by_source": caller_classes,
            "caller_sites": caller_sites,
            "live_caller_sources": live,
            "chain_pinned_by_sources": pinned_sources,
            "hand_only_sources": hand,
            "payload": payload,
            "face_git_last_commit": git_last_date(face_rel, root),
            "face_class": face_class}


def summary_of(rows, meta):
    counts = {klass: 0 for klass in FACE_VOCAB}
    for row in rows:
        klass = row.get("face_class")
        counts[klass] = counts.get(klass, 0) + 1
    caller_kind_counts = {}
    for row in rows:
        for klass in (row.get("caller_class_by_source") or {}).values():
            caller_kind_counts[klass] = caller_kind_counts.get(klass, 0) + 1
    total_bytes = sum(row.get("bytes") or 0 for row in rows)

    def _bytes(cls):
        return sum((row.get("bytes") or 0) for row in rows if row.get("face_class") == cls)

    return {
        "faces": len(rows),
        "faces_live_with_a_writing_mode_caller": counts[F_LIVE],
        "faces_pinned_by_a_read_only_chain_step": counts[F_PINNED],
        "faces_reachable_only_by_hand": counts[F_UNCALLED],
        "faces_with_no_entry_path_to_the_writer": counts[F_LEFT],
        "faces_unmeasurable": counts[F_UNMEASURABLE],
        "writer_sources": sum(len(row.get("producer_sources") or []) for row in rows),
        "caller_class_counts": caller_kind_counts,
        "bytes_total": total_bytes,
        "bytes_live": _bytes(F_LIVE),
        "bytes_pinned": _bytes(F_PINNED),
        "bytes_on_faces_with_no_entry_path": _bytes(F_LEFT),
        "mtime_floor_days": meta.get("mtime_floor_days"),
        "evidence_cutoff": meta.get("evidence_cutoff"),
    }


def _verdict(summary):
    if not summary["faces"]:
        return V_EMPTY
    if summary["faces_live_with_a_writing_mode_caller"]:
        return V_LIVE
    if (summary["faces_pinned_by_a_read_only_chain_step"]
            or summary["faces_reachable_only_by_hand"]
            or summary["faces_unmeasurable"]):
        return V_NONE_LIVE
    return V_LEFTOVER


def build(root=None, write=True):
    root = root or ROOT
    files = scan_caller_files(root)
    rows = [measure_face(row, files, root, DATE_STAMP) for row in population(root)]
    meta = {"mtime_floor_days": mtime_floor_days(root), "evidence_cutoff": DATE_STAMP}
    summary = summary_of(rows, meta)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("For each of E495's 8 written-but-unread faces: is the writer still reachable "
                  "and still rewritten by a writing-mode path, or is the file a leftover?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "writer_vocab": list(WRITER_VOCAB),
        "caller_vocab": list(CALLER_VOCAB),
        "read_only_modes": list(READ_ONLY_MODES),
        "face_vocab": list(FACE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "writer reachability is static: entry = __main__ body or a module-level dispatch dict",
            "the caller scan covers scripts/, Tools/, docs/, research/ and five root documents; "
            "results/ is excluded because a published face naming a study is not a caller",
            "a command site whose mode is check/verify/selftest/status/probe/scan is graded "
            "read-only even though it launches the script",
            "payload age uses the face's own generated/evidence_cutoff field, not st_mtime "
            "(E453 mtime floor is published next to it)",
            "caller kinds are ranked per source: a writing-mode launch outranks an importer that "
            "calls the writer, which outranks a read-only chain step, which outranks a report",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "rows": rows,
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


def row_problems(face):
    """Gate: the published verdict and summary must re-derive from the rows."""
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    meta = {"mtime_floor_days": summary.get("mtime_floor_days"),
            "evidence_cutoff": summary.get("evidence_cutoff")}
    fresh = summary_of(rows, meta)
    for key, value in fresh.items():
        if summary.get(key) != value:
            problems.append("summary.%s=%r does not re-derive from the rows (%r)"
                            % (key, summary.get(key), value))
    if face.get("verdict") != _verdict(fresh):
        problems.append("verdict=%r does not re-derive from the rows (%r)"
                        % (face.get("verdict"), _verdict(fresh)))
    for row in rows:
        klass = row.get("face_class")
        if klass not in FACE_VOCAB:
            problems.append("%s: face_class %r outside the vocabulary" % (row.get("face"), klass))
            continue
        live = row.get("live_caller_sources") or []
        pinned = row.get("chain_pinned_by_sources") or []
        hand = row.get("hand_only_sources") or []
        if klass == F_LIVE and not live:
            problems.append("%s: claimed live with no writing-mode caller" % row.get("face"))
        if klass == F_PINNED and (live or not pinned):
            problems.append("%s: claimed chain-pinned but live=%r pinned=%r"
                            % (row.get("face"), live, pinned))
        if klass == F_UNCALLED and (live or pinned or not hand):
            problems.append("%s: claimed hand-only but live=%r pinned=%r hand=%r"
                            % (row.get("face"), live, pinned, hand))
        if klass == F_LEFT and (hand or live):
            problems.append("%s: claimed leftover yet a writer is entry-reachable"
                            % row.get("face"))
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

ENTRY_FIXTURE = '''import io, json, os
OUTDIR = "results/state_tilt"
FACE_NAME = "alpha_latest.json"
def write_face(path, payload):
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
def build():
    write_face(os.path.join(OUTDIR, FACE_NAME), {"generated": "2026-11-06"})
def main():
    build()
if __name__ == "__main__":
    main()
'''

DISPATCH_FIXTURE = '''import io, json, os
FACE_NAME = "beta_latest.json"
def build():
    with io.open(FACE_NAME, "w", encoding="utf-8") as fh:
        json.dump({"generated": "2026-11-01"}, fh)
MODES = {"run": build}
if __name__ == "__main__":
    MODES["run"]()
'''

IMPORT_ONLY_FIXTURE = '''import io, json, os
FACE_NAME = "gamma_latest.json"
def build():
    with io.open(FACE_NAME, "w", encoding="utf-8") as fh:
        json.dump({"generated": "2026-10-01"}, fh)
'''

CHAIN_RUN_FIXTURE = '''import subprocess
STEPS = [("delta", ["python", "scripts/delta_builder.py", "run"])]
def main():
    subprocess.run(STEPS[0][1], capture_output=True)
if __name__ == "__main__":
    main()
'''

CHAIN_CHECK_FIXTURE = '''import subprocess
STEPS = [("delta", ["python", "scripts/delta_builder.py", "check"])]
def main():
    subprocess.run(STEPS[0][1], capture_output=True)
if __name__ == "__main__":
    main()
'''

IMPORT_WRITER_FIXTURE = '''import delta_builder
def main():
    delta_builder.build()
if __name__ == "__main__":
    main()
'''

IMPORT_OTHER_FIXTURE = '''import delta_builder
CONST = delta_builder.FACE_NAME
def main():
    print(CONST)
if __name__ == "__main__":
    main()
'''

REPORT_FIXTURE = '''# round report
the study scripts/delta_builder.py published a face today
'''


def _fixture_tree(tmp):
    os.makedirs(os.path.join(tmp, "scripts"))
    os.makedirs(os.path.join(tmp, "docs"))
    files = {
        "scripts/alpha_builder.py": ENTRY_FIXTURE,
        "scripts/beta_builder.py": DISPATCH_FIXTURE,
        "scripts/gamma_builder.py": IMPORT_ONLY_FIXTURE,
        "scripts/delta_builder.py": ENTRY_FIXTURE,
        "docs/report.md": REPORT_FIXTURE,
    }
    for rel, text in files.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return files


def _tmp_with(prefix, files):
    import tempfile
    tmp = tempfile.mkdtemp(prefix=prefix)
    for rel, text in files.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return tmp


def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, note = fn()
        except Exception as exc:  # noqa: BLE001 - a failing leg must not abort the suite
            ok, note = False, "raised %r" % (exc,)
        legs.append((name, ok, note))

    tmp = _tmp_with("e501_", {"scripts/alpha_builder.py": ENTRY_FIXTURE,
                              "scripts/beta_builder.py": DISPATCH_FIXTURE,
                              "scripts/gamma_builder.py": IMPORT_ONLY_FIXTURE,
                              "scripts/delta_builder.py": ENTRY_FIXTURE,
                              "docs/report.md": REPORT_FIXTURE})

    def leg_entry_reachable():
        got = measure_reachability("scripts/alpha_builder.py", "alpha_latest.json", [], tmp)
        return (got["class"] == W_ENTRY and got["reached_functions"],
                "class=%s reached=%r" % (got["class"], got["reached_functions"]))

    def leg_dispatch_reachable():
        got = measure_reachability("scripts/beta_builder.py", "beta_latest.json", [], tmp)
        return (got["class"] == W_ENTRY, "class=%s" % got["class"])

    def leg_import_only():
        got = measure_reachability("scripts/gamma_builder.py", "gamma_latest.json", [], tmp)
        return (got["class"] == W_IMPORT_ONLY, "class=%s" % got["class"])

    def leg_absent_source():
        got = measure_reachability("scripts/missing.py", "x_latest.json", [], tmp)
        return (got["class"] == W_ABSENT, "class=%s" % got["class"])

    def leg_chain_run_is_writing_mode():
        base = {"scripts/delta_builder.py": ENTRY_FIXTURE,
                "scripts/chain.py": CHAIN_RUN_FIXTURE}
        t = _tmp_with("e501cr_", base)
        klass, sites = classify_callers("scripts/delta_builder.py", ["write_face", "build"],
                                        scan_caller_files(t), t)
        return (klass == K_RUN, "kind=%s sites=%r" % (klass, [s["source"] for s in sites]))

    def leg_chain_check_is_read_only():
        base = {"scripts/delta_builder.py": ENTRY_FIXTURE,
                "scripts/chain.py": CHAIN_CHECK_FIXTURE}
        t = _tmp_with("e501cc_", base)
        klass, sites = classify_callers("scripts/delta_builder.py", ["write_face", "build"],
                                        scan_caller_files(t), t)
        return (klass == K_CHECK_ONLY,
                "kind=%s modes=%r" % (klass, [s.get("mode") for s in sites]))

    def leg_import_writer():
        base = {"scripts/delta_builder.py": ENTRY_FIXTURE,
                "scripts/user.py": IMPORT_WRITER_FIXTURE}
        t = _tmp_with("e501iw_", base)
        klass, _ = classify_callers("scripts/delta_builder.py", ["build"],
                                    scan_caller_files(t), t)
        return (klass == K_IMPORT_WRITER, "kind=%s" % klass)

    def leg_import_other():
        base = {"scripts/delta_builder.py": ENTRY_FIXTURE,
                "scripts/user.py": IMPORT_OTHER_FIXTURE}
        t = _tmp_with("e501io_", base)
        klass, _ = classify_callers("scripts/delta_builder.py", ["build"],
                                    scan_caller_files(t), t)
        return (klass == K_IMPORT_OTHER, "kind=%s" % klass)

    def leg_report_is_not_a_path():
        t = _tmp_with("e501r_", {"scripts/delta_builder.py": ENTRY_FIXTURE,
                                 "docs/report.md": REPORT_FIXTURE})
        klass, _ = classify_callers("scripts/delta_builder.py", ["build"],
                                    scan_caller_files(t), t)
        return (klass == K_REPORT, "kind=%s" % klass)

    def leg_payload_age_from_declared_date():
        t = _tmp_with("e501p_", {"results/state_tilt/x_latest.json":
                                 json.dumps({"generated": "2026-11-01"})})
        got = payload_age("results/state_tilt/x_latest.json", t, "2026-11-07")
        return (got["age_days"] == 6 and got["witness_field"] == "generated",
                "age=%r witness=%r" % (got.get("age_days"), got.get("witness_field")))

    def leg_verdict_live():
        rows = [{"face_class": F_LIVE}, {"face_class": F_LEFT}]
        summary = summary_of(rows, {"evidence_cutoff": DATE_STAMP})
        return (_verdict(summary) == V_LIVE, "verdict=%s" % _verdict(summary))

    def leg_verdict_pinned_is_not_leftover():
        rows = [{"face_class": F_PINNED}]
        summary = summary_of(rows, {"evidence_cutoff": DATE_STAMP})
        return (_verdict(summary) == V_NONE_LIVE, "verdict=%s" % _verdict(summary))

    def leg_verdict_leftover():
        rows = [{"face_class": F_LEFT}]
        summary = summary_of(rows, {"evidence_cutoff": DATE_STAMP})
        return (_verdict(summary) == V_LEFTOVER, "verdict=%s" % _verdict(summary))

    def leg_verdict_empty():
        summary = summary_of([], {"evidence_cutoff": DATE_STAMP})
        return (_verdict(summary) == V_EMPTY, "verdict=%s" % _verdict(summary))

    def leg_gate_catches_hidden_summary():
        face = {"rows": [{"face": "x", "face_class": F_LEFT, "live_caller_sources": [],
                          "chain_pinned_by_sources": [], "hand_only_sources": []}],
                "summary": {"faces_live_with_a_writing_mode_caller": 7},
                "verdict": V_LIVE}
        problems = row_problems(face)
        return (any("does not re-derive" in p for p in problems), "problems=%r" % (problems,))

    def leg_gate_catches_live_without_caller():
        face = {"rows": [{"face": "x", "face_class": F_LIVE, "live_caller_sources": [],
                          "chain_pinned_by_sources": [], "hand_only_sources": []}],
                "summary": summary_of([{"face_class": F_LIVE}],
                                      {"evidence_cutoff": DATE_STAMP}),
                "verdict": V_LIVE}
        problems = row_problems(face)
        return (any("no writing-mode caller" in p for p in problems),
                "problems=%r" % (problems,))

    def leg_self_excluded():
        files = scan_caller_files(ROOT)
        klass, sites = classify_callers("scripts/e495_doctorpub.py", ["build"], files, ROOT)
        named_self = [s["source"] for s in sites
                      if os.path.basename(s["source"]).lower().startswith(SELF_EXCLUDED)]
        return (not named_self, "self sites=%r (scan sees %d files)" % (named_self, len(files)))

    leg("entry: __main__ reaches the writer", leg_entry_reachable)
    leg("entry: dispatch table reaches the writer", leg_dispatch_reachable)
    leg("entry: import-only module is not an entry", leg_import_only)
    leg("entry: a missing source is unmeasurable", leg_absent_source)
    leg("caller: a writing-mode chain step is live", leg_chain_run_is_writing_mode)
    leg("caller: a check-mode chain step is read-only", leg_chain_check_is_read_only)
    leg("caller: an importer that calls the writer is live", leg_import_writer)
    leg("caller: an importer of a constant is not", leg_import_other)
    leg("caller: a report mention is not a refresh path", leg_report_is_not_a_path)
    leg("payload: age comes from the declared date", leg_payload_age_from_declared_date)
    leg("verdict: live", leg_verdict_live)
    leg("verdict: chain-pinned is not a leftover", leg_verdict_pinned_is_not_leftover)
    leg("verdict: leftover", leg_verdict_leftover)
    leg("verdict: empty", leg_verdict_empty)
    leg("gate: a carried summary is caught", leg_gate_catches_hidden_summary)
    leg("gate: a live claim without a caller is caught", leg_gate_catches_live_without_caller)
    leg("scan excludes this study", leg_self_excluded)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        print("%s %s -- %s" % ("PASS" if ok else "FAIL", name, note))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"face": FACE_NAME, "rows": len(face["rows"]),
                          "verdict": face["verdict"], "summary": face["summary"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e501_unread_refresh.py [run|check|verify|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())