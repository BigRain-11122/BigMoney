# -*- coding: utf-8 -*-
"""R248 bm-a closeout: round report entry + state round 248 + heartbeat
(orders_ack +3 CEO orders, epoch int verified) + orders double-scan."""
import datetime as dt
import io
import json
import time

NOW = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
EPOCH = int(time.time())
CLOCK = dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
CLOCK = CLOCK[:-2] + ":" + CLOCK[-2:]  # +08:00 form

# 1) round report (bm-a file)
RR = "logs/iteration-loop/round_reports-bm-a.md"
entry = (
    f"{NOW} | R248 | [wm:probe py_low_board_clear (py 0.1% board-clear legal idle: open=0 bandit=0 "
    "no local batch; honest flip-side: compute_audit pool_starvation_candidate=true post-harvest "
    "ready=0 -> supply duty next rounds) + audit CLEAN flags=[]] | did: S0 pull-rebase fast-forward "
    "8ee47a83->e721fadc (bm-b r252 CEO triple-order execution) clean, no conflict; S0.5 orders diff "
    "3 UNACKED CEO orders O-20260926-1326/1332/1342 (all via bm-a session, tickets dispatched same "
    "window): receipts recorded -- O-1326 T-79 DONE by bm-b r252 (retro-paper full arc freeze->run->"
    "leaderboard->CEO_APPROVALS ledger), O-1332 T-80 + O-1342 T-81 claimed+started by bm-b r252 "
    "(bm-a yields ticket bodies per anti-dup law, bm-b heartbeat alive 13:55); decisions tail "
    "reviewed: D-20260926-10 (trading-day-gated STALE exemption + IntradayMarks E2 closed) = "
    "reasonable, executor=HQ tool-face, this repo zero-action receipt noted; S1 smoke 25/25; "
    "S3 MAIN = CN-REV-TILT-P1 HARVEST per r244 landed-marker law: deterministic gate "
    "results/_r248bma_cnrev_harvest.py re-derived G1'v2 per-cell from stored inputs -> PASS -> pool "
    "entry+shard cnrev-0of1 flipped done + harvest_note; VERDICT NEGATIVE 4/4 (x1 net Sharpe "
    "REV20_bare 0.1976 / REV60_bare 0.4757 / REV20_tilt 0.0104 / REV60_tilt 0.4217 all < "
    "skill_line_v2 0.6147 = null term dominates; REV60 pair CI95 low >0 but line fail; G2 not "
    "applicable; D6 max|corr| 0.3238 < 0.7 no-reject) -> CN-REVERSAL-TILT model judged negative per "
    "prereg s4 (判负照登 no CN-* paper wiring); tilt axis FALSIFIED in pre-registered honest "
    "direction (tilt-bare -0.054/-0.187; tilt-vs-bare corr 0.9704/0.7553 = inert at portfolio "
    "layer); cost-face forecast hit (REV60 x2 0.4377 > REV20 x2 0.0705); extreme-day forensics "
    "results/_r248bma_d1_forensics.py: max|d1| +5.0625 = 1992-12-10 k=3 micro-universe basket "
    "600612 +927% / 600613 +886% persistent-level jumps (1992 no-limit era + suspected unadjusted "
    "corporate action in P1C close-only face; artifact inflates candidate AND it still fails = "
    "verdict robust; panel-quality note for future census preregs); prereg s1 corr blank 0.3238 + "
    "s7/s8 backfilled with run numbers only (R99 law); P0 REPAIR same round = gate_attrition "
    "dual-list consumer-chain defect: 3 rows (CE-ADMISSION-B1/DIV_LOWVOL_P1/CN-REV-TILT-P1) "
    "silently invisible since 09-25 15:06 (producers wrote misnamed 'history', consumers "
    "bandit_queue/monthly_briefing/science_audit C4 all read 'entries') -> root-fixed 3 producers "
    "scripts/{cn_rev_tilt_p1,ce_admission_intake,div_lowvol_backtest}.py + zero-loss ts-ascending "
    "merge results/_r248bma_attrition_merge.py (history left as residue); T-73 progress_r248 "
    "appended (exact resume point = s3 remaining preregs); post_review row T-73-CN-REV-TILT-P1 "
    "registered per O-2115/R246 law (9 machine checks, pre-frozen sources only) -> reviewer run "
    "YES 9/9 (17 YES/0 NO/5 WAIT) = three-state closure (立法 git/生效 判据过/验收 复审 YES); "
    "CODELY pit entry appended (r239 family new dimension: dual-list ledger producer/consumer "
    "split); S6 28 legs ALL exit 0 (weekend no-ops: daily 0 rows cutoff 09-24, regime ORANGE d2 "
    "shadow, clock ORANGE_COOL idempotent regen, lhb/heat/futures/options/sina_mf/ths zero-network "
    "or throttle no-ops, moneyflow spawn-throttle 21.5min, AH spawn throttled, fp bm-c lane, "
    "fundamental 16.5h fresh, blf 5222 all gates, NO new bars -> live.paper chain correctly "
    "skipped, scorecard 6 traders, report 4 faces, build_status, token delta=71) | evidence: "
    "commit <this> + harvest gate exit 0 output + reviewer YES row in results/post_review.jsonl + "
    "S6 exit codes in transcript | next: (1) s3 remaining model preregs CN-CORE-SATELLITE/"
    "CN-REGIME-POLICY/CN-DIV-LOWVOL-ROT = pool supply line (O-1332 不断链律, starvation candidate "
    "honest); (2) bm-b T-80 six-face battery + T-81 profile cards in flight -- do not touch; "
    "(3) 09-28 Monday new-bar chain; (4) 10-01 month-boundary trio + REGIME_GUARD v3 date gate; "
    "(5) T-70 verdict window 10-09"
)
with io.open(RR, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(entry + "\n")

# 2) state file
SP = "state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))
st["round_no"] = 248
st["did"] = ("R248: CN-REV-TILT-P1 harvested per r244 (pool flipped done, verdict NEGATIVE 4/4 "
             "G1'v2, tilt axis falsified, 1992 k=3 artifact forensics disclosed, prereg s7/s8 "
             "backfilled) + gate_attrition dual-list consumer-chain P0 repair (3 producers "
             "root-fixed + 3 rows zero-loss merged) + 3 CEO orders acked (T-79 done / T-80+T-81 "
             "bm-b in flight) + post_review T-73 row YES 9/9")
st["verdict"] = "GREEN"
st["next"] = ("s3 remaining preregs CN-CORE-SATELLITE/CN-REGIME-POLICY/CN-DIV-LOWVOL-ROT = pool "
              "supply line (starvation candidate honest); bm-b T-80/T-81 in flight do-not-touch; "
              "09-28 Monday new-bar chain; 10-01 month-boundary trio + REGIME_GUARD v3 date gate; "
              "T-70 verdict window 10-09")
st["ts"] = NOW
st["updated_at"] = NOW
st["current_task"] = ("R248 done: harvest+verdict NEGATIVE registered+attrition repair; next=s3 "
                      "remaining preregs (pool supply)")
with io.open(SP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# 3) heartbeat (bm-a writes only its own file)
HP = "fleet/machines/bm-a.json"
h = json.load(io.open(HP, encoding="utf-8"))
ack = h.get("orders_ack", "")
for o in ("O-20260926-1326-bm-a.md", "O-20260926-1332-bm-a.md",
          "O-20260926-1342-bm-a.md"):
    if o not in ack.split():
        ack = (ack + " " + o).strip()
h["orders_ack"] = ack
h["last_seen"] = NOW
h["current_task"] = st["current_task"]
h["verdict"] = "alive"
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = CLOCK
with io.open(HP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# verify epoch int (smoke F7 law)
h2 = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print(f"closeout ok: round 248, epoch={h2['heartbeat_epoch_utc']} (int verified), "
      f"acked total={len(h2['orders_ack'].split())}")
