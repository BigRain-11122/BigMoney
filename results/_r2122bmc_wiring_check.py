"""r2122 bm-c: every script a committed chain leg / smoke leg names must exist in origin/main.

r1783 family: wiring landed in git while the wired object did not.
Read-only: never writes anything except its own stdout.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked(path):
    r = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", "origin/main", "--", path],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def main():
    out = []
    for src_file in ("Tools/s6_chain_bmc.py", "smoke_test.py"):
        p = os.path.join(ROOT, src_file)
        if not os.path.exists(p):
            out.append(("MISSING_SOURCE", src_file, ""))
            continue
        text = open(p, encoding="utf-8").read()
        refs = set(re.findall(r"[\"'](scripts/[A-Za-z0-9_./-]+\.py)[\"']", text))
        for name in re.findall(r"os\.path\.join\([\"']scripts[\"'],\s*[\"']([A-Za-z0-9_.-]+\.py)[\"']\)", text):
            refs.add("scripts/" + name)
        for rel in sorted(refs):
            rel_n = rel.replace("\\", "/")
            if not tracked(rel_n):
                out.append(("NOT_IN_GIT", src_file, rel_n))

    # also: faces the chain writes must not include a script whose result json is absent
    print("checked legs referencing scripts in: Tools/s6_chain_bmc.py, smoke_test.py")
    if not out:
        print("WIRING OK: every referenced script is in origin/main")
        return 0
    for kind, src, rel in out:
        local = os.path.exists(os.path.join(ROOT, rel.replace("/", os.sep)))
        print(f"{kind} | {src} | {rel} | {'EXISTS_LOCAL' if local else 'ABSENT_BOTH'}")
    return 3


if __name__ == "__main__":
    sys.exit(main())
