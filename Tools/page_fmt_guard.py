#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""catch the page-render '%' defect at birth, not after the fifth round

WHY THIS FILE EXISTS
--------------------
Three rounds in a row lost a run to the same bug, in three costumes:

  r2105  page render  -> ValueError: unsupported format character '/'   ("%/yr" inside a
          string that IS run through the % operator)
  r2109  page table   -> the page printed "5%%"                          ("%%" inside a string
          written by a plain add(), i.e. never formatted)
  r2110  page table   -> ValueError: unsupported format character '|'    (a bare "%" in a
          formatted header row)

The class is entirely static: a string literal either goes through the `%` operator or it
does not, and the escaping rule is the exact opposite in the two cases.  The standing
"缺陷出生地拦截律" says every defect class gets a gate at its earliest detectable station;
this is that gate for page text.  It reads source with `ast`, never executes it, and asks
two questions of every non-docstring string constant:

  LITERAL_DOUBLE_PCT   the literal contains "%%" but is NOT formatted  -> the reader sees
                       a literal "%%" on the page (r2109)
  BARE_PCT_IN_FORMAT   the literal IS formatted but contains a "%" that does not open a
                       valid conversion                                          -> ValueError
                       at render time (r2105, r2110)

Both are refusals of fact, not style: they are only reported on files that actually build a
markdown page (a `.md` literal plus a writer call), because elsewhere a lone "%" is text.

