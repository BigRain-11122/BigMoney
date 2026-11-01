"""E342 -- what does a rewritten gate leave behind?

E339 measured the *loosening* of literal-count guards and found the pay-for reading was almost
vacuous: 39 of 41 commits that delete a line in a guarded file touch a face and move a number
anyway, so exactly one commit in that population is the "silent" shape.  This study asks the
general question the card posed, over the whole guard population rather than literal counts:

    check    a named assertion.  In ``smoke_test.py`` the names are the first string argument of
             ``check(...)`` -- the label the leg prints -- and the condition is the second argument.
             In ``Tools/s6_chain_bmb.py`` the check is the ``LEGS`` row: its name is the leg name and
             its condition is the command that actually runs (the leg's reach).
    rewritten  a check that survives the commit under the same name but whose condition changed, or
             that disappears while the file still carries the machinery (a label with no ``check``
             call, a leg row deleted from the table).
    widening  a condition change with a direction that can be decided deterministically: the
             condition became a constant, an ``and`` lost a term, ``and`` became ``or``, or a
             comparison's bound moved outward.  Everything else is ``changed_unclassified`` and is
             published as such rather than folded into a headline.

Two questions per event, published separately because they are different kinds of evidence:

    recorded  did the *same commit* put the new acceptance set somewhere a machine can read it?
              kinds: ``published_face_value`` (an added line in a ``results/*.json`` carries the new
              bound next to the guard's own root name), ``named_constant`` (the commit added a
              module-level assignment whose value is the new bound and whose name mentions the
              guard's root), ``neither``.
    pinned    is the new acceptance set quoted by any check at HEAD?  A widened bound that no check
              quotes is protected by custom, not machinery.

    price     for the ``neither`` rows, what a reader would have to read to recover the *old* reach
              today: diff bytes of the guarded file at that commit, files in the commit, how many
              commits have landed since.

The card's part (c) ships as ``Tools/guard_reach_claw.py``: a staged-tree check that refuses a
commit which changes a guard's condition with no ``results/`` change staged and no ``GUARD-REACH:``
line naming the new reach.  That is the cheapest mechanism that would have caught the one silent
commit (c169c702) -- it reads only what is already staged and needs no history.

Usage:
    python scripts/e342_guard_rewrite_records.py run|verify|selftest
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
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "REPAIRRECORD-%s.json" % TODAY
LATEST = "repairrecord_latest.json"
STUDY = "E342_guard_rewrite_records"

SMOKE = "smoke_test.py"
CHAIN = "Tools/s6_chain_bmb.py"
GUARDED = (SMOKE, CHAIN)

V_MESSAGE = ("the_new_acceptance_set_is_usually_written_down_only_after_the_fact_and_only_when_a_face"
             "_happens_to_move")
V_FACE = "every_rewrite_that_survived_left_the_new_acceptance_set_in_a_published_face"
V_CUSTOM = ("rewritten_gates_are_recorded_by_a_moving_face_more_often_than_by_any_statement_and_the"
            "_remainder_survives_on_custom")
V_NOTHING = "no_assertion_in_the_two_guarded_files_has_ever_been_rewritten_under_the_same_name"

ROOT_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def relp(path):
    return (path or "").replace("\\", "/")


# ---------------------------------------------------------------------------------------- git access

def _git(*args, **kw):
    proc = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if kw.get("check") and proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), (proc.stderr or "")[:200]))
    return proc.returncode, proc.stdout, proc.stderr


def show_many(rev_paths):
    """One ``git cat-file --batch`` for many ``<rev>:<path>`` queries (E339's measured recipe)."""
    queries = "".join(q + "\n" for q in rev_paths)
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=queries.encode("utf-8"),
                          capture_output=True)
    if proc.returncode != 0:
        return {q: None for q in rev_paths}
    out, blobs, pos = proc.stdout, {}, 0
    for q in rev_paths:
        nl = out.find(b"\n", pos)
        if nl < 0:
            blobs[q] = None
            continue
        header = out[pos:nl].decode("utf-8", "replace")
        pos = nl + 1
        fields = header.rsplit(" ", 2)
        if len(fields) != 3 or not fields[2].isdigit():
            blobs[q] = None
            continue
        size = int(fields[2])
        blobs[q] = out[pos:pos + size].decode("utf-8", "replace")
        pos += size + 1
    return blobs


