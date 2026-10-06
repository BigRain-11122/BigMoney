# -*- coding: utf-8 -*-
"""r809 bm-a S7 closeout: state increment + orders watermark + heartbeat + round report."""
import json, subprocess, hashlib, time, datetime, psutil

# --- orders watermark (full sha from origin blob via local group tree) ---
out = subprocess.run(["git", "-C", r"C:\Users\sjs20\Desktop\FluxGroup", "show",
                      "origin/main:docs/orders.md"], capture_output=True)
orders_sha = hashlib.sha256(out.stdout).hexdigest()

# --- state ---
sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 809
s["last_orders_sha"] = orders_sha
json.dump(s, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
sv = json.load(open(sp, encoding="utf-8"))
assert sv["round_no"] == 809 and sv["last_orders_sha"] == orders_sha

# --- heartbeat ---
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
vm = psutil.virtual_memory()
try:
    import shutil
    tot, _, free = shutil.disk_usage("C:\\")
except Exception:
    tot = free = 0
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = iso
hb["current_task"] = "r809: W168 full-lifecycle closeout (burn 12/12 + r752 gate + finalize one-pass landed)"
hb["cpu_cores"] = psutil.cpu_count()
hb["idle_ram_gb"] = round(vm.available / 1e9, 1)
hb["verdict"] = "idle_supply_engine_lane_w168_closed"
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = iso
hb["ts"] = iso
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
hv = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(hv["heartbeat_epoch_utc"], int), "epoch must be JSON int"

print("state round_no:", sv["round_no"], "| orders_sha:", orders_sha[:16])
print("heartbeat epoch int:", hv["heartbeat_epoch_utc"], "| clock:", hv["clock_read"])
