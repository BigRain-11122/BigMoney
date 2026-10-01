"""W40 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W40 = TWENTY-NINTH ENGINE-OWNED WAVE, bm-a's NINTH owned wave after
W12/W18/W21/W24/W27/W30/W33/W35 -- the SECOND bm-a wave under the engine
de-throttle law O-20261001-2355 sec.2 (per-machine self-owned continuous
series: the machine's previous wave W35 closed (finalize landed bm-a r546,
K=74,920) -> zero-gap relay to the next wave; seat system retired by the
same order; wave number 40 = first free number after W39's published claim
(bm-c r342 row landed = number occupied)).

Candidate = pure arithmetic continuation of the REGISTERED W39 row on
both sides, no skip face this wave:
    A 123_004..125_003 (== W39 A end 123_003 + 1, width 2,000 verbatim)
    B  43_201..43_400 (== W39 B end  43_200 + 1, width   200 verbatim)
The W39 row's W40+ WARNING published exactly these windows as CLEAN per
the r342 bm-c gate receipt -- this gate re-derives them from the registry
(NOT prose-copied, r535 law) and machine-proves them ADMIT against the
full reserved universe.

Machine-verified against: all registered N1 wave bands W2..W39 (37 rows,
no 15 -- W36 bm-b, W37 bm-c, W38 bm-b, W39 bm-c all registered), the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg), the
runner design-probe seed cluster 95_000..95_003 (r335 discovery leg --
mandatory on every gate receipt from W26 on), v1 in-use + W1 ext bands,
SEED_REGISTRY live values (incl. the bm-a r547 lowamp_p3 three new rows),
N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe points
(31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049), plus the origin tail-emptiness
machine check (no W40 row / no W40 prereg on origin/main, r342 leg).

r548 bm-a freeze-window run. Freeze trigger = engine de-throttle law
O-20261001-2355 sec.2 (cores idle with engine alive = red flag; own
continuous series materializes immediately) + never-dry supply law
standing step (board negative; W35 closed same machine r546; LOWAMP-P3
pool line burning in parallel via autofill).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W40_A = (123_004, 125_003)              # arithmetic: W39 A end + 1
W40_B = (43_201, 43_400)                # arithmetic: W39 B end + 1

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) ----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) -------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)      # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W40 itself EXCLUDED -- it is the candidate) --------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 40:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (37 pre-W40 rows + the candidate) ---------------
assert 38 in N1_BANDS and N1_BANDS[38]["engine_owner"] == "bm-b", \
    "leg0 failed: W38 (bm-b) row must be present (r529 freeze, finalized)"
assert 39 in N1_BANDS and N1_BANDS[39]["engine_owner"] == "bm-c", \
    "leg0 failed: W39 (bm-c) row must be present (r342 freeze)"
pre_w40 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40]
assert sorted(N1_BANDS) == pre_w40, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 38 " \
    f"registered rows + the W40 candidate, no 15, no 41)"

# --- leg 0b: W39 row's W40+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "123_004..125_003" in canon and "43_201..43_400" in canon, \
    "leg0b failed: W39 row W40+ WARNING (published projection) prose " \
    "not found in the canon file -- the published-projection basis " \
    "(r535 machine-derived gate receipt, not prose-copy) must be " \
    "canon-visible"
print("leg0b W39 row W40+ WARNING prose present (published projection "
      "CLEAN per the r342 bm-c gate receipt; re-derived here from the "
      "registry, not prose-copied)")

# --- leg 0c: origin tail-emptiness machine check (r342 leg) ----------------
subprocess.run(["git", "-C", ROOT, "fetch", "origin"],
               capture_output=True)
origin_canon = subprocess.run(
    ["git", "-C", ROOT, "show", "origin/main:research/PERPETUAL_FACES.md"],
    capture_output=True).stdout.decode("utf-8", "replace")
assert "- N1 \u6ce240" not in origin_canon and "N1 \u6ce240\uff08" not in origin_canon, \
    "leg0c failed: W40 row already on origin -- collision with another " \
    "machine's freeze (r239/r511 collision law: yield to the earlier " \
    "commit)"
origin_prereg = subprocess.run(
    ["git", "-C", ROOT, "show",
     "origin/main:research/PERPETUAL_N1_W40_PREREG.md"],
    capture_output=True)
assert origin_prereg.returncode != 0, \
    "leg0c failed: W40 prereg already on origin (occupied number)"
print("leg0c origin tail-emptiness: no W40 canon row, no W40 prereg on "
      "origin/main -> number 40 clean (r511 tail-lock law)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) ------
ARITH_A = (N1_BANDS[39]["a"][1] + 1, N1_BANDS[39]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[39]["b_exit"][1] + 1,
           N1_BANDS[39]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W40_A and ARITH_B == W40_B, \
    "leg1 failed: arithmetic window != candidate (skip would need " \
    "refusal facts -- none this wave, free choice forbidden R250)"
print(f"leg1 arithmetic windows A {ARITH_A[0]}..{ARITH_A[1]} / B "
      f"{ARITH_B[0]}..{ARITH_B[1]} == candidates (zero skip; W39 "
      f"registered-row tails + 1, step widths verbatim)")

# --- leg 2: first clean window AT the arithmetic position == candidate -----
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
assert first_a == W40_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W40_A} " \
    f"(arithmetic position is dirty -- skip must be machine-proven)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=[W40_A])
assert first_b == W40_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W40_B} " \
    f"(no further skip expected; own A band reserved per W6 law)"
assert not overlaps(W40_A, W40_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ---------------
conflicts = []
for tag, band in (("A", W40_A), ("B", W40_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 40:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W40-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W40-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W40-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W40-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W40-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W40-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W40-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W40-{tag} (r335 leg)")
# canon cross-check: the landed W40 row must equal the derived candidate
assert N1_BANDS[40]["a"] == W40_A and N1_BANDS[40]["b_exit"] == W40_B, \
    "leg3 failed: canon W40 row drift vs derived candidate"
assert N1_BANDS[40]["engine_owner"] == "bm-a", "leg3 failed: W40 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W40 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W40 ADMIT: A {W40_A[0]}..{W40_A[1]} + B {W40_B[0]}..{W40_B[1]} both "
      f"clean vs 38 registered rows (incl. W36 bm-b / W37 bm-c / W38 bm-b "
      f"finalized + W39 bm-c in-flight = registered in-use face, r531 "
      f"disjoint coexistence) + N3-R1 used-seed band + probe-seed cluster "
      f"+ registry values + probes/actuals -- engine_owner=bm-a (de-throttle "
      f"law O-20261001-2355 sec.2 own-continuous-series, zero-gap relay "
      f"after W35 close; wave 40 = first free number after W39's claim; "
      f"zero skip both sides, machine-proven).")

# --- W41+ projection (warning text for the law table row) -------------------
w41_a = (W40_A[1] + 1, W40_A[1] + WIDTH_A)
w41_b = (W40_B[1] + 1, W40_B[1] + WIDTH_B)
a_hits41 = sorted(p for p in points if w41_a[0] <= p <= w41_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w41_a)]
b_hits41 = sorted(p for p in points if w41_b[0] <= p <= w41_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w41_b)]
print(f"W41+ projection: A +2_000 = {w41_a[0]}..{w41_a[1]} "
      f"-> {'CLEAN (verify at W41 prereg)' if not a_hits41 else 'REFUSED ' + str(a_hits41)}; "
      f"B +200 from W40 end = {w41_b[0]}..{w41_b[1]} "
      f"-> {'CLEAN (verify at W41 prereg)' if not b_hits41 else 'REFUSED ' + str(b_hits41)}")
