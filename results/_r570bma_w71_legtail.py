# -*- coding: utf-8 -*-
# r570 bm-a: locate W71 leg end + what follows (W72 insertion anchor discovery)
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t.find('--- W71 materializer face')
seg = t[i:i+9000]
# find the end: the finally clause then what comes next
j = seg.find('finally:')
k = seg.find('_set_wave(2)', j)
tail = seg[k-40:k+600]
open('results/_r570bma_w71_legtail.txt', 'w', encoding='utf-8').write(
    '=== W71 leg finally tail + following 600 chars ===\n' + tail)
print('idx', i, 'tail at', k)
