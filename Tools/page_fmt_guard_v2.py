#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the page-`%` guard, second pass: keep every real finding, drop the three false classes

WHY THIS FILE EXISTS
--------------------
`Tools/page_fmt_guard.py` (r2111) catches the right defect class with a `ast`-only read, and
its own selftest is green -- but r2112 read 20 of its 37 findings and found it right only
about half the time:

  * every defect *detector* in the tree trips it (`if "%%" in md:` and the
    `problems.append("page prints a literal %% ...")` that follows it are the guard
    watching for exactly this defect -- they are the opposite of the defect);
  * every `%(name)s` mapping format is called an invalid conversion, though it is legal
    printf (and `%.f` / `%0.f`, precision with no digits, is legal too);
  * a `%%` template built into a variable and `%`-applied one line later (`head = "...%%..."`
    then `head % primary`) is reported as page prose, though it renders correctly.

A leg that is red on correct code is worse than no leg (r1789): readers learn to skip it.
So this pass re-implements the same scan with those three false classes suppressed
*mechanically* (each suppression has a named rule and its own selftest fixture), and prints
what it suppressed so the suppression can be audited instead of trusted.

WHAT IS SUPPRESSED, AND ON WHAT EVIDENCE
----------------------------------------
  DETECTOR_LITERAL        the literal is not page text:
                          - its whole value is "%%"           (`if "%%" in md:`)
                          - it is an operand of a Compare     (`assert "1.21%%" not in md`)
                          - its nearest call writes into a container whose name is defect
                            vocabulary                          (`bad.append(...)`,
                            `problems.append(...)`, `issues.append(...)`)
  MAPPING_FORMAT          the offending `%` opens `%(name)<conv>`, legal printf
  RELAXED_PRECISION       the offending `%` is a precision with no digits (`%.f`, `%0.f`)
  TEMPLATE_APPLIED_LATER  the literal is assigned to a name (or into a container assigned to
                          a name) that is later used as `<name> % ...`, or unpacked from a
                          container that is later `%`-applied in a for-loop

Everything else is reported, including the case r2112 found: a page writer that appends a
string containing `%%` and never formats it -- the reader sees two percent signs.

WHAT IS STILL OUT OF SCOPE (printed, not implied)
-------------------------------------------------
* argument-count / argument-shape mismatches (`"%(a)s" % 1`, `"%s %s" % (a,)`): legal-looking
  format strings that fail on the operand; they need the operand, not the literal;
* f-strings and `.format()` (a `%` is plain text there, so both findings would be wrong);
* anything inside a `.md` file: this reads code, not output.

Usage:
    python Tools/page_fmt_guard_v2.py scan [--json PATH] [--roots scripts Tools ...]
    python Tools/page_fmt_guard_v2.py check [--json PATH]
    python Tools/page_fmt_guard_v2.py --selftest

exit codes:
    0   no residue (PAGE_FMT_CLEAN_V2)
    3   residue found (PAGE_FMT_RESIDUE_V2) -- reported, never auto-fixed
    2   the scan could not run, or `check` could not re-derive its own face
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import page_fmt_guard as v1  # noqa: E402  (same directory, single source for shared rules)

SCHEMA = "page-fmt-guard-v2/v1"
KIND = "page_fmt_guard_v2_scan"
DEFAULT_OUT = os.path.join(ROOT, "results", "page_fmt_guard_v2.scan.json")
DEFAULT_ROOTS = v1.DEFAULT_ROOTS

H_LITERAL = v1.H_LITERAL
H_BARE = v1.H_BARE
H_SYNTAX = "SYNTAX_ERROR"
V_CLEAN = "PAGE_FMT_CLEAN_V2"
V_RESIDUE = "PAGE_FMT_RESIDUE_V2"

S_DETECTOR = "DETECTOR_LITERAL"
S_MAPPING = "MAPPING_FORMAT"
S_PRECISION = "RELAXED_PRECISION"
S_TEMPLATE = "TEMPLATE_APPLIED_LATER"

