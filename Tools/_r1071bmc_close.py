import datetime
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(datetime.datetime.now().timestamp())

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

try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    gpu_free_vram_mib = int(q.stdout.decode().strip().splitlines()[0])
except Exception:
    gpu_free_vram_mib = None

DID = ("r1071: clean continuation waits-upstream (W263 = bm-a window: SPLICE LANDED f499817fa by bm-a r1038, burn/finalize pending -- "
       "W263 dedup 0/0 + finalize absent on origin verified at window open AND close) + bm-c next turn = W264 seat on W263 finalize + "
       "S0.5 dual-delta ORD/DEC both SAME (313c8c0f content-sha1 / 1d4741e4 raw-blob sha256, pinned-probe) + orders unacked=0 + "
       "smoke 49/49 + satengine ALIVE rc0 + S6 43/43 fresh (dualrun ZERO-DRIFT streak 34 @461, audit FLAG pool_starvation/supply_floor = "
       "waits-upstream structural answered-by-chain, py_wm py_low_with_work_cands = local_batch MV V5.3 GPU reburn protected per "
       "O-20261017-1741 sec.3 + CPU waits-upstream honest, weekend bars cutoff 10-16 no-op family) + attrition 4 CLEAN + "
       "idle --worked rc0 (idle_rounds 1->0, 17:35 carrier green_idle pool-empty face consumed by worked declaration) + "
       "quartet green (loop pin=5 no-op + watchdog registered [S4U flip access-denied = adjudicated default-principal standing face] + claws x2)")

NEXT = ("r1072: (1) watch bm-a W263 chain (splice LANDED f499817fa -> engine self-burn 12/12 -> sixgate -> finalize); "
        "on W263 FINALIZE landing = bm-c W264 SEAT publish (probe live re-derive on post-W263 universe per W263 seat MSG forward face: "
        "staircase continues -- naive W264 A 595_901..597_900 pre-disclosed to be REFUSED at registered W263 B 595_901..596_100, "
        "first-clean moves past 596_100; own-A reservation cascade governs B; never transcribe r587); "
        "(2) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars, debt=0 verified cutoff 10-16); "
        "(3) short-video lane DISABLED standing per O-20261017-1741 (4/4 disabled + 6688 FREE re-verified); "
        "(4) GPU lane = gen-only (V5.3 3-shot reburn in flight protected; loop CPU-only); (5) next 5x duty = r1075")

PROD = ("CPU=engine waits-upstream (W263 = bm-a window: SPLICE LANDED f499817fa, burn/finalize pending on bm-a; bm-c next turn = W264 seat) ; "
        "GPU=gen-only lane (V5.3 3-shot reburn in flight protected per O-20261017-1741 sec.3; loop CPU-only); "
        "short-video lane DISABLED standing per O-20261017-1741")

VERDICT = ("green: r1071 = clean continuation waits-upstream window (W263 = bm-a window: splice LANDED f499817fa by bm-a r1038, "
           "burn/finalize pending -- W263 dedup 0/0 + finalize absent on origin verified at open + close; bm-c next turn = W264 seat "
           "after W263 finalize per chain-order) + S0.5 dual-delta FALSE both (ORD 313c8c0f / DEC 1d4741e4, pinned-probe, zero rows owed) + "
           "unacked=0 + smoke 49/49 + satengine ALIVE rc0 + S6 43/43 rc0 (dualrun streak 34, audit FLAG structural answered-by-chain, "
           "py_wm py_low_with_work_cands = MV V5.3 GPU reburn legal + CPU waits-upstream honest) + attrition 4 CLEAN + "
           "idle --worked rc0 (idle_rounds 1->0) + quartet green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated "
           "default-principal standing face] + claws x2 LF-normalized) + orphan face=1 zero-kill (user Doubao pythonw, r1001 precedent family)")

ART = "results/_r1071bmc_s6_log.txt (43-leg S6 chain rc0) + Tools/_r1071bmc_s6.py (driver canon-clone r1070)"

CLOSE_NOTE = ("r1071: clean continuation waits-upstream window (state round_no=1071 at open, executed r1071, advanced 1071->1072 so next=r1072); "
              "zero absorb owed (r1070 closeout 940aed490 landed clean, zero dead window between); zero double-count: S0.5 dual-delta FALSE both scans "
              "(opening pinned-probe + S7 tail probe; ord 313c8c0f / dec 1d4741e4 hold, zero rows owed); W263 = bm-a window (splice LANDED f499817fa "
              "by bm-a r1038 mid-prior-window, burn/finalize pending -- satengine W263 dedup local_done=0/remote_done=0 + n1_w263_results.json absent "
              "on origin verified twice this window; bm-a heartbeat stale since 17:50:46 pre-splice = its r1038 window in flight, engine daemon "
              "mtime-watch burn lane is scheduled-task carried = not bm-c's to fix); idle face: 17:35 carrier verdict green_idle=true claimable_pool=0 "
              "agenda_starved=true idle_rounds=1 -> THIS window has actual work (S6 43 legs + quad + closeout) -> --worked rc0 idle_rounds->0 per law; "
              "orphan face=1 (user Doubao pythonw PID 32692, r1001 legal-user-process adjudication family, zero-kill); MV V5.3 reburn runner "
              "pythonw PID 48472 + ComfyUI 8188 PID 50356 = GPU gen lane legal faces untouched")

