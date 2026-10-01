import re, json
b = open('CODELY.md', 'rb').read().decode('utf-8')
lines = b.split('\n')
print('total lines:', len(lines), 'bytes:', len(b.encode('utf-8')))
# section headers
for i, l in enumerate(lines):
    if l.startswith('#') or l.startswith('## ') or l.startswith('### '):
        print(f'L{i+1}: {l[:80]}')
# entry distribution by prefix pattern
import collections
pat = collections.Counter()
for l in lines:
    if l.startswith('- ['):
        m = re.match(r'- \[([0-9\-]+ [0-9:x]+)? ?(r\d+)? ?(bm-[abc])?\]??', l)
        pat['entry'] += 1
    elif l.startswith('- 冷层指针'):
        pat['cold_ptr'] += 1
    elif l.startswith('### '):
        pat['h3'] += 1
print('entry line counts:', dict(pat))
# sizes of each section
secs = []
cur = ('preamble', 0)
for l in lines:
    if l.startswith('## ') or l.startswith('### '):
        secs.append(cur)
        cur = (l[:40], 0)
    cur = (cur[0], cur[1] + len(l.encode('utf-8')) + 1)
secs.append(cur)
for name, size in secs:
    print(f'{size:>8}  {name}')
