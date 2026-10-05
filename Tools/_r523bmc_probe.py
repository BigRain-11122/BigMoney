# -*- coding: utf-8 -*-
"""r523 bm-c S0.5/S2 probe: orders set-diff (fleet/orders vs heartbeat ack),
fleet tasks active scan, inbox unread, watermark faces. Read-only.
Pattern credit: Tools/_r504bmc_probe.py / _r518bmc_s3.py lineage."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    with open(p, encoding="utf-8-sig") as fh:
        return json.load(fh)


# 1) orders set-diff (full scan, no timestamp filter -- R13 law)
ack = set(load(os.path.join(ROOT, "fleet", "machines", "bm-c.json"))
          .get("orders_ack", []))
files = set(os.path.basename(p)
            for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "*.md")))
unacked = sorted(files - ack)
ghost = sorted(ack - files)
print("ORDERS disk=%d ack=%d" % (len(files), len(ack)))
print("ORDERS-UNACKED %s" % (unacked if unacked else "none"))
print("ORDERS-GHOST-ACK %s" % (ghost if ghost else "none"))
for u in unacked:
    print("UNACKED-FILE %s mtime=%s" % (u, os.path.getmtime(
        os.path.join(ROOT, "fleet", "orders", u))))

# 2) fleet tasks active scan
rows = []
for p in sorted(glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json"))):
    try:
        t = load(p)
    except Exception as e:
        rows.append(("PARSE-FAIL", os.path.basename(p), str(e)[:60]))
        continue
    st = str(t.get("status", "")).lower()
    if st in ("open", "claimed", "in_progress"):
        rows.append((st, os.path.basename(p),
                     "by=%s|%s" % (t.get("claimed_by", ""),
                                   str(t.get("title", t.get("subject", "")))[:70])))
print("TASKS active=%d" % len(rows))
for r in rows[:60]:
    print("TASK %s %s %s" % r)

# 3) inbox unread (root files only; processed/ = done)
ib = os.path.join(ROOT, "fleet", "inbox")
unread = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ib, "*"))
                if os.path.isfile(p))
print("INBOX-UNREAD %s" % (unread if unread else "none"))

# 4) watermark faces
wm = load(os.path.join(ROOT, "results", "watermark_red.json"))
print("WM-RED %s reason=%s" % (wm.get("red"), str(wm.get("reason"))[:140]))
print("WM-NEXT-PICK %s" % str(wm.get("next_pick"))[:140])
try:
    lines = [l for l in open(os.path.join(ROOT, "results", "watermark.jsonl"),
                             encoding="utf-8", errors="replace")
             .read().splitlines() if l.strip()]
    j = json.loads(lines[-1])
    print("WM-LAST verdict=%s ts=%s" % (j.get("verdict"), j.get("ts")))
except Exception as e:
    print("WM-LAST unreadable %s" % e)

# 5) pool quick census (informational)
try:
    pool = load(os.path.join(ROOT, "results", "runnable_pool.json"))
    entries = pool.get("entries", pool) if isinstance(pool, dict) else pool
    if isinstance(entries, dict):
        entries = list(entries.values())
    from collections import Counter
    print("POOL-CENSUS %d %s" % (len(entries),
                                 dict(Counter(str(e.get("status")) for e in entries))))
except Exception as e:
    print("POOL unreadable %s" % e)