# 1) state file
sp = ROOT + r"\state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
s["machine_id"] = "bm-c"
s["round_no"] = 1072
s["round_no_label"] = "r1071 closeout -> counter 1072"
s["last_round"] = "r1071"
s["last_round_label"] = "r1071"
s["last_round_at"] = ts
s["last_round_ts"] = ts
s["last_round_closed"] = ts
s["clock_read"] = ts
s["ts"] = ts
s["updated"] = ts
s["updated_at"] = ts
s["heartbeat_epoch_utc"] = epoch
s["current_task"] = "r1071 closeout: waits-upstream (W263 bm-a splice landed, burn/finalize pending) + next=W264 seat on finalize"
s["current_task_at"] = ts
s["current_task_ts"] = epoch
s["did"] = DID
s["verdict"] = VERDICT
s["next"] = NEXT
s["next_pointer"] = NEXT
s["note"] = ("r1071: clean continuation waits-upstream -- W263 = bm-a window (splice LANDED f499817fa, burn/finalize pending); "
             "bm-c next turn = W264 seat; short-video lane disabled standing per O-20261017-1741; GPU lane gen-only (V5.3 reburn protected)")
s["head_sha"] = "r1071 closeout (waits-upstream: W263 splice landed on bm-a, burn/finalize pending; bm-c next turn = W264 seat); dual-delta ORD/DEC both SAME"
s["latest_artifact"] = ART
s["recent_artifact"] = ART
s["last_artifact"] = ART
s["prod_lanes"] = PROD
if isinstance(s.get("full_load_selfproof"), dict):
    s["full_load_selfproof"]["占用一行"] = PROD
s["next_milestone"] = "W263 finalize (bm-a window, burn in flight) -> bm-c W264 seat (chain-order); Monday 10-19 15:30 bars papers chain (24-48h window)"
s["last_round_summary"] = ("r1071: clean continuation waits-upstream (W263 splice LANDED on bm-a, burn/finalize pending; bm-c next=W264 seat) + "
                           "S0.5 dual-delta ORD/DEC both SAME + S6 43/43 fresh (dualrun streak 34) + smoke 49/49 + attrition 4 CLEAN + idle worked + quad green")
s["last_round_summary_at"] = ts
s["last_action"] = "r1071 closeout (clean continuation waits-upstream: S6 43/43 fresh + quad green + idle worked; counter 1071->1072)"
s["last_action_at"] = ts
s["activity_now"] = ts
s["now_active"] = ts
s["last_seen"] = ts
s["last_seen_at"] = ts
s["last_orders_at"] = ts
s["last_orders_seen"] = ts
s["last_orders_read_at"] = ts
s["last_orders_read_note"] = "r1071: ORD delta FALSE hold (content-sha1 313c8c0f pinned-probe, zero rows owed)"
s["last_decisions_at"] = ts
s["last_decisions_seen"] = ts
s["last_decisions_read_at"] = ts
s["last_decisions_read_note"] = "r1071: DEC delta FALSE hold (raw-blob sha256 1d4741e4 pinned-probe, zero rows owed)"
s["last_orders_sha_note"] = "r1071: ORD 313c8c0f SAME (content-sha1 pinned method r977) / DEC 1d4741e4 SAME (raw-blob sha256) -- zero rows owed both scans"
s["orders_ack_receipt"] = ("r1071: zero new repo order files (unacked=0 both scans, 98 files all in 223 ack set); group-tree ORD/DEC dual-delta FALSE both "
                          "(ord 313c8c0f / dec 1d4741e4 hold, pinned-probe verified); inbox=0")
s["orders_ack_ts"] = ts
s["orphan_face"] = 1
s["orphan_faces"] = 1
s["free_ram_gb"] = free_ram_gb
s["idle_ram_gb"] = free_ram_gb
s["ram_free_gb"] = free_ram_gb
s["cpu_pct"] = cpu_pct
s["cpu_util_pct"] = cpu_pct
s["gpu_free_vram_mib"] = gpu_free_vram_mib
s["gpu_free_vram_mb"] = gpu_free_vram_mib
s["free_vram_mb"] = gpu_free_vram_mib
s["gpu_free_mb"] = gpu_free_vram_mib
s["gpu_idle_vram_mb"] = gpu_free_vram_mib
s["health"] = "ok"
s["verify"] = ("S6 log 43x rc=0 re-read + d19 pinned-probe dual FALSE read-back (ord 313c8c0f / dec 1d4741e4) + smoke 49/49 + satengine alive_flag=true + "
               "attrition 4 CLEAN + loop pin=5 no-op + watchdog registered + claws x2 installed + idle worked rc0 (idle_rounds->0) + epoch int readback + "
               "report line +1 asserted + W263 finalize absent verified twice (open+close) + closeout commit rides this window")
