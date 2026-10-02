# -*- coding: utf-8 -*-
"""W69 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W69 = FIFTY-EIGHTH ENGINE-OWNED WAVE (engine_owner=bm-c -- bm-c's
TWENTY-SECOND owned, machine-derived: 21 rows + candidate). Seat =
published=reserved MSG-20261002-1015-bmc (r518-1 law; same-window
re-occupation after the W68 yield to bm-a r568 first-land per r511
commit-order law). W67 bm-b + W68 bm-a = TWO in-flight upstream seats
(W69 finalize FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION from
the registered W68 tail: A 181_004..183_003 / B 50_701..50_900, both
CLEAN (== the W68 row W69+ WARNING projections, independently re-derived
per r535 law).

Machine-verified against: all registered N1 wave bands W2..W68, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg), the
runner design-probe seed cluster 95_000..95_003 (r335 discovery leg),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points, N2-W15 draft probe points, lfc actual draw and options_wave2
actual draw. Origin slot vacancy machine-checked (ANY W69 row on
origin = abort).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

W69_A = (181_004, 183_003)              # law sec.4 W69 row (arithmetic, no skip)
W69_B = (50_701, 50_900)                # law sec.4 W69 row (arithmetic, no skip)

W68_REGISTERED_A = (179_004, 181_003)   # bm-a r568 registered tail
W68_REGISTERED_B = (50_501, 50_700)

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- leg 0-hold: zero-gap relay (W68 must be REGISTERED before ADMIT) -------
if 68 not in N1_BANDS:
    print("HOLD: W68 row not yet registered in the live registry. W69 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[68]["a"] == W68_REGISTERED_A and \
    N1_BANDS[68]["b_exit"] == W68_REGISTERED_B and \
    N1_BANDS[68].get("engine_owner") == "bm-a", \
    "leg0 failed: registered W68 row != expected registered bands " \
    "(A 179_004..181_003 / B 50_501..50_700, bm-a r568) -- derivation " \
    "basis invalidated, RE-DERIVE the W69 candidates"

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 69:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (67 pre-W69 registered rows + the candidate) -----
assert 64 in N1_BANDS and N1_BANDS[64]["engine_owner"] == "bm-a", \
    "leg0 failed: W64 (bm-a) registered row must be present"
assert 65 in N1_BANDS and N1_BANDS[65]["engine_owner"] == "bm-b", \
    "leg0 failed: W65 (bm-b) registered row must be present"
assert 66 in N1_BANDS and N1_BANDS[66]["engine_owner"] == "bm-c", \
    "leg0 failed: W66 (bm-c) registered row must be present (r359)"
assert 67 in N1_BANDS and N1_BANDS[67]["engine_owner"] == "bm-b", \
    "leg0 failed: W67 (bm-b) registered row must be present (r567)"
assert 68 in N1_BANDS and N1_BANDS[68]["engine_owner"] == "bm-a", \
    "leg0 failed: W68 (bm-a) registered row must be present (r568)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w66_results.json")), \
    "leg0 failed: W66 finalize product missing (landed bm-c r360 -- " \
    "fetch/ff freshness)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-c") == 22, \
    "leg0 failed: bm-c owned-row count != 22 (21 pre-candidate + the " \
    "landed W69 candidate -- machine-derive basis for the TWENTY-SECOND " \
    "owned wave claim)"
pre_w69 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69]
assert sorted(N1_BANDS) == pre_w69, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 67 " \
    f"registered rows + the W69 candidate)"

# --- leg 0b: W68 row's W69+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "181_004..183_003" in canon and "50_701..50_900" in canon, \
    "leg0b failed: W68 row W69+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W68 row W69+ WARNING prose present (published projection "
      "basis; machine-derived per r535; registered W68 bm-a row bands "
      "cross-checked verbatim)")

# --- leg 1: arithmetic positions DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[68]["a"][1] + 1, N1_BANDS[68]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[68]["b_exit"][1] + 1,
           N1_BANDS[68]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W68 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W68 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: arithmetic window 50_701..50_900 projected CLEAN -- " \
    f"got hits {b_hits}; refusal-facts drift, RE-DERIVE"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W68 row projection verified machine-side)")

# --- leg 2: first clean windows (both == arithmetic; zero-skip wave) ---------
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
assert first_a == W69_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W69_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W69_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W69_B} " \
    "(no skip expected -- zero-skip wave both sides)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} == "
      f"arithmetic / B {first_b[0]}..{first_b[1]} == arithmetic "
      f"(BOTH SIDES zero-skip wave)")
assert not overlaps(W69_A, W69_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W69_A), ("B", W69_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 69:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W69-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W69-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W69-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W69-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W69-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W69-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W69-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W69-{tag} (r335 leg)")
# canon cross-check: the landed W69 row must equal the derived candidate
assert N1_BANDS[69]["a"] == W69_A and N1_BANDS[69]["b_exit"] == W69_B, \
    "leg3 failed: canon W69 row drift vs derived candidate"
assert N1_BANDS[69]["engine_owner"] == "bm-c", "leg3 failed: W69 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-c") == 22, \
    "leg3 failed: post-land bm-c owned rows must be exactly 22 (TWENTY-SECOND " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
# (ANY W69 row on origin = seat collision, r511 tail-lock violation)
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8", creationflags=NO_WIN)
assert '69: {"a": (' not in out, \
    "leg3 failed: a W69 row ALREADY exists on origin (ANY-band check -- " \
    "seat collision, abort before push)"
assert "68: {\"a\": (179_004" in out, \
    "leg3 failed: the registered W68 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W69 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W69 ADMIT: BOTH SIDES ARITHMETIC CONTINUATION from the registered "
      f"W68 tail (A {W69_A[0]}..{W69_A[1]} / B {W69_B[0]}..{W69_B[1]} both "
      f"CLEAN == the W68 row W69+ published projection verbatim; zero-skip "
      f"wave) clean vs 67 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-c "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; seat "
      f"published=reserved MSG-20261002-1015-bmc; W67 bm-b + W68 bm-a = TWO "
      f"in-flight upstream seats, finalize FAIL-CLOSED r307; origin slot "
      f"vacancy machine-checked ANY-band).")

# --- W70+ projection (warning text for the law table row) --------------------
w70_a = (W69_A[1] + 1, W69_A[1] + WIDTH_A)
w70_b = (W69_B[1] + 1, W69_B[1] + WIDTH_B)
a_hits70 = sorted(p for p in points if w70_a[0] <= p <= w70_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w70_a)]
b_hits70 = sorted(p for p in points if w70_b[0] <= p <= w70_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w70_b)]
print(f"W70+ projection: A arithmetic +2_000 = {w70_a[0]}..{w70_a[1]} "
      f"-> {'CLEAN (verify at W70 prereg)' if not a_hits70 else 'REFUSED ' + str(a_hits70)}; "
      f"B +200 from W69 end = {w70_b[0]}..{w70_b[1]} "
      f"-> {'CLEAN (verify at W70 prereg)' if not b_hits70 else 'REFUSED ' + str(b_hits70)}")
if b_hits70 and isinstance(b_hits70[-1], int):
    mid = (b_hits70[-1] != w70_b[1])
    r_lo = w70_b[0]
    while clean(r_lo, WIDTH_B) is None:
        h = min(p for p in points if r_lo <= p <= r_lo + WIDTH_B - 1)
        r_lo = h + 1
    c_lo = w70_b[0]
    while clean(c_lo, WIDTH_B) is None:
        c_lo += WIDTH_B
    pos = ("MID (FORK FACE #3 -- sec.4 pin pending, "
           "HQ-FEEDBACK F-20261002-03)" if mid
           else "TAIL (both readings coincide)")
    print(f"W70 B hit position: {pos}; "
          f"restart reading: {r_lo}..{r_lo + WIDTH_B - 1} | "
          f"chained reading: {c_lo}..{c_lo + WIDTH_B - 1}")
