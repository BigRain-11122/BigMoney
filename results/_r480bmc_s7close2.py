"""r480 bm-c S7: heartbeat line-level surgery (r678 law: roundtrip mismatch
-> surgical field swap, zero collateral). Needle count==1 per field."""
import datetime
import json
import re
import subprocess
import time

P = "fleet/machines/bm-c.json"
raw = open(P, "rb").read().decode("utf-8")
lines = raw.splitlines(keepends=True)

epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# --- fresh GPU free VRAM (nvidia-smi real read, zero-window subprocess) ---
gpu_free = None
try:
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=20,
        creationflags=0x08000000)
    gpu_free = int(float(r.stdout.strip().splitlines()[0]))
except Exception as ex:
    print("gpu read skip:", ex)

import psutil
idle_ram = round(psutil.virtual_memory().available / (1 << 30), 1)

cur_task = (
    "MASS_TRIAL_W3 prereg frozen (R99 commit c2141d6c1) + runner --wave 3 "
    "legs + generate detached in-flight (pid 3484, ~80s/fam full speed) -- "
    "O-1440 sec.3 supply pre-position + T-158 post-judge consumption face | "
    "recent artifacts: research/MASS_TRIAL_W3_PREREG.md + "
    "results/_r480bmc_w3_generate_log.txt + results/_r480bmc_s6_log.txt "
    "(38/38 rc0) @ " + clock + " | next: W3 generate done -> screen 4-shard "
    "pool entries (r481) -> burn -> finalize + sec.9 s3 freeze <=10-12; "
    "fund-trio finalize 10-05 10:30 (bm-b); O-2115/O-2030 acceptance 10-08")

verdict = (
    "W3 wave ignited same-round: prereg frozen c2141d6c1 (R99 before any "
    "screen), runner wave-3 legs, banned gate ADMIT, selftest 38/38, "
    "generate detached full-speed; N2-W15 red card maintained (slice-2 = "
    "bm-b seat since 10-03 00:16, 39h unlanded, contact forbidden per "
    "anti-dup); S6 38/38 rc0; orders 155/155 dual-scan zero unacked; "
    "smoke 48/48")

# field -> new value (json-encoded with indent-1 leading space)
def j(v):
    return json.dumps(v, ensure_ascii=False)

updates = {
    "clock_read": j(clock),
    "heartbeat_epoch_utc": str(epoch),
    "idle_ram_gb": str(idle_ram),
    "last_seen": j(clock),
    "last_seen_at": j(clock),
    "current_task": j(cur_task),
    "verdict": j(verdict),
}
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
              "gpu_idle_mb"):
        updates[k] = str(gpu_free)

pat = re.compile(r'^\s*"([a-z_]+)":\s')
hits = {}
for i, l in enumerate(lines):
    m = pat.match(l)
    if m and m.group(1) in updates:
        hits.setdefault(m.group(1), []).append(i)

for k in updates:
    assert len(hits.get(k, [])) == 1, f"needle {k} count {len(hits.get(k, []))}"

for k, idxs in hits.items():
    i = idxs[0]
    stripped = lines[i].rstrip("\r\n")
    eol = "\r\n" if lines[i].endswith("\r\n") else "\n"
    comma = "," if stripped.rstrip().endswith(",") else ""
    lines[i] = f' "{k}": {updates[k]}{comma}{eol}'
# last line's trailing comma: ensure the final field line keeps valid JSON
out = "".join(lines)
v = json.loads(out)   # full reparse gate before write
open(P, "wb").write(out.encode("utf-8"))

# --- POST-WRITE assertions ---
v2 = json.load(open(P, encoding="utf-8"))
assert isinstance(v2["heartbeat_epoch_utc"], int)
assert "T" in v2["clock_read"] and "+" in v2["clock_read"]
assert len(v2.get("orders_ack", [])) == 155
print("HEARTBEAT-SURGERY-OK epoch", v2["heartbeat_epoch_utc"],
      "clock", v2["clock_read"], "gpu_free", gpu_free,
      "idle_ram", idle_ram, "fields", len(v2))
