# -*- coding: utf-8 -*-
# r1046 bm-c heal check v2: scan FULL W250 block (to W251 marker / EOF).
import hashlib
import io

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t.find('250: {"batch": "PERPETUAL-N1-W250"')
j = t.find('251: {', i)
seg = t[i:j if j > 0 else i + 60000]
print('block len:', len(seg))
for l in seg.splitlines():
    if any(k in l for k in ('68', '69', 'print', 'rows')):
        print('  ', l.strip()[:160])

# also search the whole file for the disclosed "68" faces near W250 markers
print('---global 68/69 prints---')
for l in t.splitlines():
    if 'print' in l and ('68' in l or '69' in l):
        print('  ', l.strip()[:160])
