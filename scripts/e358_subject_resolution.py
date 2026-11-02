"""E358 -- what the 55 unnamed gate subjects are actually reading.

E351 (r1372) resolved a subject for 37 of 92 ``product:`` smoke gates and published 55 as
``unresolved_subject``.  The published bound said the 55 were out of scope, so this is the
scope, not a new question: the same corpus, one extra folding step.

The reason a gate is unresolved is mechanical, not semantic: E351 collects *string literals*
from the try body and keeps the ones that already look like a repo path
(``results/...``).  A subject written as ``os.path.join("results", "state_tilt", "x.json")``
is three literals, none of which matches, so the gate reads as "no subject" even though the
subject is a constant the parser could have folded.  This study folds:

  * all-constant ``os.path.join`` / ``str + str`` composition (depth counted per fold step);
  * one hop into a module-level or in-body string constant (``OUTDIR``, ``_p63``);
  * nothing else.  A subject built from ``_dir + _files[-1]`` (the directory's sorted last
    file) or from an f-string over a date/cutoff stays dynamic BY DESIGN -- that population
    can never be replayed from git, which is the part of E351's bound that survives.

Two things are published separately and must not be mixed:

  * ``resolved_by_folding`` -- the subject was always a constant, and E351's unresolved count
    was a parser gap.  These gates get a real state class (frozen/live/never evaluated) from
    one replay at the face's own pin, and the green-by-freeze share is recomputed;
  * ``dynamic`` -- a path expression exists but cannot be folded at parse time (variable
    directory + listing, f-string over a date).  A gate whose subject is built at runtime is
    the population that cannot be replayed from git; it is counted, never guessed.

Usage:
    python scripts/e358_subject_resolution.py build
    python scripts/e358_subject_resolution.py verify
    python scripts/e358_subject_resolution.py selftest
"""
import ast
import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e351_gate_state_census as e351  # noqa: E402

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "SUBJRES-%s.json" % TODAY
LATEST = "subjres_latest.json"
STUDY = "E358_unresolved_subject_resolution"
SELF_REL = "scripts/e358_subject_resolution.py"
SMOKE_REL = "smoke_test.py"
E351_FACE = os.path.join("results", "state_tilt", "GATESTATE-2026-11-01.json")
REPLAY_COMMITS = 300
MATURE_COMMITS = 50
PATH_ROOTS = ("results/", "data/", "docs/")
FILE_SUFFIXES = (".json", ".jsonl", ".md", ".csv", ".txt", ".parquet", ".py")
MAX_FOLD_DEPTH = 6


def say(message):
    sys.stdout.write(str(message) + "\n")


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------ folding

def local_consts(body):
    """string constants assigned inside the try body, addressable by name."""
    consts = {}
    for stmt in body:
        for node in ast.walk(stmt):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            value = node.value
            if isinstance(target, ast.Name) and isinstance(value, ast.Constant) \
                    and isinstance(value.value, str):
                consts.setdefault(target.id, value.value)
    return consts


def module_consts(tree):
    out = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            out[node.targets[0].id] = node.value.value
    return out


