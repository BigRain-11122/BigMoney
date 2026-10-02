# -*- coding: utf-8 -*-
"""Pre-probe W68+ projection positions (reserved-universe scan) for the W67 canon row.
Tree state: W66 registered (bm-c r359). W67 candidate (bm-b r567) excluded from scan.
r302/r335 law: projection = machine derive, prose is only the carrier."""
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
    if wnum == 67:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

w67_a = (177_004, 179_003)   # verify candidate window CLEAN (W66 A end + 1)
w67_b = (50_201, 50_400)    # verify candidate window CLEAN (W66 B end + 1)
w68_a = (179_004, 181_003)
w68_b = (50_401, 50_600)
for tag, w in (("W67 A", w67_a), ("W67 B", w67_b), ("W68+ A", w68_a), ("W68+ B", w68_b)):
    hits = sorted(p for p in points if w[0] <= p <= w[1]) or [
        f"band {b}" for b in bands + actual if overlaps(b, w)]
    print(f"{tag} {w[0]}..{w[1]} ->", "CLEAN" if not hits else f"REFUSED {hits}")
