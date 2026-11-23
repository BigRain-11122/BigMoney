#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Which cited faces can a fresh clone open -- and which of the rest are real defects?

r1990 (bm-c).  r1783 named a defect and r1987 fixed one instance of it by hand: a
script reads `results/<face>.json`, the file is on this machine, the reader is
committed -- and the face itself never entered git, so a fresh clone's smoke leg or
S6 leg opens nothing.  r1987 left the question open: "未核其它族是否有同类面在盘不在库".

`Tools/json_face_guard.py` cannot answer it: it enumerates *tracked* faces
(`git ls-files -- results`), so an untracked face is not merely clean, it is
invisible.  This census starts from the readers instead and asks, for every face
path a committed consumer literally names:

    is it on this disk, and can a clone of origin/main open it?

Two questions decide the answer, and the second one is what keeps this from crying
wolf: (a) is the citation in a *test* context -- the enclosing function is named
`selftest` / `test_*` / `*_fixture`, so the reader is exercising its own
missing-input branch with a path that must not exist; (b) if not, does the file
exist, and is it in git.

    TRACKED             exists, in the index                -> the clone opens it
    IGNORED             `.gitignore` says machine-local     -> never published, by design
    NEGATIVE_FIXTURE    cited only from a test function      -> "this face must be missing"
    ROUND_ARTIFACT      `_r<digits>bm?` round bookkeeping    -> never a published face
    MACHINE_SCOPED      named for another machine (`*.bm-a.json`) -> absence here is normal
    ABSENT_LOCALLY      in origin/main, not on this disk    -> one fetch away
    ORPHAN              **defect**: on disk, cited by real code, not in git
    DELETED_LOCALLY     **defect**: in the index, missing from the worktree
    DEAD_POINTER        **advisory**: real code names it and no clone has it -- this
                        census cannot tell "that branch has not run yet" from "stale
                        pointer after a rename", so it does not count as a defect

Severity: a citation from `smoke_test.py` or `Tools/s6_chain_bmc.py` is HARD -- those
two are the gates every other machine runs; anything else is SOFT.

Scope, stated so the numbers stay readable: committed Python readers only --
top-level `*.py`, `scripts/**/*.py`, `Tools/**/*.py`, minus `_`-prefixed one-off round
scripts.  Citations built at runtime (f-strings, os.path.join with a variable, glob)
are invisible to a literal scan, so every count here is a floor, not a ceiling.

Usage:
    python scripts/face_orphan_census.py run       # publish the face + page
    python scripts/face_orphan_census.py check     # re-derive and compare, no writes
    python scripts/face_orphan_census.py --selftest

