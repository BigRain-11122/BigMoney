"""Run the E331 smoke leg on its own, extracted verbatim from smoke_test.py.

The full suite is ~35 minutes and does not fit a 10-minute round, so the leg is lifted out of its
enclosing function by AST (the treatment E341..E362 got) and executed against the published face.

E355 (r1377) is why the namespace is not hand-built here: two legs shipped with "standalone PASS"
evidence and then raised NameError inside the suite, because their private runners supplied imports
the suite does not have.  This runner executes the leg inside ``vars(smoke_test)`` -- exactly the
module globals the suite itself provides -- so a missing helper fails here the same way it would
fail in the suite.
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "smoke_test.py")
LEG = "E331"
VAR = "_name331"


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
    block = lines[head:tail]
    first = next(l for l in block if l.strip() and not l.lstrip().startswith("#"))
    indent = len(first) - len(first.lstrip())
    out = []
    for line in block:
        if not line.strip():
            out.append("")
        elif line[:indent].strip() == "":
            out.append(line[indent:])
        else:
            out.append(line.lstrip())
    return "\n".join(out)


def main() -> int:
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)
    import smoke_test  # noqa: E402  (importing it defines main(); it does not run it)

    body = extract(open(SMOKE, encoding="utf-8").read())
    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    ns = dict(vars(smoke_test))
    ns["check"] = check
    exec(compile(body, "<e331-leg>", "exec"), ns)  # noqa: S102 - extracted verbatim on purpose

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