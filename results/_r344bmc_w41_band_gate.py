"""W41 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W41 = THIRTY-FIRST ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's TENTH owned wave after W14/W17/W20/W23/W26/
W29/W32/W37/W39). FREEZE AUTHORITY = never-dry supply law standing step +
CEO DE-THROTTLE ORDER O-20261001-2355 sec.2 own-continuous-series:
bm-c's previous wave W39 closed FULL-LIFECYCLE (r342 freeze -> 12/12
no-restart burn -> r343 finalize one-pass K=83,720, ledger 448,340
chain-linear, products delivered to origin r344) -> zero-gap relay,
wave number 41 = FIRST FREE NUMBER after W40's landed claim (bm-b r531,
02:01 ignition live-validated, burn in flight at freeze window).

The W40 row's W41+ WARNING projects BOTH sides arithmetic CLEAN
(A 125_004..127_003 / B 43_401..43_600, both == W40 tail + 1). r335
lesson (projections can carry scanning-universe blind spots) + r535
law (clean-projection claims must be machine-derived, never
prose-copied): this gate re-derives from the live registry, never
trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W40 (38
rows, W39/W40 included), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every gate
receipt from W26 on), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r344 bm-c freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W41_A = (125_004, 127_003)              # law sec.4 W41 row (arithmetic, no skip)
W41_B = (43_401, 43_600)                # arithmetic, no skip (== W40 B tail + 1)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)       # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W41 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 41:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (38 pre-W41 rows + the candidate) ------------------
assert 39 in N1_BANDS and N1_BANDS[39]["engine_owner"] == "bm-c", \
    "leg0 failed: W39 (bm-c) rows must be present (r342 freeze; finalize " \
    "landed r343, products delivered r344)"
assert 40 in N1_BANDS and N1_BANDS[40]["engine_owner"] == "bm-b", \
    "leg0 failed: W40 (bm-b) rows must be present (r531 freeze, ignition " \
    "live-validated, burn in flight)"
pre_w41 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41]
assert sorted(N1_BANDS) == pre_w41, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"38 registered rows + the W41 candidate)"

# --- leg 0b: W40 row's W41+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "125_004..127_003" in canon and "43_401..43_600" in canon, \
    "leg0b failed: W40 row W41+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W40 row W41+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[40]["a"][1] + 1, N1_BANDS[40]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[40]["b_exit"][1] + 1,
           N1_BANDS[40]["b_exit"][1] + WIDTH_B)
# Both tails projected CLEAN by the W40 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W40 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W40 "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: expected CLEAN (W40 projection), got {b_hits}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W40 projection verified machine-side)")

# --- leg 2: first clean window (A == arithmetic; B == machine-derived) ------
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
assert first_a == W41_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W41_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W41_B == ARITH_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W41_B} (arithmetic continuation expected, derived not " \
    "prose-copied -- r307/r535)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (arithmetic continuation, derived not picked)")
assert not overlaps(W41_A, W41_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W41_A), ("B", W41_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 41:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W41-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W41-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W41-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W41-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W41-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W41-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W41-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W41-{tag} (r335 leg)")
# canon cross-check: the landed W41 row must equal the derived candidate
assert N1_BANDS[41]["a"] == W41_A and N1_BANDS[41]["b_exit"] == W41_B, \
    "leg3 failed: canon W41 row drift vs derived candidate"
assert N1_BANDS[41]["engine_owner"] == "bm-c", "leg3 failed: W41 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "41: {\"a\": (125_004" not in out, \
    "leg3 failed: a W41 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W41 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W41 ADMIT: A {W41_A[0]}..{W41_A[1]} (arithmetic continuation, no "
      f"skip) + B {W41_B[0]}..{W41_B[1]} (arithmetic continuation, no "
      f"skip) both clean vs 38 registered rows + N3-R1 used-seed band + "
      f"probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-c (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2; zero-gap relay after the W39 full closeout "
      f"r342-r344; origin slot vacancy machine-checked).")

# --- W42+ projection (warning text for the law table row) --------------------
w42_a = (W41_A[1] + 1, W41_A[1] + WIDTH_A)
w42_b = (W41_B[1] + 1, W41_B[1] + WIDTH_B)
a_hits42 = sorted(p for p in points if w42_a[0] <= p <= w42_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w42_a)]
b_hits42 = sorted(p for p in points if w42_b[0] <= p <= w42_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w42_b)]
print(f"W42+ projection: A arithmetic +2_000 = {w42_a[0]}..{w42_a[1]} "
      f"-> {'CLEAN (verify at W42 prereg)' if not a_hits42 else 'REFUSED ' + str(a_hits42)}; "
      f"B +200 from W41 end = {w42_b[0]}..{w42_b[1]} "
      f"-> {'CLEAN (verify at W42 prereg)' if not b_hits42 else 'REFUSED ' + str(b_hits42)}")
