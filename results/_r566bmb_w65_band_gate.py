# -*- coding: utf-8 -*-
"""W65 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W65 = FIFTY-FOURTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTIETH owned wave, machine-derived:
19 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (MSG-20261002-0919-bmb, r518-1 law).

W64 SAME-BAND DOUBLE-FREEZE YIELD CONTEXT (this window): the crashed
r565 bm-b session froze W64 with bands IDENTICAL to bm-a's registered
W64 row (deterministic derive, r530 same-band class). bm-a's freeze
f41a9009d landed on origin first -> r511 commit-order law: bm-b
yields; the r565 freeze drafts (uncommitted) fully discarded, 10
duplicate shard products attribution-verified (audit.machine=bm-b)
and discarded, zero ledger pollution (finalize never ran).

With W64 registered (engine_owner=bm-a, bands A 171_004..173_003 /
B 49_401..49_600) and W63 finalize LANDED (bm-c r358, K=136,520,
ledger head 503,148), this gate re-derives BOTH SIDES from the live
registry, never trusting the prose (r335 lesson + r535 law):
  A = 173_004..175_003 (W64 A end + 1, width 2_000, no skip)
  B = 49_601..49_800   (W64 B end + 1, width 200, no skip)

Machine-verified against: all registered N1 wave bands W2..W64,
the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory
leg), the runner design-probe seed cluster 95_000..95_003 (r335
discovery leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points, N2-W15 draft probe points, lfc
actual draw and options_wave2 actual draw.

r566 bm-b freeze-window run (never-dry standing step, O-20261001-2355
sec.2 own-series; crashed-r565 recovery round).
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
W65_A = (173_004, 175_003)              # law sec.4 W65 row (arithmetic, no skip)
W65_B = (49_601, 49_800)                # law sec.4 W65 row (arithmetic, no skip)

# --- registered W64 row (bm-a r566 freeze f41a9009d, registered tail) --------
W64_REGISTERED_A = (171_004, 173_003)
W64_REGISTERED_B = (49_401, 49_600)

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

# --- leg 0-hold: zero-gap relay (W64 must be REGISTERED before ADMIT) -------
if 64 not in N1_BANDS:
    print("HOLD: W64 row not yet registered in the live registry. W65 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock). "
          "Seat reservation for W65 stands (MSG-20261002-0919-bmb, "
          "published=reserved).")
    sys.exit(3)

assert N1_BANDS[64]["a"] == W64_REGISTERED_A and \
    N1_BANDS[64]["b_exit"] == W64_REGISTERED_B and \
    N1_BANDS[64].get("engine_owner") == "bm-a", \
    "leg0 failed: registered W64 row != expected registered bands " \
    "(A 171_004..173_003 / B 49_401..49_600, bm-a f41a9009d) -- " \
    "derivation basis invalidated, RE-DERIVE the W65 candidates"

# --- reserved universe (W65 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 65:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (63 pre-W65 registered rows + the candidate) ------
assert 62 in N1_BANDS and N1_BANDS[62]["engine_owner"] == "bm-a", \
    "leg0 failed: W62 (bm-a) row must be present (finalize landed " \
    "cross-machine bm-c r357 K=134,320)"
assert 63 in N1_BANDS and N1_BANDS[63]["engine_owner"] == "bm-c", \
    "leg0 failed: W63 (bm-c) row must be present (finalize LANDED " \
    "bm-c r358 K=136,520 ledger head 503,148)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w63_results.json")), \
    "leg0 failed: W63 finalize product missing (landed 4de45c3e0 -- " \
    "fetch/ff freshness)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 20, \
    "leg0 failed: bm-b owned-row count != 20 (19 pre-candidate + the " \
    "landed W65 candidate -- machine-derive basis for the TWENTIETH " \
    "owned wave claim)"
pre_w65 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65]
assert sorted(N1_BANDS) == pre_w65, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 63 " \
    f"registered rows + the W65 candidate)"

# --- leg 0b: W64 row's W65+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "173_004..175_003" in canon and "49_601..49_800" in canon, \
    "leg0b failed: W64 row W65+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W64 row W65+ WARNING prose present (published projection "
      "basis; machine-derived per r535; registered W64 bm-a row bands "
      "cross-checked verbatim")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[64]["a"][1] + 1, N1_BANDS[64]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[64]["b_exit"][1] + 1,
           N1_BANDS[64]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W64 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W64 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W64 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W64 row "
      f"projection verified machine-side)")

# --- leg 2: first clean windows (both sides == arithmetic, no skip) ----------
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
assert first_a == W65_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W65_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W65_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W65_B} " \
    "(no skip expected this wave; R250/r518 machine-derived)"
print(f"leg2 first clean windows == arithmetic positions both sides "
      f"(A {first_a[0]}..{first_a[1]} / B {first_b[0]}..{first_b[1]}, "
      f"no skip this wave)")
assert not overlaps(W65_A, W65_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W65_A), ("B", W65_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 65:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W65-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W65-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W65-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W65-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W65-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W65-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W65-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W65-{tag} (r335 leg)")
# canon cross-check: the landed W65 row must equal the derived candidate
assert N1_BANDS[65]["a"] == W65_A and N1_BANDS[65]["b_exit"] == W65_B, \
    "leg3 failed: canon W65 row drift vs derived candidate"
assert N1_BANDS[65]["engine_owner"] == "bm-b", "leg3 failed: W65 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 20, \
    "leg3 failed: post-land bm-b owned rows must be exactly 20 (TWENTIETH " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "65: {\"a\": (173_004" not in out, \
    "leg3 failed: a W65 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "64: {\"a\": (171_004" in out, \
    "leg3 failed: the registered W64 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W65 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W65 ADMIT: A {W65_A[0]}..{W65_A[1]} + B {W65_B[0]}..{W65_B[1]} both "
      f"ARITHMETIC CONTINUATION from the registered W64 tail (zero skip, "
      f"both CLEAN == the W64 row W65+ published projection verbatim, "
      f"bm-a r566 gate projection leg + this gate cross-validated) clean "
      f"vs 63 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-b "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"seat declared published=reserved MSG-20261002-0919-bmb after the "
      f"W64 same-band double-freeze yield per r511 commit-order law; W64 "
      f"bm-a = ONE in-flight upstream seat for the W65 finalize chain, "
      f"coexist per r531, finalize FAIL-CLOSED r307; origin slot vacancy "
      f"machine-checked).")

# --- W66+ projection (warning text for the law table row) --------------------
w66_a = (W65_A[1] + 1, W65_A[1] + WIDTH_A)
w66_b = (W65_B[1] + 1, W65_B[1] + WIDTH_B)
a_hits66 = sorted(p for p in points if w66_a[0] <= p <= w66_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w66_a)]
b_hits66 = sorted(p for p in points if w66_b[0] <= p <= w66_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w66_b)]
print(f"W66+ projection: A arithmetic +2_000 = {w66_a[0]}..{w66_a[1]} "
      f"-> {'CLEAN (verify at W66 prereg)' if not a_hits66 else 'REFUSED ' + str(a_hits66)}; "
      f"B +200 from W65 end = {w66_b[0]}..{w66_b[1]} "
      f"-> {'CLEAN (verify at W66 prereg)' if not b_hits66 else 'REFUSED ' + str(b_hits66)}")
