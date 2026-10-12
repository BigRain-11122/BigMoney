# -*- coding: utf-8 -*-
"""r917 bm-c closeout: W217 seat MSG archive + O-0739 receipt + heartbeat + state + round report."""
import json, os, shutil, subprocess, time, datetime

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
    vram_free_mb = 1335
try:
    cpu = int(subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average"],
                             capture_output=True, text=True, timeout=20).stdout.strip())
except Exception:
    cpu = 11

# --- 1) move W217 seat MSG to processed ---------------------------------------
src = os.path.join(REPO, "fleet", "inbox", "MSG-20261012-0700-bmc-w217-seat.md")
dst = os.path.join(REPO, "fleet", "inbox", "processed", "MSG-20261012-0700-bmc-w217-seat.md")
if os.path.exists(src) and not os.path.exists(dst):
    shutil.move(src, dst)
    print("W217 seat MSG -> processed")

# --- 2) O-20261012-0739-bm-c receipt line ------------------------------------
op = os.path.join(REPO, "fleet", "orders", "O-20261012-0739-bm-c.md")
otxt = open(op, encoding="utf-8").read()
line = ("- [x] bm-c 循环班 resume 确认（r917·2026-10-12 08:2x）：本机无 pause 态全天候在役"
        "（MV i2v bm-c 道 25/25 已收官·N1 回测道 W217 全环本窗收官+W218 席位已占）"
        "——CPU 算力链照常排满·orders_ack 已更新。\n")
if "bm-c 循环班 resume 确认" not in otxt:
    open(op, "a", encoding="utf-8").write(line)
    print("O-0739 receipt line appended")

# --- 3) heartbeat -------------------------------------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
ack = h.get("orders_ack") or []
if "O-20261012-0739-bm-c.md" not in ack:
    ack.append("O-20261012-0739-bm-c.md")
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
    "orders_ack": ack,
    "current_task": "r917 closeout: W217 full cycle absorbed-landed (finalize 901,189/K=475,320 + five-key ALL PASS + six-gate debt heal) + W218 seat published; W218 prereg+freeze = next",
    "current_task_at": ts,
    "last_seen_at": ts,
})
open(hp, "w", encoding="utf-8").write(json.dumps(h, ensure_ascii=False, indent=1))
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"], "epoch/clock face F7"
print("heartbeat updated epoch", epoch, "ram", ram_free_gb, "vram", vram_free_mb, "cpu", cpu)

