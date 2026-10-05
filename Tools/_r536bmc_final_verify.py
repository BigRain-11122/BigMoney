# -*- coding: utf-8 -*-
"""r536 bm-c final post-close verification: git status, HEAD state face,
heartbeat sanity (committed version)."""
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


rc, out, _ = git(["status", "--porcelain"])
lines = [l for l in out.splitlines() if l.strip()]
print("POST-CLOSE DIRTY %d (expect own daemon churn faces only)" % len(lines))
for l in lines:
    print(" ", l)
rc, out, _ = git(["log", "--oneline", "-4"])
print(out)
# HEAD state face check
r = subprocess.run(["git", "show", "HEAD:state-bm-c.json"], capture_output=True,
                   cwd=ROOT, creationflags=CREATE_NO_WINDOW)
st = json.loads(r.stdout.decode("utf-8", "replace"))
print("HEAD state round_no=%d epoch_type=%s clock=%s" % (
    st["round_no"], type(st["heartbeat_epoch_utc"]).__name__, st["clock_read"]))
r2 = subprocess.run(["git", "show", "HEAD:fleet/machines/bm-c.json"],
                    capture_output=True, cwd=ROOT, creationflags=CREATE_NO_WINDOW)
hb = json.loads(r2.stdout.decode("utf-8", "replace"))
print("HEAD heartbeat last_seen=%s epoch=%s (%s)" % (
    hb.get("last_seen"), hb.get("heartbeat_epoch_utc"),
    type(hb.get("heartbeat_epoch_utc")).__name__))
