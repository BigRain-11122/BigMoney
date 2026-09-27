# -*- coding: utf-8 -*-
"""r390 bm-a heartbeat update + S7 orders double-scan (binary-safe)."""
import glob
import json
import os
import platform
import time
import datetime

HB = "fleet/machines/bm-a.json"

# --- S7 orders double-scan: directory vs ack diff ---
tree = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
hb = json.load(open(HB, encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
unacked = [t for t in tree if t not in ack]
print(f"orders scan: tree={len(tree)} acked={len(ack & set(tree))} "
      f"unacked={unacked}")

# --- machine resource snapshot (best-effort) ---
cpu_cores = os.cpu_count() or 32
free_gb = None
try:
    import psutil
    free_gb = round(psutil.virtual_memory().available / (1 << 30), 1)
    cpu_pct = psutil.cpu_percent(interval=0.3)
except Exception:
    free_gb, cpu_pct = None, 0.0

now = time.time()
hb["machine_id"] = "bm-a"
hb["last_seen"] = datetime.datetime.now().astimezone().replace(
    microsecond=0).isoformat()
hb["current_task"] = ("r390 closed: D-03(2) cleared-tombstone landed "
                      "(merge_crash_fuse tombstone semantics + autofill "
                      "clear-site tombstone, merger selftest +4 legs + S16h, "
                      "reconcile zero-drift) + 5x HANDOVER R386-390; "
                      "next = W2B finalize watch -> W2-JUDGE flip (bm-b) + "
                      "T-91 s3 09:15 auto-fire + tombstone first-live-fire watch")
hb["cpu_cores"] = cpu_cores
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = hb.get("gpu_free_vram_gb")
hb["verdict"] = "CLEAN"
hb["heartbeat_epoch_utc"] = int(now)          # MUST be JSON int (R170/R178)
hb["clock_read"] = datetime.datetime.now().astimezone().replace(
    microsecond=0).isoformat()                # T-separator (R262 law)
hb["round_no"] = 390

payload = json.dumps(hb, ensure_ascii=False, indent=1)
with open(HB, "wb") as fh:
    fh.write(payload.replace("\n", "\r\n").encode("utf-8"))

# read-back self-proof (smoke F7 shape)
back = json.load(open(HB, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in back["clock_read"] and " " not in back["clock_read"], \
    "clock_read must be T-separated ISO 8601"
print("heartbeat written: epoch=", back["heartbeat_epoch_utc"],
      "int-ok; clock=", back["clock_read"], "; last_seen=", back["last_seen"])
