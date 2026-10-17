# -*- coding: utf-8 -*-
# r1068 bm-c: W262 pre-sixgate face probe (verify registration faces in spliced n1)
import io

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
needle_row = '262: {"batch": "PERPETUAL-N1-W262"'
print('wave262 row:', needle_row in t)
print('fam A:', t.count('base=591701 span=2000'), 'fam B:', t.count('base=593701 span=200'))
print('out name:', 'n1_w262_results.json' in t)
print('subdir:', 'n1_w262' in t)
i = t.find('261: {"batch": "PERPETUAL-N1-W261"')
seg = t[i:i + 9000]
if '262: {' in seg:
    seg = seg[:seg.find('262: {')]
print('w261 seg has 589501:', '589501' in seg, '591501:', '591501' in seg)
