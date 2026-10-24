# -*- coding: utf-8 -*-
"""r1206 closeout: state-bm-c.json counter + closeout note + heartbeat + round report row."""
import datetime
import hashlib
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
REP = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")

NOW = datetime.datetime.now().astimezone()
ISO = NOW.replace(microsecond=0).isoformat()
EPOCH = int(NOW.timestamp())


def s16(p):
    return hashlib.sha256(io.open(os.path.join(REPO, p), "rb").read()).hexdigest()[:16]


prereg_sha = s16("research/PERPETUAL_N1_W313_PREREG.md")
prereg_bytes = os.path.getsize(os.path.join(REPO, "research/PERPETUAL_N1_W313_PREREG.md"))
sg = json.load(io.open(os.path.join(REPO, "results/_r1206bmc_w313_sixgate.json"), encoding="utf-8"))
fk = json.load(io.open(os.path.join(REPO, "results/_r1206bmc_w313_fivekeys.json"), encoding="utf-8"))
d = json.load(io.open(os.path.join(REPO, "results/perpetual_faces/n1_w313_results.json"), encoding="utf-8"))
adj = json.load(io.open(os.path.join(REPO, "results/_n1_face_adjudication_w313.json"), encoding="utf-8"))
p = d["null_pool_cumulative"]
s = d["skill_line_v2_k_lift"]
led = d["science_gates"]["ledger"]
A = d["families"]["A_random_engine_exit"]

state = json.load(io.open(ST, encoding="utf-8"))
assert state.get("round_no") == 1205, "round_no drift: %r" % state.get("round_no")
state["round_no"] = 1206

note = (
 "r1206: W313 CYCLE CLOSED (state round_no=1205 at open, executed r1206, advanced 1205->1206 so "
 "next=r1207); zero double-count: D-19 decisions watermark migrated to the D-20261024-03 TRIPLE form "
 "and consumed (dec 3cfdec0c -> 3143a3ce2b711a47@f77f95b/209648 = D-20261020-08~12 + D-20261024-01~15 "
 "board rows; orders 8ff7de47 UNCHANGED 109 files / 234 acks / unacked=0); S0 fetch 0 behind / 0 ahead; "
 "S1 smoke 57/57; PRODUCT = W313 FINALIZE: (1) freeze-face adjudication PASS via "
 "Tools/n1_freeze_face_adjudicate.py (1 heal delta 'freeze-time commit n/a -> c110bf216e', 0 unexplained); "
 "(2) six-gate 76th consecutive ALL PASS (results/_r1206bmc_w313_sixgate.json: splice integrity / "
 "CR-normalized worktree==landed / setwave birth-station 313:1 312:0 305:0 / banned ADMIT rc0 / pf 9/9 + "
 "n1 selftest rc0 / shards 12/12 >100KB / seed admit FREE x2); (3) finalize one-pass EXACT ledger "
 f"{led['prev_total']:,}+{led['batch_trials']:,}={led['total']:,} / merged K 684,320+2,200={p['merged']['n_values']:,} "
 f"(w313-only mu {p['w313_only']['mu']:.8f}/sigma {p['w313_only']['sigma']:.8f}; merged mu "
 f"{p['merged']['mu']:.8f}/sigma {p['merged']['sigma']:.8f}; se_mu@686,520 {p['se_mu_at_k686520']:.6f}; "
 f"A p95 {A['full_sharpe_p95']} / p99 {A['full_sharpe_p99']}); (4) fivekeys 6/6 ALL PASS "
 f"(results/_r1206bmc_w313_fivekeys.json, {len(fk['prereg_prose_deviations'])} prose deviation disclosed: "
 "sec.5 key4 anchor +0.0001 is the W312 face vs W313 actual +0.0000); (5) prereg sec.7/sec.8 backfilled "
 f"zero-placeholder ({prereg_bytes:,}B, sha16 {prereg_sha}); adjudication verdict {adj['verdict']}. "
 "D-20261024-03 EXECUTED in code: Tools/d19_check.py now compares/writes the triple watermark "
 "'<sha16>@<commit7>/<bytes>' (commit+length first, then hash; legacy bare-sha accepted and upgraded; "
 "orders watermark refreshed on the same path) -- reproducing command printed on change. S6 chain 39/39 rc0 "
 "in 253.6s (dualrun ZERO-DRIFT 616 entries streak 51 / compute_audit rc0 FLAG supply_gap + supply_floor "
 "ready_ignitable 0<floor 3 with 3 bm-b-owned silent 2554min, corroboration required -> D-20261024-15 lane "
 "takeover NOT executed this round, first-lane deadline 10-25 12:00) / py_watermark loaded_ok / update_daily "
 "cutoff 2026-10-23 zero new rows / regime ORANGE breadth 0.85 / clock CALL-2026-10-23 ORANGE_HOT / "
 "bm-b-owned lanes honest no-op / scorecard 6/28/7 / daily_report REPORT-2026-10-24 / live_usage "
 "LIVE-2026-10-24 ORANGE / dashboard refreshed / token delta 0); live.paper skipped (update_daily 0 new bars); "
 "S7 attrition 4 ledger files CLEAN (3 historical shrinks healed) / orphan face=0 (py_faces=6, "
 "resident_servers=1, zero kill) / scheduled tasks NOT re-registered per the 2026-10-17 CEO cleanup order. "
 "current=W313 CLOSED, chain head free; next=r1207 W314 SEAT PROBE (live re-derive on the post-W313 "
 "REGISTERED 303-owner universe; naive W314 A 705_901..707_900 is EXPECTED to be refused by registered "
 "W313 B 705_901..706_100)"
)
state["round_t1206_closeout_note"] = note
state["current"] = ("r1206 CLOSED: W313 cycle closed (adjudication PASS / six-gate 76th ALL PASS / "
                    "finalize 1,112,941 + K=686,520 / fivekeys 6/6 / sec.7-8 backfilled); "
                    "D-20261024-03 triple D-19 watermark adopted in Tools/d19_check.py; next = W314 seat probe")
