"""W49 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W49 = THIRTY-EIGHTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's FIFTEENTH owned wave after W10/W11/W13/W16/
W19/W22/W25/W28/W31/W34/W36/W38/W40/W47). FREEZE AUTHORITY = never-dry
supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2
own-continuous-series: bm-b's TICK engine queue is EMPTY (W47 closed
r556 same-window: freeze 811e6c579 -> bm-a r555 + bm-c r349 double
YIELD receipts -> 12/12 burn -> finalize one-pass K=101,320, ledger
467,948). Wave 49 = NEXT FREE NUMBER SKIPPING the bm-a-declared W48
slot (r555 W47-yield receipt "bm-a next own wave = W48"; W19/W18
non-contiguity precedent -- wave numbers need not be contiguous,
r516 derive law).

r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W49 slot vacant on origin (no N1_BANDS 49 row, no canon
wave-49 row; machine-checked at leg3).

THE ONE AND ONLY ROOT CAUSE of the double forced skip: the W48
PUBLISHED PROJECTION = RESERVED FACE (r518-① published=reserved law,
W19-A/B re-base family). The W47 row's W48+ WARNING projects
A 139_004..141_003 / B 45_201..45_400 (machine-derived by the r534
gate's W48+ projection legs, CLEAN vs points -- the reservation is
the published face itself, NOT a point hit). bm-b's W49 arithmetic
positions from the W47 tail (A = 139_004..141_003, B =
45_201..45_400) are BOTH REFUSED by that published-reserved face ->
scan-forward first clean windows 141_004..143_003 / 45_401..45_600.
Forced, not a free pick (R250: W49 bands were never assigned).

Machine-verified against: all registered N1 wave bands W2..W47 (46
rows, W43/W44/W45/W46/W47 included), the W48 published projection
bands (reserved face), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every
gate receipt from W26 on), v1-in-use + W1 ext bands, SEED_REGISTRY
live values, N2/N4 design-probe points (40_000/40_001), N2-W15
draft probe points (31_000/31_500/32_000), lfc actual draw
(30_000..30_099) AND options_wave2 actual draw (63_000..63_049).

r556 bm-b freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W49_A = (141_004, 143_003)             # FORCED SKIP past the W48 published
                                        # projection A 139_004..141_003
W49_B = (45_401, 45_600)               # FORCED SKIP past the W48 published
                                        # projection B 45_201..45_400

# --- W48 published projection (r518-① reserved face; the ONE root cause) ---
W48_PROJ_A = (139_004, 141_003)        # W47 row W48+ WARNING projection
W48_PROJ_B = (45_201, 45_400)          # (machine-derived by r534 gate legs)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)      # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W49 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 49:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
# r518-① leg: the W48 PUBLISHED PROJECTION is a RESERVED FACE even
# though W48 is NOT YET REGISTERED (bm-a declared W48 in the r555
# W47-yield receipt; published = reserved).
published = [W48_PROJ_A, W48_PROJ_B]
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (46 pre-W49 rows + the candidate) ------------------
assert 47 in N1_BANDS and N1_BANDS[47]["engine_owner"] == "bm-b", \
    "leg0 failed: W47 (bm-b) row must be present (r534 freeze; finalize " \
    "landed r556 same-window K=101,320 ledger 467,948)"
assert 48 not in N1_BANDS, \
    "leg0 failed: W48 must NOT be registered at this freeze (bm-a " \
    "declared W48; if a W48 row landed, re-derive before freezing W49)"
assert 46 in N1_BANDS and N1_BANDS[46]["engine_owner"] == "bm-c", \
    "leg0 failed: W46 (bm-c) row must be present (r348 freeze; finalize " \
    "landed K=99,120 ledger 465,748)"
pre_w49 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           49]
assert sorted(N1_BANDS) == pre_w49, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"46 registered rows + the W49 candidate; no 15, no 48)"

# --- leg 0b: W47 row's W48+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "139_004..141_003" in canon and "45_201..45_400" in canon, \
    "leg0b failed: W47 row W48+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W47 row W48+ WARNING prose present (published projection = "
      "reserved face per r518-①; bm-a declared W48 in the r555 yield "
      "receipt)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[47]["a"][1] + 1, N1_BANDS[47]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[47]["b_exit"][1] + 1,
           N1_BANDS[47]["b_exit"][1] + WIDTH_B)
# A tail: projected CLEAN vs points, but REFUSED by the W48 published
# projection reserved face (r518-①; band-level refusal, not a point hit):
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: point refusal facts drift {a_hits} (projection was " \
    f"point-CLEAN; the refusal must be the published face only)"
a_pub = [b for b in published if overlaps(b, ARITH_A)]
assert a_pub == [W48_PROJ_A], \
    f"leg1-A failed: arithmetic window {ARITH_A} must be REFUSED by " \
    f"the W48 published projection {W48_PROJ_A} exactly (r518-① " \
    f"published=reserved law, refusal facts mismatch: {a_pub})"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} REFUSED "
      f"refusal facts = [W48 published projection "
      f"{W48_PROJ_A[0]}..{W48_PROJ_A[1]}] (bm-a declared W48 -- "
      f"published=reserved per r518-①, point hits {a_hits} = none; "
      f"FORCED skip, W19-A re-base family)")
# B tail: same published-projection refusal face:
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: point refusal facts drift {b_hits} (projection was " \
    f"point-CLEAN; the refusal must be the published face only)"
b_pub = [b for b in published if overlaps(b, ARITH_B)]
assert b_pub == [W48_PROJ_B], \
    f"leg1-B failed: arithmetic window {ARITH_B} must be REFUSED by " \
    f"the W48 published projection {W48_PROJ_B} exactly (refusal " \
    f"facts mismatch: {b_pub})"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"refusal facts = [W48 published projection "
      f"{W48_PROJ_B[0]}..{W48_PROJ_B[1]}] (FORCED skip, W19-B "
      f"re-base family)")

# --- leg 2: first clean window (scan-forward past the published face) -------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + published + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# A: arithmetic position REFUSED by the published projection -- scan
# forward past the entire reserved window (r307 tail law + r518-①):
first_a = clean(ARITH_A[0], WIDTH_A)
if first_a is None:
    # jump past the published face then step forward
    start = W48_PROJ_A[1] + 1
    first_a = None
    for _ in range(50):
        win = clean(start, WIDTH_A)
        if win is not None:
            first_a = win
            break
        blockers = [p for p in points if start <= p <= start + WIDTH_A - 1]
        blockers += [b for b in bands + published + actual
                     if overlaps((start, start + WIDTH_A - 1), b)]
        assert blockers, \
            f"leg2-A failed: window {start}.. unclean with no blocker"
        if any(isinstance(x, tuple) for x in blockers):
            nxt = max(b[1] for b in blockers if isinstance(b, tuple))
            start = max(start, nxt) + 1
        else:
            start = max(blockers) + 1
assert first_a == W49_A, \
    f"leg2-A failed: machine-derived first clean window {first_a} != " \
    f"candidate {W49_A} (forced scan-forward past the W48 published " \
    f"projection, r307/r518-①/r535 machine-derived)"
print(f"leg2-A first clean window {first_a[0]}..{first_a[1]} == candidate "
      f"(forced scan-forward past the W48 published projection, W19-A "
      f"re-base family)")
# B: same scan-forward route:
start = ARITH_B[0]
first_b = None
for _ in range(200):
    win = clean(start, WIDTH_B)
    if win is not None:
        first_b = win
        break
    blockers = [p for p in points if start <= p <= start + WIDTH_B - 1]
    blockers += [b for b in bands + published + actual
                 if overlaps((start, start + WIDTH_B - 1), b)]
    assert blockers, \
        f"leg2-B failed: window {start}.. unclean with no blocker"
    if any(isinstance(x, tuple) for x in blockers):
        nxt = max(b[1] for b in blockers if isinstance(b, tuple))
        start = max(start, nxt) + 1
    else:
        start = max(blockers) + 1
assert first_b == W49_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W49_B} (forced scan-forward past the W48 published " \
    f"projection, machine-derived, not picked -- r307/r535)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"(forced scan-forward past the W48 published projection, W19-B "
      f"re-base family)")
assert not overlaps(W49_A, W49_B), "A/B overlap"
assert not overlaps(W49_A, W48_PROJ_A) and not overlaps(W49_B, W48_PROJ_B), \
    "candidate must clear the W48 published projection both sides"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W49_A), ("B", W49_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 49:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W49-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W49-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W49-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W49-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W49-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W49-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W49-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W49-{tag} (r335 leg)")
    for nm, pr in (("W48-proj-A", W48_PROJ_A), ("W48-proj-B", W48_PROJ_B)):
        if overlaps(pr, band):
            conflicts.append(f"{nm} {pr[0]}..{pr[1]} x W49-{tag} "
                             f"(r518-① published=reserved leg)")
# canon cross-check: the landed W49 row must equal the derived candidate
assert N1_BANDS[49]["a"] == W49_A and N1_BANDS[49]["b_exit"] == W49_B, \
    "leg3 failed: canon W49 row drift vs derived candidate"
assert N1_BANDS[49]["engine_owner"] == "bm-b", "leg3 failed: W49 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "49: {\"a\": (141_004" not in out, \
    "leg3 failed: a W49 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg) | "
      f"W48 published projection: A {W48_PROJ_A[0]}..{W48_PROJ_A[1]} / "
      f"B {W48_PROJ_B[0]}..{W48_PROJ_B[1]} (r518-① reserved face)")
if conflicts:
    print("W49 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W49 ADMIT: A {W49_A[0]}..{W49_A[1]} + B {W49_B[0]}..{W49_B[1]} "
      f"(BOTH FORCED SKIP past the W48 published projection "
      f"A {W48_PROJ_A[0]}..{W48_PROJ_A[1]} / B {W48_PROJ_B[0]}..{W48_PROJ_B[1]} "
      f"per r518-① published=reserved law, W19-A/B re-base family) both "
      f"clean vs 46 registered rows + W48 reserved face + N3-R1 used-seed "
      f"band + probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-b (next free number skipping the bm-a-declared "
      f"W48 slot, W19/W18 precedent; zero-gap relay after the W47 full "
      f"closeout r556; origin slot vacancy machine-checked).")

# --- W50+ projection (warning text for the law table row) --------------------
w50_a = (W49_A[1] + 1, W49_A[1] + WIDTH_A)
w50_b = (W49_B[1] + 1, W49_B[1] + WIDTH_B)
a_hits50 = sorted(p for p in points if w50_a[0] <= p <= w50_a[1]) or [
    f"band {b}" for b in bands + published + actual if overlaps(b, w50_a)]
b_hits50 = sorted(p for p in points if w50_b[0] <= p <= w50_b[1]) or [
    f"band {b}" for b in bands + published + actual if overlaps(b, w50_b)]
print(f"W50+ projection: A arithmetic +2_000 = {w50_a[0]}..{w50_a[1]} "
      f"-> {'CLEAN (verify at W50 prereg)' if not a_hits50 else 'REFUSED ' + str(a_hits50)}; "
      f"B +200 from W49 end = {w50_b[0]}..{w50_b[1]} "
      f"-> {'CLEAN (verify at W50 prereg)' if not b_hits50 else 'REFUSED ' + str(b_hits50)}")
