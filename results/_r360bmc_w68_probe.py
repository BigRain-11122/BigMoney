# -*- coding: utf-8 -*-
"""r360 bm-c W68 draft-window probe (pre-freeze machine derive, r359 lineage).

Derives the W68 candidate bands + W69+ projections from the live registry
(r535 machine-gate derive law; never prose transcription). B-side semantics:
MID-window hit at 50_500 (cta_p2_noau) -- the two skip readings DIVERGE
(r566 W63 fork family). Governing reading = the W63 REGISTERED in-canon
face (chained whole-window stepping, 49_201..49_400 precedent) per r566
ruling "正典在册面照准"; the restart reading (bm-b's W67-row W68+ prose
projection 50_501..50_700, self-tagged "复核于 W68 prereg") is disclosed
as divergence, not adopted.
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

assert 67 in N1_BANDS and N1_BANDS[67]["engine_owner"] == "bm-b", \
    "W67 registered row missing (fetch/rebase first)"
assert N1_BANDS[67]["a"] == (177_004, 179_003) and \
    N1_BANDS[67]["b_exit"] == (50_201, 50_400), "W67 row drift"
assert 68 not in N1_BANDS, "W68 already registered?! (slot check first)"

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

# --- W68 A: arithmetic continuation from W67 A tail ---
ARITH_A = (N1_BANDS[67]["a"][1] + 1, N1_BANDS[67]["a"][1] + WIDTH_A)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
first_a = clean(ARITH_A[0], WIDTH_A)
print(f"W68 A: arithmetic {ARITH_A[0]}..{ARITH_A[1]} hits={a_hits} "
      f"-> first clean {first_a}")

# --- W68 B: arithmetic window + MID hit fork ---
ARITH_B = (N1_BANDS[67]["b_exit"][1] + 1,
           N1_BANDS[67]["b_exit"][1] + WIDTH_B)
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
print(f"W68 B: arithmetic {ARITH_B[0]}..{ARITH_B[1]} hits={b_hits} "
      f"(hit position {'MID' if b_hits and b_hits[-1] != ARITH_B[1] else 'TAIL/none'})")
# reading 1: chained whole-window stepping (W63 registered in-canon face)
b_lo = ARITH_B[0]
chain_steps = []
while True:
    w = clean(b_lo, WIDTH_B)
    if w is not None:
        break
    chain_steps.append((b_lo, b_lo + WIDTH_B - 1))
    b_lo += WIDTH_B
chained = (b_lo, b_lo + WIDTH_B - 1)
# reading 2: restart at hit+1 (越 hit 起窗, r335 W26 family)
r_lo = ARITH_B[0]
while clean(r_lo, WIDTH_B) is None:
    hit = min(p for p in points if r_lo <= p <= r_lo + WIDTH_B - 1)
    r_lo = hit + 1
restart = (r_lo, r_lo + WIDTH_B - 1)
print(f"W68 B chained-skip (W63 registered face): {chained} "
      f"(dirty windows stepped: {chain_steps})")
print(f"W68 B restart-at-hit+1 (divergent reading): {restart}")
print(f"W68 B fork: {'DIVERGE (mid hit, W63 chained governs)' if chained != restart else 'coincide'}")

# --- W69+ projections (for the canon warning row) ---
w69_a = (chained[1] + 1 - 200 + WIDTH_A, chained[1] - 200 + WIDTH_A + 2000 - 1) \
    if False else (first_a[1] + 1, first_a[1] + WIDTH_A)
w69_b = (chained[1] + 1, chained[1] + WIDTH_B)
a_hits69 = sorted(p for p in points if w69_a[0] <= p <= w69_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w69_a)]
b_hits69 = sorted(p for p in points if w69_b[0] <= p <= w69_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w69_b)]
print(f"W69+ projection: A arithmetic {w69_a[0]}..{w69_a[1]} "
      f"-> {'CLEAN (verify at W69 prereg)' if not a_hits69 else 'REFUSED ' + str(a_hits69)}")
print(f"W69+ projection: B arithmetic {w69_b[0]}..{w69_b[1]} "
      f"-> {'CLEAN (verify at W69 prereg)' if not b_hits69 else 'REFUSED ' + str(b_hits69)}")
if b_hits69 and isinstance(b_hits69[-1], int):
    tail = (b_hits69[-1] == w69_b[1])
    print(f"W69 B hit position: {'TAIL (both readings coincide)' if tail else 'MID (fork face again)'}")
    # derive first clean under both readings for the warning prose
    c_lo = w69_b[0]
    while clean(c_lo, WIDTH_B) is None:
        c_lo += WIDTH_B
    r2_lo = w69_b[0]
    while clean(r2_lo, WIDTH_B) is None:
        h = min(p for p in points if r2_lo <= p <= r2_lo + WIDTH_B - 1)
        r2_lo = h + 1
    print(f"W69 B chained-first-clean: {c_lo}..{c_lo + WIDTH_B - 1} | "
          f"restart-first-clean: {r2_lo}..{r2_lo + WIDTH_B - 1}")
