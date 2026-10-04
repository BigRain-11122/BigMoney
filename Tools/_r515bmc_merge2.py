# -*- coding: utf-8 -*-
"""r515 bm-c second-wave merge (push-race, r704 law): merge origin tip,
list UU faces (python stdout only, r511 law 3)."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "results", "_r515bmc_mmsg2.txt")


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


with open(MSG, "w", encoding="utf-8", newline="\n") as f:
    f.write("merge r515: second wave integration (push-race window, r704 law)\n")
rc, out, err = git(["merge", "origin/main", "-F", MSG])
print("MERGE rc=%d" % rc)
print((err or out).strip()[:500])
rc, uu, _ = git(["ls-files", "-u"])
faces = sorted({l.split("\t", 1)[1].strip() for l in uu.splitlines() if "\t" in l})
print("UU-FACES %d" % len(faces))
for p in faces:
    print("UU %s" % p)
if os.path.exists(MSG):
    os.remove(MSG)
    print("MMMSG2-REMOVED")
