# -*- coding: utf-8 -*-
# r570 bm-a: probe pool_core_samples.jsonl for non-dict lines (compute_audit E2 red)
import json
path = 'results/pool_core_samples.jsonl'
bad = []
n = 0
with open(path, encoding='utf-8') as f:
    for i, ln in enumerate(f, 1):
        s = ln.strip()
        if not s:
            continue
        n += 1
        try:
            r = json.loads(s)
        except Exception as e:
            bad.append((i, 'UNPARSEABLE', s[:120]))
            continue
        if not isinstance(r, dict):
            bad.append((i, type(r).__name__, s[:160]))
print('total lines:', n, '| non-dict lines:', len(bad))
for b in bad:
    print(b)
