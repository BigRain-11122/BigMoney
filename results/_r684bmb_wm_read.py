# r684 bm-b: read watermark verdict probe
import json
d = json.load(open(r'results/watermark_red.json', encoding='utf-8'))
print('red =', d.get('red'))
np = d.get('next_pick')
if isinstance(np, dict):
    print('next_pick keys:', list(np.keys()))
    print(json.dumps(np, ensure_ascii=False)[:400])
elif isinstance(np, list):
    print('next_pick:', json.dumps(np, ensure_ascii=False)[:400])
else:
    print('next_pick:', str(np)[:200])
for k in ('verdict', 'reason', 'ts'):
    if k in d:
        print(k, '=', str(d[k])[:200])
