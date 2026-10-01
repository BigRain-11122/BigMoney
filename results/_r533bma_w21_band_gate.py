"""W21 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W21 = TENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-a
-- bm-a's THIRD owned wave after W12/W18). Sovereignty rotation law
F-20261001-01 slot: W21=bm-a per the law sec.4 W20 row verbatim (W18=bm-a
anchored, +3 -> W21=bm-a). No pointer gate is pending: W20 is registered and
burned (12/12 shards on origin, bm-c r330); its finalize is sequenced by the
registry chain order and lands independently of this freeze.

The W20 row's W21+ WARNING projection fires in the BOTH-CLEAN form:
  A +2_000 arithmetic tail (84_001..86_000 == W20 A end + 1) -- projected
  CLEAN, stride kept verbatim (no skip);
  B +200 arithmetic tail (38_900..39_099 == W20 B end + 1) -- projected
  CLEAN, stride kept verbatim (no skip); 38k-segment continuation noted
  (W17 B re-base lineage). Machine-derived here -- the landing is NEVER a
  free pick (R250).

Machine-verified against: all registered N1 wave bands W2..W20 (19 rows,
W18/W19/W20 included -- this freeze reads the 19-row pre-W21 table plus the
candidate), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 bm-a
mandatory leg: every N1/N2/N4 band-gate receipt must carry the N3 used-seed
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points (40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r533 bm-a freeze-window run. Freeze trigger = never-dry supply law standing
step (engine alive status exit 0, queue 0 after the W18 closeout on this
machine, board negative -- open slices all held by other lanes, pool
next_pick=claimed, zero unclaimed fleet tickets, pool ready=0 starvation
flag = W14-GENERATE governance-park known-state; rotation slot W21=bm-a;
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
W21_A = (84_001, 86_000)                # law sec.4 W21 row
W21_B = (38_900, 39_099)

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

# --- reserved universe (W21 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 21:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (19 pre-W21 rows + the candidate) ------------------
assert 18 in N1_BANDS and N1_BANDS[18]["engine_owner"] == "bm-a", \
    "leg0 failed: W18 (bm-a) rows must be present (r531 freeze)"
assert 19 in N1_BANDS and N1_BANDS[19]["engine_owner"] == "bm-b", \
    "leg0 failed: W19 (bm-b) re-band rows must be present (r517/518 yield)"
assert 20 in N1_BANDS and N1_BANDS[20]["engine_owner"] == "bm-c", \
    "leg0 failed: W20 (bm-c) rows must be present (r330 freeze)"
assert sorted(N1_BANDS) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                            16, 17, 18, 19, 20, 21], \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
# continuation = W20 registered tail + 1 on both sides (law sec.4 stride)
ARITH_A = (N1_BANDS[20]["a"][1] + 1, N1_BANDS[20]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[20]["b_exit"][1] + 1,
           N1_BANDS[20]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W21_A, \
    f"leg1-A failed: registry-derived arithmetic tail {ARITH_A} != candidate " \
    f"{W21_A} (re-derive, do not free-pick; R250)"
assert ARITH_B == W21_B, \
    f"leg1-B failed: registry-derived arithmetic tail {ARITH_B} != candidate " \
    f"{W21_B} (re-derive, do not free-pick; R250)"
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
assert first_a == W21_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W21_A} " \
    "(skip would be FORCED -- re-derive, do not free-pick; R250)"
first_b = None
x = ARITH_B[0]
while x < 20_260_000:
    r = clean(x, WIDTH_B, extra=(W21_A,))   # own A band reserved (W6 law)
    if r:
        first_b = r
        break
    x += 1
assert first_b, "no clean 200-window found below 20260000"
assert first_b == W21_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W21_B}"
assert not overlaps(W21_A, W21_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W21_A), ("B", W21_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 21:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W21-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W21-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W21-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W21-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W21-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W21-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W21-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W21 row must equal the derived candidate
assert N1_BANDS[21]["a"] == W21_A and N1_BANDS[21]["b_exit"] == W21_B, \
    "leg3 failed: canon W21 row drift vs derived candidate"
assert N1_BANDS[21]["engine_owner"] == "bm-a", "leg3 failed: W21 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg)")
print(f"leg1 registry-derived arithmetic tails BOTH CLEAN: "
      f"A {ARITH_A[0]}..{ARITH_A[1]} (W20 A end + 1) / "
      f"B {ARITH_B[0]}..{ARITH_B[1]} (W20 B end + 1) -- no skip on either side")
print(f"leg2 first clean windows == arithmetic candidates (derive, R250): "
      f"A {first_a[0]}..{first_a[1]}, B {first_b[0]}..{first_b[1]}")
if conflicts:
    print("W21 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W21 ADMIT: A {W21_A[0]}..{W21_A[1]} + B {W21_B[0]}..{W21_B[1]} both "
      f"clean vs 19 registered rows + N3-R1 used-seed band + registry values "
      f"+ probes/actuals -- engine_owner=bm-a (rotation law slot W21=bm-a; "
      f"W20 row slot assignment verbatim).")

# --- W22+ projection (warning text for the law table row) --------------------
w22_a = (W21_A[1] + 1, W21_A[1] + WIDTH_A)
w22_b = (W21_B[1] + 1, W21_B[1] + WIDTH_B)
a_hits22 = sorted(p for p in points if w22_a[0] <= p <= w22_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w22_a)]
b_hits22 = sorted(p for p in points if w22_b[0] <= p <= w22_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w22_b)]
print(f"W22+ projection: A arithmetic +2_000 = {w22_a[0]}..{w22_a[1]} "
      f"-> {'CLEAN (verify at W22 prereg)' if not a_hits22 else 'REFUSED ' + str(a_hits22)}; "
      f"B +200 = {w22_b[0]}..{w22_b[1]} "
      f"-> {'CLEAN (verify at W22 prereg)' if not b_hits22 else 'REFUSED ' + str(b_hits22)}")
