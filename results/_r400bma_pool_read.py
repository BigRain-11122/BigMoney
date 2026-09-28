import json
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in d['entries']:
    if e.get('id') in ('DECISION-CHAIN-V2-P1', 'DECISION-CHAIN-V3-TOURNAMENT', 'TRIAL-LABOR-W4-JUDGE'):
        print('=' * 20, e.get('id'))
        for k, v in e.items():
            if k == 'shards':
                for s in v:
                    print('  shard:', json.dumps(s, ensure_ascii=False)[:400])
            else:
                print(f"{k}: {json.dumps(v, ensure_ascii=False)[:600]}")
