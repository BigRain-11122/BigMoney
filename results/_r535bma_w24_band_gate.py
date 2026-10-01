"""W24 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W24 = THIRTEENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-a
-- bm-a's FOURTH owned wave after W12/W18/W21). Sovereignty rotation law
F-20261001-01 slot: W24=bm-a per the law sec.4 W23 row verbatim (W21=bm-a
anchored -- finalize landed bm-a r534, K=44,120, ledger 410,748; +3 ->
W24=bm-a). No pointer gate is pending: W22 is registered + burned + FINALIZED
(bm-b r519 addendum, K=46,320, ledger 412,948 chain head); W23 is registered
(bm-c r332, engine burn pending on bm-c) -- coexistence is judged by band
disjointness, not commit order (r531 law).

The W23 row's W24+ WARNING projection fires in the BOTH-CLEAN form:
  A +2_000 arithmetic tail (90_001..92_000 == W23 A end + 1) -- projected
  CLEAN, stride kept verbatim (no skip);
  B +200 arithmetic tail (39_500..39_699 == W23 B end + 1) -- projected
  CLEAN, stride kept verbatim (no skip); 39k-segment continuation noted
  (W17 B re-base lineage). Machine-derived here -- the landing is NEVER a
  free pick (R250).

Machine-verified against: all registered N1 wave bands W2..W23 (22 rows,
W18/W19/W20/W21/W22/W23 included -- this freeze reads the 22-row pre-W24
table plus the candidate), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x
r529 bm-a mandatory leg: every N1/N2/N4 band-gate receipt must carry the
N3 used-seed leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values,
N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe points
(31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r535 bm-a freeze-window run. Freeze trigger = never-dry supply law standing
step (engine alive status exit 0, queue 0 after the W21 closeout on this
machine, board negative -- open slices all held by other lanes, pool
next_pick=claimed, zero unclaimed fleet tickets; rotation slot W24=bm-a;
anti-idle root fix per standing CEO full-mobilization law O-20260930-1858 /
O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W24_A = (90_001, 92_000)                # law sec.4 W24 row
W24_B = (39_500, 39_699)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

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

# --- reserved universe (W24 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 24:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (22 pre-W24 rows + the candidate) ------------------
assert 21 in N1_BANDS and N1_BANDS[21]["engine_owner"] == "bm-a", \
    "leg0 failed: W21 (bm-a) rows must be present (r533 freeze, r534 finalize)"
assert 22 in N1_BANDS and N1_BANDS[22]["engine_owner"] == "bm-b", \
    "leg0 failed: W22 (bm-b) rows must be present (r519 freeze/addendum)"
assert 23 in N1_BANDS and N1_BANDS[23]["engine_owner"] == "bm-c", \
    "leg0 failed: W23 (bm-c) rows must be present (r332 freeze)"
assert sorted(N1_BANDS) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                            16, 17, 18, 19, 20, 21, 22, 23, 24], \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
# continuation = W23 registered tail + 1 on both sides (law sec.4 stride)
ARITH_A = (N1_BANDS[23]["a"][1] + 1, N1_BANDS[23]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[23]["b_exit"][1] + 1,
           N1_BANDS[23]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W24_A, \
    f"leg1-A failed: registry-derived arithmetic tail {ARITH_A} != candidate " \
    f"{W24_A} (re-derive, do not free-pick; R250)"
assert ARITH_B == W24_B, \
    f"leg1-B failed: registry-derived arithmetic tail {ARITH_B} != candidate " \
    f"{W24_B} (re-derive, do not free-pick; R250)"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert not a_hits, f"leg1-A failed: arithmetic tail point hits {a_hits}"
assert not b_hits, f"leg1-B failed: arithmetic tail point hits {b_hits}"
reg_conflicts = []
for b in bands + actual:
    if overlaps(b, ARITH_A) or overlaps(b, ARITH_B):
        reg_conflicts.append(f"band {b}")
assert not reg_conflicts, \
    f"leg1 failed: arithmetic position dirty vs registered faces: {reg_conflicts}"

# --- leg 2: first clean window == arithmetic (no skip FORCED, R250) ----------
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
assert first_a == W24_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W24_A} " \
    "(skip would be FORCED -- re-derive, do not free-pick; R250)"
first_b = None
x = ARITH_B[0]
while x < 20_260_000:
    r = clean(x, WIDTH_B, extra=(W24_A,))   # own A band reserved (W6 law)
    if r:
        first_b = r
        break
    x += 1
assert first_b, "no clean 200-window found below 20260000"
assert first_b == W24_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W24_B}"
assert not overlaps(W24_A, W24_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W24_A), ("B", W24_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 24:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W24-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W24-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W24-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W24-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W24-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W24-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W24-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W24 row must equal the derived candidate
assert N1_BANDS[24]["a"] == W24_A and N1_BANDS[24]["b_exit"] == W24_B, \
    "leg3 failed: canon W24 row drift vs derived candidate"
assert N1_BANDS[24]["engine_owner"] == "bm-a", "leg3 failed: W24 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg)")
print(f"leg1 registry-derived arithmetic tails BOTH CLEAN: "
      f"A {ARITH_A[0]}..{ARITH_A[1]} (W23 A end + 1) / "
      f"B {ARITH_B[0]}..{ARITH_B[1]} (W23 B end + 1) -- no skip on either side")
print(f"leg2 first clean windows == arithmetic candidates (derive, R250): "
      f"A {first_a[0]}..{first_a[1]}, B {first_b[0]}..{first_b[1]}")
if conflicts:
    print("W24 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W24 ADMIT: A {W24_A[0]}..{W24_A[1]} + B {W24_B[0]}..{W24_B[1]} both "
      f"clean vs 22 registered rows + N3-R1 used-seed band + registry values "
      f"+ probes/actuals -- engine_owner=bm-a (rotation law slot W24=bm-a; "
      f"W23 row slot assignment verbatim).")

# --- W25+ projection (warning text for the law table row) --------------------
w25_a = (W24_A[1] + 1, W24_A[1] + WIDTH_A)
w25_b = (W24_B[1] + 1, W24_B[1] + WIDTH_B)
a_hits25 = sorted(p for p in points if w25_a[0] <= p <= w25_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w25_a)]
b_hits25 = sorted(p for p in points if w25_b[0] <= p <= w25_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w25_b)]
print(f"W25+ projection: A arithmetic +2_000 = {w25_a[0]}..{w25_a[1]} "
      f"-> {'CLEAN (verify at W25 prereg)' if not a_hits25 else 'REFUSED ' + str(a_hits25)}; "
      f"B +200 = {w25_b[0]}..{w25_b[1]} "
      f"-> {'CLEAN (verify at W25 prereg)' if not b_hits25 else 'REFUSED ' + str(b_hits25)}")
