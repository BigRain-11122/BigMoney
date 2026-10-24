# -*- coding: utf-8 -*-
"""Drop zero-hit legacy keys from the W311 derive NUM map (r1200)."""
import io

p = 'results/_w311bmc_prereg_derive.py'
s = io.open(p, encoding='utf-8').read()
drop = ['675,520', '0.3234', '0.24512185', '\u22120.09281744', '0.0040',
        '1.2001', '\u7b2c 307 \u679a', '\u6ce2\u53f7 307=',
        '\u884c 298 \u6ce8\u518c\u5728\u518c', 'bmc_rows=127',
        'bmc live rows 127', '\u7b2c 128 \u679a',
        '\u7b2c\u4e00\u767e\u4e8c\u5341\u4e03\u679a', '\u5f15\u64ce\u7ebf\u7b2c 299 \u6ce2',
        '\u4e09\u767e\u96f6\u4e09\u9762', 'CLEAN-AT-BIRTH 40th gen',
        '--wave 309', 'n1_w308', '_w308bmc_', '2da27a4a3a',
        '\u7b2c\u516d\u5341\u4e8c\u6b21', '13:2x', '14:0x', '13:4x']
lines = s.split('\n')
out = []
for ln in lines:
    if ln.strip().startswith('(') and ln.rstrip().endswith('),'):
        if any(('"%s"' % d) in ln for d in drop):
            continue
    out.append(ln)
io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('dropped lines:', len(lines) - len(out))