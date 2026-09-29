# r441 bm-a probe 2: verify cluster-collapse numbers + seed three-step law for FV batch
import json
import subprocess

d = json.load(open('results/gate_timing_prescreen_a158.json', encoding='utf-8'))
print('=== 588000 accept-7 oos_excess (cluster collapse inputs, landed face) ===')
gates7 = ['RESI60_q90', 'STD10_q90', 'STD20_q90', 'SUMN10_q10', 'VSUMD10_q90', 'VSUMD20_q90', 'VSUMD30_q90']
for g in gates7:
    c = d['cells']['588000|%s' % g]
    print('588000|%s excess=%+.4f oos_sharpe=%.4f entries=%d' % (
        g, c['oos_excess_vs_bh'], c['OOS']['sharpe'], c['OOS']['entries']))
pairs = d['d6']['intra_library_disclosure']['588000']['pairs']
print('=== accept-7 intra pairs >= 0.60 (588000) ===')
acc = set(gates7)
for k, v in pairs.items():
    a, b = k.split('|')
    if a in acc and b in acc and abs(v) >= 0.6:
        print('  %s = %.4f' % (k, v))
print()
print('=== 510300/510500 accept intra pairs ===')
for m, gs in [('510300', ['RANK30_q90', 'STD20_q90']),
              ('510500', ['CNTN20_q10', 'RANK30_q90', 'RSQR10_q90', 'SUMN10_q10'])]:
    pm = d['d6']['intra_library_disclosure'][m]['pairs']
    for k, v in pm.items():
        a, b = k.split('|')
        if a in gs and b in gs:
            print('  %s %s = %.4f' % (m, k, v))

print()
print('=== seed three-step law: 20313000 / 20313500 ===')
import sys
sys.path.insert(0, 'scripts')
import science_gates as sg
vals = [int(v) for v in sg.SEED_REGISTRY.values()]
for cand in (20313000, 20313500):
    print('cand %d: key-collision=%s value-collision=%s' % (
        cand, cand in [20312500], cand in vals))
# first elements of default_rng(base) vs all registry bases
import numpy as np
existing_first = {}
for k, v in sg.SEED_REGISTRY.items():
    existing_first[k] = int(np.random.default_rng(int(v)).integers(2**31))
for cand in (20313000, 20313500):
    f = int(np.random.default_rng(cand).integers(2**31))
    clashes = [k for k, fv in existing_first.items() if fv == f]
    print('cand %d first-element=%d clash-with=%s' % (cand, f, clashes or 'none'))
