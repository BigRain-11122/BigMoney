"""W19 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W19 = SEVENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-b
-- bm-b's FIFTH owned wave after W10/W11/W13/W16). Sovereignty rotation law
F-20261001-01 slot: W16=bm-b anchored (finalize landed r516: K=33,120, ledger
399,748), +3 -> W19=bm-b (modulo-3 continuation). Unified wave numbers 17
(bm-c slot) and 18 (bm-a slot) are UNFROZEN at this window -- N1 face
numbering continues at W19 with honest gap notes (their bands land at their
owners' freeze windows via the table-tail continuation scan; the r516 derive
law -- finalize wave-set from registry keys -- makes the 17/18 gap
structural-safe, 15-gap precedent).

The W16 row's W17+ WARNING projection fires at THIS freeze window (the next
frozen N1 wave regardless of number):
- A arithmetic tail 76_001..78_000 (W16 A end + 1, table-tail continuation):
  projected CLEAN -> keep the +2_000 stride verbatim (no skip).
- B arithmetic tail 29_900..30_099 (W16 B end + 1): projected REFUSED -- it
  hits the lfc actual draw range 30_000..30_099 AND the SEED_REGISTRY point
  30_000 (lfc_p1_screen) -> FORCED skip-over: B packs at the first free
  200-window clear of every reserved band + actual draw ranges (W5/W6/W8
  skip-over family precedent). The skip is machine-FORCED, NOT a re-pick
  (R250): W19 bands were never assigned, the measurement face has zero
  results to fish.

Machine-verified here against: all N1 wave bands W2..W16 (W16 included --
landed r515/r516), v1 in-use + W1 ext bands, SEED_REGISTRY live values,
N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe points
(31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND options_wave2
actual draw (63_000..63_049).

r517 bm-b freeze-window run. Freeze trigger = never-dry supply law standing
step (engine alive, queue 0, board negative-adjudicated: T-141 open slices
held by bm-a/bm-c, pool next_pick=claimed, py_cpu 0.0 idle face; T-141
acceptance face 3-workday py>=70% in flight -- anti-idle root fix per
standing CEO full-mobilization law O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W19_A_ARITH = (76_001, 78_000)          # arithmetic tail: projected CLEAN
W19_B_ARITH = (29_900, 30_099)          # arithmetic tail: projected REFUSED
LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)        # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)      # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe ------------------------------------------------------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
bands = []
for cfg in N1_BANDS.values():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# --- leg 1: A arithmetic tail CLEAN (ADMIT machine evidence) ----------------
a_hits = sorted(p for p in points if W19_A_ARITH[0] <= p <= W19_A_ARITH[1])
assert not a_hits, f"leg1 failed: A arithmetic tail dirty {a_hits}"

# --- leg 1b: B arithmetic tail REFUSED (forced-skip machine evidence) ------
b_point_hits = sorted(p for p in points if W19_B_ARITH[0] <= p <= W19_B_ARITH[1])
assert b_point_hits == [30_000], \
    f"leg1b failed: B tail point hits {b_point_hits} != [30000] (lfc_p1_screen)"
assert overlaps(LFC_ACTUAL, W19_B_ARITH), \
    "leg1b failed: B tail must hit the lfc actual draw range"

# --- leg 2: A first clean 2,000-window from the arithmetic start ------------
first = None
x = W19_A_ARITH[0]
while x < 20_260_000:
    r = clean(x, WIDTH_A)
    if r:
        first = r
        break
    x += 1
assert first, "no clean 2,000-window found below 20260000"
assert first == W19_A_ARITH, \
    f"leg2 failed: first clean window {first} != arithmetic {W19_A_ARITH} " \
    "(skip would be FORCED -- re-derive, do not free-pick)"
W19_A = first

# --- leg 2b: B forced skip-over -- first clean 200-window from 29_900 -------
firstb = None
x = W19_B_ARITH[0]
while x < 20_260_000:
    r = clean(x, WIDTH_B, extra=(W19_A,))
    if r:
        firstb = r
        break
    x += 1
assert firstb, "no clean 200-window found below 20260000"
assert firstb[0] > W19_B_ARITH[0], \
    f"leg2b failed: B skip not forced (packed at {firstb}?)"
W19_B = firstb
assert not overlaps(W19_A, W19_B), "A/B overlap after packing"

# --- leg 3: candidate ADMIT checks ------------------------------------------
conflicts = []
for tag, band in (("A", W19_A), ("B", W19_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W19-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W19-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W19-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W19-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W19-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W19-{tag}")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
print(f"leg1 A arithmetic tail CLEAN: {W19_A_ARITH[0]}..{W19_A_ARITH[1]} "
      f"(W16 A end + 1, table-tail continuation)")
print(f"leg1b B arithmetic tail REFUSED (FORCED skip evidence): "
      f"{W19_B_ARITH[0]}..{W19_B_ARITH[1]} hits SEED_REGISTRY point 30_000 "
      f"(lfc_p1_screen) + lfc actual {LFC_ACTUAL[0]}..{LFC_ACTUAL[1]}")
print(f"leg2 first clean {WIDTH_A}-wide window from {W19_A_ARITH[0]}: "
      f"{first[0]}..{first[1]} == arithmetic start (no forced skip, R250)")
print(f"leg2b first clean {WIDTH_B}-wide window from {W19_B_ARITH[0]}: "
      f"{firstb[0]}..{firstb[1]} (B packs here, W5/W6/W8 skip-over family)")
if conflicts:
    print("W19 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W19 ADMIT: A {W19_A[0]}..{W19_A[1]} + B {W19_B[0]}..{W19_B[1]} "
      f"both clean -- engine_owner=bm-b "
      "(rotation law slot W19=bm-b; numbers 17/18 unfrozen, gap noted).")

# --- W20+ projection (warning text for the law table row) -------------------
w20_a = (W19_A[1] + 1, W19_A[1] + WIDTH_A)
w20_b = (W19_B[1] + 1, W19_B[1] + WIDTH_B)
a_hits20 = sorted(p for p in points if w20_a[0] <= p <= w20_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w20_a)]
b_hits20 = sorted(p for p in points if w20_b[0] <= p <= w20_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w20_b)]
print(f"W20+ projection: A arithmetic +2_000 = {w20_a[0]}..{w20_a[1]} "
      f"-> {'CLEAN (verify at W20 prereg)' if not a_hits20 else 'REFUSED ' + str(a_hits20)}; "
      f"B +200 = {w20_b[0]}..{w20_b[1]} "
      f"-> {'CLEAN (verify at W20 prereg)' if not b_hits20 else 'REFUSED ' + str(b_hits20)}")
