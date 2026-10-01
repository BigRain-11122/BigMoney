"""W33 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W33 = TWENTY-SECOND ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- bm-a's SEVENTH owned wave after W12/W18/W21/W24/
W27/W30). Sovereignty rotation law
F-20260901-01 slot: W33=bm-a per the law sec.4 W32 row verbatim (W30=bm-a
real anchor -- finalize landed bm-a r542, K=63,920; +3 -> W33=bm-a; slot
assignment = W32 row W33+ WARNING verbatim). r543 seat discipline consumed:
"W33=本机下槽（W32 行落地后接枪）" -- the W32 row landed on origin (bm-c r339
registered + burned 12/12 + ledger-appended); W31 seat closed (bm-b finalize,
K=66,120, ledger 432,748); the only open upstream face is the W32 finalize
(bm-c seat), which consumes nothing this freeze touches -- band-disjoint
coexistence per r531 (异带共存判据=带域机证不相交, this gate is that proof).

The W32 row's W33+ WARNING projects BOTH arithmetic tails CLEAN
(A +2_000 = 109_004..111_003, B +200 = 41_601..41_800). r335 lesson
(projections can carry scanning-universe blind spots) + r535 law
(clean-projection claims must be machine-derived, never prose-copied):
this gate re-derives from the live registry, never trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W32 (30
rows, W30/W31/W32 included -- this freeze reads the 30-row pre-W33
table plus the candidate), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every gate
receipt from W26 on), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r544 bm-a freeze-window run. Freeze trigger = never-dry supply law
standing step (engine alive status exit 0, heartbeat 26s, queue 0 --
W2..W31 all burned and finalized (chain head 432,748), W32 burned
12/12 + ledger-appended on origin (finalize pending at bm-c's seat);
board negative; rotation slot W33=bm-a; anti-idle root fix per
standing CEO full-mobilization law O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W33_A = (109_004, 111_003)              # law sec.4 W33 row (arithmetic, no skip)
W33_B = (41_601, 41_800)                # arithmetic, no skip

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
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W33 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 33:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (30 pre-W33 rows + the candidate) -----------------
assert 30 in N1_BANDS and N1_BANDS[30]["engine_owner"] == "bm-a", \
    "leg0 failed: W30 (bm-a) rows must be present (r541 freeze, r542 finalize)"
assert 31 in N1_BANDS and N1_BANDS[31]["engine_owner"] == "bm-b", \
    "leg0 failed: W31 (bm-b) rows must be present (r525 freeze, finalized)"
assert 32 in N1_BANDS and N1_BANDS[32]["engine_owner"] == "bm-c", \
    "leg0 failed: W32 (bm-c) rows must be present (r339 freeze, burned)"
pre_w33 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
           33]
assert sorted(N1_BANDS) == pre_w33, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"30 registered rows + the W33 candidate)"

# --- leg 0b: W32 row's W33+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "109_004..111_003" in canon and "41_601..41_800" in canon, \
    "leg0b failed: W32 row W33+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W32 row W33+ WARNING prose present (published projection "
      "= reserved-face basis, r518)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[32]["a"][1] + 1, N1_BANDS[32]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[32]["b_exit"][1] + 1,
           N1_BANDS[32]["b_exit"][1] + WIDTH_B)
# BOTH arithmetic tails projected CLEAN by the W32 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W32 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W32 "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W32 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W32 projection verified machine-side)")

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
assert first_a == W33_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W33_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=(W33_A,))
assert first_b == W33_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W33_B} " \
    "(no skip expected; own A band reserved per W6 law)"
assert not overlaps(W33_A, W33_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W33_A), ("B", W33_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 33:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W33-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W33-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W33-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W33-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W33-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W33-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W33-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W33-{tag} (r335 leg)")
# canon cross-check: the landed W33 row must equal the derived candidate
assert N1_BANDS[33]["a"] == W33_A and N1_BANDS[33]["b_exit"] == W33_B, \
    "leg3 failed: canon W33 row drift vs derived candidate"
assert N1_BANDS[33]["engine_owner"] == "bm-a", "leg3 failed: W33 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W33 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W33 ADMIT: A {W33_A[0]}..{W33_A[1]} + B {W33_B[0]}..{W33_B[1]} both "
      f"clean vs 30 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-a "
      f"(rotation law slot W33=bm-a; W32 row slot assignment verbatim; "
      f"arithmetic continuation BOTH tails, no skip -- W32 row W33+ "
      f"WARNING projection verified machine-side).")

# --- W34+ projection (warning text for the law table row) --------------------
w34_a = (W33_A[1] + 1, W33_A[1] + WIDTH_A)
w34_b = (W33_B[1] + 1, W33_B[1] + WIDTH_B)
a_hits34 = sorted(p for p in points if w34_a[0] <= p <= w34_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w34_a)]
b_hits34 = sorted(p for p in points if w34_b[0] <= p <= w34_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w34_b)]
print(f"W34+ projection: A arithmetic +2_000 = {w34_a[0]}..{w34_a[1]} "
      f"-> {'CLEAN (verify at W34 prereg)' if not a_hits34 else 'REFUSED ' + str(a_hits34)}; "
      f"B +200 from W33 end = {w34_b[0]}..{w34_b[1]} "
      f"-> {'CLEAN (verify at W34 prereg)' if not b_hits34 else 'REFUSED ' + str(b_hits34)}")
