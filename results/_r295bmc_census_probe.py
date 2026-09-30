import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
d = json.load(open('results/multicore_census.json', encoding='utf-8'))
v = d.get('verdicts')
print(type(v).__name__)
if isinstance(v, dict):
    for k, r in v.items():
        if any(t in k for t in ('cross_start', 'exclusion_marginal', 'trial_labor')):
            print('==', k)
            print(json.dumps(r, ensure_ascii=False)[:600])
elif isinstance(v, list):
    for r in v:
        if isinstance(r, dict) and any(t in str(r) for t in ('cross_start', 'exclusion_marginal', 'trial_labor')):
            print('==', r.get('runner'))
            print(json.dumps(r, ensure_ascii=False)[:600])
print('hard_law_face:', json.dumps(d.get('hard_law_face'), ensure_ascii=False)[:400])
