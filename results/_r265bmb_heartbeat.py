# -*- coding: utf-8 -*-
"""R265 bm-b: heartbeat update (epoch MUST be JSON int per R170/R178; clock_read MUST be
T-separated ISO 8601 per R262). Mirrors HEAD blob faces: BOM=False, LF-only,
trailing_nl=True, keys preserved."""
import datetime as dt
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "fleet/machines/bm-b.json"
d = json.load(open(P, encoding="utf-8"))

d["last_seen"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
assert isinstance(epoch, int)
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
d["current_task"] = "r265 done: T-81 slice-4 LANDING-HOOKS full arc (3-family watch, zero landings confirmed, hook armed, S6 scorecard wiring + L3 divlowvol label refresh); next: T-76 face(a) 09-28 window + MF_IC_P1 gate recheck"
d["round_no"] = 265
d["verdict"] = "healthy"

# live machine faces (sampled)
ram = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
    capture_output=True).stdout.decode().strip()
try:
    d["free_ram_gb"] = float(ram)
except ValueError:
    pass
d["cpu_cores"] = 16
try:
    nvidia = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True).stdout.decode().strip().splitlines()[0]
    d["gpu_free_vram_gb"] = round(int(nvidia) / 1024, 1)
except Exception:
    pass

with open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")

# post-write self-verify: epoch int + clock T-separator (smoke F7 dual law)
chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
assert "T" in chk["clock_read"], chk["clock_read"]
print("heartbeat written: epoch=%d (int verified) clock=%s" %
      (chk["heartbeat_epoch_utc"], chk["clock_read"]))

# git diff sanity: field-increment level
out = subprocess.run(["git", "diff", "-U0", P], capture_output=True).stdout.decode("utf-8")
adds = sum(1 for l in out.splitlines() if l.startswith("+") and not l.startswith("+++"))
dels = sum(1 for l in out.splitlines() if l.startswith("-") and not l.startswith("---"))
print("heartbeat diff: +%d/-%d" % (adds, dels))
