import json, os
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = pool.get('entries', pool) if isinstance(pool, dict) else pool
if isinstance(entries, dict):
    entries = list(entries.values())
targets = ['EXCLUSION-MARGINAL-P1-RUN', 'CROSS-START-ROBUSTNESS-P1-FACEB-RUN',
           'TRIAL-LABOR-W9-JUDGE', 'TRIAL-LABOR-W10-JUDGE', 'TRIAL-LABOR-W11-JUDGE', 'TRIAL-LABOR-W13-JUDGE']
for e in entries:
    eid = e.get('id', e.get('name', '?'))
    if eid in targets:
        print('=' * 80)
        print(json.dumps(e, ensure_ascii=False, indent=1)[:1800])
