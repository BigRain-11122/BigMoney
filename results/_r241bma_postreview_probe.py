# -*- coding: utf-8 -*-
"""R241 S2: post_review verdict scan + C-arm batch status probe."""
import io
import json
import os

print('=== post_review verdict distribution ===')
dist = {}
bad = []
for line in io.open('results/post_review.jsonl', encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    v = str(r.get('verdict', r.get('status', '?')))
    dist[v] = dist.get(v, 0) + 1
    if v.upper() in ('NO', 'FAIL', 'FALSE', '✗') or '✗' in v:
        bad.append((r.get('id', r.get('ticket', '?')), v))
print('distribution:', dist)
for b in bad:
    print('BAD ROW:', b)

print()
print('=== C-arm batch (T-70) status ===')
try:
    s = json.load(io.open('results/local_coding_pilot/C_batch_status.json',
                          encoding='utf-8'))
    print(json.dumps(s, ensure_ascii=False)[:600])
except Exception as e:
    print('status file ERR', e)
    for cand in ('results/local_coding_pilot/C_batch.log',):
        if os.path.exists(cand):
            with io.open(cand, encoding='utf-8', errors='replace') as f:
                tail = f.readlines()[-8:]
            print('--- log tail ---')
            for l in tail:
                print(l.rstrip()[:160])
