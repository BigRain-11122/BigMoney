"""W29 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W29 = EIGHTEENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-c
-- bm-c's SIXTH owned wave after W14/W17/W20/W23/W26). Sovereignty rotation law
F-20261001-01 slot: W29=bm-c per the law sec.4 W28 row verbatim (W26=bm-c
anchored -- finalize landed bm-c r336, K=55,120, ledger 421,748 chain head;
+3 -> W29=bm-c). No pointer gate is pending: W27 registered + burned 12/12
by bm-a r539 (finalize pending on the bm-a seat -- chain-unblocked by the
W26 finalize landing), W28 registered by bm-b r523 (burn in progress on
bm-b) -- coexistence is judged by band disjointness, not commit order
(r531 law).

The W28 row's W29+ WARNING projects BOTH arithmetic tails CLEAN
(A +2_000 = 101_004..103_003, B +200 = 40_651..40_850). r335 lesson
(projections can carry scanning-universe blind spots): this gate
re-derives from the live registry, never trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W28 (27 rows,
W26/W27/W28 included -- this freeze reads the 27-row pre-W29 table plus
the candidate), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
bm-a mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg -- mandatory on every gate receipt from W26 on),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points (40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r336 bm-c freeze-window run. Freeze trigger = never-dry supply law standing
step (engine alive status exit 0, queue 0 after the W26 closeout on this
machine, board negative, rotation slot W29=bm-c; anti-idle root fix per
standing CEO full-mobilization law O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W29_A = (101_004, 103_003)              # law sec.4 W29 row (arithmetic, no skip)
W29_B = (40_651, 40_850)                # arithmetic, no skip

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
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

# --- reserved universe (W29 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 29:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (27 pre-W29 rows + the candidate) ------------------
assert 26 in N1_BANDS and N1_BANDS[26]["engine_owner"] == "bm-c", \
    "leg0 failed: W26 (bm-c) rows must be present (r335 freeze, r336 finalize)"
assert 27 in N1_BANDS and N1_BANDS[27]["engine_owner"] == "bm-a", \
    "leg0 failed: W27 (bm-a) rows must be present (r539 freeze)"
assert 28 in N1_BANDS and N1_BANDS[28]["engine_owner"] == "bm-b", \
    "leg0 failed: W28 (bm-b) rows must be present (r523 freeze)"
pre_w29 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
assert sorted(N1_BANDS) == pre_w29, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"27 registered rows + the W29 candidate)"

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[28]["a"][1] + 1, N1_BANDS[28]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[28]["b_exit"][1] + 1,
           N1_BANDS[28]["b_exit"][1] + WIDTH_B)
# BOTH arithmetic tails projected CLEAN by the W28 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W28 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W28 projection verified)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W28 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W28 projection verified)")

# --- leg 2: first clean window == arithmetic position (NO skip either side) --
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
assert first_a == W29_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W29_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=(W29_A,))
assert first_b == W29_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W29_B} " \
    "(no skip expected; own A band reserved per W6 law)"
assert not overlaps(W29_A, W29_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W29_A), ("B", W29_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 29:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W29-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W29-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W29-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W29-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W29-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W29-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W29-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W29-{tag} (r335 leg)")
# canon cross-check: the landed W29 row must equal the derived candidate
assert N1_BANDS[29]["a"] == W29_A and N1_BANDS[29]["b_exit"] == W29_B, \
    "leg3 failed: canon W29 row drift vs derived candidate"
assert N1_BANDS[29]["engine_owner"] == "bm-c", "leg3 failed: W29 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W29 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W29 ADMIT: A {W29_A[0]}..{W29_A[1]} + B {W29_B[0]}..{W29_B[1]} both "
      f"clean vs 27 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-c "
      f"(rotation law slot W29=bm-c; W28 row slot assignment verbatim; "
      f"arithmetic continuation BOTH tails, no skip -- W28 row W29+ "
      f"WARNING projection verified machine-side).")

# --- W30+ projection (warning text for the law table row) --------------------
w30_a = (W29_A[1] + 1, W29_A[1] + WIDTH_A)
w30_b = (W29_B[1] + 1, W29_B[1] + WIDTH_B)
a_hits30 = sorted(p for p in points if w30_a[0] <= p <= w30_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w30_a)]
b_hits30 = sorted(p for p in points if w30_b[0] <= p <= w30_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w30_b)]
print(f"W30+ projection: A arithmetic +2_000 = {w30_a[0]}..{w30_a[1]} "
      f"-> {'CLEAN (verify at W30 prereg)' if not a_hits30 else 'REFUSED ' + str(a_hits30)}; "
      f"B +200 from W29 end = {w30_b[0]}..{w30_b[1]} "
      f"-> {'CLEAN (verify at W30 prereg)' if not b_hits30 else 'REFUSED ' + str(b_hits30)}")