Exit: 0 ok, 3 published face disagrees with the worktree (STALE), 2 mechanism.
"""
import argparse
import ast
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The group tree this repo sits inside (K:/Fluxgroup/FluxGroup).  Readers here
# legitimately cite its canon (docs/decisions.md, docs/orders.md, ...), which is
# absent from THIS repo by design and is therefore not a dead pointer.
GROUP_ROOT = os.path.dirname(os.path.dirname(ROOT))

# Built by concatenation on purpose: a literal "results/<x>.json" in this file would
# be read back by this very census as a citation of itself, and the face would flag
# itself as an orphan on its first run, before it has ever been committed.
OUT_JSON = os.path.join("results", "face_orphan_census" + ".json")
OUT_MD = os.path.join("research", "FACE-ORPHAN-CENSUS" + ".md")

CITE_RE = re.compile(
    # `.jsonl` before `.json` and a right boundary after the extension: without both,
    # a citation of `results/x/ledger.jsonl` is read as `results/x/ledger.json`, a file
    # that must not exist -- four of r1992's six "dead pointers" were that truncation.
    r"(?<![\w./\\-])((?:results|research|docs)/[A-Za-z0-9_.\-/]+"
    r"\.(?:jsonl|json|md|html))(?![\w])"
)
HARD_CONSUMERS = {"smoke_test.py", "Tools/s6_chain_bmc.py"}
SKIP_DIRS = {"__pycache__", ".git", ".codely-cli", "legacy", "Money02", "labbench"}
MAX_READ = 2 * 1024 * 1024
EXT_ORDER = {"json": 0, "md": 1, "html": 2}

TEST_WORDS = {"selftest", "selftests", "test", "tests", "fixture", "fixtures",
              "fake", "dummy", "dryrun", "dry_run"}
NAME_FIXTURE_TOKENS = ("no_such", "nope", "definitely_not_here", "does_not_exist",
                       "__")
ROUND_RE = re.compile(r"_r\d+(bm[abc])_", re.I)
MACHINE_TOKEN_RE = re.compile(r"(?:^|[._-])(bm[-_]?[abc])(?:[._-]|$)", re.I)
DEFECTS = ("ORPHAN", "DELETED_LOCALLY")
STATES = ("TRACKED", "IGNORED", "NEGATIVE_FIXTURE", "DOCUMENTED_EXAMPLE",
          "FIXTURE_LITERAL", "TEMPLATE_PLACEHOLDER", "ROUND_ARTIFACT",
          "MACHINE_SCOPED", "EXTERNAL_CANON", "ABSENT_LOCALLY", "ORPHAN",
          "DELETED_LOCALLY", "DEAD_POINTER")

# A citation is a *path* only if the string can be that file.  A usage line shows the
# shape of a name -- `REPORT-YYYYMMDD.md`, `results/...json`, `ENTRYDELAY-x.json` --
# and no clone will ever contain it, so counting those as dead pointers is noise that
# trains the reader to ignore the list (r1813: a gate that is always lit).
TEMPLATE_RE = re.compile(r"YYYY|(?<![A-Za-z])(?:MM|DD)(?![A-Za-z])|\.\.\.|%[ds]|\{|\}-x\.|-x\.",
                         re.I)


# ------------------------------------------------------------------ identity
def machine_id():
    """fleet/machine.json is the one place this file is allowed to learn who we are."""
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), "r",
                  encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id")
            if mid:
                return str(mid)
    except (OSError, ValueError):
        pass
    return "bm-c"


# ------------------------------------------------------------------ readers
def consumer_files():
    """Committed Python readers, one-off `_r####` scripts excluded.

    The `_`-prefix filter applies at the top level too: those round scripts are
    historical evidence, not readers anybody re-runs, and their citations would turn
    one-off files into "orphans" nobody needs.
    """
    out = []
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if name.endswith(".py") and not name.startswith("_") and os.path.isfile(p):
            out.append(name)
    for base in ("scripts", "Tools"):
        root = os.path.join(ROOT, base)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
                out.append(rel.replace("\\", "/"))
    return sorted(set(out))


def read_source(rel):
    p = os.path.join(ROOT, rel)
    try:
        if os.path.getsize(p) > MAX_READ:
            return ""
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def normalize(path):
    p = path.replace("\\", "/")
    while "//" in p:
        p = p.replace("//", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def citations(text):
    """Literal face paths in `text`; an angle-bracket metavariable is not one.

    `usage: <results/path.json> [--stage1 F]` names a *shape*: no file can carry `<`,
    so the string is documentation of the interface, not a reader of a face.
    """
    flat = text.replace("\\\\", "/")
    for m in CITE_RE.finditer(flat):
        if flat[m.start() - 1:m.start()] == "<" and flat[m.end():m.end() + 1] == ">":
            continue
        yield normalize(m.group(1))


def is_test_name(name):
    """`selftest_x`, `test_y`, `x_fixture` -- but not `latest`.

    Word-split, because a substring test makes `latest` a test and silently hides a
    real reader's face (r1990 second draft: `latest_bar` was being dropped).
    """
    low = name.lower()
    if "selftest" in low:
        return True
    return any(part in TEST_WORDS for part in re.split(r"_+", low))


def citations_with_context(src):
    """[(path, enclosing_function_or_None, kind)] via ast; None when the file will not parse.

    Enclosing-function identity is the only reliable way to tell a reader that tests
    its missing-input branch from a reader that expects a face: the literal path `a.json`
    is a fixture inside `selftest()` and a live path in `run()` -- the same string.

    `kind` answers the *other* half of r1990's noise, which function names cannot:
    a citation is a live path only when the string can be an argument to a writer or a
    reader.  Three shapes are not paths no matter which function holds them --

        docstring    a bare `Expr(Constant(str))` statement never opens a file; it is
                     the usage line a human reads (`--out=results/...json`)
        literal      a string inside a dict/list/tuple/set is data: a fixture run the
                     test writes, or a registry row; it is not an `open()` argument
        path         everything else, including a string assigned to a name, because
                     the name may be opened later
    """
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    out = []

    def emit(node, stack, kind):
        for path in citations(node.value):
            out.append((path, stack[-1] if stack else None, kind))

    def visit(node, stack):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, stack + [child.name])
            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant) \
                    and isinstance(child.value.value, str):
                emit(child.value, stack, "docstring")
            elif isinstance(child, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
                for sub in ast.walk(child):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        emit(sub, stack, "literal")
            else:
                if isinstance(child, ast.Constant) and isinstance(child.value, str):
                    emit(child, stack, "path")
                visit(child, stack)

    visit(tree, [])
    return out


def collect_citations(readers=None):
    """path -> {"readers": [...], "real_readers": [...], "doc_readers": [...], "literal_readers": [...]}.

    `real_readers` drops citations whose only home is a test function and citations that
    are not path-shaped at all (docstring usage lines, strings inside data literals).
    """
    readers = readers if readers is not None else consumer_files()
    cited = {}
    for rel in readers:
        src = read_source(rel)
        if not src:
            continue
        pairs = citations_with_context(src)
        if pairs is None:                      # unparsable: regex floor, no context
            pairs = [(p, None, "path") for p in citations(src)]
        for path, func, kind in pairs:
            rec = cited.setdefault(path, {"readers": set(), "real": set(),
                                          "doc": set(), "literal": set()})
            rec["readers"].add(rel)
            if kind == "docstring":
                rec["doc"].add(rel)
            elif kind == "literal":
                rec["literal"].add(rel)
            elif func is None or not is_test_name(func):
                rec["real"].add(rel)
    return {k: {"readers": sorted(v["readers"]),
                "real_readers": sorted(v["real"]),
                "doc_readers": sorted(v["doc"]),
                "literal_readers": sorted(v["literal"])}
            for k, v in cited.items()}


# ------------------------------------------------------------------ git
def _chunks(seq, n=400):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def tracked_set(paths):
    got = set()
    for ch in _chunks(sorted(set(paths))):
        p = subprocess.run(["git", "ls-files", "-z", "--"] + ch,
                           cwd=ROOT, capture_output=True)
        if p.returncode != 0:
            raise RuntimeError("git ls-files rc=%d %s"
                               % (p.returncode, p.stderr[:200]))
        for item in p.stdout.split(b"\x00"):
            if item:
                got.add(item.decode("utf-8", "replace").replace("\\", "/"))
    return got


def ignored_set(paths):
    got = set()
    for ch in _chunks(sorted(set(paths))):
        # -z means BOTH directions are NUL-separated: newline-joined input is read as
        # one enormous pathname and matches nothing -- silently zero ignored faces,
        # which would turn every machine-local face into an "orphan".  The batch leg
        # in --selftest pins this.
        data = ("\x00".join(ch) + "\x00").encode("utf-8")
        p = subprocess.run(["git", "check-ignore", "-z", "--stdin"],
                           cwd=ROOT, input=data, capture_output=True)
        if p.returncode not in (0, 1):
            raise RuntimeError("git check-ignore rc=%d %s"
                               % (p.returncode, p.stderr[:200]))
        for item in p.stdout.split(b"\x00"):
            if item:
                got.add(item.decode("utf-8", "replace").replace("\\", "/"))
    return got


def origin_set(paths, ref="origin/main"):
    """Paths that exist in the remote-tracking tree (so a clone would have them)."""
    got = set()
    for ch in _chunks(sorted(set(paths))):
        p = subprocess.run(["git", "ls-tree", "-z", ref, "--"] + ch,
                           cwd=ROOT, capture_output=True)
        if p.returncode != 0:
            raise RuntimeError("git ls-tree %s rc=%d %s"
                               % (ref, p.returncode, p.stderr[:200]))
        for item in p.stdout.split(b"\x00"):
            if not item:
                continue
            _meta, _sep, name = item.partition(b"\t")
            if name:
                got.add(name.decode("utf-8", "replace").replace("\\", "/"))
    return got


def group_set(paths):
    """Cited paths that exist in the group tree above this repo."""
    got = set()
    if os.path.abspath(GROUP_ROOT) == os.path.abspath(ROOT):
        return got
    for path in paths:
        if os.path.isfile(os.path.join(GROUP_ROOT, path.replace("/", os.sep))):
            got.add(path)
    return got


def head_date():
    p = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=short"],
                       cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        return datetime.date.today().isoformat()
    return (p.stdout or "").strip() or datetime.date.today().isoformat()


# ------------------------------------------------------------------ classify
def _basename(path):
    return path.rsplit("/", 1)[-1].lower()


def is_name_fixture(path):
    name = _basename(path)
    return any(t in name for t in NAME_FIXTURE_TOKENS)


def is_template_path(path):
    """The string is the *shape* of a name, not a name (`REPORT-YYYYMMDD.md`).

    Angle brackets are the other giveaway: `<results/path.json>` is an argparse
    metavariable in a usage epilog, and no file can carry a `<` in its name.
    """
    return bool(TEMPLATE_RE.search(_basename(path)) or "..." in path
                or "<" in path or ">" in path)


def foreign_machine(path, me):
    """The face is named for a machine that is not this one."""
    name = _basename(path)
    hit = MACHINE_TOKEN_RE.search(name)
    if hit and hit.group(1).lower().replace("-", "") != me.lower().replace("-", ""):
        return True
    rm = ROUND_RE.search(name)
    return bool(rm and rm.group(1).lower() != me.lower().replace("-", ""))


def classify(path, cited, tracked, ignored, in_origin, me, in_group=frozenset()):
    """-> (state, severity). `cited` is the record from collect_citations."""
    real = cited["real_readers"]
    doc = cited.get("doc_readers") or []
    lit = cited.get("literal_readers") or []
    exists = os.path.isfile(os.path.join(ROOT, path.replace("/", os.sep)))
    if exists:
        if path in tracked:
            return "TRACKED", None
        if path in ignored:
            return "IGNORED", None
        if not real:
            # a selftest that writes a scratch face: harmless, and publishing it
            # would be the wrong fix
            return ("FIXTURE_LITERAL" if lit and not doc else "DOCUMENTED_EXAMPLE",
                    None) if (lit or doc) else ("NEGATIVE_FIXTURE", None)
        if is_name_fixture(path):
            return "NEGATIVE_FIXTURE", None
        sev = "HARD" if any(c in HARD_CONSUMERS for c in real) else "SOFT"
        return "ORPHAN", sev
    # absent: ask *why* before calling anybody a defect
    if path in tracked:
        return "DELETED_LOCALLY", None
    if path in ignored:
        return "IGNORED", None
    if is_template_path(path):
        # `REPORT-YYYYMMDD.md` cannot exist under any date; nothing to publish
        return "TEMPLATE_PLACEHOLDER", None
    if not real:
        if lit and not doc:
            return "FIXTURE_LITERAL", None
        if doc or is_name_fixture(path):
            return "DOCUMENTED_EXAMPLE", None
        return "NEGATIVE_FIXTURE", None
    if is_name_fixture(path):
        return "NEGATIVE_FIXTURE", None
    if ROUND_RE.search(_basename(path)):
        return "ROUND_ARTIFACT", None
    if foreign_machine(path, me):
        return "MACHINE_SCOPED", None
    if path in in_group:
        return "EXTERNAL_CANON", None
    if path in in_origin:
        return "ABSENT_LOCALLY", None
    return "DEAD_POINTER", None


def build(cited=None, me=None):
    me = me or machine_id()
    cited = cited if cited is not None else collect_citations()
    paths = sorted(cited)
    tracked = tracked_set(paths)
    ignored = ignored_set(paths)
    absent = [p for p in paths
              if not os.path.isfile(os.path.join(ROOT, p.replace("/", os.sep)))]
    in_origin = origin_set(absent) if absent else set()
    in_group = group_set(absent) if absent else set()
    counts = {"cited": len(paths)}
    for st in STATES:
        counts[st] = 0
    rows = []
    for path in paths:
        state, sev = classify(path, cited[path], tracked, ignored, in_origin, me,
                              in_group)
        counts[state] += 1
        if state in DEFECTS or state == "DEAD_POINTER":
            rows.append({"path": path, "state": state, "severity": sev or "SOFT",
                         "cited_by": cited[path]["real_readers"] or
                         cited[path]["readers"]})
    rank = {"ORPHAN": 0, "DELETED_LOCALLY": 1, "DEAD_POINTER": 2}
    rows.sort(key=lambda r: (rank[r["state"]], r["severity"] != "HARD",
                             EXT_ORDER.get(r["path"].rsplit(".", 1)[-1], 9),
                             r["path"]))
    orphans = [r for r in rows if r["state"] == "ORPHAN"]
    deleted = [r for r in rows if r["state"] == "DELETED_LOCALLY"]
    dead = [r for r in rows if r["state"] == "DEAD_POINTER"]
    if orphans:
        verdict = "CITED_FACES_A_FRESH_CLONE_CANNOT_OPEN"
    elif deleted:
        verdict = "CITED_FACES_ARE_IN_THE_INDEX_BUT_MISSING_HERE"
    else:
        verdict = "EVERY_CITED_FACE_IS_IN_GIT_OR_MACHINE_LOCAL_BY_DESIGN"
    return {
        "tool": "face_orphan_census",
        "machine_id": me,
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": head_date(),
        "scope": {"readers": "top-level *.py + scripts/** + Tools/** (no _-prefixed)",
                  "literal_citations_only": True,
                  "test_context_excluded": True},
        "counts": counts,
        "hard_orphans": sum(1 for r in orphans if r["severity"] == "HARD"),
        "soft_orphans": sum(1 for r in orphans if r["severity"] == "SOFT"),
        "dead_pointers": len(dead),
        "verdict": verdict,
        "rows": rows,
    }


# ------------------------------------------------------------------ render
def _family(path):
    parts = path.split("/")
    return parts[0] + "/" + parts[1] if len(parts) > 2 else parts[0]


def render_md(face):
    c = face["counts"]
    orphans = [r for r in face["rows"] if r["state"] == "ORPHAN"]
    dead = [r for r in face["rows"] if r["state"] == "DEAD_POINTER"]
    deleted = [r for r in face["rows"] if r["state"] == "DELETED_LOCALLY"]
    lines = [
        "# Cited faces: what a clone can open, and what points nowhere",
        "",
        "generated %s | evidence_cutoff %s | machine %s"
        % (face["generated"], face["evidence_cutoff"], face["machine_id"]),
        "",
        "**Verdict: `%s`**" % face["verdict"],
        "",
        "%d face paths are literally named by a committed reader. %d are on disk and in "
        "git, %d are machine-local by `.gitignore` policy, and **%d are on disk but "
        "unreadable from a fresh clone** -- the r1783/r1987 defect."
        % (c["cited"], c["TRACKED"], c["IGNORED"], c["ORPHAN"]),
        "",
        "Citations live inside a `selftest` / `test_*` / `*_fixture` function are excluded "
        "(%d paths): those readers are exercising their own missing-input branch with a "
        "path that *must* not exist, and publishing it would be the wrong fix. Without "
        "that exclusion this census reported 167 \"dead pointers\", and the first draft "
        "counted `a.json` and `deadbeef.json` as evidence."
        % c["NEGATIVE_FIXTURE"],
        "",
        "| state | count | reading |",
        "|---|---|---|",
        "| TRACKED | %d | clone opens it |" % c["TRACKED"],
        "| IGNORED | %d | machine-local by policy, never published |" % c["IGNORED"],
        "| NEGATIVE_FIXTURE | %d | named only by a test — must be missing |" % c["NEGATIVE_FIXTURE"],
        "| DOCUMENTED_EXAMPLE | %d | named only inside a usage line / docstring |" % c["DOCUMENTED_EXAMPLE"],
        "| FIXTURE_LITERAL | %d | a string inside a data literal, never an `open()` argument |" % c["FIXTURE_LITERAL"],
        "| TEMPLATE_PLACEHOLDER | %d | the *shape* of a name (`REPORT-YYYYMMDD.md`) |" % c["TEMPLATE_PLACEHOLDER"],
        "| ROUND_ARTIFACT | %d | `_r####bm?` round bookkeeping |" % c["ROUND_ARTIFACT"],
        "| MACHINE_SCOPED | %d | another machine's local state |" % c["MACHINE_SCOPED"],
        "| EXTERNAL_CANON | %d | lives in the group tree above this repo |" % c["EXTERNAL_CANON"],
        "| ABSENT_LOCALLY | %d | in origin, not on this disk — one fetch |" % c["ABSENT_LOCALLY"],
        "| ORPHAN | %d | **defect**: on disk, cited by real code, not in git |" % c["ORPHAN"],
        "| DELETED_LOCALLY | %d | **defect**: in the index, gone from disk |" % c["DELETED_LOCALLY"],
        "| DEAD_POINTER | %d | advisory: real code names it, no clone has it |" % c["DEAD_POINTER"],
        "",
    ]
    quoted = [r for r in face["rows"] if r["state"] in
              ("DOCUMENTED_EXAMPLE", "FIXTURE_LITERAL", "TEMPLATE_PLACEHOLDER")]
    if quoted:
        lines += ["## Quoted, not read (advisory, by design)", "",
                  "These strings appear in committed code but no reader can open them: a "
                  "usage line shows the shape of a name, a fixture literal is data a test "
                  "compares against, and a template can never be a file. Keeping them out "
                  "of the defect count is what makes the rest of the list worth reading -- "
                  "if they were counted, %d of the %d citations here would be noise."
                  % (len(quoted), c["cited"]), "",
                  "| state | path | cited by |", "|---|---|---|"]
        for r in sorted(quoted, key=lambda r: (r["state"], r["path"])):
            lines.append("| %s | `%s` | %s |"
                         % (r["state"], r["path"], ", ".join(r["cited_by"])))
        lines.append("")
    if orphans:
        hard = [r for r in orphans if r["severity"] == "HARD"]
        soft = [r for r in orphans if r["severity"] == "SOFT"]
        lines += ["## Orphans — publish these", ""]
        if hard:
            lines += ["**HARD** — a gate every machine runs reads them "
                      "(`smoke_test.py` / S6):", ""]
            for r in hard:
                lines.append("- `%s` ← %s" % (r["path"], ", ".join(r["cited_by"])))
            lines.append("")
        if soft:
            fam = {}
            for r in soft:
                fam.setdefault(_family(r["path"]), []).append(r)
            lines += ["**SOFT** — an analysis reader reads them:", ""]
            for k in sorted(fam, key=lambda k: (-len(fam[k]), k)):
                lines.append("`%s` (%d)" % (k, len(fam[k])))
                for r in fam[k]:
                    lines.append("- `%s` ← %s" % (r["path"], ", ".join(r["cited_by"])))
                lines.append("")
    if deleted:
        lines += ["## Deleted but still in the index", "",
                  "Tracked, missing from the worktree: the clone has the file, this "
                  "checkout does not. Either someone deleted it without `git rm`, or a "
                  "restore is half-finished.", ""]
        for r in deleted:
            lines.append("- `%s` ← %s" % (r["path"], ", ".join(r["cited_by"])))
        lines.append("")
    if dead:
        fam = {}
        for r in dead:
            fam.setdefault(_family(r["path"]), []).append(r)
        hard_dead = [r for r in dead if r["severity"] == "HARD"]
        lines += ["## Dead pointers (advisory)", "",
                  "Real code (not a test) names these and no clone has them. Either that "
                  "branch has never run, or the file was renamed and the reader was not "
                  "updated. Neither is an orphan -- there is nothing on disk to publish -- "
                  "and this census cannot separate the two cases, so they are listed, not "
                  "counted as defects.", "",
                  "| family | count | examples |", "|---|---|---|"]
        for k in sorted(fam, key=lambda k: (-len(fam[k]), k)):
            ex = ", ".join("`%s`" % r["path"].split("/", 1)[-1] for r in fam[k][:3])
            lines.append("| %s | %d | %s |" % (k, len(fam[k]), ex))
        lines.append("")
        if hard_dead:
            lines += ["**HARD (a gate reads them):**", ""]
            for r in hard_dead:
                lines.append("- `%s` ← %s" % (r["path"], ", ".join(r["cited_by"])))
            lines.append("")
    lines += [
        "## How to read this",
        "",
        "An ORPHAN is not a broken number -- it is a number nobody else can read. The face "
        "was computed here, a committed reader names it, and the file never entered git, so "
        "the same reader on another machine or in a fresh clone gets nothing (or, worse, "
        "catches the error and continues: the r98 shape, where a missing face is printed as "
        "zero). Adding the file to git is the whole fix.",
        "",
        "Limits: (1) literal citations only -- paths assembled at runtime are invisible, so "
        "every count is a floor; (2) IGNORED comes from `.gitignore` policy and is not audited "
        "for whether that policy is still right; (3) the test-context filter trusts function "
        "names, so a real reader whose function happens to be called `test_*` would be hidden, "
        "and a fixture in a function with an innocent name shows up as an orphan; (4) the ast "
        "walk falls back to a context-free regex on files that will not parse, and those "
        "citations count as real; (5) ABSENT_LOCALLY is measured against `origin/main` as of "
        "this run, so a machine whose peer has not pushed yet looks the same as one behind.",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ modes
def cmd_run(write=True):
    face = build()
    if write:
        jp = os.path.join(ROOT, OUT_JSON)
        os.makedirs(os.path.dirname(jp), exist_ok=True)
        with open(jp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        mp = os.path.join(ROOT, OUT_MD)
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        with open(mp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_md(face))
    c = face["counts"]
    print("face-orphan-census %s cited=%d tracked=%d ignored=%d orphan=%d (hard %d) "
          "deleted=%d dead_advisory=%d absent_locally=%d fixtures=%d round=%d "
          "machine=%d group_canon=%d quoted=%d"
          % (face["verdict"], c["cited"], c["TRACKED"], c["IGNORED"], c["ORPHAN"],
             face["hard_orphans"], c["DELETED_LOCALLY"], c["DEAD_POINTER"],
             c["ABSENT_LOCALLY"], c["NEGATIVE_FIXTURE"], c["ROUND_ARTIFACT"],
             c["MACHINE_SCOPED"], c["EXTERNAL_CANON"],
             c["DOCUMENTED_EXAMPLE"] + c["FIXTURE_LITERAL"] + c["TEMPLATE_PLACEHOLDER"]))
    for r in face["rows"]:
        print("  %-16s %-5s %s  <- %s"
              % (r["state"], r["severity"], r["path"], ", ".join(r["cited_by"])))
    return 0


def cmd_check():
    jp = os.path.join(ROOT, OUT_JSON)
    if not os.path.isfile(jp):
        print("STALE face missing: %s" % OUT_JSON)
        return 3
    with open(jp, "r", encoding="utf-8") as fh:
        published = json.load(fh)
    fresh = build()
    diffs = []
    for key in ("verdict", "counts", "hard_orphans", "soft_orphans", "dead_pointers"):
        if published.get(key) != fresh.get(key):
            diffs.append(key)

    def _paths(face):
        return sorted((r["path"], r["state"], r["severity"]) for r in face.get("rows", []))
    if _paths(published) != _paths(fresh):
        diffs.append("rows")
    if diffs:
        print("STALE published face disagrees with the worktree: %s" % ", ".join(diffs))
        print("  published: %s orphan=%s dead=%s" % (published.get("verdict"),
              published.get("counts", {}).get("ORPHAN"),
              published.get("counts", {}).get("DEAD_POINTER")))
        print("  now:       %s orphan=%s dead=%s" % (fresh["verdict"],
              fresh["counts"]["ORPHAN"], fresh["counts"]["DEAD_POINTER"]))
        return 3
    c = fresh["counts"]
    print("CHECK_OK %s cited=%d orphan=%d hard=%d deleted=%d dead_advisory=%d"
          % (fresh["verdict"], c["cited"], c["ORPHAN"], fresh["hard_orphans"],
             c["DELETED_LOCALLY"], c["DEAD_POINTER"]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    me = machine_id()
    leg("machine_id comes from fleet/machine.json", me.startswith("bm-"), me)

    leg("tracked_set sees a tracked file", ".gitignore" in tracked_set([".gitignore"]))
    leg("ignored_set sees a machine-local face",
        "results/watermark.jsonl" in ignored_set(["results/watermark.jsonl"]))

    # check-ignore -z --stdin wants NUL input; a newline-joined batch matches nothing
    # and every ignored face silently becomes an "orphan".
    batch = ignored_set(["results/watermark.jsonl", "results/watermark_red.json",
                         "results/_quarantine/a.json", ".gitignore"])
    leg("ignored_set splits a batch (NUL input, not newline)",
        {"results/watermark.jsonl", "results/watermark_red.json"} <= batch
        and ".gitignore" not in batch, sorted(batch))

    readers = consumer_files()
    leg("consumer_files skips _-prefixed one-off scripts",
        not any(os.path.basename(r).startswith("_") for r in readers),
        str([r for r in readers if os.path.basename(r).startswith("_")][:3]))

    leg("normalize strips ./ and collapses slashes",
        normalize(".\\results\\\\a.json") == "results/a.json"
        and normalize("./results/a.json") == "results/a.json")

    found = sorted(citations("see results/ dir; read results/a.json and research/B.md"))
    leg("citations picks files and skips the bare directory",
        found == ["research/B.md", "results/a.json"], str(found))
    fnd = sorted(citations("see results/x/ledger.jsonl and results/y.json"))
    leg("citations does not truncate .jsonl to .json",
        fnd == ["results/x/ledger.jsonl", "results/y.json"], str(fnd))
    meta = list(citations("usage: <results/path.json> [--stage1 F]"))
    leg("an angle-bracket metavariable is not a citation", meta == [], str(meta))

    # test-context detection: word-split, so `latest` is not a test
    leg("is_test_name is word-split (latest is not a test)",
        is_test_name("selftest_git_reach") and is_test_name("test_funnel")
        and is_test_name("_fixture_paths") and not is_test_name("latest_bar")
        and not is_test_name("run"), "")

    # the same literal string, two functions, two different answers
    src = (
        "def selftest():\n"
        "    return open('results/a.json')\n"
        "def run():\n"
        "    return open('results/b.json')\n"
    )
    ctx = dict()
    kinds = dict()
    for path, func, kind in citations_with_context(src):
        ctx.setdefault(path, set()).add(func)
        kinds[path] = kind
    leg("ast gives the enclosing function per citation",
        ctx.get("research/x") is None and sorted(ctx) == ["results/a.json", "results/b.json"]
        and ctx["results/a.json"] == {"selftest"} and ctx["results/b.json"] == {"run"},
        str(ctx))
    leg("an open() argument is a path, not a quote",
        kinds.get("results/b.json") == "path", str(kinds))

    # r1992: three shapes that are not paths, no matter which function holds them
    doc_src = 'def run():\n    """usage: python x.py --out=results/foo.json"""\n    return 1\n'
    doc_kinds = {p: k for p, _f, k in citations_with_context(doc_src)}
    leg("a usage line in a docstring is not a path",
        doc_kinds.get("results/foo.json") == "docstring", str(doc_kinds))
    lit_src = 'def run():\n    return {"result": "results/b.json"}\n'
    lit_kinds = {p: k for p, _f, k in citations_with_context(lit_src)}
    leg("a string inside a data literal is not a path",
        lit_kinds.get("results/b.json") == "literal", str(lit_kinds))
    leg("a template name is not a file",
        is_template_path("docs/daily_report/REPORT-YYYYMMDD.md")
        and is_template_path("results/...json")
        and is_template_path("results/e44_midmonth/ENTRYDELAY-x.json")
        and is_template_path("<results/path.json>")
        and not is_template_path("results/etf_book_order/ledger.jsonl"),
        "template detector")

    # severity comes from the consumer, not from the face
    probe = "results/_selftest_probe_%d.json" % os.getpid()
    pp = os.path.join(ROOT, probe)
    try:
        with open(pp, "w", encoding="utf-8") as fh:
            fh.write("{}\n")
        tt, ii = tracked_set([probe]), ignored_set([probe])
        hard = {"readers": ["smoke_test.py"], "real_readers": ["smoke_test.py"]}
        soft = {"readers": ["scripts/x.py"], "real_readers": ["scripts/x.py"]}
        st_hard, sev_hard = classify(probe, hard, tt, ii, set(), me)
        st_soft, sev_soft = classify(probe, soft, tt, ii, set(), me)
        leg("untracked+not-ignored+on-disk+real citation is ORPHAN",
            st_hard == "ORPHAN" and st_soft == "ORPHAN", "%s/%s" % (st_hard, st_soft))
        leg("a gate citation is HARD, an analysis citation is SOFT",
            sev_hard == "HARD" and sev_soft == "SOFT", "%s/%s" % (sev_hard, sev_soft))
        # a scratch face only a selftest writes is not something to publish
        only_test = {"readers": ["scripts/x.py"], "real_readers": []}
        st, _ = classify(probe, only_test, tt, ii, set(), me)
        leg("a face cited only from a test is NEGATIVE_FIXTURE", st == "NEGATIVE_FIXTURE", st)
    finally:
        if os.path.exists(pp):
            os.remove(pp)

    real = {"readers": ["scripts/x.py"], "real_readers": ["scripts/x.py"]}
    # the reasons a real citation can be legitimately absent
    st, _ = classify("results/_r1049bmb_roll.json", real, set(), set(), set(), me)
    leg("another machine's round artifact is ROUND_ARTIFACT", st == "ROUND_ARTIFACT", st)
    st, _ = classify("results/_sentinel_bm-a.json", real, set(), set(), set(), me)
    leg("another machine's local state is MACHINE_SCOPED", st == "MACHINE_SCOPED", st)
    if os.path.isfile(os.path.join(GROUP_ROOT, "docs", "decisions.md")):
        found_group = group_set(["docs/decisions.md"])
        leg("group_set finds group-tree canon",
            "docs/decisions.md" in found_group, str(found_group))
        st, _ = classify("docs/decisions.md", real, set(), set(), set(), me,
                         {"docs/decisions.md"})
        leg("group-tree canon is EXTERNAL_CANON, not a dead pointer",
            st == "EXTERNAL_CANON", st)
    else:
        leg("group-tree canon is EXTERNAL_CANON, not a dead pointer", True,
            "skipped: group tree absent")
    plain = "results/plain_absent_face_%d.json" % os.getpid()
    st, _ = classify(plain, real, set(), set(), {plain}, me)
    leg("a plain path in origin is ABSENT_LOCALLY", st == "ABSENT_LOCALLY", st)
    st, _ = classify(plain, real, set(), set(), set(), me)
    leg("a plain path nobody has is DEAD_POINTER", st == "DEAD_POINTER", st)
    # ...and the three shapes that only look like a pointer (r1992)
    doc_rec = {"readers": ["scripts/x.py"], "real_readers": [],
               "doc_readers": ["scripts/x.py"], "literal_readers": []}
    st, _ = classify(plain, doc_rec, set(), set(), set(), me)
    leg("a face named only in a docstring is DOCUMENTED_EXAMPLE",
        st == "DOCUMENTED_EXAMPLE", st)
    lit_rec = {"readers": ["scripts/x.py"], "real_readers": [],
               "doc_readers": [], "literal_readers": ["scripts/x.py"]}
    st, _ = classify(plain, lit_rec, set(), set(), set(), me)
    leg("a fixture literal is FIXTURE_LITERAL, not a dead pointer",
        st == "FIXTURE_LITERAL", st)
    st, _ = classify("docs/daily_report/REPORT-YYYYMMDD.md", real, set(), set(), set(), me)
    leg("a template is TEMPLATE_PLACEHOLDER even from real code",
        st == "TEMPLATE_PLACEHOLDER", st)
    st, _ = classify("results/plain_gone.json", real, {"results/plain_gone.json"},
                     set(), set(), me)
    leg("tracked but missing from disk is DELETED_LOCALLY", st == "DELETED_LOCALLY", st)
    leg("a real face name is not read as a fixture",
        not is_name_fixture("results/etf_book_forward/LEDGER.json"))

    # the census never writes the faces it reads
    jp = os.path.join(ROOT, OUT_JSON)
    before = os.path.getmtime(jp) if os.path.isfile(jp) else None
    build(me=me)
    after = os.path.getmtime(jp) if os.path.isfile(jp) else None
    leg("build() does not touch the published face", before == after)

    if os.path.isfile(jp):
        with open(jp, "r", encoding="utf-8") as fh:
            face = json.load(fh)
        leg("published face carries verdict+cutoff+counts+machine",
            face.get("verdict") and face.get("evidence_cutoff")
            and isinstance(face.get("counts"), dict) and face.get("machine_id"))
    else:
        leg("published face carries verdict+cutoff+counts+machine", True,
            "skipped: nothing published yet")

    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, detail in legs:
        print("  %s %s%s" % ("PASS" if ok else "FAIL", n,
                             ("  [%s]" % detail) if detail and not ok else ""))
    print("selftest %d/%d %s" % (len(legs) - len(bad), len(legs),
                                 "PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            return selftest()
        if args.mode == "check":
            return cmd_check()
        return cmd_run()
    except RuntimeError as exc:
        print("MECHANISM: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
