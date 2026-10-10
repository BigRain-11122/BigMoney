#!/usr/bin/env python
# r858 bm-b T23 re-arm executor: archive stale r854 timeout receipt (move,
# evidence preserved per single-flight law) then spawn the r858 watcher
# detached (zero-window law: DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP|
# CREATE_NO_WINDOW, stdin DEVNULL, no pipe held by parent). The r854
# watcher process is verified dead by the caller before this runs.
# Encoding: pure ASCII body (repo PS/py GBK decode law).
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = os.path.join(ROOT, "results", "_r854bmb_t23_autofire_receipt.json")
ARCHIVE = os.path.join(
    ROOT, "results", "_r854bmb_t23_autofire_receipt_timeout_r854.json")
WATCHER = os.path.join(ROOT, "results", "_r858bmb_t23_watch.py")
WATCHER_LOG = os.path.join(ROOT, "results", "_r858bmb_t23_watch.log")
RECEIPT = os.path.join(ROOT, "results", "_r858bmb_t23_watch_receipt.json")
REARM = os.path.join(ROOT, "results", "_r858bmb_t23_rearm.json")

# 1) safety: refuse to re-arm if a live watcher receipt of either
#    generation still says watching/fired (single-flight law)
for path in (LEGACY, RECEIPT):
    if not os.path.exists(path):
        continue
    with open(path, encoding="utf-8") as f:
        st = json.load(f).get("state")
    if st in ("watching", "fired"):
        print("REFUSE: receipt %s state=%s (live watcher/burn in flight)"
              % (os.path.basename(path), st))
        sys.exit(3)

# 2) archive the stale timeout receipt (move, never delete: evidence law)
if os.path.exists(LEGACY):
    os.replace(LEGACY, ARCHIVE)
    print("archived legacy timeout receipt ->", os.path.basename(ARCHIVE))
else:
    print("legacy receipt already absent (no-op)")

# 3) spawn the r858 watcher detached
flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
         | subprocess.CREATE_NO_WINDOW)
with open(WATCHER_LOG, "a", encoding="utf-8") as lf:
    proc = subprocess.Popen([sys.executable, WATCHER],
                            stdout=lf, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, creationflags=flags,
                            close_fds=False, cwd=ROOT)
doc = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "round": 858,
    "machine": "bm-b",
    "watcher_pid": proc.pid,
    "watcher": os.path.basename(WATCHER),
    "receipt": os.path.basename(RECEIPT),
    "archived": os.path.basename(ARCHIVE) if os.path.exists(ARCHIVE) else None,
}
with open(REARM + ".tmp", "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)
    f.flush()
    os.fsync(f.fileno())
os.replace(REARM + ".tmp", REARM)
print("re-armed: watcher pid=%s receipt=%s"
      % (proc.pid, os.path.basename(RECEIPT)))
