# r714 bm-b closeout writer: CODELY pit entry + ledger backfill x2 + r714 line + state bump + heartbeat
# byte-safe UTF-8 append (r705 paradigm), no %-format (r709 law)
import json, time, datetime, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

entry = "- [2026-10-05 06:4x r714 bm-b] **\u6b7b\u4f1a\u8bdd\u5c3e\u90e8\u4e09\u8d26\u8131\u94a9\u5751\uff08r713 bm-b \u5b9e\u5f39\u00b7r708 bm-a \u53cc\u6b7b\u4f1a\u8bdd\u65cf\u59ca\u59b9\u9762\uff09**\uff1a\u4f1a\u8bdd\u6b7b\u5728 S7 \u524d\uff08r713 \u5df2\u5b8c\u6210 S4 \u8bb0\u5fc6 append+\u4e24\u8f6e merge push\uff0c\u4f46 state round_no \u505c 711/\u8f6e\u8d26\u672c\u7f3a\u884c/S6 regen \u5c3e\u5df4+receipts \u672a\u63d0\u4ea4\uff09\u2192\u4e0b\u8f6e\u63a5\u624b\u9762=\u8f6e\u53f7\u4e0d\u8fde\u7eed\uff08commits \u5df2\u7528 r712/r713 \u800c state=711\uff09+\u8d26\u672c\u65ad\u6863+\u5de5\u4f5c\u6811\u810f\u9762\u8bef\u5224\u98ce\u9669\u3002\u6b63\u6cd5=\u2460\u8f6e\u53f7\u8bda\u5b9e\u8df3\u53f7\uff08state \u76f4\u63a5\u5bf9\u9f50\u672c\u4f1a\u8bdd\u5b9e\u9645\u8f6e\u53f7\u975e\u673a\u68b0 +1\uff0cgap \u6ce8\u8bb0\uff09\u2461r712/r713 \u8d26\u672c\u884c\u4ece git commit message \u56de\u586b\uff08POST-MORTEM BACKFILL \u6807\u8bb0\uff09\u2462\u5c3e\u90e8\u4ea7\u7269 churn-absorb \u4e00\u5e76\u6536\u7f16\uff08r620 \u5f8b\uff09\u2463CODELY \u65ad\u6761\u76ee\u7ecf merge block-union \u81ea\u52a8\u627e\u56de\uff08r706 \u5f8b\u5b9e\u8bc1\uff1ashared_diff=0 appended=1\uff09\u3002How to apply\uff1a\u89c1 state round_no \u843d\u540e\u4e8e commit message \u8f6e\u53f7=\u6b7b\u4f1a\u8bdd\u5c3e\u90e8\u5f81\uff0c\u5148 git log --grep \u8f6e\u53f7\u5bf9\u9f50\u771f\u503c\u518d\u8865\u8d26\uff0c\u7981\u673a\u68b0 +1 \u9020\u6210\u649e\u53f7\u3002\n"

# --- 1) CODELY.md: append pit entry at end of Project section (before ### Reference) ---
p = os.path.join(ROOT, 'CODELY.md')
raw = open(p, 'rb').read().decode('utf-8')
assert entry[:30] not in raw, 'entry already present'
marker = '\n### Reference\n'
assert marker in raw, 'Reference section marker missing'
raw = raw.replace(marker, '\n' + entry + marker, 1)
open(p, 'wb').write(raw.encode('utf-8'))
print('CODELY entry appended')

