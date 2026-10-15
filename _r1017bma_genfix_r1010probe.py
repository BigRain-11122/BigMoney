# -*- coding: utf-8 -*-
# r1017 bm-a scratch: locate residual r1010 in T2
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
for m in re.finditer('r1010', T2):
    ls = T2.rfind('\n', 0, m.start()) + 1
    print('@%d: %r' % (m.start(), T2[ls:ls + 170]))
print('--- T0 all r1010 ---')
for m in re.finditer('r1010', t0):
    ls = t0.rfind('\n', 0, m.start()) + 1
    print('@%d: %r' % (m.start(), t0[ls:ls + 150]))
