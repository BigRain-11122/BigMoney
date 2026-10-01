"""W57 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W57 = FORTY-SIXTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- bm-a's FOURTEENTH owned wave). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series: bm-a's previous wave W54
burned 12/12 and products were delivered to origin at r561 S0 surgical
(finalize chain-pending behind W53). Wave number 57 = FIRST FREE NUMBER
after the registered W56 row (the W56 slot was taken same-window by
bm-b r560; this machine's W56 drafts yielded unpushed and unburned --
zero pollution, yield_record in the round report).

The W56 row's W57+ WARNING projects BOTH SIDES ARITHMETIC CLEAN:
A 157_004..159_003, B 47_401..47_600 -- bm-b r560 freeze gate machine
projection + this gate re-derives from the live registry, never trusts
the prose (r335 lesson + r535 law).

Machine-verified against: all registered N1 wave bands W2..W56 (54
rows, incl. W53 bm-c / W54 bm-a / W55+W56 bm-b registered with
finalizes NOT landed = FOUR in-flight upstream seats -- coexist by
band disjointness per r531 law), the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 mandatory leg), the runner design-probe
seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use + W1 ext
bands, SEED_REGISTRY live values, N2/N4 design-probe points, N2-W15
draft probe points, lfc actual draw and options_wave2 actual draw.

r561 bm-a freeze-window run (de-throttle order O-20261001-2355 sec.2).
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
W57_A = (157_004, 159_003)              # law sec.4 W57 row (arithmetic, no skip)
W57_B = (47_401, 47_600)                # law sec.4 W57 row (arithmetic, no skip)

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

# --- reserved universe (W57 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 57:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (54 pre-W57 rows + the candidate) -----------------
assert 56 in N1_BANDS and N1_BANDS[56]["engine_owner"] == "bm-b", \
    "leg0 failed: W56 (bm-b) row must be present (r560 freeze, in-flight seat)"
assert 55 in N1_BANDS and N1_BANDS[55]["engine_owner"] == "bm-b", \
    "leg0 failed: W55 (bm-b) row must be present (12/12 delivered, finalize pending)"
assert 54 in N1_BANDS and N1_BANDS[54]["engine_owner"] == "bm-a", \
    "leg0 failed: W54 (bm-a) row must be present (12/12 delivered r561 S0, finalize pending)"
assert 53 in N1_BANDS and N1_BANDS[53]["engine_owner"] == "bm-c", \
    "leg0 failed: W53 (bm-c) row must be present (registered, finalize pending)"
assert 52 in N1_BANDS and N1_BANDS[52]["engine_owner"] == "bm-c", \
    "leg0 failed: W52 (bm-c) row must be present (finalize landed K=112,320 ledger head 478,948)"
assert 48 in N1_BANDS and N1_BANDS[48]["engine_owner"] == "bm-a", \
    "leg0 failed: W48 (bm-a) row must be present (finalize landed r558 K=103,520)"
pre_w57 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
assert sorted(N1_BANDS) == pre_w57, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 54 " \
    f"registered rows + the W57 candidate)"

# --- leg 0b: W56 row's W57+ WARNING prose present in the canon law file ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "157_004..159_003" in canon and "47_401..47_600" in canon, \
    "leg0b failed: W56 row W57+ WARNING (published projection) prose not " \
    "found in the canon file"
print("leg0b W56 row W57+ WARNING prose present (published projection basis; "
      "machine-derived per r535; bm-b r560 gate + this gate cross-checked)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[56]["a"][1] + 1, N1_BANDS[56]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[56]["b_exit"][1] + 1,
           N1_BANDS[56]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W56 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W56 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W56 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W56 row "
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
assert first_a == W57_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W57_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W57_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W57_B} " \
    "(no skip expected; R250/r518 machine-derived)"
print("leg2 both sides: first clean window == arithmetic == candidate "
      "(zero-skip wave, both-sides arithmetic continuation)")
assert not overlaps(W57_A, W57_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W57_A), ("B", W57_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 57:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W57-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W57-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W57-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W57-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W57-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W57-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W57-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W57-{tag} (r335 leg)")
# canon cross-check: the landed W57 row must equal the derived candidate
assert N1_BANDS[57]["a"] == W57_A and N1_BANDS[57]["b_exit"] == W57_B, \
    "leg3 failed: canon W57 row drift vs derived candidate"
assert N1_BANDS[57]["engine_owner"] == "bm-a", "leg3 failed: W57 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "57: {\"a\": (157_004" not in out, \
    "leg3 failed: a W57 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W57 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W57 ADMIT: A {W57_A[0]}..{W57_A[1]} + B {W57_B[0]}..{W57_B[1]} both "
      f"ARITHMETIC CONTINUATION from the W56 tail (zero skip, both CLEAN "
      f"== the W56 row W57+ published projection verbatim, bm-b r560 gate "
      f"+ this gate cross-validated) clean vs 54 registered rows + N3-R1 "
      f"used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-a (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; own-series continuation after "
      f"the W54 burn-and-delivery; W53/W54/W55/W56 in-flight finalizes "
      f"coexist per r531; origin slot vacancy machine-checked).")

# --- W58+ projection (warning text for the law table row) --------------------
w58_a = (W57_A[1] + 1, W57_A[1] + WIDTH_A)
w58_b = (W57_B[1] + 1, W57_B[1] + WIDTH_B)
a_hits58 = sorted(p for p in points if w58_a[0] <= p <= w58_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w58_a)]
b_hits58 = sorted(p for p in points if w58_b[0] <= p <= w58_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w58_b)]
print(f"W58+ projection: A arithmetic +2_000 = {w58_a[0]}..{w58_a[1]} "
      f"-> {'CLEAN (verify at W58 prereg)' if not a_hits58 else 'REFUSED ' + str(a_hits58)}; "
      f"B +200 from W57 end = {w58_b[0]}..{w58_b[1]} "
      f"-> {'CLEAN (verify at W58 prereg)' if not b_hits58 else 'REFUSED ' + str(b_hits58)}")
