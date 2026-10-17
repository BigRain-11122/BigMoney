import datetime
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(datetime.datetime.now().timestamp())

# machine metrics via CIM (in-process PowerShell call avoided; use python wmic-equivalent through subprocess powershell? Use psutil if available)
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / (1024 ** 3), 2)
    cpu_pct = psutil.cpu_percent(interval=1.0)
    cores = psutil.cpu_count(logical=True)
except Exception:
    free_ram_gb = None
    cpu_pct = None
    cores = 32

# GPU free VRAM via nvidia-smi
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    gpu_free_vram_mib = int(q.stdout.decode().strip().splitlines()[0])
except Exception:
    gpu_free_vram_mib = None

DID = ("r1070: 5x HANDOVER duty row (r986-r1070 window, 16 missing 5x cuts disclosed) + S6 43/43 fresh (dualrun streak 33, "
       "audit flags pool_starvation/supply_floor = waits-upstream structural face honest, zt soft-warns disclosed, weekend no-op family) "
       "+ waits-upstream verified (origin tip aba6247ec, W263 splice/burn/finalize pending on bm-a) + dual-delta ORD/DEC both SAME + "
       "orders unacked=0 + smoke 49/49 + satengine ALIVE + attrition 4 CLEAN + idle --worked + quartet green (watchdog S4U flip denied = adjudicated face)")

# 1) state file
sp = ROOT + r"\state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
s["machine_id"] = "bm-c"
s["round_no"] = 1071
s["round_no_label"] = "r1070 closeout -> counter 1071"
s["last_round"] = "r1070"
s["last_round_at"] = ts
s["last_round_ts"] = ts
s["clock_read"] = ts
s["ts"] = ts
s["updated"] = ts
s["updated_at"] = ts
s["heartbeat_epoch_utc"] = epoch
s["current_task"] = "r1070 closeout: waits-upstream (W263 bm-a) + next=W264 seat on finalize"
s["current_task_at"] = ts
s["did"] = DID
s["free_ram_gb"] = free_ram_gb
s["idle_ram_gb"] = free_ram_gb
s["ram_free_gb"] = free_ram_gb
s["cpu_pct"] = cpu_pct
s["gpu_free_vram_mib"] = gpu_free_vram_mib
s["gpu_free_vram_mb"] = gpu_free_vram_mib
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 2) heartbeat
hp = ROOT + r"\fleet\machines\bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["machine_id"] = "bm-c"
h["last_seen"] = ts
h["last_seen_at"] = ts
h["ts"] = ts
h["clock_read"] = ts
h["heartbeat_epoch_utc"] = epoch
h["cpu_cores"] = cores
h["free_ram_gb"] = free_ram_gb
h["gpu_free_vram_mib"] = gpu_free_vram_mib
h["gpu_free_vram_mb"] = gpu_free_vram_mib
h["current_task"] = "waits-upstream: W263 bm-a chain (splice/burn/finalize pending); next bm-c turn = W264 seat on finalize"
h["verdict"] = "green (waits-upstream; smoke 49/49; S6 43/43; boards clear; pool ready=0 structural per W263 bm-a window)"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["did"] = DID
if "orders_ack" not in h or not isinstance(h.get("orders_ack"), list):
    h["orders_ack"] = []
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# epoch int self-assert
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"], "clock_read must be T-separated"

# 3) round report line
rp = ROOT + r"\round_reports-bm-c.md"
line = (
    "2026-10-17T18:28:xx+08:00 | r1070 | bm-c | watermark verdict=绿 (red=false / satengine ALIVE waits-upstream / tickets 0 / jobs 0 / "
    "W263=bm-a window splice pending) | "
    "r1070 (5x HANDOVER duty round, waits-upstream clean continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=1 zero-kill "
    "(orphan=user Doubao pythonw domain-external read-only; resident_exempt=1 ComfyUI 8188 T28 belt); S0 stash-bridge 5 daemon live-faces -> pull --rebase "
    "Already up to date (origin tip aba6247ec = r1069 closeout; no mid-round bm-a arrival); (2) S0.5: fleet/orders diff unacked=0; DEC delta=NONE "
    "(1d4741e4 raw-blob sha256 hold); ORD delta=NONE (313c8c0f content-sha1 pinned method SAME); orders_ack 223>=disk 98 verified; "
    "(3) S1 smoke 49/49; satengine ALIVE rc0 (burns_active=[] queue_next=[]; W263=bm-a window per chain-order: seat 0d2fa8c13 + prereg b32f6bf1c frozen, "
    "splice ungated post-W262-finalize, pending on bm-a -- bm-c waits-upstream, next bm-c turn = W264 seat after W263 finalize); "
    "wm red=false healthy; idle GREEN-IDLE honest (pool 0, backlog rows 5/6=BigLife CEO-gated parked non-claimable, agenda=W264 waits-upstream structural); "
    "(4) PRODUCT = HANDOVER r1070 row LANDED (research/HANDOVER.md top insert: increment window r986-r1070 85 rounds, 16 missing 5x cuts disclosed "
    "r990-r1065 pit-79 family, W237->W262 chain lifecycle + absorb generations 26th-58th + ledger 1,000,735/K=574,320 W262 EXACT + short-video disable "
    "batch + ORD phantom heal + pointers) + S6 43/43 rc0 fresh run (driver Tools/_r1070bmc_s6.py canon-clone r1069, log results/_r1070bmc_s6_log.txt: "
    "dualrun ZERO-DRIFT streak 33 @461, compute_audit FLAG pool_starvation/supply_floor honest [pool ready=0 = W263 bm-a window waits-upstream, "
    "supply rides bm-a turn, non-idleness], py_watermark py_low_with_work_cands local_batch=S6-chain honest, zt crosscheck soft-warns 7-day band "
    "disclosed, weekend bars 10-16 honest no-op family, lane guards honest no-ops, daily_report+ceo_live_usage written, token L2 0); "
    "(5) S7: attrition 4 CLEAN + idle --worked rc0 (idle_rounds 1->0) + loop pin=5 no-op + watchdog registered (S4U flip access-denied = adjudicated "
    "standing face, first fire 18:28) + claws x2 re-installed LF-normalized + counter 1070->1071 + heartbeat epoch int + clock_read T-sep self-asserted | "
    "verify: smoke 49/49 + S6 log 43x rc=0 + HANDOVER row insert verified L2 + orders diff 0 + dual-delta SAME x2 + attrition CLEAN | "
    "next r1071: watch bm-a W263 chain (splice->burn->finalize) -> on finalize bm-c W264 SEAT (live re-derive post-W263 universe, staircase forward face, "
    "never transcribe r587); Monday 10-19 15:30 bars papers chain re-arm; short-video lane disabled standing per O-20261017-1741; next 5x=bm-c r1075\n"
)
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)

print("STATE+HEARTBEAT+REPORT OK; epoch", epoch, "ram", free_ram_gb, "gpu_free_mib", gpu_free_vram_mib)
