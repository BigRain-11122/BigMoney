"""W52 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W52 = FORTY-FIRST ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- bm-a's TWELFTH owned wave). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series: bm-a's previous wave W48
closed FULL-LIFECYCLE this same window (r557 freeze -> tick 12/12 burn
-> seat-loss re-derive finalize one-pass prev=470,148 total=472,348
K=103,520) -> zero-gap relay, wave number 52 = FIRST FREE NUMBER after
the registered W51 row.

The W51 row's W52+ WARNING projects BOTH SIDES ARITHMETIC CLEAN:
A 147_004..147_003+2_000 = 147_004..149_003, B 46_200+1..46_400.
This gate re-derives from the live registry, never trusts the prose
(r335 lesson + r535 law).

Machine-verified against: all registered N1 wave bands W2..W51 (49
rows, incl. W48 bm-a r557 landed / W49 bm-b r556 landed / W50+W51
bm-c r350 in-flight finalizes -- coexist by band disjointness per
r531 law), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points, N2-W15 draft probe points, lfc
actual draw and options_wave2 actual draw.

r558 bm-a freeze-window run (de-throttle order O-20261001-2355 sec.2).
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
W52_A = (147_004, 149_003)              # law sec.4 W52 row (arithmetic, no skip)
W52_B = (46_201, 46_400)                # law sec.4 W52 row (arithmetic, no skip)

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

# --- reserved universe (W52 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 52:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (49 pre-W52 rows + the candidate) -----------------
assert 51 in N1_BANDS and N1_BANDS[51]["engine_owner"] == "bm-c", \
    "leg0 failed: W51 (bm-c) row must be present (r350 freeze, burn 12/12, " \
    "finalize chain-pending)"
assert 50 in N1_BANDS and N1_BANDS[50]["engine_owner"] == "bm-c", \
    "leg0 failed: W50 (bm-c) row must be present (r350 freeze this window, " \
    "burn 12/12, finalize chain-pending)"
assert 49 in N1_BANDS and N1_BANDS[49]["engine_owner"] == "bm-b", \
    "leg0 failed: W49 (bm-b) row must be present (r556 freeze, finalize " \
    "landed ledger 470,148)"
assert 48 in N1_BANDS and N1_BANDS[48]["engine_owner"] == "bm-a", \
    "leg0 failed: W48 (bm-a) row must be present (r557 freeze, finalize " \
    "landed r558 seat-loss re-derive K=103,520 ledger 472,348)"
pre_w52 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52]
assert sorted(N1_BANDS) == pre_w52, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 49 " \
    f"registered rows + the W52 candidate)"

# --- leg 0b: W51 row's W52+ WARNING prose present in the canon law file ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "147_004..149_003" in canon and "46_201..46_400" in canon, \
    "leg0b failed: W51 row W52+ WARNING (published projection) prose not " \
    "found in the canon file"
print("leg0b W51 row W52+ WARNING prose present (published projection basis; "
      "machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[51]["a"][1] + 1, N1_BANDS[51]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[51]["b_exit"][1] + 1,
           N1_BANDS[51]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W51 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W51 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W51 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W51 row "
      f"projection verified machine-side)")

# --- leg 2: first clean window (both sides == arithmetic; zero-skip wave) ---
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
assert first_a == W52_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W52_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W52_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W52_B} " \
    "(no skip expected; R250/r518 machine-derived)"
print("leg2 both sides: first clean window == arithmetic == candidate "
      "(zero-skip wave, first both-sides arithmetic since W51)")
assert not overlaps(W52_A, W52_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W52_A), ("B", W52_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 52:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W52-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W52-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W52-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W52-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W52-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W52-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W52-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W52-{tag} (r335 leg)")
# canon cross-check: the landed W52 row must equal the derived candidate
assert N1_BANDS[52]["a"] == W52_A and N1_BANDS[52]["b_exit"] == W52_B, \
    "leg3 failed: canon W52 row drift vs derived candidate"
assert N1_BANDS[52]["engine_owner"] == "bm-a", "leg3 failed: W52 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "52: {\"a\": (147_004" not in out, \
    "leg3 failed: a W52 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W52 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W52 ADMIT: A {W52_A[0]}..{W52_A[1]} + B {W52_B[0]}..{W52_B[1]} both "
      f"ARITHMETIC CONTINUATION from the W51 tail (zero skip, both CLEAN "
      f"== the W51 row W52+ published projection verbatim) clean vs 49 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-a "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"zero-gap relay after the W48 full closeout this same window; "
      f"W50/W51 in-flight finalizes coexist per r531; origin slot vacancy "
      f"machine-checked).")

# --- W53+ projection (warning text for the law table row) --------------------
w53_a = (W52_A[1] + 1, W52_A[1] + WIDTH_A)
w53_b = (W52_B[1] + 1, W52_B[1] + WIDTH_B)
a_hits53 = sorted(p for p in points if w53_a[0] <= p <= w53_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w53_a)]
b_hits53 = sorted(p for p in points if w53_b[0] <= p <= w53_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w53_b)]
print(f"W53+ projection: A arithmetic +2_000 = {w53_a[0]}..{w53_a[1]} "
      f"-> {'CLEAN (verify at W53 prereg)' if not a_hits53 else 'REFUSED ' + str(a_hits53)}; "
      f"B +200 from W52 end = {w53_b[0]}..{w53_b[1]} "
      f"-> {'CLEAN (verify at W53 prereg)' if not b_hits53 else 'REFUSED ' + str(b_hits53)}")
