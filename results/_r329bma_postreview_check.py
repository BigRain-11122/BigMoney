import json, io
lines = [l for l in io.open('results/post_review.jsonl', encoding='utf-8').read().splitlines() if l.strip()]
nos = []
for l in lines:
    d = json.loads(l)
    if d.get('verdict') == 'NO':
        nos.append(d)
for d in nos:
    print(d.get('ts'), d.get('id'), str(d.get('reason', ''))[:90])
print('total NO:', len(nos))
