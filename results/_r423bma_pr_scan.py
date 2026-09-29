import json

bad = []
n = 0
with open('results/post_review.jsonl', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        n += 1
        try:
            r = json.loads(line)
        except Exception:
            continue
        # look for reviewer=NO / review_verdict NO / x_fail markers
        verdict = json.dumps(r, ensure_ascii=False)
        if ('"NO"' in verdict and ('review' in verdict.lower())) or r.get('review') == 'NO' or r.get('reviewer_run') == 'NO':
            bad.append(r)
print('total lines:', n)
print('suspect NO rows:', len(bad))
for r in bad[-8:]:
    s = json.dumps(r, ensure_ascii=False)
    rid = r.get('id') or r.get('row_id') or r.get('name')
    print('-', rid, '::', s[:300])