def commits_with_deletions():
    """Newest-first commits touching the guarded files, with their per-file deleted-line counts."""
    rc, out, err = _git("log", "--format=%x01%H|%ct", "--numstat", "--", *GUARDED)
    if rc != 0:
        raise RuntimeError("git log failed: %s" % (err or "")[:200])
    rows, cur = [], None
    for line in out.splitlines():
        if line.startswith("\x01"):
            sha, _sep, ts = line[1:].strip().partition("|")
            cur = {"sha": sha, "ts": int(ts) if ts.strip().isdigit() else 0, "deleted": {}}
            rows.append(cur)
            continue
        parts = line.split("\t")
        if len(parts) != 3 or cur is None:
            continue
        added, deleted, path = parts
        try:
            cur["deleted"][relp(path)] = int(deleted)
        except ValueError:
            pass
    return rows


def commit_paths(sha):
    rc, out, _err = _git("show", "--name-only", "--format=", sha)
    if rc != 0:
        return []
    return [relp(p.strip()) for p in out.splitlines() if p.strip()]


def commit_message(sha):
    rc, out, _err = _git("log", "-1", "--format=%B", sha)
    return out if rc == 0 else ""


def diff_bytes(sha, path, cache={}):
    key = (sha, path)
    if key not in cache:
        rc, out, _err = _git("show", "--format=", "--unified=0", sha, "--", path)
        cache[key] = len(out.encode("utf-8", "replace")) if rc == 0 else 0
    return cache[key]


# ------------------------------------------------------------------------------------- check parsing

def check_conditions(src, path):
    """label -> [condition text] for one file version.

    smoke_test.py: ``check(name, ok, detail)`` is a three-argument call, so the condition is
    ``args[1]`` and ``args[2]`` is a human-readable detail string.  Joining them (the first draft did)
    turns every detail tweak into an apparent gate rewrite -- four of the eleven events this study
    first reported were exactly that, and the repaired extractor is what removed them.
    Tools/s6_chain_bmb.py: the ``LEGS`` table, where the name is the leg and the condition is the
    argv that runs.
    """
    tree = ast.parse(src)
    out = {}
    if path == CHAIN:
        for node in tree.body:
            if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "LEGS"):
                continue
            if not isinstance(node.value, ast.List):
                continue
            for elt in node.value.elts:
                if not (isinstance(elt, ast.Tuple) and elt.elts):
                    continue
                name = elt.elts[0]
                if not (isinstance(name, ast.Constant) and isinstance(name.value, str)):
                    continue
                reach = " | ".join(ast.unparse(e) for e in elt.elts[1:])
                out.setdefault(name.value, []).append(reach)
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Name) and fn.id == "check"):
            continue
        if len(node.args) < 2:
            continue
        first = node.args[0]
        if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
            continue
        out.setdefault(first.value, []).append(ast.unparse(node.args[1]))
    return out


SKEL_OP = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
           ast.In: "in", ast.NotIn: "not in", ast.Is: "is", ast.IsNot: "is not"}


def skeleton(text):
    """A token string for a condition that keeps the machinery and drops the wording.

    Identifiers collapse to ``N`` (this is what makes ``len(same_day) == 0`` and ``len(viol) == 0``
    the same gate), attribute names survive, non-string constants keep their value, and every
    string / f-string collapses to ``S`` because those carry the message, not the acceptance set.
    """
    try:
        node = ast.parse(text, mode="eval").body
    except SyntaxError:
        return "unparseable:" + text.strip()
    toks = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Compare):
            for op in sub.ops:
                toks.append(SKEL_OP.get(type(op), "?op"))
        elif isinstance(sub, ast.BoolOp):
            toks.append("and" if isinstance(sub.op, ast.And) else "or")
        elif isinstance(sub, ast.UnaryOp) and isinstance(sub.op, ast.Not):
            toks.append("not")
        elif isinstance(sub, ast.Attribute):
            toks.append("attr:" + sub.attr)
        elif isinstance(sub, ast.Call):
            fn = sub.func
            if isinstance(fn, ast.Name):
                toks.append("call:" + fn.id)
            elif isinstance(fn, ast.Attribute):
                toks.append("call:" + fn.attr)
            else:
                toks.append("call:?")
        elif isinstance(sub, ast.Name):
            toks.append("N")
        elif isinstance(sub, ast.Constant):
            toks.append("S" if isinstance(sub.value, str) else repr(sub.value))
    return " ".join(sorted(toks))


