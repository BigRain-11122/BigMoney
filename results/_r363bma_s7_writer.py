# -*- coding: utf-8 -*-
"""r363 bm-a S7 close-out writer: CODELY pit row append + round report lines
(R362 addendum + R363) + state-bm-a.json + heartbeat. All byte-safe, verified.
"""
import json
import subprocess
import time

sys_reconfigure = None
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOW = "2026-09-27T23:31:30+08:00"
EPOCH = int(time.time())

# ---------- 1) CODELY pit-law row: DROPPED by four-question gate Q2 ----------
# r339 already carries the autocrlf worktree CRLF-illusion canon (byte-edit face);
# this lesson (line-level verify corollary) = thin delta over r339 -> recorded in
# round report 流水 layer + resolver scripts instead of hot CODELY (would breach
# 10,000B hard line at 10,186B). No CODELY write this round; stays 9,714B.

# ---------- 2) round report lines ----------
addendum = """2026-09-27T23:31:30+08:00 | R362 addendum bm-a | push-cycle yield + two-wave storm resolved by R363 recovery: (a) T-94 claim-collision adjudicated per fleet README sec.4 -- bm-b 22:49:09 first-claim owns s1 lane, my 22:57 blind-parallel claim yields (r239-family race 4th instance, same-window as bm-c r113/r114); wave-1 s1+s2 artifacts (prereg c638f8cf R99 seed 20283000 + engine selftest 11/11 + screen 975->166) land as SIDE-BRANCH EVIDENCE, adopt-vs-supersede = owner bm-b per MSG-2261 precedent, s2/s3 shard offer = MSG-2335, ledger +975 stays counted (invalidated-runs-still-count); ticket yield_note_bm_a + progress_r362 = yield record; (b) storm wave-1 = 17-UU final-pick stop of killed r362 session, recovered via commit-blob sourcing (:2:=5c8e4542/:3:=9ddf5883), twins same-side MINE, compute_audit 201+201->202 no-cap, autofill identical-47 tie->HEAD r140, regime 2+2 identical, CODELY+archive memory-union with batch-collision renumber mine 35->36 (bm-c r113 batch-35 in place, r176 yield law); (c) storm wave-2 vs bmb-r347+bmc-r114/115 = 16-UU mirror, snapshots/twins take-OURS fresher 23:19-20, compute_audit 201+202->204 no-cap zero-loss, autofill auto-merged-verified (launches 47 last_tick 23:20:02), archive auto-merge==mine LINE-IDENTICAL (CRLF +1,152B = worktree translation noise, line-level check law), CODELY union 10,401B over line -> in-window fold r91/r93/r98 (verbatim batch-36 section x3 verified) -> 9,714B <= 10,000B; resolvers = results/_r363bma_resolve.py + _r363bma_resolve2.py + _r363bma_hand_phase.py + _r363bma_hand_phase2.py; PUSHED c19468d7 pre-amend window message-fixed (yield+storm+renumber facts). The R362 'next: s3 per-stage freeze' pointer is SUPERSEDED: s3 = owner bm-b's face, my role = shard claim on owner freeze per MSG-2335.
"""
r363 = f"""2026-09-27T23:31:30+08:00 | R363 bm-a (dept:总经办·舰队·killed-session recovery) | WM first-line verdict: py_low_board_clear legal-idle (probe 23:28 py 0.2% n=2 span 23.1min board-clear; audit v2.3 23:28 CLEAN py 0.2% flags=[] load_state pool-supply-gap W2A-ready-owned-by-bmb; T-94 trial batch IN FLIGHT owner bm-b per yield -> anti-dup forbids parallel wave drafting, supply = owner freeze + my MSG-2335 shard offer, not idle-by-choice) | did: S0-1 identity anchor bm-a -> S0 inherited MID-REBASE stop of killed r362 session (23:12 death, resolver scripts 23:10-12 fresh, no concurrent session, round.lock 23:18:01 mine) -> two-wave storm resolved per skill canon (see R362 addendum: 33 UU total, zero-loss unions, yield adjudication, batch renumber 35->36, in-window fold, PUSHED c19468d7) + S0.5 orders 98/98 zero-unacked (99th file=README not an order) + decisions zero-new-actionable (C-01 seat-3 opinion already issued r326, window to 09-29 12:00) + MSG-2335 shard-offer materialized (ticket pointer was dangling, r362 killed pre-write) + S1 smoke 25/25 + S2 board zero-open + S6 chain 25+ scripts ALL rc=0 Sunday no-op family zero-masked (daily 0-new cutoff 09-24 + regime ORANGE shadow #10 + scorecard 6strat/28trader/7port S2 A4 + clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 + lhb honest quarter refetch 5209 rows 0-new (09-25 Mid-Autumn closed) + heat weekend + futures/repo/options cutoff-covered zero-network + MF rank-pass 23.3min<30min throttle self-heal + sina_mf covered + lane-guards astock/rev_osc/alloc/fund_premium stdout-no-op + ths same-day idempotent + ah spawn-throttled 23min same EM family + fundamental 1.8h fresh-skip + b_layer 5222 mask all-5-gates pass + paper family: live.paper OK 2-bars shadow + t35v PASS zero-pending + t24 22/22 drift=0 + promo 0/22 honest NOT-ELIGIBLE + aggr/grid/sysv1 idempotent no-op + t35 export 09-24 regen 6traders 18pos equity 5,996,645 + daily_scorecard + daily_report REPORT-2026-09-27 faces=4 token=1 + build_status + token_meter delta=0 L2 1-leg) + S7: schtasks 4/4 + claw identical + tick 23:30:01 keepalive carried (launches 47 flat, pool W2A=bm-b lane) + CODELY held 9,714B<=10,000B (CRLF line-level-verify pit deferred to 流水 layer per four-question gate Q2 r339-overlap) + state/heartbeat round 363 | verify: smoke 25/25 + resolver parse-verify 15/15 + 14/14 marker-clean + entry-level zero-loss both waves + push FAST c19468d7 + S6 all rc=0 zero masked + orders 98/98 + epoch int verified + MSG-2335 json valid | next: bm-b T-94 s2 screen-shard declare watch -> my shard claim per MSG-2335 (owner freeze gate); Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25 armed; first bar ~15:30 -> live.paper accrue + t35 verify + exports; sysv1 first SIG marks via bm-b BARS evening); MF/AH EM self-heal watch; council vote-record window close 09-29 12:00; next 5x=R365 HANDOVER
"""
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(addendum + r363)
print("round report: R362 addendum + R363 appended")

