# -*- coding: utf-8 -*-
import io, re

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
m252 = re.search(r'252: \{"batch": "PERPETUAL-N1-W252"', n1t)
seg = n1t[m252.start():m252.start() + 9000]
if '253: {' in seg:
    seg = seg[:seg.find('253: {')]

for m in re.finditer(r'569701', seg):
    s = max(0, m.start() - 80)
    print('CTX-A:', seg[s:m.start() + 120].replace('\n', '\\n')[:220])
    print()

for m in re.finditer(r'seed_admit', seg):
    s = m.start()
    print('ADMIT-CTX:', seg[s:s + 160].replace('\n', '\\n')[:220])
    print()

# whole-file count for the W251-style verbatim lines
print('whole-file count base=569701 span=2000:', n1t.count('base=569701 span=2000'))
print('whole-file count base=571701 span=200:', n1t.count('base=571701 span=200'))
