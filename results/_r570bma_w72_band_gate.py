# -*- coding: utf-8 -*-
"""W72 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W72 = SIXTY-FIRST ENGINE-OWNED WAVE candidate, bm-a's SEVENTEENTH owned per
machine-derive (engine_owner==bm-a rows 16 + candidate). Freeze authority =
never-dry supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series. W71 (bm-c r361) = table tail; W72 = next free
number (origin vacancy machine-checked at leg3). W71 = bm-c's wave
(seat MSG-20261002-1017-bmc) -- NOT touched by this gate.

Bands: BOTH SIDES ARITHMETIC CONTINUATION, zero skip:
  A 187_004..189_003 = W71 A tail (187_003 + 1) + 2_000 width
  B 51_401..51_600   = W71 B tail (51_400 + 1) + 200 width
The W71 canon row carries the W72+ WARNING projection "A 187_004..189_003 /
B 51_401..51_600 double CLEAN" (bm-c r361 gate projection leg) -- this gate
re-derives from the live registry per r335/r302 (never trusts prose).

Machine-verified against: all 69 registered N1 wave bands W2..W71, N3-R1
used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values (LOWAMP-P1/P2/P3 20.33M domain keys
included), N2/N4 design-probe points, N2-W15 draft probe points, lfc
actual draw, options_wave2 actual draw.

r570 bm-a freeze-window run. READ-ONLY against the 69-row table + origin
(candidate passed as parameter; local insertion happens in freeze edits
with FIX-A/B/C hardening, MSG-0640 lineage).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (pre-insertion gate: parameter, not local row) ----------------
W72_A = (187_004, 189_003)              # arithmetic continuation, W71 A tail +1
W72_B = (51_401, 51_600)                # arithmetic continuation, W71 B tail +1

N3R1_USED = (70_000, 70_005)
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

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (69 registered rows, NO W72 locally yet) -----------
pre_w72 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70, 71]
assert sorted(N1_BANDS) == pre_w72, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 69 registered rows, candidate W72 NOT yet local)"
assert 71 in N1_BANDS and N1_BANDS[71]["engine_owner"] == "bm-c", \
    "leg0 failed: W71 (bm-c) table-tail row must be present (r361 freeze)"
assert 70 in N1_BANDS and N1_BANDS[70]["engine_owner"] == "bm-b", \
    "leg0 failed: W70 (bm-b) row must be present (r568 freeze)"
assert 69 in N1_BANDS and N1_BANDS[69]["engine_owner"] == "bm-c", \
    "leg0 failed: W69 (bm-c) row must be present (r360 freeze, finalize landed r361)"
assert 68 in N1_BANDS and N1_BANDS[68]["engine_owner"] == "bm-a", \
    "leg0 failed: W68 (bm-a) row must be present (finalize landed r569)"
assert N1_BANDS[71]["a"] == (185_004, 187_003) and \
    N1_BANDS[71]["b_exit"] == (51_201, 51_400), \
    "leg0 failed: W71 band drift vs canon row"
assert N1_BANDS[70]["a"] == (183_004, 185_003) and \
    N1_BANDS[70]["b_exit"] == (51_001, 51_200), \
    "leg0 failed: W70 band drift vs canon row"
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(bma_rows) == 16, f"leg0 failed: bm-a rows {bma_rows} (expect 16)"
print("leg0: 69 registered rows (W2..W14, W16..W71), tail=W71 bm-c, "
      "candidate W72 not local (pre-insertion gate), bm-a rows=16")

# --- leg 0b: W71 row W72+ WARNING prose present in the canon law file --------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "187_004..189_003" in canon, \
    "leg0b failed: W71 row W72+ A projection prose not found in canon"
assert "51_401..51_600" in canon, \
    "leg0b failed: W71 row W72+ B projection prose not found in canon"
print("leg0b: W71 row W72+ WARNING prose present (double CLEAN projection; "
      "this gate re-derives from the live registry, never trusts prose "
      "-- r335/r535/r302)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[71]["a"][1] + 1, N1_BANDS[71]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[71]["b_exit"][1] + 1,
           N1_BANDS[71]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (187_004, 189_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (51_401, 51_600), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} {a_band_hits} (W71 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits -- no skip, W71 row projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [] and b_band_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} {b_band_hits} (W71 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, W71 row projection verified machine-side)")

# --- leg 2: first clean window -----------------------------------------------
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
    f"leg2-A failed: first clean window {first_a} != candidate {W72_A}"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W72_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W72_B}"
print(f"leg2: A first-clean == arithmetic == candidate {W72_A[0]}..{W72_A[1]}; "
      f"B first-clean == arithmetic == candidate {W72_B[0]}..{W72_B[1]} "
      f"(BOTH SIDES ARITHMETIC CONTINUATION, zero skip; no divergence face -- "
      f"zero refusal points in either arithmetic window, single reading)")
assert not overlaps(W72_A, W72_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W72_A), ("B", W72_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W72-{tag}")
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
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W72-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W72-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W72 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "72: {\"a\": (187_004" not in out, \
    "leg3 failed: a W72 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "N1 \u6ce272\uff08" not in out, "leg3 failed: canon W72 row exists on origin"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W72"' not in outn1, \
    "leg3 failed: a W72 WAVE_CONFIGS entry ALREADY exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W72 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W72 ADMIT: A {W72_A[0]}..{W72_A[1]} (ARITHMETIC CONTINUATION from the "
      f"W71 A tail, zero skip) + B {W72_B[0]}..{W72_B[1]} (ARITHMETIC "
      f"CONTINUATION from the W71 B tail, zero skip, single reading no "
      f"divergence) -- clean vs 69 registered rows + N3-R1 used-seed band + "
      f"probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-a (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2; origin slot vacancy machine-checked; seat "
      f"declaration published=reserved follows in this window "
      f"MSG-20261002-1032-bma).")

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
