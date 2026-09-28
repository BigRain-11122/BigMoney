"""r367 bm-b heartbeat update: fleet/machines/bm-b.json (single-writer own file).
Fields per FLEET-OPS: last_seen/clock_read ISO8601 T-sep, heartbeat_epoch_utc=JSON int, current_task, resources, verdict, orders_ack 99 kept."""
import json, time, subprocess

def ps(cmd):
    return subprocess.run(["powershell","-NoProfile","-Command",cmd],capture_output=True,text=True).stdout.strip()

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
free_ram_gb = float(ps("[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"))
cpu_pct = float(ps("[math]::Round((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average,1)"))
gpu = ps("(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits)")
gpu_free_mb = int(gpu.splitlines()[0]) if gpu else -1

p = "fleet/machines/bm-b.json"
d = json.load(open(p, encoding="utf-8"))
d["last_seen"] = now
d["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (R170/R178)
d["clock_read"] = now                      # ISO8601 T-sep (R262)
d["current_task"] = ("r367: S0 push-storm double-wave discharge landed (push 3ad7877d, escape machine/bm-b-r366 superseded in-place per bm-c r143 precedent); "
                     "census W2B burning i~1800/5620 honest ETA ~17:00 (avg 7.0/min); next = census finalize watch -> RAM window (12GB prep guard) -> "
                     "W1-JUDGE/MASS x4/W2-JUDGE flips (bm-b = flip executor) -> W2 judge-finalize -> intake live fire")
d["free_ram_gb"] = free_ram_gb
d["idle_ram_gb"] = free_ram_gb
d["cpu_util_pct"] = cpu_pct
d["cpu_pct"] = cpu_pct
d["gpu_free_vram_gb"] = round(gpu_free_mb/1024, 1) if gpu_free_mb >= 0 else d.get("gpu_free_vram_gb", 0)
d["gpu_idle_vram_mb"] = gpu_free_mb if gpu_free_mb >= 0 else d.get("gpu_idle_vram_mb", 0)
d["round_no"] = 367
d["round"] = 367
d["loop_round"] = 367
d["verdict"] = ("healthy: smoke 25/25, S6 29 legs rc=0 (bm-b lanes idempotent no-op, 4 host-guard skips lawful), "
                "push-storm discharged (24-UU wave1 + 1-UU wave2 canon-resolved, zero-loss verified), "
                "census W2B in-flight 4-worker (py 25.8% structural), free RAM " + str(free_ram_gb) + "GB (judge flips RAM-gated lawful)")
d["idle_ram_mb"] = int(free_ram_gb*1024)
d["free_ram_mb"] = int(free_ram_gb*1024)

json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(open(p, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO T-sep"
print("heartbeat ok: epoch=%r(int) clock=%s ram=%.1f cpu=%.1f gpu_free_mb=%d ack=%d" % (
    chk["heartbeat_epoch_utc"], chk["clock_read"], free_ram_gb, cpu_pct, gpu_free_mb, chk.get("n_orders_ack")))
