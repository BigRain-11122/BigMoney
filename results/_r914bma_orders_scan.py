# -*- coding: utf-8 -*-
"""r914 bm-a S7 orders double-scan (closeout leg): fleet/orders diff vs
heartbeat orders_ack + fleet/inbox unprocessed check."""
import io
import json
import os

ACK = "fleet/machines/bm-a.json"
ORD = "fleet/orders"
INBOX = "fleet/inbox"
PROC = "fleet/inbox/processed"

hb = json.load(io.open(ACK, encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
orders = sorted(f for f in os.listdir(ORD) if f.endswith(".md"))
unacked = [o for o in orders if o not in acked]
print("orders files=%d acked=%d unacked=%s" %
      (len(orders), len(acked), unacked or "NONE"))

msgs = sorted(f for f in os.listdir(INBOX)
              if f.lower().endswith(".md"))
unproc = [m for m in msgs if m not in acked]
print("inbox md=%d not-in-ack=%s" % (len(msgs), unproc or "NONE"))
proc_files = set(os.listdir(PROC))
still_inbox = [m for m in msgs if m in acked and m in proc_files]
print("seat MSGs still in inbox though acked+processed:", still_inbox or "NONE")
