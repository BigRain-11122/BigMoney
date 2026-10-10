# -*- coding: utf-8 -*-
# r846 bm-c: extract W204 prereg §7/§8 backfill as template for W206 mechanical backfill
import io, re
t = io.open('research/PERPETUAL_N1_W204_PREREG.md', encoding='utf-8').read()
heads = [(m.start(), m.group(0)) for m in re.finditer(r'^## .+$', t, re.M)]
out = []
for i, (pos, h) in enumerate(heads):
    if '7' in h and '实证' in h or '8' in h and '复盘' in h:
        end = heads[i + 1][0] if i + 1 < len(heads) else len(t)
        out.append(t[pos:end])
io.open('results/_r846bmc_w204_s78_extract.txt', 'w', encoding='utf-8').write('\n\n=====\n\n'.join(out))
print('sections found:', len(out), 'bytes:', sum(len(s) for s in out))
