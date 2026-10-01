"""W28 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W28 = SEVENTEENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-b
-- bm-b's EIGHTH owned wave after W10/W11/W13/W16/W19/W22/W25). Sovereignty
rotation law F-20260901-01 slot: W28=bm-b per the law sec.4 W27 row verbatim
(W25=bm-b real anchor -- finalize landed bm-b r522, K=52,920, ledger 419,548
chain head; W26=bm-c / W27=bm-a seats continue the +3 rotation -> W28=bm-b).
No pointer gate is pending: W26 registered + burned 12/12 by bm-c r335
(finalize pending on the bm-c seat), W27 registered by bm-a r539 (burn in
progress on bm-a, 5/12 at their freeze) -- coexistence is judged by band
disjointness, not commit order (r531 law).

The W27 row's W28+ WARNING projects BOTH tails arithmetic-clean -- this
gate machine-verifies that projection:
  A +2_000 arithmetic tail (99_004..101_003 == W27 A end + 1) -> CLEAN
    (no registry value, no registered band, no probe seed, no actual
    draw range inside);
  B +200 arithmetic tail (40_451..40_650 == W27 B end + 1) -> CLEAN
    (nearest reserved points 40_000/40_001/40_050 sit BELOW the window;
    p4_batch1=41_000 sits ABOVE it; no N1 B band reaches past 40_450).
No skip on either side (R250: W28 bands were never assigned; the
measurement face has no result to fish).

Machine-verified against: all registered N1 wave bands W2..W27 (26 rows,
W24/W25/W26/W27 included -- this freeze reads the 26-row pre-W28 table
plus the candidate), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x
r529 bm-a mandatory leg: every N1/N2/N4 band-gate receipt must carry the
N3 used-seed leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg -- mandatory in every gate receipt from W26 on),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points (40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r523 bm-b freeze-window run. Freeze trigger = never-dry supply law standing
step (engine alive status exit 0, heartbeat 57s, queue 0 after the W25
finalize on this machine r522 -- all bm-b-registered waves burned, board
negative, rotation slot W28=bm-b; anti-idle root fix per standing CEO
full-mobilization law O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W28_A = (99_004, 101_003)                # law sec.4 W28 row (arithmetic, no skip)
W28_B = (40_451, 40_650)                 # law sec.4 W28 row (arithmetic, no skip)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)             # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg: mandatory in every gate
#     receipt from W26 on -- probe seeds are batch-band-reserved by the
#     selftest disjoint law; register the CONSUMED VALUE SET) -----------------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003

LFC_ACTUAL = (30_000, 30_099)            # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)        # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)      # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W28 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 28:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (26 pre-W28 rows + the candidate) -----------------
assert 25 in N1_BANDS and N1_BANDS[25]["engine_owner"] == "bm-b", \
    "leg0 failed: W25 (bm-b) rows must be present (r520 freeze, r522 finalize)"
assert 26 in N1_BANDS and N1_BANDS[26]["engine_owner"] == "bm-c", \
    "leg0 failed: W26 (bm-c) rows must be present (r335 freeze)"
assert 27 in N1_BANDS and N1_BANDS[27]["engine_owner"] == "bm-a", \
    "leg0 failed: W27 (bm-a) rows must be present (r539 freeze)"
pre_w28 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
assert sorted(N1_BANDS) == pre_w28, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"26 registered rows + the W28 candidate)"

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[27]["a"][1] + 1, N1_BANDS[27]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[27]["b_exit"][1] + 1,
           N1_BANDS[27]["b_exit"][1] + WIDTH_B)
# BOTH arithmetic tails project CLEAN per the W27 row's W28+ WARNING --
# this gate verifies it (no skip expected on either side).
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: W27 row projection drift -- arithmetic " \
    f"{ARITH_A[0]}..{ARITH_A[1]} unexpectedly hits {a_hits}"
print(f"leg1-A arithmetic tail {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(no registry point/probe seed inside -- ADMIT, no skip)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: W27 row projection drift -- arithmetic " \
    f"{ARITH_B[0]}..{ARITH_B[1]} unexpectedly hits {b_hits}"
print(f"leg1-B arithmetic tail {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(40_000/40_001/40_050 sit below, 41_000 above -- ADMIT, no skip)")

# --- leg 2: first clean window == the arithmetic window (NO skip) ------------
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
assert first_a == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != arithmetic " \
    f"{ARITH_A} (both project clean per the W27 row -- a skip here " \
    f"would be an unexplained deviation; R250/r518)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=(W28_A,))  # own A band reserved (W6 law)
assert first_b == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != arithmetic " \
    f"{ARITH_B} (both project clean per the W27 row -- R250/r518)"
assert W28_A == ARITH_A and W28_B == ARITH_B, \
    "leg2 failed: candidate must equal the machine-derived arithmetic window"
assert not overlaps(W28_A, W28_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ---------------
conflicts = []
for tag, band in (("A", W28_A), ("B", W28_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 28:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W28-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W28-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W28-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W28-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W28-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W28-{tag} (r335 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W28-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W28-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W28 row must equal the derived candidate
assert N1_BANDS[28]["a"] == W28_A and N1_BANDS[28]["b_exit"] == W28_B, \
    "leg3 failed: canon W28 row drift vs derived candidate"
assert N1_BANDS[28]["engine_owner"] == "bm-b", "leg3 failed: W28 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
print(f"leg1 both arithmetic tails CLEAN (W27 row W28+ WARNING projection "
      f"verified); leg2 first clean windows == arithmetic windows "
      f"A {first_a[0]}..{first_a[1]}, B {first_b[0]}..{first_b[1]} "
      f"(NO skip, R250)")
if conflicts:
    print("W28 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W28 ADMIT: A {W28_A[0]}..{W28_A[1]} + B {W28_B[0]}..{W28_B[1]} both "
      f"clean vs 26 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-b "
      f"(rotation law slot W28=bm-b; W27 row slot assignment verbatim; "
      f"BOTH tails arithmetic continuation, no skip on either side).")

# --- W29+ projection (warning text for the law table row) --------------------
w29_a = (W28_A[1] + 1, W28_A[1] + WIDTH_A)
w29_b = (W28_B[1] + 1, W28_B[1] + WIDTH_B)
a_hits29 = sorted(p for p in points if w29_a[0] <= p <= w29_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w29_a)]
b_hits29 = sorted(p for p in points if w29_b[0] <= p <= w29_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w29_b)]
print(f"W29+ projection: A arithmetic +2_000 = {w29_a[0]}..{w29_a[1]} "
      f"-> {'CLEAN (verify at W29 prereg)' if not a_hits29 else 'REFUSED ' + str(a_hits29)}; "
      f"B +200 = {w29_b[0]}..{w29_b[1]} "
      f"-> {'CLEAN (verify at W29 prereg)' if not b_hits29 else 'REFUSED ' + str(b_hits29)}")
