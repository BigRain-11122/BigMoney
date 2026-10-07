# -*- coding: utf-8 -*-
"""r852 bm-a r835-final-escape leg: manual commit of the resolved rebase
step (author-preserved per r808/r659 law), then rebase --quit, then
symbolic-ref self-check + branch -f main HEAD + checkout main (r624 law).
False-conflict third state: continue refused with ls-files -u empty."""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

msg = io.open(r".git/rebase-merge/message", encoding="utf-8").read()
au = io.open(r".git/rebase-merge/author-script", encoding="utf-8",
             errors="replace").read()
vals = dict(re.findall(r"^([^=]+)='(.*)'$", au, re.M))
print("author keys:", sorted(vals.keys()))
env = dict(os.environ)
for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE"):
    assert k in vals, k
    env[k] = vals[k]
r = subprocess.run(["git", "commit", "-F", r".git/rebase-merge/message", "-q"],
                  env=env, capture_output=True, text=True)
print("manual commit rc", r.returncode, r.stderr[:200])
assert r.returncode == 0, r.stderr
r2 = subprocess.run(["git", "log", "-1", "--format=%h %an %ai %s"],
                    capture_output=True, text=True)
print("new head:", r2.stdout[:150])

r3 = subprocess.run(["git", "rebase", "--quit"], capture_output=True, text=True)
print("rebase --quit rc", r3.returncode, r3.stderr[:120])
r4 = subprocess.run(["git", "symbolic-ref", "-q", "HEAD"],
                   capture_output=True, text=True)
print("symbolic-ref:", repr(r4.stdout.strip()), "rc", r4.returncode)
if r4.returncode != 0:
    r5 = subprocess.run(["git", "branch", "-f", "main", "HEAD"],
                        capture_output=True, text=True)
    print("branch -f main rc", r5.returncode)
    r6 = subprocess.run(["git", "checkout", "main"], capture_output=True, text=True)
    print("checkout main rc", r6.returncode, r6.stderr[:100])
r7 = subprocess.run(["git", "log", "-3", "--format=%h %s"],
                    capture_output=True, text=True)
print(r7.stdout)
r8 = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
print("dirty after cure:"); print(r8.stdout)
