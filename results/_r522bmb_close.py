# -*- coding: utf-8 -*-
# r522 bm-b closing bookkeeping: state.json round_no++, heartbeat, round report line
import json, time, datetime

NOW = datetime.datetime.now().astimezone()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + NOW.strftime("%z")[:3] + ":" + NOW.strftime("%z")[3:]
EPOCH = int(time.time())

# 1. state.json (bm-b convention file) -- round_no 521 -> 522
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 522
st["last_round_at"] = ISO
st["last_round_ts"] = EPOCH
st["ts"] = ISO
st["updated"] = ISO
st["updated_at"] = ISO
with open("state.json", "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json round_no:", st["round_no"])

# 2. heartbeat fleet/machines/bm-b.json
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH          # MUST be JSON int (R170/R178)
hb["clock_read"] = ISO                      # T-separated ISO 8601 (R262)
hb["round_no"] = 522
hb["current_task"] = ("r522 closed: W25 finalize one-pass (K=52,920, ledger 419,548, S5 4/4 PASS, "
                      "S7/S8 backfill+selftest green) + engine orphan-reconcile telemetry fix "
                      "(4 orphans W10/W13/W25 healed, selftest 8 legs); next: W28 freeze gated on "
                      "bm-a W27 row (r511 table-tail law)")
ack = hb.get("orders_ack") or []
for o in ["O-20261001-2103-bm-a.md", "O-20261001-2106-bm-a.md"]:
    if o not in ack:
        ack.append(o)
hb["orders_ack"] = ack
import psutil
hb["cpu_util_pct"] = psutil.cpu_percent(interval=None)
mem = psutil.virtual_memory()
hb["free_ram_gb"] = round(mem.available / 1024**3, 1)
hb["idle_ram_gb"] = hb["free_ram_gb"]
gpu_free = None
try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free = round(int(r.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
    hb["gpu_idle_vram_gb"] = gpu_free
    hb["gpu_free_vram_mb"] = int(gpu_free * 1024)
    hb["gpu_idle_vram_mb"] = int(gpu_free * 1024)
hb["verdict"] = "healthy"
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# self-verify: epoch MUST be int (smoke F7)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat ok: epoch=int", chk["heartbeat_epoch_utc"], "orders_ack:", len(chk["orders_ack"]))

# 3. round report line (bm-b convention: logs/iteration-loop/round_reports.md)
line = (
    f"{ISO} | r522 | bm-b | W25 finalize one-pass same-round closed loop (14th engine wave, "
    f"bm-b 7th own: K=52,920 exact, merged mu -0.09240 sigma 0.24460, S5 4/4 PASS, ledger "
    f"417,348+2,200=419,548 chain-linear prev=W24 live-head derive; S7/S8 backfill 8/8 + runner "
    f"selftest green post-backfill + attrition CLEAN) + engine orphan-reconcile telemetry fix "
    f"(scripts/saturation_engine.py: igniting-tick pre-persist crash loses burn record -> no "
    f"ledger row ever; 4 historical orphans W10-7/W13-0/W13-1/W25-0 reconciled "
    f"orphan_reconciled=true, selftest 8 legs, live-verified) + O-2103/O-2106 receipts (bm-b "
    f"lane: full-A panel fresh cutoff 2026-09-30 + engine grammar machinery standing; R-tickets "
    f"await GM dispatch) + S6 34 legs rc0 holiday no-ops + D-19 MATCH-unchanged + watermark "
    f"green (red=false) + engine alive (heartbeat 38s, queue 0 honest: W26=bm-c in-flight, "
    f"W27 row absent, W28 seat gated on it per r511) | evidence: n1_w25_results.json on origin "
    f"(65aa00add), _r522bmb_w25_backfill.py 8/8, _r522bmb_conflict_resolver.py 13/13 "
    f"ts-newer, push verified ls-tree 5/5 | next: W28 freeze when bm-a W27 row lands; "
    f"bm-c Tools/saturation_engine.py orphan-leg port handed via MSG-213x\n"
)
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report line appended")