# ---------- 3) state-bm-a.json ----------
state = {
    "round_no": 363,
    "did": "R363: killed-r362-session recovery round: two-wave push-storm resolved (wave-1 17-UU via commit-blob sourcing 5c8e4542/9ddf5883; wave-2 16-UU mirror vs bmb-r347+bmc-r114/115 take-OURS fresher; compute_audit 201+201->202->204 no-cap zero-loss; autofill identical-47 tie->HEAD then auto-merged-verified; archive auto-merge==mine line-identical per new CRLF line-level check law) + T-94 yield landed (bm-b 22:49:09 owner per sec.4; artifacts side-branch evidence; batch-collision renumber mine 35->36; in-window fold r91/r93/r98; CODELY held 9,714B<=10,000B (pit row deferred to 流水 layer per r339-overlap four-question gate); PUSHED c19468d7) + MSG-2335 shard-offer materialized (dangling pointer fixed) + orders 98/98 + smoke 25/25 + S6 25+ rc=0 Sunday no-op family zero-masked + S7 schtasks 4/4 claw identical heartbeat closeout",
    "verify": "smoke 25/25 + resolver parse-verify 15/15+14/14 + zero-loss asserts both waves + push FAST c19468d7 + S6 all rc=0 + orders 98/98 + epoch int",
    "next": "NEXT-ROUND watch: bm-b T-94 owner s2/s3 freeze -> my shard claim per MSG-2335 on pool declare; Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25; first bar ~15:30); MF/AH EM self-heal; council window 09-29 12:00; next 5x=R365 HANDOVER",
    "last_round_at": NOW,
    "current_task": "R363 recovery closed (yield complete, storm landed); next = owner-freeze watch + Monday T-91 chain",
    "updated": NOW,
}
open("state-bm-a.json", "w", encoding="utf-8", newline="\n").write(json.dumps(state, ensure_ascii=False, indent=1) + "\n")
print("state: round 363 written")

# ---------- 4) heartbeat ----------
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
h["last_seen"] = NOW
h["current_task"] = "R363 recovery closed: two-wave storm resolved + T-94 yielded to bm-b (owner); shard offer MSG-2335; Monday T-91 s3 auto-fire armed"
h["cpu_cores"] = 32
h["cpu_pct"] = 32.0
h["free_ram_gb"] = 46.5
h["gpu_free_vram_gb"] = 5.2
h["verdict"] = "healthy recovery round (killed r362 push-cycle inherited and landed: 33 UU zero-loss, T-94 yield adjudication complete owner=bm-b, smoke 25/25, S6 25+ rc=0 zero-masked, orders 98/98, MSG-2335 shard offer)"
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["round_no"] = 363
assert isinstance(h["heartbeat_epoch_utc"], int) and "T" in h["clock_read"]
open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n").write(json.dumps(h, ensure_ascii=False, indent=1) + "\n")
h2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert len(h2["orders_ack"]) == 98
print(f"heartbeat: epoch={EPOCH} (int verified) clock={NOW} orders_ack 98 round_no=363")
print("S7 WRITER DONE")
