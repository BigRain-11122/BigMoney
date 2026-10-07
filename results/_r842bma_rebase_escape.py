# -*- coding: utf-8 -*-
"""r842 bm-a rebase false-conflict terminal escape (r835 law, third state):
1) git commit -F .git/rebase-merge/message (resolved face, message preserved)
2) git rebase --quit (abandon stuck sequencer; zero abort = r220)
3) symbolic-ref detached check -> git branch -f main HEAD + checkout main
Then fresh churn-absorb tail commit rebuilds the dropped todo content."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CREATE_NO_WINDOW = 0x08000000

def run(args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=e,
                          creationflags=CREATE_NO_WINDOW)

# sanity: index truly clean of unmerged
r = run(["git", "ls-files", "-u"])
assert r.stdout.strip() == "", r.stdout
assert os.path.exists(r".git\rebase-merge\message"), "no rebase-merge/message"

# 1) manual commit of resolved face
r = run(["git", "commit", "-F", ".git/rebase-merge/message"],
        env={"GIT_EDITOR": "true"})
print("commit rc", r.returncode)
print((r.stdout or r.stdout or "")[-200:], (r.stderr or "")[-200:])
assert r.returncode == 0, r.stderr

# 2) quit stuck sequencer
r = run(["git", "rebase", "--quit"])
print("quit rc", r.returncode, (r.stderr or "")[-150:])

# 3) detached-HEAD proof then branch reattach (r624)
r = run(["git", "symbolic-ref", "-q", "HEAD"])
print("symbolic-ref rc", r.returncode, "(nonzero=detached, expected) out:", r.stdout.strip()[:80])
r = run(["git", "branch", "-f", "main", "HEAD"])
print("branch -f rc", r.returncode, (r.stderr or "")[-150:])
r = run(["git", "checkout", "main"])
print("checkout rc", r.returncode, (r.stdout or "")[-150:], (r.stderr or "")[-150:])
r = run(["git", "log", "--oneline", "-3"])
print(r.stdout)
