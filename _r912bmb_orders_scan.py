"""r912 bm-b: S0.5 orders scan helper - diff fleet/orders/*.md vs heartbeat orders_ack."""
import glob
import json
import os

hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
files = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/*.md"))
unacked = [f for f in files if f not in ack]
print("ORDERS_TOTAL=%d ACKED=%d UNACKED=%d" % (len(files), len(files) - len(unacked), len(unacked)))
for f in unacked:
    print("UNACKED: " + f)
# group decisions/orders watermark probe face (read-only, informational)
try:
    import subprocess
    out = subprocess.run(
        ["git", "show", "origin/main:docs/decisions.md"],
        capture_output=True,
    )
    blob = out.stdout
    import hashlib
    print("DEC_SHA=" + hashlib.sha1(blob).hexdigest())
except Exception as e:
    print("DEC_SHA_ERR=" + str(e)[:80])
