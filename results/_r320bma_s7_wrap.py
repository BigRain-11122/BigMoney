"""r320 bm-a S7 wrap: state round_no 319->320 + heartbeat refresh + round-report append."""
import io
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# --- state file
sp = ROOT / "state-bm-a.json"
st = json.loads(sp.read_text(encoding="utf-8-sig"))
st["round_no"] = 320
st["did"] = ("R320: 5x HANDOVER check (R316-320 window entry) + repull probe #4 (1450/5228 @12:10 "
             "pace 21.9/min zero-fail ETA ~15:02) + P0 post_review T-90-V1 criteria path typo fixed "
             "(re-derive YES=44 NO=0) + S6 32/32 rc=0 + smoke 25/25")
st["verdict"] = ("py_low_with_work_cands legal-occupied: sina_mf A1 deep repull in flight (1450/5228 @12:10, "
                 "pace 21.9/min, ETA ~15:02, zero-fail); board 0 open; pool ready=1 (bm-c lane); audit CLEAN")
st["next"] = ("R321: repull terminal verdict window ~15:0x (mechanical three-piece: update_sina_mf exit-code law "
              "+ sina_mf_accept sec-4 gates + N=250 depth census -> complete = bm-b sina-construct prereg open-gate); "
              "Monday 09-28 09:15 T-91 s3 auto-fire full chain; 10-01 month trio standing; next 5x HANDOVER = R325")
st["ts"] = NOW
st["last_round_ts"] = NOW
st["updated_at"] = NOW
st["last_run"] = NOW
st["last_round_at"] = NOW
st["last_round"] = 319
st["updated"] = NOW
st["last_seen"] = NOW
st["current_task"] = ("R320 done: HANDOVER 5x + T-90 criteria path fix (reviewer YES=44 NO=0) + probe #4 1450/5228; "
                      "R321: repull terminal verdict ~15:0x")
