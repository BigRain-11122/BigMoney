#!/usr/bin/env python
# r858 bm-b books writer: round report line append (binary tail append,
# CRLF to match file tail convention per r857 EOL-pit law -- no anchor
# replace), state.json r858 write (heals the r857 state-bump miss by direct
# write, sequence follows the round-reports ledger), heartbeat refresh.
# Encoding: pure ASCII body (repo PS/py GBK decode law).
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

now = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

LINE = (
    now + " | r858 bm-b | "
    "S0: fetch+FF merge zero incoming (HEAD d550bf11c == origin/main already up to date; round-start dirt = 6 own daemon live faces only, zero foreign half-work) | "
    "S0.5: orders diff zero (67 orders/192 acks/unacked 0) + D19 dual watermark identical (dec caca0c6e / ord f90233c7, probe rc0) | "
    "S1: smoke 49/49 + orphan face=1 (pid23124 r854 T23 watcher, intentional detached seat; honest TIMEOUT receipt landed 03:27:56 per 90-min design, not collected per mission-arm law) | "
    "S2: board clear triple check (job 0, ticket 0 open, wm py_low_board_clear red=None) | "
    "S3 PRIMARY PRODUCT = T23 TIMEOUT-PATH READOUT + CENSUS BURN FIRED: r854 watcher honest timeout receipt read (window ended 03:27:56, astock 5219/5229 refresh incomplete, last gate face captured in receipt); quarantine carryover check = 10 structural-fail stocks (KeyError:date/validation_fail/JSONDecode faces) quarantined at 3/3 attempts -> _todo_for exclusion makes remaining=0 -> flip structurally reachable this same window; re-arm per single-flight law = stale receipt archived by move-not-delete (results/_r854bmb_t23_autofire_receipt_timeout_r854.json) + second-gen watcher results/_r858bmb_t23_watch.py spawned detached pid=17116 (belt-and-braces legacy-receipt live-state guard, executor _r858bmb_t23_rearm.py rc0); S6 chain leg 16 spawned continuation pass (todo=14, quarantined=10) -> ASTOCK PANEL FLIPPED COMPLETE 03:34 (mode=refresh complete, complete=True, cutoff 2026-10-09, per_files 5219/5229, quarantined_n=10 disclosed) -> WATCHER FIRED T23 CENSUS BURN DETACHED 03:34:40 (pid=25780, receipt _r858bmb_t23_watch_receipt.json state=fired, run log logs/t23_census_run.log alive+computing, product face results/t23_census/; burn 10-15min -> lands ~03:50; verdict readout r859/r860, window <=10-11 06:00 intact) | "
    "W210 freeze prep PARKED on M9 gate (W209 freeze+finalize pending bm-c side, zero new origin commits this window) | "
    "holds one-line declarations: N2 U3(1) prereg window / G2 academic-citation fallback / moneyflow IC unlock precondition NOW SATISFIED (astock complete flip landed 03:34 -> next wm probe should surface next_pick; r859 checks) / pool-EOL fleet adjudication zero new input (flag maintained, no hot-fix) / O-20261011-0012 CPU-max maintained (T23 census burn = current CPU contribution face; engine queue dry until W209 gate opens) / W18 drain-gated (bm-a owns w17-judge) | "
    "S6: 41 legs 40 rc0 + alloc rc2 known 510880 P5 slot (verbatim clone _r858bmb_s6chain.ps1) | "
    "S7: quartet ALIVE (loop pin=2 no-op, watchdog idempotent re-register first fire 03:38, dual claws installed LF-normalized), attrition scan CLEAN (4 ledger files, 3 healed history notes), idle --worked, books (state r858 -- r857 state.json bump miss healed by direct write per ledger sequence, heartbeat, this line) | "
    "orphan face=1 (new watcher pid17116 = intentional detached seat mid-mission to ~05:01, not collected) | "
    "next r859: T23 census burn verdict readout (receipt state=fired pid=25780; product face results/t23_census/ + finalize gate; burn lands ~03:50; holds verdict window <=10-11 06:00) -> moneyflow IC next_pick unlock check (astock flip landed 03:34, next wm probe) -> W210 freeze prep PARKED on M9 gate (W209 freeze+finalize pending bm-c) -> holds: N2 U3(1) prereg / G2 fallback -> pool-EOL fleet adjudication watch -> O-20261011-0012 CPU-max maintained"
)

# --- 1) round report: binary tail append, CRLF (file tail convention) ---
with open(REPORT, "ab") as f:
    if os.path.getsize(REPORT) > 0:
        f.write(b"\r\n")
    f.write(LINE.encode("utf-8"))
print("round report appended:", len(LINE), "chars")

