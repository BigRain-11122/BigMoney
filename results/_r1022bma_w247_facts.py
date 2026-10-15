# -*- coding: utf-8 -*-
# r1022 bm-a: W247 pre-finalize fact extraction (boundary + argparse faces)
import io
import re

n1t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
m246 = re.search(r'246: \{"batch": "PERPETUAL-N1-W246"', n1t)
seg = n1t[m246.start():m246.start() + 8000]
if '247: {' in seg:
    seg = seg[:seg.find('247: {')]
print('w246 557501:', '557501' in seg, '| 542201:', '542201' in seg)

for line in n1t.splitlines():
    ls = line.strip()
    if 'add_argument' in ls and ('wave' in ls or 'finalize' in ls or 'choices' in ls):
        print('ARG:', ls[:170])
