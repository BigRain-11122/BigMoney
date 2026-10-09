# -*- coding: utf-8 -*-
import io
t = io.open(r'results\_r803bma_w167_probe_n1_entry.txt', encoding='utf-8', newline='').read()
for line in t.splitlines():
    if 'a_seed_base' in line or 'b_exit_seed_base' in line:
        print(repr(line))
p = io.open(r'results\_r803bma_w167_probe_pf_block.txt', encoding='utf-8', newline='').read()
for line in p.splitlines():
    if '166: {"a"' in line or 'engine_owner' in line:
        print(repr(line))
# also the mat header + W165-row chain tail + disjointness anchor shapes
m = io.open(r'results\_r803bma_w167_probe_n1_mat.txt', encoding='utf-8', newline='').read()
i = m.find('assert pf.N1_BANDS[165]')
print('CHAIN TAIL:', repr(m[i:i + 260]))
