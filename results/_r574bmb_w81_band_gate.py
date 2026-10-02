# -*- coding: utf-8 -*-
"""W81 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W81 = SEVENTY-FIRST ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTY-SEVENTH owned wave, machine-derived:
26 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (r518-1 law; MSG-20261002-1220-bmb PUSHED to
origin BEFORE this freeze per r565 early-visibility law, commit
d0f450cb5) + same-window W80 YIELD to bm-c r364 (7fbeadb2e
first-land 12:07:03 per r511 commit-order law, receipt
MSG-20261002-1220-bmb) then same-window next-seat re-occupation
per r565 law. W1..W79 finalizes ALL LANDED (net chain head 538,348,
K=171,720, bm-b r574 this window); W80 bm-c (registered r364, burn
in flight) = ONE in-flight upstream seat at this freeze
(FAIL-CLOSED r307).

BANDS:
  A: W80 A end 205_003 + 1 -> 205_004..207_003  (arithmetic, CLEAN)
  B: arithmetic 53_801..54_000 REFUSED at upper-edge point
     SEED_REGISTRY t18_deep_axis=54_000 -> PAST-HIT RESTART first
     clean window 54_001..54_200 (W74-B upper-edge family; BOTH
     READINGS COINCIDE = single reading, no fork face,
     F-20261002-03 not triggered)
NOT a re-pick (R250: W81 bands were never assigned).
The W80 canon row CARRIES the W81+ WARNING projection (A CLEAN /
B REFUSED at 54_000, machine-verified by the bm-c r364 gate
projection leg). This gate re-derives BOTH sides independently from
the registered W80 row (r302 stale-pointer law / r335 machine-derive
law -- prose is a cross-check only, never the derivation basis).

Machine-verified against: all registered N1 wave bands W2..W80, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r574 bm-b freeze-window run (never-dry standing step,
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
W81_A = (205_004, 207_003)              # law sec.4 W81 row (arithmetic, no skip)
W81_B = (54_001, 54_200)                # law sec.4 W81 row (past-hit restart)

# --- registered W80 row (bm-c r364 freeze, registered tail) -------------------
W80_REGISTERED_A = (203_004, 205_003)
W80_REGISTERED_B = (53_601, 53_800)

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

# --- leg 0-hold: zero-gap relay (W80 must be REGISTERED before ADMIT) --------
if 80 not in N1_BANDS:
    print("HOLD: W80 row not yet registered in the live registry. W81 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[80]["a"] == W80_REGISTERED_A and \
    N1_BANDS[80]["b_exit"] == W80_REGISTERED_B and \
    N1_BANDS[80].get("engine_owner") == "bm-c", \
    "leg0 failed: registered W80 row != expected registered bands " \
    "(A 203_004..205_003 / B 53_601..53_800, bm-c r364) -- " \
    "derivation basis invalidated, RE-DERIVE the W81 candidates"

# --- reserved universe (W81 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 81:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (78 pre-W81 registered rows + the candidate) -------
assert 78 in N1_BANDS and N1_BANDS[78]["engine_owner"] == "bm-c", \
    "leg0 failed: W78 (bm-c) row must be present (finalize LANDED r364)"
assert 79 in N1_BANDS and N1_BANDS[79]["engine_owner"] == "bm-b", \
    "leg0 failed: W79 (bm-b) row must be present (registered r573, " \
    "finalize LANDED bm-b r574 -- chain head 538,348, K=171,720)"
assert 80 in N1_BANDS and N1_BANDS[80]["engine_owner"] == "bm-c", \
    "leg0 failed: W80 (bm-c) row must be present (registered r364, " \
    "burn in flight -- finalize chain-pending FAIL-CLOSED r307)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w79_results.json")), \
    "leg0 failed: W79 finalize product missing (landed by bm-b r574, " \
    "net chain head 538,348, K=171,720 -- it stays the S5 anchor " \
    "while the W80 finalize is in flight)"
pre_w81 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
           80, 81]
assert sorted(N1_BANDS) == pre_w81, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 78 " \
    f"registered rows + the W81 candidate)"

# --- leg 0b: W80 row's W81+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for prose in ("205_004..207_003", "53_801..54_000"):
    assert prose in canon, \
        f"leg0b failed: W80 row W81+ WARNING prose '{prose}' not found " \
        f"in the canon file"
print("leg0b W80 row W81+ WARNING prose present (registered projection "
      "basis; machine-derived by the bm-c r364 gate projection leg; "
      "registered W80 bm-c row bands cross-checked verbatim; this gate "
      "re-derives independently per r302/r535 law)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[80]["a"][1] + 1, N1_BANDS[80]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[80]["b_exit"][1] + 1,
           N1_BANDS[80]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W80 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W80 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [54_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (W80 row projected " \
    f"REFUSED at the single upper-edge point t18_deep_axis=54_000 -- " \
    f"expected [54000])"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED at "
      f"upper-edge point SEED_REGISTRY t18_deep_axis=54_000 "
      f"(W74-B upper-edge family; both readings coincide = single "
      f"reading, no fork face)")

# --- leg 2: first clean windows (A arithmetic; B past-hit restart) ----------
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
assert first_a == W81_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W81_A} " \
    f"(no skip expected; R250/r518 machine-derived)"
RESTART_B = (b_hits[-1] + 1, b_hits[-1] + WIDTH_B)
first_b = clean(RESTART_B[0], WIDTH_B)
assert first_b == W81_B == RESTART_B, \
    f"leg2-B failed: first clean past-hit restart window {first_b} != " \
    f"candidate {W81_B} != derived restart {RESTART_B} " \
    f"(single-mid-hit precedent family W26-A/W68-B/W70-B/W74-B)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} (arithmetic "
      f"continuation) / B {first_b[0]}..{first_b[1]} (past-hit restart over "
      f"54_000; both readings coincide, no fork face)")
assert not overlaps(W81_A, W81_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W81_A), ("B", W81_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 81:
            continue
        for key in ("a", "b_exit"):
            lo2, hi2 = cfg[key]
            if overlaps((lo2, hi2), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo2}..{hi2} x W81-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W81-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W81-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W81-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W81-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W81-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W81-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W81-{tag} (r335 leg)")
# canon cross-check: the landed W81 row must equal the derived candidate
assert N1_BANDS[81]["a"] == W81_A and N1_BANDS[81]["b_exit"] == W81_B, \
    "leg3 failed: canon W81 row drift vs derived candidate"
assert N1_BANDS[81]["engine_owner"] == "bm-b", "leg3 failed: W81 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 27, \
    "leg3 failed: post-land bm-b owned rows must be exactly 27 (TWENTY-SEVENTH " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "81: {\"a\": (205_004" not in out, \
    "leg3 failed: a W81 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "80: {\"a\": (203_004" in out, \
    "leg3 failed: the registered W80 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W81 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W81 ADMIT: A {W81_A[0]}..{W81_A[1]} (ARITHMETIC CONTINUATION from the "
      f"registered W80 tail, zero skip) + B {W81_B[0]}..{W81_B[1]} "
      f"(PAST-HIT RESTART over the upper-edge refusal point "
      f"SEED_REGISTRY t18_deep_axis=54_000; both readings coincide, single "
      f"reading no fork face) clean vs 78 registered rows + N3-R1 used-seed "
      f"band + probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-b (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2; W80 yielded to bm-c 7fbeadb2e first-land per r511 "
      f"commit-order law, same-window next-seat re-occupation per r565 law; "
      f"seat declared published=reserved MSG-20261002-1220-bmb pushed to "
      f"origin BEFORE this freeze; W80 bm-c = ONE in-flight upstream seat "
      f"for the W81 finalize chain, finalize FAIL-CLOSED r307; origin slot "
      f"vacancy machine-checked).")

# --- W82+ projection (warning text for the law table row) --------------------
w82_a = (W81_A[1] + 1, W81_A[1] + WIDTH_A)
w82_b = (W81_B[1] + 1, W81_B[1] + WIDTH_B)
a_hits82 = sorted(p for p in points if w82_a[0] <= p <= w82_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w82_a)]
b_hits82 = sorted(p for p in points if w82_b[0] <= p <= w82_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w82_b)]
print(f"W82+ projection: A arithmetic +2_000 = {w82_a[0]}..{w82_a[1]} "
      f"-> {'CLEAN (verify at W82 prereg)' if not a_hits82 else 'REFUSED ' + str(a_hits82)}; "
      f"B +200 from W81 end = {w82_b[0]}..{w82_b[1]} "
      f"-> {'CLEAN (verify at W82 prereg)' if not b_hits82 else 'REFUSED ' + str(b_hits82)}")
