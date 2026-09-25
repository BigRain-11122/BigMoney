import io, json

# 1) last watermark probe full dump
lines = io.open('results/watermark.jsonl', encoding='utf-8-sig').read().strip().splitlines()
last = json.loads(lines[-1])
print('last probe keys:', list(last.keys()))
print(json.dumps(last, ensure_ascii=False)[:700])

# 2) post_review active FAIL rows
try:
    pr = io.open('results/post_review.jsonl', encoding='utf-8-sig').read().strip().splitlines()
    print('post_review lines=', len(pr))
    fails = []
    for l in pr:
        try:
            d = json.loads(l)
        except Exception:
            continue
        v = d.get('verdict') or d.get('result')
        if v in ('FAIL', 'fail', 'x', 'X', False):
            fails.append(d)
    print('fail rows=', len(fails))
    for d in fails[-5:]:
        print(json.dumps(d, ensure_ascii=False)[:260])
except Exception as e:
    print('post_review ERR', e)