def has_comparison(text):
    try:
        node = ast.parse(text, mode="eval").body
    except SyntaxError:
        return False
    return any(isinstance(s, ast.Compare) for s in ast.walk(node))


def condition_signature(text):
    """A stable, format-insensitive reading of one condition string.

    Returns ``{"kind": and|or|atom, "terms": [...], "cmp": {left: (op, literal)}}``.  Whitespace is
    normalised by ``ast.unparse`` already; the terms are sorted so a reordering is not an event.
    """
    try:
        node = ast.parse(text, mode="eval").body
    except SyntaxError:
        return {"kind": "unparseable", "terms": [text.strip()], "cmp": {}}
    terms, kind = [], "atom"
    if isinstance(node, ast.BoolOp):
        kind = "and" if isinstance(node.op, ast.And) else "or"
        terms = [ast.unparse(v) for v in node.values]
    else:
        terms = [ast.unparse(node)]
    cmp_ = {}
    for sub in ast.walk(node):
        if isinstance(sub, ast.Compare) and len(sub.ops) == 1:
            op = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
                  ast.Gt: ">", ast.GtE: ">="}.get(type(sub.ops[0]))
            if op is None:
                continue
            left = ast.unparse(sub.left)
            right = sub.comparators[0]
            if isinstance(right, ast.Constant) and isinstance(right.value, (int, float, str)) \
                    and not isinstance(right.value, bool):
                cmp_[left] = (op, right.value)
    return {"kind": kind, "terms": sorted(terms), "cmp": cmp_}


def _lt(a, b):
    """Comparable ordering that never raises: a str/number mix has no direction."""
    try:
        return a < b
    except TypeError:
        return False


def widen_class(old_text, new_text, path=SMOKE):
    """Decided direction, or a named undecided class.  Frozen here, read off by the face."""
    if path == CHAIN:
        # a leg's condition is the command it runs; "wider" has no meaning, only "different reach"
        return "reach_changed"
    o, n = condition_signature(old_text), condition_signature(new_text)
    if n["kind"] == "unparseable":
        return "changed_unclassified"
    raw = new_text.strip()
    if raw in ("True", "1"):
        return "loosened_to_a_constant"
    if skeleton(old_text) == skeleton(new_text):
        return "changed_by_renaming_only"
    if o["kind"] == "and" and n["kind"] == "or":
        return "loosened_and_became_or"
    if o["kind"] == "and" and set(n["terms"]) < set(o["terms"]):
        return "loosened_by_dropping_a_term"
    if o["kind"] == "or" and set(n["terms"]) < set(o["terms"]):
        return "tightened_by_dropping_a_term"
    if has_comparison(old_text) and not has_comparison(new_text):
        # the acceptance set did not disappear, it moved behind a name the check now trusts; a
        # reader of the check alone can no longer say what it accepts
        return "reach_moved_out_of_the_check"
    direction = None
    for left, (op, lit) in n["cmp"].items():
        if left not in o["cmp"]:
            continue
        oop, olit = o["cmp"][left]
        if (oop, olit) == (op, lit):
            continue
        if oop in ("==", "!=") and op == "!=" and oop == "==":
            direction = "loosened"
        elif oop in ("==", "!=") and op == "==" and oop == "!=":
            direction = "tightened"
        elif op in (">=", ">"):
            direction = "loosened" if _lt(lit, olit) else "tightened"
        elif op in ("<=", "<"):
            direction = "loosened" if _lt(olit, lit) else "tightened"
        elif oop in (">=", ">") and op in (">=", ">"):
            direction = "loosened" if _lt(lit, olit) else "tightened"
    if direction:
        return "bound_%s" % direction
    return "changed_unclassified"


def check_events(old_map, new_map, path=SMOKE):
    """Two versions of one file -> (events keyed by the stable name, detail-only changes).

    A detail-string change is not a rewrite: the printed message moved, the acceptance set did not.
    Counting them separately is what keeps the rewrite population honest.
    """
    events, detail_only = [], 0
    for name in sorted(set(old_map) | set(new_map)):
        olds, news = list(old_map.get(name) or []), list(new_map.get(name) or [])
        for text in list(olds):
            if text in news:
                olds.remove(text)
                news.remove(text)
        if olds and not news:
            for text in olds:
                events.append({"name": name, "kind": "removed", "old": text, "new": None,
                               "widen": "gate_gone"})
            continue
        if news and not olds:
            continue  # a brand-new check is not a rewrite
        for old_text, new_text in zip(olds, news):
            # a reordering or a reformat inside a boolean conjunction is not a rewrite: the
            # acceptance set is identical, so the name kept the same reach.
            _o, _n = condition_signature(old_text), condition_signature(new_text)
            if _o["terms"] == _n["terms"] and _o["cmp"] == _n["cmp"]:
                continue
            events.append({"name": name, "kind": "rewritten", "old": old_text, "new": new_text,
                           "widen": widen_class(old_text, new_text, path)})
        for text in olds[len(news):]:
            events.append({"name": name, "kind": "removed", "old": text, "new": None,
                           "widen": "gate_gone"})
    return events, detail_only


