# -*- coding: utf-8 -*-
# r444 bm-c W2 landing probe: summarize w2_judge.json (negative-result honest face)
import io, json
p = 'results/mass_trial/w2_judge.json'
d = json.load(io.open(p, encoding='utf-8'))
print('== scalar fields ==')
for k in sorted(d.keys()):
    v = d[k]
    if isinstance(v, (str, int, float, bool)) or v is None:
        print(k, '=', v)
print('== container fields ==')
for k in sorted(d.keys()):
    v = d[k]
    if isinstance(v, list):
        print(k, 'list len', len(v))
        if v and isinstance(v[0], dict):
            print('  row0 keys:', sorted(v[0].keys())[:14])
    elif isinstance(v, dict):
        print(k, 'dict len', len(v))
