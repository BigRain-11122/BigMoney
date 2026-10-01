"""W26 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W26 = FIFTEENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-c
-- bm-c's FIFTH owned wave after W14/W17/W20/W23). Sovereignty rotation law
F-20261001-01 slot: W26=bm-c per the law sec.4 W25 row verbatim (W23=bm-c
anchored -- finalize landed bm-c r335, K=48,520, ledger 415,148; +3 ->
W26=bm-c). No pointer gate is pending: W24 registered + burned 12/12 (bm-a
r536, finalize chain-gated on W23, now unblocked), W25 registered + burned
12/12 (bm-b r521 ride1 a14fc3b77) -- coexistence is judged by band
disjointness, not commit order (r531 law).

The W25 row's W26+ WARNING fires in the SPLIT form -- but the freeze
window DISCOVERED a wider refusal: the r520/r535 receipt family's
reserved universe omitted the four runner design-probe seeds
(95_000/95_001 ext + 95_002/95_003 n1), so the "A projects clean"
projection was WRONG. The n1 materializer selftest leg caught it:
  A +2_000 arithmetic tail (94_001..96_000 == W25 A end + 1) -- REFUSED:
  hits ALL FOUR probe-seed constants (batch-band-reserved by the
  selftest disjoint law). Forced skip -> first clean 2,000-window
  95_004..97_003 (W12 A-skip precedent);
  B +200 arithmetic tail (39_900..40_099 == W25 B end + 1) -- REFUSED:
  hits the N2/N4 design-probe retention points 40_000/40_001 AND the
  SEED_REGISTRY value 40_050 exactly as the W25 row projected. Forced
  skip -> first clean 200-window 40_051..40_250 (W5/W6/W8/W12/W17
  precedent). Both jumps are machine-derived, never free picks (R250;
  r518 law). Past waves W24/W25 clear the probe cluster -- zero
  retroactive harm.

Machine-verified against: all registered N1 wave bands W2..W25 (24 rows,
W21/W22/W23/W24/W25 included -- this freeze reads the 24-row pre-W26
table plus the candidate), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x
r529 bm-a mandatory leg: every N1/N2/N4 band-gate receipt must carry the
N3 used-seed leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values,
N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe points
(31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r335 bm-c freeze-window run. Freeze trigger = never-dry supply law standing
step (engine alive status exit 0, queue 0 after the W23 closeout on this
machine -- all registered waves 2..25 burned, board negative, rotation slot
W26=bm-c; anti-idle root fix per standing CEO full-mobilization law
O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W26_A = (95_004, 97_003)                # law sec.4 W26 row (forced-skip jump)
W26_B = (40_051, 40_250)                # forced-skip jump target (first clean)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (W26 freeze-window discovery: the r520/r535
# gate receipts' reserved universe OMITTED these -- the arithmetic A window
# 94_001..96_000 hits ALL FOUR probe constants and the n1 materializer
# selftest leg caught it. Probe seeds are batch-band-reserved by the
# selftest disjoint law ("probe seed inside a batch band" assertion family);
# every gate receipt from W26 on MUST carry this leg (r529 family: register
# the CONSUMED VALUE SET, not just registry points). Past waves W24/W25
# bands (90_001..94_000) clear the cluster -- zero retroactive harm. ---
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003

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

# --- reserved universe (W26 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 26:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (23 pre-W26 rows + the candidate) ------------------
assert 23 in N1_BANDS and N1_BANDS[23]["engine_owner"] == "bm-c", \
    "leg0 failed: W23 (bm-c) rows must be present (r332 freeze, r335 finalize)"
assert 24 in N1_BANDS and N1_BANDS[24]["engine_owner"] == "bm-a", \
    "leg0 failed: W24 (bm-a) rows must be present (r535 freeze)"
assert 25 in N1_BANDS and N1_BANDS[25]["engine_owner"] == "bm-b", \
    "leg0 failed: W25 (bm-b) rows must be present (r520 freeze)"
pre_w26 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
assert sorted(N1_BANDS) == pre_w26, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"23 registered rows + the W26 candidate)"

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[25]["a"][1] + 1, N1_BANDS[25]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[25]["b_exit"][1] + 1,
           N1_BANDS[25]["b_exit"][1] + WIDTH_B)
# BOTH arithmetic tails are DIRTY -- forced skip on BOTH sides:
# A hits the four runner design-probe seeds 95_000..95_003 (r335
# discovery: the W25 row's "A projects clean" WARNING was a scanning-
# universe blind spot, caught by the n1 materializer selftest leg);
# B hits the N2/N4 design-probe points 40_000/40_001 + registry 40_050
# exactly as the W25 row projected.
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [95_000, 95_001, 95_002, 95_003], \
    f"leg1-A failed: refusal facts drift {a_hits} (probe-seed cluster " \
    f"95_000..95_003 expected per the n1 selftest disjoint law)"
print(f"leg1-A refusal facts (forced skip, not a free pick): "
      f"arithmetic {ARITH_A[0]}..{ARITH_A[1]} hits probe seeds {a_hits}")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [40_000, 40_001, 40_050], \
    f"leg1-B failed: refusal facts drift {b_hits} (W25 row WARNING " \
    f"projection: 40_000/40_001/40_050)"
print(f"leg1-B refusal facts (forced skip, not a free pick): "
      f"arithmetic {ARITH_B[0]}..{ARITH_B[1]} hits points {b_hits}")

# --- leg 2: first clean window (BOTH sides = first clean after forced skip) --
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first_a = None
x = ARITH_A[0]
while x < 20_260_000:
    r = clean(x, WIDTH_A)
    if r:
        first_a = r
        break
    x += 1
assert first_a, "no clean 2,000-window found below 20260000"
assert first_a == W26_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W26_A} " \
    "(jump target must be machine-derived, never a free pick; R250/r518)"
first_b = None
x = ARITH_B[0]
while x < 20_260_000:
    r = clean(x, WIDTH_B, extra=(W26_A,))   # own A band reserved (W6 law)
    if r:
        first_b = r
        break
    x += 1
assert first_b, "no clean 200-window found below 20260000"
if W26_B is None:
    print(f"DERIVE MODE: first clean B window after forced skip = "
          f"{first_b[0]}..{first_b[1]} -- pin W26_B and re-run for ADMIT")
    sys.exit(3)
assert first_b == W26_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W26_B} " \
    "(jump target must be machine-derived, never a free pick; R250/r518)"
assert not overlaps(W26_A, W26_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W26_A), ("B", W26_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 26:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W26-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W26-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W26-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W26-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W26-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W26-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W26-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W26 row must equal the derived candidate
assert N1_BANDS[26]["a"] == W26_A and N1_BANDS[26]["b_exit"] == W26_B, \
    "leg3 failed: canon W26 row drift vs derived candidate"
assert N1_BANDS[26]["engine_owner"] == "bm-c", "leg3 failed: W26 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
print(f"leg1-A refusal facts: arithmetic {ARITH_A[0]}..{ARITH_A[1]} hits "
      f"probe seeds {a_hits}; leg1-B refusal facts: arithmetic "
      f"{ARITH_B[0]}..{ARITH_B[1]} hits points {b_hits} -- BOTH forced skip")
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} (jump target, "
      f"machine-derived), B {first_b[0]}..{first_b[1]} (jump target, "
      f"machine-derived)")
if conflicts:
    print("W26 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W26 ADMIT: A {W26_A[0]}..{W26_A[1]} + B {W26_B[0]}..{W26_B[1]} both "
      f"clean vs 24 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-c "
      f"(rotation law slot W26=bm-c; W25 row slot assignment verbatim; "
      f"BOTH tails forced-skip, A per the r335 probe-seed discovery + "
      f"B per the W25 row WARNING).")

# --- W27+ projection (warning text for the law table row) --------------------
w27_a = (W26_A[1] + 1, W26_A[1] + WIDTH_A)
w27_b = (W26_B[1] + 1, W26_B[1] + WIDTH_B)
a_hits27 = sorted(p for p in points if w27_a[0] <= p <= w27_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w27_a)]
b_hits27 = sorted(p for p in points if w27_b[0] <= p <= w27_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w27_b)]
print(f"W27+ projection: A arithmetic +2_000 = {w27_a[0]}..{w27_a[1]} "
      f"-> {'CLEAN (verify at W27 prereg)' if not a_hits27 else 'REFUSED ' + str(a_hits27)}; "
      f"B +200 from jump base = {w27_b[0]}..{w27_b[1]} "
      f"-> {'CLEAN (verify at W27 prereg)' if not b_hits27 else 'REFUSED ' + str(b_hits27)}")
