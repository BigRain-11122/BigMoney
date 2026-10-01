"""W30 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W30 = NINETEENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- bm-a's SIXTH owned wave after W12/W18/W21/W24/W27).
Sovereignty rotation law F-20260901-01 slot: W30=bm-a per the W28 row
slot assignment verbatim (W27=bm-a real anchor -- finalize landed bm-a
r540, K=57,320, ledger 423,948 chain head; W28=bm-b / W29=bm-c seats
continue the +3 rotation -> W30=bm-a).

SKIP FACES (both disclosed, r518 + W26-B precedent families):

(1) W29 PUBLISHED-PROJECTION RESERVATION (r518: published projection =
    reserved face). W29 (bm-c seat) is NOT registered at this freeze,
    but the W28 row's W29+ WARNING publishes its arithmetic window
    (A 101_004..103_003 / B 40_651..40_850) AND names the rotation
    slot owner (W29=bm-c). The gate writes that projected window into
    the reserved universe as REFUSAL facts -- W30 may not take it
    (taking it would manufacture a third-collision face on the bm-c
    seat exactly as the re-based W17-v2 would have done on bm-a's W18,
    r518 lesson ①).

(2) B-side IN-BAND POINT SKIP (W26 B re-base lineage). The arithmetic
    window from the W29 projected B tail + 1 (40_851..41_050) contains
    SEED_REGISTRY p4_batch1=41_000 -> advance to the first clean
    200-wide window: 41_001..41_200 (41_000 below-band, p4_folk=43_000
    above-band; same family as W26 B skipping 40_000/40_001/40_050).

A side: first clean window past the W29 projected A tail = 103_004..
105_003, no further skip (all registry values sit below 103_004; the
N1 A ladder tops out at W28's 101_003).

Machine-verified against: all registered N1 wave bands W2..W28 (26
rows, W23/W24/W25/W26/W27/W28 included -- this freeze reads the 26-row
pre-W30 table plus the candidate), the W29 published projection bands,
the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 bm-a mandatory
leg: every N1/N2/N4 band-gate receipt must carry the N3 used-seed
leg), the runner design-probe seed cluster 95_000..95_003 (r335
discovery leg -- mandatory in every gate receipt from W26 on), v1
in-use + W1 ext bands, SEED_REGISTRY live values (incl. p4_batch1=
41_000), N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r541 bm-a freeze-window run. Freeze trigger = never-dry supply law
standing step (engine alive status exit 0, heartbeat 8s, queue 0 after
the W27 finalize on this machine r540 -- all bm-a-registered waves
burned, board negative, pool ready=0, rotation slot W30=bm-a; anti-idle
root fix per standing CEO full-mobilization law O-20260930-1858 /
O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W30_A = (103_004, 105_003)                # law sec.4 W30 row (skip past W29 projection)
W30_B = (41_001, 41_200)                  # law sec.4 W30 row (skip past p4_batch1=41_000)

# --- W29 published projection (W28 row W29+ WARNING; bm-c rotation slot) ---
W29_PROJ_A = (101_004, 103_003)           # published = reserved face (r518)
W29_PROJ_B = (40_651, 40_850)             # published = reserved face (r518)

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

# --- reserved universe (W30 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 30:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
reserved_projections = [("W29 published projection (r518 reserved face)", W29_PROJ_A),
                        ("W29 published projection (r518 reserved face)", W29_PROJ_B)]
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (26 pre-W30 rows + the candidate) ------------------
assert 27 in N1_BANDS and N1_BANDS[27]["engine_owner"] == "bm-a", \
    "leg0 failed: W27 (bm-a) rows must be present (r539 freeze, r540 finalize)"
assert 28 in N1_BANDS and N1_BANDS[28]["engine_owner"] == "bm-b", \
    "leg0 failed: W28 (bm-b) rows must be present (r523 freeze)"
assert 29 not in N1_BANDS, \
    "leg0 failed: W29 is expected UNREGISTERED at this freeze (bm-c seat " \
    "pending); if W29 has landed, re-derive this gate from the new tail"
pre_w30 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30]
assert sorted(N1_BANDS) == pre_w30, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 26 " \
    f"registered rows + the W30 candidate)"

# --- leg 0b: the W28 canon row's published W29+ WARNING (prose face) ---------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for needle in ("101_004..103_003", "40_651..40_850", "W29=bm-c"):
    assert needle in canon, \
        f"leg0b failed: W28 row W29+ WARNING prose drift -- {needle!r} absent"
print("leg0b W28-row W29+ WARNING prose present (projection + slot owner "
      "named -- published = reserved, r518)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
# ARITH = the W29 published projection window (tail + 1 on both sides);
# machine-verify it equals the published reservation before skipping it.
ARITH_A = (N1_BANDS[28]["a"][1] + 1, N1_BANDS[28]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[28]["b_exit"][1] + 1,
           N1_BANDS[28]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W29_PROJ_A and ARITH_B == W29_PROJ_B, \
    "leg1 failed: registry-derived arithmetic window != the W28 row's " \
    "published W29+ projection (prose/registry drift)"
print(f"leg1 registry-derived arithmetic window A {ARITH_A[0]}..{ARITH_A[1]} "
      f"/ B {ARITH_B[0]}..{ARITH_B[1]} == the published W29 projection "
      f"(bm-c rotation slot) -> RESERVED for W29, W30 must skip (r518)")

# --- leg 1b: W29 projection reservation leg (refusal facts) ------------------
for tag, cand in (("A", W30_A), ("B", W30_B)):
    proj = W29_PROJ_A if tag == "A" else W29_PROJ_B
    assert not overlaps(cand, proj), \
        f"leg1b failed: W30-{tag} {cand[0]}..{cand[1]} overlaps the W29 " \
        f"published projection {proj[0]}..{proj[1]} (reserved face, r518)"
print("leg1b W30 bands do NOT overlap the W29 published projection "
      "(A 101_004..103_003 / B 40_651..40_850 reserved for the bm-c seat)")

# --- leg 2: first clean window past the W29 projection (machine-derived) -----
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

first_a = first_clean(W29_PROJ_A[1] + 1, WIDTH_A)
assert first_a == W30_A, \
    f"leg2-A failed: first clean window past the W29 projection {first_a} " \
    f"!= candidate {W30_A} (candidate must be the machine-derived window)"
print(f"leg2-A first clean window past W29 projection = "
      f"{first_a[0]}..{first_a[1]} == candidate (no further skip)")
first_b = first_clean(W29_PROJ_B[1] + 1, WIDTH_B, extra=(W30_A,))
assert first_b == W30_B, \
    f"leg2-B failed: first clean window past the W29 projection {first_b} " \
    f"!= candidate {W30_B} (expected the 41_000 in-band skip)"
assert W30_B[0] == 41_001, \
    "leg2-B failed: B start must be p4_batch1=41_000 + 1 (in-band point " \
    "skip, W26-B re-base lineage)"
print(f"leg2-B arithmetic window 40_851..41_050 REFUSED (hits "
      f"SEED_REGISTRY p4_batch1=41_000) -> first clean window "
      f"{first_b[0]}..{first_b[1]} == candidate (in-band skip)")
assert not overlaps(W30_A, W30_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ---------------
conflicts = []
for tag, band in (("A", W30_A), ("B", W30_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 30:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W30-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W30-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W30-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W30-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W30-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W30-{tag} (r335 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W30-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W30-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W30 row must equal the derived candidate
assert N1_BANDS[30]["a"] == W30_A and N1_BANDS[30]["b_exit"] == W30_B, \
    "leg3 failed: canon W30 row drift vs derived candidate"
assert N1_BANDS[30]["engine_owner"] == "bm-a", "leg3 failed: W30 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
print(f"leg1b/leg2 both skip faces machine-derived (W29 projection reserved "
      f"r518 + B-side 41_000 in-band skip): A {first_a[0]}..{first_a[1]}, "
      f"B {first_b[0]}..{first_b[1]}")
if conflicts:
    print("W30 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W30 ADMIT: A {W30_A[0]}..{W30_A[1]} + B {W30_B[0]}..{W30_B[1]} both "
      f"clean vs 26 registered rows + W29 published projection (reserved) "
      f"+ N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-a (rotation law slot W30=bm-a; "
      f"W28 row slot assignment verbatim; A skip past W29 projection, "
      f"B skip past p4_batch1=41_000).")

# --- W31+ projection (warning text for the law table row) ---------------------
w31_a = (W30_A[1] + 1, W30_A[1] + WIDTH_A)
w31_b = (W30_B[1] + 1, W30_B[1] + WIDTH_B)
a_hits31 = sorted(p for p in points if w31_a[0] <= p <= w31_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w31_a)]
b_hits31 = sorted(p for p in points if w31_b[0] <= p <= w31_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w31_b)]
print(f"W31+ projection: A arithmetic +2_000 = {w31_a[0]}..{w31_a[1]} "
      f"-> {'CLEAN (verify at W31 prereg)' if not a_hits31 else 'REFUSED ' + str(a_hits31)}; "
      f"B +200 = {w31_b[0]}..{w31_b[1]} "
      f"-> {'CLEAN (verify at W31 prereg)' if not b_hits31 else 'REFUSED ' + str(b_hits31)} "
      f"(rotation slot W31=bm-b)")
