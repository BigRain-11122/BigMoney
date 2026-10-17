# r1073 bm-c closeout: round report row + state-bm-c.json + heartbeat update (append-only report, programmatic state edit; r583 zero-literal law: shas read from probe facts)
import datetime, json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- machine stats sample (psutil, same as compute_audit face) ---
cpu_pct = free_ram = gpu_free = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / (1024**3), 2)
except Exception:
    pass

# --- 1) round report row (canonical ROOT round_reports-bm-c.md) ---
ROW = (
    NOW + " | r1073 | bm-c | watermark verdict=green (red=false / satengine ALIVE waits-upstream / tickets 0 open+0 claimed-by-none / jobs 0 / W263=bm-a window splice LANDED f499817fa burn/finalize pending; upstream ACTIVE verified: bm-a listener ALIVE + bm-a local unpushed bigmoney head 46ba27c5fa8f = r1038+ window in flight, not stalled) | "
    "r1073 (waits-upstream clean continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=1 zero-kill (orphan=Doubao pythonw PID 32692 parent-dead CPU-stalled r1001 precedent family legal-user-process, cross-lane not killed per discipline); S0 fetch 0/0 clean (origin tip a76b71fac = r1072 closeout; pull --rebase blocked by 3 shared regenerable probe faces legit dirty, no rebase owed, behind=0); "
    "(2) S0.5: ORD delta=NONE (313c8c0f content-sha1 pinned method SAME) + DEC delta=NONE (1d4741e4 raw-blob sha256 hold) + fleet/orders unacked=0 + inbox=0; S7 tail dual-scan same (zero mid-round rows, behind=0 at close); "
    "(3) S1 smoke 49/49; satengine ALIVE rc0 (alive_flag=true heartbeat_age 63s fresh, burns_active=[] queue_next=[]; W263 dedup local_done=0/remote_done=0 + n1_w263_results.json absent on disk AND origin ls-tree = burn/finalize pending on bm-a) -- bm-c waits-upstream, next bm-c turn = W264 seat after W263 finalize; wm red=false healthy (next_pick=claimed moneyflow-IC parked source-blocked standing); boards clear (jobs 0, task board 0 open, all non-done rows foreign-claimed); "
    "(4) PRODUCT = S6 43/43 rc0 fresh run (driver Tools/_r1073bmc_s6.py canon-clone r1072, log results/_r1073bmc_s6_log.txt: dualrun ZERO-DRIFT streak 36 @461, compute_audit FLAG pool_starvation/supply_floor honest [pool ready=0 = W263 bm-a window waits-upstream structural, supply rides bm-a turn, answered-by-chain], py_watermark py_low_board_clear [legal idle whitelist face: board clear + bandit 0 + pool 0 + no local batch + bars weekend absent, upstream ACTIVE verified pre-declare], update_daily no-op cutoff 10-16 fresh [weekend no-op family, papers debt=0], lane no-ops honest per R31, daily_report REPORT-2026-10-17 faces=5 idempotent, token delta=0 L2 legs 0 today); "
    "(5) S7: attrition 4 CLEAN (healed notes as-is) + idle --worked rc0 (idle_rounds=0, window has actual work) + loop pin=5 no-op (first fire 19:15) + watchdog registered (S4U flip access-denied = adjudicated default-principal standing face) + claws x2 re-installed LF-normalized + counter 1073->1074 + heartbeat epoch int + clock_read T-sep self-asserted | "
    "verify: smoke 49/49 + S6 log 43x rc=0 + orders diff 0 + dual-delta SAME x2 (opening + S7 tail) + attrition CLEAN + W263 finalize absent on origin (satengine dedup 0/0 + ls-tree absent) + upstream liveness (bm-a :8790 ALIVE + unpushed local head 46ba27c5fa8f) | behind-origin=0 (closeout push rides this window) | "
    "next r1074: watch bm-a W263 chain (burn->sixgate->finalize) -> on finalize bm-c W264 SEAT (live re-derive post-W263 universe per W263 seat MSG forward face: staircase continues, naive W264 A 595_901..597_900 pre-disclosed REFUSED at registered W263 B 595_901..596_100, first-clean moves past 596_100; own-A reservation cascade governs B; never transcribe r587); Monday 10-19 15:30 bars papers chain re-arm; short-video lane disabled standing per O-20261017-1741; next 5x=bm-c r1075 HANDOVER duty\n"
)
rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "r", encoding="utf-8") as f:
    txt = f.read()