# ------------------------------------------------------------------------------ machine-readable record

def _added_lines(sha, paths, cap=4):
    jsons = [p for p in paths if p.startswith("results/") and p.endswith(".json")][:cap]
    if not jsons:
        return []
    rc, out, _err = _git("show", "--unified=0", "--format=", sha, "--", *jsons)
    if rc != 0:
        return []
    return [l[1:] for l in out.splitlines()
            if l.startswith("+") and not l.startswith("+++")]


def _root_token(expr):
    words = ROOT_TOKEN.findall(expr)
    words = [w for w in words if w not in ("len", "get", "and", "or", "not", "True", "False",
                                           "isinstance", "str", "int", "float", "None")]
    return words[0] if words else ""


def _new_bound(expr):
    m = NUM.findall(expr)
    return m[-1] if m else None


def records_in_commit(sha, paths, expr):
    """Did the same commit put the new acceptance set where a machine can read it?"""
    token, bound = _root_token(expr), _new_bound(expr)
    added = _added_lines(sha, paths)
    if bound and added:
        for line in added:
            if bound in line and (not token or token in line):
                return "published_face_value"
    pys = [p for p in paths if p.endswith(".py") and p not in GUARDED][:4]
    if pys and bound:
        blobs = show_many(["%s:%s" % (sha, p) for p in pys])
        for path in pys:
            src = blobs.get("%s:%s" % (sha, path))
            if not src:
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for node in tree.body:
                if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)):
                    continue
                val = node.value.value
                if isinstance(val, bool) or str(val) != str(bound):
                    continue
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and token and token.lower() in tgt.id.lower():
                        return "named_constant"
    return "neither"


def pinned_at_head(name, new_expr, head_maps):
    """Is the new acceptance set quoted by any check at HEAD (itself excluded)?"""
    sig = condition_signature(new_expr)
    wanted = set(sig["terms"])
    for path, mapping in head_maps.items():
        for other, texts in mapping.items():
            for text in texts:
                if other == name and text == new_expr:
                    continue
                if new_expr.strip() and new_expr.strip() in text:
                    return True
                if wanted and wanted <= set(condition_signature(text)["terms"]):
                    return True
    return False


def _prose_words(text):
    words = [w.lower() for w in ROOT_TOKEN.findall(text) if len(w) > 3]
    return set(words)


def prose_mentions(sha, name, new_expr):
    msg = _prose_words(commit_message(sha))
    if not msg:
        return False
    if _prose_words(name) and _prose_words(name) <= msg:
        return True
    overlap = _prose_words(new_expr or "") & msg
    return len(overlap) >= 2


# ---------------------------------------------------------------------------------------- the maths