# a printf conversion, plus the two shapes Python accepts that the first pass did not:
# the mapping form %(name)s and a precision with no digits (%.f / %0.f).
_CONV = re.compile(
    r"%(?:\([^)]*\))?[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*)?)?[hlL]?[diouxXeEfFgGcrsa%]"
)
_MAPPING_AT = re.compile(r"%\([^)]*\)[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*)?)?[hlL]?[diouxXeEfFgGcrsa]")
_PRECISION_ONLY = re.compile(r"%[-+ #0]*(?:\d+|\*)?\.(?:\d+|\*)?[hlL]?[diouxXeEfFgGcrsa]")

# names a file uses for the list of complaints it is about to print: a string appended to
# one of these is the guard's own message, never page prose.
_DEFECT_VOCAB = re.compile(
    r"^(bad|errs?|errors?|issues?|problems?|fails?|failures?|warnings?|warns?|notes?|"
    r"diag|diagnostics?|alerts?|violations?|complaints?|offenders?)$",
    re.I,
)

_MD_ROOTS = ("research", "docs")


# --------------------------------------------------------------------------- conversions

def bad_conversions(text):
    """[(offset, char, why)] for every '%' that does not open a valid conversion"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "%":
            i += 1
            continue
        m = _CONV.match(text, i)
        if m:
            i = m.end()
            continue
        out.append((i, text[i:i + 2], "no valid conversion"))
        i += 1
    return out


def first_pass_only_class(text):
    """name the first pass's complaint about this literal, when this pass has none.

    The two passes disagree only on shapes Python accepts: the mapping conversion and a
    precision with no digits.  Naming which one it was keeps the suppression auditable
    instead of a silent `continue`.
    """
    first = v1.bad_conversions(text)
    if not first:
        return None
    seg = text[first[0]:first[0] + 40]
    if _MAPPING_AT.match(seg):
        return S_MAPPING
    if _PRECISION_ONLY.match(seg):
        return S_PRECISION
    return None


# --------------------------------------------------------------------------- ast helpers

def _parents(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


_BOUNDARY = v1._BOUNDARY


def _in_compare(node, parents):
    """`assert "1.21%%" not in md` -- a comparison operand is a probe, not page text"""
    cur = node
    while True:
        p = parents.get(id(cur))
        if p is None:
            return False
        if isinstance(p, ast.Compare):
            return True
        if isinstance(p, _BOUNDARY):
            return False
        cur = p


def _defect_receiver(call):
    """`bad.append(...)` / `problems.append(...)`: the call writes complaints, not rows"""
    if call is None:
        return False
    name = v1._call_name(call)
    if v1._WRITER.search(name) is None:
        return False
    if _DEFECT_VOCAB.match(name or ""):
        return True
    f = call.func
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        return bool(_DEFECT_VOCAB.match(f.value.id))
    return False


def _assignment_targets(node, parents):
    """the names this literal is bound to (walking up to the enclosing assignment)"""
    cur = node
    while True:
        p = parents.get(id(cur))
        if p is None:
            return set()
        if isinstance(p, ast.Assign):
            names = set()
            for t in p.targets:
                names.update(x.id for x in ast.walk(t) if isinstance(x, ast.Name))
            return names
        if isinstance(p, (ast.AnnAssign, ast.AugAssign)):
            return {x.id for x in ast.walk(p.target) if isinstance(x, ast.Name)}
        if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            return set()
        cur = p


def _percent_applied_names(tree):
    """every name used as the left operand of a `%` operator anywhere in the module"""
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod):
            out.update(x.id for x in ast.walk(n.left) if isinstance(x, ast.Name))
    return out


def _unpacked_containers(tree, applied):
    """containers whose unpacked members are `%`-applied (`for a, b, fmt in rows: fmt % x`)"""
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.For, ast.AsyncFor)):
            tgts = {x.id for x in ast.walk(n.target) if isinstance(x, ast.Name)}
            if tgts & applied:
                out.update(x.id for x in ast.walk(n.iter) if isinstance(x, ast.Name))
        if isinstance(n, ast.Assign) and n.targets and isinstance(n.targets[0], (ast.Tuple, ast.List)):
            tgts = {x.id for x in ast.walk(n.targets[0]) if isinstance(x, ast.Name)}
            if tgts & applied:
                out.update(x.id for x in ast.walk(n.value) if isinstance(x, ast.Name))
    return out


# --------------------------------------------------------------------------- page corpus

def md_corpus(roots=_MD_ROOTS):
    """(relpath, text) for every reader-facing markdown file, read once per process"""
    for root in roots:
        base = root if os.path.isabs(root) else os.path.join(ROOT, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
            for fn in sorted(filenames):
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    text = io.open(p, encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                yield os.path.relpath(p, ROOT).replace("\\", "/"), text


def phrase_probe(value):
    """the first 24 reader-visible characters of the literal, normalised for a text search"""
    s = re.sub(r"^[|#>\-\s]+", "", (value or "").strip())
    s = re.sub(r"\s+", " ", s)
    return s[:24]


def published_hits(phrase, corpus):
    hits = []
    if len(phrase) < 8:
        return hits
    for rel, text in corpus:
        if phrase in text:
            hits.append(rel)
            if len(hits) >= 3:
                break
    return hits


# --------------------------------------------------------------------------- the scan

def scan_text(text, path, tag, corpus=None):
    """return (residue hazards, suppressed tally, stats)"""
    stats = {"constants": 0, "fstrings": 0}
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return ([{"file": path, "line": getattr(exc, "lineno", 0), "kind": H_SYNTAX,
                  "snippet": str(exc)[:120], "where": "syntax", "tag": tag}], {}, stats)
    parents = _parents(tree)
    page_renderer = v1._looks_like_page_renderer(text)
    applied = _percent_applied_names(tree)
    containers = _unpacked_containers(tree, applied)

    hazards = []
    suppressed = {}

    def bump(k):
        suppressed[k] = suppressed.get(k, 0) + 1

    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            stats["fstrings"] += 1
            continue
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if "%" not in node.value:
            continue
        if v1._is_docstring(node, parents) or v1._in_fstring(node, parents):
            continue
        stats["constants"] += 1
        if not page_renderer:
            continue
        if v1._is_concat_fragment(node, parents):
            continue
        formatted = v1._is_formatted(node, parents)
        snippet = node.value.strip().replace("\n", " ")[:110]

        if formatted:
            bad = bad_conversions(node.value)
            if not bad:
                rule = first_pass_only_class(node.value)
                if rule is not None:
                    bump(rule)
                continue
            off, char, _why = bad[0]
            window = node.value[max(0, off - 18):off + 12]
            hazards.append({"file": path, "line": node.lineno, "kind": H_BARE,
                            "offset": off, "offender": char, "window": window,
                            "snippet": snippet, "where": "format", "tag": tag})
            continue

        if "%%" not in node.value:
            continue
        call = v1._nearest_call(node, parents)
        if call is not None and not v1._WRITER.search(v1._call_name(call)):
            continue  # assertion text / exception message: '%' is plain there
        if node.value.strip() == "%%":
            bump(S_DETECTOR)
            continue
        if _in_compare(node, parents):
            bump(S_DETECTOR)
            continue
        if _defect_receiver(call):
            bump(S_DETECTOR)
            continue
        targets = _assignment_targets(node, parents)
        if targets & (applied | containers):
            bump(S_TEMPLATE)
            continue
        row = {"file": path, "line": node.lineno, "kind": H_LITERAL,
               "snippet": snippet, "where": "writer" if call is not None else "container",
               "tag": tag, "phrase": phrase_probe(node.value)}
        if corpus is not None:
            row["published_hits"] = published_hits(row["phrase"], corpus)
        hazards.append(row)
    return hazards, suppressed, stats


def _sources(roots):
    """every .py the scan reads: the first pass's walk minus both guard files (they carry fixtures)"""
    skip = (os.path.abspath(__file__), os.path.abspath(v1.__file__))
    for path in v1.iter_sources(roots):
        if os.path.abspath(path) in skip:
            continue
        yield path


