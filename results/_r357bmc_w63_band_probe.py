# r357 bm-c: W63 band probe -- single-source derive of the first-clean B
# window past the refused arithmetic position (48_801..49_000 contains
# SEED_REGISTRY 49_000 p4_ext_tilt_q; 49_001..49_200 contains 49_100
# p4_ext_tilt_d20). Read-only; mirror of the W60 gate's reserved universe.
import os
import sys

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
WIDTH_A = 2_000
WIDTH_B = 200

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

print("registry keys:", sorted(N1_BANDS))
print("registry int values sorted (49000..51000 window):",
      sorted(p for p in points if 49_000 <= p <= 51_000))

# A side: arithmetic from W62 A end
arith_a = (N1_BANDS[62]["a"][1] + 1, N1_BANDS[62]["a"][1] + WIDTH_A)
a_hits = sorted(p for p in points if arith_a[0] <= p <= arith_a[1])
a_band_hits = [b for b in bands + actual if overlaps(b, arith_a)]
print("A arith %d..%d hits=%s bandhits=%s" % (
    arith_a[0], arith_a[1], a_hits, a_band_hits))

# B side: scan forward from the W62 B end + 1
lo = N1_BANDS[62]["b_exit"][1] + 1
for i in range(60):
    hi = lo + WIDTH_B - 1
    hits = sorted(p for p in points if lo <= p <= hi)
    bh = [b for b in bands + actual if overlaps(b, (lo, hi))]
    if not hits and not bh:
        print("B FIRST CLEAN: %d..%d (window #%d)" % (lo, hi, i + 1))
        break
    print("B window %d..%d REFUSED: points=%s bands=%s" % (lo, hi, hits, bh))
    lo = hi + 1
