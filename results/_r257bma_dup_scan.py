import json, glob, os
hits = 0
for p in glob.glob('results/**/*.json', recursive=True) + glob.glob('results/**/*.jsonl', recursive=True):
    b = os.path.basename(p).lower()
    if not any(k in b for k in ('factor', 'ic', 'p1c', 'p1d', 'p1e', 'alpha')):
        continue
    try:
        s = open(p, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    low = s.lower()
    if 'turnover' not in low or 'ic' not in low:
        continue
    # a judged row literally named turnover-ish (plain TO level factor)
    for marker in ('"turnover"', 'turnover_level', 'f_turnover', '"to"', 'TO20', 'TO60'):
        if marker in s:
            print('HIT', p, 'marker', marker)
            hits += 1
            break
    if hits > 10:
        break
print('done, hits', hits)
