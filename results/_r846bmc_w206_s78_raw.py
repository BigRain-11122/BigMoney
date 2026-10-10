# -*- coding: utf-8 -*-
# r846: dump W206 prereg §7/§8 raw for precise replace
import io, re
t = io.open('research/PERPETUAL_N1_W206_PREREG.md', encoding='utf-8').read()
heads = [(m.start(), m.group(0)) for m in re.finditer(r'^## .+$', t, re.M)]
parts = {}
for i, (pos, h) in enumerate(heads):
    end = heads[i + 1][0] if i + 1 < len(heads) else len(t)
    if '7' in h and '实证' in h:
        parts['s7'] = t[pos:end]
    if '8' in h and '复盘' in h:
        parts['s8'] = t[pos:end]
io.open('results/_r846bmc_w206_s78_raw.txt', 'w', encoding='utf-8').write(
    '---S7---\n' + parts['s7'] + '\n---S8---\n' + parts['s8'] + '\n---END---\n')
print('s7 bytes:', len(parts['s7']), 's8 bytes:', len(parts['s8']))