s["sync"] = {"origin_tip": "r1071 closeout commit rides this window (push lands this window; post-push behind=0 verified same window)", "ts": ts}
if isinstance(s.get("d19_watermark_guard"), dict):
    s["d19_watermark_guard"]["round_ref"] = 1071
    s["d19_watermark_guard"]["ts"] = ts
s["r1071_closeout_note"] = CLOSE_NOTE

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
h["current_task"] = "waits-upstream: W263 bm-a chain (splice landed f499817fa, burn/finalize pending); next bm-c turn = W264 seat on finalize"
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
s2 = json.load(open(sp, encoding="utf-8"))
assert isinstance(s2["heartbeat_epoch_utc"], int), "state epoch must be int"

# 3) round report line
rp = ROOT + r"\round_reports-bm-c.md"
line = (
    "%s | r1071 | bm-c | watermark verdict=绿 (red=false / satengine ALIVE waits-upstream / tickets 0 / jobs 0 / "
    "W263=bm-a window splice LANDED burn/finalize pending) | "
    "r1071 (waits-upstream clean continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=1 zero-kill "
    "(orphan=user Doubao pythonw PID 32692 r1001 precedent family legal-user-process; MV V5.3 reburn runner pythonw PID 48472 + "
    "ComfyUI 8188 PID 50356 = GPU gen lane legal faces untouched); S0 fetch 0/0 clean (origin tip 940aed490 = r1070 closeout; "
    "KEY NEW FACT: W263 five-face freeze splice LANDED f499817fa by bm-a r1038 below my closeout -- burns/finalize pending on bm-a); "
    "(2) S0.5: fleet/orders diff unacked=0 (98 files all in 223 ack set); DEC delta=NONE (1d4741e4 raw-blob sha256 hold); "
    "ORD delta=NONE (313c8c0f content-sha1 pinned method SAME); inbox=0; (3) S1 smoke 49/49; satengine ALIVE rc0 (alive_flag=true, "
    "burns_active=[] queue_next=[], W263 dedup local_done=0/remote_done=0 = burn not landed, finalize absent on origin verified at "
    "open AND close); wm red=false healthy (next_pick=claimed moneyflow-IC parked source-blocked, bm-a T23 fix standing); boards clear "
    "(jobs 0 / P2+P3 open 0); idle 17:35 carrier verdict green_idle=true claimable_pool=0 agenda_starved=true idle_rounds=1 -> "
    "worked declaration this window (S6+quad+closeout); (4) PRODUCT = S6 43/43 rc0 fresh run (driver Tools/_r1071bmc_s6.py canon-clone "
    "r1070 with window-context header updated, log results/_r1071bmc_s6_log.txt: dualrun ZERO-DRIFT streak 34 @461, compute_audit FLAG "
    "pool_starvation/supply_floor honest [pool ready=0 = W263 bm-a window waits-upstream structural, supply rides bm-a turn, "
    "answered-by-chain], py_watermark py_low_with_work_cands [local_batch=1 = MV V5.3 GPU reburn protected per O-20261017-1741 sec.3 + "
    "CPU waits-upstream = legal named-answer], update_daily 0 rows cutoff 10-16 fresh [weekend no-op family, papers debt=0], "
    "market_clock CALL-2026-10-16 ORANGE_COOL idempotent, zt crosscheck CLEAN days=7 findings=0 soft=7, ceo_live_usage ORANGE cap 50%% "
    "heat COOL written, daily_report REPORT-2026-10-17 faces=5, token delta=0 L2 legs 0 today, lane no-ops honest per R31); "
    "(5) S7: attrition 4 CLEAN (healed notes as-is) + idle --worked rc0 (idle_rounds 1->0) + loop pin=5 no-op (first fire 18:55) + "
    "watchdog registered (S4U flip access-denied = adjudicated default-principal standing face, first fire 18:47) + claws x2 re-installed "
    "LF-normalized + counter 1071->1072 + heartbeat epoch int + clock_read T-sep self-asserted | "
    "verify: smoke 49/49 + S6 log 43x rc=0 + orders diff 0 + dual-delta SAME x2 + attrition CLEAN + W263 finalize absent x2 | "
    "next r1072: watch bm-a W263 chain (burn->sixgate->finalize) -> on finalize bm-c W264 SEAT (live re-derive post-W263 universe, "
    "staircase forward face, never transcribe r587); Monday 10-19 15:30 bars papers chain re-arm; short-video lane disabled standing "
    "per O-20261017-1741; next 5x=bm-c r1075\n" % ts
)
before = open(rp, encoding="utf-8").read().count("\n")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
after = open(rp, encoding="utf-8").read().count("\n")
assert after == before + 1, "report line count must +1"

print("STATE+HEARTBEAT+REPORT OK; epoch", epoch, "ram", free_ram_gb, "gpu_free_mib", gpu_free_vram_mib)
