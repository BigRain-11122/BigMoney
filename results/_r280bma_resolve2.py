# -*- coding: utf-8 -*-
"""R280 bm-a S7-tail rebase resolver #2: results/autofill_state.json (mixed-dict+ledger).

Collision: my maintenance commit 982809e4 vs origin (bm-b pushed new tick/claim
state in the same window). Same recipe as _r280bma_resolve.py (r203/R208/r215/
r220/r245): launches union -> ts desc cap 50 -> re-sort asc; last_tick inner-ts
whole-dict; field-level keep richer side; CRLF/no-trailing-newline/indent=1.
"""
import subprocess, json, io

def load(rev):
    raw = subprocess.run(['git','show',rev+':results/autofill_state.json'],
                         capture_output=True, check=True).stdout
    return raw, json.loads(raw.decode('utf-8-sig'))

raw_m, m = load('REBASE_HEAD')   # my maintenance commit
raw_o, o = load('HEAD')          # origin/main tip

def key(l): return (l['entry'], l['ts'], l.get('machine'), l.get('shard'))

merged = {}
for l in o['launches']: merged[key(l)] = dict(l)
for l in m['launches']:
    k = key(l)
    if k in merged:
        if len(l) >= len(merged[k]): merged[k] = dict(l)
    else:
        merged[k] = dict(l)

desc = sorted(merged.values(), key=lambda l: l['ts'], reverse=True)
if len(desc) > 50:
    print('cap50 dropped:', [(l['entry'], l['ts']) for l in desc[50:]])
kept = sorted(desc[:50], key=lambda l: l['ts'])

lt_m, lt_o = m['last_tick'], o['last_tick']
last_tick = lt_m if lt_m.get('ts','') >= lt_o.get('ts','') else lt_o
assert isinstance(last_tick, dict)

out = {'launches': kept, 'last_tick': last_tick}
for src in (m, o):
    for extra in src:
        if extra not in out: out[extra] = src[extra]

s = json.dumps(out, indent=1, ensure_ascii=False)
with io.open('results/autofill_state.json','w',encoding='utf-8',newline='\r\n') as f:
    f.write(s)

chk = json.loads(io.open('results/autofill_state.json',encoding='utf-8-sig').read())
ts_list = [l['ts'] for l in chk['launches']]
assert len(chk['launches']) == len(kept) and isinstance(chk['last_tick'], dict)
assert ts_list == sorted(ts_list), 'launches must be ts-ascending (r245)'
mine_keys = {key(l) for l in m['launches']}; orig_keys = {key(l) for l in o['launches']}
surv = {key(l) for l in chk['launches']}
print('resolved: launches', len(kept), '| last_tick', chk['last_tick'].get('ts'),
      '| mine-only-surviving', len((mine_keys-orig_keys) & surv),
      '| orig-only-surviving', len((orig_keys-mine_keys) & surv))
