# -*- coding: utf-8 -*-
"""W70 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W70 = FIFTY-NINTH ENGINE-OWNED WAVE candidate, bm-a's SEVENTEENTH owned per
machine-derive (engine_owner==bm-a rows 16 + candidate). Freeze authority =
never-dry supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series. W69 (bm-c r360) = table tail; W70 = next free
number (origin vacancy machine-checked at leg3). W69 = bm-c's seat
(published=reserved MSG-20261002-1015-bmc) -- NOT touched by this gate.

Bands: A 183_004..185_003 = ARITHMETIC CONTINUATION from the W69 A tail
(183_003 + 1). B = FORCED-SKIP family: arithmetic window 50_901..51_100 is
REFUSED by SEED_REGISTRY xstock_synth_null_a=51_000 (mid-band single-point
hit -- r307 W5 machine-red precedent: skip is forced, not a free pick).
DIVERGENCE FACE THIRD EXAMPLE (canon W69 row warning, F-20261002-03 ruling
pending): past-hit restart 51_001..51_200 (W26 r335 + W68 bm-a in-register
family -- THE PICK, this machine's own most-recent registered precedent)
vs window-stride chain 51_101..51_300 (W63 bm-c in-register family --
DISCLOSED alternative). Pre-ruling freeze = freezing-party gate derive +
mandatory divergence disclosure per the W69 row's directive line.

Machine-verified against: all 67 registered N1 wave bands W2..W69, N3-R1
used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points,
N2-W15 draft probe points, lfc actual draw, options_wave2 actual draw.

r569 bm-a freeze-window run. READ-ONLY against the 67-row table + origin
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
W70_A = (183_004, 185_003)              # arithmetic continuation, W69 A tail +1
W70_B = (51_001, 51_200)                # forced-skip past-hit restart (51_000)

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

# --- leg 0: registry shape (67 registered rows, NO W70 locally yet) -----------
pre_w70 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69]
assert sorted(N1_BANDS) == pre_w70, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 67 registered rows, candidate W70 NOT yet local)"
assert 69 in N1_BANDS and N1_BANDS[69]["engine_owner"] == "bm-c", \
    "leg0 failed: W69 (bm-c) table-tail row must be present (r360 freeze)"
assert 68 in N1_BANDS and N1_BANDS[68]["engine_owner"] == "bm-a", \
    "leg0 failed: W68 (bm-a) row must be present (finalize landed r569)"
assert 67 in N1_BANDS and N1_BANDS[67]["engine_owner"] == "bm-b", \
    "leg0 failed: W67 (bm-b) row must be present"
assert N1_BANDS[69]["a"] == (181_004, 183_003) and \
    N1_BANDS[69]["b_exit"] == (50_701, 50_900), \
    "leg0 failed: W69 band drift vs canon row"
assert N1_BANDS[68]["a"] == (179_004, 181_003) and \
    N1_BANDS[68]["b_exit"] == (50_501, 50_700), \
    "leg0 failed: W68 band drift vs canon row"
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(bma_rows) == 16, f"leg0 failed: bm-a rows {bma_rows} (expect 16)"
print("leg0: 67 registered rows (W2..W14, W16..W69), tail=W69 bm-c, "
      "candidate W70 not local (pre-insertion gate), bm-a rows=16")

# --- leg 0b: W69 row W70+ WARNING prose present in the canon law file --------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "183_004..185_003" in canon, \
    "leg0b failed: W69 row W70+ A projection prose not found in canon"
assert "50_901..51_100 REFUSED" in canon, \
    "leg0b failed: W69 row W70+ B arithmetic REFUSED prose not found in canon"
assert "51_001..51_200" in canon and "51_101..51_300" in canon, \
    "leg0b failed: W69 row W70+ B divergence disclosure prose not found in canon"
print("leg0b: W69 row W70+ WARNING prose present (A CLEAN / B REFUSED 51_000 "
      "-> divergence pair disclosed; bm-c r360 gate projection + this gate "
      "re-derives from live registry, never trusts prose -- r335/r535/r302)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[69]["a"][1] + 1, N1_BANDS[69]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[69]["b_exit"][1] + 1,
           N1_BANDS[69]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (183_004, 185_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (50_901, 51_100), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} {a_band_hits} (W69 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits -- no skip, W69 row projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [51_000] and b_band_hits == [], \
    f"leg1-B failed: expected machine-red [51_000] (forced skip, r307 W5 " \
    f"precedent -- refusal facts identity), got {b_hits} {b_band_hits}"
reg_key = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 51_000]
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"{{SEED_REGISTRY {reg_key}={b_hits[0]}}} -- machine-red = skip is "
      f"FORCED not free-picked (r307 W5 law)")

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
assert first_a == W70_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W70_A}"
# B: past-hit restart (W26 r335 + W68 bm-a in-register family -- THE PICK)
first_b = clean(b_hits[0] + 1, WIDTH_B)
assert first_b == W70_B, \
    f"leg2-B failed: past-hit first clean window {first_b} != candidate {W70_B}"
# window-stride alternative reading disclosure (r566 W63 divergence family):
stride_b = clean(ARITH_B[0] + WIDTH_B, WIDTH_B)
print(f"leg2: A first-clean == arithmetic == candidate {W70_A[0]}..{W70_A[1]}; "
      f"B past-hit restart == candidate {W70_B[0]}..{W70_B[1]} "
      f"(W26 + W68 bm-a in-register precedent family; window-stride "
      f"alternative reading would be {stride_b} -- disclosed, divergence "
      f"face THIRD example, law-sec.4 skip-semantics pin still pending "
      f"HQ-FEEDBACK F-20261002-03; canon W69 row pre-ruling directive = "
      f"freezing-party gate derive + mandatory divergence disclosure)")
assert not overlaps(W70_A, W70_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W70_A), ("B", W70_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W70-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W70-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W70-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W70-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W70-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W70-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W70-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W70-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W70 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "70: {\"a\": (183_004" not in out, \
    "leg3 failed: a W70 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "N1 \u6ce270\uff08" not in out, "leg3 failed: canon W70 row exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W70 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W70 ADMIT: A {W70_A[0]}..{W70_A[1]} (ARITHMETIC CONTINUATION from the "
      f"W69 A tail, zero skip) + B {W70_B[0]}..{W70_B[1]} (FORCED-SKIP "
      f"past-hit restart past SEED_REGISTRY {reg_key[0]}=51_000, W26+W68 "
      f"in-register past-hit family, window-stride alternative {stride_b} "
      f"DISCLOSED per the W69 row pre-ruling directive) -- clean vs 67 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-a "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"origin slot vacancy machine-checked; seat declaration "
      f"published=reserved follows in this window).")

# --- W71+ projection (warning text for the law table row) --------------------
w71_a = (W70_A[1] + 1, W70_A[1] + WIDTH_A)
w71_b = (W70_B[1] + 1, W70_B[1] + WIDTH_B)
a_hits71 = sorted(p for p in points if w71_a[0] <= p <= w71_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w71_a)]
b_hits71 = sorted(p for p in points if w71_b[0] <= p <= w71_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w71_b)]
print(f"W71+ projection: A arithmetic +2_000 = {w71_a[0]}..{w71_a[1]} "
      f"-> {'CLEAN (verify at W71 prereg)' if not a_hits71 else 'REFUSED ' + str(a_hits71)}; "
      f"B +200 from W70 end = {w71_b[0]}..{w71_b[1]} "
      f"-> {'CLEAN (verify at W71 prereg)' if not b_hits71 else 'REFUSED ' + str(b_hits71)}")