def scan(roots=DEFAULT_ROOTS, with_v1=True):
    corpus = list(md_corpus())
    files = 0
    renderers = 0
    constants = 0
    fstrings = 0
    hazards = []
    suppressed = {}
    unreadable = []
    inputs = {}
    for path in _sources(roots):
        text = None
        for enc in ("utf-8-sig", "gbk"):
            try:
                with io.open(path, "r", encoding=enc, errors="strict") as fh:
                    text = fh.read()
                break
            except Exception:
                continue
        if text is None:
            unreadable.append(os.path.relpath(path, ROOT).replace("\\", "/"))
            continue
        files += 1
        tag = "page" if v1._looks_like_page_renderer(text) else "other"
        if tag == "page":
            renderers += 1
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        hz, sup, st = scan_text(text, rel, tag, corpus=corpus)
        constants += st["constants"]
        fstrings += st["fstrings"]
        for k, v in sup.items():
            suppressed[k] = suppressed.get(k, 0) + v
        if hz:
            inputs[rel] = hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()[:16]
            hazards.extend(hz)

    v1_ref = None
    if with_v1:
        try:
            ref = v1.scan(roots)
            # the first pass only skips its own file; this one carries deliberate fixtures and
            # would be counted as six hazards, so it is excluded from the comparison too.
            mine = os.path.relpath(os.path.abspath(__file__), ROOT).replace("\\", "/")
            kept = [h for h in ref["hazards"] if h.get("file") != mine]
            v1_ref = {
                "total": len(kept),
                "counts": {
                    H_LITERAL: sum(1 for h in kept if h["kind"] == H_LITERAL),
                    H_BARE: sum(1 for h in kept if h["kind"] == H_BARE),
                    H_SYNTAX: sum(1 for h in kept if h["kind"] == H_SYNTAX),
                },
                "excluded": [mine],
            }
        except Exception as exc:  # never let the comparison break this face
            v1_ref = {"error": str(exc)[:120]}

    suppressed_total = sum(suppressed.values())
    counts = {
        H_LITERAL: sum(1 for h in hazards if h["kind"] == H_LITERAL),
        H_BARE: sum(1 for h in hazards if h["kind"] == H_BARE),
        H_SYNTAX: sum(1 for h in hazards if h["kind"] == H_SYNTAX),
        "residue_total": len(hazards),
        "suppressed_total": suppressed_total,
        "suppressed": dict(sorted(suppressed.items())),
        "residue_with_published_hit": sum(1 for h in hazards if h.get("published_hits")),
    }
    return {
        "schema": SCHEMA,
        "kind": KIND,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tool": "Tools/page_fmt_guard_v2.py",
        "reads": "Tools/page_fmt_guard.py (same-dir import: shared rules, one source)",
        "scope": {
            "roots": list(roots),
            "files_scanned": files,
            "page_renderers": renderers,
            "percent_constants": constants,
            "fstrings_skipped": fstrings,
            "unreadable": unreadable,
            "md_corpus": len(corpus),
            "note": "only files that build a markdown page (.md literal + a writer call) are "
                    "reported; f-strings and .format() are out of scope; the residue is "
                    "checked against the published .md corpus so a reader-visible finding "
                    "carries its page, not just its source line",
        },
        "counts": counts,
        "v1_reference": v1_ref,
        "suppressed_rules": {
            S_DETECTOR: "whole-value '%%', or a Compare operand, or appended to bad/err/"
                        "issues/problems/fail/warn/note/diag/alerts/violations",
            S_MAPPING: "the offending '%' opens a legal %(name)<conv> mapping conversion",
            S_PRECISION: "the offending '%' is a precision with no digits (%.f / %0.f), legal printf",
            S_TEMPLATE: "the literal is bound to a name (or to a container of names) that is "
                        "later used as '<name> %% ...' or unpacked into a %-applied member",
        },
        "inputs": inputs,
        "hazards": hazards,
        "verdict": V_CLEAN if not hazards else V_RESIDUE,
    }


