# -*- coding: utf-8 -*-
# r600 ring pre-check: current dirty set vs origin delta intersection
import io, sys, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()


theirs = set(run('git', 'diff', '--name-only', '--no-renames', 'HEAD...origin/main').split('\n')) - {''}
st = run('git', 'status', '--porcelain')
dirty = set()
for l in st.split('\n'):
    if not l.strip():
        continue
    p = l[3:].strip()
    dirty.add(p)
print('theirs n=', len(theirs), ' dirty n=', len(dirty))
inter = sorted(dirty & theirs)
print('dirty^theirs:', inter)
for f in sorted(theirs):
    print('TH|', f)