state["activity_now"] = ("idle at chain head: W313 registered + finalized; "
                         "next = r1207 W314 seat probe (live re-derive)")
state["current_task"] = state["activity_now"]
state["current_task_at"] = ISO
state["current_task_ts"] = ISO
state["clock_read"] = ISO
state["health"] = "green"
state["verdict"] = ("green r1206: W313 CYCLE CLOSED (six-gate 76th ALL PASS, finalize 1,112,941 / "
                    "K=686,520, fivekeys 6/6, adjudication PASS); D-03 triple watermark adopted; "
                    "S6 39/39 rc0; smoke 57/57; attrition CLEAN; orphan 0")
state["verify"] = ("smoke 57/57 | six-gate ALL PASS | fivekeys 6/6 | ledger exact 1,112,941 | "
                   "K exact 686,520 | S6 39/39 rc0 | attrition CLEAN | orphan 0 | unacked 0")
json.dump(state, io.open(ST, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

hb = json.load(io.open(HB, encoding="utf-8"))
hb["last_seen"] = ISO
hb["ts"] = ISO
hb["clock_read"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = ("W313 cycle closed (finalize 1,112,941 / K=686,520, six-gate 76th ALL PASS, "
                      "fivekeys 6/6); chain head free, next = W314 seat probe")
hb["verdict"] = "green r1206: W313 CLOSED; D-03 triple watermark live; smoke 57/57; S6 39/39 rc0"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
json.dump(hb, io.open(HB, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(json.load(io.open(HB, encoding="utf-8"))["heartbeat_epoch_utc"], int)

row = (
 f"{ISO} | r1206 | r1206: W313 CYCLE CLOSED (state round_no=1205 at open, executed r1206, advanced "
 f"1205->1206 so next=r1207). PRODUCT = W313 FINALIZE end-to-end: adjudication PASS (1 heal delta, "
 f"0 unexplained) -> six-gate 76th consecutive ALL PASS (results/_r1206bmc_w313_sixgate.json) -> finalize "
 f"one-pass EXACT ledger {led['prev_total']:,}+{led['batch_trials']:,}={led['total']:,} / merged K "
 f"684,320+2,200={p['merged']['n_values']:,} (w313-only mu {p['w313_only']['mu']:.8f} sigma "
 f"{p['w313_only']['sigma']:.8f}; merged mu {p['merged']['mu']:.8f} sigma {p['merged']['sigma']:.8f}; "
 f"se_mu@686,520 {p['se_mu_at_k686520']:.6f}; A p95 {A['full_sharpe_p95']} / p99 {A['full_sharpe_p99']}) -> "
 f"fivekeys 6/6 ALL PASS with {len(fk['prereg_prose_deviations'])} disclosed prose deviation (sec.5 key4 "
 f"anchor is the W312 face) -> sec.7/sec.8 backfilled zero-placeholder ({prereg_bytes:,}B, sha16 "
 f"{prereg_sha}). (2) D-20261024-03 EXECUTED: Tools/d19_check.py now reads/writes the triple watermark "
 f"'<sha16>@<commit7>/<bytes>' (commit+length first then hash; legacy bare sha auto-upgraded; orders "
 f"watermark refreshed in the same pass) -- state now dec 3143a3ce2b711a47@f77f95b/209648 / ord "
 f"8ff7de47df154ffa@f77f95b/370071, MATCH idempotent on re-run. (3) decision D-20261024-15 lane takeover "
 f"NOT executed: compute_audit shows ready_ignitable 0 < floor 3 with the 3 ready units owned by bm-b "
 f"(silent 2554min, corroboration required, RAM 7.4% free) -> honest deferral, first-lane deadline "
 f"10-25 12:00 disclosed. S1 smoke 57/57; S3 satengine ALIVE rc0 queue_next=[]; S6 chain 39/39 rc0 in "
 f"253.6s (dualrun ZERO-DRIFT streak 51 / py_watermark loaded_ok / update_daily cutoff 2026-10-23 zero new "
 f"rows / regime ORANGE breadth 0.85 / clock CALL-2026-10-23 ORANGE_HOT / scorecard 6/28/7 / "
 f"daily_report REPORT-2026-10-24 / live_usage LIVE-2026-10-24 ORANGE / dashboard refreshed / token delta 0); "
 f"live.paper skipped (0 new bars); S7 attrition 4 ledger files CLEAN (3 historical shrinks healed) / "
 f"orphan face=0 (py_faces=6, resident_servers=1, zero kill) / scheduled tasks not re-registered per the "
 f"2026-10-17 CEO cleanup order. CEO face: 当前活=W313 已收口（finalize 账本 1,112,941 / K=686,520）；"
 f"最近实物=research/PERPETUAL_N1_W313_PREREG.md §7/§8 回填 + results/_r1206bmc_w313_sixgate.json "
 f"{ISO[:16]}；下个里程碑=W314 席位探针+pre-reg 冻结+五面 splice（≤48h）。 | watermark verdict: GREEN "
 f"(dualrun ZERO-DRIFT streak 51, board inflight 0, pool ready 3 all foreign-owned) | local-not-on-origin "
 f"commits=0 | registry zero-hit (no sweep action) | dept:研究/策略"
)
with io.open(REP, "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")
print("state round_no=1206 ; heartbeat", ISO, EPOCH)
print("report row appended", len(row), "chars")