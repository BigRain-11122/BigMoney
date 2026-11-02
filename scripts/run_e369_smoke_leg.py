"""Run one leg of smoke_test.py verbatim, out of the suite (the suite is a single ~12k-line run).

A leg is written inside ``main()``, so this extracts the source text between two markers, dedents
it, and execs it with a stub ``check`` -- the leg's own text, not a copy of it.
"""
import json
import os
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK_START = "# E369: a pin at the publishing commit"
MARK_END = "# E358: E351 called 55 gate subjects"


def dedent_code(block):
    """Dedent the code lines while leaving the block's own column-0 comment markers alone."""
    lines = block.splitlines()
    indents = [len(l) - len(l.lstrip()) for l in lines
               if l.strip() and not l.lstrip().startswith("#")]
    cut = min(indents) if indents else 0
    return "\n".join(l[cut:] if l.strip() and (len(l) - len(l.lstrip())) >= cut else l
                     for l in lines)


def main():
    os.chdir(ROOT)
    with open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8") as fh:
        src = fh.read()
    if MARK_START not in src or MARK_END not in src:
        print("leg markers not found")
        return 2
    block = src[src.index(MARK_START):src.index(MARK_END)]
    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))
        print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if not ok and detail else ""))

    ns = {"os": os, "json": json, "sys": sys, "check": check, "__name__": "smoke_leg"}
    exec(compile(dedent_code(block), "smoke_test.py:[E369]", "exec"), ns)
    if not results:
        print("the block ran no check() call")
        return 2
    failed = [r for r in results if not r[1]]
    print("leg %d/%d" % (len(results) - len(failed), len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())