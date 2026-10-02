# -*- coding: utf-8 -*-
"""W78 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W78 = SIXTY-SEVENTH ENGINE-OWNED WAVE candidate, bm-c's TWENTY-FOURTH
owned per machine-derive (engine_owner==bm-c rows 23 + candidate).
Freeze authority = never-dry supply law standing step + CEO DE-THROTTLE
ORDER O-20261001-2355 sec.2 own-continuous-series + r565
yield-then-reoccupy law (SECOND re-occupation this window): this
machine's W76 draft (bands A 195_004..197_003 / B 52_401..52_600) was
yielded to bm-b r572 (24ec53190 first-land per r511 commit-order;
bitwise cross-validation #11) and its W77 re-occupation draft (bands
A 197_004..199_003 / B 52_601..52_800, gate ADMIT
results/_r363bmc_w77_band_gate.py) was yielded to bm-a r572 (034c81887
first-land; bitwise cross-validation #12; the W77 freeze-edits run was
intercepted by FIX-A pre-edit = zero edit zero burn). W78 = second
re-occupation in the yield-receipt window; seat published=reserved
MSG-20261002-1150-bmc (pushed to origin BEFORE this freeze per r565
early-visibility lesson).

Bands (r535 machine-derive law; live-registry derived, W77-row prose
projection CORRECTED -- see leg1-B2):
  A 199_004..201_003 = W77 A tail (199_003 + 1) + 2_000 width -- CLEAN
  B  52_801..53_000  = W77 B tail (52_800 + 1) arithmetic window --
     REFUSED at upper-edge point SEED_REGISTRY j13v2_mill_ic1=53_000;
     the W77 row's prose first-clean 53_001..53_200 is STALE vs the
     live registry (mid point j13v2_mill_ic2=53_100, bm-b J13V2 IC2
     claim ac8a58490) -> chained double-hit skip 53_201..53_400
     (W63-B in-register precedent family; fork 53_101..53_300
     disclosed not taken, r566 face).

Machine-verified against: all 75 registered N1 wave bands W2..W77,
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points,
N2-W15 draft probe points, lfc actual draw, options_wave2 actual draw.

r363 bm-c freeze-window run (second yield-then-reoccupy). READ-ONLY
against the 75-row table + origin (candidate passed as parameter; local
insertion happens in the freeze edits tool with FIX-A/B/C hardening,
MSG-0640 lineage).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

# --- candidate (pre-insertion gate: parameter, not local row) ----------------
W78_A = (199_004, 201_003)              # arithmetic continuation, W77 A tail +1
W78_B = (53_201, 53_400)                # chained double-hit skip (W63 family)

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

# --- fresh tail check (r511 law: fetch before any freeze action) -------------
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

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

# --- leg 0: registry shape (75 registered rows, NO W78 locally yet) ----------
base_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 78))
assert sorted(N1_BANDS) == base_rows, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 75 registered rows W2..W14, W16..W77)"
assert 77 in N1_BANDS and N1_BANDS[77]["engine_owner"] == "bm-a", \
    "leg0 failed: W77 (bm-a r572) table-tail row must be present"
assert 76 in N1_BANDS and N1_BANDS[76]["engine_owner"] == "bm-b", \
    "leg0 failed: W76 (bm-b r572) row must be present"
assert N1_BANDS[77]["a"] == (197_004, 199_003) and \
    N1_BANDS[77]["b_exit"] == (52_601, 52_800), \
    "leg0 failed: W77 band drift vs canon row (bm-a r572 -- must equal " \
    "this machine's yielded W77 draft bands bitwise, r530 family)"
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(bmc_rows) == 23, f"leg0 failed: bm-c rows {bmc_rows} (expect 23)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W77 bm-a (r572; bands "
      "bitwise == this machine's yielded W77 draft -- r530 family "
      f"cross-validation), candidate W78 not local, bm-c rows={len(bmc_rows)}")

# --- leg 0b: W77 row W78+ WARNING projection prose (soft, W71 precedent) -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
proj_a_in_canon = "199_004..201_003" in canon
proj_b_in_canon = "53_001..53_200" in canon
print(f"leg0b: W77 row W78+ projection prose present: A={proj_a_in_canon} "
      f"B={proj_b_in_canon} (soft check, W71 precedent -- this gate "
      "re-derives from the live registry, never trusts prose "
      "-- r335/r535/r302)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[77]["a"][1] + 1, N1_BANDS[77]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[77]["b_exit"][1] + 1,
           N1_BANDS[77]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (199_004, 201_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (52_801, 53_000), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts {a_hits} {a_band_hits} (W77 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero hits -- no skip)")
# leg1-B: arithmetic window REFUSED -- refusal facts identity (r494 law)
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [53_000], \
    f"leg1-B refusal facts drift: {b_hits} (expect exactly [53_000], " \
    "the SEED_REGISTRY j13v2_mill_ic1 upper-edge endpoint)"
assert not b_band_hits, f"leg1-B unexpected band hits {b_band_hits}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"[{','.join(str(x) for x in b_hits)}] -- forced skip (r307 W5 "
      "precedent family, upper-edge endpoint)")
# leg1-B2: chained window 53_001..53_200 REFUSED at mid point 53_100
# (SEED_REGISTRY j13v2_mill_ic2, bm-b J13V2 IC2 claim ac8a58490) --
# double-hit chain face (W63-B precedent family). NOTE: the W77 row's
# W78+ prose projection named 53_001..53_200 as first-clean -- it is
# stale vs the live registry (r535 law: machine derive is the only
# derive face; prose cross-checked, corrected, disclosed).
b2_hits = sorted(p for p in points if 53_001 <= p <= 53_200)
assert b2_hits == [53_100], \
    f"leg1-B2 refusal facts drift: {b2_hits} (expect exactly [53_100])"
print(f"leg1-B2 chained window 53_001..53_200 REFUSED "
      f"[{','.join(str(x) for x in b2_hits)}] -- double-hit chain face "
      "(W63 family; W77-row prose projection stale vs live registry)")

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
assert first_a == W78_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W78_A}"
# chained window-step scan (W63 double-hit family): 52_801..53_000 hit
# at edge 53_000 -> chain window 53_001..53_200 hit mid at 53_100
# (leg1-B2) -> chain window 53_201..53_400 CLEAN == candidate.
b2_probe = clean(53_001, WIDTH_B)
assert b2_probe is None, \
    f"leg2-B failed: chained window 53_001..53_200 must be refused (got {b2_probe})"
chain_b = clean(53_201, WIDTH_B)
assert chain_b == W78_B, \
    f"leg2-B failed: chained first-clean window {chain_b} != candidate {W78_B}"
# FORK DISCLOSURE (r566 W63/W68 divergence face, F-20261002-03 pin
# pending): the past-hit-restart reading (lo=max(hits)+1, iterated)
# gives 53_101..53_300 -- also machine-clean, disclosed NOT taken; the
# double-hit chain family takes the chained full-window-step reading
# (W63-B in-register precedent).
fork_b = clean(53_101, WIDTH_B)
assert fork_b == (53_101, 53_300), \
    f"fork face drift: past-hit restart reading {fork_b} != (53_101, 53_300)"
print(f"leg2: A first-clean == arithmetic == candidate {W78_A[0]}..{W78_A[1]}; "
      f"B chained double-hit first-clean == candidate {W78_B[0]}..{W78_B[1]} "
      f"(A arithmetic continuation zero skip; B chained skip, W63 family; "
      f"fork 53_101..53_300 disclosed not taken)")
assert not overlaps(W78_A, W78_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W78_A), ("B", W78_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W78-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W78-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W78-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W78-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W78-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W78-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W78-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W78-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W78 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "78: {\"a\": (199_004" not in out, \
    "leg3 failed: a W78 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "N1 \u6ce278\uff08" not in out, "leg3 failed: canon W78 row exists on origin"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W78"' not in outn1, \
    "leg3 failed: a W78 WAVE_CONFIGS entry ALREADY exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W78 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W78 ADMIT: A {W78_A[0]}..{W78_A[1]} (arithmetic continuation zero skip) "
      f"+ B {W78_B[0]}..{W78_B[1]} (chained double-hit skip past 53_000+53_100, "
      f"W63 family, fork 53_101..53_300 disclosed not taken) "
      f"-- clean vs 75 registered rows + N3-R1 used-seed band + "
      f"probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-c (r565 second yield-then-reoccupy after the "
      f"W76 yield to bm-b r572 and the W77 yield to bm-a r572 per r511 "
      f"commit-order; seat published=reserved PUSHED to origin "
      f"MSG-20261002-1150-bmc before this freeze).")

# --- W79+ projection (warning text for the law table row) --------------------
w79_a = (W78_A[1] + 1, W78_A[1] + WIDTH_A)
w79_b = (W78_B[1] + 1, W78_B[1] + WIDTH_B)
a_hits79 = sorted(p for p in points if w79_a[0] <= p <= w79_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w79_a)]
b_hits79 = sorted(p for p in points if w79_b[0] <= p <= w79_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w79_b)]
print(f"W79+ projection: A arithmetic +2_000 = {w79_a[0]}..{w79_a[1]} "
      f"-> {'CLEAN (verify at W79 prereg)' if not a_hits79 else 'REFUSED ' + str(a_hits79)}; "
      f"B +200 from W78 end = {w79_b[0]}..{w79_b[1]} "
      f"-> {'CLEAN (verify at W79 prereg)' if not b_hits79 else 'REFUSED ' + str(b_hits79)}")
