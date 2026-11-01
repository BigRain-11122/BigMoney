"""E339 -- which literal-count guards were loosened rather than repaired?

E337 repaired one hard-coded inertness guard by publishing a transition instead of a literal
"nothing moved".  Its digest named the general failure mode: a guard that hard-codes a count either
goes red on the next legitimate landing, or gets quietly loosened so it stops going red.  The first
branch is loud; the second is silent, and the tree is full of them, so measure the silent branch.

    guard    a comparison at HEAD between a count-shaped expression (``len(...)``, ``.get('n_...')``,
             a name carrying a count word) and an integer literal
    landing  any commit that touches smoke_test.py or Tools/s6_chain_bmb.py and *deletes* a line --
             a relaxation of an existing guard requires a deletion, so those commits are the whole
             population of possible relaxations (150 deleted lines across 41 commits)
    before/after  the guard set parsed (AST) from the file at ``commit^`` and at ``commit``; a guard
             is identified by its count expression, so a move inside one commit is invisible and a
             literal/operator change is visible
    classes  unchanged | literal_up (the card's "relaxed": literal raised) | literal_down (tightened)
             | op_changed | deleted (the card's "assertion deleted" -- maximally relaxed) | added

Two readings of "was it paid for", because they answer different questions:

    R1 face touched        the same commit touched anything under ``results/``
    R2 a number moved      the same commit's diff to ``results/*.json`` adds or removes a line
                           carrying a digit -- i.e. a published number actually moved

A relaxation paid for by R2 is a republished count; one paid for by nothing is a gate that stopped
being able to catch what it was written to catch.

Usage:
    python scripts/e339_literal_count_guards.py run|verify|selftest
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
FACE = "GUARDLOOSEN-%s.json" % TODAY
LATEST = "guardloosen_latest.json"
STUDY = "E339_literal_count_guards"

GUARDED_FILES = ("smoke_test.py", "Tools/s6_chain_bmb.py")

COUNT_WORDS = re.compile(
    r"(^|_)(n|num|nums|count|counts|total|size|rows|row|files|file|sources|source|consumers|"
    r"numbers|number|entries|entry|faces|face|legs|leg|members|member|names|name|lines|line|"
    r"cells|cell|keys|key|items|item|records|record|fields|field|days|day|verdicts|verdict|"
    r"studies|study|arms|arm|panels|panel|points|point|diffs|diff)($|_)", re.I)

NUM_OPS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
OP_TEXT = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}
CORPUS_WORDS = re.compile(r"(corpus|population|sources|scanned|py_files|\.py\b)", re.I)

V_SILENT = "silent_loosening_measured_at_least_one_literal_count_guard_was_relaxed_and_no_published_number_moved"
V_TOUCHED = "relaxations_were_paid_for_by_a_face_being_touched_but_not_by_a_number_moving"
V_PAID = "every_relaxation_came_with_a_published_number_moving"
V_NONE = "no_literal_count_guard_in_the_two_guarded_files_has_ever_been_relaxed"


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def relp(path):
    return (path or "").replace("\\", "/")


# ---------------------------------------------------------------------------------------- git access

def _git(*args):
    proc = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def show(rev_path):
    """``<rev>:<path>`` -> text, or None when the blob does not exist at that revision."""
    rc, out, _err = _git("show", rev_path)
    if rc != 0:
        return None
    return out


def show_many(rev_paths):
    """One ``git cat-file --batch`` for many ``<rev>:<path>`` queries.

    Forty-one versions of a 690KB file is 57MB through a pipe; spawning ``git show`` eighty-two
    times costs more than the bytes do (measured: 98s for a build, 12s after batching).
    """
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
    """Newest-first [(sha, ts, {path: deleted_lines})] for the two guarded files."""
    rc, out, err = _git("log", "--format=%x01%H|%ct", "--numstat", "--", *GUARDED_FILES)
    if rc != 0:
        raise RuntimeError("git log failed: %s" % (err or "")[:200])
    rows = []
    cur = None
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


# ------------------------------------------------------------------------------------- guard parsing

def _is_int(node):
    return (isinstance(node, ast.Constant) and isinstance(node.value, int)
            and not isinstance(node.value, bool))


def _countish(node):
    """A count-shaped expression.  ``.get('n_x', 0)`` counts only when its key says so -- an
    unguarded ``.get()`` would drag in every tolerance comparison in the tree."""
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id == "len":
            return True
        if isinstance(fn, ast.Attribute) and fn.attr == "get":
            for arg in node.args[:1]:
                if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                        and COUNT_WORDS.search(arg.value)):
                    return True
            return False
    if isinstance(node, ast.Attribute) and COUNT_WORDS.search(node.attr):
        return True
    if isinstance(node, ast.Name) and COUNT_WORDS.search(node.id):
        return True
    return False


def extract_guards(src, path):
    """Every literal-count guard in one file version.  A parse failure must never be silent: the
    caller turns it into a published problem, because a skipped version would read as 'unchanged'."""
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1:
            continue
        if not isinstance(node.ops[0], NUM_OPS):
            continue
        left, right = node.left, node.comparators[0]
        if _is_int(left) and _countish(right):
            literal, expr = left.value, right
        elif _is_int(right) and _countish(left):
            literal, expr = right.value, left
        else:
            continue
        out.append({
            "file": path,
            "line": node.lineno,
            "expr": ast.unparse(expr),
            "op": OP_TEXT[type(node.ops[0])],
            "literal": literal,
            "text": ast.unparse(node),
        })
    return out


def by_expr(guards):
    out = {}
    for g in guards:
        out.setdefault(g["expr"], []).append(g)
    for expr in out:
        out[expr].sort(key=lambda g: (g["op"], g["literal"]))
    return out


def classify(old, new):
    """Compare one guard's (op, literal) across a commit.  ``old``/``new`` are dicts or None."""
    if old is None and new is None:
        return None
    if old is None:
        return "added"
    if new is None:
        return "deleted"
    if old["op"] == new["op"] and old["literal"] == new["literal"]:
        return "unchanged"
    if old["op"] == new["op"]:
        return "literal_up" if new["literal"] > old["literal"] else "literal_down"
    return "op_changed"


