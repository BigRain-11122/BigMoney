# r260 bm-c S0.5/S2/S3 programmatic scan: orders diff (no timestamp filter),
# inbox unread, tasks not-done, watermark red card, decisions tail, HANDOVER tail.
import json, glob, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ack = set(json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))["orders_ack"])
orders = set(os.path.basename(p) for p in glob.glob("fleet/orders/*.md"))
print("ORDERS:", len(orders), "on disk |", len(ack), "acked")
print("NEW-ORDERS:", sorted(orders - ack) or "none")
print("ACK-MISSING-ON-DISK:", sorted(ack - orders) or "none")
unread = glob.glob("fleet/inbox/*.md")
print("INBOX-UNREAD:", [os.path.basename(p) for p in unread] or "none")
op = []
for p in sorted(glob.glob("fleet/tasks/*.json")):
    d = json.load(open(p, encoding="utf-8"))
    st = d.get("status", "?")
    if st not in ("done", "completed", "closed"):
        op.append((os.path.basename(p), st, d.get("claimed_by", "")))
print("TASKS-NOT-DONE:", op or "none")
try:
    wr = json.load(open("results/watermark_red.json", encoding="utf-8"))
    print("WM-RED:", wr.get("red"), "|", str(wr.get("reason", ""))[:120])
except Exception as e:
    print("WM-RED-ERR:", e)
try:
    lines = open(r"..\..\docs\decisions.md", encoding="utf-8").read().splitlines()
    print("DECISIONS-TAIL-4:")
    for l in lines[-4:]:
        print("  " + l[:200])
except Exception as e:
    print("DECISIONS-ERR:", e)
print("HANDOVER-TAIL-6:")
for l in open("research/HANDOVER.md", encoding="utf-8").read().splitlines()[-6:]:
    print("  " + l[:190])
