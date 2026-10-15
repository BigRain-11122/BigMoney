# -*- coding: utf-8 -*-
# r1017 bm-a scratch: extract D-20261015-01..06 decision rows (utf-8 file out)
import io
import subprocess

G = r'C:/Users/sjs20/Desktop/FluxGroup'
r = subprocess.run(['git', '-C', G, 'show', 'origin/main:docs/decisions.md'],
                   capture_output=True, timeout=60)
t = r.stdout.decode('utf-8', errors='replace')
lines = t.split('\n')
out = []
for n, ln in enumerate(lines):
    if 'D-20261015-0' in ln:
        for k in range(max(0, n - 1), min(len(lines), n + 6)):
            out.append('L%d: %s' % (k + 1, lines[k].rstrip()))
        out.append('---')
io.open('_r1017bma_d02_rows.txt', 'w', encoding='utf-8', newline='').write('\n'.join(out))
print('rows written:', len(out))
