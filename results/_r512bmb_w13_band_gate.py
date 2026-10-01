"""W13 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W13 = FOURTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-b
-- bm-b's third owned wave after W10/W11; W12 = bm-a, in flight 11/12+shard-11
burning at freeze time). The W12 row's W13+ WARNING projection fires: the A
+2_000 arithmetic tail (65_050..67_049) hits the SEED_REGISTRY cluster
bond_carry_w3a=66_000 / p1e_zoo_behavior=67_000 / p1e_synth_null_b=67_200 ->
REFUSED. Per the r307/r309 forced-skip law the A band packs at the FIRST
2,000-wide window clear of every reserved face: all N1 wave bands (W2..W12,
W12 included this freeze -- first gate to see it), v1 in-use + W1 ext bands,
SEED_REGISTRY all values, N2/N4 probe points (40_000/40_001), lfc actual draw
(30_000..30_099) AND options_wave2 actual draw (63_000..63_049). Scan floor =
arithmetic tail start 65_050 (skip is FORCED, not a re-pick: minimal clean
window from the refused tail; W5/W8/W12 family).
B +200 arithmetic tail (29_300..29_499, W12 B end + 1) projects clean --
machine-verified here.

r512 bm-b freeze-window run. Freeze trigger = never-dry supply law standing
step (watermark red runnable-work-idle-low-cpu at 16:12: engine alive, queue
0, pool claimable 0, board negative adjudicated) -- anti-idle root fix.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W13_A_ARITH = (65_050, 67_049)          # arithmetic tail: projected REFUSED
W13_B = (29_300, 29_499)                # arithmetic tail: projected clean
LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)        # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH = 2_000

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe ------------------------------------------------------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS)
bands = []
for cfg in N1_BANDS.values():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def clean(lo, width=WIDTH):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# --- leg 1: arithmetic A tail REFUSED (forced-skip machine evidence) -------
arith_hits = sorted(p for p in points
                   if W13_A_ARITH[0] <= p <= W13_A_ARITH[1])
assert arith_hits, "leg1 failed: arithmetic tail unexpectedly clean -- re-derive"
# --- leg 2: first clean window scan from the refused tail (minimal skip) ---
x = W13_A_ARITH[0]
first = None
while x < 20_260_000:
    r = clean(x)
    if r:
        first = r
        break
    x += 1
assert first, "no clean 2,000-window found below 20260000"
W13_A = first

# --- leg 3: candidate ADMIT checks ------------------------------------------
conflicts = []
for tag, band in (("A", W13_A), ("B", W13_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W13-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W13-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W13-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W13-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W13-{tag}")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
print(f"leg1 arithmetic A tail {W13_A_ARITH[0]}..{W13_A_ARITH[1]}: REFUSED "
      f"(hits {arith_hits}) -> skip FORCED (r307 law, W5/W8/W12 family)")
print(f"leg2 first clean {WIDTH}-wide window from {W13_A_ARITH[0]}: "
      f"{first[0]}..{first[1]}")
if conflicts:
    print("W13 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W13 ADMIT: A {W13_A[0]}..{W13_A[1]} (forced skip-over) + "
      f"B {W13_B[0]}..{W13_B[1]} (arithmetic) both clean -- engine_owner=bm-b.")
print("W14+ projection: A arithmetic +2_000 = "
      f"{W13_A[1] + 1}..{W13_A[1] + 2_000} (verify at W14 prereg); "
      f"B +200 = {W13_B[1] + 1}..{W13_B[1] + 200} (verify at W14 prereg).")
