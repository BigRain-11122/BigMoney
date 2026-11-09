#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A committed Python file must at least parse -- otherwise it cannot report its own failure.

r1473 (bm-c).  `smoke_test.py` was committed on 2026-11-09 by two consecutive rounds
(r1471 / r1472) in a state that raises `IndentationError: unindent does not match any
outer indentation level` at import.  The suite is the company's only whole-tree gate, so
for two rounds there was NO gate at all: the file died before it could print a single
[FAIL].  Both rounds' notes say "full smoke not verified" -- which was true, and which
is exactly why nobody noticed the suite could not run.

Nothing in the repo could see it:

* the pre-commit claw looks for conflict markers and for JSON that will not open;
* the S6 chain runs legs, not the smoke suite;
* reading the diff does not show it -- a 4-space vs 0-space `try:` looks like style.

The cheapest possible judgement is `compile()` on the bytes the commit will publish.
It is also the most valuable one: a Python file that does not parse is a file whose
every consumer is dead, and that failure is invisible to the round that ships it.

Usage:
    python Tools/py_face_guard.py --staged      # the blobs this commit will publish
    python Tools/py_face_guard.py --paths a.py b.py
    python Tools/py_face_guard.py --selftest

Exit codes: 0 clean, 1 findings, 2 mechanism failure (git unreadable).
Silent on success so a normal commit's output is unchanged.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE_CAP = 2 * 1024 * 1024          # a .py over this is generated data, not source


def staged_python_files():
    """(path, blob) for every added/modified/renamed .py the staged tree will publish."""
    names = subprocess.run(["git", "-C", ROOT, "diff", "--cached", "--name-only",
                            "--diff-filter=ACMR", "--", "*.py"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    if names.returncode != 0:
        raise RuntimeError("git diff --cached unreadable: %s"
                           % (names.stderr or "").strip()[:160])
    out = []
    for path in (names.stdout or "").splitlines():
        path = path.strip()
        if not path:
            continue
        blob = subprocess.run(["git", "-C", ROOT, "show", ":%s" % path],
                              capture_output=True)
        if blob.returncode != 0:
            raise RuntimeError("git show :%s unreadable" % path)
        out.append((path, blob.stdout))
    return out


def judge_bytes(raw, path):
    """One verdict for one byte string. Both readers (staged blob, file on disk) use it,
    so a gate that passes in one path cannot fail in the other for a different reason."""
    if len(raw) > SIZE_CAP:
        return "over the %dKB source cap -- not compiled" % (SIZE_CAP // 1024)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        return "not utf-8 (%s) -- readers open with encoding='utf-8'" % e
    try:
        compile(text, path, "exec")
    except SyntaxError as e:
        return "does not parse: %s (line %s)" % (e.msg, e.lineno)
    except ValueError as e:            # e.g. source with a NUL byte
        return "does not parse: %s" % e
    except MemoryError:
        return "compiled out of memory -- not judged"
    return None


def check(paths=None):
    """Findings list; empty means clean. paths=None reads the staged blobs."""
    items = staged_python_files() if paths is None else [
        (p, open(p, "rb").read()) for p in paths]
    bad = []
    for path, raw in items:
        why = judge_bytes(raw, path)
        if why:
            bad.append((path, why))
    return bad


# ------------------------------------------------------------------ selftest
_FIXTURES = [
    ("ok_simple", b"x = 1\n", None),
    ("bad_indent", b"def f():\n    return 1\n  return 2\n", "does not parse"),
    ("bad_mixed_try", b"def f():\n    try:\n        pass\nexcept Exception:\n    pass\n"
                      b"try:\n        pass\n    except Exception:\n        pass\n",
     "does not parse"),
    ("bom_ok", b"\xef\xbb\xbfx = 1\n", None),
    ("latin1_bad", "é = 1\n".encode("latin-1"), "not utf-8"),
    ("nul_bad", b"x = 1\x00\n", "does not parse"),
]


def selftest():
    bad = []
    for name, raw, want in _FIXTURES:
        got = judge_bytes(raw, name + ".py")
        if want is None and got is not None:
            bad.append("%s judged %r, expected clean" % (name, got))
        elif want is not None and (got is None or want not in got):
            bad.append("%s judged %r, expected a finding carrying %r" % (name, got, want))
    # the real file that started this: HEAD~2 parsed, the two commits after it did not
    live = os.path.join(ROOT, "smoke_test.py")
    if os.path.exists(live):
        with open(live, "rb") as f:
            why = judge_bytes(f.read(), "smoke_test.py")
        if why:
            bad.append("the shipped smoke_test.py still cannot be compiled: %s" % why)
    print("%d/%d selftest legs pass" % (len(_FIXTURES) + 1 - len(bad), len(_FIXTURES) + 1))
    for b in bad:
        print("  FAIL " + b)
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--paths" in argv:
        paths = argv[argv.index("--paths") + 1:]
        if not paths:
            print("--paths needs at least one file", file=sys.stderr)
            return 2
    elif "--staged" in argv or not argv:
        paths = None
    else:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: py_face_guard.py [--staged | --paths f... | --selftest]",
              file=sys.stderr)
        return 2
    try:
        bad = check(paths)
    except (RuntimeError, OSError) as e:
        print("py_face_guard: %s" % e, file=sys.stderr)
        return 2
    for path, why in bad:
        print("%s: %s" % (path, why))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))