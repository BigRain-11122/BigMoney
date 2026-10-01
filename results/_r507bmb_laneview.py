import json
import os

def nulls_status(path):
    if not os.path.exists(path):
        return path + ' -> ABSENT'
    try:
        p = json.load(open(path, encoding='utf-8'))
    except Exception as ex:
        return path + ' -> PARSE FAIL ' + str(ex)
    ents = p.get('entries', p) if isinstance(p, dict) else p
    if isinstance(ents, dict):
        ents = list(ents.values())
    for e in ents:
        if e.get('id') == 'LOWAMP-P2-NULLS':
            sh = e.get('shards', [{}])[0]
            return (path + ' -> entry=' + str(e.get('status')) +
                    ' shard=' + str(sh.get('status')) +
                    ' owner=' + str(sh.get('owner')) +
                    ' done_at=' + str(sh.get('done_at')) +
                    ' harvested_by=' + str(sh.get('harvested_by')))
    return path + ' -> ENTRY ABSENT'

for f in ['results/runnable_pool.json',
          'results/runnable_pool.bm-a.json',
          'results/runnable_pool.bm-b.json',
          'results/runnable_pool.bm-c.json']:
    print(nulls_status(f))