def fold(node, consts, modconsts, depth=0, hops=0):
    """fold a path expression to a string; return (value, depth, kind).

    ``depth`` counts folding steps actually taken (0 = a single literal, 1 = one join/plus
    over pure literals, +1 per constant hop).  Anything with a runtime part returns None with
    a reason naming the blocking shape -- the reason is published, not hidden.
    """
    if hops > MAX_FOLD_DEPTH:
        return None, depth, "fold_budget"
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return node.value, depth, "literal"
        return None, depth, "non_string_literal"
    if isinstance(node, ast.Name):
        name = node.id
        for table, kind in ((consts, "body_constant"), (modconsts, "module_constant")):
            if name in table:
                return table[name], depth + 1, kind
        return None, depth, "runtime_name:%s" % name
    if isinstance(node, ast.Call):
        func = node.func
        attr = getattr(func, "attr", None)
        base = getattr(getattr(func, "value", None), "attr", None) \
            or getattr(getattr(func, "value", None), "id", None)
        if attr == "join" and base == "path":
            parts, step = [], depth
            for arg in node.args:
                value, sub_depth, kind = fold(arg, consts, modconsts, depth, hops + 1)
                if value is None:
                    return None, max(step, sub_depth), kind
                parts.append(value)
                step = max(step, sub_depth)
            value = os.path.join(*parts) if parts else ""
            return value.replace("\\", "/"), step + 1, "join"
        return None, depth, "call:%s" % (attr or getattr(func, "id", "?"))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, dl, kl = fold(node.left, consts, modconsts, depth, hops + 1)
        right, dr, kr = fold(node.right, consts, modconsts, depth, hops + 1)
        if left is None:
            return None, max(dl, dr), kl
        if right is None:
            return None, max(dl, dr), kr
        return left + right, max(dl, dr) + 1, "concat"
    if isinstance(node, ast.JoinedStr):
        return None, depth, "fstring"
    if isinstance(node, ast.Subscript):
        return None, depth, "subscript:%s" % ast.unparse(node)[:60]
    return None, depth, "shape:%s" % type(node).__name__


