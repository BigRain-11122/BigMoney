# -*- coding: utf-8 -*-
import io
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
out = io.open('results/_r885bma_w187_anchor_probe.txt', 'w', encoding='utf-8')
for pf in ('research/PERPETUAL_N1_W185_PREREG.md', 'research/PERPETUAL_N1_W186_PREREG.md'):
    t = io.open(pf, encoding='utf-8', newline='').read()
    i = t.find('起稿窗实况')
    out.write('==== %s ====\n%s\n\n' % (pf, t[i:i+560]))
out.close()
print('written')
