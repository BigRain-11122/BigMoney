# -*- coding: utf-8 -*-
"""Pre-probe W66+ projection positions (reserved-universe scan) for the W65 canon row."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 65:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

w66_a = (175_004, 177_003)
w66_b = (49_801, 50_000)
a_hits = sorted(p for p in points if w66_a[0] <= p <= w66_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w66_a)]
b_hits = sorted(p for p in points if w66_b[0] <= p <= w66_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w66_b)]
print("W66+ A 175_004..177_003 ->", "CLEAN" if not a_hits else f"REFUSED {a_hits}")
print("W66+ B 49_801..50_000 ->", "CLEAN" if not b_hits else f"REFUSED {b_hits}")
