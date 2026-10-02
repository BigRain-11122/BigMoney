# -*- coding: utf-8 -*-
"""W76 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W76 = SIXTY-FIFTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTY-FIFTH owned wave, machine-derived:
24 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (r518-1 law; MSG-20261002-1130-bmb). W74 finalize
LANDED (bm-b r572, net chain head 527,348, K=160,720 -- W1..W74 all
landed); W75 bm-a (burn in flight, finalize pending) = ONE in-flight
upstream seat at this freeze (FAIL-CLOSED r307).

BANDS (BOTH SIDES ARITHMETIC CONTINUATION from the registered W75
tail, zero skip):
  A: W75 A end 195_003 + 1 -> 195_004..197_003  (CLEAN, no hits)
  B: W75 B end 52_400 + 1 -> 52_401..52_600      (CLEAN, no hits)
Single reading, no fork face (F-20261002-03 skip-semantics divergence
not triggered -- no refusal point inside either window). NOT a re-pick
(R250: W76 bands were never assigned).
The W75 canon row CARRIES the W76+ WARNING projection (A CLEAN /
B CLEAN, machine-verified by the bm-a r571 gate projection leg). This
gate re-derives BOTH sides independently from the registered W75 row
(r302 stale-pointer law / r335 machine-derive law -- prose is a
cross-check only, never the derivation basis).

Machine-verified against: all registered N1 wave bands W2..W75, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r572 bm-b freeze-window run (never-dry standing step,
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
W76_A = (195_004, 197_003)              # law sec.4 W76 row (arithmetic, no skip)
W76_B = (52_401, 52_600)                # law sec.4 W76 row (arithmetic, no skip)

# --- registered W75 row (bm-a r571 freeze, registered tail) -------------------
W75_REGISTERED_A = (193_004, 195_003)
W75_REGISTERED_B = (52_201, 52_400)

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

# --- leg 0-hold: zero-gap relay (W75 must be REGISTERED before ADMIT) --------
if 75 not in N1_BANDS:
    print("HOLD: W75 row not yet registered in the live registry. W76 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[75]["a"] == W75_REGISTERED_A and \
    N1_BANDS[75]["b_exit"] == W75_REGISTERED_B and \
    N1_BANDS[75].get("engine_owner") == "bm-a", \
    "leg0 failed: registered W75 row != expected registered bands " \
    "(A 193_004..195_003 / B 52_201..52_400, bm-a r571) -- " \
    "derivation basis invalidated, RE-DERIVE the W76 candidates"

# --- reserved universe (W76 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 76:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (73 pre-W76 registered rows + the candidate) ------
assert 74 in N1_BANDS and N1_BANDS[74]["engine_owner"] == "bm-b", \
    "leg0 failed: W74 (bm-b) row must be present (registered r571, " \
    "finalize LANDED r572 -- chain head 527,348, K=160,720)"
assert 75 in N1_BANDS and N1_BANDS[75]["engine_owner"] == "bm-a", \
    "leg0 failed: W75 (bm-a) row must be present (registered r571, " \
    "burn in flight -- finalize chain-pending FAIL-CLOSED r307)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w74_results.json")), \
    "leg0 failed: W74 finalize product missing (landed by bm-b r572, " \
    "net chain head 527,348, K=160,720 -- it stays the S5 anchor " \
    "while the W75 finalize is in flight)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 25, \
    "leg0 failed: bm-b owned-row count != 25 (24 pre-candidate + the " \
    "landed W76 candidate -- machine-derive basis for the TWENTY-FIFTH " \
    "owned wave claim)"
pre_w76 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76]
assert sorted(N1_BANDS) == pre_w76, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 73 " \
    f"registered rows + the W76 candidate)"

# --- leg 0b: W75 row's W76+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for prose in ("195_004..197_003", "52_401..52_600"):
    assert prose in canon, \
        f"leg0b failed: W75 row W76+ WARNING prose '{prose}' not found " \
        f"in the canon file"
print("leg0b W75 row W76+ WARNING prose present (registered projection "
      "basis; machine-derived by the bm-a r571 gate projection leg; "
      "registered W75 bm-a row bands cross-checked verbatim; this gate "
      "re-derives independently per r302/r535 law)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[75]["a"][1] + 1, N1_BANDS[75]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[75]["b_exit"][1] + 1,
           N1_BANDS[75]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W75 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W75 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W75 row projected " \
    f"CLEAN -- expected zero hits, arithmetic continuation)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W75 row "
      f"projection verified machine-side)")

# --- leg 2: first clean windows (no skip expected either side) ---------------
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
assert first_a == W76_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W76_A} " \
    f"(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W76_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W76_B} " \
    f"(no skip expected -- arithmetic window CLEAN, single reading)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} / B "
      f"{first_b[0]}..{first_b[1]} (BOTH SIDES arithmetic continuation -- "
      f"zero skip, single reading, no fork face)")
assert not overlaps(W76_A, W76_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W76_A), ("B", W76_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 76:
            continue
        for key in ("a", "b_exit"):
            lo2, hi2 = cfg[key]
            if overlaps((lo2, hi2), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo2}..{hi2} x W76-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W76-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W76-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W76-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W76-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W76-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W76-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W76-{tag} (r335 leg)")
# canon cross-check: the landed W76 row must equal the derived candidate
assert N1_BANDS[76]["a"] == W76_A and N1_BANDS[76]["b_exit"] == W76_B, \
    "leg3 failed: canon W76 row drift vs derived candidate"
assert N1_BANDS[76]["engine_owner"] == "bm-b", "leg3 failed: W76 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 25, \
    "leg3 failed: post-land bm-b owned rows must be exactly 25 (TWENTY-FIFTH " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "76: {\"a\": (195_004" not in out, \
    "leg3 failed: a W76 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "75: {\"a\": (193_004" in out, \
    "leg3 failed: the registered W75 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W76 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W76 ADMIT: A {W76_A[0]}..{W76_A[1]} + B {W76_B[0]}..{W76_B[1]} "
      f"(BOTH SIDES ARITHMETIC CONTINUATION from the registered W75 tail, "
      f"zero skip, single reading no fork face) clean vs 73 registered rows "
      f"+ N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-b (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; seat declared published=reserved "
      f"MSG-20261002-1130-bmb; W75 bm-a = ONE in-flight upstream seat for "
      f"the W76 finalize chain, finalize FAIL-CLOSED r307; origin slot "
      f"vacancy machine-checked).")

# --- W77+ projection (warning text for the law table row) --------------------
w77_a = (W76_A[1] + 1, W76_A[1] + WIDTH_A)
w77_b = (W76_B[1] + 1, W76_B[1] + WIDTH_B)
a_hits77 = sorted(p for p in points if w77_a[0] <= p <= w77_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w77_a)]
b_hits77 = sorted(p for p in points if w77_b[0] <= p <= w77_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w77_b)]
print(f"W77+ projection: A arithmetic +2_000 = {w77_a[0]}..{w77_a[1]} "
      f"-> {'CLEAN (verify at W77 prereg)' if not a_hits77 else 'REFUSED ' + str(a_hits77)}; "
      f"B +200 from W76 end = {w77_b[0]}..{w77_b[1]} "
      f"-> {'CLEAN (verify at W77 prereg)' if not b_hits77 else 'REFUSED ' + str(b_hits77)}")
