import json
c = json.load(open('results/multicore_census.json', encoding='utf-8'))
v = c.get('verdicts')
print('verdicts type:', type(v).__name__)
if isinstance(v, dict):
    sc = [k for k, x in v.items() if isinstance(x, dict) and x.get('verdict') == 'single_core']
    other = [k for k, x in v.items() if isinstance(x, dict) and x.get('verdict') != 'single_core']
    print('single_core', len(sc), ':')
    for k in sorted(sc):
        print('  ', k)
    print('multiproc', len(other))
elif isinstance(v, list):
    print(json.dumps(v[:3], ensure_ascii=False, indent=1)[:500])
