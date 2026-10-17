# r1074 bm-c closeout: round report row + state-bm-c.json + heartbeat update (append-only report, programmatic state edit; r583 zero-literal law: watermark keys stay untouched -- d19 guard single-source wrote them with read-back)
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

cpu_pct = free_ram = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / (1024**3), 2)
except Exception:
    pass

# --- 1) round report row (canonical ROOT round_reports-bm-c.md) ---
ROW = (
    NOW + " | r1074 | bm-c | watermark verdict=green (red=false / satengine ALIVE waits-upstream / tickets 0 / jobs 0 / W263=bm-a window burn 12/12 shards LANDED 355c716b7 + sixgate/finalize pending; upstream ACTIVE verified: bm-a listener ALIVE + bm-a local unpushed bigmoney head 46ba27c5fa8f = in-flight window) | "
    "r1074 (waits-upstream clean continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=1 zero-kill (orphan=Doubao pythonw PID 32692 family r1001 precedent legal-user-process, cross-lane not killed per discipline); S0 discard-1-shared-regenerable probe face (watermark_red.json, rewritten by this round S6) + pull --rebase already-up-to-date (origin tip 30b9058d6 = r1073 closeout, behind=0); "
    "(2) S0.5: ORD delta TRUE consumed TWO faces both via d19 guard advance read-back OK -- (a) opening 313c8c0f->f6d580cf = 1 new row (19:2x bm-c r1058 填载收官 receipt, own-lane already-executed by interactive window, zero loop action) + (b) S7-tail probe catch f6d580cf->085559d2 = group commit 720542d 19:31:11 (bm-c r1058-4 own blank-line phantom-pad removal before its receipt row, zero rows, zero action) -- final probe FALSE both faces; DEC delta=NONE (1d4741e4 raw-blob sha256 hold all scans); fleet/orders unacked=0 (98 files all in ack set, probe-verified); inbox=0 (3 MSGs all in processed); "
    "(3) S1 smoke 49/49; satengine ALIVE rc0 (alive_flag fresh, W263 dedup local_done=12 = bm-a burn shards landed via origin pull / remote_done=0 + n1_w263_results.json absent on disk AND origin ls-tree = sixgate/finalize pending on bm-a) -- bm-c waits-upstream, next bm-c turn = W264 seat after W263 finalize; wm red=false healthy (next_pick=claimed moneyflow-IC parked source-blocked standing); boards clear (jobs 0); CEO gaming yield face 17:3x standing per 19:2x ORD row (GPU frozen machine-state pause; loop CPU-only legal bookkeeping lane; '全面开工' resume trigger not present this window); "
    "(4) PRODUCT = S6 43/43 rc0 fresh run (driver Tools/_r1074bmc_s6.py canon-clone r1073, log results/_r1074bmc_s6_log.txt: dualrun ZERO-DRIFT streak 37 @461, compute_audit FLAG pool_starvation/supply_floor honest [pool ready=0 = W263 waits-upstream structural, supply rides bm-a turn, answered-by-chain], py_watermark py_low_board_clear [legal idle whitelist: board clear + bandit 0 + pool 0 + no local batch + bars weekend absent], update_daily no-op cutoff 10-16 fresh [weekend no-op family, papers debt=0], zt crosscheck CLEAN days=7 findings=0 soft=7, market_regime ORANGE 6th day shadow, market_clock CALL-2026-10-16 ORANGE_COOL idempotent, papers idempotent at cutoff 10-16, lane no-ops honest per R31, daily_report REPORT-2026-10-17 faces=5 idempotent, ceo_live_usage LIVE-2026-10-17 ORANGE cap 50%, token delta=0 L2 legs 0 today); "
    "(5) S7: attrition 4 CLEAN (healed notes as-is) + idle --worked rc0 (idle_rounds=0, window has actual work) + loop pin=5 no-op (first fire 19:45) + watchdog registered (S4U flip access-denied = adjudicated default-principal standing face) + claws x2 re-installed LF-normalized + counter 1074->1075 + heartbeat epoch int + clock_read T-sep self-asserted | "
    "verify: smoke 49/49 + S6 log 43x rc=0 + ORD dual-delta consumed with pinned-probe FALSE at close (ord 085559d2 / dec 1d4741e4) + attrition CLEAN + W263 finalize absent on origin (ls-tree + satengine dedup 12/0) + upstream liveness (bm-a :8790 ALIVE + unpushed local head 46ba27c5fa8f) | behind-origin=0 (closeout push rides this window) | "
    "next r1075: (1) 5x DUTY = HANDOVER check (window r1016-r1074); (2) watch bm-a W263 chain (sixgate->finalize) -> on finalize bm-c W264 SEAT (live re-derive post-W263 universe per W263 seat MSG forward face: staircase continues, naive W264 A 595_901..597_900 pre-disclosed REFUSED at registered W263 B 595_901..596_100, first-clean moves past 596_100; own-A reservation cascade governs B; never transcribe r587); (3) Monday 10-19 15:30 bars window: papers chain fires on the new bar (debt=0 verified cutoff 10-16); (4) short-video lane DISABLED standing per O-20261017-1741; (5) GPU lane = gen-only, CEO gaming yield window standing (loop CPU-only)\n"
)
rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "r", encoding="utf-8") as f:
    txt = f.read()
