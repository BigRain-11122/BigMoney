"""W42 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W42 = THIRTY-SECOND ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's FOURTEENTH owned wave after W10/W11/W13/
W16/W19/W22/W25/W28/W31/W34/W36/W38/W40). FREEZE AUTHORITY = never-dry
supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series: bm-b's previous wave W40 closed
FULL-LIFECYCLE (r531 freeze -> 12/12 burn -> r532 finalize one-pass
K=85,920, ledger head 450,540, prereg s7/s8 backfilled); W41 = bm-c
lineage (registered + burn in flight, finalize pending bm-c lane)
-> zero-gap relay, wave number 42 = FIRST FREE NUMBER after bm-c's
W41 landed claim (r511 tail-lock fetch-verified before landing).

The W41 row's W42+ WARNING projects: A arithmetic +2_000 = 127_004..
129_003 CLEAN; B +200 = 43_601..43_800 CLEAN. r335/r535 lesson: this
gate re-derives from the live registry, never trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W41 (39
rows), N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x mandatory leg),
runner design-probe seed cluster 95_000..95_003 (r335 mandatory leg),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe
points (40_000/40_001), N2-W15 draft probe points (31_000/31_500/
32_000), lfc actual draw (30_000..30_099) AND options_wave2 actual
draw (63_000..63_049).

r533 bm-b freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W42_A = (127_004, 129_003)              # law sec.4 W42 row (arithmetic, no skip)
W42_B = (43_601, 43_800)                # arithmetic continuation (no skip)

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

# --- reserved universe (W42 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 42:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (39 pre-W42 rows + the candidate) ----------------
assert 41 in N1_BANDS and N1_BANDS[41]["engine_owner"] == "bm-c", \
    "leg0 failed: W41 (bm-c) row must be present (r344 freeze lineage)"
pre_w42 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42]
assert sorted(N1_BANDS) == pre_w42, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"39 registered rows + the W42 candidate)"

# --- leg 0b: W41 row's W42+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "127_004..129_003" in canon and "43_601..43_800" in canon, \
    "leg0b failed: W41 row W42+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W41 row W42+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[41]["a"][1] + 1, N1_BANDS[41]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[41]["b_exit"][1] + 1,
           N1_BANDS[41]["b_exit"][1] + WIDTH_B)
# A arithmetic projected CLEAN by the W41 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [f"band {b}" for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} {a_band_hits} " \
    "(W41 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits -- no skip, W41 projection verified machine-side)")
# B arithmetic projected CLEAN by the W41 row -- verify machine-side:
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [f"band {b}" for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [] and b_band_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} {b_band_hits} " \
    "(W41 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W41 projection verified machine-side)")

# --- leg 2: first clean window == candidate (A and B both no-skip) -----------
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
assert first_a == W42_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W42_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=(W42_A,))
assert first_b == W42_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W42_B} " \
    "(no skip expected; both sides independently adjudicated per the " \
    f"W41 WARNING prose -- machine-derived)"
assert not overlaps(W42_A, W42_B), "A/B overlap"
print(f"leg2-B first clean window: {first_b[0]}..{first_b[1]} "
      f"(arithmetic, zero skip both sides)")

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W42_A), ("B", W42_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 42:
            continue
        for key in ("a", "b_exit"):
            lo_, hi_ = cfg[key]
            if overlaps((lo_, hi_), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo_}..{hi_} x W42-{tag}")
    for kk, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{kk}]={v} inside W42-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W42-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W42-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W42-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W42-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W42-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W42-{tag} (r335 leg)")
# canon cross-check: the landed W42 row must equal the derived candidate
assert N1_BANDS[42]["a"] == W42_A and N1_BANDS[42]["b_exit"] == W42_B, \
    "leg3 failed: canon W42 row drift vs derived candidate"
assert N1_BANDS[42]["engine_owner"] == "bm-b", "leg3 failed: W42 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "42: {\"a\": (127_004, 129_003)" not in out, \
    "leg3 failed: a W42 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W42 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W42 ADMIT: A {W42_A[0]}..{W42_A[1]} (arithmetic, no skip) + "
      f"B {W42_B[0]}..{W42_B[1]} (arithmetic, no skip) both clean vs 39 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-b "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"zero-gap relay after the W40 FULL CLOSEOUT; both sides zero-skip "
      f"arithmetic continuation, refusal facts machine-verified; origin "
      f"slot vacancy machine-checked).")

# --- W43+ projection (warning text for the law table row) --------------------
w43_a = (W42_A[1] + 1, W42_A[1] + WIDTH_A)
w43_b = (W42_B[1] + 1, W42_B[1] + WIDTH_B)
a_hits43 = sorted(p for p in points if w43_a[0] <= p <= w43_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w43_a)]
b_hits43 = sorted(p for p in points if w43_b[0] <= p <= w43_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w43_b)]
print(f"W43+ projection: A arithmetic +2_000 = {w43_a[0]}..{w43_a[1]} "
      f"-> {'CLEAN (verify at W43 prereg)' if not a_hits43 else 'REFUSED ' + str(a_hits43)}; "
      f"B +200 from W42 B end = {w43_b[0]}..{w43_b[1]} "
      f"-> {'CLEAN (verify at W43 prereg)' if not b_hits43 else 'REFUSED ' + str(b_hits43)}")
