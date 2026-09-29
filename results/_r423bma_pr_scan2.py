import json

rows = []
with open('results/post_review.jsonl', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

print('sample keys:', sorted(rows[-1].keys()))
print()
# check all distinct review-ish field values in last 40 rows
for r in rows[-40:]:
    rid = r.get('id', '?')
    rev = {k: v for k, v in r.items() if 'review' in k.lower() or 'verdict' in k.lower() or k.lower() in ('yes', 'no')}
    print(rid, '->', json.dumps(rev, ensure_ascii=False)[:220])
