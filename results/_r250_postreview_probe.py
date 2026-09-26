import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
rows = [json.loads(l) for l in open('results/post_review.jsonl', encoding='utf-8') if l.strip()]
# real failures = verdict explicitly negative (not WAIT/pending states)
neg = [r for r in rows if str(r.get('verdict', '')).strip().upper() in ('NO', 'FAIL', 'FALSE', 'X') or r.get('verdict') == '\u2717']
wait = [r for r in rows if str(r.get('verdict', '')).strip().upper() == 'WAIT']
print('total', len(rows), 'WAIT', len(wait), 'NEG', len(neg))
for r in neg[-10:]:
    print('NEG:', r.get('id'), r.get('ts'), r.get('failed_checks'))
# latest run timestamp of the re-derivation
print('latest ts:', rows[-1].get('ts') if rows else None)
# moneyflow panel state location probe
for cand in ['data/moneyflow', 'data/shortline/moneyflow', 'data/shortline', 'results/moneyflow']:
    if os.path.isdir(cand):
        print(cand, '->', sorted(os.listdir(cand))[:12])
