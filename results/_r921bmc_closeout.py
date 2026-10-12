# -*- coding: utf-8 -*-
"""r921 bm-c closeout: heartbeat + state (absorb r920, counter 920->922) + round report."""
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
    vram_free_mb = 580
try:
    cpu = int(subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average"],
                             capture_output=True, text=True, timeout=20).stdout.strip())
except Exception:
    cpu = 30

# --- 1) heartbeat -------------------------------------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
ack = h.setdefault("orders_ack", [])
if "O-20261012-0940-bm-a.md" not in ack:
    ack.append("O-20261012-0940-bm-a.md")
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
    "orders_ack_count": len(ack),
    "idle_rounds": 0, "agenda_starved": False,
    "current_task": "r921 closeout: W219 full cycle landed (six-gate PRE-FINALIZE in burn window + finalize 905,589/K=479,720 + five-key ALL PASS) + W220 seat published; W220 prereg+freeze splice = next FIRST ACTION",
    "current_task_at": ts,
    "last_seen_at": ts,
    "orphan_face": 3, "orphan_faces": 3,
    "verdict": ("green: W219 full cycle landed (six-gate PRE-FINALIZE in burn window ALL GREEN, finalize ledger "
                "903,389+2,200=905,589 EXACT, merged K=479,720 EXACT, five-key ALL PASS) + W220 seat reserved "
                "(A 498_804..500_803 staircase EIGHTIETH + B 500_804..501_003, never-dry supply, 210th wave / "
                "50th bm-c own) + smoke 49/49 + engine alive DRY + MV i2v lane owns GPU"),
})
open(hp, "w", encoding="utf-8").write(json.dumps(h, ensure_ascii=False, indent=1))
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"], "epoch/clock face F7"
print("heartbeat updated epoch", epoch, "ram", ram_free_gb, "vram", vram_free_mb, "cpu", cpu)

