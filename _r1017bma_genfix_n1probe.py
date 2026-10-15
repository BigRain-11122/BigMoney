# -*- coding: utf-8 -*-
# r1017 bm-a scratch: locate n1_w245 / n1w245 residuals in T2
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
for pat in ('n1_w245', 'n1w245', 'n1_w244'):
    hits = [m.start() for m in re.finditer(re.escape(pat), T2)]
    print(pat, 'T2 count:', len(hits))
    for h in hits:
        ls = T2.rfind('\n', 0, h) + 1
        print('   ', repr(T2[ls:ls + 120]))
