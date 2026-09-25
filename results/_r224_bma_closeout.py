# -*- coding: utf-8 -*-
"""R224 bm-a closeout: state bump + heartbeat + round report line append."""
import json
import time
import datetime as dt

NOW = dt.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

# --- state file: round_no +1 (223 -> 224) ---
p = "state-bm-a.json"
d = json.load(open(p, encoding="utf-8-sig"))
d["round_no"] = 224
d["did"] = ("R224: T-72 prereg s5 open-item (sina tier-threshold docs) batch leg ADVANCED-PARTIAL "
            "(5 probes/18 reqs: sina official JS r0=zhu-li/r3=retail investor-class labels -> "
            "R118 non-mapping law direct-evidence upgrade; r1/r2+thresholds UNDOCUMENTED stays; "
            "zero criteria touch) + digest + prereg note + ticket progress_s2 R224 + memory 1 line; "
            "T-72 first pull healthy 2185/5228 @06:10 ETA ~08:24 read-only monitoring")
d["verdict"] = "GREEN"
d["next"] = ("T-72 s2 acceptance RUN at pull completion (~08:24 round, sina_mf_accept.py run) then s3 "
             "S6 wiring; tier open-item next batch = different surface not different string; "
             "09-28 Monday new-bar full-chain relay; 10-01 month-boundary trio + REGIME_GUARD v3 "
             "date gate; T-70 midterm 10-09")
d["current_task"] = ("r224 done: T-72 open-item tier-doc batch leg (ADVANCED-PARTIAL, R118 evidence "
                     "upgrade); next: s2 acceptance RUN at pull completion (~08:24)")
d["ts"] = TS
d["last_round_ts"] = d.get("last_round_ts", TS)
d["last_round_at"] = TS
d["updated_at"] = TS
with open(p, "wb") as f:
    f.write(json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8-sig"))
print("state round_no ->", d["round_no"])

# --- heartbeat: fleet/machines/bm-a.json (own file only) ---
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8-sig"))
h["last_seen"] = TS
h["current_task"] = d["current_task"]
h["cpu_cores"] = 32
h["idle_ram_gb"] = None  # filled below if psutil available
try:
    import psutil
    vm = psutil.virtual_memory()
    h["idle_ram_gb"] = round(vm.available / 1024 ** 3, 1)
    h["cpu_pct"] = psutil.cpu_percent(interval=0.3)
except Exception:
    pass
h["gpu_idle_vram_mb"] = None
try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        h["gpu_idle_vram_mb"] = int(float(r.stdout.strip().splitlines()[0]))
except Exception:
    pass
h["verdict"] = "GREEN"
h["heartbeat_epoch_utc"] = EPOCH            # JSON int (R170/R178 law)
h["clock_read"] = CLOCK                      # T-04 F5 clock-drift field
with open(hp, "wb") as f:
    f.write(json.dumps(h, ensure_ascii=False, indent=2).encode("utf-8-sig"))
# self-verify: epoch must be int
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int!"
print("heartbeat updated, epoch int OK:", chk["heartbeat_epoch_utc"], "| clock:", chk["clock_read"])
