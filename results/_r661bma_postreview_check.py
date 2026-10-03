import json

lines = open(r'results\post_review.jsonl', encoding='utf-8').read().strip().splitlines()
from collections import Counter
c = Counter()
nos = []
for ln in lines:
    try:
        d = json.loads(ln)
        v = str(d.get('verdict', ''))
        c[v] += 1
        if v == 'NO':
            nos.append(d)
    except Exception:
        c['parse_err'] += 1
print('verdict dist:', dict(c))
print('NO receipts:', len(nos))
for d in nos[-8:]:
    print(d.get('ts'), '|', d.get('id'), '|', str(d.get('claim'))[:70])