assert " | r1074 | " not in txt, "r1074 row already present"
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
with open(rp, "r", encoding="utf-8") as f:
    assert " | r1074 | " in f.read()
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
st["last_round"] = "r1074"
st["round_no"] = 1075
st["round_no_label"] = "r1074 closeout -> counter 1075"
st["current_task"] = "r1074 closeout: waits-upstream (W263 bm-a sixgate/finalize pending, upstream ACTIVE verified; burn 12/12 landed) + next=W264 seat on finalize"
st["current_task_at"] = NOW
st["last_action"] = "r1074 closeout (waits-upstream clean continuation: ORD dual-delta consumed 2 faces + S6 43/43 + upstream liveness verified + quad green; counter 1074->1075)"
st["last_round_summary"] = "r1074: clean continuation waits-upstream (W263 bm-a sixgate/finalize pending, burn 12/12 landed; upstream ACTIVE: listener ALIVE + unpushed head; bm-c next=W264 seat) + S0.5 ORD delta consumed 2 faces (receipt row + own blank-line cleanup) + S6 43/43 fresh (dualrun streak 37) + smoke 49/49 + attrition 4 CLEAN + idle worked + quartet green"
did = ("r1074: clean continuation waits-upstream window (W263 = bm-a window: splice LANDED f499817fa + burn 12/12 shards LANDED 355c716b7, sixgate/finalize pending -- satengine dedup local_done=12/remote_done=0 + n1_w263_results.json absent on disk AND origin ls-tree verified; upstream ACTIVE verified: bm-a listener :8790 ALIVE + bm-a local unpushed bigmoney head 46ba27c5fa8f = in-flight window; engine chain carried on bm-a, not bm-c's to fix) + bm-c next turn = W264 seat on W263 finalize + S0.5 ORD delta TRUE consumed two faces both via d19 guard advance read-back OK (opening 313c8c0f->f6d580cf = 19:2x bm-c r1058 receipt row own-lane zero loop action; S7-tail f6d580cf->085559d2 = group commit 720542d bm-c r1058-4 own blank-line phantom-pad removal zero rows) + DEC 1d4741e4 FALSE hold all scans + orders unacked=0 + inbox=0 + smoke 49/49 + satengine ALIVE rc0 + S6 43/43 fresh (dualrun ZERO-DRIFT streak 37 @461, audit FLAG pool_starvation/supply_floor = waits-upstream structural answered-by-chain, py_wm py_low_board_clear = legal idle whitelist face, daily_report REPORT-2026-10-17 faces=5, ceo_live_usage LIVE-2026-10-17 ORANGE cap 50%, token delta=0) + attrition 4 CLEAN + idle --worked rc0 + quartet green (loop pin=5 no-op + watchdog registered [S4U flip access-denied adjudicated standing] + claws x2) + orphan face=1 zero-kill (Doubao pythonw PID 32692 r1001 precedent family legal-user-process) + CEO gaming yield face 17:3x standing (GPU frozen, loop CPU-only legal)")
st["did"] = did
st["verdict"] = "green: r1074 = clean continuation waits-upstream window (W263 bm-a sixgate/finalize pending, burn 12/12 landed; upstream ACTIVE verified via bm-a listener ALIVE + unpushed local head 46ba27c5fa8f; bm-c next=W264 seat on finalize) + S0.5 ORD delta consumed 2 faces (313c8c0f->f6d580cf->085559d2, both own-machine faces zero loop action, d19 guard single-source) + DEC 1d4741e4 FALSE hold + unacked=0 + smoke 49/49 + satengine ALIVE rc0 + S6 43/43 rc0 (dualrun streak 37, audit FLAG structural answered-by-chain, py_wm py_low_board_clear = legal idle whitelist [board clear + bandit 0 + pool 0 + bars weekend absent]) + attrition 4 CLEAN + idle --worked rc0 + quartet green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated default-principal standing face] + claws x2 LF-normalized) + orphan face=1 zero-kill (legal-user-process precedent) + CEO gaming yield standing (loop CPU-only legal)"
nxt = ("r1075: (1) 5x DUTY = HANDOVER check (window r1016-r1074, per every-5-rounds law); (2) watch bm-a W263 chain (sixgate->finalize); on W263 FINALIZE landing = bm-c W264 SEAT publish (probe live re-derive on post-W263 universe per W263 seat MSG forward face: staircase continues -- naive W264 A 595_901..597_900 pre-disclosed to be REFUSED at registered W263 B 595_901..596_100, first-clean moves past 596_100; own-A reservation cascade governs B; never transcribe r587); (3) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars, debt=0 verified cutoff 10-16); (4) short-video lane DISABLED standing per O-20261017-1741 (4/4 disabled + 6688 FREE); (5) GPU lane = gen-only (CEO gaming yield window standing per 19:2x ORD row: GPU frozen, loop CPU-only; on CEO '全面开工' machine-state resume face fires)")
st["next"] = nxt
st["next_pointer"] = nxt
st["note"] = ("r1074: clean continuation waits-upstream window (state round_no=1074 at open, executed r1074, advanced 1074->1075 so next=r1075); zero absorb owed (r1073 closeout 30b9058d6 landed clean, zero dead window between); zero double-count: S0.5 ORD delta consumed THIS window in two faces (opening pinned-probe advanced 313c8c0f->f6d580cf = 1 row 19:2x bm-c r1058 receipt own-lane zero loop action; S7-tail probe caught group commit 720542d 19:31:11 = bm-c r1058-4 own blank-line phantom-pad removal, advanced f6d580cf->085559d2 zero rows zero action; final probe FALSE both faces); W263 = bm-a window (burn 12/12 shards LANDED 355c716b7 mid-r1073, sixgate/finalize pending -- n1_w263_results.json absent on disk AND origin ls-tree verified; bm-a heartbeat 17:50 stale = its r1038+ window in flight BUT upstream ACTIVE verified: listener :8790 ALIVE + bm-a local unpushed bigmoney head 46ba27c5fa8f; engine chain carried on bm-a, not bm-c's to fix); idle face: window has actual work (S6 43 legs + quad + closeout) -> --worked rc0 declared; orphan face=1 (probe py_faces=5, orphan=Doubao pythonw PID 32692 r1001 precedent family legal-user-process cross-lane, zero-kill); CEO gaming yield face 17:3x standing per 19:2x ORD row (GPU frozen machine-state pause, loop CPU-only legal bookkeeping lane, '全面开工' resume trigger not present this window)")
st["verify"] = "S6 log 43x rc=0 re-read + d19 pinned-probe dual FALSE at close (ord 085559d2 / dec 1d4741e4) + smoke 49/49 + satengine alive rc0 + attrition 4 CLEAN + loop pin=5 no-op + watchdog registered + claws x2 installed + idle worked rc0 + epoch int readback + report line +1 asserted + W263 finalize absent verified (ls-tree + satengine dedup 12/0) + upstream liveness (bm-a listener + unpushed head) + closeout commit rides this window"
st["latest_artifact"] = "results/_r1074bmc_s6_log.txt (43-leg S6 chain rc0) + Tools/_r1074bmc_s6.py (driver canon-clone r1073)"
st["next_milestone"] = "W263 finalize (bm-a window, upstream ACTIVE verified) -> bm-c W264 seat (chain-order); Monday 10-19 15:30 bars papers chain (24-48h window)"
st["head_sha"] = "r1074 closeout (waits-upstream clean continuation: W263 bm-a sixgate/finalize pending, upstream ACTIVE verified; bm-c next turn = W264 seat); ORD dual-delta consumed 2 faces"
st["heartbeat_epoch_utc"] = EPOCH
st["orders_ack_receipt"] = "r1074: zero new repo order files (unacked=0 both scans, 98 order files all in ack set); group-tree ORD delta consumed 2 faces this window (19:2x bm-c r1058 receipt row own-lane + 720542d own blank-line pad removal, both zero loop action); DEC 1d4741e4 FALSE hold; inbox=0 (3 MSGs all processed)"
st["last_orders_sha_note"] = "r1074: ORD 313c8c0f->f6d580cf (1 row = 19:2x bm-c r1058 receipt own-lane) ->085559d2 (720542d own blank-line removal) both consumed via d19 guard advance read-back OK (content-sha1 pinned method r977)"
st["last_orders_read_note"] = "r1074: ORD delta FALSE hold at close (content-sha1 085559d2 pinned-probe, zero rows owed)"
st["last_decisions_read_note"] = "r1074: DEC delta FALSE hold (raw-blob sha256 1d4741e4 pinned-probe, zero rows owed)"
if cpu_pct is not None:
    st["cpu_pct"] = cpu_pct
if free_ram is not None:
    st["free_ram_gb"] = free_ram
    st["idle_ram_gb"] = free_ram
    st["ram_free_gb"] = free_ram
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
back = json.load(open(sp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int) and back["round_no"] == 1075
assert "T" in back["clock_read"]
assert back["last_orders_sha"] == "085559d2dd0faf55c881a81a3c2849bc48dafe63"
assert back["last_decisions_sha"] == "1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1"
print("state updated: round_no=1075 epoch=%d cpu=%s ram=%s" % (EPOCH, cpu_pct, free_ram))

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
hb["did"] = did
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
if cpu_pct is not None:
    hb["cpu_pct"] = cpu_pct
if free_ram is not None:
    hb["free_ram_gb"] = free_ram
    hb["ram_free_gb"] = free_ram
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int)
assert "T" in back["clock_read"] and " " not in back["clock_read"]
print("heartbeat updated: epoch int ok, clock T-sep ok")
print("CLOSEOUT-WRITE-OK %s" % NOW)
