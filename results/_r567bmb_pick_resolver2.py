# -*- coding: utf-8 -*-
"""marks-20261002.jsonl: new file both sides (no base) -> union = origin lines + my unique lines."""
import subprocess, json

def show(rev, path):
    return subprocess.check_output(['git', 'show', f'{rev}:{path}'], errors='replace')

p = 'results/paper/marks/marks-20261002.jsonl'
mine_lines = show('d7a1be6fb', p).splitlines()
orig_lines = show('ed52184e6', p).splitlines()
orig_set = set(orig_lines)
merged = list(orig_lines) + [l for l in mine_lines if l not in orig_set]
out = '\n'.join(merged) + ('\n' if merged else '')
assert '<<<<<<<' not in out and '>>>>>>>' not in out
for l in merged:
    if l.strip():
        json.loads(l)
open(p, 'wb').write(out.encode('utf-8'))
print(f'marks union: origin {len(orig_lines)} + mine-new {len([l for l in mine_lines if l not in orig_set])} = {len(merged)} lines')
print('RESOLVER2_OK')