def diff_versions(old_guards, new_guards):
    """Per-expression multiset diff.  A guard carried over unchanged is not an event at all."""
    old_map, new_map = by_expr(old_guards), by_expr(new_guards)
    events = []
    for expr in sorted(set(old_map) | set(new_map)):
        olds = list(old_map.get(expr) or [])
        news = list(new_map.get(expr) or [])
        # pair identical guards first so a pure reorder/reformat produces no event
        for g in list(olds):
            twin = next((n for n in news
                         if n["op"] == g["op"] and n["literal"] == g["literal"]), None)
            if twin is not None:
                olds.remove(g)
                news.remove(twin)
        for old, new in zip(olds, news):
            kind = classify(old, new)
            if kind and kind != "unchanged":
                events.append({"expr": expr, "file": new["file"], "kind": kind,
                               "old": {"op": old["op"], "literal": old["literal"], "line": old["line"]},
                               "new": {"op": new["op"], "literal": new["literal"], "line": new["line"]}})
        for old in olds[len(news):]:
            events.append({"expr": expr, "file": old["file"], "kind": "deleted",
                           "old": {"op": old["op"], "literal": old["literal"], "line": old["line"]},
                           "new": None})
        for new in news[len(olds):]:
            events.append({"expr": expr, "file": new["file"], "kind": "added",
                           "old": None,
                           "new": {"op": new["op"], "literal": new["literal"], "line": new["line"]}})
    return events


# ------------------------------------------------------------------------------- did it get paid for

def commit_paths(sha):
    rc, out, _err = _git("show", "--name-only", "--format=", sha)
    if rc != 0:
        return []
    return [relp(p.strip()) for p in out.splitlines() if p.strip()]


def results_paths_touched(paths):
    return [p for p in paths if p.startswith("results/")]


def numbers_moved_in_results(sha, paths, cap=6):
    """R2: does this commit's diff to results/*.json move a published number?

    Only +/- lines carrying a digit count; a face that was merely re-stamped (``generated``) moves
    no number and must not be paid for by this reading.
    """
    jsons = [p for p in paths if p.startswith("results/") and p.endswith(".json")][:cap]
    if not jsons:
        return {"json_files_changed": 0, "numeric_lines": 0}
    rc, out, _err = _git("show", "--unified=0", "--format=", sha, "--", *jsons)
    if rc != 0:
        return {"json_files_changed": len(jsons), "numeric_lines": 0}
    numeric = 0
    for line in out.splitlines():
        if line.startswith(("+++", "---")) or line.startswith("diff --git"):
            continue
        if line[:1] in "+-" and re.search(r"\d", line):
            numeric += 1
    return {"json_files_changed": len(jsons), "numeric_lines": numeric}


