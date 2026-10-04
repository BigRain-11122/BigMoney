import json

pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = pool.get('entries', [])
from collections import Counter
c = Counter(e.get('status') for e in entries)
print('pool entries:', len(entries), dict(c))
n2 = [e for e in entries if 'N2-W15-JUDGE' in str(e.get('id', ''))]
for e in n2:
    print(e.get('id'), '|', e.get('status'), '| claimed_by:', e.get('claimed_by'), '| owner_since:', e.get('owner_since'))
st = json.load(open('results/n2_w15/n2_w15_judge_state.json', encoding='utf-8'))
print('--- judge state keys ---')
for k in sorted(st.keys()):
    v = st[k]
    if isinstance(v, (int, float, str, bool)):
        print(k, '=', str(v)[:100])
