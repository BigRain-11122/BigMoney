"""W17 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W17 = SEVENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-c
-- bm-c's SECOND owned wave after W14). Sovereignty rotation law F-20261001-01
slot: W14=bm-c anchored, +3 -> W17=bm-c. Unified wave number 15 remains held
by bm-a's N2-W15 draft; N1 face numbering keeps the gap (..14, 16, 17..).

The W16 row's W17+ WARNING projection fires in the SPLIT form:
  A +2_000 arithmetic tail (76_001..78_000 == W16 A end + 1) -- projected
  CLEAN, stride kept verbatim (no skip);
  B +200 arithmetic tail (29_900..30_099 == W16 B end + 1) -- REFUSED by
  projection: it hits the lfc actual draw range 30_000..30_099 (and the
  SEED_REGISTRY point lfc_p1_screen=30_000) -> B packs at the FIRST clean
  200-window scanning upward past every reserved band (incl. this wave's
  own A band), per the W5/W6/W8/W12 forced-skip-over family. Machine-derived
  here -- the landing is NEVER a free pick (R250).

Machine-verified against: all N1 wave bands W2..W16 (W16 included, this
freeze reads the 14-row pre-W17 table), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 design-probe points (40_000/40_001),
N2-W15 draft probe points (31_000/31_500/32_000), lfc actual draw
(30_000..30_099) AND options_wave2 actual draw (63_000..63_049).

r328 bm-c freeze-window run. Freeze trigger = never-dry supply law standing
step (watermark red runnable-work-idle-low-cpu at 17:50, py tail 0/0/0:
engine alive, queue 0, board negative adjudicated, rotation slot W17=bm-c
-- anti-idle root fix per standing CEO full-mobilization law
O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W17_A_ARITH = (76_001, 78_000)          # arithmetic tail: projected CLEAN
W17_B_ARITH = (29_900, 30_099)          # arithmetic tail: projected REFUSED
LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)       # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
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

def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# --- leg 1: A arithmetic tail CLEAN / B arithmetic tail REFUSED (machine) ---
a_hits = sorted(p for p in points if W17_A_ARITH[0] <= p <= W17_A_ARITH[1])
assert not a_hits, f"leg1-A failed: arithmetic tail dirty {a_hits}"
b_hits = sorted(p for p in points if W17_B_ARITH[0] <= p <= W17_B_ARITH[1])
assert b_hits, \
    f"leg1-B failed: B arithmetic tail {W17_B_ARITH} unexpectedly clean " \
    "-- skip-over would NOT be forced (re-derive, no free pick, R250)"
b_band_hits = [b for b in bands + actual if overlaps(b, W17_B_ARITH)]
assert b_band_hits, "leg1-B failed: no band overlap evidence for the refusal"

# --- leg 2: A first clean window == arithmetic (no skip, R250) -------------
first_a = None
x = W17_A_ARITH[0]
while x < 20_260_000:
    r = clean(x, WIDTH_A)
    if r:
        first_a = r
        break
    x += 1
assert first_a, "no clean 2,000-window found below 20260000"
assert first_a == W17_A_ARITH, \
    f"leg2-A failed: first clean window {first_a} != arithmetic {W17_A_ARITH} " \
    "(skip would be FORCED -- re-derive, do not free-pick)"
W17_A = first_a

# --- leg 2b: B FORCED jump -- first clean 200-window past every reserved ---
# (scan universe includes THIS wave's A band -- W6 precedent)
bands_with_w17a = bands + [W17_A]
first_b = None
x = W17_B_ARITH[0]
while x < 20_000_000:
    hi = x + WIDTH_B - 1
    ok = True
    for p in points:
        if x <= p <= hi:
            ok = False
            break
    if ok:
        for b in bands_with_w17a + actual:
            if overlaps((x, hi), b):
                ok = False
                break
    if ok:
        first_b = (x, hi)
        break
    x += 1
assert first_b, "no clean 200-window found below 20000000"
assert first_b[0] > W17_B_ARITH[0], \
    "leg2-B failed: landed at/before the refused arithmetic start"
W17_B = first_b

# --- leg 3: candidate ADMIT checks ------------------------------------------
conflicts = []
for tag, band in (("A", W17_A), ("B", W17_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W17-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W17-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W17-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W17-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W17-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W17-{tag}")
assert not overlaps(W17_A, W17_B), "leg3 failed: W17 A/B self-overlap"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
print(f"leg1-A arithmetic tail CLEAN: A {W17_A_ARITH[0]}..{W17_A_ARITH[1]} "
      f"(W16 A end + 1) -- stride kept verbatim")
print(f"leg1-B arithmetic tail REFUSED: B {W17_B_ARITH[0]}..{W17_B_ARITH[1]} "
      f"hits registry points {b_hits} + bands {b_band_hits} "
      "-- skip-over FORCED (machine evidence, R250 no-free-pick)")
print(f"leg2-A first clean {WIDTH_A}-wide window from {W17_A_ARITH[0]}: "
      f"{W17_A[0]}..{W17_A[1]} == arithmetic start (no skip)")
print(f"leg2-B first clean {WIDTH_B}-wide window from {W17_B_ARITH[0]} "
      f"upward past every reserved band: B = {W17_B[0]}..{W17_B[1]}")
if conflicts:
    print("W17 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W17 ADMIT: A {W17_A[0]}..{W17_A[1]} (arithmetic) + "
      f"B {W17_B[0]}..{W17_B[1]} (forced skip-over) both clean -- "
      "engine_owner=bm-c (rotation law slot W17=bm-c).")

# --- W18+ projection (warning text for the law table row) ------------------
w18_a = (W17_A[1] + 1, W17_A[1] + WIDTH_A)
w18_b = (W17_B[1] + 1, W17_B[1] + WIDTH_B)
a_hits18 = sorted(p for p in points if w18_a[0] <= p <= w18_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w18_a)]
b_hits18 = sorted(p for p in points if w18_b[0] <= p <= w18_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w18_b)]
print(f"W18+ projection: A +2_000 = {w18_a[0]}..{w18_a[1]} "
      f"-> {'CLEAN (verify at W18 prereg)' if not a_hits18 else 'REFUSED ' + str(a_hits18)}; "
      f"B +200 = {w18_b[0]}..{w18_b[1]} "
      f"-> {'CLEAN (verify at W18 prereg)' if not b_hits18 else 'REFUSED ' + str(b_hits18)}")
