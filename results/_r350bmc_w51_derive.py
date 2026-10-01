# r350 bm-c: W51 band derivation probe -- A arithmetic (W50 A end + 1) and
# B forced-scan first clean window past the 46_000 refusal fact (r535 law:
# derive, never prose-copy; W43/W39-B skip family precedent).
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WIDTH_A, WIDTH_B = 2_000, 200
N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 51:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None, p
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None, f"band {b}"
    return (lo, hi), None

# A: arithmetic from W50 A end
ar_a = (N1_BANDS[50]["a"][1] + 1, N1_BANDS[50]["a"][1] + WIDTH_A)
a_win, a_blk = clean(ar_a[0], WIDTH_A)
print(f"A arithmetic {ar_a[0]}..{ar_a[1]} -> {'CLEAN' if a_win else 'REFUSED blocker=' + str(a_blk)}")
# B: arithmetic from W50 B end (expected REFUSED @46_000) then scan-forward
ar_b = (N1_BANDS[50]["b_exit"][1] + 1, N1_BANDS[50]["b_exit"][1] + WIDTH_B)
b_win, b_blk = clean(ar_b[0], WIDTH_B)
print(f"B arithmetic {ar_b[0]}..{ar_b[1]} -> {'CLEAN' if b_win else 'REFUSED blocker=' + str(b_blk)}")
start = ar_b[0]
first_b = None
for _ in range(200):
    win, blk = clean(start, WIDTH_B)
    if win:
        first_b = win
        break
    if isinstance(blk, int):
        start = blk + 1
    else:
        print(f"UNEXPECTED band blocker at {start}: {blk}")
        break
print(f"B first clean window (scan-forward): {first_b}")
# W52+ projection from the derived W51
if first_b:
    w52_a = (a_win[1] + 1, a_win[1] + WIDTH_A)
    w52_b = (first_b[1] + 1, first_b[1] + WIDTH_B)
    w52_a_win, w52_a_blk = clean(w52_a[0], WIDTH_A)
    w52_b_win, w52_b_blk = clean(w52_b[0], WIDTH_B)
    print(f"W52+ projection: A {w52_a[0]}..{w52_a[1]} -> {'CLEAN' if w52_a_win else 'REFUSED ' + str(w52_a_blk)}; "
          f"B {w52_b[0]}..{w52_b[1]} -> {'CLEAN' if w52_b_win else 'REFUSED ' + str(w52_b_blk)}")