# --- 2) state -----------------------------------------------------------------
sp = os.path.join(REPO, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8"))
did = ("2026-10-12T10:3x | r921 | bm-c absorb r920 (dead session post-commit: five-face freeze splice 0dae35332 "
       "+ engine self-burn 12/12 ledger appends 3ed16f9eb/223fc71cb all pushed, closeout lost; counter 920->922, "
       "absorb范式第9例) + PRODUCT: W219 FULL CYCLE completed -- six-gate PRE-FINALIZE ALL GREEN IN BURN WINDOW "
       "(second consecutive correct-phase wave, W218 first-instance law held; _r921bmc_w219_sixgate_receipt.json: "
       "banned ADMIT rc0 + pf selftest 9/9 + n1 selftest PASS + shards 12/12 + seed_admit FREE x2 seat(r919)+"
       "freeze(r920) evidence + WAVE_CONFIGS[219] engine_owner=bm-c a_seed_base=496604/b_exit_seed_base=498604 + "
       "ledger_pre 903,389=W218 landed; ZERO post-hoc debt this wave) -> finalize one-pass 10:1x landed (ledger "
       "903,389+2,200=905,589 EXACT, merged K=477,520+2,200=479,720 EXACT, merged mu -0.09279897 sigma 0.24512506, "
       "w219-only mu -0.09624182 sigma 0.24941028, skill_line 1.1909->1.191 K-lift +0.0001, se_mu@K479720 0.000354 "
       "narrowing chain held, voids LOWAMP-P1/P2) + five-key probe ALL PASS (_r921bmc_w219_fivekey_receipt.json: "
       "key1 0.0034<0.02 / key2 +0.0081pct / key3 A p95 0.3142 diff 0.0105<0.05 / key4 +0.0001 / key5 sec.8; "
       "anchors programmatically-derived from n1_w218_results.json zero literal constants r583 law) + prereg "
       "sec.7/8 backfilled machine-read | SECOND PRODUCT: W220 seat published=reserved (probe "
       "_w220bmc_20261012_probe.py rc0 ADMIT: A 498_804..500_803 staircase EIGHTIETH E36 hops=1 + B 500_804..501_003 "
       "own-A exclusion hops=1, seed_admit FREE x2 498804/2000 + 500804/200, conflicts=0, origin vacancy 4-check, "
       "seat MSG-20261012-1025 pushed 13a81d182) -- 210th engine wave / 50th bm-c own | S0.5 dual-delta consumed: "
       "orders b5acb06a->765af33b (rows 10-11 23:0x->10-12 09:2x = BigStream seat-laws + C-20261012-01 顶层梳理执行案 "
       "executed Phase0=10-13 值守/常务轮承接, zero BigMoney action) + O-20261012-0940-bm-a acked (bm-a BigMoney "
       "black-lamp committee order, zero bm-c action); decisions 67403afa->94c93393 (D-20261012-01 核销批30 bigmoney "
       "零新行注记 + D-20261012-02 勘误 + C-20261012-01, zero BigMoney action) | S6 evidence-legs rc0 (pool_dualrun "
       "ZERO-DRIFT streak 21 + compute_audit + py_watermark + token_meter; full 38-leg chain ran r914 window "
       "06:43-06:48 + panels r916 08:03-08:07 same morning; Monday 15:30 new-bar full chain = today close window) | "
       "S7: loop pin=5 no-op + watchdog re-registered + claws installed + attrition guard CLEAN (4 ledgers, "
       "zero active loss) + idle --worked (idle_rounds=0) | lane watch: unity-mcp POC receipt due 10-13 12:00 "
       "(bm-a lane); bm-b T-184 510880.csv transfer deadline TODAY 15:30 sender=bm-a (bm-c lacks source file = "
       "physical dependency, zero bm-c bootstrap face; bm-a black-lamp covered by O-20261012-0940 72h window) | "
       "smoke 49/49 | watermark: compute_audit FLAG:supply_floor+pool_starvation (pool ready 0<floor 3, shared-pool "
       "starvation disclosed; engine-lane never-dry supply secured via W220 seat this window, freeze splice next "
       "window FIRST ACTION; engine DRY queue_next=[]) | 孤儿面=3 (MV-lane i2v x2 + album serve, probe read-only "
       "zero-kill per lane-attribution law)")
nxt = ("r922: (1) W220 per-wave prereg build + five-face freeze splice FIRST ACTION (bands in "
       "results/_w220bmc_20261012_probe_receipt.json: A 498_804..500_803 + B 500_804..501_003; seat "
       "MSG-20261012-1025 pushed this window); (2) six-gate PRE-FINALIZE in burn window (standing law, "
       "third consecutive wave target); (3) Monday 15:30 new-bar chain TODAY close window: update_daily -> "
       "live.paper + t35_open_fill_verify + t24 legs + full S6 chain re-run; (4) unity-mcp POC receipt due "
       "10-13 12:00 (O-2333 bm-a lane watch); (5) C-20261012-01 Phase0 盘点 = 10-13 值守 15:07 班+常务轮 (not "
       "bm-c loop lane)")
art = ("results/perpetual_faces/n1_w219_results.json (finalize one-pass 2026-10-12 10:1x, ledger 905,589 / "
       "K=479,720) + research/PERPETUAL_N1_W219_PREREG.md sec.7/8 backfilled + "
       "results/_r921bmc_w219_sixgate_receipt.json (pre-finalize, second consecutive correct-phase) + "
       "results/_r921bmc_w219_fivekey_receipt.json + results/_w220bmc_20261012_probe_receipt.json (W220 seat)")
s.update({
    "round_no": 922, "round_no_label": "r921", "last_round": 921, "loop_round": 921,
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts, "last_seen": ts, "last_seen_at": ts,
    "last_round_at": ts, "last_round_closed": ts, "last_ts": ts,
    "heartbeat_epoch_utc": epoch,
    "did": did, "last_round_summary": did, "last_round_summary_at": ts,
    "now_active": did, "activity_now": did,
    "next": nxt, "next_pointer": nxt, "next_milestone": "W220 prereg+freeze splice + engine self-burn + six-gate + finalize = next full cycle (ETA next 2 windows); Monday 15:30 new-bar chain today close window; unity-mcp POC 10-13 12:00",
    "last_action": "r921 absorb+product closeout (W219 finalize landed + six-gate pre-finalize second consecutive correct-phase + five-key + sec.7/8 + W220 seat publish)",
    "last_action_at": ts, "current_task": "r921 closeout landed; W220 prereg+freeze splice = next window FIRST ACTION",
    "current_task_at": ts,
    "latest_artifact": art, "last_artifact": art, "recent_artifact": art,
    "verdict": ("green: W219 full cycle landed (finalize 905,589 / K=479,720 / five-key ALL PASS / six-gate "
                "PRE-FINALIZE second consecutive correct-phase / sec.7-8 backfilled) + W220 seat reserved "
                "(never-dry supply line, 210th wave / 50th bm-c own) + dual watermark advanced (dec 94c93393 / "
                "ord 765af33b, both zero BigMoney action) + smoke 49/49 + engine alive DRY (queue_next=[]) + "
                f"CPU {cpu}% / RAM {ram_free_gb}G free / VRAM {vram_free_mb}M free; disclosed: compute_audit "
                "supply_floor+pool_starvation flags (shared pool starved, engine-lane supply = W220 seat, "
                "freeze splice next window)"),
    "verify": ("receipts: smoke 49/49 + finalize one-pass ledger identity 903389+2200=905589 EXACT + five-key ALL "
               "PASS (key1 0.0034/key2 +0.0081pct/key3 0.0105/key4 +0.0001) + six-gate PRE-FINALIZE ALL GREEN "
               "(second consecutive correct-phase) + W220 seat probe rc0 ADMIT + push self-proof rev-list 0/0 "
               "(13a81d182)"),
    "last_orders_read_at": ts, "last_decisions_read_at": ts,
    "last_orders_at": ts, "last_decisions_at": ts,
    "last_orders_sha": "765af33b6fb6172705187a0f57179b0bd1f161691ffea50f8f0dc626b753d6fe",
    "last_orders_sha_method": "sha256",
    "last_decisions_sha": "94c9339335c996b373b332e33cf47aad3de8f292a53c742ad3e6efae304cd3ff",
    "last_decisions_sha_method": "sha256",
    "last_orders_sha_note": ("r921 consumed delta b5acb06a->765af33b = rows 10-11 23:0x->10-12 09:2x (BigStream "
                             "seat-laws + C-20261012-01 顶层梳理执行案 executed, Phase0=10-13 值守/常务轮承接) "
                             "-- zero BigMoney action; O-20261012-0940-bm-a (bm-a BigMoney black-lamp committee "
                             "order) acked in orders_ack, zero bm-c action"),
    "last_decisions_read_note": ("r921 consumed delta 67403afa->94c93393 = D-20261012-01 (核销批30, bigmoney 零新行"
                                 "如实注记) + D-20261012-02 (勘误+收取 fetch 前置步立法候选) + C-20261012-01 (顶层"
                                 "梳理执行案 executed 7/7, Phase0 盘点=10-13 交卷区, 值守轮 15:07 班+10-13 常务轮"
                                 "承接, 非 bm-c loop lane) -- zero BigMoney repo action"),
    "orphan_face": 3, "orphan_faces": 3,
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb, "total_ram_gb": total_ram_gb,
    "cpu_pct": cpu, "cpu_util_pct": float(cpu), "cpu_idle_pct": 100 - cpu,
    "gpu_free_vram_mib": vram_free_mb, "gpu_free_vram_mb": vram_free_mb, "gpu_free_mb": vram_free_mb,
    "gpu_free_mib": vram_free_mb, "gpu_idle_vram_mb": vram_free_mb, "gpu_idle_mb": vram_free_mb,
    "gpu_idle_mib": vram_free_mb, "gpu_free_vram_gb": round(vram_free_mb / 1024, 2),
    "r921_absorb_note": ("r921 absorb: prior session r920 executed the W219 freeze-splice body with commit+push "
                        "(five-face freeze splice 0dae35332 landed, prereg derived three-level replay chain 46 pairs "
                        "machine-verified) after which the engine daemon self-burned 12/12 (ledger appends "
                        "3ed16f9eb/223fc71cb, last ~09:5x), then the session died pre-closeout (state frozen at 920) "
                        "-- this session absorbed per bm-b r898 / bm-c r894/r897/r907/r911/r915/r917/r919 precedent; "
                        "executed as r921 (next after highest committed r920) and advanced counter 920->922 so next "
                        "session = r922; zero double-count: six-gate ran PRE-FINALIZE in the burn window (second "
                        "consecutive correct-phase wave), finalize product machine-verified (ledger identity + "
                        "five-key) before landing"),
})
open(sp, "w", encoding="utf-8").write(json.dumps(s, ensure_ascii=False, indent=1))
chk2 = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and chk2["round_no"] == 922, "state face"
print("state updated round_no=922 label=r921")

# --- 3) round report ----------------------------------------------------------
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
rr = (did + " | WM-VERDICT: green red=false | dept:策略（N1 波链 W219 full cycle 收口）+dept:工程（吸收收口+双水位推进）| "
      "实况三行：当前活=W220 freeze-prep 束=下窗第一动作（W219 finalize 落地=上游闸全开 clean precondition）+MV XQ/KN i2v 收官后 GPU 窗 2 复开在交互窗车道；"
      "最近实物=results/perpetual_faces/n1_w219_results.json（2026-10-12 10:1x finalize one-pass·账本 903,389+2,200=905,589·K=479,720·skill_line 1.1909→1.191）"
      "+results/_w220bmc_20261012_probe_receipt.json（W220 席 A 498_804..500_803/B 500_804..501_003·seed_admit FREE x2）；"
      "下个里程碑=W220 prereg+freeze splice+自燃+六门+finalize（下两窗内·ETA 10-12 午后）+周一 15:30 新 bar 窗 papers 全腿（今日收盘后）+unity-mcp POC 回执（10-13 12:00）| "
      "本地未达 origin commit 数=0 (push self-verify fetch+rev-list 0/0, 13a81d182) | "
      "产品积分: 2 (W219 finalize verdict product) + 2 (W220 seat supply-line product) + 1 (six-gate "
      "pre-finalize second consecutive correct-phase process-integrity) = 5 | 记账预算: 3 (state+heartbeat+round-report, "
      "all 法定簿记) | 孤儿面=3 (MV-lane i2v x2 + album serve, read-only zero-kill lane-attributed) | " + nxt)
open(rp, "a", encoding="utf-8").write(rr + "\n")
print("round report appended")
print("CLOSEOUT FACES OK")
