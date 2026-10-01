"""W50 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W50 = THIRTY-NINTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's FOURTEENTH owned wave after W14/W17/W20/W23/
W26/W29/W32/W37/W39/W41/W42/W43/W46). FREEZE AUTHORITY = never-dry supply
law standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2
own-continuous-series: bm-c's previous owned wave W46 closed FULL-LIFECYCLE
via the r348 session (freeze -> 12/12 burn -> finalize landed K=99,120,
ledger 465,748; r348 died before S7 bookkeeping -- products fully
delivered on origin, numbers 347/348/349 burned per r529 law, r350
resumes the series) -> zero-gap relay, wave number 50 = FIRST FREE NUMBER
after the registered W49 row (W48 = bm-a-declared slot per the r555
W47-yield receipt, still UNREGISTERED -- W19/W18 non-contiguity
precedent).

The W49 row's W50+ WARNING projects: BOTH SIDES ARITHMETIC CONTINUATION
CLEAN (A 143_004..145_003 = W49 A end + 1; B 45_601..45_800 = W49 B end
+ 1). r335 lesson (projections can carry scanning-universe blind spots) +
r535 law (clean-projection claims must be machine-derived, never
prose-copied): this gate re-derives from the live registry, never trusts
the prose.

Machine-verified against: all registered N1 wave bands W2..W49 (46
rows, W49 in-flight coexists by band disjointness per r531 law), the W48
PUBLISHED PROJECTION bands A 139_004..141_003 / B 45_201..45_400
(r518-1 published=reserved law -- bm-a declared W48 in the r555 yield
receipt), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 bm-a
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg -- mandatory on every gate receipt from W26 on),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points (40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r350 bm-c freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W50_A = (143_004, 145_003)              # law sec.4 W50 row (arithmetic, no skip)
W50_B = (45_601, 45_800)                # law sec.4 W50 row (arithmetic, no skip)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)       # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
# W48 PUBLISHED PROJECTION (r518-1 published=reserved law): bm-a declared
# W48 as their next own wave in the r555 W47-yield receipt; the W47 row's
# W48+ WARNING projects these bands (machine-derived by the r534 gate's
# W48+ projection legs). W48 is still UNREGISTERED at this freeze -- the
# published face itself is the reservation, not a point hit.
W48_PUBLISHED_PROJECTION = [(139_004, 141_003), (45_201, 45_400)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W50 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 50:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT + W48_PUBLISHED_PROJECTION
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (46 pre-W50 rows + the candidate) ------------------
assert 49 in N1_BANDS and N1_BANDS[49]["engine_owner"] == "bm-b", \
    "leg0 failed: W49 (bm-b) row must be present (r556 freeze; in-flight " \
    "burn, finalize NOT landed -- finalize merge loop FAIL-CLOSED r307)"
assert 47 in N1_BANDS and N1_BANDS[47]["engine_owner"] == "bm-b", \
    "leg0 failed: W47 (bm-b) rows must be present (r556 finalize landed " \
    "same-window K=101,320 ledger 467,948)"
assert 46 in N1_BANDS and N1_BANDS[46]["engine_owner"] == "bm-c", \
    "leg0 failed: W46 (bm-c) rows must be present (r348 freeze; finalize " \
    "landed K=99,120 ledger 465,748)"
assert 43 in N1_BANDS and N1_BANDS[43]["engine_owner"] == "bm-c", \
    "leg0 failed: W43 (bm-c) rows must be present (r346 freeze; finalize " \
    "landed K=92,520 ledger 457,140)"
pre_w50 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           49, 50]
assert sorted(N1_BANDS) == pre_w50, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 46 " \
    f"registered rows + the W50 candidate)"

# --- leg 0b: W49 row's W50+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "143_004..145_003" in canon and "45_601..45_800" in canon, \
    "leg0b failed: W49 row W50+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W49 row W50+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[49]["a"][1] + 1, N1_BANDS[49]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[49]["b_exit"][1] + 1,
           N1_BANDS[49]["b_exit"][1] + WIDTH_B)
# A tail projected CLEAN by the W49 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W49 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W49 "
      f"projection verified machine-side)")
# B tail projected CLEAN likewise -- machine-verify (fail-closed on drift):
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: W49 row projected CLEAN but arithmetic window has " \
    f"point hits {b_hits} -- projection drift, re-derive before landing"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W49 "
      f"projection verified machine-side)")

# --- leg 2: first clean window (A == arithmetic; B == machine-derived) ------
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
assert first_a == W50_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W50_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W50_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W50_B} " \
    "(no skip expected; R250/r518 machine-derived)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (arithmetic continuation, not picked)")
assert not overlaps(W50_A, W50_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W50_A), ("B", W50_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 50:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W50-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W50-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W50-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W50-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W50-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT),
                   ("w48-published-projection", W48_PUBLISHED_PROJECTION)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W50-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                          f"x W50-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W50-{tag} (r335 leg)")
# canon cross-check: the landed W50 row must equal the derived candidate
assert N1_BANDS[50]["a"] == W50_A and N1_BANDS[50]["b_exit"] == W50_B, \
    "leg3 failed: canon W50 row drift vs derived candidate"
assert N1_BANDS[50]["engine_owner"] == "bm-c", "leg3 failed: W50 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "50: {\"a\": (143_004" not in out, \
    "leg3 failed: a W50 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg) | "
      f"W48 published projection (r518-1 reserved): "
      f"A {W48_PUBLISHED_PROJECTION[0][0]}..{W48_PUBLISHED_PROJECTION[0][1]} / "
      f"B {W48_PUBLISHED_PROJECTION[1][0]}..{W48_PUBLISHED_PROJECTION[1][1]}")
if conflicts:
    print("W50 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W50 ADMIT: A {W50_A[0]}..{W50_A[1]} (arithmetic continuation from "
      f"W49 tail, no skip) + B {W50_B[0]}..{W50_B[1]} (arithmetic "
      f"continuation from W49 tail, no skip) both clean vs 46 registered "
      f"rows + W48 published projection (r518-1) + N3-R1 used-seed band + "
      f"probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-c (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2; zero-gap relay after the W46 full closeout "
      f"r348; W49 in-flight coexists by band disjointness r531; origin "
      f"slot vacancy machine-checked).")

# --- W51+ projection (warning text for the law table row) --------------------
w51_a = (W50_A[1] + 1, W50_A[1] + WIDTH_A)
w51_b = (W50_B[1] + 1, W50_B[1] + WIDTH_B)
a_hits51 = sorted(p for p in points if w51_a[0] <= p <= w51_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w51_a)]
b_hits51 = sorted(p for p in points if w51_b[0] <= p <= w51_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w51_b)]
print(f"W51+ projection: A arithmetic +2_000 = {w51_a[0]}..{w51_a[1]} "
      f"-> {'CLEAN (verify at W51 prereg)' if not a_hits51 else 'REFUSED ' + str(a_hits51)}; "
      f"B +200 from W50 end = {w51_b[0]}..{w51_b[1]} "
      f"-> {'CLEAN (verify at W51 prereg)' if not b_hits51 else 'REFUSED ' + str(b_hits51)}")
