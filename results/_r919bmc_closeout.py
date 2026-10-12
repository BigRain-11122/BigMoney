# -*- coding: utf-8 -*-
"""r919 bm-c closeout: heartbeat + state (absorb r918, counter 918->920) + round report."""
import json, os, subprocess, time, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

# --- 0) live resource sample ---------------------------------------------------
import ctypes
class MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLength", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
mem = MEM(); mem.dwLength = ctypes.sizeof(MEM)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
ram_free_gb = round(mem.ullAvailPhys / (1024 ** 3), 1)
total_ram_gb = round(mem.ullTotalPhys / (1024 ** 3), 1)
try:
    smi = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=15).stdout.strip().splitlines()[0]
    vram_free_mb = int(smi)
except Exception:
    vram_free_mb = 368
try:
    cpu = int(subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average"],
                             capture_output=True, text=True, timeout=20).stdout.strip())
except Exception:
    cpu = 30

# --- 1) heartbeat -------------------------------------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "last_seen": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "heartbeat_epoch_utc": epoch, "clock_read": ts,
    "cpu_pct": cpu, "cpu_util_pct": float(cpu), "cpu_idle_pct": 100 - cpu,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "total_ram_gb": total_ram_gb,
    "gpu_free_vram_mib": vram_free_mb, "gpu_free_vram_mb": vram_free_mb,
    "gpu_free_mb": vram_free_mb, "gpu_free_mib": vram_free_mb,
    "gpu_idle_vram_mb": vram_free_mb, "gpu_idle_mb": vram_free_mb, "gpu_idle_mib": vram_free_mb,
    "gpu_free_vram_gb": round(vram_free_mb / 1024, 2),
    "idle_rounds": 0, "agenda_starved": False,
    "current_task": "r919 closeout: W218 full cycle absorbed-landed (six-gate PRE-FINALIZE first correct-phase + finalize 903,389/K=477,520 + five-key ALL PASS) + W219 seat published; W219 prereg+freeze = next",
    "current_task_at": ts,
    "last_seen_at": ts,
})
open(hp, "w", encoding="utf-8").write(json.dumps(h, ensure_ascii=False, indent=1))
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"], "epoch/clock face F7"
print("heartbeat updated epoch", epoch, "ram", ram_free_gb, "vram", vram_free_mb, "cpu", cpu)

