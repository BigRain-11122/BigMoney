# r663 bm-a: reliable fleet/tasks scan (PS5.1 ConvertFrom-Json crashes on CJK-heavy tickets)
import json, glob, os

rows = []
for fp in sorted(glob.glob(r'fleet\tasks\*.json')):
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            t = json.load(f)
    except Exception as e:
        rows.append((os.path.basename(fp), 'PARSE_FAIL', '', str(e)[:80], ''))
        continue
    st = t.get('status', '?')
    if st != 'done':
        rows.append((os.path.basename(fp), st, t.get('claimed_by', ''), t.get('id', ''),
                     (t.get('title') or '')[:70]))

print(f'not-done count={len(rows)}')
for fn, st, cb, tid, title in rows:
    print(f'{st:10s} {cb:6s} {tid:22s} {title}')
