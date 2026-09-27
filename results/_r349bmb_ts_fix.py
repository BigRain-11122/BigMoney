# -*- coding: utf-8 -*-
# r349 bm-b: fix future-dated timestamps (r96 fresh-read correction family)
import io, json

p = 'logs/iteration-loop/round_reports.md'
t = io.open(p, encoding='utf-8').read()
assert '2026-09-28T00:33:00+08:00 | round 349 bm-b' in t
t = t.replace('2026-09-28T00:33:00+08:00 | round 349 bm-b', '2026-09-28T00:21:00+08:00 | round 349 bm-b')
io.open(p, 'w', encoding='utf-8', newline='').write(t)

p2 = 'logs/iteration-loop/state.json'
d = json.load(io.open(p2, encoding='utf-8'))
for k in ('last_round_ts', 'updated_at', 'last_seen', 'ts'):
    d[k] = '2026-09-28T00:21:00+08:00'
s = json.dumps(d, ensure_ascii=False, indent=1)
io.open(p2, 'wb').write(s.replace('\n', '\r\n').encode('utf-8'))

p3 = 'fleet/inbox/MSG-20260928-0030-bmb-bma-T94-adjudication.json'
t3 = io.open(p3, encoding='utf-8').read()
old_ts = '"ts": "2026-09-28T00:26:00+08:00"'
assert old_ts in t3
t3 = t3.replace(old_ts, '"ts": "2026-09-28T00:16:00+08:00"')
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)

p4 = 'CODELY.md'
t4 = io.open(p4, encoding='utf-8').read()
assert '[2026-09-28 00:3x r349 bm-b]' in t4
t4 = t4.replace('[2026-09-28 00:3x r349 bm-b]', '[2026-09-28 00:2x r349 bm-b]')
io.open(p4, 'w', encoding='utf-8', newline='').write(t4)

print('all four timestamp fixes applied')