st["task"] = st["current_task"]
sp.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# --- heartbeat
hp = ROOT / "fleet" / "machines" / "bm-a.json"
hb = json.loads(hp.read_text(encoding="utf-8-sig"))
hb["last_seen"] = NOW
hb["current_task"] = st["current_task"]
hb["cpu_pct"] = 8.1
hb["free_ram_gb"] = 46.9
hb["gpu_free_vram_gb"] = 5.4
hb["verdict"] = st["verdict"]
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 320
hb["task"] = st["current_task"]
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
hp.write_text(json.dumps(hb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# --- round report line
rp = ROOT / "logs" / "iteration-loop" / "round_reports-bm-a.md"
line = (
    "2026-09-27T12:1x:xx+08:00 | R320 bm-a (dept:工程+舰队+治理) | WM first-line verdict: red=false lane healthy; "
    "probe 12:10 py_low_with_work_cands LEGAL-occupied face: sina_mf A1 deep repull in flight (probe #4 1450/5228 "
    "@12:10:16 pace 21.9/min attempts_fail=0 lock-alive ETA ~15:02 stable vs R319 estimate; board 0 open tickets 0 "
    "bandit 0; pool ready=1 = bm-c T19-PHANTOM-P1 lane not ours; audit v2.3 CLEAN flags[] load_state pool-supply-gap "
    "non-flag) | did: (A) S0 pull FF 2ede96da->e21bc4f6 (bm-c r79 T19-PHANTOM pool v11) + S0.5 round-start set-diff "
    "96/96 orders zero unacked + decisions.md zero new D-rows (12:08 mtime write=BigStream order-row status flip "
    "non-our-face; D-20260927-04 self-correct-maintain + D-05 items standing incl 03 commit-pre conflict-marker "
    "check re-executed clean this round) + smoke 25/25 (B) board watch 0 open (31 claimed + 3 BOM-file tickets "
    "utf-8-sig verified all done) job_list empty watermark next_pick=claimed (moneyflow IC event-attention lane) "
    "zero claimable -> R320 5x HANDOVER check delivered (header 对账增量 R316-320 窗: T-93 转移收线收编+sina_mf "
    "深史重拉看护连营+双推撞车典解+S6 32 腿稳态) (C) repull watch-face probe #4 landed "
    "results/_r320bma_sina_repull_probe.json (1450/5228=27.7% zero-fail pace 21.9/min ETA ~15:02 progress-file "
    "age 2.7s=live-advancing) terminal verdict window unchanged ~15:0x mechanical three-piece standing "
    "(D) **P0 post_review: T-90-V1-E2E-FINALIZE open NO (json_field key 'ring_table' absent) caught by fresh "
    "reviewer derive** -> root-caused = bm-b r319 (5e667f10) registration-side path typo: check path wrote "
    "'verdict.ring_table.base...' but LANDED product results/decision_chain_e2e.json keeps ring_table at TOP "
    "level parallel to verdict (their own r319 D4 wiring claim 'consuming verdict/ring_table/seat_vacancy/"
    "trials_ledger' + monthly_briefing sec-6 consumer selftest 19/19 both attest); frozen value -0.0528 verified "
    "EQUAL both sides pre-edit + BAD path structurally absent in product (KeyError proof) -> criteria path "
    "reconciliation per r223 bm-a cross-lane precedent + r270 bm-b re-anchor precedent: "
    "results/_r320bma_t90_criteria_path_fix.py (idempotent, re-run NO-OP; pre-edit fact self-assert; science "
    "values zero-change; product untouched; ledger verdict reviewer-derived never hand-flipped per O-2115) + "
    "_reconciled trace row appended -> re-derive ALL GREEN: **YES=44 NO=0 WAIT=5, T-90-V1 YES 10/10 checks** "
    "(ledger 12:13:49 row) + MSG-20260927-1215 sent to bm-b (no-double-write + no-action notice) "
    "(E) S6 chain 32/32 rc=0 (_r320bma_s6_chain.ps1 = r319 lineage Copy-Item header-only delta per r298 law; "
    "Sunday no-new-bar posture cutoff 09-24: audit CLEAN py 1.2% / wm legal-occupied / daily 0-new / regime "
    "ORANGE shadow breadth 0.77 / scorecard 6-28-7 / clock CALL-09-24 idempotent / lhb 30min-guard / heat weekend / "
    "fut+opt cutoff-covered zero-network / mf rank-throttle 19.8min / smf lock-alive no-op repull-in-flight / "
    "astock+sigexp+alloc+fundprem lane-guards honest no-op / ths same-day idempotent / ah spawn-throttle 19min "
    "panel-incomplete self-heal next window / fundamental 14.5h fresh / b-layer all-pass / live.paper OK / t35v "
    "PASS 6 zero-pending / t24 22-22 drift0 / promo 0-22 honest / aggr+grid+sysv1 idempotent no-op sysv1 ARMED "
    "Monday / t35 export 09-24 idempotent / daily_scorecard 6 traders / daily_report faces=4 token=1 / "
    "build_status 10factors 432combos / token L2 1 leg ~6450 tok local) | VERIFIED: smoke 25/25 round-start; "
    "S6 32x rc=0 chain stdout; probe artifact parse-verified; post_review re-derive YES=44 NO=0; schtasks alive "
    "per R49 schtasks-not-CIM law (IterationLoop Running next 12:18 + Watchdog Ready next 12:20); heartbeat "
    "epoch int self-assert PASS + clock ISO T-separated; state 319->320 | NEXT: (1) R321+ repull terminal "
    "verdict window ~15:0x = mechanical three-piece (update_sina_mf exit-code law + sina_mf_accept sec-4 gates "
    "coverage>=5000/self-collapse/idempotency + N=250 depth census -> sina_mf_update_status complete+N=250 = "
    "bm-b sina-construct prereg open-gate + MSG ready-panel notice); (2) Monday 09-28 09:15 T-91 s3 auto-fire "
    "full chain (SIG/BARS-09-28 -> sysv1 replay -> first-cohort entries+marks -> three report faces); (3) 10-01 "
    "month trio standing (science_audit+monthly_briefing+self_review first October round); (4) next 5x HANDOVER "
    "= R325 [via bm-a]"
)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")
print("state round_no:", st["round_no"], "| heartbeat epoch:", hb["heartbeat_epoch_utc"],
      "| clock_read:", hb["clock_read"], "| report line appended:", len(line), "chars")
