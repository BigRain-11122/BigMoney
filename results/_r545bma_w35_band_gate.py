"""W35 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W35 = TWENTY-FOURTH ENGINE-OWNED WAVE, bm-a's EIGHTH owned wave after
W12/W18/W21/W24/W27/W30/W33 -- the FIRST bm-a wave under the engine
de-throttle law O-20261001-2355 sec.2 (per-machine self-owned continuous
series: the machine's previous wave W33 closed (finalize landed bm-a r544,
K=70,520, ledger 437,148 chain-linear) -> zero-gap relay to the next wave;
seat system retired by the same order).

Wave number 35 = next free number after W34's published claim: bm-b's
pre-scan ADMIT-READY receipt (r527, on origin) holds W34 bands
A 111_004..113_003 / B 41_801..42_000 with the freeze pending at the bm-b
seat. Per r518 (published projection = reserved face; skip positions must
be machine-proven forced, never prose-copied), those windows are REFUSED
for this wave and the candidate lands at the first clean window after
them: A 113_004..115_003 / B 42_001..42_200 (== W34 published projection
end + 1 on both sides).

Machine-verified against: all registered N1 wave bands W2..W33 (30 rows,
no W34 row in the registry yet -- the W33 row's W34+ WARNING published
projection is asserted present in the canon prose and carried as a
reserved face), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg -- mandatory on every gate receipt from W26 on),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points (40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r545 bm-a freeze-window run. Freeze trigger = engine de-throttle law
O-20261001-2355 sec.2 (cores idle with engine alive = red flag; own
continuous series materializes immediately) + never-dry supply law
standing step (board negative; W33 closed same machine).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W35_A = (113_004, 115_003)              # first clean window AFTER the W34 projection
W35_B = (42_001, 42_200)                # == W34 published B end + 1

# --- W34 PUBLISHED PROJECTION (bm-b pre-scan ADMIT-READY r527) -------------
# r518 law: published projection = reserved face. The W33 row's W34+
# WARNING in the canon file publishes exactly these windows; bm-b's r527
# pre-scan receipt ADMIT-READY'd them (freeze pending at the bm-b seat).
W34_PROJ_A = (111_004, 113_003)
W34_PROJ_B = (41_801, 42_000)
PUBLISHED = [W34_PROJ_A, W34_PROJ_B]

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) ----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) -------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

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

# --- reserved universe (W35 itself EXCLUDED -- it is the candidate) --------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 35:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (30 pre-W35 rows + the candidate; NO W34 row) ---
assert 30 in N1_BANDS and N1_BANDS[30]["engine_owner"] == "bm-a", \
    "leg0 failed: W30 (bm-a) rows must be present (r541 freeze, r542 finalize)"
assert 31 in N1_BANDS and N1_BANDS[31]["engine_owner"] == "bm-b", \
    "leg0 failed: W31 (bm-b) rows must be present (r525 freeze, finalized)"
assert 32 in N1_BANDS and N1_BANDS[32]["engine_owner"] == "bm-c", \
    "leg0 failed: W32 (bm-c) rows must be present (r339 freeze, finalized)"
assert 33 in N1_BANDS and N1_BANDS[33]["engine_owner"] == "bm-a", \
    "leg0 failed: W33 (bm-a) rows must be present (r544 full closeout)"
assert 34 not in N1_BANDS, \
    "leg0 failed: W34 row unexpectedly present in the registry -- re-run " \
    "this gate only after reconciling with bm-b's freeze (r239 collision law)"
pre_w35 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 35]
assert sorted(N1_BANDS) == pre_w35, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 31 " \
    f"registered rows + the W35 candidate, no 15, no 34)"

# --- leg 0b: W33 row's W34+ WARNING prose present in the canon law file ---
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "111_004..113_003" in canon and "41_801..42_000" in canon, \
    "leg0b failed: W33 row W34+ WARNING (published projection) prose " \
    "not found in the canon file -- the published-projection reserved " \
    "face basis (r518) must be canon-visible"
print("leg0b W33 row W34+ WARNING prose present (published projection "
      "= reserved-face basis, r518; wave 34 = bm-b pre-scan ADMIT-READY "
      "receipt r527, freeze pending at the bm-b seat)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -----
ARITH_A = (N1_BANDS[33]["a"][1] + 1, N1_BANDS[33]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[33]["b_exit"][1] + 1,
           N1_BANDS[33]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W34_PROJ_A and ARITH_B == W34_PROJ_B, \
    "leg1 failed: arithmetic tail != W34 published projection (drift)"
# The arithmetic windows ARE the published W34 projection -> REFUSED for
# this wave (reserved face per r518): machine-proof the forced skip.
for tag, band in (("A", ARITH_A), ("B", ARITH_B)):
    hit_pub = [pb for pb in PUBLISHED if overlaps(pb, band)]
    assert hit_pub, \
        f"leg1-{tag} failed: arithmetic window {band} does not overlap " \
        f"any published projection -- the skip would NOT be forced (free " \
        f"choice forbidden, r518)"
print(f"leg1 arithmetic windows A {ARITH_A[0]}..{ARITH_A[1]} / B "
      f"{ARITH_B[0]}..{ARITH_B[1]} == W34 published projection -> "
      f"REFUSED (reserved face, r518; skip forced machine-proven)")

# --- leg 2: first clean window AFTER the published projection == candidate -
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first_a = clean(ARITH_A[1] + 1, WIDTH_A, extra=PUBLISHED)
assert first_a == W35_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W35_A} " \
    f"(forced skip over the published W34 projection only)"
first_b = clean(ARITH_B[1] + 1, WIDTH_B, extra=PUBLISHED + [W35_A])
assert first_b == W35_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W35_B} " \
    f"(no further skip expected; own A band reserved per W6 law)"
assert not overlaps(W35_A, W35_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ---------------
conflicts = []
for tag, band in (("A", W35_A), ("B", W35_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 35:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W35-{tag}")
    for pb in PUBLISHED:
        if overlaps(pb, band):
            conflicts.append(f"W34 published projection {pb[0]}..{pb[1]} "
                             f"x W35-{tag} (r518 reserved face)")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W35-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W35-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W35-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W35-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W35-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W35-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W35-{tag} (r335 leg)")
# canon cross-check: the landed W35 row must equal the derived candidate
assert N1_BANDS[35]["a"] == W35_A and N1_BANDS[35]["b_exit"] == W35_B, \
    "leg3 failed: canon W35 row drift vs derived candidate"
assert N1_BANDS[35]["engine_owner"] == "bm-a", "leg3 failed: W35 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W35 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W35 ADMIT: A {W35_A[0]}..{W35_A[1]} + B {W35_B[0]}..{W35_B[1]} both "
      f"clean vs 31 registered rows + W34 published projection (reserved "
      f"face, r518) + N3-R1 used-seed band + probe-seed cluster + registry "
      f"values + probes/actuals -- engine_owner=bm-a (de-throttle law "
      f"O-20261001-2355 sec.2 own-continuous-series, zero-gap relay after "
      f"W33 close; forced skip over the published W34 projection windows, "
      f"machine-proven; wave 35 = first free number after W34's claim).")

# --- W36+ projection (warning text for the law table row) -------------------
w36_a = (W35_A[1] + 1, W35_A[1] + WIDTH_A)
w36_b = (W35_B[1] + 1, W35_B[1] + WIDTH_B)
a_hits36 = sorted(p for p in points if w36_a[0] <= p <= w36_a[1]) or [
    f"band {b}" for b in bands + actual + PUBLISHED if overlaps(b, w36_a)]
b_hits36 = sorted(p for p in points if w36_b[0] <= p <= w36_b[1]) or [
    f"band {b}" for b in bands + actual + PUBLISHED if overlaps(b, w36_b)]
print(f"W36+ projection: A +2_000 = {w36_a[0]}..{w36_a[1]} "
      f"-> {'CLEAN (verify at W36 prereg)' if not a_hits36 else 'REFUSED ' + str(a_hits36)}; "
      f"B +200 from W35 end = {w36_b[0]}..{w36_b[1]} "
      f"-> {'CLEAN (verify at W36 prereg)' if not b_hits36 else 'REFUSED ' + str(b_hits36)}")
