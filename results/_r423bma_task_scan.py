import json, glob
from collections import Counter

for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        j = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print(f'{p}: PARSE-ERR {e}')
        continue
    st = j.get('status', '?')
    if st in ('open', 'claimed'):
        cb = (j.get('claimed_by') or '')[:60]
        print(f"{j.get('id')} | {st} | claimed_by={cb} | immediate={j.get('immediate')}")

print('--- status counts ---')
c = Counter()
for p in glob.glob('fleet/tasks/*.json'):
    try:
        c[json.load(open(p, encoding='utf-8')).get('status', '?')] += 1
    except Exception:
        c['parse-err'] += 1
print(dict(c))
