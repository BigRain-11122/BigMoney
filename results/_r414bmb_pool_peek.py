import json

d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in d['entries']:
    if e['id'] in ('TRIAL-LABOR-W5-JUDGE', 'TRIAL-LABOR-W5-SCREEN'):
        print('==', e['id'])
        print('  status:', e.get('status'))
        print('  result_ref:', str(e.get('result_ref'))[:300])
        print('  done_at:', e.get('done_at'))
        for sh in e.get('shards', []):
            print('  shard:', sh.get('key'), sh.get('status'), '| owner:', sh.get('owner'), '| completed_at:', sh.get('completed_at'), '| result_ref:', str(sh.get('result_ref'))[:200])