def summarize(events):
    rewrites = [e for e in events if e["kind"] == "rewritten"]
    widenings = [e for e in rewrites if e["widen"].startswith(("loosened", "bound_loosened"))]
    tightenings = [e for e in rewrites if e["widen"].startswith(("tightened", "bound_tightened"))]
    unclassified = [e for e in rewrites if e["widen"] == "changed_unclassified"]
    removed = [e for e in events if e["kind"] == "removed"]
    by_widen = {}
    for e in rewrites:
        by_widen[e["widen"]] = by_widen.get(e["widen"], 0) + 1
    by_record = {}
    for e in events:
        by_record[e["record"]] = by_record.get(e["record"], 0) + 1
    no_record = [e for e in events if e["record"] == "neither"]
    no_record_rewrites = [e for e in rewrites if e["record"] == "neither"]
    return {
        "checks_at_head": None,
        "events": len(events),
        "rewritten": len(rewrites),
        "removed": len(removed),
        "loosened": len(widenings),
        "tightened": len(tightenings),
        "changed_unclassified": len(unclassified),
        "changed_by_renaming_only": sum(1 for e in rewrites
                                        if e["widen"] == "changed_by_renaming_only"),
        "reach_moved_out_of_the_check": sum(1 for e in rewrites
                                            if e["widen"] == "reach_moved_out_of_the_check"),
        "leg_reach_changed": sum(1 for e in rewrites if e["widen"] == "reach_changed"),
        "rewritten_by_kind": by_widen,
        "record_by_kind": by_record,
        "rewritten_recorded_machine_readably": sum(
            1 for e in rewrites if e["record"] in ("published_face_value", "named_constant")),
        "events_with_no_machine_record": len(no_record),
        "rewrites_with_no_machine_record": len(no_record_rewrites),
        "events_pinned_at_head": sum(1 for e in events if e.get("pinned_at_head")),
        "rewrites_pinned_at_head": sum(1 for e in rewrites if e.get("pinned_at_head")),
        "removed_then_restored": sum(1 for e in removed if e.get("present_at_head")),
        "loosened_with_no_machine_record": sum(1 for e in widenings if e["record"] == "neither"),
        "loosened_and_unpinned": sum(1 for e in widenings
                                     if e["record"] == "neither" and not e.get("pinned_at_head")),
        "prose_only": sum(1 for e in events
                          if e["record"] == "neither" and e["prose_mentions"]),
        "silent_shape": sum(1 for e in events
                            if e["record"] == "neither" and not e["prose_mentions"]
                            and not e["face_or_number_moved"]),
    }


def decide(summary):
    total = summary.get("rewritten") or 0
    if total == 0:
        return V_NOTHING, ["no named assertion was ever rewritten in place in the guarded files"]
    recorded = summary.get("rewritten_recorded_machine_readably") or 0
    if recorded == total:
        return V_FACE, ["%s/%s rewrites left the new acceptance set in a published face"
                        % (total, total)]
    prose = summary.get("prose_only") or 0
    silent = summary.get("silent_shape") or 0
    if silent == 0 and prose > 0:
        return V_MESSAGE, ["%s of %s rewrites are machine-readably recorded; the rest live in a "
                           "commit message, and %s had none of the above"
                           % (recorded, total, silent)]
    return V_CUSTOM, ["%s of %s rewrites are machine-readably recorded, %s survive only as prose, "
                      "%s are silent" % (recorded, total, prose, silent)]


# ---------------------------------------------------------------------------------------- build

