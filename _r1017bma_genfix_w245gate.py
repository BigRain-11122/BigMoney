# -*- coding: utf-8 -*-
# r1017 bm-a scratch: locate w<245 instances in T2
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
# apply block replacements like the gen does (OLD/NEW) -- up to the precise gates
seg2 = src.split('# ---------- post gates')[0]
idx = seg2.find('# ---------- Phase-A inline')
exec(seg2[idx:], ns)  # defines OLD/NEW + applies? no -- check
print('T2 w<245 count:', T2.count('w<245'))
for m in re.finditer('w<245', T2):
    ls = T2.rfind('\n', 0, m.start()) + 1
    print('@%d: %r' % (m.start(), T2[ls:ls + 140]))
print('T1 w<244 count:', T1.count('w<244'), 'T1 w<245 count:', T1.count('w<245'))
for m in re.finditer('w<244', T1):
    ls = T1.rfind('\n', 0, m.start()) + 1
    print('T1 w<244 @%d: %r' % (m.start(), T1[ls:ls + 140]))
