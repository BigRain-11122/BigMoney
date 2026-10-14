# -*- coding: utf-8 -*-
# r990 anchor probe for the W237 freeze editor derivation (read-only, zero writes)
import json
o = json.load(open('results/perpetual_faces/n1_w236_results.json', encoding='utf-8'))
led = (o.get('science_gates') or {}).get('ledger') or {}
print('ledger.total:', led.get('total'))
print('merged.n_values:', o['null_pool_cumulative']['merged']['n_values'])

n1 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')
pf = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')
NL = chr(10)
anchors_n1 = [
    '236: {"batch"',
    '    # --- W236 materializer face',
    '    # --- T-141 s2 lane face',
    '          "+ T-141 s2 ',
    'PREREG = WAVE_CONFIGS[2]["prereg"]',
    '# prior-wave disjointness W2..W236 (single state',
    '"a_seed_base": 534004',
    '"pre-run; design = frozen v1 null calibration verbatim, "',
    '"prereg": ("research/PERPETUAL_N1_W236_PREREG.md (wave-level frozen "',
]
for a in anchors_n1:
    print(n1.count(a), '|', a[:58])
print('---')
for a in ['    236: {"a"', '# v1 + ext(wave-1) in-use bands']:
    print(pf.count(a), '|', a[:58])
i = pf.find('    236: {"a"')
ls = pf.find(NL, i) + 1
le = pf.find(NL, ls)
print('owner line:', repr(pf[ls:le]))
# cfg close anchor shape (23 spaces? verify)
c = n1.find('PREREG = WAVE_CONFIGS[2]["prereg"]')
ls2 = n1.rfind(NL, 0, c) + 1
prev_line_start = n1.rfind(NL, 0, ls2 - 1) + 1
print('cfg close prev line:', repr(n1[prev_line_start:ls2]))
# W236 block parity span face
b0 = n1.find('    # --- W236 materializer face')
b1 = n1.find('    # --- T-141 s2 lane face')
blk = n1[b0:b1]
import re
m_first = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
print('parity span found:', bool(m_first), bool(m_disj), 'block bytes:', b1 - b0)
row_ls = blk.rfind(NL, 0, m_first.start()) + len(NL)
par_full = blk[row_ls:m_disj.start()]
ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_full)
print('par_full rows:', par_full.count('assert pf.N1_BANDS['), 'first/last:', ws[:2], ws[-4:])
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
print('m232 found:', bool(m232))
est = par_full[:m232.start()]
ews = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", est)
print('estate rows:', est.count('assert pf.N1_BANDS['),
      'head:', [int(x) for x in ews[:3]], 'tail:', [int(x) for x in ews[-6:]])
# engine shard identity face + engine daemon liveness
print('n1w236-0of12 count:', n1.count('n1w236-0of12'))
print('n1_w236 subdir count:', n1.count('"shard_subdir": "n1_w236"'))
