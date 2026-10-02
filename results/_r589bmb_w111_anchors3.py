# -*- coding: utf-8 -*-
"""r589 bm-b W111 anchor dump 3: W110 selftest leg tail + following face (read-only)."""
t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
m = t2.find('# --- W110 materializer face')
print('W110 leg comment at', m)
# what precedes the leg?
print('=== 500 chars before W110 leg ===')
print(repr(t2[m-500:m]))
print()
# find the end of the W110 leg: the next '    # ---' face comment after m
import re
faces = [(mm.start(), t2[mm.start():mm.start()+80].split('\n')[0]) for mm in re.finditer(r'    # --- ', t2)]
after = [(p, s) for p, s in faces if p > m]
print('=== next face comments after W110 leg ===')
for p, s in after[:6]:
    print(p, repr(s))
# dump the region right after the W110 leg's finally/_set_wave(2)
fw = t2.find('finally', m)
sw = t2.find('_set_wave(2)', fw)
print('=== region after W110 leg _set_wave(2) ===')
print(repr(t2[sw:sw+400]))
