# -*- coding: utf-8 -*-
import io
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
i = pf.find('155: {')
print('--- pf W155 row anchor ---')
print(repr(pf[i-8:i+100]))
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
j = n1.find('"shard_subdir": "n1_w155"')
print('--- n1 W155 CONFIGS tail ---')
print(repr(n1[j-40:j+150]))
anchor3 = '    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face'
print('--- materializer anchor count:', n1.count(anchor3))
s = n1.find('r768 bm-a]')
print('--- PASS snippet tail ---')
print(repr(n1[s-260:s+90]))
# W155 row in WAVE_CONFIGS PRE block start
k = n1.find('155: {"batch": "PERPETUAL-N1-W155"')
print('--- W155 WAVE_CONFIGS head ---')
print(repr(n1[k-40:k+120]))
# materializer leg W155 present (sanity)
print('--- W155 materializer leg present:', 'W155 materializer face' in n1)
print('--- W155 prereg-block wrap tail (paren-keep):')
seg = n1[k:k+8000]
t = seg.find('always on)"')
print(repr(seg[t:t+400]))