assert " | r1073 | " not in txt, "r1073 row already present"
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
with open(rp, "r", encoding="utf-8") as f:
    assert " | r1073 | " in f.read()
print("report row appended")

# --- 2) state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_seen_at"] = NOW
st["last_ts"] = NOW
st["activity_now"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_round"] = "r1073"
st["round_no"] = 1074
st["round_no_label"] = "r1073 closeout -> counter 1074"
st["current_task"] = "r1073 closeout: waits-upstream (W263 bm-a burn/finalize pending, upstream ACTIVE verified) + next=W264 seat on finalize"
st["current_task_at"] = NOW
st["last_action"] = "r1073 closeout (waits-upstream clean continuation: S6 43/43 + upstream liveness verified + quad green; counter 1073->1074)"
st["last_round_summary"] = "r1073: clean continuation waits-upstream (W263 bm-a burn/finalize pending; upstream ACTIVE: listener ALIVE + bm-a unpushed head 46ba27c5fa8f; bm-c next=W264 seat) + S0.5 dual-delta FALSE both + S6 43/43 fresh (dualrun streak 36) + smoke 49/49 + attrition 4 CLEAN + idle worked + quartet green"
did = ("r1073: clean continuation waits-upstream (W263 = bm-a window: splice LANDED f499817fa r1038, burn/finalize pending -- dedup 0/0 + n1_w263_results.json absent on disk AND origin ls-tree verified at open; upstream ACTIVE not stalled: bm-a listener ALIVE + bm-a local unpushed bigmoney head 46ba27c5fa8f = r1038+ window in flight) + bm-c next turn = W264 seat on W263 finalize + S0.5 dual-delta ORD/DEC both SAME (313c8c0f content-sha1 / 1d4741e4 raw-blob, opening + S7 tail) + orders unacked=0 + smoke 49/49 + satengine ALIVE rc0 (hb 63s, burns/queue empty) + S6 43/43 fresh (dualrun ZERO-DRIFT streak 36 @461, audit FLAG pool_starvation/supply_floor = waits-upstream structural answered-by-chain, py_wm py_low_board_clear = legal idle whitelist face, daily_report REPORT-2026-10-17 faces=5, token delta=0) + attrition 4 CLEAN + idle --worked rc0 + quartet green (loop pin=5 no-op + watchdog registered [S4U flip access-denied adjudicated standing] + claws x2) + orphan face=1 zero-kill (Doubao pythonw PID 32692 r1001 precedent family legal-user-process)")
st["did"] = did
st["verdict"] = "green: r1073 = clean continuation waits-upstream window (W263 bm-a burn/finalize pending; upstream ACTIVE verified via bm-a listener ALIVE + unpushed local head 46ba27c5fa8f; bm-c next=W264 seat on finalize) + S0.5 dual-delta FALSE both (ORD 313c8c0f / DEC 1d4741e4, pinned-probe, zero rows owed, opening + S7 tail) + unacked=0 + smoke 49/49 + satengine ALIVE rc0 + S6 43/43 rc0 (dualrun streak 36, audit FLAG structural answered-by-chain, py_wm py_low_board_clear = legal idle whitelist [board clear + bandit 0 + pool 0 + bars weekend absent; upstream ACTIVE verified]) + attrition 4 CLEAN + idle --worked rc0 + quartet green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated default-principal standing face] + claws x2 LF-normalized) + orphan face=1 zero-kill (legal-user-process precedent)"
nxt = ("r1074: (1) watch bm-a W263 chain (splice LANDED f499817fa -> engine self-burn 12/12 -> sixgate -> finalize); on W263 FINALIZE landing = bm-c W264 SEAT publish (probe live re-derive on post-W263 universe per W263 seat MSG forward face: staircase continues -- naive W264 A 595_901..597_900 pre-disclosed to be REFUSED at registered W263 B 595_901..596_100, first-clean moves past 596_100; own-A reservation cascade governs B; never transcribe r587); (2) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars, debt=0 verified cutoff 10-16); (3) short-video lane DISABLED standing per O-20261017-1741 (4/4 disabled + 6688 FREE); (4) GPU lane = gen-only (V5.3 reburn in flight protected; loop CPU-only); (5) next 5x duty = r1075 HANDOVER check")
st["next"] = nxt
st["next_pointer"] = nxt
st["note"] = ("r1073: clean continuation waits-upstream window (state round_no=1073 at open, executed r1073, advanced 1073->1074 so next=r1074); zero absorb owed (r1072 closeout a76b71fac landed clean, zero dead window between); zero double-count: S0.5 dual-delta FALSE both scans (opening pinned-probe + S7 tail probe; ord 313c8c0f / dec 1d4741e4 hold, zero rows owed); W263 = bm-a window (splice LANDED f499817fa by bm-a r1038, burn/finalize pending -- satengine W263 dedup local_done=0/remote_done=0 + n1_w263_results.json absent on disk AND origin ls-tree verified; bm-a heartbeat 17:50 stale = its r1038+ window in flight BUT upstream ACTIVE verified: listener :8790 ALIVE + bm-a local unpushed bigmoney head 46ba27c5fa8f = unpushed work beyond origin; engine burn lane = scheduled-task carried on bm-a, not bm-c's to fix); idle face: window has actual work (S6 43 legs + quad + closeout) -> --worked rc0 declared; orphan face=1 (probe py_faces=6, orphan=Doubao pythonw PID 32692 r1001 precedent family legal-user-process cross-lane, zero-kill); MV V5.3 reburn GPU gen lane untouched per O-20261017-1741 sec.3")
st["verify"] = "S6 log 43x rc=0 re-read + d19 pinned-probe dual FALSE read-back (ord 313c8c0f / dec 1d4741e4) + smoke 49/49 + satengine alive_flag=true + attrition 4 CLEAN + loop pin=5 no-op + watchdog registered + claws x2 installed + idle worked rc0 + epoch int readback + report line +1 asserted + W263 finalize absent verified (dedup 0/0 + ls-tree absent) + upstream liveness (bm-a listener + unpushed head) + closeout commit rides this window"
st["latest_artifact"] = "results/_r1073bmc_s6_log.txt (43-leg S6 chain rc0) + Tools/_r1073bmc_s6.py (driver canon-clone r1072)"
st["next_milestone"] = "W263 finalize (bm-a window, upstream ACTIVE verified) -> bm-c W264 seat (chain-order); Monday 10-19 15:30 bars papers chain (24-48h window)"
st["head_sha"] = "r1073 closeout (waits-upstream clean continuation: W263 bm-a burn/finalize pending, upstream ACTIVE verified; bm-c next turn = W264 seat); dual-delta ORD/DEC both SAME"
st["heartbeat_epoch_utc"] = EPOCH
if cpu_pct is not None:
    st["cpu_pct"] = cpu_pct
if free_ram is not None:
    st["free_ram_gb"] = free_ram
    st["idle_ram_gb"] = free_ram
    st["ram_free_gb"] = free_ram
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
back = json.load(open(sp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int) and back["round_no"] == 1074
assert "T" in back["clock_read"]
print("state updated: round_no=1074 epoch=%d cpu=%s ram=%s" % (EPOCH, cpu_pct, free_ram))

# --- 3) heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = st["current_task"]
hb["verdict"] = st["verdict"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
if cpu_pct is not None:
    hb["cpu_pct"] = cpu_pct
if free_ram is not None:
    hb["free_ram_gb"] = free_ram
    hb["ram_free_gb"] = free_ram
if gpu_free is not None:
    hb["gpu_free_vram_mb"] = gpu_free
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int)
assert "T" in back["clock_read"] and " " not in back["clock_read"]
print("heartbeat updated: epoch int ok, clock T-sep ok")
print("CLOSEOUT-WRITE-OK %s" % NOW)
