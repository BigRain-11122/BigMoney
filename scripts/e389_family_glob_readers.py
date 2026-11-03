"""E389 -- what do the 18 family-glob readers actually compute?

E386 published `family_glob_readers: 18` from `FAMILY_GLOB_RX.search(src)`: a regular
expression run over the raw text of every in-repo .py file.  A text hit is not a read --
the same three tokens also appear in the .gitignore note that each wave runner carries in
a comment ("results/trial_labor_w*/checkpoint/ covers w9"), and in the detection regex of
E386 itself.  So the count answers "which files mention the pattern", not "which studies
compute something from the family".

This study re-derives the same population from tokens instead of text, and then prices
each real read by what it does with the matched family:

    comment            the pattern lives in a COMMENT token -- prose, computes nothing
    pattern_definition the pattern is an argument to re.compile -- a detector, not a reader
    path_argument      the pattern is a path component passed to a glob/listdir call
    glob_call          the pattern is a glob argument used directly in the call

and for `path_argument` the consumer is classified from the statement that receives the
result (count / newest_by_mtime / sorted_then_last / first_match / iterate_all / unknown).

Never claims a computation the source does not show: an unknown consumer stays unknown.

    python scripts/e389_family_glob_readers.py run
    python scripts/e389_family_glob_readers.py verify
    python scripts/e389_family_glob_readers.py selftest
"""
import ast
import io
import json
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E389_family_glob_readers"
TODAY = "2026-11-03"
FACE = "FAMILYGLOBREAD-%s.json" % TODAY
LATEST = "familyglobread_latest.json"

GLOB_PATTERN = "trial_labor_w*"          # the family E386 counted
PATTERN_STEM = "trial_labor_w"           # a regex form escapes the star: trial_labor_w\*
PARENT_FACE = os.path.join(OUTDIR, "MERGEDCOST-2026-11-03.json")

SKIP_DIRS = (".git", "__pycache__", "_quarantine", "node_modules", ".codely-cli")

V_PROSE_ONLY = "family_glob_is_prose"
V_MIXED = "some_members_compute_something"
V_ALL_COMPUTE = "every_member_computes_something"
V_EMPTY = "empty_population"

GLOB_FUNCS = ("glob", "iglob", "listdir", "scandir", "walk", "rglob")


def _py_corpus(root):
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".py"):
                out.append(os.path.join(base, fn))
    return sorted(out)


def _enclosing_call(tree, line):
    """Innermost ast.Call whose line range covers `line`.

    Tie on span is broken by the later start, so `len(glob.glob(x))` is read as the
    glob call and not as the wrapper -- the wrapper is what the statement does, the
    glob is what the pattern is passed to.
    """
    best = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            lo = getattr(node, "lineno", 0)
            hi = getattr(node, "end_lineno", lo) or lo
            if lo <= line <= hi:
                span = hi - lo
                col = getattr(node, "col_offset", 0)
                if best is None or (span, -lo, -col) < (best[0], -best[2], -best[4]):
                    name = ""
                    f = node.func
                    if isinstance(f, ast.Name):
                        name = f.id
                    elif isinstance(f, ast.Attribute):
                        name = f.attr
                    best = (span, name, lo, hi, col)
    return None if best is None else {"func": best[1], "line": best[2], "end_line": best[3]}


