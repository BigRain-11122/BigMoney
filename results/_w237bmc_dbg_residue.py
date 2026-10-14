# -*- coding: utf-8 -*-
"""r990 residue-context probe: exec derive head (facts+SUBs+apply), dump residue contexts."""
import io

src = io.open('results/_w237bmc_prereg_derive.py', encoding='utf-8').read()
cut = src.index('# ---------- forbidden-residue scan ----------')
head = src[:cut]
g = {}
exec(compile(head, 'derive_head', 'exec'), g)
out = g['out']
tpl = g['tpl']
for needle in ['536_004..536_203', '_w236bma', '938,589']:
    print('====', needle, 'out_count=', out.count(needle), 'tpl_count=', tpl.count(needle))
    i = out.find(needle)
    while i >= 0:
        print('OUT@%d: %s' % (i, out[max(0, i - 120):i + len(needle) + 120].replace('\n', ' | ')))
        i = out.find(needle, i + 1)