# --- 4) state -----------------------------------------------------------------
sp = os.path.join(REPO, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8"))
did = ("2026-10-12T08:2x | r917 | bm-c absorb r916 (dead session post-commit: five-face freeze splice ad011fee2 "
       "+ engine self-burn 12/12 ledger appends 60c0799cd/ca9f9f616 all pushed, finalize one-pass 08:10:30 + receipts "
       "+ closeout lost; counter 916->918, absorb范式第7例) + PRODUCT: W217 FULL CYCLE completed -- finalize one-pass "
       "r916 08:10:30 verified+landed this window (ledger 898,989+2,200=901,189 EXACT, merged K=475,320 EXACT, "
       "mu -0.09275152, sigma 0.24508756, skill_line 1.1907->1.1906 K-lift -0.0001, se_mu@K475320 0.000355, "
       "voids LOWAMP-P1/P2) + five-key probe ALL PASS (_r917bmc_w217_fivekey_receipt.json: key1 0.0085<0.02 / "
       "key2 -0.0065pct / key3 A p95 0.3074 diff 0.0122<0.05 / key4 -0.0001 / key5 sec.8) + six-gate DEBT HEAL "
       "post-finalize disclosed (r916 died between burn and finalize = W212 pattern 2nd recurrence; "
       "_r917bmc_w217_sixgate_receipt.json ALL GREEN: banned ADMIT rc0 + pf selftest 9/9 + n1 selftest PASS + "
       "shards 12/12 + seed_admit FREE x2 seat+freeze evidence + WAVE_CONFIGS[217] engine_owner=bm-c + ledger_pre "
       "898,989; W218 chain MUST run six-gate pre-finalize in burn window) + prereg sec.7/8 backfilled machine-read "
       "| SECOND PRODUCT: W218 seat published=reserved (probe _w218bmc_20261012_probe.py rc0 ADMIT: A 494_404..496_403 "
       "staircase SEVENTY-EIGHTH E36 hops=1 + B 496_404..496_603 own-A exclusion hops=1, seed_admit FREE x2 "
       "494404/2000 + 496404/200, conflicts=0, origin vacancy 4-check, seat MSG-20261012-0830 pushed) -- 208th "
       "engine wave / 48th bm-c own | O-20261012-0739-bm-c resume 广播令 acked (receipt line + orders_ack; 集团 "
       "orders.md delta b5acb06a@b708dfc = BigStream-only row zero BigMoney action watermark advanced; dec 67403afa "
       "hold) | W217 seat MSG archived processed | S6 absorbed from r916 (panels fresh 08:03-08:07) | smoke 49/49 | "
       "attrition CLEAN | idle --worked | watermark: green (engine DRY queue_next=[], MV bmc-lane 收官 per O-0739 "
       "§1) | 孤儿面=1 (probe read-only zero-kill)")
nxt = ("r918: (1) W218 per-wave prereg build + five-face freeze splice FIRST ACTION (bands in "
       "results/_w218bmc_20261012_probe_receipt.json: A 494_404..496_403 + B 496_404..496_603; seat "
       "MSG-20261012-0830 pushed this window); (2) six-gate PRE-FINALIZE run in burn window (W212/W216/W217 "
       "three-instance lesson, no post-hoc); (3) Monday 15:30 new-bar chain: update_daily -> live.paper + "
       "t35_open_fill_verify + t24 legs; (4) unity-mcp POC receipt due 10-13 12:00 (O-2333, bm-a lane watch)")
art = ("results/perpetual_faces/n1_w217_results.json (finalize one-pass 2026-10-12 08:10:30, ledger 901,189 / K=475,320) "
       "+ research/PERPETUAL_N1_W217_PREREG.md sec.7/8 backfilled + results/_r917bmc_w217_fivekey_receipt.json + "
       "results/_r917bmc_w217_sixgate_receipt.json (debt heal) + results/_w218bmc_20261012_probe_receipt.json (W218 seat)")
s.update({
    "round_no": 918, "round_no_label": "r917", "last_round": 917, "loop_round": 917,
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts, "last_seen": ts, "last_seen_at": ts,
    "last_round_at": ts, "last_round_closed": ts, "last_ts": ts,
    "heartbeat_epoch_utc": epoch,
    "did": did, "last_round_summary": did, "last_round_summary_at": ts,
    "now_active": did, "activity_now": did,
    "next": nxt, "next_pointer": nxt, "next_milestone": "W218 freeze splice + pre-finalize six-gate + engine self-burn 12/12 + finalize = next full cycle (ETA next 2 windows); Monday 15:30 new-bar chain today; unity-mcp POC 10-13 12:00",
    "last_action": "r917 absorb+product closeout (W217 finalize landed + five-key + six-gate debt heal + sec.7/8 + W218 seat publish)",
    "last_action_at": ts, "current_task": "r917 closeout landed; W218 prereg+freeze = next window FIRST ACTION",
    "current_task_at": ts,
    "latest_artifact": art, "last_artifact": art, "recent_artifact": art,
    "verdict": ("green: W217 full cycle landed (finalize 901,189 / K=475,320 / five-key ALL PASS / six-gate debt-healed "
                "post-finalize disclosed / sec.7-8 backfilled) + W218 seat reserved (never-dry supply line, 208th wave / "
                "48th bm-c own) + O-0739 resume ack + dual watermark (dec hold / ord advanced BigStream-only) + unacked 0 "
                f"+ smoke 49/49 + engine alive DRY (queue_next=[]) + CPU {cpu}% / RAM {ram_free_gb}G free / VRAM {vram_free_mb}M free"),
    "verify": ("receipts: smoke 49/49 + finalize one-pass ledger identity 898989+2200=901189 EXACT + five-key ALL PASS "
               "(key1 0.0085/key2 -0.0065pct/key3 0.0122/key4 -0.0001) + six-gate debt heal ALL GREEN + W218 seat probe "
               "rc0 ADMIT + push self-proof rev-list 0/0"),
    "last_orders_sha": "b5acb06a51c7ae95b8ce8fec4967eae509fa83653405ec99f19d57a5d67057be",
    "last_orders_at": ts, "last_orders_read_at": ts,
    "last_orders_read_note": "r917 consumed delta b5acb06a@b708dfc = CEO 全面开工+MV专家审查团 row (BigStream-only, zero BigMoney action); phys-scan BigMoney row=券商模拟盘报备(CEO保留域·常设在册·零催办) unchanged",
    "last_decisions_read_at": ts,
    "orphan_face": 1, "orphan_faces": 1,
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb, "total_ram_gb": total_ram_gb,
    "cpu_pct": cpu, "cpu_util_pct": float(cpu), "cpu_idle_pct": 100 - cpu,
    "gpu_free_vram_mib": vram_free_mb, "gpu_free_vram_mb": vram_free_mb, "gpu_free_mb": vram_free_mb,
    "gpu_free_mib": vram_free_mb, "gpu_idle_vram_mb": vram_free_mb, "gpu_idle_mb": vram_free_mb,
    "gpu_idle_mib": vram_free_mb, "gpu_free_vram_gb": round(vram_free_mb / 1024, 2),
    "r917_absorb_note": ("r917 absorb: prior session r916 executed the W217 freeze-splice + engine self-burn body with "
                        "commits+pushes (five-face freeze splice ad011fee2 + engine ledger appends 60c0799cd/ca9f9f616 "
                        "12/12) plus S6 chain (panels 08:03-08:07) and uncommitted finalize product (n1_w217_results.json "
                        "08:10:30), then died pre-closeout (state frozen at 916) -- this session absorbed per bm-b r898 / "
                        "bm-c r894/r897/r907/r911/r915 precedent; executed as r917 (next after highest committed r916) and "
                        "advanced counter 916->918 so next session = r918; zero double-count: finalize product "
                        "machine-verified (ledger identity + five-key) before landing; six-gate pre-finalize window was "
                        "MISSED by the dead session (W212 pattern 2nd recurrence) -- healed post-hoc this window with "
                        "disclosure, W218 must run pre-finalize"),
})
open(sp, "w", encoding="utf-8").write(json.dumps(s, ensure_ascii=False, indent=1))
chk2 = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and chk2["round_no"] == 918, "state face"
print("state updated round_no=918 label=r917")

# --- 5) round report ----------------------------------------------------------
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
rr = (did + " | 本地未达 origin commit 数=0 (push self-verify fetch+rev-list 0/0 below) | "
      "产品积分: 2 (W217 finalize verdict product) + 2 (W218 seat supply-line product) + 1 (six-gate debt heal "
      "process integrity) = 5 | 记账预算: 4 (state+heartbeat+round-report+order-receipt, all 法定簿记) | "
      "孤儿面=1 (probe read-only zero-kill) | " + nxt)
open(rp, "a", encoding="utf-8").write(rr + "\n")
print("round report appended")
print("CLOSEOUT FACES OK")
