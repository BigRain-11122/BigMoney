# -*- coding: utf-8 -*-
# r772 bm-a: dump the parity chain region verbatim (rows 140..155) + boundaries
import io

t = io.open(r'results/_r772bma_w157_src_block.txt', encoding='utf-8', newline='').read()
i = t.find('assert pf.N1_BANDS[140]')
j = t.find('assert pf.N1_BANDS[155]')
k2 = t.find('\r\n', t.find('r768', j)) if t.find('r768', j) > 0 else -1
print('i=', i, 'j=', j, 'k2=', k2, 'r768-after-155:', t.find('r768', j))
end = t.find('\r\n', j)
line155 = t[j:end]
print('--- W155 row assert line ---')
print(repr(line155))
print('--- chain head 300 ---')
print(repr(t[i:i + 300]))
print('--- pre-chain tail 200 ---')
print(repr(t[max(0, i - 200):i]))
print('--- post-W155-line head 400 ---')
print(repr(t[end:end + 400]))
import re
rows = re.findall(r'assert pf\.N1_BANDS\[(\d+)\]', t[i:end])
print('chain rows:', rows)