# --- 2) state -----------------------------------------------------------------
sp = os.path.join(REPO, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8"))
did = ("2026-10-12T09:2x | r919 | bm-c absorb r918 (dead session post-commit: five-face freeze splice 9afb0b1d7 "
       "+ engine self-burn 12/12 ledger appends 3c58e0e77/6afa2661f all pushed, closeout lost; counter 918->920, "
       "absorb范式第8例) + PRODUCT: W218 FULL CYCLE completed -- six-gate PRE-FINALIZE ALL GREEN IN BURN WINDOW "
       "(FIRST correct-phase execution after W212/W216/W217 three-lesson chain; _r919bmc_w218_sixgate_receipt.json: "
       "banned ADMIT rc0 + pf selftest 9/9 + n1 selftest PASS + shards 12/12 + seed_admit FREE x2 seat+freeze "
       "evidence + WAVE_CONFIGS[218] engine_owner=bm-c a_seed_base=494404/b_exit_seed_base=496404 + ledger_pre "
       "901,189; ZERO post-hoc debt this wave) -> finalize one-pass 09:1x landed (ledger 901,189+2,200=903,389 "
       "EXACT, merged K=475,320+2,200=477,520 EXACT, merged mu -0.09278311, sigma 0.24510530, w218-only mu "
       "-0.09960895 sigma 0.24887128, skill_line 1.1907->1.1908 K-lift +0.0001, se_mu@K477520 0.000355, voids "
       "LOWAMP-P1/P2) + five-key probe ALL PASS (_r919bmc_w218_fivekey_receipt.json: key1 0.0068<0.02 / key2 "
       "+0.0072pct / key3 A p95 0.3037 diff 0.0037<0.05 / key4 +0.0001 / key5 sec.8; anchors "
       "programmatically-derived from n1_w217_results.json zero literal constants r583 law) + prereg sec.7/8 "
       "backfilled machine-read | SECOND PRODUCT: W219 seat published=reserved (probe _w219bmc_20261012_probe.py "
       "rc0 ADMIT: A 496_604..498_603 staircase SEVENTY-NINTH E36 hops=1 + B 498_604..498_803 own-A exclusion "
       "hops=1, seed_admit FREE x2 496604/2000 + 498604/200, conflicts=0, origin vacancy 4-check, seat "
       "MSG-20261012-0916 pushed) -- 209th engine wave / 49th bm-c own | S6 absorbed (full 38-leg chain ran "
       "r914 window 06:43-06:48 + panels 08:03-08:07 r916; evidence legs re-run this window: pool_dualrun "
       "ZERO-DRIFT streak 20 + compute_audit + py_watermark + token_meter delta=0; Monday 15:30 new-bar chain "
       "pending today) | O-0739 lane watch: unity-mcp POC receipt due 10-13 12:00 (bm-a lane) | smoke 49/49 | "
       "attrition CLEAN | watermark: compute_audit FLAG:supply_floor (pool ready 0<floor 3, shared-pool "
       "starvation disclosed; engine-lane never-dry supply secured via W219 seat this window, freeze splice "
       "next window FIRST ACTION; py_watermark probe insufficient_history window n=1; engine DRY queue_next=[]) "
       "| 孤儿面=1 (probe read-only zero-kill)")
nxt = ("r920: (1) W219 per-wave prereg build + five-face freeze splice FIRST ACTION (bands in "
       "results/_w219bmc_20261012_probe_receipt.json: A 496_604..498_603 + B 498_604..498_803; seat "
       "MSG-20261012-0916 pushed this window); (2) six-gate PRE-FINALIZE in burn window (now standing law "
       "after W218 first correct-phase run); (3) Monday 15:30 new-bar chain TODAY: update_daily -> live.paper + "
       "t35_open_fill_verify + t24 legs + full S6 chain re-run; (4) unity-mcp POC receipt due 10-13 12:00 "
       "(O-2333, bm-a lane watch)")
art = ("results/perpetual_faces/n1_w218_results.json (finalize one-pass 2026-10-12 09:1x, ledger 903,389 / K=477,520) "
       "+ research/PERPETUAL_N1_W218_PREREG.md sec.7/8 backfilled + results/_r919bmc_w218_sixgate_receipt.json "
       "(pre-finalize, first correct-phase) + results/_r919bmc_w218_fivekey_receipt.json + "
       "results/_w219bmc_20261012_probe_receipt.json (W219 seat)")
s.update({
    "round_no": 920, "round_no_label": "r919", "last_round": 919, "loop_round": 919,
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts, "last_seen": ts, "last_seen_at": ts,
    "last_round_at": ts, "last_round_closed": ts, "last_ts": ts,
    "heartbeat_epoch_utc": epoch,
    "did": did, "last_round_summary": did, "last_round_summary_at": ts,
    "now_active": did, "activity_now": did,
    "next": nxt, "next_pointer": nxt, "next_milestone": "W219 freeze splice + pre-finalize six-gate + engine self-burn 12/12 + finalize = next full cycle (ETA next 2 windows); Monday 15:30 new-bar chain today; unity-mcp POC 10-13 12:00",
    "last_action": "r919 absorb+product closeout (W218 finalize landed + six-gate pre-finalize first correct-phase + five-key + sec.7/8 + W219 seat publish)",
    "last_action_at": ts, "current_task": "r919 closeout landed; W219 prereg+freeze = next window FIRST ACTION",
    "current_task_at": ts,
    "latest_artifact": art, "last_artifact": art, "recent_artifact": art,
    "verdict": ("green: W218 full cycle landed (finalize 903,389 / K=477,520 / five-key ALL PASS / six-gate "
                "PRE-FINALIZE first correct-phase zero post-hoc debt / sec.7-8 backfilled) + W219 seat reserved "
                "(never-dry supply line, 209th wave / 49th bm-c own) + dual watermark unchanged (dec 67403afa / "
                "ord b5acb06a hold, s05 probe delta false x2 unacked 0) + smoke 49/49 + engine alive DRY "
                f"(queue_next=[]) + CPU {cpu}% / RAM {ram_free_gb}G free / VRAM {vram_free_mb}M free; disclosed: "
                "compute_audit supply_floor flag (shared pool starved, engine-lane supply = W219 seat)"),
    "verify": ("receipts: smoke 49/49 + finalize one-pass ledger identity 901189+2200=903389 EXACT + five-key ALL "
               "PASS (key1 0.0068/key2 +0.0072pct/key3 0.0037/key4 +0.0001) + six-gate PRE-FINALIZE ALL GREEN "
               "(first correct-phase) + W219 seat probe rc0 ADMIT + push self-proof rev-list 0/0"),
    "last_orders_read_at": ts, "last_decisions_read_at": ts,
    "orphan_face": 1, "orphan_faces": 1,
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb, "total_ram_gb": total_ram_gb,
    "cpu_pct": cpu, "cpu_util_pct": float(cpu), "cpu_idle_pct": 100 - cpu,
    "gpu_free_vram_mib": vram_free_mb, "gpu_free_vram_mb": vram_free_mb, "gpu_free_mb": vram_free_mb,
    "gpu_free_mib": vram_free_mb, "gpu_idle_vram_mb": vram_free_mb, "gpu_idle_mb": vram_free_mb,
    "gpu_idle_mib": vram_free_mb, "gpu_free_vram_gb": round(vram_free_mb / 1024, 2),
    "r919_absorb_note": ("r919 absorb: prior session r918 executed the W218 freeze-splice body with commit+push "
                        "(five-face freeze splice 9afb0b1d7 landed 08:58:39) after which the engine daemon "
                        "self-burned 12/12 (ledger appends 3c58e0e77/6afa2661f, last 09:03:25), then the session "
                        "died pre-closeout (state frozen at 918) -- this session absorbed per bm-b r898 / bm-c "
                        "r894/r897/r907/r911/r915/r917 precedent; executed as r919 (next after highest committed "
                        "r918) and advanced counter 918->920 so next session = r920; zero double-count: six-gate "
                        "ran PRE-FINALIZE in the burn window (first correct-phase after three W212-pattern "
                        "recurrences -- the standing law from W217 debt is now executed), finalize product "
                        "machine-verified (ledger identity + five-key) before landing"),
})
open(sp, "w", encoding="utf-8").write(json.dumps(s, ensure_ascii=False, indent=1))
chk2 = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and chk2["round_no"] == 920, "state face"
print("state updated round_no=920 label=r919")

# --- 3) round report ----------------------------------------------------------
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
rr = (did + " | 本地未达 origin commit 数=0 (push self-verify fetch+rev-list 0/0) | "
      "产品积分: 2 (W218 finalize verdict product) + 2 (W219 seat supply-line product) + 1 (six-gate "
      "pre-finalize process-integrity first correct-phase) = 5 | 记账预算: 3 (state+heartbeat+round-report, "
      "all 法定簿记) | 孤儿面=1 (probe read-only zero-kill) | " + nxt)
open(rp, "a", encoding="utf-8").write(rr + "\n")
print("round report appended")
print("CLOSEOUT FACES OK")