def _assign_target_before(tree, line):
    """Name assigned on `line` (or the line that opens the statement), else None."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node, "lineno", -1) == line:
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    return tgt.id
    return None


def _consumer_class(stmt):
    s = stmt
    if "getmtime" in s or "st_mtime" in s or ".stat(" in s:
        return "newest_by_mtime"
    if "len(" in s:
        return "count"
    if "sorted(" in s and ("[-1]" in s or "[-1:]" in s or "max(" in s):
        return "sorted_then_last"
    if "sorted(" in s:
        return "sorted"
    if "[-1]" in s:
        return "last_match"
    if "[0]" in s:
        return "first_match"
    return "unknown"


def _mentions(s):
    """The family name immediately followed by a star, in path form or regex-escaped form.

    Proximity matters: a bare `*` anywhere in a docstring is not this family, so the star
    must sit on the stem (one optional backslash between them).
    """
    for form in (PATTERN_STEM + "*", PATTERN_STEM + "\\*"):
        if form in s:
            return True
    return False


def classify_source(src, pattern=GLOB_PATTERN):
    """Token-level ledger of every place the family pattern appears in one source file."""
    occ = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return {"occurrences": occ, "parse_error": True}
    for tok in toks:
        if not _mentions(tok.string):
            continue
        if tok.type == tokenize.COMMENT:
            kind = "comment"
        elif tok.type == tokenize.STRING:
            kind = "string"
        else:
            kind = "other"
        occ.append({"line": tok.start[0], "kind": kind,
                    "text": tok.string.strip()[:200]})
    if not occ:
        return {"occurrences": occ, "parse_error": False}

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {"occurrences": occ, "parse_error": True}

    lines = src.splitlines()
    for o in occ:
        if o["kind"] != "string":
            continue
        call = _enclosing_call(tree, o["line"])
        stmt = lines[o["line"] - 1] if o["line"] - 1 < len(lines) else ""
        if call and call["func"] == "compile":
            o["kind"] = "pattern_definition"
            o["func"] = "re.compile"
        elif call and call["func"] in GLOB_FUNCS:
            o["kind"] = "glob_call"
            o["func"] = call["func"]
            o["consumer"] = _consumer_class(stmt)
            o["stmt"] = stmt.strip()[:200]
        elif "glob(" in stmt or "listdir(" in stmt or "scandir(" in stmt:
            # the literal is a path component assembled inside a glob call
            # (`glob.glob(os.path.join(root, "results", "trial_labor_w*"))`)
            o["kind"] = "path_argument"
            o["func"] = call["func"] if call else "join"
            o["consumer"] = _consumer_class(stmt)
            o["stmt"] = stmt.strip()[:200]
        else:
            # no call wraps the literal: it is a path constant if some later statement
            # hands it to a glob/listdir, otherwise it is text (a dead constant is text:
            # a name is only a use at a word boundary, so FAMILY_GLOB_RX is not FAMILY_GLOB)
            name = _assign_target_before(tree, o["line"])
            uses = []
            if name:
                rx = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name))
                for i, l in enumerate(lines):
                    if i + 1 == o["line"]:
                        continue
                    if rx.search(l) and ("glob" in l or "listdir" in l or "walk" in l):
                        uses.append({"line": i + 1, "stmt": l.strip()[:200],
                                     "consumer": _consumer_class(l)})
            if uses:
                o["kind"] = "path_argument"
                o["func"] = call["func"] if call else "assignment"
                o["assigned_to"] = name
                o["uses"] = uses
                o["consumer"] = uses[0]["consumer"]
            else:
                o["kind"] = "text"
                o["func"] = call["func"] if call else None
                o["assigned_to"] = name
                if name:
                    o["dead_constant"] = True
        if o["kind"] in ("glob_call", "path_argument"):
            s = (o.get("stmt") or "") + " " + (o.get("text") or "")
            if "results" in s:
                o["target"] = "results_dirs"
            elif ".py" in s:
                o["target"] = "runner_sources"
            else:
                o["target"] = "unknown"
    return {"occurrences": occ, "parse_error": False}


def _file_class(occ):
    kinds = {o["kind"] for o in occ}
    for k in ("glob_call", "path_argument"):
        if k in kinds:
            return k
    if "pattern_definition" in kinds:
        return "pattern_definition"
    if kinds == {"comment"}:
        return "comment"
    return "text"


def scan(root=ROOT, exclude_self=True):
    self_rel = os.path.relpath(os.path.abspath(__file__), root).replace("\\", "/")
    rows = []
    for p in _py_corpus(root):
        try:
            src = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if not _mentions(src):
            continue
        rel = os.path.relpath(p, root).replace("\\", "/")
        if exclude_self and rel == self_rel:
            continue
        c = classify_source(src)
        rows.append({"file": rel, "class": _file_class(c["occurrences"]),
                     "parse_error": c["parse_error"],
                     "occurrences": c["occurrences"]})
    return rows


def parent_population(path=PARENT_FACE):
    """The 18 files E386 named, machine-read from E386's own face (never hand-copied)."""
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        return None
    return sorted({r.get("file") for r in (d.get("family_glob_rows") or []) if r.get("file")})


def build(root=ROOT):
    rows = scan(root)
    parent = parent_population() or []
    by_file = {r["file"]: r for r in rows}

    results_readers = []
    runner_readers = []
    by_target = {"results_dirs": [], "runner_sources": [], "unknown": []}
    consumers = {}
    dead = []
    for r in rows:
        for o in r["occurrences"]:
            if o["kind"] in ("glob_call", "path_argument"):
                t = o.get("target", "unknown")
                if r["file"] not in by_target[t]:
                    by_target[t].append(r["file"])
                c = o.get("consumer") or "unknown"
                consumers[c] = consumers.get(c, 0) + 1
            if o.get("dead_constant"):
                dead.append({"file": r["file"], "line": o["line"],
                             "name": o.get("assigned_to")})
    results_readers = sorted(by_target["results_dirs"])
    runner_readers = sorted(by_target["runner_sources"])

    comments = [r for r in rows if r["class"] == "comment"]
    detectors = [r for r in rows if r["class"] == "pattern_definition"]

    # members of E386's population that this study would not count as readers of the
    # results family (prose, dead constants, or a glob over the runner scripts instead)
    downgraded = sorted(f for f in parent if f not in results_readers)
    gained = sorted(f for f in results_readers if f not in parent)

    summary = {
        "text_hits": len(rows),
        "parent_population": len(parent),
        "results_family_readers": len(results_readers),
        "runner_source_readers": len(runner_readers),
        "comment_only_files": len(comments),
        "pattern_definition_files": len(detectors),
        "parent_members_downgraded": len(downgraded),
        "members_gained_vs_parent": len(gained),
        "consumer_classes": consumers,
        "reader_files": results_readers,
        "runner_source_reader_files": runner_readers,
        "dead_path_constants": len(dead),
    }
    if not rows:
        verdict = V_EMPTY
    elif not results_readers:
        verdict = V_PROSE_ONLY
    elif len(results_readers) == len(rows):
        verdict = V_ALL_COMPUTE
    else:
        verdict = V_MIXED

    return {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "generated_for_round": "r1406",
        "pattern": GLOB_PATTERN,
        "parent_face": os.path.relpath(PARENT_FACE, root).replace("\\", "/"),
        "verdict": verdict,
        "summary": summary,
        "rows": rows,
        "downgraded_members": downgraded,
        "gained_members": gained,
        "dead_constants": dead,
        "note": ("a text census counts mentions; a token census counts reads.  The same stem "
                 "also names a second family (scripts/trial_labor_w*.py), so a reader of the "
                 "runner sources is not a reader of the results directories."),
    }