def build(root=None):
    root = root or ROOT
    head_maps = {}
    for path in GUARDED:
        src = io.open(os.path.join(root, path), encoding="utf-8").read()
        head_maps[path] = check_conditions(src, path)

    rows = commits_with_deletions()
    planned = []
    for row in rows:
        for path, deleted in (row["deleted"] or {}).items():
            if deleted > 0:
                planned.append((row, path))
    blobs = show_many([q for row, path in planned
                       for q in ("%s:%s" % (row["sha"], path), "%s^:%s" % (row["sha"], path))])

    scanned, events, skipped = [], [], []
    for row, path in planned:
        before = blobs.get("%s^:%s" % (row["sha"], path))
        after = blobs.get("%s:%s" % (row["sha"], path))
        if before is None or after is None:
            skipped.append({"sha": row["sha"], "file": path,
                            "why": "blob missing at one side (first commit or a rename)"})
            continue
        try:
            old_map = check_conditions(before, path)
            new_map = check_conditions(after, path)
        except SyntaxError as exc:
            skipped.append({"sha": row["sha"], "file": path, "why": "unparseable: %s" % exc})
            continue
        scanned.append({"sha": row["sha"], "ts": row["ts"], "file": path,
                        "deleted_lines": row["deleted"][path],
                        "checks_before": sum(len(v) for v in old_map.values()),
                        "checks_after": sum(len(v) for v in new_map.values())})
        for ev in check_events(old_map, new_map, path)[0]:
            ev["sha"] = row["sha"]
            ev["ts"] = row["ts"]
            ev["file"] = path
            events.append(ev)

    paths_cache = {}
    for ev in events:
        sha = ev["sha"]
        if sha not in paths_cache:
            paths_cache[sha] = commit_paths(sha)
        paths = paths_cache[sha]
        ev["record"] = records_in_commit(sha, paths, ev["new"] or ev["old"] or "")
        ev["prose_mentions"] = prose_mentions(sha, ev["name"], ev["new"] or "")
        ev["face_or_number_moved"] = any(p.startswith("results/") for p in paths)
        # Two readings that are easy to confuse and must not be: a *removed* check cannot be
        # "pinned"; it can only have come back (`present_at_head`).  The first draft published
        # three removals as pinned=True, which reads as impossible and was: those three names were
        # deleted in 9f8010c78 and re-added later, so the pair (name, condition) exists at HEAD.
        ev["present_at_head"] = (ev["old"] if ev["kind"] == "removed" else None) in (
            head_maps[ev["file"]].get(ev["name"]) or [])
        ev["pinned_at_head"] = (pinned_at_head(ev["name"], ev["new"] or "", head_maps)
                                if ev["kind"] == "rewritten" else None)
        ev["price"] = {
            "diff_bytes_at_that_commit": diff_bytes(sha, ev["file"]),
            "files_in_commit": len(paths),
            "records_in_commit": sum(1 for p in paths if p.startswith("results/")),
        }

    events.sort(key=lambda e: (e["ts"], e["sha"], e["file"], e["name"]))
    summary = summarize(events)
    summary["checks_at_head"] = sum(len(v) for v in head_maps[SMOKE].values()), \
        sum(len(v) for v in head_maps[CHAIN].values())
    summary["checks_at_head"] = {"smoke_checks": sum(len(v) for v in head_maps[SMOKE].values()),
                                 "chain_legs": sum(len(v) for v in head_maps[CHAIN].values())}

    # what a reader must read to recover the old reach, over the no-machine-record rows
    no_record = [e for e in events if e["record"] == "neither"]
    price = {
        "rows": len(no_record),
        "diff_bytes_total": sum(e["price"]["diff_bytes_at_that_commit"] for e in no_record),
        "diff_bytes_median": sorted(e["price"]["diff_bytes_at_that_commit"] for e in no_record)[
            len(no_record) // 2] if no_record else 0,
        "commits_where_all_of_it_sits": len({e["sha"] for e in no_record}),
        "note": ("each row is one git show of one file at one commit; the count is the number of "
                 "commits a reader has to open, not the number of rows"),
    }

    verdict, reasons = decide(summary)
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "definition": {
            "guarded_files": list(GUARDED),
            "check": ("smoke_test.py: the label printed by check(<label>, <condition>, ...); "
                      "s6_chain_bmb.py: one LEGS row, named by its leg name, whose condition is "
                      "the argv that runs"),
            "rewritten": ("same name on both sides of the commit with a different condition, or the "
                          "name gone while the file still carries the machinery"),
            "widen": ("decided only where the direction is mechanical: became a constant, an and "
                      "lost a term, and became or, or a comparison bound moved outward; anything "
                      "else is changed_unclassified and is not counted as a loosening"),
            "record": ("published_face_value (an added results/*.json line carries the new bound "
                       "next to the guard's root name) | named_constant (the commit added a "
                       "module-level assignment holding the new bound under a name mentioning the "
                       "root) | neither"),
            "pinned_at_head": "some other check at HEAD quotes the same condition text or terms",
            "population": ("commits that delete at least one line in a guarded file -- a rewrite of "
                           "an existing check needs a deletion, so a pure-addition commit cannot be "
                           "one"),
        },
        "head": {"smoke_checks": summary["checks_at_head"]["smoke_checks"],
                 "chain_legs": summary["checks_at_head"]["chain_legs"]},
        "history": {
            "commits_scanned": len(scanned),
            "commits_with_deletions": sum(1 for r in rows if sum((r.get("deleted") or {}).values()) > 0),
            "skipped": skipped,
            "events": events,
            "price_of_no_record": price,
        },
        "summary": summary,
        "verdict": verdict,
        "reasons": reasons,
        "self_disclosure": {
            "this_study_adds_a_check_to_the_corpus": True,
            "note": ("landing this study adds one smoke leg and one chain leg, i.e. exactly two new "
                     "named checks after the cutoff; the face states that instead of claiming the "
                     "measurement stands outside its own population"),
        },
    }
    os.makedirs(OUTDIR, exist_ok=True)
    for name in (FACE, LATEST):
        with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")
    return doc


