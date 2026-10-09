"""r806 bm-b: repr-debug the distribution line of post_review REPORT face."""
import glob, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
face = sorted(glob.glob('results/post_review/REPORT*'), key=os.path.getmtime)[-1]
raw = open(face, encoding='utf-8').read()
for ln in raw.splitlines():
    if '判定分布' in ln or '分布' in ln:
        print(repr(ln[:300]))
        break
# verdict column values across table rows
import collections
col2 = collections.Counter()
for ln in raw.splitlines():
    if ln.startswith('|'):
        parts = [p.strip() for p in ln.split('|')]
        if len(parts) >= 3:
            col2[parts[2][:2]] += 1
print('verdict-col top:', col2.most_common(10))
