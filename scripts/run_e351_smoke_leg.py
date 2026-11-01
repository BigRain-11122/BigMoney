"""Run the E351 smoke leg on its own, extracted verbatim from smoke_test.py.

The full suite is ~35 minutes and does not fit a 10-minute round, so the new leg is lifted out
of its enclosing function by AST (same treatment E341/E342/E346/E349/E350 got) and executed
against the published face.  Nothing here re-implements the assertion: the source lines are the
ones in smoke_test.py.
"""
import ast
import json
import os
import re
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "smoke_test.py")
LEG = "E351"
VAR = "_name351"


def extract(src: str) -> str:
    tree = ast.parse(src)
    start = None
    tail = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == VAR):
            start = node.lineno
        if (isinstance(node, ast.Call) and node.args
                and isinstance(node.args[0], ast.Name) and node.args[0].id == VAR):
            tail = max(tail or 0, getattr(node, "end_lineno", node.lineno))
    if not start or not tail:
        raise SystemExit("could not locate the %s leg by AST" % LEG)
    lines = src.splitlines()
    head = start - 1
    for i in range(start - 1, 0, -1):
        if lines[i].lstrip().startswith("# %s:" % LEG):
            head = i
            break
    return textwrap.dedent("\n".join(lines[head:tail]))


def main() -> int:
    src = open(SMOKE, encoding="utf-8").read()
    body = extract(src)
    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    def _finish():
        return 0

    ns = {"os": os, "json": json, "re": re, "sys": sys, "check": check, "_finish": _finish}
    os.chdir(ROOT)
    exec(compile(body, "<e351-leg>", "exec"), ns)  # noqa: S102 - extracted verbatim on purpose
    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if not ok else ""))
    print(f"{LEG} smoke leg {len(results) - len(failed)}/{len(results)}")
    if not failed:
        for _name, _ok, detail in results:
            print("   " + str(detail))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())