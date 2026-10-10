# -*- coding: utf-8 -*-
# r852 probe5: module-name liveness in landed W205 block + prereg order citation bytes
import io, re

n1 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')
i = n1.find('    # --- W205 materializer face')
j = n1.find('    # --- T-141 s2 lane face', i)
blk = n1[i:j]
for name in ('reg_ints', 'v1_a', 'v1_b', 'w1_a', 'w1_b', 'probes', 'A_SEED_BASE', 'A_N',
             'B_N', 'B_EXIT_SEED_BASE', '_set_wave', '_entry_shard_of', 'SHARD_DIR', 'OUT',
             'PATHS', 'OUT_DIR', '_worker_init', 'lfc_actual12', 'options_actual12', 'pickle'):
    print(name, '->', blk.count(name))

pre = io.open('research/PERPETUAL_N1_W207_PREREG.md', encoding='utf-8').read()
for m in re.finditer(r'O-2026\d{4}-\d{4}[^,，】）\)]{0,30}', pre):
    s = m.group(0)
    if '2355' in s or '1410' in s or '1730' in s:
        print('CITE:', s[:60])
print('---')
# W205 cfg PRE 'own-series continuation' line bytes (pattern source for my cfg)
k = n1.find('"prereg": ("research/PERPETUAL_N1_W205_PREREG.md')
print(repr(n1[k-320:k+80]))
