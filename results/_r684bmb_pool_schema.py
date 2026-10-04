# r684 bm-b: dump a done W3 judge entry + look for pool register helpers
import json, io

d = json.load(io.open(r'results/runnable_pool.json', encoding='utf-8'))
ents = d.get('entries', [])
for e in ents:
    if 'W3' in str(e.get('id', '')):
        s = json.dumps(e, ensure_ascii=False)
        print(e.get('id'), '| status', e.get('status'), '| shards',
              [(x.get('key'), x.get('status')) for x in e.get('shards', [])][:8])
        print('  runner:', e.get('runner'), e.get('runner_args'))
        print('  first 1000:', s[:1000])
        break