# ---------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__))
        return
    if isinstance(a, dict):
        for key in set(a) | set(b):
            if key in ("generated",):
                continue
            if key not in a or key not in b:
                out.append("%s.%s: present in only one side" % (path, key))
                continue
            _cmp(a[key], b[key], "%s.%s" % (path, key), out)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            out.append("%s: length %s vs %s" % (path, len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, "%s[%s]" % (path, i), out)
        return
    if isinstance(a, float):
        if abs(a - b) > 1e-9:
            out.append("%s: %r vs %r" % (path, a, b))
        return
    if a != b:
        out.append("%s: %r vs %r" % (path, a, b))


def verify(root=None):
    root = root or ROOT
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build(root)
    problems = []
    _cmp(disk, fresh, "face", problems)
    return problems


# ---------------------------------------------------------------------------------------- selftest

def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    smoke_src = (
        "def f():\n"
        "    check('leg a', len(rows) == 3)\n"
        "    check('leg b', a > 1 and b > 2, 'detail one')\n"
        "    check('leg c', a > 1 or b > 2)\n"
        "    check('leg d', True)\n"
    )
    m = check_conditions(smoke_src, SMOKE)
    check("L1 the label is the identity and the condition is everything after it",
          set(m) == {"leg a", "leg b", "leg c", "leg d"}, str(sorted(m)))
    check("L2 a check with no string label is not a named check",
          check_conditions("def f():\n    check(cond, detail)\n", SMOKE) == {}, "unexpected label")
    check("L3 the third argument is a detail string and does not enter the condition",
          m.get("leg b") == ["a > 1 and b > 2"], str(m.get("leg b")))

    chain_src = "LEGS = [('a', ['python', 'x.py']), ('b', ['python', 'y.py', 'run'])]\n"
    m2 = check_conditions(chain_src, CHAIN)
    check("L4 a chain leg is named by its leg name and its condition is the argv",
          m2.get("b") == ["['python', 'y.py', 'run']"], str(m2))

    # widening classes -- each one a decided direction, never a silent guess
    check("L5 a condition that became True is a loosening",
          widen_class("a > 1", "True") == "loosened_to_a_constant", widen_class("a > 1", "True"))
    check("L6 and -> or is a loosening",
          widen_class("a > 1 and b > 2", "a > 1 or b > 2") == "loosened_and_became_or")
    check("L7 dropping a conjunct is a loosening, including down to one atom",
          widen_class("a > 1 and b > 2", "a > 1") == "loosened_by_dropping_a_term",
          widen_class("a > 1 and b > 2", "a > 1"))
    check("L8 a >= bound moving down is a loosening",
          widen_class("n >= 3", "n >= 1") == "bound_loosened", widen_class("n >= 3", "n >= 1"))
    check("L9 a >= bound moving up is a tightening",
          widen_class("n >= 1", "n >= 3") == "bound_tightened", widen_class("n >= 1", "n >= 3"))
    check("L10 == -> != is a loosening",
          widen_class("s == 'x'", "s != 'x'") == "bound_loosened",
          widen_class("s == 'x'", "s != 'x'"))
    check("L11 an incomparable rewrite is published as unclassified, not as a loosening",
          widen_class("a in b", "a == b") == "changed_unclassified",
          widen_class("a in b", "a == b"))
    check("L12 a rename is its own class, not an unclassified change",
          widen_class("len(same_day) == 0 and f'{n} same-day'",
                      "len(viol) == 0 and f'{n} entry-day closes'") == "changed_by_renaming_only",
          widen_class("len(same_day) == 0 and f'{n} same-day'",
                      "len(viol) == 0 and f'{n} entry-day closes'"))
    check("L13 a condition replaced by names has moved its reach out of the check",
          widen_class("_hf.get('a') in ('ok',) and _hf.get('b') is False",
                      "_face_ok and _why") == "reach_moved_out_of_the_check",
          widen_class("_hf.get('a') in ('ok',) and _hf.get('b') is False", "_face_ok and _why"))
    check("L14 a chain leg change is a reach change, never a widening",
          widen_class("['python', 'x.py', 'audit']", "['python', 'x.py', 'apply']", CHAIN)
          == "reach_changed")
    check("L15 a reordering inside an and is not an event",
          check_events({"x": ["a > 1 and b > 2"]}, {"x": ["b > 2 and a > 1"]})[0] == [],
          str(check_events({"x": ["a > 1 and b > 2"]}, {"x": ["b > 2 and a > 1"]})))

    ev = check_events({"x": ["a > 1"]}, {"x": ["a > 0"]})[0]
    check("L16 a rewrite keeps its name and reports both sides",
          len(ev) == 1 and ev[0]["kind"] == "rewritten" and ev[0]["name"] == "x", str(ev))
    ev = check_events({"x": ["a > 1"]}, {})[0]
    check("L17 a vanished name is a removal, not a rewrite",
          len(ev) == 1 and ev[0]["kind"] == "removed", str(ev))
    ev = check_events({}, {"x": ["a > 1"]})[0]
    check("L18 a brand-new check is not an event at all", ev == [], str(ev))

    # the record ladder and the frozen rule
    s = summarize([
        {"kind": "rewritten", "widen": "bound_loosened", "record": "published_face_value",
         "pinned_at_head": True, "prose_mentions": True, "face_or_number_moved": True},
        {"kind": "rewritten", "widen": "bound_loosened", "record": "neither",
         "pinned_at_head": False, "prose_mentions": False, "face_or_number_moved": False},
    ])
    check("L19 a silent rewrite is counted separately from a prose-only one",
          s["silent_shape"] == 1 and s["prose_only"] == 0, str(s))
    check("L20 loosened-and-unpinned counts only rows with neither record nor pin",
          s["loosened_and_unpinned"] == 1, str(s))
    s2 = summarize([
        {"kind": "removed", "widen": "gate_gone", "record": "neither", "pinned_at_head": None,
         "present_at_head": True, "prose_mentions": False, "face_or_number_moved": True},
        {"kind": "removed", "widen": "gate_gone", "record": "neither", "pinned_at_head": None,
         "present_at_head": False, "prose_mentions": False, "face_or_number_moved": True},
    ])
    check("L21 a removal is counted as restored, never as pinned",
          s2["removed_then_restored"] == 1 and s2["events_pinned_at_head"] == 0, str(s2))
    v, why = decide({"rewritten": 2, "rewritten_recorded_machine_readably": 0,
                     "prose_only": 0, "silent_shape": 1})
    check("L22 the frozen rule calls a silent rewrite what it is", v == V_CUSTOM, "%s %s" % (v, why))
    v, why = decide({"rewritten": 0})
    check("L23 an empty population is not a verdict about the tree", v == V_NOTHING, v)
    v, why = decide({"rewritten": 2, "rewritten_recorded_machine_readably": 2})
    check("L24 every rewrite recorded machine-readably is its own verdict", v == V_FACE, v)

    # the skeleton is what makes a rename invisible and a message change irrelevant
    check("L25 the skeleton ignores the wording inside a message",
          skeleton("len(a) == 0 and f'{n} same-day'") == skeleton("len(a) == 0 and f'{m} closes'"),
          skeleton("len(a) == 0 and f'{n} same-day'"))
    check("L26 the skeleton does not ignore a number that moved",
          skeleton("n >= 3") != skeleton("n >= 7"), skeleton("n >= 3"))
    check("L27 a bound is read off the expression, last number wins",
          _new_bound("n >= 3 and m <= 7") == "7", _new_bound("n >= 3 and m <= 7"))
    check("L28 the root token skips borrowed names",
          _root_token("len(faces) >= 3") == "faces", _root_token("len(faces) >= 3"))

    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + str(detail)))
    failed = [n for n, ok, _d in checks if not ok]
    say("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


# ------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    say("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
    say("verdict: %s" % doc["verdict"])
    say("checks at head: %s smoke checks / %s chain legs | commits scanned %s"
        % (doc["head"]["smoke_checks"], doc["head"]["chain_legs"],
           doc["history"]["commits_scanned"]))
    say("events: rewritten %s (loosened %s / tightened %s / unclassified %s) | removed %s"
        % (s["rewritten"], s["loosened"], s["tightened"], s["changed_unclassified"], s["removed"]))
    say("record: %s machine-readable | %s prose only | %s silent"
        % (s["rewritten_recorded_machine_readably"], s["prose_only"], s["silent_shape"]))
    say("pinned at head: %s of %s events | loosened and unpinned: %s"
        % (s["events_pinned_at_head"], s["events"], s["loosened_and_unpinned"]))
    price = doc["history"]["price_of_no_record"]
    say("price of the no-record rows: %s rows over %s commits, %s diff bytes (median %s)"
        % (price["rows"], price["commits_where_all_of_it_sits"], price["diff_bytes_total"],
           price["diff_bytes_median"]))
    for reason in doc["reasons"]:
        say("  - %s" % reason)
    for ev in doc["history"]["events"][:12]:
        say("  * %s %s %s: %s (%s) record=%s pinned=%s"
            % (ev["sha"][:9], ev["file"], ev["name"][:46], ev["kind"], ev["widen"],
               ev["record"], ev["pinned_at_head"]))
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        say("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    say("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))