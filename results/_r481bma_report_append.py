import io

line = (
    "2026-09-30T17:01:xx+08:00 | r481 | dept:engineering | "
    "WM=py_low_with_work_cands rc0 (§四 legal-idle proof: board open=0 + bandit 0 + pool ready=0/0 all-closed; probe-seen cands = ① in-flight standing batch (GPU face 93% util, rogue_apps empty = sanctioned standing compute) ② bars_present=true (data-face fact, not a burn candidate); RW-5 freeze window forbids new burns = no legal new batch to ignite) | "
    "What was done: (1) S0.5 double scan: orders 127/127 zero unacked + decisions tail max=D-40 zero new rows (acked r480) (2)**Q9 post-settle full rescan PASS** (r476 pointer debt discharged: 62 ticks / 1116 position records / pre-fix 20 defect rows preserved / post-fix zero-priced=0, 15:00 settle tick face included, exit 0) (3)**HANDOVER 5x catch-up** (r480 in-round miss = pit-79 family re-offense, this window lands r476-480 5x entry: RW-1~7 closeout window full record + unified chain 362,083 + product drift list + pointers) (4)**09-30 bar upstream direct probe**: sina 510300 upstream tail=2026-09-29 (pre-holiday evening lag evidence, collector honest no mis-fetch, failures=0; tonight's rounds auto-hook via update_daily + live.paper auto-hook shadow when bar lands) (5) S6 chain 36 legs all rc0: dualrun ZERO-DRIFT 51/3, audit flags pool_starvation+supply_floor (RW-5 freeze legal idle), WM probe, update_daily 0-new rc0 x2, regime ORANGE d3 (hs300<MA200 #10 + breadth 0.83>=65%), scorecard 6/28/7 (S2/A4, VOLATILITY 87.0 best), CALL ORANGE_COOL sleeves4 act0, collectors lhb rc3 source-rewrite quarantine round 10 (42->67 netbuy flip, local zero-write) / heat already-collected / futures/repo/options/sina_mf/ths legal no-op, moneyflow rank-spawn throttled, ah detached refresh spawned, fundamental 5.2h fresh skip, b_layer 5 gates pass, lane guards 6 honest no-op, promotion 0/22 honest (paper=0m g2 subleg_fail), aggr/grid/sysv1 marks idempotent no-op, t35_export 09-29 regenerated (6 traders 18 pos equity 5,995,354), dscore / dreport REPORT-20260930 faces=5 / ceo_live LIVE-20260930 (ORANGE cap50 COOL 6 members intraday 15:00 settle included) / build_status / token delta=0 all rc0 (6) attrition guard CLEAN (4 ledgers, 2 healed notes), self-heal trio green (loop pin=8 no-op, watchdog Ready 17:20, claw installed), inbox W14 berth materials (bmc->ALL, bm-b primary, not this machine) read->processed | "
    "Verification evidence: smoke 47/47, Q9 scan PASS exit 0, S6 all rc0 (lhb rc3 honest), sina upstream tail 09-29 direct evidence, heartbeat epoch int 1790758749 self-verified, state 481 | "
    "Current activity: pre-holiday closeout done, awaiting 10-01 month-first trio (science_audit/monthly_briefing/self_review); "
    "Latest deliverable: research/HANDOVER.md 5x catch-up entry r476-480 (RW closeout window, 16:5x) + LIVE-2026-09-30 regenerated (15:00 settle marks included); "
    "Next milestone: 10-01 month-first trio + REGIME_GUARD v3 date gate auto-activation (10-01 00:00, hands-off) + RW-5 external review 10-03 -> unfreeze supply lines + Q4 slimming first live-fire = 10-08 post-holiday 2nd tick + holiday rounds one-line discipline (10-01~10-07) | "
    "next: r482 = watch round (09-30 bar lands -> S6 chain auto-hook + live.paper conditional block on new bar); 10-01 first round = month-first trio + governance zero-double-run (Q4 slot discharged, standing instance = 2027-01-01) [via bm-a]\n"
)

with io.open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write('\n' + line if not io.open('round_reports-bm-a.md', encoding='utf-8').read().endswith('\n') else line)

# verify append
t = io.open('round_reports-bm-a.md', encoding='utf-8').read()
assert 'r481' in t.splitlines()[-1], 'append verify failed'
print('report appended, last line starts:', t.splitlines()[-1][:60])
print('total lines:', len(t.splitlines()))
