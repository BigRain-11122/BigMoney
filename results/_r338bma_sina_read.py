import json
import io

# 1. census results
try:
    r = json.load(open('results/shortline/sina_construct_p1.json', encoding='utf-8'))
    print('== sina_construct_p1.json keys:', list(r.keys()))
    for k in ['verdict', 'judgment', 'status', 'd6', 'pass', 'cutoff', 'evidence_cutoff']:
        if k in r:
            print(' ', k, '=', json.dumps(r[k], ensure_ascii=False)[:300])
    # dump structure summary
    def brief(o, depth=0):
        if depth > 2: return '...'
        if isinstance(o, dict):
            return {k: brief(v, depth + 1) for k, v in list(o.items())[:12]}
        if isinstance(o, list):
            return ['len=%d' % len(o)] + ([brief(o[0], depth + 1)] if o else [])
        return o
    print(json.dumps(brief(r), ensure_ascii=False, indent=1)[:1800])
except Exception as e:
    print('census json read fail:', e)

# 2. pool entry for SINA-CONSTRUCT-P1
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in pool.get('entries', []):
    if 'SINA' in json.dumps(e):
        print('== POOL ENTRY:', json.dumps(e, ensure_ascii=False)[:600])
