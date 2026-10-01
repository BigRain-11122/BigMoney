"""r349 bm-c W47 derive-phase probe (pre-edit: machine-derive A/B windows).

W47 = THIRTY-SEVENTH ENGINE-OWNED WAVE (bm-c's FIFTEENTH owned wave after
W14/W17/W20/W23/W26/W29/W32/W37/W39/W41/W42/W43/W46; the dead r348 session
closed W46 same-window: freeze ea9bc4336 -> 12/12 no-restart burn -> finalize
bbf082e9b K=99,120, ledger 465,748 -- adopted+verified per r471/r529 this
round). Wave 47 = FIRST FREE NUMBER after W46's landed row (canon tail=W46).
Per the W46 row W47+ WARNING: A arithmetic 137_004..139_003 CLEAN projection
/ B arithmetic 44_801..45_000 REFUSED at SEED_REGISTRY 45_000 (W39-B/W43-B
forced-skip family) -- scan-forward first-clean derive, never prose-copied
(r535 law).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
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
WIDTH_A, WIDTH_B = 2_000, 200

assert sorted(N1_BANDS) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                            28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
                            40, 41, 42, 43, 44, 45, 46], "unexpected registry"
assert 46 in N1_BANDS and N1_BANDS[46]["engine_owner"] == "bm-c"

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
    if any(overlaps((lo, hi), b) for b in bands + actual):
        return None
    return (lo, hi)

ARITH_A = (N1_BANDS[46]["a"][1] + 1, N1_BANDS[46]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[46]["b_exit"][1] + 1, N1_BANDS[46]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_hit_keys = [k for k, v in science_gates.SEED_REGISTRY.items()
              if isinstance(v, int) and ARITH_B[0] <= v <= ARITH_B[1]]
print(f"ARITH_A {ARITH_A[0]}..{ARITH_A[1]} hits={a_hits}")
print(f"ARITH_B {ARITH_B[0]}..{ARITH_B[1]} hits={b_hits} keys={b_hit_keys}")

start = ARITH_A[0]
first_a = None
for _ in range(500):
    win = clean(start, WIDTH_A)
    if win is not None:
        first_a = win
        break
    blockers = [p for p in points if start <= p <= start + WIDTH_A - 1]
    if not blockers:
        print(f"A window {start}.. unclean by BAND overlap (not point) -- investigate")
        break
    start = max(blockers) + 1
print(f"FIRST_CLEAN_A {first_a}")

start = ARITH_B[0]
first_b = None
for _ in range(500):
    win = clean(start, WIDTH_B)
    if win is not None:
        first_b = win
        break
    blockers = [p for p in points if start <= p <= start + WIDTH_B - 1]
    if not blockers:
        print(f"B window {start}.. unclean by BAND overlap (not point) -- investigate")
        break
    start = max(blockers) + 1
print(f"FIRST_CLEAN_B {first_b}")

if first_a and first_b:
    w48_a = (first_a[1] + 1, first_a[1] + WIDTH_A)
    w48_b = (first_b[1] + 1, first_b[1] + WIDTH_B)
    a48 = sorted(p for p in points if w48_a[0] <= p <= w48_a[1]) or [
        f"band {b}" for b in bands + actual if overlaps(b, w48_a)]
    b48 = sorted(p for p in points if w48_b[0] <= p <= w48_b[1]) or [
        f"band {b}" for b in bands + actual if overlaps(b, w48_b)]
    print(f"W48+_PROJECTION A {w48_a[0]}..{w48_a[1]} -> "
          f"{'CLEAN' if not a48 else 'REFUSED ' + str(a48)}")
    print(f"W48+_PROJECTION B {w48_b[0]}..{w48_b[1]} -> "
          f"{'CLEAN' if not b48 else 'REFUSED ' + str(b48)}")
