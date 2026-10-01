"""W38 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W38 = TWENTY-SEVENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWELFTH owned wave after W10/W11/W13/W16/
W19/W22/W25/W28/W31/W34/W36). FREEZE AUTHORITY = never-dry supply law
standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2 own-
continuous-series: bm-b's previous wave W36 closed FULL-LIFECYCLE this
same window (r529: finalize one-pass prev 439,540 + 2,200 = 441,740,
K=77,120 == sec.0 projection verbatim; r528 crashed-session closeout)
-> zero-gap relay, wave number 38 = FIRST FREE NUMBER after W37's
landed claim (bm-c r341; seat system retired by the same order --
first-free-number law, no seat assignment). W37 (bm-c) is BURNING at
this freeze; finalize chain order preserved (W37 finalize precedes
W38 finalize -- order is not idleness, r543 law).

The W37 row's W38+ WARNING projects BOTH arithmetic tails CLEAN
(A +2_000 = 119_004..121_003, B +200 = 42_601..42_800). r335 lesson
(projections can carry scanning-universe blind spots) + r535 law
(clean-projection claims must be machine-derived, never prose-copied):
this gate re-derives from the live registry, never trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W37 (35
rows, W36/W37 included), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every gate
receipt from W26 on), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r529 bm-b freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W38_A = (119_004, 121_003)              # law sec.4 W38 row (arithmetic, no skip)
W38_B = (42_601, 42_800)                # arithmetic, no skip

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

# --- reserved universe (W38 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 38:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (35 pre-W38 rows + the candidate) -----------------
assert 36 in N1_BANDS and N1_BANDS[36]["engine_owner"] == "bm-b", \
    "leg0 failed: W36 (bm-b) rows must be present (r528 freeze, r529 close)"
assert 37 in N1_BANDS and N1_BANDS[37]["engine_owner"] == "bm-c", \
    "leg0 failed: W37 (bm-c) rows must be present (r341 freeze, burn in flight)"
pre_w38 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
           33, 34, 35, 36, 37, 38]
assert sorted(N1_BANDS) == pre_w38, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"35 registered rows + the W38 candidate)"

# --- leg 0b: W37 row's W38+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "119_004..121_003" in canon and "42_601..42_800" in canon, \
    "leg0b failed: W37 row W38+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W37 row W38+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[37]["a"][1] + 1, N1_BANDS[37]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[37]["b_exit"][1] + 1,
           N1_BANDS[37]["b_exit"][1] + WIDTH_B)
# BOTH arithmetic tails projected CLEAN by the W37 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W37 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W37 "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W37 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W37 projection verified machine-side)")

# --- leg 2: first clean window == arithmetic position (NO skip either side) --
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
assert first_a == W38_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W38_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=(W38_A,))
assert first_b == W38_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W38_B} " \
    "(no skip expected; own A band reserved per W6 law)"
assert not overlaps(W38_A, W38_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W38_A), ("B", W38_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 38:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W38-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W38-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W38-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W38-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W38-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W38-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W38-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W38-{tag} (r335 leg)")
# canon cross-check: the landed W38 row must equal the derived candidate
assert N1_BANDS[38]["a"] == W38_A and N1_BANDS[38]["b_exit"] == W38_B, \
    "leg3 failed: canon W38 row drift vs derived candidate"
assert N1_BANDS[38]["engine_owner"] == "bm-b", "leg3 failed: W38 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "38: {\"a\": (119_004, 121_003)" not in out, \
    "leg3 failed: a W38 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W38 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W38 ADMIT: A {W38_A[0]}..{W38_A[1]} + B {W38_B[0]}..{W38_B[1]} both "
      f"clean vs 35 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-b "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"zero-gap relay after the W36 full closeout; arithmetic continuation "
      f"BOTH tails, no skip -- W37 row W38+ WARNING projection verified "
      f"machine-side; origin slot vacancy machine-checked).")

# --- W39+ projection (warning text for the law table row) --------------------
w39_a = (W38_A[1] + 1, W38_A[1] + WIDTH_A)
w39_b = (W38_B[1] + 1, W38_B[1] + WIDTH_B)
a_hits39 = sorted(p for p in points if w39_a[0] <= p <= w39_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w39_a)]
b_hits39 = sorted(p for p in points if w39_b[0] <= p <= w39_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w39_b)]
print(f"W39+ projection: A arithmetic +2_000 = {w39_a[0]}..{w39_a[1]} "
      f"-> {'CLEAN (verify at W39 prereg)' if not a_hits39 else 'REFUSED ' + str(a_hits39)}; "
      f"B +200 from W38 end = {w39_b[0]}..{w39_b[1]} "
      f"-> {'CLEAN (verify at W39 prereg)' if not b_hits39 else 'REFUSED ' + str(b_hits39)}")
