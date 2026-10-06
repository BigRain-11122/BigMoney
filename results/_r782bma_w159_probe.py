# -*- coding: utf-8 -*-
import json, os, glob

lines = open('results/saturation_engine/ledger_bm-a.jsonl', encoding='utf-8').read().strip().splitlines()
w159 = []
for l in lines:
    try:
        d = json.loads(l)
    except Exception:
        continue
    if d.get('wave') == 159 or 'W159' in str(d.get('batch', '')):
        w159.append(d)
print('W159 ledger entries:', len(w159))
for d in w159:
    print('shard', d.get('shard'), d.get('started_at', '')[:19], '->', (d.get('done_at') or 'RUNNING?')[:19])

print('--- shard files mtime ---')
def snum(p):
    b = os.path.basename(p)
    return int(b.split('-')[1])
for f in sorted(glob.glob('results/p2cal_ext/n1_w159/shard-*.json'), key=snum):
    print(os.path.basename(f), os.path.getmtime(f))

# engine face state
st = json.load(open('results/saturation_engine/state_bm-a.json', encoding='utf-8'))
print('--- engine state keys:', {k: st[k] for k in list(st)[:10] if not isinstance(st[k], (dict, list))})
