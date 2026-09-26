import json
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in d['entries']:
    shards = ','.join("%s:%s(%s)" % (s['key'], s['status'], s.get('owner')) for s in e.get('shards', []))
    print(e['id'], '|', e['status'], '|', shards, '|lane=', e.get('lane_owner'), '|prio=', e.get('priority'))
print('updated_at=', d.get('updated_at'))
