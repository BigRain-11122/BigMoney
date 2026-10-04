# -*- coding: utf-8 -*-
# r667 bm-b heartbeat update (R170/R178: epoch must be JSON int via int(time.time());
# clock_read T-separated ISO 8601; write-then-json.loads self-verify)
import json, time, datetime, io, subprocess

p = r"fleet\machines\bm-b.json"
d = json.load(io.open(p, encoding="utf-8"))
now = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def ps_num(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    try:
        return float(r.stdout.decode("utf-8", "replace").strip() or 0)
    except ValueError:
        return -1

free_ram_gb = ps_num("[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)")
gpu_free_mb = ps_num("(Get-CimInstance Win32_VideoController | Select-Object -First 1).AdapterRAM/1MB")

d["last_seen"] = clock
d["current_task"] = ("round 667 done: golden-week watch (trio V725/Q558/D410 of 2000 healthy "
                     "3 burners CIM-verified; S6 38/38 green; D-19 dual MATCH; origin merge "
                     "integrated 0 UU)")
d["cpu_cores"] = 16
d["free_ram_gb"] = free_ram_gb
d["gpu_free_vram_mb"] = gpu_free_mb
d["verdict"] = "healthy: smoke 48/48, S6 38/38 green, trio burns healthy, round 667 delivered"
d["heartbeat_epoch_utc"] = now  # int, not str
d["clock_read"] = clock
d["round_no"] = 667
d["round_no_label"] = "round 667 (bm-b)"

with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
chk = json.loads(io.open(p, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and chk["clock_read"].count("+") == 1, "clock_read format"
print("heartbeat OK epoch=%d int-verified clock=%s free_ram=%.1fGB gpu_free=%.0fMB"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], free_ram_gb, gpu_free_mb))