def verify(root=ROOT):
    """Re-derive and compare against the face on disk; a mismatch is a seam, not noise."""
    problems = []
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    disk = json.load(io.open(path, encoding="utf-8"))
    live = build(root)
    for k in ("verdict", "summary"):
        if disk.get(k) != live.get(k):
            problems.append("%s does not re-derive" % k)
    if disk.get("pattern") != GLOB_PATTERN:
        problems.append("pattern drifted")
    return problems


FIXTURES = [
    ("# results/trial_labor_w*/checkpoint/ covers w9\nx = 1\n", ["comment"]),
    ('import re\nRX = re.compile(r"trial_labor_w\\*")\n', ["pattern_definition"]),
    ('import glob\nG = "results/trial_labor_w*"\nrows = sorted(glob.glob(G))\n',
     ["path_argument"]),
    ('import glob\nrows = len(glob.glob("results/trial_labor_w*"))\n', ["glob_call"]),
    ('import os\nP = os.path.join("results", "trial_labor_w*")\n',
     ["text"]),
    ('import os, glob\nP = os.path.join("results", "trial_labor_w*")\nfor d in sorted(glob.glob(P)):\n    print(d)\n',
     ["path_argument"]),
    ('import os, glob\nfor d in sorted(glob.glob(os.path.join(ROOT, "results", "trial_labor_w*"))):\n    pass\n',
     ["path_argument"]),
    # a dead path constant: the only later name is a different identifier
    ('import os, re\nP = os.path.join("results", "trial_labor_w*")\nPRX = re.compile(r"trial_labor_w\\*")\n',
     ["text", "pattern_definition"]),
]


def selftest():
    fails = []
    for i, (src, kinds) in enumerate(FIXTURES):
        got = [o["kind"] for o in classify_source(src)["occurrences"]]
        if got != kinds:
            fails.append("fixture %d: expected %s got %s" % (i, kinds, got))
    # consumer classification must not claim more than the statement shows
    c = classify_source(FIXTURES[2][0])
    o = c["occurrences"][0]
    if o.get("consumer") != "sorted":
        fails.append("fixture 2 consumer: expected sorted got %s" % o.get("consumer"))
    c3 = classify_source(FIXTURES[3][0])
    if c3["occurrences"][0].get("consumer") != "count":
        fails.append("fixture 3 consumer not count")
    # a comment-only file must never be graded as a reader
    if _file_class(classify_source(FIXTURES[0][0])["occurrences"]) != "comment":
        fails.append("comment file graded as a reader")
    # an empty corpus is empty, not prose-only
    if build(root=os.path.join(HERE, "_e389_no_such_tree"))["verdict"] != V_EMPTY:
        fails.append("empty tree did not grade V_EMPTY")
    # the scanner must not count itself (E180/E207 family)
    live = scan()
    if any(r["file"].endswith("e389_family_glob_readers.py") for r in live):
        fails.append("scanner counted its own source")
    # a glob over the runner scripts is a different family from the results directories
    live_doc = build()
    if set(live_doc["summary"]["reader_files"]) & set(
            live_doc["summary"]["runner_source_reader_files"]):
        fails.append("the two families were merged")
    total = len(FIXTURES) + 6
    print("selftest %d/%d" % (total - len(fails), total))
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "run":
        doc = build()
        os.makedirs(OUTDIR, exist_ok=True)
        with io.open(os.path.join(OUTDIR, FACE), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        mirror = dict(doc)
        mirror["face"] = FACE
        with io.open(os.path.join(OUTDIR, LATEST), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(mirror, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        s = doc["summary"]
        print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
        print("verdict: %s" % doc["verdict"])
        print("%d text hits / %d read the results family / %d read the runner sources / "
              "%d comment-only / %d dead path constants; parent %d -> %d downgraded, %d gained"
              % (s["text_hits"], s["results_family_readers"], s["runner_source_readers"],
                 s["comment_only_files"], s["dead_path_constants"], s["parent_population"],
                 s["parent_members_downgraded"], s["members_gained_vs_parent"]))
        for f in s["reader_files"]:
            print("  results reader:", f)
        for f in s["runner_source_reader_files"]:
            print("  runner reader:", f)
        return 0
    print("unknown mode: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))