def path_candidates(body, modconsts):
    """every expression in the body that could produce a path, folded or not."""
    consts = local_consts(body)
    out = []
    for stmt in body:
        for node in ast.walk(stmt):
            interesting = False
            if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "join":
                interesting = True
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                interesting = True
            elif isinstance(node, ast.JoinedStr):
                interesting = True
            if not interesting:
                continue
            value, depth, kind = fold(node, consts, modconsts)
            text = ast.unparse(node)
            if value is not None and value.startswith(PATH_ROOTS):
                out.append({"expr": text[:160], "folded": value, "depth": depth, "kind": kind,
                            "path_class": _path_class(value)})
            elif value is None and _is_path_attempt(node):
                # a path expression the parser cannot fold: published as dynamic, never guessed
                out.append({"expr": text[:160], "folded": None, "depth": depth, "kind": kind,
                            "path_class": None})
    # deduplicate by the folded value (a subject named twice is one subject)
    seen, uniq = set(), []
    for row in out:
        key = (row["folded"], row["expr"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(row)
    return uniq


def _path_class(value):
    if any(ch in value for ch in "*?["):
        return "wildcard"
    if value.endswith("/") or not value.endswith(FILE_SUFFIXES):
        return "directory"
    return "file"


def _path_shaped(text):
    return any(root in text for root in PATH_ROOTS)


def _is_os_join(node):
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    base = getattr(getattr(func, "value", None), "attr", None) \
        or getattr(getattr(func, "value", None), "id", None)
    return getattr(func, "attr", None) == "join" and base == "path"


def _is_path_attempt(node):
    """an unfolded expression that is trying to be a path -- not a message string.

    ``os.path.join(_dir, _files[-1])`` is the canonical dynamic subject (whatever the
    directory's newest file is).  ``" | " + "; ".join(_bad)`` is a message and is dropped:
    it is an Add or a join whose receiver is a literal, not ``os.path``.
    """
    if _is_os_join(node):
        return True
    if isinstance(node, ast.JoinedStr):
        return any(isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                   and any(root in sub.value for root in PATH_ROOTS)
                   for sub in ast.walk(node))
    return False


# ------------------------------------------------------------------ git replay

def blob_series(paths, commits, events, seed):
    """per-path blob at each commit index, seeded with the state BEFORE the window.

    E351 leaves a path at None until its first in-window write, so a face older than the
    window reads as ``distinct_states == 0`` and is published as ``never_evaluated`` -- the
    opposite of the truth (it is present and unchanged).  The window's base tree is read
    once and used as the starting state; a file created inside the window still starts None
    because it is not in the base tree.
    """
    tracked = {p: [seed.get(p)] * len(commits) for p in paths}
    for idx in range(len(commits)):
        for path, blob in (events.get(idx) or {}).items():
            if path in tracked:
                tracked[path][idx] = blob
    for path, seq in tracked.items():
        last = seed.get(path)
        for idx in range(len(commits)):
            if seq[idx] is None:
                seq[idx] = last
            else:
                last = seq[idx]
    return tracked


def base_tree(paths, commits, root=ROOT):
    """blob of each path in the tree the window starts from (commits[0]~1)."""
    if not paths or not commits:
        return {}
    text, rc = e351.git(["ls-tree", commits[0] + "~1", "--"] + list(paths), cwd=root)
    seed = {}
    if rc != 0:
        return seed
    for line in text.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        mode, kind, blob, path = parts
        if kind == "blob":
            seed[path] = blob
    return seed


def replay(paths, root=ROOT):
    """ONE git call over the SAME contiguous window E351 used.

    A ``-- <paths>`` filter here would answer a different question: ``git log -- path``
    lists only the commits that touched the path, so a file that changed twice would be
    graded over a two-commit "window" (the r1261 shape -- two curves equal because both
    were empty).  The window must be the repository's commits, and the path history is
    read out of it.
    """
    if not paths:
        return {}, []
    text, rc = e351.git(["log", "--no-merges", "-n", str(REPLAY_COMMITS), "--no-abbrev",
                         "--format=COMMIT %H", "--raw", "HEAD"], cwd=root)
    if rc != 0:
        return {}, []
    commits, events = e351.parse_raw_log(text)
    seed = base_tree(list(paths), commits, root)
    tracked = blob_series(list(paths), commits, events, seed)
    return tracked, commits


# ------------------------------------------------------------------ build

def gate_bodies(source):
    """gate label -> list of try bodies (a gate may be checked at several sites)."""
    tree = ast.parse(source, filename=SMOKE_REL)
    parents = e351._walk_parents(tree)
    bodies = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name != "check" or not node.args:
            continue
        first = node.args[0]
        if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
            continue
        if not first.value.startswith("product:"):
            continue
        bodies.setdefault(first.value, []).append(e351._try_body_for(node, parents))
    return tree, bodies


def dirty_paths(paths, root=ROOT):
    """folded faces whose working-tree bytes differ from HEAD -- the gate reads disk, not git.

    A subject that is frozen in git but rewritten on disk every round is not a green against
    a stale face; it is a green whose replayability is the open question.  Published, never
    assumed.
    """
    if not paths:
        return set()
    text, rc = e351.git(["status", "--porcelain", "--"] + list(paths), cwd=root)
    if rc != 0:
        return set()
    out = set()
    for line in text.splitlines():
        name = line[3:].strip()
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        out.add(name.replace("\\", "/"))
    return out


def build_face(root=ROOT):
    smoke = os.path.join(root, SMOKE_REL)
    with open(smoke, encoding="utf-8") as fh:
        source = fh.read()
    tree, bodies = gate_bodies(source)
    modconsts = module_consts(tree)

    gates = e351.collect_gates(source)
    self_prefix = "product: the product-gate state census"
    gates = [g for g in gates if self_prefix not in g["label"]]
    unresolved = [g for g in gates if not g["faces"] and not g["companions"]]

    rows = []
    all_faces = set()
    for gate in unresolved:
        cands = []
        for body in bodies.get(gate["label"], []):
            cands.extend(path_candidates(body, modconsts))
        files = [c for c in cands if c["folded"] and c["path_class"] == "file"]
        dirs = [c for c in cands if c["folded"] and c["path_class"] == "directory"]
        dyn = [c for c in cands if c["folded"] is None]
        all_faces.update(c["folded"] for c in files)
        rows.append({
            "label": gate["label"],
            "folded_files": sorted({c["folded"] for c in files}),
            "folded_dirs": sorted({c["folded"] for c in dirs}),
            "dynamic_exprs": [{"expr": c["expr"], "reason": c["kind"]} for c in dyn][:4],
            "min_depth": min((c["depth"] for c in files), default=None),
            "kinds": sorted({c["kind"] for c in files}),
        })

    tracked, commits = replay(sorted(all_faces), root)
    present = {p for p in all_faces if os.path.exists(os.path.join(root, p))}
    dirty = dirty_paths(sorted(all_faces), root)

    classes = {"frozen_subject": 0, "live_subject": 0, "never_evaluated": 0,
               "unresolved_subject": 0, "dynamic_subject": 0, "no_path_expression": 0}
    depth_hist = {}
    for row in rows:
        if row["folded_files"]:
            state = e351.gate_states({"faces": row["folded_files"], "companions": []}, tracked)
            row["class"] = e351.classify(state)
            row["distinct_states"] = state["distinct_states"]
            row["present_commits"] = state.get("present_commits", 0)
            row["window_commits"] = state.get("window_commits", 0)
            row["subject_present_on_disk"] = any(p in present for p in row["folded_files"])
            row["subject_dirty_on_disk"] = any(p in dirty for p in row["folded_files"])
            row["also_reads_a_listing"] = bool(row["dynamic_exprs"])
            depth_hist[str(row["min_depth"])] = depth_hist.get(str(row["min_depth"]), 0) + 1
        elif row["dynamic_exprs"]:
            row["class"] = "dynamic_subject"
            row["distinct_states"] = None
        else:
            row["class"] = "no_path_expression"
            row["distinct_states"] = None
        classes[row["class"]] = classes.get(row["class"], 0) + 1

    before = _before_counts(root)
    resolved = classes["frozen_subject"] + classes["live_subject"] + classes["never_evaluated"]
    with_subject_after = before["gates_with_subject"] + resolved
    frozen_after = before["frozen"] + classes["frozen_subject"]
    share_before = round(100.0 * before["frozen"] / before["gates_with_subject"], 1) \
        if before["gates_with_subject"] else None
    share_after = round(100.0 * frozen_after / with_subject_after, 1) if with_subject_after else None

    summary = {
        "e351_unresolved_published": before["unresolved"],
        "gates_measured_here": len(rows),
        "class_counts": classes,
        "resolved_by_folding": resolved,
        "resolved_mature": sum(1 for r in rows if r["class"] == "frozen_subject"
                               and (r.get("present_commits") or 0) >= MATURE_COMMITS),
        "frozen_subjects_dirty_on_disk": sum(1 for r in rows
                                             if r["class"] == "frozen_subject"
                                             and r.get("subject_dirty_on_disk")),
        "folded_files_dirty_on_disk": sorted(dirty)[:10],
        "fold_depth_histogram": depth_hist,
        "folded_files_total": len(all_faces),
        "folded_files_on_disk": len(all_faces & present),
        "folded_files_never_on_disk": sorted(all_faces - present)[:8],
        "dynamic_remainder": classes.get("dynamic_subject", 0),
        "gates_folding_and_also_listing": sum(1 for r in rows if r.get("also_reads_a_listing")),
        "no_path_expression": classes.get("no_path_expression", 0),
        "gates_with_subject_before": before["gates_with_subject"],
        "gates_with_subject_after": with_subject_after,
        "green_by_freeze_share_before_pct": share_before,
        "green_by_freeze_share_after_pct": share_after,
        "replay_commits": len(commits),
        "replay_head": (commits[-1][:8] if commits else ""),
        "dominant_blocking_shape": _dominant_reason(rows),
    }
    face = {
        "schema": "e358_subject_resolution/1",
        "study": STUDY,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generated_by": "bm-b r1380",
        "source_rel": SMOKE_REL,
        "evidence_cutoff": TODAY,
        "upstream_face": E351_FACE,
        "summary": summary,
        "rows": sorted(rows, key=lambda r: (-(r["min_depth"] or 99), r["label"])),
    }
    face["verdict"] = decide(face)
    return face


def _reason_class(kind):
    """a blocking shape that is readable on a page, not an AST node name."""
    text = str(kind)
    if text.startswith("subscript"):
        return "listing_of_a_directory"
    if text.startswith("runtime_name"):
        return "runtime_name"
    if text.startswith("call:"):
        return "call_" + text.split(":", 1)[1]
    if text.startswith("shape:"):
        return text
    return text


def _dominant_reason(rows):
    counts = {}
    for row in rows:
        for item in row["dynamic_exprs"]:
            reason = _reason_class(item["reason"])
            counts[reason] = counts.get(reason, 0) + 1
    if not counts:
        return ""
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def _before_counts(root=ROOT):
    path = os.path.join(root, E351_FACE)
    if not os.path.exists(path):
        return {"frozen": 0, "unresolved": 0, "gates_with_subject": 0}
    with open(path, encoding="utf-8") as fh:
        upstream = json.load(fh)
    summary = upstream.get("summary") or {}
    counts = summary.get("class_counts") or {}
    resolved = counts.get("frozen_subject", 0) + counts.get("live_subject", 0) \
        + counts.get("never_evaluated", 0)
    return {"frozen": counts.get("frozen_subject", 0),
            "unresolved": counts.get("unresolved_subject", 0),
            "gates_with_subject": summary.get("gates_with_subject", 0) or resolved}


def decide(face):
    s = face.get("summary") or {}
    counts = s.get("class_counts") or {}
    total = sum(counts.values())
    if total != s.get("gates_measured_here"):
        return "the class counts do not sum to the measured population, so nothing is claimed"
    resolved = s.get("resolved_by_folding") or 0
    dynamic = s.get("dynamic_remainder") or 0
    neither = s.get("no_path_expression") or 0
    if resolved == 0:
        return ("none of the %d gates E351 left unresolved names a constant subject, so "
                "unresolved was the truthful class" % total)
    if dynamic + neither == 0:
        return ("all %d gates E351 left unresolved name a constant subject, so the unresolved "
                "class was a parser gap and the green-by-freeze share moves from %s to %s pct"
                % (total, s.get("green_by_freeze_share_before_pct"),
                   s.get("green_by_freeze_share_after_pct")))
    dirty_n = s.get("frozen_subjects_dirty_on_disk") or 0
    tail = "" if not dirty_n else (
        "; %d of those frozen subjects are dirty on disk, so their committed blob is not "
        "the bytes the gate reads" % dirty_n)
    return ("%d of %d gates E351 left unresolved had a constant subject all along, %d read "
            "whatever a directory holds and %d name no file at all; the green-by-freeze share "
            "moves from %s to %s pct%s"
            % (resolved, total, dynamic, neither,
               s.get("green_by_freeze_share_before_pct"),
               s.get("green_by_freeze_share_after_pct"), tail))


# ------------------------------------------------------------------ io

def write_face(face, root=ROOT):
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir, exist_ok=True)
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE, LATEST):
        with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")