# --- 2) ledger backfill r712/r713 + r714 line ---
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
lines = []
lines.append("2026-10-05T05:4x:xx+08:00 | round 712 (bm-b, dept:engineering+fleet coordination) [POST-MORTEM BACKFILL r714 from git history -- session died pre-S7, ledger line lost]: churn-absorb r712 38-leg S6 products + daemon lane faces (95e193702) + merge bm-c r515 S6 wave 1-UU attrition-scan ts-newer-wins theirs 05:11:13 (c270cb22d) + push delivered | verification evidence: git 95e193702 + c270cb22d on origin/main | local undelivered-to-origin commit count: 0 at push | product score: 1\n")
lines.append("2026-10-05T06:2x:xx+08:00 | round 713 (bm-b, dept:engineering+fleet coordination) [POST-MORTEM BACKFILL r714 from git history -- session died pre-S7]: merge bm-a r709 S6 wave 18-UU 17-take-ours 05:39-05:43 newer (15c44d66d) + merge round-2 bm-c r516 S6 wave 31-UU canon-resolved 28-take-ours + compute_audit union-2 208 rows + x2 union 3012 lines (2c0096a85) + r713 pit law = UU list from diff-filter=U not merge stdout (CODELY entry absorbed+merged by r714) | verification evidence: git 15c44d66d + 2c0096a85 + receipt results/_r712bmb_merge_resolve.json | local undelivered: tail S6 faces delivered via r714 absorb+merge | product score: 1\n")
r714 = now + " | round 714 (bm-b, dept:engineering+fleet coordination, dead-session-tail recovery + 31-UU integration + S6 full chain) | [watermark verdict: GREEN (red=false; probe verdict=py_low_with_work_cands legal holding surface: trio NULLS three lanes burning in place + RAM free 3.54GB < 4.0GB floor = engine self-hold machine discipline, no new burn legal)] | current activity: FUND trio NULLS V/Q/D 1191/958/759 of 2000 @06:3x burning (59.6/47.9/38.0pct, owner=bm-b keepalive fresh, ETA V 10-06T1x / Q 10-07T1x / D 10-08T0x) + satengine queue 1 RAM-gated | latest deliverable: docs/daily_report/REPORT-2026-10-05.md + docs/live_usage/LIVE-2026-10-05.md (S6 34-leg rc0 full regen 06:3x, market clock ORANGE_COOL cap50 sleeves 4 activated 0) + merge r714 31-UU canon integration delivered (origin tip 4604e1c26) | next milestone: trio V lane closeout 10-06T17 (window <=48h) + D-06 closeout report 10-07 12:00 | what was done: S0 identity anchor bm-b + churn-absorb r714 64-face (post-r713 S6 regen tail 06:07-06:09 + daemon lane faces + W118 partial shards 2-10/12 runner-dead + r712/713 evidence artifacts + r713 pit entry; r620 law) + merge-mode pull bm-a r710/711 + bm-c r516/517 wave 31 UU canon-resolved (resolver results/_r714bmb_merge_resolve.py receipt results/_r714bmb_merge_resolve.json: 27 regen take-theirs 06:10 newer per-face ts probe vs ours 06:08-06:09; attrition-scan take-ours 06:10:15; compute_audit/regime_state rolling-ledger union zero-loss; x2 identity-union 3036 lines zero-residual r706 law; token per-key max-union picked_theirs=2; CODELY per-section block-union r713 pit entry appended r706 lstrip law; stage-blob CR-normalized readback + line-anchored marker assertions r515/r506 laws) + r712/r713 dead-session ledger backfill (2 git-derived lines) + S0.5 orders double-scan 154/154 zero unacked (head scan + this closeout) + D-19 decisions watermark MATCH 755428F8 (Tools/d19_check.py canonical) zero action + S1 smoke 48/48 + S2 dual board check (job_list 0 + ticket board 0 open) + S3 watermark green + satengine alive rc0 (queue 1, RAM floor self-hold; standing line = judgment batch trio in flight, no new draft) + S6 34 legs rc0 (driver results/_r714bmb_s6_chain.ps1 r711 lineage; legs 25-28 golden-week no-new-bar honest skip cutoff 09-30 unchanged; dualrun ZERO-DRIFT streak 11 @403 entries; compute_audit CLEAN burning-healthy py 62pct window parallel_efficiency 7.06 effective cores; all collectors correct no-op; paper faces idempotent; t35 export 6 traders 18 positions equity 5,998,496 CNY; scorecard factors=10 backtest 432combos/0pass traders=6 milestones 5/7) + S7 quartet 4/4 (loop pin=2 no-op + watchdog re-registered + pre-commit/pre-push dual claws LF-normalized IN-SYNC) + attrition 4 ledgers CLEAN (healed notes) + state round_no 711->714 honest gap-note (r712/r713 died pre-S7 state bump) + heartbeat epoch int self-verify | verification evidence: smoke 48/48 rc0; S6 log results/_r714bmb_s6_chain.log 34 legs ALL RC=0; resolver receipt 32 faces + dashboard twin ts check PASS; dualrun ZERO-DRIFT streak 11; attrition evidence results/_attrition_guard_scan.json; D-19 MATCH; orders set-diff empty x2 | local undelivered-to-origin commit count: 0 (post-push fetch+rev-list self-verify) | product score: 1 (S6 CEO faces 34 legs regen = actual file changes + 31-UU integration delivered + dead-session tail recovery; no new compute legal per RAM floor + judgment batch in flight) | next-round pointers: (a) trio V closeout 10-06T17 -> FUND-VALUE nulls finalize candidate window; (b) D-06 closeout report 10-07 12:00; (c) W118 wave shard 11/12 + queue resume on RAM window (engine-owned, watch only); (d) 10-09 post-holiday data-chain check\n"
lines.append(r714)
p = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.writelines(lines)
print('ledger: 2 backfill + 1 r714 lines appended')

# --- 3) state.json round bump 711 -> 714 with gap note ---
p = os.path.join(ROOT, 'state.json')
s = json.load(open(p, encoding='utf-8'))
assert s['round_no'] == 711, 'unexpected round_no %s' % s['round_no']
s['round_no'] = 714
s['round_no_gap_note'] = 'r712/r713 sessions died pre-S7 (state bump skipped); r714 aligned to true session number per dead-session-tail law'
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
json.load(open(p, encoding='utf-8'))
print('state round_no -> 714')

# --- 4) heartbeat fleet/machines/bm-b.json ---
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
hb = {
    'machine_id': 'bm-b',
    'last_seen': clock,
    'heartbeat_epoch_utc': epoch,
    'clock_read': clock,
    'cpu_cores': 16,
    'free_ram_gb': 3.54,
    'gpu_free_vram_gb': 3.6,
    'verdict': 'healthy-burning (trio NULLS 3 lanes + RAM floor self-hold; r714 integration+S6 closeout delivered)',
    'current_task': 'trio NULLS keepalive lanes V/Q/D @1191/958/759 of 2000 + satengine W118 queue 1 RAM-gated',
    'orders_ack_count': 154,
}
p = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
old = json.load(open(p, encoding='utf-8'))
if 'orders_ack' in old:
    hb['orders_ack'] = old['orders_ack']
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
chk = json.load(open(p, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written, epoch=%d (int verified)' % epoch)