# --------------------------------------------------------------------------- check

def check(path=DEFAULT_OUT, deep=False):
    """re-derive and compare: drift in the sources says STALE, same input disagreeing says FAILED

    The default is per-file: it re-reads the files the face is *about* and compares their line
    sets, plus the tree's file count, in about a second.  A full tree re-scan answers the same
    question for files the face says nothing about, which is what `--deep` is for.
    """
    if not os.path.exists(path):
        sys.stderr.write("STALE: face missing: %s\n" % path)
        return 2
    face = json.load(io.open(path, encoding="utf-8"))
    roots = tuple(face["scope"]["roots"])
    problems = []
    stale = []

    if deep:
        again = scan(roots, with_v1=False)
        a = {(h["file"], h["line"], h["kind"]) for h in face.get("hazards") or []}
        b = {(h["file"], h["line"], h["kind"]) for h in again.get("hazards") or []}
        for k in sorted(b - a):
            problems.append("finding missing from the face: %s:%s %s" % k)
        for k in sorted(a - b):
            problems.append("finding on the face is gone: %s:%s %s" % k)
        for key in ("residue_total", "suppressed_total"):
            if face["counts"].get(key) != again["counts"].get(key):
                problems.append("count %s: face %s vs recomputed %s"
                                % (key, face["counts"].get(key), again["counts"].get(key)))
    else:
        by_file = {}
        for h in face.get("hazards") or []:
            by_file.setdefault(h["file"], set()).add((h["line"], h["kind"]))
        for rel, want in (face.get("inputs") or {}).items():
            p = os.path.join(ROOT, rel.replace("/", os.sep))
            text = None
            for enc in ("utf-8-sig", "gbk"):
                try:
                    with io.open(p, encoding=enc, errors="strict") as fh:
                        text = fh.read()
                    break
                except Exception:
                    continue
            if text is None:
                stale.append(rel + " (missing or unreadable)")
                continue
            got = hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()[:16]
            if got != want:
                stale.append(rel)
                continue
            tag = "page" if v1._looks_like_page_renderer(text) else "other"
            hz, _sup, _st = scan_text(text, rel, tag)
            got_rows = {(h["line"], h["kind"]) for h in hz}
            want_rows = by_file.get(rel, set())
            for row in sorted(got_rows - want_rows):
                problems.append("finding missing from the face: %s:%s %s"
                                % (rel, row[0], row[1]))
            for row in sorted(want_rows - got_rows):
                problems.append("finding on the face is gone: %s:%s %s" % (rel, row[0], row[1]))
        n_now = sum(1 for _p in _sources(roots))
        if n_now != face["scope"].get("files_scanned"):
            stale.append("tree file count %s -> %d (a .py file appeared or vanished)"
                         % (face["scope"].get("files_scanned"), n_now))
        # the face's own arithmetic, and every finding must point at a file whose bytes it recorded
        n_rows = sum(len(v) for v in by_file.values())
        if n_rows != face["counts"].get("residue_total"):
            problems.append("face is self-inconsistent: %d rows but residue_total=%s"
                            % (n_rows, face["counts"].get("residue_total")))
        for rel in sorted(by_file):
            if rel not in (face.get("inputs") or {}):
                problems.append("finding names a file with no recorded input: %s" % rel)

    if stale:
        print("STALE (%d source(s) moved since this face was written)" % len(stale))
        for s in stale[:10]:
            print("  drift %s" % s)
        if problems:
            print("CHECK FAILED (%d): the files that did not move already disagree" % len(problems))
            for p in problems[:10]:
                print("  %s" % p)
        return 3
    if problems:
        print("CHECK FAILED (%d)" % len(problems))
        for p in problems:
            print("  %s" % p)
        return 3
    print("CHECK_OK residues=%d suppressed=%d mode=%s"
          % (len(face.get("hazards") or []), face["counts"]["suppressed_total"],
             "deep" if deep else "per-file"))
    return 0


