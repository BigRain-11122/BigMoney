# -*- coding: utf-8 -*-
"""W74 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W74 = SIXTY-THIRD ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTY-FOURTH owned wave, machine-derived:
23 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (r518-1 law; MSG-20261002-1108-bmb). W72 finalize
LANDED (bm-b r571, net chain head 522,948, K=156,320 -- W1..W72 all
landed); W73 bm-a (12/12 burned, finalize pending) = ONE in-flight
upstream seat at this freeze (FAIL-CLOSED r307).

BANDS:
  A: W73 A end 191_003 + 1 -> 191_004..193_003  (arithmetic, no skip)
  B: arithmetic 51_801..52_000 REFUSED at its upper-edge point
     SEED_REGISTRY xstock_synth_null_b=52_000 (r307 W5 skip-precedent
     family) -> first clean window 52_001..52_200; BOTH READINGS
     COINCIDE (past-hit restart == window-step chain) = no fork face,
     unlike the W63 double-mid divergence (r566 law). Skip forced
     (R250), not a free pick.
The W73 canon row CARRIES the W74+ WARNING projection (A CLEAN /
B REFUSED -> 52_001..52_200, machine-verified by the bm-a r570 gate
projection leg). This gate re-derives BOTH sides independently from
the registered W73 row (r302 stale-pointer law / r335 machine-derive
law -- prose is a cross-check only, never the derivation basis).

Machine-verified against: all registered N1 wave bands W2..W73, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r571 bm-b freeze-window run (never-dry standing step,
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
W74_A = (191_004, 193_003)              # law sec.4 W74 row (arithmetic, no skip)
W74_B = (52_001, 52_200)                # law sec.4 W74 row (forced skip past 52_000)

# --- registered W73 row (bm-a r570 freeze, registered tail) -------------------
W73_REGISTERED_A = (189_004, 191_003)
W73_REGISTERED_B = (51_601, 51_800)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) ---------
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

# --- leg 0-hold: zero-gap relay (W73 must be REGISTERED before ADMIT) --------
if 73 not in N1_BANDS:
    print("HOLD: W73 row not yet registered in the live registry. W74 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[73]["a"] == W73_REGISTERED_A and \
    N1_BANDS[73]["b_exit"] == W73_REGISTERED_B and \
    N1_BANDS[73].get("engine_owner") == "bm-a", \
    "leg0 failed: registered W73 row != expected registered bands " \
    "(A 189_004..191_003 / B 51_601..51_800, bm-a r570) -- " \
    "derivation basis invalidated, RE-DERIVE the W74 candidates"

# --- reserved universe (W74 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 74:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (71 pre-W74 registered rows + the candidate) ------
assert 72 in N1_BANDS and N1_BANDS[72]["engine_owner"] == "bm-b", \
    "leg0 failed: W72 (bm-b) row must be present (registered r570, " \
    "finalize LANDED r571 -- chain head 522,948, K=156,320)"
assert 73 in N1_BANDS and N1_BANDS[73]["engine_owner"] == "bm-a", \
    "leg0 failed: W73 (bm-a) row must be present (registered r570, " \
    "12/12 burned -- finalize chain-pending FAIL-CLOSED r307)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w72_results.json")), \
    "leg0 failed: W72 finalize product missing (landed by bm-b r571, " \
    "net chain head 522,948, K=156,320 -- it stays the S5 anchor " \
    "while the W73 finalize is in flight)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 24, \
    "leg0 failed: bm-b owned-row count != 24 (23 pre-candidate + the " \
    "landed W74 candidate -- machine-derive basis for the TWENTY-FOURTH " \
    "owned wave claim)"
pre_w74 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74]
assert sorted(N1_BANDS) == pre_w74, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 71 " \
    f"registered rows + the W74 candidate)"

# --- leg 0b: W73 row's W74+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for prose in ("191_004..193_003", "52_001..52_200"):
    assert prose in canon, \
        f"leg0b failed: W73 row W74+ WARNING prose '{prose}' not found " \
        f"in the canon file"
print("leg0b W73 row W74+ WARNING prose present (registered projection "
      "basis; machine-derived by the bm-a r570 gate projection leg; "
      "registered W73 bm-a row bands cross-checked verbatim; this gate "
      "re-derives independently per r302/r535 law)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[73]["a"][1] + 1, N1_BANDS[73]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[73]["b_exit"][1] + 1,
           N1_BANDS[73]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W73 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W73 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [52_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (expected exactly " \
    f"[52_000] = SEED_REGISTRY xstock_synth_null_b upper-edge endpoint " \
    f"-- refusal facts identity, r307 W5 skip family)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"at upper-edge point 52_000 (SEED_REGISTRY xstock_synth_null_b; "
      f"window position = band upper edge, r307 W5 skip-precedent family)")

# --- leg 2: first clean windows (BOTH READINGS for the B skip) ---------------
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
assert first_a == W74_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W74_A} " \
    f"(no skip expected; R250/r518 machine-derived)"
# B side reading 1: past-hit restart (lo = max(hit) + 1)
b_read1 = clean(b_hits[-1] + 1, WIDTH_B)
# B side reading 2: window-step chain (scan forward from the refused
# arithmetic start in WIDTH_B steps until the first clean window)
lo = ARITH_B[0]
b_read2 = None
for _ in range(10):
    w = clean(lo, WIDTH_B)
    if w:
        b_read2 = w
        break
    lo += WIDTH_B
assert b_read1 is not None and b_read2 is not None, \
    "leg2-B failed: no clean window found within scan horizon"
assert b_read1 == b_read2, \
    f"leg2-B FORK FACE: past-hit restart {b_read1} != window-step chain " \
    f"{b_read2} (divergence family r566 -- pin the semantics before " \
    f"landing, HQ-FEEDBACK F-20261002-03)"
assert b_read1 == W74_B, \
    f"leg2-B failed: first clean window {b_read1} != candidate {W74_B} " \
    f"(both readings must coincide AND equal the forced-skip candidate)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} / B "
      f"{b_read1[0]}..{b_read1[1]} (B: past-hit restart == window-step "
      f"chain -- BOTH READINGS COINCIDE, no fork face this wave)")
assert not overlaps(W74_A, W74_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W74_A), ("B", W74_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 74:
            continue
        for key in ("a", "b_exit"):
            lo2, hi2 = cfg[key]
            if overlaps((lo2, hi2), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo2}..{hi2} x W74-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W74-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W74-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W74-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W74-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W74-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W74-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W74-{tag} (r335 leg)")
# canon cross-check: the landed W74 row must equal the derived candidate
assert N1_BANDS[74]["a"] == W74_A and N1_BANDS[74]["b_exit"] == W74_B, \
    "leg3 failed: canon W74 row drift vs derived candidate"
assert N1_BANDS[74]["engine_owner"] == "bm-b", "leg3 failed: W74 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 24, \
    "leg3 failed: post-land bm-b owned rows must be exactly 24 (TWENTY-FOURTH " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "74: {\"a\": (191_004" not in out, \
    "leg3 failed: a W74 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "73: {\"a\": (189_004" in out, \
    "leg3 failed: the registered W73 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W74 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W74 ADMIT: A {W74_A[0]}..{W74_A[1]} (ARITHMETIC CONTINUATION from the "
      f"registered W73 tail, zero skip) + B {W74_B[0]}..{W74_B[1]} (FORCED "
      f"SKIP past the refused arithmetic window 51_801..52_000 upper-edge "
      f"point xstock_synth_null_b=52_000; BOTH READINGS COINCIDE = no fork "
      f"face, r307 W5 skip family, skip forced not picked) clean vs 71 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-b (first-free-"
      f"number law under O-20261001-2355 de-throttle sec.2; seat declared "
      f"published=reserved MSG-20261002-1108-bmb; W73 bm-a = ONE in-flight "
      f"upstream seat for the W74 finalize chain, finalize FAIL-CLOSED "
      f"r307; origin slot vacancy machine-checked).")

# --- W75+ projection (warning text for the law table row) --------------------
w75_a = (W74_A[1] + 1, W74_A[1] + WIDTH_A)
w75_b = (W74_B[1] + 1, W74_B[1] + WIDTH_B)
a_hits75 = sorted(p for p in points if w75_a[0] <= p <= w75_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w75_a)]
b_hits75 = sorted(p for p in points if w75_b[0] <= p <= w75_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w75_b)]
print(f"W75+ projection: A arithmetic +2_000 = {w75_a[0]}..{w75_a[1]} "
      f"-> {'CLEAN (verify at W75 prereg)' if not a_hits75 else 'REFUSED ' + str(a_hits75)}; "
      f"B +200 from W74 end = {w75_b[0]}..{w75_b[1]} "
      f"-> {'CLEAN (verify at W75 prereg)' if not b_hits75 else 'REFUSED ' + str(b_hits75)}")
