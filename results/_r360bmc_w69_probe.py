# -*- coding: utf-8 -*-
"""r360 bm-c W69 draft-window probe (pre-freeze machine derive).

W69 = my published seat (MSG-20261002-1015-bmc, published=reserved r518-1).
Derives W69 candidates + W70+ projections from the live registry (bm-a's
registered W68 row is the tail). Both W69 sides expected ARITHMETIC
CONTINUATION clean. W70-B projection hits xstock_synth_null_a=51_000
mid-window = fork face AGAIN (canon now holds W63 chained AND W68 restart
with opposite readings; sec.4 pin pending HQ-FEEDBACK F-20261002-03) --
both readings disclosed in the warning prose.
"""
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
WIDTH_A = 2_000
WIDTH_B = 200

assert 68 in N1_BANDS and N1_BANDS[68]["engine_owner"] == "bm-a", \
    "W68 registered row missing (bm-a r568 -- fetch/rebase first)"
assert N1_BANDS[68]["a"] == (179_004, 181_003) and \
    N1_BANDS[68]["b_exit"] == (50_501, 50_700), "W68 row drift"
assert 69 not in N1_BANDS, "W69 already registered?! (slot check first)"

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

def clean(lo, width):
    hi = lo + width - 1
    if any(lo <= p <= hi for p in points):
        return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

ARITH_A = (N1_BANDS[68]["a"][1] + 1, N1_BANDS[68]["a"][1] + WIDTH_A)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
first_a = clean(ARITH_A[0], WIDTH_A)
print(f"W69 A: arithmetic {ARITH_A[0]}..{ARITH_A[1]} hits={a_hits} -> first clean {first_a}")

ARITH_B = (N1_BANDS[68]["b_exit"][1] + 1, N1_BANDS[68]["b_exit"][1] + WIDTH_B)
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
first_b = clean(ARITH_B[0], WIDTH_B)
print(f"W69 B: arithmetic {ARITH_B[0]}..{ARITH_B[1]} hits={b_hits} -> first clean {first_b}")

# --- W70+ projections (warning row) ---
w70_a = (first_a[1] + 1, first_a[1] + WIDTH_A)
w70_b = (first_b[1] + 1, first_b[1] + WIDTH_B)
a_hits70 = sorted(p for p in points if w70_a[0] <= p <= w70_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w70_a)]
b_hits70 = sorted(p for p in points if w70_b[0] <= p <= w70_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w70_b)]
print(f"W70+ projection A: {w70_a[0]}..{w70_a[1]} "
      f"-> {'CLEAN (verify at W70 prereg)' if not a_hits70 else 'REFUSED ' + str(a_hits70)}")
print(f"W70+ projection B: {w70_b[0]}..{w70_b[1]} "
      f"-> {'CLEAN' if not b_hits70 else 'REFUSED ' + str(b_hits70)}")
if b_hits70 and isinstance(b_hits70[-1], int):
    mid = (b_hits70[-1] != w70_b[1])
    # restart reading
    r_lo = w70_b[0]
    while clean(r_lo, WIDTH_B) is None:
        h = min(p for p in points if r_lo <= p <= r_lo + WIDTH_B - 1)
        r_lo = h + 1
    # chained reading
    c_lo = w70_b[0]
    while clean(c_lo, WIDTH_B) is None:
        c_lo += WIDTH_B
    print(f"W70 B hit position: {'MID (FORK FACE AGAIN)' if mid else 'TAIL'}; "
          f"restart reading: {r_lo}..{r_lo + WIDTH_B - 1} | "
          f"chained reading: {c_lo}..{c_lo + WIDTH_B - 1} "
          f"(canon holds BOTH W63-chained + W68-restart; sec.4 pin pending)")