# --------------------------------------------------------------------------- selftest

_HEAD = 'DOC = os.path.join(ROOT, "research", "X.md")\n'


def _page(body):
    return _HEAD + "def render():\n    L = []\n" + body + '    io.open(DOC, "w", encoding="utf-8").write("\\n".join(L))\n'


# Each tuple is (name, file content, expected residue count, expected suppression tally).
# The strings below are *file contents*: every '%' is exactly the character that will land on
# disk, so a doubled percent here really is a doubled percent in the fixture file.
FIXTURES = [
    ("clean-formatted", _page('    L.append("| vol %.1f%% | %d |" % (1.5, 3))\n'), 0, {}),
    ("residue-writer-literal", _page('    L.append("| net %%/yr | yes |")\n'), 1, {}),
    ("suppress-whole-double", _page('    if "%%" in DOC:\n        pass\n'), 0, {S_DETECTOR: 1}),
    ("suppress-compare", _page('    assert "1.21%%" not in DOC\n'), 0, {S_DETECTOR: 1}),
    ("suppress-defect-receiver", _page('    problems.append("page prints a literal %% (r2039)")\n'),
     0, {S_DETECTOR: 1}),
    ("suppress-mapping", _page('    L.append("> gen %(g)s cost 0.10%%" % {"g": 1})\n'), 0, {S_MAPPING: 1}),
    ("suppress-precision", _page('    L.append("n=%0.f%%" % 1.53)\n'), 0, {S_PRECISION: 1}),
    ("suppress-template-assign", _page('    head = "| a | 实际%% | %s |"\n    L.append(head % "x")\n'),
     0, {S_TEMPLATE: 1}),
    ("suppress-template-unpack", _page(
        '    rows = [("a", "%.1f%%"), ("b", "%.0f")]\n'
        '    for label, fmt in rows:\n        L.append(label + (fmt % 2.5))\n'), 0, {S_TEMPLATE: 1}),
    ("residue-bare-cjk", _page('    L.append("−0.3983%；diff %s" % 1)\n'), 1, {}),
    ("residue-mapping-invalid", _page('    L.append("x %(g)s %|" % {"g": 1})\n'), 1, {}),
]

