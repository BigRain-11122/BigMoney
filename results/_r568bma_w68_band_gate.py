# -*- coding: utf-8 -*-
"""W68 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W68 = FIFTY-SEVENTH ENGINE-OWNED WAVE candidate, bm-a's SIXTEENTH owned per
machine-derive (engine_owner==bm-a rows 15 + candidate). Freeze authority =
never-dry supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series. W67 (bm-b r567) = table tail; W68 = next free
number (origin vacancy machine-checked at leg3).

Bands: A 179_004..181_003 = ARITHMETIC CONTINUATION from the W67 A tail
(179_003 + 1). B = FORCED-SKIP family: arithmetic window 50_401..50_600 is
REFUSED by SEED_REGISTRY cta_p2_noau=50_500 (mid-band single-point hit --
r307 W5 machine-red precedent: skip is forced, not a free pick); first clean
window past-hit restart = 50_501..50_700 (W26 r335 precedent family + the
W67 row W68+ published projection verbatim; window-stride alternative
reading 50_601..50_800 diverges -- mid-band single hit past-hit-restart is
the registered-projection reading, r566 in-canon-projection-governs law).

Machine-verified against: all 65 registered N1 wave bands W2..W67, N3-R1
used-seed band 70_000..70_070_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points,
N2-W15 draft probe points, lfc actual draw, options_wave2 actual draw.

r568 bm-a freeze-window run. READ-ONLY against the 65-row table + origin
(candidate passed as parameter; local insertion happens in freeze edits
with FIX-A/B/C hardening, MSG-0640 lineage).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (pre-insertion gate: parameter, not local row) ----------------
W68_A = (179_004, 181_003)              # arithmetic continuation, W67 A tail +1
W68_B = (50_501, 50_700)                # forced-skip past-hit restart (50_500)

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"
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

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (65 registered rows, NO W68 locally yet) -----------
pre_w68 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67]
assert sorted(N1_BANDS) == pre_w68, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 65 registered rows, candidate W68 NOT yet local)"
assert 67 in N1_BANDS and N1_BANDS[67]["engine_owner"] == "bm-b", \
    "leg0 failed: W67 (bm-b) table-tail row must be present (r567 freeze)"
assert 66 in N1_BANDS and N1_BANDS[66]["engine_owner"] == "bm-c", \
    "leg0 failed: W66 (bm-c) row must be present"
assert 65 in N1_BANDS and N1_BANDS[65]["engine_owner"] == "bm-b", \
    "leg0 failed: W65 (bm-b) row must be present"
assert 64 in N1_BANDS and N1_BANDS[64]["engine_owner"] == "bm-a", \
    "leg0 failed: W64 (bm-a) row must be present (finalize landed r568)"
assert N1_BANDS[67]["a"] == (177_004, 179_003) and \
    N1_BANDS[67]["b_exit"] == (50_201, 50_400), \
    "leg0 failed: W67 band drift vs canon row"
print("leg0: 65 registered rows (W2..W14, W16..W67), tail=W67 bm-b, "
      "candidate W68 not local (pre-insertion gate)")

# --- leg 0b: W67 row W68+ WARNING prose present in the canon law file --------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "179_004..181_003" in canon, \
    "leg0b failed: W67 row W68+ A projection prose not found in canon"
assert "50_501..50_700" in canon, \
    "leg0b failed: W67 row W68+ B first-clean-window prose not found in canon"
assert "50_401..50_600 REFUSED" in canon, \
    "leg0b failed: W67 row W68+ B arithmetic REFUSED prose not found in canon"
print("leg0b: W67 row W68+ WARNING prose present (A CLEAN / B REFUSED 50_500 "
      "-> first clean 50_501..50_700; bm-b r567 gate projection + this gate "
      "re-derives from live registry, never trusts prose -- r335/r535/r302)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[67]["a"][1] + 1, N1_BANDS[67]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[67]["b_exit"][1] + 1,
           N1_BANDS[67]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (179_004, 181_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (50_401, 50_600), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} {a_band_hits} (W67 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits -- no skip, W67 row projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [50_500] and b_band_hits == [], \
    f"leg1-B failed: expected machine-red [50_500] (forced skip, r307 W5 " \
    f"precedent -- refusal facts identity), got {b_hits} {b_band_hits}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"{{SEED_REGISTRY cta_p2_noau={b_hits[0]}}} -- machine-red = skip is "
      f"FORCED not free-picked (r307 W5 law)")

# --- leg 2: first clean window -----------------------------------------------
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first_a = clean(ARITH_A[0], WIDTH_A)
assert first_a == W68_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W68_A}"
# B: past-hit restart (W26 r335 precedent family + W67 row published projection)
first_b = clean(b_hits[0] + 1, WIDTH_B)
assert first_b == W68_B, \
    f"leg2-B failed: past-hit first clean window {first_b} != candidate {W68_B}"
# window-stride alternative reading disclosure (r566 W63 divergence family):
stride_b = clean(ARITH_B[0] + WIDTH_B, WIDTH_B)
print(f"leg2: A first-clean == arithmetic == candidate {W68_A[0]}..{W68_A[1]}; "
      f"B past-hit restart == candidate {W68_B[0]}..{W68_B[1]} "
      f"(W26 precedent + W67 published projection governs per r566 "
      f"in-canon-projection law; window-stride alternative reading would be "
      f"{stride_b} -- disclosed, divergence family of r566 W63, law-sec.4 "
      f"skip-semantics pin still pending HQ-FEEDBACK)")
assert not overlaps(W68_A, W68_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W68_A), ("B", W68_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W68-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W68-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W68-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W68-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W68-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W68-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W68-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W68-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W68 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "68: {\"a\": (179_004" not in out, \
    "leg3 failed: a W68 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "N1 \u6ce268\uff08" not in out, "leg3 failed: canon W68 row exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W68 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W68 ADMIT: A {W68_A[0]}..{W68_A[1]} (ARITHMETIC CONTINUATION from the "
      f"W67 A tail, zero skip) + B {W68_B[0]}..{W68_B[1]} (FORCED-SKIP "
      f"past-hit restart past SEED_REGISTRY cta_p2_noau=50_500 == the W67 row "
      f"W68+ published projection verbatim) -- clean vs 65 registered rows + "
      f"N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-a (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; origin slot vacancy "
      f"machine-checked; seat declaration published=reserved follows in "
      f"this window).")

# --- W69+ projection (warning text for the law table row) --------------------
w69_a = (W68_A[1] + 1, W68_A[1] + WIDTH_A)
w69_b = (W68_B[1] + 1, W68_B[1] + WIDTH_B)
a_hits69 = sorted(p for p in points if w69_a[0] <= p <= w69_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w69_a)]
b_hits69 = sorted(p for p in points if w69_b[0] <= p <= w69_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w69_b)]
print(f"W69+ projection: A arithmetic +2_000 = {w69_a[0]}..{w69_a[1]} "
      f"-> {'CLEAN (verify at W69 prereg)' if not a_hits69 else 'REFUSED ' + str(a_hits69)}; "
      f"B +200 from W68 end = {w69_b[0]}..{w69_b[1]} "
      f"-> {'CLEAN (verify at W69 prereg)' if not b_hits69 else 'REFUSED ' + str(b_hits69)}")
