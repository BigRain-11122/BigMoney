import json
lines = [l for l in open('results/post_review.jsonl', encoding='utf-8').read().splitlines() if l.strip()]
r = json.loads(lines[-1])
print('LAST_ROW=', json.dumps(r, ensure_ascii=False)[:500])
bad = []
for l in lines[-80:]:
    d = json.loads(l)
    s = json.dumps(d, ensure_ascii=False)
    low = s.lower()
    if '\u2717' in s or '"x"' in low or 'fail' in low or 'no-' in low or 'reject' in low:
        bad.append(s[:220])
print('recent_flag_rows=', len(bad))
for x in bad[-5:]:
    print('FLAG>', x)
print('---POOL ENTRIES---')
p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in p.get('entries', []):
    if isinstance(e, dict):
        print(e.get('id'), '|', e.get('status'), '|', e.get('claimed_by', ''), '|', str(e.get('result_ref', ''))[:50])
