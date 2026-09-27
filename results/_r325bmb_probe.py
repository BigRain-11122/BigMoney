# -*- coding: utf-8 -*-
"""r325 bm-b push-collision resolver: probe + resolve 18 UU files per bigmoney-conflict-resolve recipes."""
import subprocess, json, re, io

def blob(rev, path):
    return subprocess.run(['git', 'show', rev + ':' + path], capture_output=True).stdout.decode('utf-8', errors='replace')

p = 'docs/daily_report/REPORT-2026-09-27.json'
for rev in [':2', ':3']:
    raw = blob(rev, p)
    m = re.findall(r'"(generated[^"]*|ts|asof)"\s*:\s*"(2026[^"]+)"', raw)[:3]
    print(rev, 'len', len(raw), '| ts fields:', m)

pm = 'docs/daily_report/REPORT-2026-09-27.md'
for rev in [':2', ':3']:
    raw = blob(rev, pm)
    m = re.findall(r'2026-09-27[ T]\d\d:\d\d', raw)[:3]
    print(rev, 'md len', len(raw), '| ts in md:', m)

# check current worktree state.json round_no (post pick-2 partial merge)
s = json.load(io.open('logs/iteration-loop/state.json', encoding='utf-8-sig'))
print('worktree state.json round_no:', s.get('round_no'))
# autofill launches shapes
for rev in [':2', ':3']:
    d = json.loads(blob(rev, 'results/autofill_state.json'))
    print(rev, 'autofill launches n=', len(d.get('launches', [])), '| last_tick ts=', (d.get('last_tick') or {}).get('ts'))
# compute_audit shapes
for rev in [':2', ':3']:
    d = json.loads(blob(rev, 'results/compute_audit.json'))
    h = d.get('history', [])
    print(rev, 'compute_audit history n=', len(h), '| latest ts=', (d.get('latest') or {}).get('ts'), '| hist tail ts:', h[-1].get('ts') if h else None)
# regime_state shapes
for rev in [':2', ':3']:
    d = json.loads(blob(rev, 'results/regime_state.json'))
    h = d.get('history', [])
    print(rev, 'regime keys:', list(d.keys()), '| history n=', len(h), '| state=', repr(d.get('state'))[:40],
          '| last hist:', {k: h[-1][k] for k in list(h[-1])[:4]} if h else None)
