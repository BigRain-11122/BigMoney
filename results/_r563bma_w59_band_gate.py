"""W59 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W59 = FORTY-EIGHTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- next bm-a owned wave after the registered W57 row,
own-series continuation). FREEZE AUTHORITY = never-dry supply law
standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2
own-continuous-series. Wave number 59 = FIRST FREE NUMBER after the
registered W58 row (origin slot vacancy machine-checked at leg3);
chain state at this freeze: W1..W57 finalizes ALL LANDED (ledger head
489,948, W57 K=123,320 bm-a r562 same-window closeout) and W58
REGISTERED with finalize NOT landed = ONE in-flight upstream seat
(bm-c engine burning 10/12 shards on origin at the freeze window).

The W58 row's W59+ WARNING projects: A +2_000 arithmetic
(161_004..163_003) CLEAN and B +200 arithmetic (47_801..48_000)
REFUSED [48_000 SEED_REGISTRY point]. r335 lesson + r535 law: this
gate re-derives from the live registry, never trusts the prose; the
B-side skip forcedness is machine-proven per r518 (refusal facts at
the arithmetic position are mandatory red).

Machine-verified against: all registered N1 wave bands W2..W58 (56
rows, incl. W58 bm-c r354 freeze with finalize in-flight), the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r563 bm-a freeze-window run (never-dry standing step, O-20261001-2355
sec.2 own-series).
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
W59_A = (161_004, 163_003)              # law sec.4 W59 row (arithmetic, no skip)
W59_B = (48_001, 48_200)                # forced skip past SEED_REGISTRY 48_000

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

# --- reserved universe (W59 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 59:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (56 pre-W59 rows + the candidate) -----------------
assert 58 in N1_BANDS and N1_BANDS[58]["engine_owner"] == "bm-c", \
    "leg0 failed: W58 (bm-c) row must be present (r354 freeze; finalize " \
    "in-flight at this window = the ONE upstream seat disclosed in the " \
    "W59 prereg sec.0)"
assert 57 in N1_BANDS and N1_BANDS[57]["engine_owner"] == "bm-a", \
    "leg0 failed: W57 (bm-a) row must be present (r561 freeze; r562 " \
    "same-window full-lifecycle closeout K=123,320 ledger 489,948)"
assert 56 in N1_BANDS and N1_BANDS[56]["engine_owner"] == "bm-b", \
    "leg0 failed: W56 (bm-b) row must be present (finalize landed r561 " \
    "K=121,120 ledger 487,748)"
pre_w59 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
assert sorted(N1_BANDS) == pre_w59, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 56 " \
    f"registered rows + the W59 candidate)"

# --- leg 0b: W58 row's W59+ WARNING prose present in the canon law file ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "161_004..163_003" in canon and "47_801..48_000" in canon, \
    "leg0b failed: W58 row W59+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W58 row W59+ WARNING prose present (published projection "
      "basis; machine-derived per r535; the W59 window derived fresh "
      "this gate)")

# --- leg 1: arithmetic positions DERIVED FROM THE REGISTRY (not prose) ------
ARITH_A = (N1_BANDS[58]["a"][1] + 1, N1_BANDS[58]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[58]["b_exit"][1] + 1,
           N1_BANDS[58]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W58 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W58 "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [48_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (W58 row projected " \
    f"REFUSED at exactly the SEED_REGISTRY point 48_000 = " \
    f"p1d_gdhs_quarterly + p4_pairs; r518 forcedness)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"exactly at [48_000] (SEED_REGISTRY p1d_gdhs_quarterly + "
      f"p4_pairs; refusal facts machine-proven per r518 -- the skip is "
      f"forced, not a free pick)")

# --- leg 2: first clean windows (A == arithmetic; B = first clean past the
#     refused arithmetic tail, machine-scanned) -------------------------------
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

def first_clean(lo, width):
    for cand_lo in range(lo, lo + 10 * width):
        w = clean(cand_lo, width)
        if w is not None:
            return w
    return None

first_a = clean(ARITH_A[0], WIDTH_A)
assert first_a == W59_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W59_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = first_clean(ARITH_B[0], WIDTH_B)
assert first_b == W59_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W59_B} " \
    "(skip forced past 48_000; R250/r518 machine-derived)"
assert W59_B[0] > ARITH_B[0], \
    "leg2-B failed: B must skip past the refused arithmetic tail (r518)"
assert W59_B[0] == 48_001 == ARITH_B[1] + 1, \
    "leg2-B failed: B must sit at the FIRST clean window past the refused " \
    "tail (48_000 + 1; r535 machine-derive)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} == "
      f"arithmetic (no skip); B {first_b[0]}..{first_b[1]} = first clean "
      f"window machine-scanned past the refused tail (skip forced per "
      f"r518, W39-B/W43-B/W47-B skip-family precedent)")
assert not overlaps(W59_A, W59_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W59_A), ("B", W59_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 59:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W59-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W59-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W59-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W59-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W59-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W59-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W59-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W59-{tag} (r335 leg)")
# canon cross-check: the landed W59 row must equal the derived candidate
assert N1_BANDS[59]["a"] == W59_A and N1_BANDS[59]["b_exit"] == W59_B, \
    "leg3 failed: canon W59 row drift vs derived candidate"
assert N1_BANDS[59]["engine_owner"] == "bm-a", "leg3 failed: W59 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "59: {\"a\": (161_004" not in out, \
    "leg3 failed: a W59 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W59 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W59 ADMIT: A {W59_A[0]}..{W59_A[1]} (arithmetic continuation from "
      f"the W58 tail, no skip) + B {W59_B[0]}..{W59_B[1]} (FORCED SKIP "
      f"past SEED_REGISTRY 48_000 = p1d_gdhs_quarterly + p4_pairs, first "
      f"clean window machine-scanned per r518/r535) both clean vs 56 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-a "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"W1..W57 finalizes ALL LANDED ledger head 489,948; W58 = ONE "
      f"in-flight upstream seat; origin slot vacancy machine-checked).")

# --- W60+ projection (warning text for the law table row) --------------------
w60_a = (W59_A[1] + 1, W59_A[1] + WIDTH_A)
w60_b = (W59_B[1] + 1, W59_B[1] + WIDTH_B)
a_hits60 = sorted(p for p in points if w60_a[0] <= p <= w60_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w60_a)]
b_hits60 = sorted(p for p in points if w60_b[0] <= p <= w60_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w60_b)]
print(f"W60+ projection: A arithmetic +2_000 = {w60_a[0]}..{w60_a[1]} "
      f"-> {'CLEAN (verify at W60 prereg)' if not a_hits60 else 'REFUSED ' + str(a_hits60)}; "
      f"B +200 from W59 end = {w60_b[0]}..{w60_b[1]} "
      f"-> {'CLEAN (verify at W60 prereg)' if not b_hits60 else 'REFUSED ' + str(b_hits60)}")
