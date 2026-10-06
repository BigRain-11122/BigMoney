# -*- coding: utf-8 -*-
# r772 bm-a: dump the W156 materializer block + T-141 boundary for the W157 insertion anchor
import io

n1 = io.open(r'scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
w = n1.find('_set_wave(156)')
t = n1.find('# --- T-141 s2 lane face')
print('w =', w, 't =', t)
assert 0 < w < t
block = n1[w:t]
print('W156 materializer block chars:', len(block))
print('--- block head 300 ---')
print(repr(block[:300]))
print('--- block tail 500 ---')
print(repr(block[-500:]))
print('--- immediately before block ---')
print(repr(n1[w - 200:w]))
# PASS snippet: current tail after r771 a4 edit
p = n1.find('_r769bma_w156_band_gate.json, law sec.4 W156 row')
assert p > 0
print('--- PASS snippet region ---')
print(repr(n1[p - 700:p + 200]))
