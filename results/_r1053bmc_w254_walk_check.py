# -*- coding: utf-8 -*-
# r1053 bm-c: W254 live-walk quick derive (pre-seat, live universe governs r587)
import os
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

N3R1_USED = (71_000, 71_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


W253_A = tuple(N1_BANDS[253]["a"])
W253_B = tuple(N1_BANDS[253]["b_exit"])
print("W253 registry:", W253_A, W253_B, N1_BANDS[253].get("engine_owner"))
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print("owner", len(owner_rows), "bma", len(bma_rows), "bmb", len(bmb_rows), "bmc", len(bmc_rows))
print("254 in N1_BANDS:", 254 in N1_BANDS)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]
print("seed points in 574_101..576_300 range:", sorted(p for p in points if 574_101 <= p <= 576_300))


def first_clean(lo, width, trace=None, extra_bands=()):
    hops = 0
    prev_lo = lo
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in list(bands) + list(extra_bands) + actual
                     if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        jump = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        if trace is not None:
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump,
                          "refuser_pts": sorted(bad_pts),
                          "refuser_bands": [list(b) for b in bad_bands]})
        lo = jump
        prev_lo = lo
        hops += 1


ARITH_A = (W253_A[1] + 1, W253_A[1] + WIDTH_A)
ARITH_B = (W253_B[1] + 1, W253_B[1] + WIDTH_B)
print("ARITH_A naive", ARITH_A, "ARITH_B naive", ARITH_B)
a_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A, trace=a_trace)
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace, extra_bands=(fc_a,))
print("LIVE A:", fc_a, "hops", hops_a, "trace", a_trace)
print("LIVE B:", fc_b, "hops", hops_b, "trace", b_trace)
print("B lands above own-A:", fc_b[0] > fc_a[1], "| B==own-A tail+1:", fc_b[0] == fc_a[1] + 1)
print("A base == W253 B tail+1:", fc_a[0] == W253_B[1] + 1)

# leg4 projection for W255+ (assuming W254 registers at live bands)
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
print("W255p naive A", pA, "-> first-clean", pA_fc, "hops", pA_hops)
print("W255p naive B", pB, "-> first-clean", pB_fc, "hops", pB_hops)