WHAT IS OUT OF SCOPE (printed, not implied)
-------------------------------------------
* argument-count mismatches between a format string and its `%` arguments ("not enough
  arguments"), which need type information this pass does not have;
* f-strings and `.format()` / `str.format_map` (different escaping rules: a "%" is literal
  there, so both findings would be false positives -- they are skipped, not silently
  passed);
* anything inside a `.md` file itself: this reads code, not output.

Usage:
    python Tools/page_fmt_guard.py scan [--json PATH] [--roots scripts Tools monitor]
    python Tools/page_fmt_guard.py --selftest

exit codes:
    0   no hazard found (PAGE_FMT_CLEAN)
    3   hazard(s) found (PAGE_FMT_HAZARDS) -- reported, never auto-fixed
    2   the scan itself could not run (no readable roots)
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SCHEMA = "page-fmt-guard/v1"
KIND = "page_fmt_guard_scan"
DEFAULT_OUT = os.path.join(ROOT, "results", "page_fmt_guard.scan.json")
DEFAULT_ROOTS = ("scripts", "Tools", "monitor", "live", "firm")

H_LITERAL = "LITERAL_DOUBLE_PCT"
H_BARE = "BARE_PCT_IN_FORMAT"
V_CLEAN = "PAGE_FMT_CLEAN"
V_HAZARD = "PAGE_FMT_HAZARDS"

# a complete printf-style conversion: flags, width, precision, length, type
_CONV = re.compile(r"%[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlL]?[diouxXeEfFgGcrsa%]")


def bad_conversions(text):
    """every single '%' that does not open a valid conversion (escaped '%%' is fine)"""
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
        out.append(i)
        i += 1
    return out


def has_double_pct(text):
    return "%%" in text


_SCOPE = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def _is_docstring(node, parents):
    """first statement of a module / class / function body"""
    p = parents.get(id(node))
    if p is None:
        return False
    if isinstance(p, ast.Expr):
        holder = parents.get(id(p))
        if holder is None or not isinstance(holder, _SCOPE):
            return False
        body = holder.body
        return bool(body) and body[0] is p
    body = getattr(p, "body", None)
    if not isinstance(body, list) or not body:
        return False
    if body[0] is not node:
        return False
    return isinstance(p, _SCOPE)


def _in_fstring(node, parents):
    """a literal inside an f-string has different escaping rules: '%' is plain text there"""
    cur = node
    while True:
        p = parents.get(id(cur))
        if p is None:
            return False
        if isinstance(p, ast.JoinedStr):
            return True
        cur = p


_BOUNDARY = (ast.Expr, ast.Assign, ast.Return, ast.AnnAssign, ast.AugAssign, ast.Yield)


def _is_formatted(node, parents):
    """is this literal run through the % operator (as its operand, or part of it)?

    `"%.1f" % v`, `("%s %s" % (a, b))`, `("a" + "%d") % v` and `add("%d" % v)` are all
    formatted; a literal sitting anywhere else in the expression is not.
    """
    cur = node
    while True:
        p = parents.get(id(cur))
        if p is None:
            return False
        if isinstance(p, ast.JoinedStr):
            return False
        if isinstance(p, ast.BinOp) and isinstance(p.op, ast.Mod) and _contains(p.left, node):
            return True
        if isinstance(p, _BOUNDARY):
            return False
        cur = p


def _contains(root, target):
    for n in ast.walk(root):
        if n is target:
            return True
    return False


_WRITER = re.compile(r"(add|append|write|emit|extend|insert|put|line|row|cell|bullet|para|text)",
                     re.I)


def _nearest_call(node, parents):
    """the closest call whose arguments (or keywords) contain this literal"""
    cur = node
    while True:
        p = parents.get(id(cur))
        if p is None:
            return None
        if isinstance(p, ast.Call):
            if any(_contains(a, node) for a in p.args):
                return p
            if any(_contains(k.value, node) for k in p.keywords):
                return p
        cur = p


def _call_name(call):
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    try:
        return ast.unparse(f)
    except Exception:
        return ""


def _is_concat_fragment(node, parents):
    """("." + str(d) + "f") % x -- the pieces are not format strings on their own"""
    cur = node
    while True:
        p = parents.get(id(cur))
        if p is None:
            return False
        if isinstance(p, ast.BinOp) and isinstance(p.op, ast.Mod):
            left = p.left
            if isinstance(left, ast.BinOp) and isinstance(left.op, ast.Add) and _contains(left, node):
                return True
            return False
        if isinstance(p, _BOUNDARY):
            return False
        cur = p


def scan_text(text, path, tag):
    """return (hazards, skipped_fstrings, checked_constants)"""
    hazards = []
    f_strings = 0
    checked = 0
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return ([{"file": path, "line": getattr(exc, "lineno", 0), "kind": "SYNTAX_ERROR",
                  "snippet": str(exc)[:120]}], 0, 0)
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node

    page_renderer = _looks_like_page_renderer(text)

    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            f_strings += 1
            continue
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if "%" not in node.value:
            continue
        if _is_docstring(node, parents):
            continue
        if _in_fstring(node, parents):
            continue
        checked += 1
        if not page_renderer:
            continue
        if _is_concat_fragment(node, parents):
            continue
        formatted = _is_formatted(node, parents)
        snippet = node.value.strip().replace("\n", " ")[:110]
        if formatted:
            bad = bad_conversions(node.value)
            if bad:
                hazards.append({"file": path, "line": node.lineno, "kind": H_BARE,
                                "col": bad[0], "snippet": snippet, "where": "format",
                                "tag": tag})
        else:
            if not has_double_pct(node.value):
                continue
            call = _nearest_call(node, parents)
            if call is not None and not _WRITER.search(_call_name(call)):
                # an assertion message or an exception string: "%" is text there
                continue
            hazards.append({"file": path, "line": node.lineno, "kind": H_LITERAL,
                            "snippet": snippet,
                            "where": "writer" if call is not None else "container",
                            "tag": tag})
    return hazards, f_strings, checked


_MD_HINT = re.compile(r"""['"][^'"]*\.md['"]""")
_WRITER_HINT = re.compile(r"\b(add|append|write|writelines|_w|_add|emit|line)\s*\(")


def _looks_like_page_renderer(text):
    """a file that builds a markdown page: it names a .md path and writes lines"""
    return bool(_MD_HINT.search(text)) and bool(_WRITER_HINT.search(text))


def iter_sources(roots):
    for root in roots:
        base = root if os.path.isabs(root) else os.path.join(ROOT, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
            for fn in sorted(filenames):
                if fn.endswith(".py"):
                    yield os.path.join(dirpath, fn)


def scan(roots=DEFAULT_ROOTS):
    files = 0
    renderers = 0
    constants = 0
    fstrings = 0
    hazards = []
    unreadable = []
    for path in iter_sources(roots):
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue  # this file's fixtures are deliberate examples of both classes
        text = None
        for enc in ("utf-8-sig", "gbk"):
            try:
                with io.open(path, "r", encoding=enc, errors="strict") as fh:
                    text = fh.read()
                break
            except Exception:
                continue
        if text is None:
            unreadable.append(os.path.relpath(path, ROOT))
            continue
        files += 1
        if _looks_like_page_renderer(text):
            renderers += 1
        hz, fs, ck = scan_text(text, os.path.relpath(path, ROOT).replace("\\", "/"),
                               "page" if _looks_like_page_renderer(text) else "other")
        hazards.extend(hz)
        fstrings += fs
        constants += ck
    return {
        "schema": SCHEMA,
        "kind": KIND,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tool": "Tools/page_fmt_guard.py",
        "scope": {
            "roots": list(roots),
            "files_scanned": files,
            "page_renderers": renderers,
            "percent_constants": constants,
            "fstrings_skipped": fstrings,
            "unreadable": unreadable,
            "note": "hazards are only reported for files that build a markdown page "
                    "(.md literal + a writer call); f-strings and .format() are out of scope",
        },
        "counts": {
            H_LITERAL: sum(1 for h in hazards if h["kind"] == H_LITERAL),
            H_BARE: sum(1 for h in hazards if h["kind"] == H_BARE),
            "SYNTAX_ERROR": sum(1 for h in hazards if h["kind"] == "SYNTAX_ERROR"),
            "literal_in_writer_call": sum(1 for h in hazards
                                           if h["kind"] == H_LITERAL and h.get("where") == "writer"),
            "literal_in_container": sum(1 for h in hazards
                                        if h["kind"] == H_LITERAL and h.get("where") == "container"),
            "total": len(hazards),
        },
        "hazards": hazards,
        "verdict": V_CLEAN if not hazards else V_HAZARD,
    }


# --------------------------------------------------------------------------- selftest

FIXTURES = [
    ("clean", '''
DOC = os.path.join(ROOT, "research", "X.md")
def render(face):
    body = []
    body.append("| vol %.1f%% | %d blocks |" % (face["vol"], face["n"]))
    body.append("plain row, no percent")
    io.open(DOC, "w", encoding="utf-8").write("\\n".join(body))
''', 0),
    ("literal_double_pct", '''
DOC = "research/X.md"
def render(face):
    body = []
    body.append("| vol 5%% | one block |")
    io.open(DOC, "w", encoding="utf-8").write("\\n".join(body))
''', 1),
    ("bare_pct_in_format", '''
DOC = "research/X.md"
def render(face):
    body = []
    body.append("| block vol % | %d blocks |" % (face["d"], face["n"]))
    io.open(DOC, "w", encoding="utf-8").write("\\n".join(body))
''', 1),
    ("not_a_page_renderer", '''
def calc(x):
    return "%.1f%%" % x
''', 0),
    ("fstring_is_out_of_scope", '''
DOC = "research/X.md"
def render(face):
    line = f"| vol {face['v']:.1f}% | 5%% "
    io.open(DOC, "w", encoding="utf-8").write(line)
''', 0),
    ("docstring_is_skipped", '''
DOC = "research/X.md"
def render(face):
    """prints %.1f%% when called"""
    io.open(DOC, "w", encoding="utf-8").write("ok")
''', 0),
]


def selftest():
    legs = 0
    fails = []

    def ok(cond, name):
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    for name, src, expect in FIXTURES:
        hz, _fs, _ck = scan_text(src, name, "page")
        ok(len(hz) == expect, "fixture:%s expected %d hazard(s), got %d" % (name, expect, len(hz)))

    # the two kind labels must be distinguishable, or a reader cannot act on the finding
    hz, _, _ = scan_text(FIXTURES[1][1], "f1", "page")
    ok(hz and hz[0]["kind"] == H_LITERAL, "literal double pct keeps its label")
    hz, _, _ = scan_text(FIXTURES[2][1], "f2", "page")
    ok(hz and hz[0]["kind"] == H_BARE, "bare pct keeps its label")

    # conversions that look unusual but are legal must not be flagged
    ok(bad_conversions("%.3f%%") == [], "(%%) is a legal conversion")
    ok(bad_conversions("%-8s|%05.2f|%+d|%*d") == [], "flags/width/precision/star are legal")
    ok(len(bad_conversions("%/yr")) == 1, "'%/yr' is one bad conversion")
    ok(len(bad_conversions("% |")) == 1, "'% |' is one bad conversion")
    ok(len(bad_conversions("100%% of %d")) == 0, "escaped pct before a real conversion is clean")

    # a syntax error is reported, never silently dropped
    hz, _, _ = scan_text("def broken(:\n", "broken", "page")
    ok(len(hz) == 1 and hz[0]["kind"] == "SYNTAX_ERROR", "syntax error is surfaced")

    # live repo: the tool must run and every hazard must carry a file and a line
    face = scan()
    ok(face["schema"] == SCHEMA, "schema")
    ok(face["scope"]["files_scanned"] > 50, "scanned a real tree (%d files)" % face["scope"]["files_scanned"])
    ok(face["verdict"] in (V_CLEAN, V_HAZARD), "verdict token")
    ok(face["verdict"] == (V_CLEAN if face["counts"]["total"] == 0 else V_HAZARD), "verdict follows counts")
    ok(all(h.get("file") and isinstance(h.get("line"), int) for h in face["hazards"]),
       "every hazard names a file and a line")

    print("page_fmt_guard selftest %d/%d %s" % (legs - len(fails), legs,
                                                "ALL_PASS" if not fails else "FAILED"))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


# --------------------------------------------------------------------------- cli

def cmd_scan(args):
    face = scan(tuple(args.roots))
    out = args.json or DEFAULT_OUT
    try:
        d = os.path.dirname(out)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=2))
            fh.write("\n")
    except Exception as exc:  # a linter that cannot write its evidence is still a linter
        print("warn: could not write %s (%s)" % (out, exc))
    c = face["counts"]
    print("%s  files=%d renderers=%d percent_constants=%d  literal_double_pct=%d "
          "bare_pct_in_format=%d syntax_error=%d"
          % (face["verdict"], face["scope"]["files_scanned"], face["scope"]["page_renderers"],
             face["scope"]["percent_constants"], c[H_LITERAL], c[H_BARE], c["SYNTAX_ERROR"]))
    for h in face["hazards"][:40]:
        print("  %-8s %s:%d  %s" % (h["kind"], h["file"], h["line"], h["snippet"]))
    if len(face["hazards"]) > 40:
        print("  ... %d more" % (len(face["hazards"]) - 40))
    if not face["scope"]["files_scanned"]:
        return 2
    return 0 if face["verdict"] == V_CLEAN else 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="static guard for page-render %% escaping")
    ap.add_argument("cmd", nargs="?", default="scan", choices=("scan",))
    ap.add_argument("--json", default=None)
    ap.add_argument("--roots", nargs="*", default=list(DEFAULT_ROOTS))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    return cmd_scan(args)


if __name__ == "__main__":
    sys.exit(main())