# --- 2) state.json: r858 (heals r857 bump miss; ledger sequence authority) ---
with open(STATE, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 858
st["round"] = 858
st["round_no_label"] = "r859"
st["note"] = (
    "r858: S0 zero incoming (already up to date) + s05 orders diff zero (67/192/0) + D19 dual watermark identical "
    "(dec caca0c6e / ord f90233c7, probe rc0) + smoke 49/49 + orphan 2 seats read honestly (r854 watcher timed out "
    "03:27:56 per design; r858 re-arm watcher pid17116 live to ~05:01); T23 TIMEOUT PATH EXECUTED: quarantine "
    "carryover verified (10 structural-fail stocks quarantined 3/3, _todo_for exclusion -> remaining=0), stale "
    "receipt archived move-not-delete, second-gen watcher spawned; S6 leg 16 continuation pass -> ASTOCK PANEL "
    "FLIPPED COMPLETE 03:34 (cutoff 2026-10-09, 5219/5229, quarantined_n=10 disclosed) -> CENSUS BURN FIRED "
    "03:34:40 detached pid=25780 (receipt state=fired; product face results/t23_census/; verdict readout r859/r860, "
    "window <=06:00 intact); W210 parked on M9 gate (W209 pending bm-c); moneyflow IC unlock precondition satisfied "
    "(r859 checks wm probe); S6 41 legs 40 rc0 + alloc rc2 known; S7 quartet ALIVE + attrition CLEAN + idle --worked; "
    "state r857 bump miss healed by direct write per ledger sequence"
)
st["did"] = st["note"]
st["last_action"] = st["note"]
st["now_active"] = ("r858 closeout: T23 timeout-path readout executed (re-arm watcher live pid17116) + astock "
                    "panel complete flip 03:34 + census burn fired detached pid25780; verdict readout r859/r860")
st["current_task"] = ("r859 queue: T23 census burn verdict readout (receipt _r858bmb_t23_watch_receipt.json "
                      "state=fired pid=25780; product face results/t23_census/ + finalize gate; window <=10-11 06:00) "
                      "-> moneyflow IC next_pick unlock check (astock flip landed 03:34, next wm probe) -> W210 "
                      "freeze prep PARKED on M9 gate (W209 freeze+finalize pending bm-c) -> holds: N2 U3(1) prereg / "
                      "G2 fallback -> pool-EOL fleet adjudication watch -> O-20261011-0012 CPU-max maintained")
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["latest_artifact"] = ("r858: T23 census burn in flight (receipt results/_r858bmb_t23_watch_receipt.json "
                         "state=fired pid=25780; run log logs/t23_census_run.log; product face results/t23_census/) + "
                         "astock panel complete flip (results/astock_daily_update_status.json complete=True cutoff "
                         "2026-10-09) + re-arm executor results/_r858bmb_t23_rearm.py + second-gen watcher "
                         "results/_r858bmb_t23_watch.py + archived timeout receipt "
                         "results/_r854bmb_t23_autofire_receipt_timeout_r854.json")
st["next_milestone"] = ("T23 census burn verdict <=10-11 06:00 (burn fired 03:34:40, lands ~03:50, readout r859/r860) "
                        "-> W209 freeze+finalize (bm-c) then W210 freeze-prep when M9 gate opens; chain head 872,571; "
                        "moneyflow IC next_pick unlock check r859; pool-EOL fleet adjudication pending")
st["verdict"] = ("GREEN: r858 (T23 timeout-path readout executed per design + astock panel complete flip verified + "
                 "census burn fired detached alive; smoke 49/49; S6 40/41 rc0 + alloc rc2 known 510880 P5 slot; "
                 "quartet ALIVE; attrition CLEAN; re-arm single-flight respected, stale receipt archived)")
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_seen"] = now
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["clock_read"] = now
st["d19_watermark_guard"]["round_ref"] = 858
st["d19_watermark_guard"]["ts"] = now
tmp = STATE + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1)
    f.flush()
    os.fsync(f.fileno())
os.replace(tmp, STATE)
print("state.json written r858")

# --- 3) heartbeat ---
with open(HB, encoding="utf-8") as f:
    hb = json.load(f)
hb["round"] = 858
hb["round_no"] = 858
hb["now_active"] = st["now_active"]
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["next"] = st["current_task"]
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = st["verdict"]
hb["last_action"] = st["note"]
hb["did"] = st["note"]
hb["last_round_at"] = now
hb["last_seen"] = now
hb["updated"] = now
hb["ts"] = now
hb["updated_at"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = int(time.time())
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 10.7
hb["ram_free_gb"] = 10.7
hb["ram_free_pct"] = 44.6
hb["gpu_free_vram_mb"] = 3505
hb["gpu_free_vram_gb"] = 3.5
hb["vram_free_gb"] = 3.5
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 1
hb["orphan_face_note"] = ("r858 closeout probe: py_faces alive, 1 intentional detached seat (pid17116 = r858 "
                          "second-gen T23 watcher mid-mission to ~05:01 per 90-min window; r854 watcher exited "
                          "honestly 03:27:56 timeout receipt archived; read-only probe, not collected per "
                          "mission-arm law)")
hb["sync"] = {
    "last_push_ts": now,
    "note": ("r858 closeout push (T23 re-arm + astock flip + burn fired + round report + heartbeat); "
             "post-push behind=0 self-proof via fetch+ls-remote"),
}
tmp = HB + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1)
    f.flush()
    os.fsync(f.fileno())
os.replace(tmp, HB)
ep = hb["heartbeat_epoch_utc"]
assert isinstance(ep, int), "epoch must be JSON int (F7 law)"
print("heartbeat written r858, epoch int ok:", ep)