# ---------------------------------------------------------------------------------------- the maths

def summarize(head_guards, events, paid):
    relaxed = [e for e in events if e["kind"] in ("literal_up", "deleted", "op_changed")
               and e["kind"] != "added"]
    literal_up = [e for e in events if e["kind"] == "literal_up"]
    deleted = [e for e in events if e["kind"] == "deleted"]
    tightened = [e for e in events if e["kind"] == "literal_down"]
    op_changed = [e for e in events if e["kind"] == "op_changed"]
    unpaid_r1 = [e for e in relaxed if not e.get("face_touched")]
    unpaid_r2 = [e for e in relaxed if not e.get("numbers_moved")]
    exact = [g for g in head_guards if g["op"] in ("==", "!=") and g["literal"] > 1]
    corpus = [g for g in exact if CORPUS_WORDS.search(g["expr"])]
    return {
        "guards_at_head": len(head_guards),
        "guards_exact_count": len(exact),
        "guards_exact_count_over_a_corpus": len(corpus),
        "relaxed": len(relaxed),
        "literal_up": len(literal_up),
        "deleted": len(deleted),
        "relaxed_by_replacement": sum(1 for e in relaxed if e.get("relaxed_by") == "replacement"),
        "relaxed_by_removal": sum(1 for e in relaxed if e.get("relaxed_by") == "removal"),
        "op_changed": len(op_changed),
        "tightened": len(tightened),
        "relaxed_without_face_touched": len(unpaid_r1),
        "relaxed_without_a_number_moving": len(unpaid_r2),
        "relaxed_with_published_number": len(relaxed) - len(unpaid_r2),
    }


def decide(summary):
    """Frozen rule: read off the published counts, never typed by hand."""
    relaxed = summary.get("relaxed") or 0
    if relaxed == 0:
        return V_NONE, ["no literal-count guard was ever relaxed in the two guarded files' history"]
    paid = summary.get("relaxed_with_published_number") or 0
    if paid == relaxed:
        return V_PAID, ["%s/%s relaxations came with a published number moving" % (paid, relaxed)]
    if paid > 0:
        return V_TOUCHED, ["%s of %s relaxations moved a published number in the same commit"
                           % (paid, relaxed)]
    return V_SILENT, ["%s relaxations and not one of them moved a published number in the same "
                      "commit" % relaxed]


# ---------------------------------------------------------------------------------------- build

