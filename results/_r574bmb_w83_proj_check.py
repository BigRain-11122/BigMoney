# -*- coding: utf-8 -*-
"""r574 bm-b: W83+ projection pre-check (canon row prose must be machine-derived, r335 law)."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= {(40_000, 40_001)[0], (40_000, 40_001)[1]}
points |= {31_000, 31_500, 32_000}
points |= set(range(70_000, 70_006))
points |= {95_000, 95_001, 95_002, 95_003}
w83_a = (209_004, 211_003)
w83_b = (54_401, 54_600)
a_hits = sorted(p for p in points if w83_a[0] <= p <= w83_a[1])
b_hits = sorted(p for p in points if w83_b[0] <= p <= w83_b[1])
print('W83+ A 209_004..211_003 hits:', a_hits)
print('W83+ B 54_401..54_600 hits:', b_hits)

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])
for w, cfg in N1_BANDS.items():
    for key in ('a', 'b_exit'):
        if overlaps(tuple(cfg[key]), w83_a):
            print('W83+ A overlap W%d.%s' % (w, key))
        if overlaps(tuple(cfg[key]), w83_b):
            print('W83+ B overlap W%d.%s' % (w, key))
for nm, rng in (('lfc', (30_000, 30_099)), ('options', (63_000, 63_049))):
    if overlaps(rng, w83_a):
        print('W83+ A overlap', nm)
    if overlaps(rng, w83_b):
        print('W83+ B overlap', nm)
for nm, bb in (('v1', [(10_000, 10_099), (20_000, 20_019)]),
               ('w1ext', [(10_100, 12_099), (20_100, 20_299)])):
    for r in bb:
        if overlaps(r, w83_a):
            print('W83+ A overlap', nm, r)
        if overlaps(r, w83_b):
            print('W83+ B overlap', nm, r)
print('check done')
