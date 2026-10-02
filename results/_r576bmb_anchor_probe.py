# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'research'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, ROOT)
import science_gates
reg = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
arith_b = set(range(54_801, 55_001))
hits = sorted(arith_b & reg)
print('B arithmetic window 54_801..55_000 registry hits:', hits)
assert hits == [55_000], 'not single-point refusal!'
arith_a = set(range(213_004, 215_004))
print('A arithmetic window 213_004..215_003 registry hits:', sorted(arith_a & reg))
assert not (arith_a & reg)
w85_a = set(range(213_004, 215_004)); w85_b = set(range(55_001, 55_201))
import perpetual_faces as pf
for w, c in sorted(pf.N1_BANDS.items()):
    a = set(range(c['a'][0], c['a'][1] + 1)); b = set(range(c['b_exit'][0], c['b_exit'][1] + 1))
    assert not (w85_a & a) and not (w85_a & b), f'A collides W{w}'
    assert not (w85_b & a) and not (w85_b & b), f'B collides W{w}'
print('W85 bands disjoint vs all 82 registered rows: OK')
for probe in [95_000, 95_001, 95_002, 95_003, 70_000, 70_005, 40_000, 40_001, 31_000, 31_500, 32_000]:
    assert probe not in w85_a and probe not in w85_b, f'probe {probe} inside W85'
print('W85 clears probe cluster + N3-R1 + N2/N4 + N2-W15 points: OK')
print('PRE-VERIFY PASS')
