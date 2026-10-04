# -*- coding: utf-8 -*-
"""r690 bm-a closeout: state round_no + heartbeat (programmatic write +
reparse self-proof per r678; epoch int + clock T-format per R170/R262/r641)."""
import json, time, datetime, io, subprocess

# ---- state: round_no + next pointer ----
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 690
st["next"] = ("r691+: (1) W3 judge verdict product harvest (bm-c pid 33768 in flight, "
              "projected ~22:1x; on landing: verify complete=true + 777 cells + E[FP] 38.85 "
              "+ eligible -> adoption commit per W2 precedent 4f4100dc1 -> CEO 48h report "
              "clock starts) (2) N2 slice-2 seat-ping MSG-2026-10-04-1830-bma-bmb sent: no "
              "reply + zero tree progress within 2 rounds = plan A takeover (build legs per "
              "tl14 4-face recipe) (3) W117 finalize single-shot on bm-b W116 finalize landing "
              "(rehearsal r684 armed) (4) fund trio NULLS finalize watch 10-05..09 (bm-b "
              "canonical) (5) 10-06+ style-rotation drafting (needs bm-b astock_daily panel)")
with io.open(sp, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
re_st = json.load(open(sp, encoding="utf-8-sig"))
assert re_st["round_no"] == 690, "round_no write failed"
print("state round_no -> 690 reparse OK")

# ---- heartbeat: fresh sampling + epoch int + clock T-format ----
import psutil
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
now = datetime.datetime.now().astimezone()
epoch = int(time.time())
clock = now.isoformat(timespec="seconds")          # T-separated, +08:00 suffix
assert "T" in clock and clock[10] == "T", "clock T-format violation"
cpu = psutil.virtual_memory()
hb["clock_read"] = clock
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
hb["current_task"] = ("r690 waiting-state round DELIVERED: W3 judge in flight (bm-c canonical "
                      "~22:1x projected), W117 gated on bm-b W116, N2 slice-2 seat-ping "
                      "MSG-2026-10-04-1830 sent (42h-stalled claim, plan-A default), trio "
                      "NULLS bm-b canonical 10-05..09; S6 37/37 rc0 + smoke 48/48")
hb["verdict"] = ("green: smoke 48/48, S6 37/37 rc0 113.9s, board 0 open, satengine alive, "
                 "D-19 dual MATCH, orders 154/154, pool dualrun zero-drift")
hb["health"] = "ok"
hb["last_round"] = "r690"
hb["loop_round"] = 690
hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.3), 1)
hb["cpu_util_pct"] = hb["cpu_pct"]
hb["idle_ram_gb"] = round((cpu.total - cpu.used) / 2**30, 1)
hb["free_ram_gb"] = hb["idle_ram_gb"]
hb["idle_ram_mb"] = int((cpu.total - cpu.used) / 2**20)
# GPU best-effort via nvidia-smi (single short call, CREATE_NO_WINDOW)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, timeout=20,
                       creationflags=0x08000000)
    free_mb = int(r.stdout.decode().strip().splitlines()[0])
    hb["gpu_free_vram_mb"] = free_mb
    hb["gpu_free_vram_mib"] = free_mb
    hb["gpu_idle_vram_mb"] = free_mb
    hb["gpu0_free_vram_gb"] = round(free_mb / 1024, 2)
except Exception as e:  # keep prior values on read failure
    print("nvidia-smi read skipped:", str(e)[:80])
with io.open(hp, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
re_hb = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(re_hb["heartbeat_epoch_utc"], int), "reparse epoch int FAIL"
assert "T" in re_hb["clock_read"], "reparse clock T FAIL"
print("heartbeat OK: epoch=%d int, clock=%s, cpu=%s%%, ram_free=%sGB" %
      (re_hb["heartbeat_epoch_utc"], re_hb["clock_read"],
       re_hb["cpu_pct"], re_hb["idle_ram_gb"]))
