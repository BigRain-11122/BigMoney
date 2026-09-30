import json
c = json.load(open('results/multicore_census.json', encoding='utf-8'))
v = c.get('verdicts')
for k in sorted(v.keys()):
    if 'innovation' in k or 'quota' in k or 'w3' in k or 'w8' in k:
        print(k, '->', json.dumps(v[k], ensure_ascii=False)[:300])
