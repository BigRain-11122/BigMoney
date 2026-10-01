import json
import os
import glob

# 1. claim file for LOWAMP-P2-NULLS
for f in glob.glob('results/claims/LOWAMP-P2-NULLS/*.json'):
    print('CLAIM_FILE:', f)
    print(json.dumps(json.load(open(f, encoding='utf-8')), ensure_ascii=False, indent=1)[:800])

# 2. nulls.jsonl product count
n = 0
with open('results/lowamp_p2/nulls.jsonl', encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            n += 1
print('NULLS_JSONL_ROWS:', n)

# 3. the waiting entry
p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
ents = p.get('entries', p) if isinstance(p, dict) else p
if isinstance(ents, dict):
    ents = list(ents.values())
for e in ents:
    if e.get('status') not in ('done',):
        print('NON_DONE:', json.dumps(e, ensure_ascii=False)[:600])
