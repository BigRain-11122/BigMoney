# -*- coding: utf-8 -*-
"""r515 bm-c push-race probe: fetch + ahead/behind + last-origin commits.
Zero-window git. Read-only after fetch."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


rc, out, err = git(["fetch", "origin"])
print("FETCH rc=%d %s" % (rc, (err or out).strip()[:120]))
rc, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
rc2, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
print("AHEAD %s BEHIND %s" % (ahead.strip(), behind.strip()))
rc, subj, _ = git(["log", "--oneline", "-6", "HEAD..origin/main"])
print("--- new behind commits ---")
print(subj.strip() or "(none)")
