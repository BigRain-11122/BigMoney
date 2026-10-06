# -*- coding: utf-8 -*-
# r772 bm-a: dump W156 WAVE_CONFIGS entry + materializer block + PASS region for the
# W157 freeze-edits value-map source; check bare-155/156 contexts
import io

n1 = io.open(r'scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()

# WAVE_CONFIGS entry: from '156: {"batch"' to the entry-closing '},'
k = n1.find('156: {"batch"')
m = n1.find('"engine_owner": "bm-a"},', k)
entry = n1[k:m + len('"engine_owner": "bm-a"},')]
io.open(r'results/_r772bma_w157_src_entry.txt', 'w', encoding='utf-8', newline='').write(entry)
print('entry chars =', len(entry))
print('bare 155 in entry:', entry.count('155'), '| bare 156 in entry:', entry.count('156'))

# materializer block: from the W156 marker to the second T-141 marker
w = n1.find('# --- W156 materializer face')
t2 = n1.find('# --- T-141 s2 lane face', w)
assert 0 < w < t2
block = n1[w:t2]
io.open(r'results/_r772bma_w157_src_block.txt', 'w', encoding='utf-8', newline='').write(block)
print('block chars =', len(block))
print('bare 155 in block:', block.count('155'), '| bare 156 in block:', block.count('156'))
import re
for mm in re.finditer(r'155', block):
    s = max(0, mm.start() - 30)
    print('  155 ctx:', repr(block[s:mm.start() + 10]))

# PASS snippet region
p = n1.find('_r769bma_w156_band_gate.json, law sec.4 W156 row')
assert p > 0
io.open(r'results/_r772bma_w157_src_pass.txt', 'w', encoding='utf-8', newline='').write(n1[p - 700:p + 200])
print('pass region dumped')