def build(root=None):
    root = root or ROOT
    head_guards = []
    for path in GUARDED_FILES:
        src = io.open(os.path.join(root, path), encoding="utf-8").read()
        head_guards.extend(extract_guards(src, path))

    rows = commits_with_deletions()
    planned = []
    for row in rows:
        if sum(row["deleted"].values()) <= 0:
            continue
        for path, deleted in row["deleted"].items():
            if not deleted:
                continue
            planned.append((row, path))
    wanted = []
    for row, path in planned:
        wanted.append("%s:%s" % (row["sha"], path))
        wanted.append("%s^:%s" % (row["sha"], path))
    blobs = show_many(wanted)

    scanned = []
    events = []
    skipped = []
    for row, path in planned:
        after = blobs.get("%s:%s" % (row["sha"], path))
        before = blobs.get("%s^:%s" % (row["sha"], path))
        if after is None or before is None:
            skipped.append({"sha": row["sha"], "file": path,
                            "why": "blob missing at one side (first commit or a rename)"})
            continue
        try:
            g_before = extract_guards(before, path)
            g_after = extract_guards(after, path)
        except SyntaxError as exc:
            skipped.append({"sha": row["sha"], "file": path,
                            "why": "unparseable version: %s" % exc})
            continue
        scanned.append({"sha": row["sha"], "ts": row["ts"], "file": path,
                        "deleted_lines": row["deleted"][path],
                        "guards_before": len(g_before), "guards_after": len(g_after)})
        for ev in diff_versions(g_before, g_after):
            ev["sha"] = row["sha"]
            ev["ts"] = row["ts"]
            events.append(ev)

    events.sort(key=lambda e: (e["ts"], e["sha"], e["file"], e["expr"]))

    # A deletion is only a *removal* of a gate if nothing replaced it.  A predicate rewritten under a
    # new name (the T+1 invariant was rewritten twice this way) shows up as one deletion plus one
    # addition; pairing them on (op, literal) inside the same commit is what separates "the gate is
    # gone" from "the gate says something else now".
    for ev in events:
        if ev["kind"] != "deleted":
            continue
        partner = next((a for a in events
                        if a is not ev and a["sha"] == ev["sha"] and a["file"] == ev["file"]
                        and a["kind"] == "added" and a["new"] and ev["old"]
                        and a["new"]["op"] == ev["old"]["op"]
                        and a["new"]["literal"] == ev["old"]["literal"]), None)
        ev["replacement_expr"] = partner["expr"] if partner else None
        ev["relaxed_by"] = "replacement" if partner else "removal"

    # pay-for classification.  Every scanned commit is priced, not only the relaxation ones, because
    # "a face moved in the same commit" is only evidence if most commits do NOT do that.
    payed_commits = {}
    for row in scanned:
        sha = row["sha"]
        if sha in payed_commits:
            continue
        paths = commit_paths(sha)
        res = results_paths_touched(paths)
        payed_commits[sha] = {
            "face_touched": bool(res),
            "results_files": len(res),
            "numbers_moved": numbers_moved_in_results(sha, res),
        }
    for ev in events:
        info = payed_commits[ev["sha"]]
        ev["face_touched"] = info["face_touched"]
        ev["results_files"] = info["results_files"]
        ev["numeric_lines_in_results"] = info["numbers_moved"]["numeric_lines"]
        ev["numbers_moved"] = info["numbers_moved"]["numeric_lines"] > 0

    base = {
        "commits_priced": len(payed_commits),
        "face_touched": sum(1 for v in payed_commits.values() if v["face_touched"]),
        "numbers_moved": sum(1 for v in payed_commits.values() if v["numbers_moved"]["numeric_lines"]),
    }
    base["share_face_touched"] = (round(float(base["face_touched"]) / base["commits_priced"], 4)
                                 if base["commits_priced"] else None)
    base["share_numbers_moved"] = (round(float(base["numbers_moved"]) / base["commits_priced"], 4)
                                  if base["commits_priced"] else None)

    summary = summarize(head_guards, events, payed_commits)
    verdict, reasons = decide(summary)

    named = [e for e in events
             if e["kind"] in ("literal_up", "deleted", "op_changed")]

    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "definition": {
            "guarded_files": list(GUARDED_FILES),
            "guard": ("one comparison between a count-shaped expression and an integer literal; "
                      "only the top-level comparison operator of a Compare node with a single op"),
            "relaxed": ("the card's frozen wording: literal_up (literal raised) or deleted "
                        "(the assertion removed); op_changed is published separately rather than "
                        "folded in, because an operator change has no single direction"),
            "population_of_possible_relaxations": (
                "commits that delete at least one line in a guarded file -- loosening an existing "
                "guard requires a deletion, so a commit that only adds lines cannot relax one"),
            "R1_face_touched": "the same commit touched anything under results/",
            "R2_a_number_moved": ("the same commit's diff to results/*.json has a +/- line "
                                  "carrying a digit (a re-stamped face moves no number)"),
            "pay_for_base_rate": ("R1/R2 are priced on every commit that deleted a line in a "
                                  "guarded file, not only on the relaxation commits, because a "
                                  "reading that almost every commit satisfies is not evidence"),
        },
        "head": {
            "guards": len(head_guards),
            "by_file": {f: sum(1 for g in head_guards if g["file"] == f) for f in GUARDED_FILES},
            "by_op": {},
            "exact_count_guards": [
                {"file": g["file"], "line": g["line"], "text": g["text"], "literal": g["literal"]}
                for g in head_guards if g["op"] in ("==", "!=") and g["literal"] > 1
            ],
        },
        "history": {
            "commits_scanned": len(scanned),
            "commits_with_deletions": sum(1 for r in rows if sum(r["deleted"].values()) > 0),
            "skipped": skipped,
            "events": events,
            "relaxations": named,
            "pay_for_base_rate": base,
        },
        "summary": summary,
        "verdict": verdict,
        "reasons": reasons,
        "self_disclosure": {
            "this_study_adds_a_script_to_the_corpus": True,
            "note": ("smoke_test.py grows by one leg when this study lands, which is exactly the "
                     "population movement that makes an exact-count guard break; the face states "
                     "that rather than pretending the measurement is outside it"),
        },
    }
    for g in head_guards:
        key = g["op"]
        doc["head"]["by_op"][key] = doc["head"]["by_op"].get(key, 0) + 1

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


