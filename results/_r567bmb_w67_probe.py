# -*- coding: utf-8 -*-
"""Pre-probe W67+ projection positions (reserved-universe scan) for the W66 canon row.
Excludes the W66 candidate itself (it is the candidate being frozen this window)."""
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
    if wnum == 66:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

w67_a = (177_004, 179_003)
w67_b = (50_201, 50_400)
a_hits = sorted(p for p in points if w67_a[0] <= p <= w67_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w67_a)]
b_hits = sorted(p for p in points if w67_b[0] <= p <= w67_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w67_b)]
print("W67+ A 177_004..179_003 ->", "CLEAN" if not a_hits else f"REFUSED {a_hits}")
print("W67+ B 50_201..50_400 ->", "CLEAN" if not b_hits else f"REFUSED {b_hits}")
if b_hits:
    lo = w67_b[0]
    while True:
        hi = lo + 200 - 1
        hits = sorted(p for p in points if lo <= p <= hi)
        band_hit = [b for b in bands + actual if overlaps((lo, hi), b)]
        if not hits and not band_hit:
            print(f"W67+ B first clean window -> {lo}..{hi}")
            break
        lo = (max(hits) + 1) if hits else lo + 200
