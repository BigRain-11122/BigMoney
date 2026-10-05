# r719 bm-b S7 accounts writer (state/round-report/heartbeat)
import json, io, time, datetime

s = json.load(io.open('state.json', encoding='utf-8'))
s['round_no'] = 719
s['round_no_gap_note'] = ('r719 honest skip: r716-718 dead-session chain adopted in-window; '
                          'r716 principal (56964, started 08:24) completed 6bbdbf1a0 + addendum d35c2ef96 pushed; '
                          'state gap 715->719 per r713 law')
s['last_round_at'] = '2026-10-05T08:58:00+08:00'
s['updated'] = '2026-10-05 08:58:00'
s['clock_read'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
io.open('state.json', 'w', encoding='utf-8').write(json.dumps(s, ensure_ascii=False, indent=1))

line = ('2026-10-05T08:58:00+08:00 | round 719 (bm-b, dept:engineering+fleet coordination, '
        'S0 dead-session-chain recovery + integration round, yield-to-principal) | '
        '[watermark verdict: GREEN (red=false; probe family GREEN per r716 principal S6 chain 08:49)] | '
        'recovery+merge: r716/717/718 dead-session chain + bm-c r523 + live-race tips adopted -- '
        'S0 churn-absorb 45b158fa9 (35 files) + 16-UU wave canon-resolved c808b5e38 '
        '(resolver _r719bmb_merge_resolve.py: 15 take-theirs byte-faithful ts-newer 08:43-08:46 '
        '+ compute_audit rolling union 201+202->203 + token per-key union; reparse+CR-stage-blob asserts all PASS) '
        '+ r719-2 zero-UU live-race merge d35c2ef96 | '
        'evidence: smoke 48/48 PASS post-merge; push 9ecc485a8 delivered N=0 verified | '
        'lane posture: r716 principal (codely 56964, started 08:24) alive at push d35c2ef96 -- '
        'this session (56140, started 08:42) yields per fleet README 4 (later-arrival yields); '
        'S6 full chain NOT re-run (principal already ran S6 38 legs rc0 at 08:49, re-run = duplicate compute waste) | '
        'next: r720 next-lane firing resumes normal cycle; principal S7 state-write watched '
        '(state 715->719 gap note carries r713 law)\n')
with io.open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(line)

h = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
h['last_seen'] = '2026-10-05T08:58:00+08:00'
h['current_task'] = 'r719 recovery+integration round done (dead-session chain adopted, yielded to r716 principal)'
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8').write(json.dumps(h, ensure_ascii=False, indent=1))

h2 = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
print('accounts written; epoch=', h2['heartbeat_epoch_utc'], 'clock=', h2['clock_read'])
