# -*- coding: utf-8 -*-
# r772 bm-a: extract current W156 anchors from pf.py / n1.py for the W157 freeze edits
import io

pf = io.open(r'scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
i = pf.find('156: {')
assert i > 0
j = pf.find('}', pf.find('engine_owner', i))
print('--- pf.py W156 row region ---')
print(repr(pf[i - 20:j + 10]))

n1 = io.open(r'scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
k = n1.find('156: {"batch"')
assert k > 0
m = n1.find('engine_owner": "bm-a"},', k)
assert m > 0
print('n1 W156 entry chars', k, '..', m)
print('--- n1.py W156 entry head 500 ---')
print(repr(n1[k:k + 500]))
print('--- n1.py W156 entry tail region ---')
print(repr(n1[m - 60:m + 90]))
# what follows the W156 entry (dict close?)
print('--- after W156 entry ---')
print(repr(n1[m + 20:m + 140]))
# materializer face anchor: the _set_wave(156) block and T-141 boundary
w = n1.find('_set_wave(156)')
assert w > 0
t = n1.find('# --- T-141 s2 lane face')
print('--- _set_wave(156) region ---')
print(repr(n1[w - 100:w + 120]))
print('--- T-141 boundary region ---')
print(repr(n1[t - 160:t + 40]))
# PASS snippet region: r771 a4 face
p = n1.find('r771 bm-a]')
print('--- PASS snippet region (r771 bm-a] tail) ---')
print(repr(n1[p - 200:p + 120]) if p > 0 else 'r771 bm-a] NOT FOUND')
p2 = n1.find('_r769bma_w156_band_gate.json, law sec.4 W156 row')
print('--- a4-anchor candidate ---')
print(repr(n1[p2 - 100:p2 + 260]) if p2 > 0 else 'a4 anchor not found')
