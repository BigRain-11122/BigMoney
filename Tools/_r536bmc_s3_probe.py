"""r536 bm-c S2/S3 probe: fleet tasks by status, pool states, watermark,
satengine status, inbox unread. Read-only."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
CREATE_NO_WINDOW = 0x08000000


def rp(path):
    return os.path.join(ROOT, path)


# fleet tasks census
tdir = rp("fleet/tasks")
counts = {}
open_tasks = []
if os.path.isdir(tdir):
    for fn in os.listdir(tdir):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(tdir, fn), encoding="utf-8") as f:
                t = json.load(f)
            st = t.get("status", "?")
            counts[st] = counts.get(st, 0) + 1
            if st in ("open",):
                open_tasks.append((fn, t.get("title", t.get("subject", ""))[:60]))
        except Exception as e:
            counts["UNREADABLE"] = counts.get("UNREADABLE", 0) + 1
print("FLEET-TASKS %s open=%s" % (counts, open_tasks[:10]))

# pool census
try:
    with open(rp("results/runnable_pool.json"), encoding="utf-8") as f:
        pool = json.load(f)
    ents = pool.get("entries", pool if isinstance(pool, list) else [])
    st = {}
    for e in ents:
        s = e.get("status", "?")
        st[s] = st.get(s, 0) + 1
    print("POOL %s total=%d" % (st, len(ents)))
    for e in ents:
        if e.get("status") == "ready":
            print("  READY: %s lane=%s owner=%s" % (
                e.get("id", "?"), e.get("lane_owner", "?"), e.get("owner_since", "?")))
except Exception as e:
    print("POOL-ERR %s" % e)

# watermark red flag
try:
    with open(rp("results/watermark_red.json"), encoding="utf-8") as f:
        wm = json.load(f)
    print("WM red=%s next_pick=%s reason=%s" % (
        wm.get("red"), (wm.get("next_pick") or "")[:80], (wm.get("reason") or wm.get("note") or "")[:120]))
except Exception as e:
    print("WM-ERR %s" % e)

# satengine status (bm-c face = Tools copy)
r = subprocess.run([PY, rp("Tools/saturation_engine.py"), "status"], capture_output=True,
                   creationflags=CREATE_NO_WINDOW, cwd=ROOT,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})
print("SATENGINE rc=%d out=%s err=%s" % (
    r.returncode, (r.stdout or b"").decode("utf-8", "replace").strip()[:200],
    (r.stderr or b"").decode("utf-8", "replace").strip()[:200]))

# inbox unread for bm-c / ALL
inbox = rp("fleet/inbox")
unread = []
if os.path.isdir(inbox):
    for fn in os.listdir(inbox):
        if fn.endswith(".md") or fn.endswith(".json"):
            unread.append(fn)
print("INBOX-UNREAD %d %s" % (len(unread), unread[:10]))