def verify(root=ROOT):
    """re-derive the face from source and compare the accounting, not the timestamps."""
    path = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(path):
        say("PROBLEM: no published face at %s" % LATEST)
        return 1
    with open(path, encoding="utf-8") as fh:
        stored = json.load(fh)
    fresh = build_face(root)
    problems = []
    if stored.get("verdict") != decide(stored):
        problems.append("the stored verdict does not re-derive from its own summary")
    if (stored.get("summary") or {}).get("class_counts") != fresh["summary"]["class_counts"]:
        problems.append("the class counts do not re-derive")
    if len(stored.get("rows") or []) != len(fresh["rows"]):
        problems.append("the row count does not re-derive")
    if (stored.get("summary") or {}).get("fold_depth_histogram") != \
            fresh["summary"]["fold_depth_histogram"]:
        problems.append("the fold-depth histogram does not re-derive")
    counts = (stored.get("summary") or {}).get("class_counts") or {}
    if sum(counts.values()) != (stored.get("summary") or {}).get("gates_measured_here"):
        problems.append("the class counts do not sum to the measured population")
    if any(r.get("class") == "frozen_subject" and not r.get("folded_files")
           for r in (stored.get("rows") or [])):
        problems.append("a frozen subject exists without a folded file")
    if any(r.get("class") == "dynamic_subject" and r.get("folded_files")
           for r in (stored.get("rows") or [])):
        problems.append("a dynamic subject is also published as folded")
    for item in problems:
        say("PROBLEM: %s" % item)
    if problems:
        return 1
    say("OK: %d rows over %d gates, %d resolved by folding, problems=[]"
        % (len(stored.get("rows") or []), stored["summary"]["gates_measured_here"],
           stored["summary"]["resolved_by_folding"]))
    return 0


