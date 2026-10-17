# r1000 stash post_review 50-row union audit (ASCII only per encoding law)
import subprocess, os, sys

repo = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(repo)

# 1) get added rows from stash@{2} diff
diff = subprocess.run(
    ['git', 'diff', 'stash@{2}^', 'stash@{2}', '--', 'results/post_review.jsonl'],
    capture_output=True)
rows = []
for line in diff.stdout.decode('utf-8', errors='replace').splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        rows.append(line[1:].rstrip('\r'))
print('stash added rows:', len(rows))

# 2) load current face
cur_lines = set()
with open('results/post_review.jsonl', 'r', encoding='utf-8', errors='replace') as f:
    for l in f:
        cur_lines.add(l.rstrip('\r\n'))

missing = []
for r in rows:
    if r not in cur_lines:
        missing.append(r)
print('rows missing from current:', len(missing))

import json
valid_missing = []
for m in missing:
    try:
        json.loads(m)
        valid_missing.append(m)
    except Exception:
        print('NON-JSON row (len=%d):' % len(m), m[:120])

# 3) report md 6 lines check
diff2 = subprocess.run(
    ['git', 'diff', 'stash@{2}^', 'stash@{2}', '--', 'results/post_review/REPORT-20261018.md'],
    capture_output=True)
added_md = [l[1:].rstrip('\r') for l in diff2.stdout.decode('utf-8', errors='replace').splitlines() if l.startswith('+') and not l.startswith('+++')]
cur_md = open('results/post_review/REPORT-20261018.md', 'r', encoding='utf-8', errors='replace').read()
md_missing = [l for l in added_md if l.strip() and l not in cur_md]
print('report-md added lines:', len(added_md), 'missing from current:', len(md_missing))
for l in md_missing[:6]:
    print('MD+', l[:160])

# 4) sample of missing rows (first 3)
for m in valid_missing[:3]:
    print('MISS-SAMPLE:', m[:200])

# write full audit to file
out = os.path.join(os.environ['TEMP'], 'r1000_post_review_union.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'stash_added': len(rows), 'missing': len(missing),
               'missing_valid_json': len(valid_missing),
               'missing_rows': valid_missing, 'md_missing': md_missing}, f, ensure_ascii=False, indent=1)
print('audit written:', out)
