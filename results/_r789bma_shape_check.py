# -*- coding: utf-8 -*-
import io
n1 = io.open(r'scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
i = n1.find('"engine_owner": "bm-a"},', n1.find('162: {"batch"'))
print('ENTRY CLOSE:', repr(n1[i:i+120]))
pf = io.open(r'scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
j = pf.find('"engine_owner": "bm-a"},', pf.find('162: {"a": (371_204'))
print('PF CLOSE:', repr(pf[j:j+60]))
k = n1.find('"r787 bm-a] "')
print('CLAIM END:', repr(n1[k:k+80]))
w = n1.find('# --- W162 materializer face')
t = n1.find('# --- T-141 s2 lane face', w)
print('MAT ANCHORS:', w > 0, t > w)
# EOL dominance in the three faces
for tag, a, b in (('pfblk', pf.find('    # W162 (bm-a r787 freeze'), None),):
    pass
blk_pf = pf[pf.find('    # W162 (bm-a r787 freeze'): pf.find('"engine_owner": "bm-a"},', pf.find('162: {"a": (371_204')) + len('"engine_owner": "bm-a"},')]
print('pf_blk CRLF:', blk_pf.count('\r\n'), 'LF-only:', blk_pf.count('\n') - blk_pf.count('\r\n'))
