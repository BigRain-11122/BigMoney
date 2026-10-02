# -*- coding: utf-8 -*-
"""W72 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W72 = SIXTY-FIRST ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTY-THIRD owned wave, machine-derived:
22 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (r518-1 law; MSG-20261002-1028-bmb). W68 finalize
LANDED (bm-a r569, net chain head 514,148, K=147,520); W69 bm-c
(12/12 burned, finalize pending) + W70 bm-b (12/12 burned, finalize
pending, chain-ordered after W69) + W71 bm-c (burn in flight) =
THREE in-flight upstream seats at this freeze (FAIL-CLOSED r307).

BOTH SIDES = PLAIN ARITHMETIC CONTINUATION from the registered W71
tail (bm-c r361 freeze c08c1dac5), zero skip, no fork face this wave:
  A: W71 A end 187_003 + 1 -> 187_004..189_003
  B: W71 B end 51_400 + 1 -> 51_401..51_600
The W71 canon row CARRIES the W72+ WARNING projection (A 187_004..189_003
/ B 51_401..51_600 both CLEAN, machine-verified by the bm-c r361 gate
projection leg). This gate re-derives BOTH sides independently from the
registered W71 row (r302 stale-pointer law / r335 machine-derive law --
prose is a cross-check only, never the derivation basis).

Machine-verified against: all registered N1 wave bands W2..W71, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r570 bm-b freeze-window run (never-dry standing step,
O-20261001-2355 sec.2 own-series).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W72_A = (187_004, 189_003)              # law sec.4 W72 row (arithmetic, no skip)
W72_B = (51_401, 51_600)                # law sec.4 W72 row (arithmetic, no skip)

# --- registered W71 row (bm-c r361 freeze c08c1dac5, registered tail) -------
W71_REGISTERED_A = (185_004, 187_003)
W71_REGISTERED_B = (51_201, 51_400)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

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

# --- leg 0-hold: zero-gap relay (W71 must be REGISTERED before ADMIT) -------
if 71 not in N1_BANDS:
    print("HOLD: W71 row not yet registered in the live registry. W72 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[71]["a"] == W71_REGISTERED_A and \
    N1_BANDS[71]["b_exit"] == W71_REGISTERED_B and \
    N1_BANDS[71].get("engine_owner") == "bm-c", \
    "leg0 failed: registered W71 row != expected registered bands " \
    "(A 185_004..187_003 / B 51_201..51_400, bm-c r361 c08c1dac5) -- " \
    "derivation basis invalidated, RE-DERIVE the W72 candidates"

# --- reserved universe (W72 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 72:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (69 pre-W72 registered rows + the candidate) -----
assert 69 in N1_BANDS and N1_BANDS[69]["engine_owner"] == "bm-c", \
    "leg0 failed: W69 (bm-c) row must be present (registered r360, " \
    "12/12 burned -- finalize chain-pending FAIL-CLOSED r307)"
assert 70 in N1_BANDS and N1_BANDS[70]["engine_owner"] == "bm-b", \
    "leg0 failed: W70 (bm-b) row must be present (registered r568, " \
    "12/12 burned -- finalize chain-pending after W69, FAIL-CLOSED r307)"
assert 71 in N1_BANDS and N1_BANDS[71]["engine_owner"] == "bm-c", \
    "leg0 failed: W71 (bm-c) row must be present (registered r361, " \
    "burn in flight -- finalize chain-pending FAIL-CLOSED r307)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w68_results.json")), \
    "leg0 failed: W68 finalize product missing (landed by bm-a r569, " \
    "net chain head 514,148, K=147,520 -- it stays the S5 anchor " \
    "while W69/W70/W71 finalizes are in flight)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 23, \
    "leg0 failed: bm-b owned-row count != 23 (22 pre-candidate + the " \
    "landed W72 candidate -- machine-derive basis for the TWENTY-THIRD " \
    "owned wave claim)"
pre_w72 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70, 71, 72]
assert sorted(N1_BANDS) == pre_w72, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 69 " \
    f"registered rows + the W72 candidate)"

# --- leg 0b: W71 row's W72+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for prose in ("187_004..189_003", "51_401..51_600"):
    assert prose in canon, \
        f"leg0b failed: W71 row W72+ WARNING prose '{prose}' not found " \
        f"in the canon file"
print("leg0b W71 row W72+ WARNING prose present (registered projection "
      "basis; machine-derived by the bm-c r361 gate projection leg; "
      "registered W71 bm-c row bands cross-checked verbatim; this gate "
      "re-derives independently per r302/r535 law)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[71]["a"][1] + 1, N1_BANDS[71]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[71]["b_exit"][1] + 1,
           N1_BANDS[71]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W71 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W71 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W71 row projected " \
    f"CLEAN -- expected zero hits)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, no fork face this wave)")

# --- leg 2: first clean windows -----------------------------------------------
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
assert first_a == W72_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W72_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W72_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W72_B} " \
    "(no skip expected -- arithmetic continuation both sides)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} / B "
      f"{first_b[0]}..{first_b[1]} (BOTH = arithmetic continuation "
      f"windows, zero skip, zero fork)")
assert not overlaps(W72_A, W72_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W72_A), ("B", W72_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 72:
            continue
        for key in ("a", "b_exit"):
            lo2, hi2 = cfg[key]
            if overlaps((lo2, hi2), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo2}..{hi2} x W72-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W72-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W72-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W72-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W72-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W72-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W72-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W72-{tag} (r335 leg)")
# canon cross-check: the landed W72 row must equal the derived candidate
assert N1_BANDS[72]["a"] == W72_A and N1_BANDS[72]["b_exit"] == W72_B, \
    "leg3 failed: canon W72 row drift vs derived candidate"
assert N1_BANDS[72]["engine_owner"] == "bm-b", "leg3 failed: W72 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 23, \
    "leg3 failed: post-land bm-b owned rows must be exactly 23 (TWENTY-THIRD " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "72: {\"a\": (187_004" not in out, \
    "leg3 failed: a W72 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "71: {\"a\": (185_004" in out, \
    "leg3 failed: the registered W71 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W72 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W72 ADMIT: A {W72_A[0]}..{W72_A[1]} + B {W72_B[0]}..{W72_B[1]} "
      f"BOTH ARITHMETIC CONTINUATION from the registered W71 tail "
      f"(zero skip both sides, zero fork face; == the W71 row W72+ "
      f"published projection verbatim) clean vs 69 registered rows + "
      f"N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-b (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; seat declared published=reserved "
      f"MSG-20261002-1028-bmb; W69 bm-c + W70 bm-b + W71 bm-c = THREE "
      f"in-flight upstream seats for the W72 finalize chain, finalize "
      f"FAIL-CLOSED r307; origin slot vacancy machine-checked).")

# --- W73+ projection (warning text for the law table row) --------------------
w73_a = (W72_A[1] + 1, W72_A[1] + WIDTH_A)
w73_b = (W72_B[1] + 1, W72_B[1] + WIDTH_B)
a_hits73 = sorted(p for p in points if w73_a[0] <= p <= w73_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w73_a)]
b_hits73 = sorted(p for p in points if w73_b[0] <= p <= w73_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w73_b)]
print(f"W73+ projection: A arithmetic +2_000 = {w73_a[0]}..{w73_a[1]} "
      f"-> {'CLEAN (verify at W73 prereg)' if not a_hits73 else 'REFUSED ' + str(a_hits73)}; "
      f"B +200 from W72 end = {w73_b[0]}..{w73_b[1]} "
      f"-> {'CLEAN (verify at W73 prereg)' if not b_hits73 else 'REFUSED ' + str(b_hits73)}")
