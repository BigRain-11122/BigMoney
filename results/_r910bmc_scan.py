# -*- coding: utf-8 -*-
"""debug: run builder REP logic in-memory, print r908 contexts post-cut."""
import importlib.util, re, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
t = open(os.path.join(ROOT, 'research', 'PERPETUAL_N1_W213_PREREG.md'), encoding='utf-8').read()
eol = '\r\n' if t.count('\r\n') > (t.count('\n') - t.count('\r\n')) else '\n'
spec = importlib.util.spec_from_file_location('b', os.path.join(ROOT, 'results', '_r910bmc_w214_prereg_build.py'))
# cannot import directly (it executes); instead re-extract REP by exec with a stub that skips write
src = open(os.path.join(ROOT, 'results', '_r910bmc_w214_prereg_build.py'), encoding='utf-8').read()
# cut the file at the REP application loop so we can grab REP only
i = src.find('for i, (old, new, expect) in enumerate(REP):')
exec(src[:i], globals())
for i, (old, new, expect) in enumerate(REP):
    c = t.count(old)
    assert c == expect, f'REP[{i}] count {c} != {expect}'
    t = t.replace(old, new, 1)
marker = '## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011'
pos = t.find(marker)
print('marker pos:', pos)
t2 = t[:pos]
print('pre-cut r908:', t.count('r908'), ' post-cut r908:', t2.count('r908'))
for m in re.finditer('r908', t2):
    s = max(0, m.start() - 70)
    print('---')
    print(t2[s:m.start() + 70].replace('\n', ' | '))
