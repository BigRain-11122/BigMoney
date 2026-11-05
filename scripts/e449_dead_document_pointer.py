"""E449: E448 graded 30 dropped compositions as opened nowhere in their own file, and 25 of them
name a path that already exists.  The largest single family is a research-note pointer: a study
script composes `os.path.join(ROOT, "research", "<STUDY>-P1.md")` into a PREREG constant and never
opens it.

A pointer to a note is harmless when the note is documentation and the code never claims to have
read it, and it is a claim with nothing behind it when the code says "our prereg" and the string is
the only link.  That difference is measurable: for each dropped composition that resolves under
research/ or docs/ and exists on disk, this study asks

  1. does any `.py` in the corpus open that note -- i.e. does any opener call take an argument whose
     source segment carries the note's basename, directly or through a same-file constant?
  2. failing that, is the note cited in *code text* -- a docstring, a comment, a log line, a printed
     receipt -- anywhere in the corpus?
  3. failing that, is it cited at all outside the declaring file (prose in .md/.txt)?
  4. and, for the declaring file only: is the constant named there used anywhere beyond its own
     assignment (a printed receipt, a guard, a function argument)?  A name that is assigned and
     never read again cannot be said to gate anything.

Classes published per row (frozen vocabulary):

    read_by_an_opener_elsewhere      some .py (other than the declaring file) opens the note
    cited_in_code_text_only          no opener anywhere; a .py names it in a string/comment/log
    cited_in_prose_only              no opener, no code-text citation; only .md/.txt mentions it
    declared_and_unread_in_code      nothing in the corpus names it beyond its own assignment line

Rows whose composition does not land on an existing document under research/ or docs/ are published
in `out_of_scope_rows` with the reason, so the 30-row population is never silently narrowed.

Usage:
    python scripts/e449_dead_document_pointer.py run|verify|check|selftest

`check` re-derives every tally and every class from the published rows (fast, no walk).  `verify`
re-runs the corpus walk against the live tree and refuses a face that no longer re-derives.
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "deadprereg_latest.json"
DATED_PREFIX = "DEADPREREG"
CARD = "E449-WHICH-DEAD-PREREG-POINTER-IS-A-DOCUMENT-NO-STUDY-CODE-EVER-READS"
SOURCE_FACE = "droppedpath_latest.json"
SOURCE_CLASS = "opened_nowhere_in_the_file"
SELF_SKIP = ("e449", "run_e449", "e448_dropped_path")

SKIP_DIRS = frozenset({
    ".git", "node_modules", "__pycache__", ".codely-cli", "_quarantine", ".mypy_cache",
    ".pytest_cache", "venv", ".venv",
})
DOC_DIRS = ("research/", "docs/")
TEXT_EXTS = (".py", ".md", ".txt")
MAX_SEGMENT = 140

K_READ = "read_by_an_opener_elsewhere"
K_CODE_TEXT = "cited_in_code_text_only"
K_PROSE = "cited_in_prose_only"
K_DECLARED = "declared_and_unread_in_code"
CLASS_VOCAB = (K_READ, K_CODE_TEXT, K_PROSE, K_DECLARED)

V_NONE = "no_dropped_composition_names_a_document_under_research_or_docs"
V_ALL_READ = "every_dropped_document_pointer_is_opened_by_an_opener_somewhere_in_the_corpus"
V_CODE_TEXT = "some_dropped_document_pointers_are_named_in_code_text_but_never_opened"
V_PROSE = "some_dropped_document_pointers_are_cited_only_in_prose"
V_DECLARED = "no_dropped_document_pointer_is_named_anywhere_beyond_its_own_assignment"
VERDICT_VOCAB = (V_NONE, V_ALL_READ, V_CODE_TEXT, V_PROSE, V_DECLARED)

OPENER_TAILS = frozenset({
    "open", "read_text", "read_bytes", "readlines", "read_csv", "read_parquet", "read_json",
    "read_excel", "read_table", "read_feather", "read_pickle", "loadtxt", "load", "loads",
    "write_text", "write_bytes", "to_csv", "to_parquet", "to_json", "dump", "writelines",
})


# ---------------------------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------------------------
def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def rel(path: str) -> str:
    """Repo-relative, forward-slash form; a foreign absolute path keeps its tail after the repo."""
    p = path.replace("\\", "/")
    root = ROOT.replace("\\", "/")
    if p.lower().startswith(root.lower() + "/"):
        return p[len(root) + 1:]
    marker = "/quant/bigmoney/"
    if marker in p.lower():
        i = p.lower().index(marker) + len(marker)
        return p[i:]
    return p


def norm_target(key):
    """E448 publishes some keys repo-relative and some as absolute `K:/...` paths."""
    if not key:
        return None
    r = rel(key)
    if re.match(r"^[a-zA-Z]:/", r):
        return None
    return r.lstrip("./") if r.startswith("./") else r


def kind_of(target):
    base = os.path.basename(target)
    if "*" in target or "?" in target:
        return "pattern"
    if "." not in base:
        return "directory"
    return "file"


def in_doc_scope(target):
    t = target.replace("\\", "/")
    return any(t.startswith(d) for d in DOC_DIRS) and t.lower().endswith(".md")


def walk_corpus_files():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(TEXT_EXTS):
                continue
            if any(name.startswith(s) for s in SELF_SKIP):
                continue
            out.append(os.path.join(base, name))
    return out


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return None


def _segment(lines, node):
    """Source text of one node from a line table.

    ast.get_source_segment re-splits the whole source per call (E442's 16 min -> 44 s lesson), so
    every node is cut from the already-split table instead.
    """
    lo = getattr(node, "lineno", None)
    hi = getattr(node, "end_lineno", None)
    if not lo or not hi or hi < lo or hi > len(lines):
        return ""
    return "".join(lines[lo - 1:hi])


def opener_evidence(text, path, basename):
    """Openers whose argument segment carries the basename, directly or via a same-file constant."""
    if basename not in text:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.splitlines(keepends=True)

    const_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Call, ast.BinOp)):
            seg = _segment(lines, node.value)
            if basename in seg:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        const_names.add(t.id)

    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        tail = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if tail not in OPENER_TAILS:
            continue
        args = list(node.args) + [k.value for k in node.keywords]
        for a in args:
            seg = _segment(lines, a)
            reason = None
            if basename in seg:
                reason = "literal"
            else:
                for n in ast.walk(a):
                    if isinstance(n, ast.Name) and n.id in const_names:
                        reason = "via_const:%s" % n.id
                        break
            if reason:
                found.append({
                    "file": rel(path),
                    "line": getattr(node, "lineno", 0),
                    "callee": tail,
                    "reason": reason,
                    "segment": seg[:MAX_SEGMENT],
                })
                break
    return found


def text_citation(text, path, basename, stem, own_file, own_line):
    """Lines in a .py that name the note *file* outside the declaring assignment.

    A mention of the study stem alone (FUND-QUALITY-P1) is not a citation of the note: the stem is
    the study id and appears in every closeout script that touches the study.  Only the basename
    with its extension is evidence that the document itself was named.
    """
    hits = []
    stem_only = []
    for i, line in enumerate(text.splitlines(), 1):
        if own_file and i == own_line:
            continue
        stripped = line.strip()
        kind = "comment" if stripped.startswith("#") else "code_text"
        if basename in line:
            hits.append({"file": rel(path), "line": i, "kind": kind,
                         "text": stripped[:MAX_SEGMENT]})
        elif stem and stem in line:
            stem_only.append({"file": rel(path), "line": i,
                              "text": stripped[:MAX_SEGMENT]})
    return hits, stem_only


def binding_usage(path, binding, own_line):
    """How often the declaring file names its own constant beyond the assignment."""
    text = read_text(path)
    if text is None:
        return {"references": 0, "kinds": {}, "samples": [], "file_readable": False}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"references": 0, "kinds": {}, "samples": [], "file_readable": False}
    src = "".join(text.splitlines(keepends=True))
    kinds = {}
    samples = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == binding and isinstance(node.ctx, ast.Load):
            parent_kind = "load"
            seg = ast.get_source_segment(src, node) or binding
            kinds[parent_kind] = kinds.get(parent_kind, 0) + 1
            if len(samples) < 5:
                samples.append({"line": node.lineno, "segment": seg[:MAX_SEGMENT]})
    return {"references": sum(kinds.values()), "kinds": kinds, "samples": samples,
            "file_readable": True}


def classify(row_reads, code_text, prose, exists, scope):
    if not scope:
        return None
    if not exists:
        return None
    if row_reads:
        return K_READ
    if code_text:
        return K_CODE_TEXT
    if prose:
        return K_PROSE
    return K_DECLARED


def verdict_for(rows, out_of_scope):
    graded = [r for r in rows if r.get("class") in CLASS_VOCAB]
    if not graded:
        return V_NONE
    classes = {r["class"] for r in graded}
    if classes == {K_READ}:
        return V_ALL_READ
    if K_CODE_TEXT in classes:
        return V_CODE_TEXT
    if K_PROSE in classes:
        return V_PROSE
    return V_DECLARED


# ---------------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------------
def build():
    src_path = os.path.join(ST, SOURCE_FACE)
    src = json.load(open(src_path, encoding="utf-8"))
    src_rows = [r for r in src.get("rows") or [] if r.get("class") == SOURCE_CLASS]
    src_summary = src.get("summary") or {}

    targets = {}
    for r in src_rows:
        t = norm_target(r.get("composed_key"))
        if t and in_doc_scope(t):
            targets.setdefault(os.path.basename(t), []).append(r)

    files = walk_corpus_files()
    texts = {}
    for p in files:
        t = read_text(p)
        if t is not None:
            texts[p] = t

    rows = []
    out_of_scope = []
    code_cite_files = set()
    prose_cite_files = set()
    for r in src_rows:
        target = norm_target(r.get("composed_key"))
        k = kind_of(target) if target else None
        scope = bool(target and in_doc_scope(target))
        exists = bool(target and os.path.exists(os.path.join(ROOT, target)))
        if not scope:
            out_of_scope.append({
                "file": r.get("file"), "line": r.get("line"), "binding": r.get("binding"),
                "target": target, "kind": k,
                "reason": ("target_not_resolvable" if not target else
                           ("not_a_file" if k in ("directory", "pattern") else
                            "outside_research_or_docs")),
            })
            continue
        base = os.path.basename(target)
        stem = base[:-3] if base.lower().endswith(".md") else base
        owner = r.get("file")
        reads, code_text, prose, stem_only, prose_stem = [], [], [], [], []
        if exists:
            for p, t in texts.items():
                if base not in t and stem not in t:
                    continue
                if p.endswith(".py"):
                    if rel(p) != owner:
                        reads.extend(opener_evidence(t, p, base))
                    ct, so = text_citation(t, p, base, stem, rel(p) == owner, r.get("line"))
                    code_cite_files.update(c["file"] for c in ct)
                    code_text.extend(ct)
                    stem_only.extend(so)
                else:
                    for i, line in enumerate(t.splitlines(), 1):
                        if base in line:
                            prose_cite_files.add(rel(p))
                            prose.append({"file": rel(p), "line": i,
                                          "text": line.strip()[:MAX_SEGMENT]})
                            break
                        if stem and stem in line:
                            prose_stem.append({"file": rel(p), "line": i,
                                               "text": line.strip()[:MAX_SEGMENT]})
                            break
        usage = binding_usage(os.path.join(ROOT, owner), r.get("binding"), r.get("line")) \
            if r.get("binding") else {"references": 0, "kinds": {}, "samples": [],
                                      "file_readable": False}
        rows.append({
            "file": owner, "line": r.get("line"), "col": r.get("col"),
            "binding": r.get("binding"), "expression": r.get("expression"),
            "target": target, "on_disk": exists,
            "read_by_opener": reads[:5], "read_by_opener_count": len(reads),
            "code_text_citations": code_text[:5], "code_text_citation_count": len(code_text),
            "code_text_study_id_mentions": stem_only[:5],
            "code_text_study_id_mention_count": len(stem_only),
            "prose_citations": prose[:5], "prose_citation_count": len(prose),
            "prose_study_id_mentions": prose_stem[:5],
            "prose_study_id_mention_count": len(prose_stem),
            "constant_references_beyond_assignment": usage["references"],
            "constant_reference_samples": usage["samples"],
            "class": classify(reads, code_text, prose, exists, scope),
        })

    rows.sort(key=lambda r: (r["class"] or "", r["file"], r["line"] or 0))
    by_class = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1

    summary = {
        "population": len(src_rows),
        "population_source": SOURCE_FACE,
        "population_source_class": SOURCE_CLASS,
        "source_orphan_sites": src_summary.get("orphan_sites"),
        "document_rows": len(rows),
        "out_of_scope_rows": len(out_of_scope),
        "out_of_scope_reasons": {},
        "by_class": by_class,
        "notes_absent_from_disk": sum(1 for r in rows if not r["on_disk"]),
        "rows_with_any_opener_evidence": sum(1 for r in rows if r["read_by_opener_count"]),
        "rows_named_in_code_text": sum(1 for r in rows if r["code_text_citation_count"]),
        "rows_cited_only_in_prose": sum(1 for r in rows if r["class"] == K_PROSE),
        "rows_whose_constant_is_never_read_again":
            sum(1 for r in rows if not r["constant_references_beyond_assignment"]),
        "rows_mentioned_by_study_id_only":
            sum(1 for r in rows if r["class"] == K_DECLARED
                and (r["code_text_study_id_mention_count"] or r["prose_study_id_mention_count"])),
        "study_id_mentions_excluded_from_the_class":
            sum(r["code_text_study_id_mention_count"] + r["prose_study_id_mention_count"]
                for r in rows),
        "distinct_code_files_naming_a_note": len(code_cite_files),
        "distinct_prose_files_naming_a_note": len(prose_cite_files),
        "corpus_files_walked": len(files),
        "corpus_py_files": sum(1 for p in files if p.endswith(".py")),
        "walk_exclusions": sorted(SKIP_DIRS),
        "class_vocabulary": list(CLASS_VOCAB),
    }
    for o in out_of_scope:
        summary["out_of_scope_reasons"][o["reason"]] = \
            summary["out_of_scope_reasons"].get(o["reason"], 0) + 1

    return {
        "card": CARD,
        "study": "E449_which_dead_prereg_pointer_is_a_document_no_study_code_ever_reads",
        "title": "a dropped research-note pointer: is the note opened, cited in code, cited in "
                 "prose, or only assigned",
        "evidence_cutoff": str(date.today()),
        "generated": "static AST + read-only corpus text walk; no file outside results/state_tilt "
                     "is written",
        "source_face": SOURCE_FACE,
        "source_face_sha16": _sha16(json.dumps(src, sort_keys=True)),
        "method_limits": [
            "opener evidence means an opener call whose argument source segment carries the note "
            "basename, directly or through a same-file constant: a path assembled in another "
            "module and imported here is not followed",
            "a citation means the note *file name* (with its .md extension); a mention of the "
            "study id alone is counted separately as study_id_mentions_excluded_from_the_class "
            "because that stem appears in every closeout script that touches the study",
            "a prose citation is counted once per file (first matching line) and is not evidence "
            "that a human read the note",
            "the constant-use count reads ast.Name loads in the declaring file only",
            "rows outside research/*.md with an existing file are published in out_of_scope_rows "
            "with a reason, not graded",
        ],
        "rows": rows,
        "out_of_scope_rows": out_of_scope,
        "summary": summary,
        "verdict": verdict_for(rows, out_of_scope),
    }


# ---------------------------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------------------------
def tally_problems(face):
    bad = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    oos = face.get("out_of_scope_rows") or []
    pop = s.get("population")
    if pop is not None and pop != len(rows) + len(oos):
        bad.append("population does not close over graded plus out-of-scope rows")
    bc = s.get("by_class") or {}
    want = {}
    for r in rows:
        want[r.get("class")] = want.get(r.get("class"), 0) + 1
    if bc != want:
        bad.append("the class tally does not re-derive from the rows")
    if sum(bc.values()) != len(rows):
        bad.append("the class tally does not close over the graded rows")
    for r in rows:
        if r.get("class") not in CLASS_VOCAB:
            bad.append("%s:%s class outside the frozen vocabulary" % (r.get("file"), r.get("line")))
            break
        if r.get("class") == K_READ and not r.get("read_by_opener"):
            bad.append("%s:%s claims a reader and publishes none" % (r.get("file"), r.get("line")))
            break
        if r.get("class") != K_READ and r.get("read_by_opener"):
            bad.append("%s:%s publishes a reader outside the read class"
                       % (r.get("file"), r.get("line")))
            break
        if r.get("class") == K_CODE_TEXT and not r.get("code_text_citations"):
            bad.append("%s:%s claims a code citation and publishes none"
                       % (r.get("file"), r.get("line")))
            break
        if r.get("class") == K_PROSE and not r.get("prose_citations"):
            bad.append("%s:%s claims a prose citation and publishes none"
                       % (r.get("file"), r.get("line")))
            break
        if r.get("class") == K_DECLARED and (r.get("code_text_citations")
                                            or r.get("prose_citations")
                                            or r.get("read_by_opener")):
            bad.append("%s:%s is declared_and_unread yet publishes a citation"
                       % (r.get("file"), r.get("line")))
            break
        if r.get("on_disk") is False and r.get("class") in CLASS_VOCAB:
            bad.append("%s:%s is graded although the note is not on disk"
                       % (r.get("file"), r.get("line")))
            break
        if r.get("read_by_opener_count") != len(r.get("read_by_opener") or []):
            bad.append("%s:%s read count does not match its rows"
                       % (r.get("file"), r.get("line")))
            break
    if s.get("rows_with_any_opener_evidence") != sum(1 for r in rows if r.get("read_by_opener")):
        bad.append("the opener-evidence total does not re-derive")
    if s.get("rows_whose_constant_is_never_read_again") != \
            sum(1 for r in rows if not r.get("constant_references_beyond_assignment")):
        bad.append("the never-read-again constant total does not re-derive")
    if s.get("document_rows") != len(rows):
        bad.append("document_rows does not match the graded rows")
    return bad


# ---------------------------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------------------------
def selftest():
    out = []

    def leg(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    # 1 path normalisation
    leg("rel strips the repo root",
        rel(os.path.join(ROOT, "research", "X-P1.md")) == "research/X-P1.md")
    leg("norm_target strips a foreign absolute prefix",
        norm_target("K:/Fluxgroup/FluxGroup/quant/bigmoney/research/X-P1.md") == "research/X-P1.md")
    leg("norm_target refuses an unresolvable key", norm_target(None) is None)

    # 2 scope and kind
    leg("a research note is in scope", in_doc_scope("research/X-P1.md"))
    leg("a docs note is in scope", in_doc_scope("docs/x/NOTE.md"))
    leg("a json artefact is out of scope", not in_doc_scope("results/x.json"))
    leg("a directory is out of scope", not in_doc_scope("results/state_tilt"))
    leg("kind names a glob a pattern", kind_of("results/trial_labor_w*") == "pattern")
    leg("kind names a suffixless path a directory", kind_of("results/state_tilt") == "directory")

    # 3 opener evidence: literal, via constant, and a non-opener mention
    py_lit = ('NOTES = "research/ABC-P1.md"\n'
              'with open(os.path.join(ROOT, "research", "ABC-P1.md")) as fh:\n    pass\n')
    ev = opener_evidence(py_lit, os.path.join(ROOT, "scripts", "t.py"), "ABC-P1.md")
    leg("a literal opener argument is evidence", len(ev) == 1 and ev[0]["reason"] == "literal",
        str(ev))
    py_const = ('P = os.path.join(ROOT, "research", "ABC-P1.md")\n'
                'head = open(P).read()\n')
    ev2 = opener_evidence(py_const, os.path.join(ROOT, "scripts", "t.py"), "ABC-P1.md")
    leg("a same-file constant feeding an opener is evidence",
        len(ev2) == 1 and ev2[0]["reason"].startswith("via_const"), str(ev2))
    py_text = ('NOTE = os.path.join(ROOT, "research", "ABC-P1.md")\n'
               'print("see research/ABC-P1.md")\n')
    leg("a printed mention is not an opener",
        not opener_evidence(py_text, os.path.join(ROOT, "scripts", "t.py"), "ABC-P1.md"))

    # 4 comment vs code text; the stem alone is not a citation of the note
    cites, stem_only = text_citation("# see ABC-P1.md for the freeze\nx = 1\n",
                                     os.path.join(ROOT, "scripts", "t.py"), "ABC-P1.md", "ABC-P1",
                                     "scripts/other.py", 0)
    leg("a comment is recorded as a text citation", len(cites) == 1 and cites[0]["kind"] == "comment",
        str(cites))
    cites2, stem2 = text_citation('x = "ABC-P1-SENS"\n',
                                  os.path.join(ROOT, "scripts", "t.py"), "ABC-P1.md", "ABC-P1",
                                  "scripts/other.py", 0)
    leg("a study-id mention is not a note citation",
        not cites2 and len(stem2) == 1, "%s %s" % (cites2, stem2))

    # 5 the declaring line is not its own citation
    own, _own_stem = text_citation('P = "research/ABC-P1.md"  # ABC-P1.md\n',
                                   os.path.join(ROOT, "scripts", "t.py"), "ABC-P1.md", "ABC-P1",
                                   "scripts/t.py", 1)
    leg("the declaration line is excluded", not [c for c in own if c["line"] == 1], str(own))

    # 6 classification ladder
    leg("a reader outranks a citation", classify([{"x": 1}], [{"x": 1}], [{"x": 1}], True, True) == K_READ)
    leg("a code citation outranks prose", classify([], [{"x": 1}], [{"x": 1}], True, True) == K_CODE_TEXT)
    leg("prose alone is its own class", classify([], [], [{"x": 1}], True, True) == K_PROSE)
    leg("nothing is declared_and_unread", classify([], [], [], True, True) == K_DECLARED)

    # 7 binding usage on a real temp file
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write('P = 1\nprint(P)\nprint(P)\n')
        tmp = fh.name
    try:
        u = binding_usage(tmp, "P", 1)
        leg("binding usage counts loads, not the assignment", u["references"] == 2, str(u))
    finally:
        os.unlink(tmp)

    # 8 verdict is a function of the classes, not a carried literal
    r_read = [{"class": K_READ}]
    r_text = [{"class": K_READ}, {"class": K_CODE_TEXT}]
    leg("an all-read population returns V_ALL_READ", verdict_for(r_read, []) == V_ALL_READ)
    leg("one code-text row moves the verdict", verdict_for(r_text, []) == V_CODE_TEXT)
    leg("an empty population says so", verdict_for([], [{"reason": "x"}]) == V_NONE)

    # 9 tally gate refuses a flipped class and accepts the published face
    face = {"summary": {"population": 2, "document_rows": 2, "by_class": {K_READ: 1, K_DECLARED: 1},
                        "rows_with_any_opener_evidence": 1,
                        "rows_whose_constant_is_never_read_again": 1},
            "rows": [{"file": "a.py", "line": 1, "class": K_READ, "on_disk": True,
                      "read_by_opener": [{"file": "b.py"}], "read_by_opener_count": 1,
                      "constant_references_beyond_assignment": 1},
                     {"file": "c.py", "line": 2, "class": K_DECLARED, "on_disk": True,
                      "read_by_opener": [], "read_by_opener_count": 0,
                      "code_text_citations": [], "prose_citations": [],
                      "constant_references_beyond_assignment": 0}],
            "out_of_scope_rows": []}
    leg("the published-shape fixture passes the gate", not tally_problems(face),
        str(tally_problems(face)))
    doctor = json.loads(json.dumps(face))
    doctor["rows"][1]["class"] = K_READ
    leg("a flipped class with no reader is refused", bool(tally_problems(doctor)))
    doctor2 = json.loads(json.dumps(face))
    doctor2["rows"][0]["on_disk"] = False
    leg("a graded row whose note is absent is refused", bool(tally_problems(doctor2)))

    passed = sum(1 for _, ok, _ in out if ok)
    for name, ok, detail in out:
        print(("[PASS] " if ok else "[FAIL] ") + name + ((" | " + detail) if detail and not ok else ""))
    print("selftest %d/%d" % (passed, len(out)))
    return 0 if passed == len(out) else 1


# ---------------------------------------------------------------------------------------------
# entry points
# ---------------------------------------------------------------------------------------------
def _write(face):
    os.makedirs(ST, exist_ok=True)
    dated = os.path.join(ST, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for p in (dated, os.path.join(ST, FACE_NAME)):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return dated


def cmd_run():
    face = build()
    s = face["summary"]
    dated = _write(face)
    print("%s | %s" % (dated, face["verdict"]))
    print("population %d -> graded %d (out of scope %d) | by_class %s"
          % (s["population"], s["document_rows"], s["out_of_scope_rows"], s["by_class"]))
    print("opener evidence on %d row(s); code-text citations %d; never read again %d"
          % (s["rows_with_any_opener_evidence"], s["rows_named_in_code_text"],
             s["rows_whose_constant_is_never_read_again"]))
    print("walked %d text files (%d .py)" % (s["corpus_files_walked"], s["corpus_py_files"]))
    return 0


def cmd_check():
    face = json.load(open(os.path.join(ST, FACE_NAME), encoding="utf-8"))
    bad = tally_problems(face)
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("verdict outside the frozen vocabulary")
    elif face.get("verdict") != verdict_for(face.get("rows") or [],
                                            face.get("out_of_scope_rows") or []):
        bad.append("the verdict does not re-derive from the rows")
    if bad:
        print("PROBLEMS: " + "; ".join(bad))
        return 1
    s = face.get("summary") or {}
    print("ok | %s | graded %s/%s | by_class %s"
          % (face.get("verdict"), s.get("document_rows"), s.get("population"),
             s.get("by_class")))
    return 0


def cmd_verify():
    face = json.load(open(os.path.join(ST, FACE_NAME), encoding="utf-8"))
    live = build()
    problems = []
    if (face.get("summary") or {}).get("by_class") != (live.get("summary") or {}).get("by_class"):
        problems.append("the class tally does not re-derive from the live tree")
    if face.get("verdict") != live.get("verdict"):
        problems.append("the verdict does not re-derive from the live tree")
    if len(face.get("rows") or []) != len(live.get("rows") or []):
        problems.append("the graded population moved")
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    print("ok | %s | problems=[]" % live.get("verdict"))
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "run":
        return cmd_run()
    if mode == "check":
        return cmd_check()
    if mode == "verify":
        return cmd_verify()
    if mode == "selftest":
        return selftest()
    print("usage: python scripts/e449_dead_document_pointer.py run|verify|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))