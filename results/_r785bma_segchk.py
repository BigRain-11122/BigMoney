# -*- coding: utf-8 -*-
import io
n2 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
k2 = n2.find('161: {"batch"')
m2 = n2.find('"engine_owner": "bm-a"},', k2)
seg = n2[k2:m2]
i = seg.find('REGISTERED')
print(repr(seg[i:i+320]))
print('---')
print('has ee04482a2:', 'ee04482a2' in seg)
print('has 6ee1207bb:', '6ee1207bb' in seg)
print('count 161 batch:', n2.count('161: {"batch"'))
