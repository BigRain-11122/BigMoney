import json
p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in p['entries']:
    sh = ','.join("%s:%s(own=%s)" % (s['key'], s['status'], s['owner']) for s in e.get('shards', []))
    print(e['id'], '|', e['status'], '|', sh or ("owner=" + str(e.get('owner'))))
