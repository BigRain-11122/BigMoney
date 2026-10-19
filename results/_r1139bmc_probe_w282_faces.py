# -*- coding: utf-8 -*-
# r1139 bm-c: quick face probe for W282 sixgate authoring (read-only).
import io
import re

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t.find('282: {"batch": "PERPETUAL-N1-W282"')
print('wave282_row_idx', i)
seg = t[i:i + 9000]
if '283: {' in seg:
    seg = seg[:seg.find('283: {')]
for k in ['635701', '637701', 'n1_w282', 'n1_w282_results.json',
          '"engine_owner": "bm-c"']:
    print('face', k, k in seg)
print('setwave counts', {w: t.count('_set_wave(%d)' % w) for w in (282, 281, 280)})
p = t.rfind('_set_wave(281)')
aft = t[p + len('_set_wave(281)'):]
print('after281 has282', '_set_wave(282)' in aft,
      'has281', '_set_wave(281)' in aft, 'has280', '_set_wave(280)' in aft)
print('fam faces', t.count('law sec.4 W282 A: 635_701..637_700'),
      t.count('law sec.4 W282 B: 637_701..637_900'))
m = re.search(r'281: \{"batch": "PERPETUAL-N1-W281"', t)
s2 = t[m.start():m.start() + 9000]
if '282: {' in s2:
    s2 = s2[:s2.find('282: {')]
print('w281 boundary has 633501/635501', '633501' in s2, '635501' in s2)