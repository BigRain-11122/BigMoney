# -*- coding: utf-8 -*-
import sys, re
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
n1 = open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
j = n1.find('    # --- W204 materializer face')
end = n1.find('    # --- T-141 s2 lane face', j)
mat = n1[j:end]
ci = mat.find('_set_wave(204)')
body = mat[ci:]
cfg = n1[n1.find('204: {"batch"'):]
cfg = cfg[:cfg.find('"engine_owner": "bm-c"},') + 24]

toks = ['463_604..465_603', '465_604..465_803', '463_204..465_203', '463_404..465_403',
        '463_604..463_803', '463_404..463_603', '465_604..467_603', '465_804..466_003',
        '463_604', '463_603', '465_604', '465_603', '463_403', '465_803', '467_803',
        'SIXTY-FOURTH', 'w203_a', 'w203_b', 'w < 204', 'range(16, 204)', 'range(17, 204)',
        'n1_w204', 'PERPETUAL-N1-W204', 'PERPETUAL_N1_W204_PREREG', 'W204', 'W203',
        'bm-a r936 freeze', 'b2bb60963', 'bm-c r837', '860,945', '444,520', 'W17..W203']
print('=== BODY counts ===')
for t in toks:
    print('%-32r %d' % (t, body.count(t)))
print('=== CFG counts ===')
for t in toks:
    print('%-32r %d' % (t, cfg.count(t)))
print('=== body residual W203 lines ===')
for m in re.finditer(r'.*W203.*', body):
    print('  L:', m.group(0).strip()[:120])
