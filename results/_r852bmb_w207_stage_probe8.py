# -*- coding: utf-8 -*-
# r852 probe8: final W204 owner check (decisive)
n1 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')
i = n1.find('205: {"batch"')
seg = n1[i - 140:i]
w = seg[seg.rfind('"engine_owner"'):]
print('W204 cfg owner line:', w.strip()[:44])
pf = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')
j = pf.find('204: {"a"')
print('W204 pf owner line:', pf[j:j + 130].split('\n')[1].strip())
