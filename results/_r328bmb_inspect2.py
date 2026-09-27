# -*- coding: utf-8 -*-
"""r328 resolve2 part B: full header line diff + archive preservation check + r328 line absence."""
import subprocess

def blob(sha):
    return subprocess.run(['git', 'cat-file', 'blob', sha], capture_output=True).stdout

out = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True).stdout
files = {}
for l in out.strip().splitlines():
    p = l.split()
    files.setdefault(p[3], {})[int(p[2])] = p[1]

c2 = blob(files['CODELY.md'][2]).decode('utf-8').splitlines()
c3 = blob(files['CODELY.md'][3]).decode('utf-8').splitlines()
s2 = set(c2)

# my r328 line must be absent from ours
r328 = [l for l in c3 if 'r328 bm-b' in l and 'BOM' in l]
print('r328 line found in theirs:', len(r328), '| present in ours:', bool(r328 and r328[0] in s2))

# show ours' full header line (the O-ONLY edited one)
for l in c2:
    if l.startswith('- 坑律正典全量归档'):
        print('OURS HEADER FULL:')
        print(l)
print()
for l in c3:
    if l.startswith('- 坑律正典全量归档'):
        print('THEIRS HEADER FULL:')
        print(l)

# check removed index lines are preserved in the archive file (comes with 644594be)
arch = subprocess.run(['git', 'show', '644594be:research/memory-archive/202609.md'],
                      capture_output=True).stdout.decode('utf-8', errors='replace')
for probe in ['十一批', '十二批', '十三批', '十四批', '十五批', 'r327 bm-b']:
    print('archive contains %r:' % probe, probe in arch)
# also verify the r326 pandas line presence on both sides
pandas2 = [l for l in c2 if 'pandas 3.x DatetimeIndex.asi8' in l]
pandas3 = [l for l in c3 if 'pandas 3.x DatetimeIndex.asi8' in l]
print('r326 pandas line: ours', len(pandas2), 'theirs', len(pandas3))
# resulting size if ours + my r328 line
merged = c2 + r328
size = len(('\n'.join(merged) + '\n').encode('utf-8'))
print('resolved CODELY size with r328 line:', size, 'bytes (<10240:', size < 10240, ')')
