# -*- coding: utf-8 -*-
import io
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
i = n1.find('# --- W199 materializer face')
j = n1.find('    _set_wave(2)', i)
frag = n1[i:j]
k = frag.find('--no-verify; self-ack')
print('=== MAT199 archive region ===')
print(frag[max(0, k-250):k+850])
print()
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
i2 = pf.find('# W199 (bm-a r919 freeze')
endm = '"engine_owner": "bm-a"},'
j2 = pf.find(endm, i2)
pffrag = pf[i2:j2 + len(endm)]
k2 = pffrag.find('self-ack')
print('=== PF199 archive region ===')
print(pffrag[max(0, k2-150):k2+750])