# ------------------------------------------------------------------ selftest

def selftest():
    legs = []

    def leg(name, fn):
        try:
            legs.append((name, bool(fn())))
        except Exception as exc:  # noqa: BLE001
            say("LEG ERROR %s: %r" % (name, exc))
            legs.append((name, False))

    grow = lambda *a: None  # noqa: E731
    tree = ast.parse("OUTDIR = 'results'\nNAME = 'x.json'\n")
    modc = module_consts(tree)

    def l_literal():
        value, depth, kind = fold(ast.parse("'results/a.json'", mode="eval").body, {}, modc)
        return value == "results/a.json" and depth == 0 and kind == "literal"

    def l_join_depth():
        node = ast.parse("os.path.join('results', 'state_tilt', 'x.json')",
                         mode="eval").body
        value, depth, kind = fold(node, {}, modc)
        return value == "results/state_tilt/x.json" and depth == 1 and kind == "join"

    def l_module_hop():
        node = ast.parse("os.path.join(OUTDIR, 'a.json')", mode="eval").body
        value, depth, kind = fold(node, {}, modc)
        return value == "results/a.json" and depth == 2

    def l_body_constant():
        body = ast.parse("_p = 'results/b.json'\nopen(_p)\n").body
        node = ast.parse("open(_p)").body[0].value.args[0]
        value, depth, _ = fold(node, local_consts(body), {})
        return value == "results/b.json" and depth == 1

    def l_listing_stays_dynamic():
        body = ast.parse("_d = 'results'\n_f = ['a.json']\n").body
        node = ast.parse("os.path.join(_d, _f[-1])", mode="eval").body
        value, depth, kind = fold(node, local_consts(body), {})
        return value is None and kind.startswith("subscript")

    def l_fstring_dynamic():
        node = ast.parse("f'results/{d}.json'", mode="eval").body
        value, _, kind = fold(node, {}, {})
        return value is None and kind == "fstring"

    def l_directory_class():
        return _path_class("results/e43_tilt_4member") == "directory" \
            and _path_class("results/a.json") == "file"

    def l_candidates_filter_message():
        body = ast.parse("_b = []\n_b.append(' | ' + ' | '.join(_bad))").body
        rows = path_candidates(body, {})
        return rows == []

    def l_candidates_keep_face():
        body = ast.parse("_p = os.path.join('results', 'state_tilt', 'x.json')\n"
                         "_f = json.load(open(_p))").body
        rows = path_candidates(body, {})
        return any(r["folded"] == "results/state_tilt/x.json" for r in rows)

    def l_verdict_rederives():
        fake = {"summary": {"gates_measured_here": 3,
                            "class_counts": {"frozen_subject": 1, "live_subject": 1,
                                             "dynamic_subject": 1},
                            "resolved_by_folding": 2, "dynamic_remainder": 1,
                            "green_by_freeze_share_before_pct": 16.2,
                            "green_by_freeze_share_after_pct": 20.0}}
        return decide(fake).startswith("2 of 3") and "20.0" in decide(fake)

    def l_double_counting_guard():
        fake = {"summary": {"gates_measured_here": 5,
                            "class_counts": {"frozen_subject": 1}, "resolved_by_folding": 1,
                            "dynamic_remainder": 0}}
        return "do not sum" in decide(fake)

    def l_prewindow_face_is_frozen():
        commits = ["c%d" % i for i in range(4)]
        tracked = blob_series(["results/a.json"], commits, {}, {"results/a.json": "b0"})
        state = e351.gate_states({"faces": ["results/a.json"], "companions": []}, tracked)
        return state["distinct_states"] == 1 and state["present_commits"] == 4 \
            and e351.classify(state) == "frozen_subject"

    def l_inwindow_creation_is_one_state():
        commits = ["c%d" % i for i in range(4)]
        events = {2: {"results/new.json": "b9"}}
        tracked = blob_series(["results/new.json"], commits, events, {})
        state = e351.gate_states({"faces": ["results/new.json"], "companions": []}, tracked)
        return state["distinct_states"] == 1 and state["present_commits"] == 2 \
            and e351.classify(state) == "frozen_subject"

    def l_listing_is_a_path_attempt():
        node = ast.parse("os.path.join(_d, _f[-1])", mode="eval").body
        return _is_path_attempt(node) and not _is_path_attempt(
            ast.parse("'; '.join(_bad)", mode="eval").body)

    def l_wildcard_is_not_a_face():
        return _path_class("data/x/*.csv") == "wildcard" \
            and _path_class("results/x.json") == "file"

    def l_class_partition_real():
        path = os.path.join(ROOT, LATEST if False else os.path.join("results", "state_tilt", LATEST))
        if not os.path.exists(path):
            return True
        with open(path, encoding="utf-8") as fh:
            face = json.load(fh)
        counts = (face.get("summary") or {}).get("class_counts") or {}
        return sum(counts.values()) == face["summary"]["gates_measured_here"] \
            and face.get("verdict") == decide(face)

    for name, fn in [("literal depth 0", l_literal),
                     ("join folds to one depth step", l_join_depth),
                     ("module constant costs one hop", l_module_hop),
                     ("in-body constant folds", l_body_constant),
                     ("index into a list stays dynamic", l_listing_stays_dynamic),
                     ("f-string stays dynamic", l_fstring_dynamic),
                     ("directory vs file classification", l_directory_class),
                     ("message expressions are not subjects", l_candidates_filter_message),
                     ("a face expression survives the filter", l_candidates_keep_face),
                     ("verdict names the split and the share", l_verdict_rederives),
                     ("a partial class table is refused", l_double_counting_guard),
                     ("a face older than the window is frozen, not never evaluated",
                      l_prewindow_face_is_frozen),
                     ("a face created inside the window is one state", l_inwindow_creation_is_one_state),
                     ("a directory listing is a path attempt, a message join is not",
                      l_listing_is_a_path_attempt),
                     ("a wildcard is not a face", l_wildcard_is_not_a_face),
                     ("published face partitions and re-derives", l_class_partition_real)]:
        leg(name, fn)

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        say("%s %s" % ("PASS" if ok else "FAIL", name))
    say("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "build").lower()
    if cmd == "build":
        face = build_face()
        write_face(face)
        s = face["summary"]
        say("wrote %s: %d gates, classes=%s, resolved=%d, dynamic=%d, no_path=%d, share %s->%s"
            % (FACE, s["gates_measured_here"], s["class_counts"], s["resolved_by_folding"],
               s["dynamic_remainder"], s["no_path_expression"],
               s["green_by_freeze_share_before_pct"], s["green_by_freeze_share_after_pct"]))
        say("VERDICT: %s" % face["verdict"])
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: %s [build|verify|selftest]" % SELF_REL)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))