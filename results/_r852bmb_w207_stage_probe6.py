# -*- coding: utf-8 -*-
# r852 probe6: W204 owner mirror check (pf N1_BANDS vs n1 WAVE_CONFIGS) + pf row 204 bytes
import io, re

pf = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')
n1 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')

i = pf.find('204: {"a"')
print('pf N1_BANDS[204] row bytes:')
print(repr(pf[i:i+200]))

# WAVE_CONFIGS[204] owner line
j = n1.find('204: {"batch"')
seg = n1[j:j+20000]
k = seg.find('"engine_owner"')
print()
print('n1 WAVE_CONFIGS[204] owner bytes:')
print(repr(seg[k-120:k+80]))

# and 203 for comparison
j3 = n1.find('203: {"batch"')
seg3 = n1[j3:j3+20000]
k3 = seg3.find('"engine_owner"')
print()
print('n1 WAVE_CONFIGS[203] owner bytes:')
print(repr(seg3[k3-60:k3+80]))
