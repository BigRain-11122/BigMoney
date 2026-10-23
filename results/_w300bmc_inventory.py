# -*- coding: utf-8 -*-
import io, re, collections
t = io.open('results/_w300bmc_w299_frozen_face.txt', encoding='utf-8').read().replace('\r\n', '\n')
lines = []
for lit in ['651,320', '653,520', '655,720', '1,075,541', '1,077,741', '1,079,941', '1,082,141',
            '2,200', '0.24514361', '0.24514167', '0.3200', '0.3030', '0.3191', '0.3017']:
    lines.append('%-14s %d' % (lit, t.count(lit)))
lines.append('--- wave tokens ---')
cnt = collections.Counter(re.findall(r'W\d{3}', t))
for k in sorted(cnt):
    lines.append('%s %d' % (k, cnt[k]))
lines.append('--- band tokens ---')
bt = collections.Counter(re.findall(r'\d{3}_\d{3}', t))
for k in sorted(bt):
    lines.append('%s %d' % (k, bt[k]))
lines.append('--- lowercase wave ids ---')
for k in sorted(collections.Counter(re.findall(r'(?:n1_w\d{3}|_w\d{3}bmc_)', t))):
    lines.append('%s %d' % (k, collections.Counter(re.findall(r'(?:n1_w\d{3}|_w\d{3}bmc_)', t))[k]))
io.open('results/_w300bmc_inventory.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')