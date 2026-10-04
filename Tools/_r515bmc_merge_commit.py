# -*- coding: utf-8 -*-
"""r515 bm-c merge completion: stage all + git commit --no-edit (MERGE_MSG
from the stopped merge) + HEAD echo. Zero-window git (CREATE_NO_WINDOW)."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                        creationflags=CREATE)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out, err


rc, out, err = git(["add", "-A"])
print("ADD rc=%d %s" % (rc, (err or out).strip()[:200]))
rc, out, err = git(["commit", "--no-edit"])
print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:300]))
rc, out, err = git(["rev-parse", "HEAD"])
print("HEAD %s" % out.strip())
rc, out, err = git(["log", "--oneline", "-2"])
print(out.strip())
rc, uu, _ = git(["ls-files", "-u"])
print("UU-AFTER %d" % len([l for l in uu.splitlines() if l.strip()]))
