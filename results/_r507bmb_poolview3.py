import json

p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
ents = p.get('entries', p) if isinstance(p, dict) else p
if isinstance(ents, dict):
    ents = list(ents.values())
for e in ents:
    if e.get('id') in ('LOWAMP-P2-NULLS', 'TRIAL-LABOR-W14-GENERATE'):
        print(json.dumps(e, ensure_ascii=False, indent=1))
        print('---')