_NON_PAGE = 'DOC = "no page here %s"\nx = "a %% b"\n'
_SYNTAX = _HEAD + 'def render():\n    L.append("unterminated\n'


def selftest():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    legs = []

    def ok(cond, name):
        legs.append((bool(cond), name))

    import tempfile
    for name, src, want_hz, want_sup in FIXTURES:
        tmp = tempfile.mkdtemp(prefix="pfgv2_")
        p = os.path.join(tmp, "page_%s.py" % name.replace("-", "_"))
        io.open(p, "w", encoding="utf-8").write(src)
        hz, sup, _st = scan_text(src, "fixture/%s.py" % name, "page")
        ok(len(hz) == want_hz, "%s: %d hazard(s) (want %d)" % (name, len(hz), want_hz))
        for k, v in want_sup.items():
            ok(sup.get(k) == v, "%s: suppressed %s=%s (want %s)" % (name, k, sup.get(k), v))
        del tmp

    hz, sup, _ = scan_text(_NON_PAGE, "fixture/nonpage.py", "other")
    ok(not hz, "non page-renderer reports nothing")
    hz, sup, _ = scan_text(_SYNTAX, "fixture/broken.py", "page")
    ok(len(hz) == 1 and hz[0]["kind"] == H_SYNTAX, "syntax error is its own class")
    ok(all(h["kind"] != H_SYNTAX for h in scan_text(_page('    L.append("x %%/y")\n'),
                                                    "f", "page")[0]),
       "syntax class does not leak into the residue")

    hz, _sup, _ = scan_text(_page('    L.append("−0.3983%；diff %s" % 1)\n'), "f", "page")
    ok(hz and hz[0].get("offender", "").endswith("；"),
       "bare finding names the offending character")
    ok(hz and hz[0].get("window"), "bare finding carries a context window")

    hz, _sup, _ = scan_text(_page('    L.append("| net %%/yr | yes |")\n'), "f", "page")
    ok(hz and hz[0].get("phrase", "").startswith("| net") is False,
       "phrase probe strips leading table marks")
    ok(hz and phrase_probe(hz[0]["snippet"]) == "net %%/yr | yes |"[:24],
       "phrase probe is the first 24 reader-visible characters")

    corpus = [("research/FAKE.md", "| net %% | yes |")]
    hz, _sup, _ = scan_text(_page('    L.append("net %% | yes")\n'), "f", "page", corpus=corpus)
    ok(hz and hz[0].get("published_hits") == ["research/FAKE.md"],
       "a finding that reaches a published page carries that page")
    hz, _sup, _ = scan_text(_page('    L.append("never published here %%")\n'), "f", "page", corpus=corpus)
    ok(hz and hz[0].get("published_hits") == [], "unpublished finding carries an empty hit list")

    ok(bad_conversions("%(a)s") == [], "mapping conversion is not a bad conversion")
    ok(bad_conversions("%.f") == [] and bad_conversions("%0.f") == [], "digit-less precision is legal")
    ok(bad_conversions("%%") == [], "escaped percent is legal")
    ok(len(bad_conversions("%/yr")) == 1, "a bare %/yr is still a bad conversion")
    ok(first_pass_only_class("%(a)s") == S_MAPPING, "the first pass's mapping complaint is named")
    ok(first_pass_only_class("%.f") == S_PRECISION, "the first pass's precision complaint is named")
    ok(first_pass_only_class("%s") is None, "a clean string is not attributed to a blind spot")
    ok(first_pass_only_class("%/yr") is None,
       "a real defect is never attributed to a blind spot (that would silence it)")

    passed = sum(1 for c, _ in legs if c)
    for cond, name in legs:
        if not cond:
            print("  FAIL  %s" % name)
    print("%d/%d %s" % (passed, len(legs), "ALL_PASS" if passed == len(legs) else "FAILED"))
    return 0 if passed == len(legs) else 1


