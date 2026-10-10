# -*- coding: utf-8 -*-
# r852 probe2: actual bytes around the two suspect anchors
import io

n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()

i = n1.find('PREREG = WAVE_CONFIGS[2]["prereg"]')
print('=== n1 bytes around PREREG line (idx', i, ') ===')
print(repr(n1[i-260:i+80]))

# N1_BANDS dict close in pf: find the tail comment
j = pf.find('# v1 + ext(wave-1) in-use bands')
print()
print('=== pf bytes around tail comment (idx', j, ') ===')
print(repr(pf[j-300:j+60]))

# W205 row owner line context in pf
k = pf.find('205: {"a"')
print()
print('=== pf W205 row (idx', k, ') ===')
print(repr(pf[k-20:k+260]))

# estate end: bytes just before the 204-row-leg
m = n1.find('        assert pf.N1_BANDS[204] == {')
print()
print('=== n1 bytes before 204-row-leg (idx', m, ') ===')
print(repr(n1[m-200:m+120]))
print()
print('n1 file size:', len(n1.encode('utf-8')), '| pf size:', len(pf.encode('utf-8')))
