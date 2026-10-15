# -*- coding: utf-8 -*-
# r1017 bm-a scratch: run gen transforms to T2 (pre-gates) and locate residual needles
import io, re, sys

src = io.open('results/_r1017bma_w246_gen.py', encoding='utf-8', newline='').read()
t0 = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
ns = {'__file__': r'results\_r1017bma_w246_gen.py'}
seg = src.split('# ---------- Phase-A inline')[0]
try:
    exec(seg, ns)
except SystemExit as e:
    print('floors raised:', e)
    sys.exit(1)
T1 = t0
for o, n in ns['CHAIN']:
    T1 = T1.replace(o, n)
T2 = ns['xf'](T1)
for pat in ['PERPETUAL_N1_W245', 'PERPETUAL_N1_W244']:
    for m in re.finditer(re.escape(pat), T2):
        ls = T2.rfind('\n', 0, m.start()) + 1
        print('%s @%d: %r' % (pat, m.start(), T2[ls:ls + 150]))
