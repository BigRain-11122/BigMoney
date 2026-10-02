# -*- coding: utf-8 -*-
"""W71 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W71 = SIXTIETH ENGINE-OWNED WAVE (engine_owner=bm-c -- bm-c's
TWENTY-THIRD owned, machine-derived: 22 rows + candidate). Seat =
published=reserved MSG-20261002-1017-bmc (r518-1 law; never-dry
standing step under CEO de-throttle order O-20261001-2355 sec.2).
Wave 71 = first free number after the registered W70 row (bm-b r568,
burn in flight). BOTH SIDES ARITHMETIC CONTINUATION from the
registered W70 tail: A 185_004..187_003 / B 51_201..51_400, both
CLEAN.

DERIVATION BASIS DISCLOSURE (r302/r535): the W70 canon row carries NO
W71+ WARNING projection prose (bm-b r568 row omitted the standing
tail); the published W71+ projection lives in the bm-b r568 commit
message + their gate receipt (A 185_004..187_003 / B 51_201..51_400
both CLEAN). This gate therefore derives BOTH windows machine-side
from the registered W70 row bands (N1_BANDS import, not prose) and
cross-checks the registered W70 row bands prose in the canon file.

W68 bm-a (12/12 burned, finalize pending) + W69 bm-c (12/12 burned,
finalize pending) + W70 bm-b (burn in flight) = THREE in-flight
upstream seats (W71 finalize FAIL-CLOSED r307).

Machine-verified against: all registered N1 wave bands W2..W70, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw. Origin slot vacancy machine-checked (ANY
W71 row on origin = abort).
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

W71_A = (185_004, 187_003)              # law sec.4 W71 row (arithmetic, no skip)
W71_B = (51_201, 51_400)                # law sec.4 W71 row (arithmetic, no skip)

W70_REGISTERED_A = (183_004, 185_003)   # bm-b r568 registered tail
W70_REGISTERED_B = (51_001, 51_200)

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

# --- leg 0-hold: zero-gap relay (W70 must be REGISTERED before ADMIT) -------
if 70 not in N1_BANDS:
    print("HOLD: W70 row not yet registered in the live registry. W71 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[70]["a"] == W70_REGISTERED_A and \
    N1_BANDS[70]["b_exit"] == W70_REGISTERED_B and \
    N1_BANDS[70].get("engine_owner") == "bm-b", \
    "leg0 failed: registered W70 row != expected registered bands " \
    "(A 183_004..185_003 / B 51_001..51_200, bm-b r568) -- derivation " \
    "basis invalidated, RE-DERIVE the W71 candidates"

# --- reserved universe (W71 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 71:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (68 pre-W71 registered rows + the candidate) -------
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
assert 69 in N1_BANDS and N1_BANDS[69]["engine_owner"] == "bm-c", \
    "leg0 failed: W69 (bm-c) registered row must be present (r360)"
assert 70 in N1_BANDS and N1_BANDS[70]["engine_owner"] == "bm-b", \
    "leg0 failed: W70 (bm-b) registered row must be present (r568)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w67_results.json")), \
    "leg0 failed: W67 finalize product missing (landed 77fd35e87, net " \
    "chain head 511,948, K=145,320 -- fetch/ff freshness)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-c") == 23, \
    "leg0 failed: bm-c owned-row count != 23 (22 pre-candidate + the " \
    "landed W71 candidate -- machine-derive basis for the TWENTY-THIRD " \
    "owned wave claim)"
pre_w71 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70, 71]
assert sorted(N1_BANDS) == pre_w71, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 68 " \
    f"registered rows + the W71 candidate)"

# --- leg 0b: W70 registered-bands prose present (row carries NO W71+ WARN) ---
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "183_004..185_003" in canon and "51_001..51_200" in canon, \
    "leg0b failed: registered W70 row bands prose not found in the " \
    "canon file (derivation cross-check basis)"
assert "- N1 \u6ce270\uff08" in canon, "leg0b failed: W70 canon row absent"
print("leg0b W70 registered-bands prose present (the W70 row carries NO "
      "W71+ WARNING tail -- bm-b r568 row omitted it; published W71+ "
      "projection = bm-b r568 commit message + their gate receipt; this "
      "gate machine-derives BOTH W71 windows from the registered W70 "
      "bands -- r302/r535 law, not prose copy)")

# --- leg 1: arithmetic positions DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[70]["a"][1] + 1, N1_BANDS[70]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[70]["b_exit"][1] + 1,
           N1_BANDS[70]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (bm-b r568 projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip; matches "
      f"bm-b r568 commit-message projection)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: arithmetic window 51_201..51_400 projected CLEAN -- " \
    f"got hits {b_hits}; refusal-facts drift, RE-DERIVE"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip; matches bm-b r568 commit-message projection)")

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
assert first_a == W71_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W71_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W71_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W71_B} " \
    "(no skip expected -- zero-skip wave both sides)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} == "
      f"arithmetic / B {first_b[0]}..{first_b[1]} == arithmetic "
      f"(BOTH SIDES zero-skip wave)")
assert not overlaps(W71_A, W71_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W71_A), ("B", W71_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 71:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W71-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W71-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W71-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W71-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W71-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W71-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W71-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W71-{tag} (r335 leg)")
# canon cross-check: the landed W71 row must equal the derived candidate
assert N1_BANDS[71]["a"] == W71_A and N1_BANDS[71]["b_exit"] == W71_B, \
    "leg3 failed: canon W71 row drift vs derived candidate"
assert N1_BANDS[71]["engine_owner"] == "bm-c", "leg3 failed: W71 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-c") == 23, \
    "leg3 failed: post-land bm-c owned rows must be exactly 23 (TWENTY-THIRD " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
# (ANY W71 row on origin = seat collision, r511 tail-lock violation)
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8", errors="replace", creationflags=NO_WIN)
assert '71: {"a": (' not in out, \
    "leg3 failed: a W71 row ALREADY exists on origin (ANY-band check -- " \
    "seat collision, abort before push)"
assert '70: {"a": (183_004' in out, \
    "leg3 failed: the registered W70 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W71 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W71 ADMIT: BOTH SIDES ARITHMETIC CONTINUATION from the registered "
      f"W70 tail (A {W71_A[0]}..{W71_A[1]} / B {W71_B[0]}..{W71_B[1]} both "
      f"CLEAN, machine-derived from the registered W70 bands per r535 law "
      f"-- the W70 row carried no W71+ WARNING prose, bm-b r568 "
      f"commit-message projection cross-checked; zero-skip wave) clean vs "
      f"68 registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-c (first-free-"
      f"number law under O-20261001-2355 de-throttle sec.2; seat "
      f"published=reserved MSG-20261002-1017-bmc; W68 bm-a + W69 bm-c + "
      f"W70 bm-b = THREE in-flight upstream seats, finalize FAIL-CLOSED "
      f"r307; origin slot vacancy machine-checked ANY-band).")

# --- W72+ projection (warning text for the law table row) --------------------
w72_a = (W71_A[1] + 1, W71_A[1] + WIDTH_A)
w72_b = (W71_B[1] + 1, W71_B[1] + WIDTH_B)
a_hits72 = sorted(p for p in points if w72_a[0] <= p <= w72_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w72_a)]
b_hits72 = sorted(p for p in points if w72_b[0] <= p <= w72_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w72_b)]
print(f"W72+ projection: A arithmetic +2_000 = {w72_a[0]}..{w72_a[1]} "
      f"-> {'CLEAN (verify at W72 prereg)' if not a_hits72 else 'REFUSED ' + str(a_hits72)}; "
      f"B +200 from W71 end = {w72_b[0]}..{w72_b[1]} "
      f"-> {'CLEAN (verify at W72 prereg)' if not b_hits72 else 'REFUSED ' + str(b_hits72)}")