# --------------------------------------------------------------------------- cli

def cmd_scan(args):
    face = scan(tuple(args.roots), with_v1=not args.no_v1)
    out = args.json or DEFAULT_OUT
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(face, ensure_ascii=False, indent=1) + "\n")
    c = face["counts"]
    print("%s residues=%d literal=%d bare=%d syntax=%d suppressed=%d files=%d"
          % (face["verdict"], c["residue_total"], c[H_LITERAL], c[H_BARE], c[H_SYNTAX],
             c["suppressed_total"], face["scope"]["files_scanned"]))
    print("  suppressed: " + ", ".join("%s=%d" % kv for kv in c["suppressed"].items()))
    if face.get("v1_reference", {}).get("total") is not None:
        print("  first pass total=%d -> residue=%d (dropped %d)"
              % (face["v1_reference"]["total"], c["residue_total"],
                 face["v1_reference"]["total"] - c["residue_total"]))
    print("  face -> %s" % out)
    return 0 if c["residue_total"] == 0 else 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="page %% guard, second pass")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sc = sub.add_parser("scan")
    sc.add_argument("--json", default=None)
    sc.add_argument("--roots", nargs="*", default=list(DEFAULT_ROOTS))
    sc.add_argument("--no-v1", action="store_true", help="skip the first-pass comparison")
    ch = sub.add_parser("check")
    ch.add_argument("--json", default=None)
    ch.add_argument("--deep", action="store_true", help="re-scan the whole tree, not just the face's inputs")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "scan":
        return cmd_scan(args)
    if args.cmd == "check":
        return check(args.json or DEFAULT_OUT, deep=args.deep)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
