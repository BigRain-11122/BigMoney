# -*- coding: utf-8 -*-
"""r589 bm-b W111 freeze-window anchor inspection (read-only)."""
t = open('scripts/perpetual_faces.py', encoding='utf-8').read()
i = t.find('110: {')
print('=== pf.py context before W110 row ===')
print(repr(t[i-700:i+120]))
print()
t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
j = t2.find('110: {"batch"')
print('=== n1.py W110 WAVE_CONFIGS entry ===')
print(repr(t2[j-60:j+640]))
print()
k = t2.count('W110 materializer face')
print('n1.py W110 materializer face count:', k)
m = t2.find('sec.4 W110 row')
print('=== n1.py summary segment anchor ===')
print(repr(t2[m-80:m+260]))
print()
lines = open('research/PERPETUAL_FACES.md', encoding='utf-8').read().splitlines()
for idx, ln in enumerate(lines):
    if ln.startswith('- N1 \u6ce2110\uff08'):
        print('canon W110 row at line', idx + 1, 'len', len(ln))
    if ln.startswith('- \u6bcf\u6ce2 finalize'):
        print('canon sec.5 anchor line', idx + 1, ':', repr(ln[:80]))
