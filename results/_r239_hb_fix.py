# -*- coding: utf-8 -*-
"""R239: heartbeat field hygiene -- drop None-valued idle_ram_gb key I added, refresh
canonical fields (cpu_pct/free_ram_gb/round_no) per prior heartbeat convention."""
import json
import os
import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)

hb.pop("idle_ram_gb", None)
hb["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
hb["round_no"] = 239

with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(hp, encoding="utf-8") as f:
    check = json.load(f)
assert isinstance(check["heartbeat_epoch_utc"], int)
assert "idle_ram_gb" not in check
print("heartbeat hygiene ok; cpu_pct:", check["cpu_pct"], "free_ram_gb:", check["free_ram_gb"], "round_no:", check["round_no"])
