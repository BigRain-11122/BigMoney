"""W31 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W31 = TWENTIETH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's NINTH owned wave after W10/W11/W13/W16/
W19/W22/W25/W28). Sovereignty rotation law F-20260901-01 slot W31=bm-b
per the W30 row's W31+ WARNING verbatim (W28=bm-b real anchor, bm-b
r524 finalize K=59,520; W29=bm-c SEATED AND FINALIZED MID-DRAFT
bm-c r337 -- K=61,720, ledger head 428,348 chain-linear; W30=bm-a
frozen r541 burn in flight -- registered in-use face; the +3
rotation continues -> W31=bm-b).

NO SKIP FACES this wave (both disclosed as clean projections by the
W30 row's W31+ WARNING and machine-verified here):

(1) W29 SEATED MID-DRAFT (bm-c r337, freeze+burn+finalize landed
    while this prereg was being drafted): W29 took its published
    projection window VERBATIM (A 101_004..103_003 / B 40_651..
    40_850) -- the r518 published=reserved law is hereby DISCHARGED
    for W29; its bands are now REGISTERED IN-USE rows (K=61,720,
    ledger head 428,348). W31's arithmetic continuation lands past
    them naturally -- leg1b proves clearance against the registered
    W29 bands (== the former projection, parity-checked).

(2) BOTH tails arithmetic-clean (first wave since W28 with zero
    forced skip on either side): A 105_004..107_003 == W30 A end + 1
    stride verbatim; B 41_201..41_400 == W30 B end + 1 stride
    verbatim. The W30 row's W31+ WARNING published exactly these
    windows -- the registry-derived arithmetic window must equal the
    published projection (leg1 prose/registry parity) and the first
    clean window scan must equal the candidate (leg2 -- published-
    clean is a prose claim until the machine gate re-derives it,
    r535 lesson).

Machine-verified against: all registered N1 wave bands W2..W28 +
W29 + W30 (28 rows -- this freeze reads the 28-row pre-W31 table
plus the candidate), the W29 registered bands (former published
projection, r518 discharge parity leg), the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 bm-a mandatory leg: every N1/N2/N4
band-gate receipt must carry the N3 used-seed leg), the runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg --
mandatory in every gate receipt from W26 on), v1 in-use + W1 ext
bands, SEED_REGISTRY live values, N2/N4 design-probe points
(40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r525 bm-b freeze-window run (re-run after the r337 integration -- W29
seated+finalized mid-draft on this window). Freeze trigger = never-dry
supply law standing step (engine alive status exit 0, queue depth 0 --
all ten bm-b-owned waves burned 12/12 and finalized; board zero bm-b
claimable tickets, pool ready=0; rotation slot W31=bm-b per the W30
row verbatim; anti-idle root fix per standing CEO full-mobilization
law O-20260930-1858 / O-20260930-2054; W30 bm-a r541 burn in flight
-- engine-wave ownership means zero cross-machine burn overlap by
construction, engine_owner filter is the lock).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W31_A = (105_004, 107_003)                # law sec.4 W31 row (arithmetic continuation)
W31_B = (41_201, 41_400)                  # law sec.4 W31 row (arithmetic continuation)

# --- W29 registered bands (bm-c r337 -- former published projection,
#     r518 published=reserved DISCHARGED: the seat took its projected
#     window verbatim; parity-checked here) -----------------------------
W29_PROJ_A = (101_004, 103_003)           # == N1_BANDS[29]["a"] (r337)
W29_PROJ_B = (40_651, 40_850)             # == N1_BANDS[29]["b_exit"] (r337)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)              # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg: mandatory in every
#     gate receipt from W26 on -- probe seeds are batch-band-reserved by the
#     selftest disjoint law; register the CONSUMED VALUE SET) -----------------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003

LFC_ACTUAL = (30_000, 30_099)             # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)         # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)        # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W31 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 31:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (28 pre-W31 rows + the candidate) -----------------
assert 28 in N1_BANDS and N1_BANDS[28]["engine_owner"] == "bm-b", \
    "leg0 failed: W28 (bm-b) rows must be present (r523 freeze, r524 finalize)"
assert 29 in N1_BANDS and N1_BANDS[29]["engine_owner"] == "bm-c", \
    "leg0 failed: W29 (bm-c) rows must be present (r337 seated+finalized " \
    "mid-draft); re-derive this gate if W29 is absent"
assert 30 in N1_BANDS and N1_BANDS[30]["engine_owner"] == "bm-a", \
    "leg0 failed: W30 (bm-a) rows must be present (r541 freeze, burn in flight)"
pre_w31 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
assert sorted(N1_BANDS) == pre_w31, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 28 " \
    f"registered rows + the W31 candidate)"

# --- leg 0b: the W30 canon row's published W31+ WARNING (prose face) --------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for needle in ("105_004..107_003", "41_201..41_400", "W31=bm-b"):
    assert needle in canon, \
        f"leg0b failed: W30 row W31+ WARNING prose drift -- {needle!r} absent"
print("leg0b W30-row W31+ WARNING prose present (projection + slot owner "
      "named -- published = reserved, r518)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
# ARITH = W30 registered-band tail + 1 on both sides; it must equal the
# W30 row's published W31+ WARNING window (prose/registry parity) AND
# the candidate (arithmetic continuation, zero forced skip this wave).
ARITH_A = (N1_BANDS[30]["a"][1] + 1, N1_BANDS[30]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[30]["b_exit"][1] + 1,
           N1_BANDS[30]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W31_A and ARITH_B == W31_B, \
    "leg1 failed: registry-derived arithmetic window != candidate " \
    "(prose/registry drift or hidden collision)"
print(f"leg1 registry-derived arithmetic window A {ARITH_A[0]}..{ARITH_A[1]} "
      f"/ B {ARITH_B[0]}..{ARITH_B[1]} == candidate == the W30 row's "
      f"published W31+ WARNING (arithmetic continuation, no skip face)")

# --- leg 1b: W29 registered-band clearance + r518 discharge parity -----------
# W29 (bm-c r337) took its published projection VERBATIM -- the registered
# band must equal the former projection (discharge parity), and W31 must
# clear it on both sides (also covered by the registered-row loop in leg3).
assert N1_BANDS[29]["a"] == W29_PROJ_A and \
    N1_BANDS[29]["b_exit"] == W29_PROJ_B, \
    "leg1b failed: W29 registered bands != its published projection " \
    "(r518 discharge parity broken -- re-derive from the r337 freeze)"
for tag, cand in (("A", W31_A), ("B", W31_B)):
    proj = W29_PROJ_A if tag == "A" else W29_PROJ_B
    assert not overlaps(cand, proj), \
        f"leg1b failed: W31-{tag} {cand[0]}..{cand[1]} overlaps the W29 " \
        f"registered band {proj[0]}..{proj[1]} (r337 in-use face)"
print("leg1b W29 registered bands == its published projection (r518 "
      "discharge parity) and W31 bands do NOT overlap them "
      "(A 101_004..103_003 / B 40_651..40_850 in-use)")

# --- leg 2: first clean window past the W30 bands (machine-derived) ----------
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

def first_clean(start, width, extra=()):
    lo = start
    for _ in range(1000):
        w = clean(lo, width, extra)
        if w is not None:
            return w
        blocking = sorted(p for p in points if lo <= p <= lo + width - 1)
        lo = (blocking[-1] + 1) if blocking else lo + width
    return None

first_a = first_clean(N1_BANDS[30]["a"][1] + 1, WIDTH_A)
assert first_a == W31_A, \
    f"leg2-A failed: first clean window past the W30 A band {first_a} " \
    f"!= candidate {W31_A} (candidate must be the machine-derived window)"
print(f"leg2-A first clean window past W30 A = {first_a[0]}..{first_a[1]} "
      f"== candidate (arithmetic stride kept verbatim, no skip)")
first_b = first_clean(N1_BANDS[30]["b_exit"][1] + 1, WIDTH_B, extra=(W31_A,))
assert first_b == W31_B, \
    f"leg2-B failed: first clean window past the W30 B band {first_b} " \
    f"!= candidate {W31_B} (candidate must be the machine-derived window)"
print(f"leg2-B first clean window past W30 B = {first_b[0]}..{first_b[1]} "
      f"== candidate (arithmetic stride kept verbatim, no skip)")
assert not overlaps(W31_A, W31_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W31_A), ("B", W31_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 31:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W31-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W31-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W31-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W31-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W31-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W31-{tag} (r335 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W31-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W31-{tag} (MSG-183x mandatory leg)")
    for nm, proj in (("W29-band-A", W29_PROJ_A), ("W29-band-B", W29_PROJ_B)):
        if overlaps(proj, band):
            conflicts.append(f"{nm} {proj[0]}..{proj[1]} x W31-{tag} "
                             f"(r337 in-use face, r518 discharge)")
# canon cross-check: the landed W31 row must equal the derived candidate
assert N1_BANDS[31]["a"] == W31_A and N1_BANDS[31]["b_exit"] == W31_B, \
    "leg3 failed: canon W31 row drift vs derived candidate"
assert N1_BANDS[31]["engine_owner"] == "bm-b", "leg3 failed: W31 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
print("leg1b W29 registered-band discharge parity leg + leg2 machine-derived "
      "windows both faces green (zero forced skip this wave -- first since W28)")
if conflicts:
    print("W31 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W31 ADMIT: A {W31_A[0]}..{W31_A[1]} + B {W31_B[0]}..{W31_B[1]} both "
      f"clean vs 28 registered rows (incl. W29 seated r337 + W30 in-flight) "
      f"+ N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-b (rotation law slot W31=bm-b; "
      f"W30 row slot assignment verbatim; both tails arithmetic "
      f"continuation, zero skip face; W29 r518 discharge parity verified).")

# --- W32+ projection (warning text for the law table row) --------------------
w32_a = (W31_A[1] + 1, W31_A[1] + WIDTH_A)
w32_b = (W31_B[1] + 1, W31_B[1] + WIDTH_B)
a_hits32 = sorted(p for p in points if w32_a[0] <= p <= w32_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w32_a)]
b_hits32 = sorted(p for p in points if w32_b[0] <= p <= w32_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w32_b)]
print(f"W32+ projection: A arithmetic +2_000 = {w32_a[0]}..{w32_a[1]} "
      f"-> {'CLEAN (verify at W32 prereg)' if not a_hits32 else 'REFUSED ' + str(a_hits32)}; "
      f"B +200 = {w32_b[0]}..{w32_b[1]} "
      f"-> {'CLEAN (verify at W32 prereg)' if not b_hits32 else 'REFUSED ' + str(b_hits32)} "
      f"(rotation slot W32=bm-c)")