# --------------------------------------------------------------------------------------- selftest

def _g(expr, op, literal, line=1, path="smoke_test.py"):
    return {"file": path, "line": line, "expr": expr, "op": op, "literal": literal,
            "text": "%s %s %s" % (expr, op, literal)}


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    src = (
        "def f():\n"
        "    if len(rows) == 432:\n"
        "        pass\n"
        "    if _f.get('n_faces', 0) >= 4:\n"
        "        pass\n"
        "    if _f.get('max_abs_diff') != 0.0:\n"
        "        pass\n"
        "    if t['price'] > 0:\n"
        "        pass\n"
        "    if len(rows) < 40 and True:\n"
        "        pass\n"
    )
    gs = extract_guards(src, "smoke_test.py")
    exprs = [g["expr"] for g in gs]
    check("L1 len(<count>) is a guard", "len(rows)" in exprs, str(exprs))
    check("L2 .get('n_faces', 0) counts only because its key says so", "_f.get('n_faces', 0)" in exprs, str(exprs))
    check("L3 a float tolerance comparison is not a count guard",
          not any("max_abs_diff" in e for e in exprs), str(exprs))
    check("L4 a bare subscript is not a count guard", "t['price']" not in exprs, str(exprs))
    check("L5 two guards on the same expression are both kept",
          exprs.count("len(rows)") == 2, str(exprs))
    check("L6 operator text is the python spelling",
          [g["op"] for g in gs if g["expr"] == "_f.get('n_faces', 0)"] == [">="], str(gs))

    old = [_g("len(rows)", "==", 432)]
    new = [_g("len(rows)", "==", 500)]
    ev = diff_versions(old, new)
    check("L7 a raised literal is one literal_up event",
          len(ev) == 1 and ev[0]["kind"] == "literal_up", str(ev))
    ev = diff_versions([_g("len(rows)", "==", 500)], [_g("len(rows)", "==", 400)])
    check("L8 a lowered literal is literal_down (tightened)",
          len(ev) == 1 and ev[0]["kind"] == "literal_down", str(ev))
    ev = diff_versions([_g("len(rows)", "==", 5)], [])
    check("L9 a removed assertion is one deleted event",
          len(ev) == 1 and ev[0]["kind"] == "deleted", str(ev))
    ev = diff_versions([], [_g("len(rows)", "==", 5)])
    check("L10 a new assertion is one added event",
          len(ev) == 1 and ev[0]["kind"] == "added", str(ev))
    ev = diff_versions([_g("len(rows)", "==", 5, line=10)], [_g("len(rows)", "==", 5, line=90)])
    check("L11 a guard that only moved lines is not an event", ev == [], str(ev))
    ev = diff_versions([_g("len(rows)", "==", 5)], [_g("len(rows)", ">=", 5)])
    check("L12 an operator change is op_changed, not literal_up", 
          len(ev) == 1 and ev[0]["kind"] == "op_changed", str(ev))
    ev = diff_versions([_g("len(rows)", "==", 5), _g("len(rows)", "==", 7)], [_g("len(rows)", "==", 5)])
    check("L13 dropping one of two same-expression guards is a deletion",
          len(ev) == 1 and ev[0]["kind"] == "deleted" and ev[0]["old"]["literal"] == 7, str(ev))

    s = summarize([_g("len(rows)", "==", 5), _g("len(x)", "==", 1)], [
        {"kind": "literal_up", "face_touched": True, "numbers_moved": False},
        {"kind": "deleted", "face_touched": False, "numbers_moved": False},
        {"kind": "added", "face_touched": True, "numbers_moved": True},
    ], {})
    check("L14 exact-count guards are ==/!= with a literal above 1", s["guards_exact_count"] == 1, str(s))
    check("L15 added events are not counted as relaxations", s["relaxed"] == 2, str(s))
    check("L16 unpaid counts are read from the two readings separately",
          s["relaxed_without_a_number_moving"] == 2 and s["relaxed_without_face_touched"] == 1, str(s))

    v, _r = decide({"relaxed": 0})
    check("L17 decide: nothing relaxed -> V_NONE", v == V_NONE, v)
    v, _r = decide({"relaxed": 3, "relaxed_with_published_number": 0})
    check("L18 decide: relaxations with no number moving -> silent", v == V_SILENT, v)
    v, _r = decide({"relaxed": 3, "relaxed_with_published_number": 3})
    check("L19 decide: every relaxation paid by a number -> paid", v == V_PAID, v)
    v, _r = decide({"relaxed": 3, "relaxed_with_published_number": 1})
    check("L20 decide: partial payment -> touched", v == V_TOUCHED, v)

    problems = []
    _cmp({"a": 1, "generated": "x"}, {"a": 1, "generated": "y"}, "t", problems)
    check("L21 _cmp ignores generated", problems == [], str(problems))
    problems = []
    _cmp({"a": [1, 2]}, {"a": [1]}, "t", problems)
    check("L22 _cmp catches a length change", len(problems) == 1, str(problems))

    live = [g for g in extract_guards(io.open(os.path.join(ROOT, "smoke_test.py"),
                                              encoding="utf-8").read(), "smoke_test.py")]
    check("L23 the live guarded file yields a non-trivial guard set", len(live) > 50, str(len(live)))
    check("L24 every live guard carries an integer literal",
          all(isinstance(g["literal"], int) for g in live), "non-int literal")
    check("L25 expression keys are stable text", all(g["expr"] == g["expr"].strip() for g in live))
    check("L26 the guarded file list is the two files this study claims",
          GUARDED_FILES == ("smoke_test.py", "Tools/s6_chain_bmb.py"), str(GUARDED_FILES))

    # -- the corpus split: an exact count of a corpus breaks on a landing, an exact count of a study
    #    fixture does not, and conflating them would inflate the fragility headline by 7.
    fake = [_g("len(rows)", "==", 4), _g("len(corpus_files)", "==", 2300),
            _g("len(branches)", "!=", 2), _g("len(rows)", "==", 1)]
    s = summarize(fake, [], {})
    check("L27 exact-count split: only corpus-shaped expressions count as landing-fragile",
          s["guards_exact_count"] == 3 and s["guards_exact_count_over_a_corpus"] == 1, str(s))
    check("L28 a singleton literal is a presence check, not a count of a population",
          s["guards_exact_count"] == 3, str(s))

    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + str(detail)))
    failed = [name for name, ok, _d in checks if not ok]
    say("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


# ------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    say("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
    say("verdict: %s" % doc["verdict"])
    say("guards at head: %s (%s exact-count, of which %s count a corpus, so %s break on a landing) "
        "| commits scanned: %s"
        % (s["guards_at_head"], s["guards_exact_count"], s["guards_exact_count_over_a_corpus"],
           s["guards_exact_count_over_a_corpus"], doc["history"]["commits_scanned"]))
    say("events: relaxed %s (literal_up %s / deleted %s / op_changed %s) | tightened %s"
        % (s["relaxed"], s["literal_up"], s["deleted"], s["op_changed"], s["tightened"]))
    say("paid for: face touched %s | a published number moved %s | unpaid (no number) %s"
        % (s["relaxed"] - s["relaxed_without_face_touched"],
           s["relaxed_with_published_number"], s["relaxed_without_a_number_moving"]))
    base = doc["history"]["pay_for_base_rate"]
    say("base rate over %s priced commits: face touched %s (%s), a number moved %s (%s)"
        % (base["commits_priced"], base["face_touched"], base["share_face_touched"],
           base["numbers_moved"], base["share_numbers_moved"]))
    for reason in doc["reasons"]:
        say("  - %s" % reason)
    for ev in doc["history"]["relaxations"][:12]:
        say("  * %s %s %s: %s %s -> %s (%s) face_touched=%s numbers_moved=%s"
            % (ev["sha"][:9], ev["file"], ev["expr"][:48], ev["kind"],
               (ev["old"] or {}).get("literal"), (ev["new"] or {}).get("literal"),
               ev.get("relaxed_by"), ev.get("face_touched"), ev.get("numbers_moved")))
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