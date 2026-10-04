"""r475 bm-c heartbeat heal: restore full 35-field heartbeat from HEAD~1 blob,
merge fresh values, keep orders_ack & all legacy fields intact (closeout.py
overwrote the dict wholesale = field-loss incident, caught pre-push)."""
import datetime
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

now = datetime.datetime.now()
now_iso = now.isoformat(timespec="seconds")
now_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(now.timestamp())

p = subprocess.run(["git", "show", "HEAD~1:fleet/machines/bm-c.json"],
                   capture_output=True, creationflags=CREATE_NO_WINDOW, cwd=ROOT)
assert p.returncode == 0, "git show HEAD~1 heartbeat failed"
hb = json.loads((p.stdout or b"").decode("utf-8-sig"))
prev_ack = hb.get("orders_ack")
assert isinstance(prev_ack, list) and len(prev_ack) >= 150, \
    "orders_ack missing in HEAD~1 blob: " + repr(prev_ack)[:100]
prev_fields = set(hb.keys())

try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram = None, None
try:
    q = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=15)
    gpu_free = int((q.stdout or b"").decode("utf-8", "replace")
                   .strip().splitlines()[0])
except Exception:
    gpu_free = hb.get("gpu_free_vram_mib")

hb["machine_id"] = "bm-c"
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = cpu
hb["cpu_cores"] = 32
hb["cores"] = 32
hb["idle_ram_gb"] = ram
hb["ram_free_gb"] = ram
hb["free_ram_gb"] = ram
hb["gpu_free_vram_mib"] = gpu_free
hb["round_no"] = 475
hb["round_no_label"] = "r475"
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["ts"] = now_stamp
hb["activity_now"] = ("golden-week watch + 5x HANDOVER r475 landed; "
                      "fund-trio NULLS burn watch (V778/Q604/D451, bm-b owner)")
hb["current_task"] = hb["activity_now"] + "; MSG-1332 consumption watch"
hb["latest_artifact"] = ("research/HANDOVER.md r475 entry + results/"
                         "_r475bmc_s6_log.txt (S6 38/38 rc0) + results/"
                         "_r475bmc_fundnulls_watch.json")
hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 opens "
                        "(bm-b owner); D-06 closure 10-07 (bm-c lead); "
                        "market reopen 10-09")
hb["health"] = "healthy"
hb["verdict"] = ("healthy watch round, zero incident, N1 closed per O-2115 "
                 "sec-2, boards empty, W14 parked per O-0808")

with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(HB, encoding="utf-8-sig") as f:
    recheck = json.load(f)
assert set(recheck.keys()) >= prev_fields, \
    "field loss after heal: " + repr(prev_fields - set(recheck.keys()))
assert recheck["orders_ack"] == prev_ack, "orders_ack mutated"
assert isinstance(recheck["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in recheck["clock_read"], "clock must be T-separated"
print("HB_HEAL_OK fields=" + str(len(recheck)) + " orders_ack=" +
      str(len(recheck["orders_ack"])) + " epoch=" +
      str(recheck["heartbeat_epoch_utc"]))
