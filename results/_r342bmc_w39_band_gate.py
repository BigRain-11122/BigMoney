"""W39 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W39 = TWENTY-EIGHTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's NINTH owned wave after W14/W17/W20/W23/W26/
W29/W32/W37). FREEZE AUTHORITY = never-dry supply law standing step +
CEO DE-THROTTLE ORDER O-20261001-2355 sec.2 own-continuous-series:
bm-c's previous wave W37 closed FULL-LIFECYCLE the same window
(r341-r342: freeze -> 12/12 burn -> finalize one-pass K=79,320, ledger
443,940 chain-linear) -> zero-gap relay, wave number 39 = FIRST FREE
NUMBER after W38's landed claim (bm-b r529, 01:01:00).

The W38 row's W39+ WARNING projects A arithmetic CLEAN (121_004..123_003)
and B arithmetic REFUSED (42_801..43_000, tail point 43_000 =
SEED_REGISTRY p4_folk). r335 lesson (projections can carry scanning-
universe blind spots) + r535 law (clean-projection claims must be
machine-derived, never prose-copied): this gate re-derives from the live
registry, never trusts the prose. The B-side skip is FORCED (r307
wave-band tail law precedent W26/W30): the refusal facts are machine-
proven, the first clean window is machine-derived.

Machine-verified against: all registered N1 wave bands W2..W38 (36
rows, W35/W36/W37/W38 included), the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 bm-a mandatory leg), the runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg --
mandatory on every gate receipt from W26 on), v1 in-use + W1 ext
bands, SEED_REGISTRY live values (incl. bm-a r547 lowamp_p3 three new
rows), N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r342 bm-c freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W39_A = (121_004, 123_003)              # law sec.4 W39 row (arithmetic, no skip)
W39_B = (43_001, 43_200)                # FORCED SKIP past p4_folk=43_000

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

# --- reserved universe (W39 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 39:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (36 pre-W39 rows + the candidate) ------------------
assert 37 in N1_BANDS and N1_BANDS[37]["engine_owner"] == "bm-c", \
    "leg0 failed: W37 (bm-c) rows must be present (r341 freeze, finalize " \
    "landed r342 same-window closeout)"
assert 38 in N1_BANDS and N1_BANDS[38]["engine_owner"] == "bm-b", \
    "leg0 failed: W38 (bm-b) rows must be present (r529 freeze, burned " \
    "12/12 + finalize pending)"
pre_w39 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39]
assert sorted(N1_BANDS) == pre_w39, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"36 registered rows + the W39 candidate)"

# --- leg 0b: W38 row's W39+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "121_004..123_003" in canon and "42_801..43_000" in canon, \
    "leg0b failed: W38 row W39+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W38 row W39+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[38]["a"][1] + 1, N1_BANDS[38]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[38]["b_exit"][1] + 1,
           N1_BANDS[38]["b_exit"][1] + WIDTH_B)
# A tail projected CLEAN by the W38 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W38 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W38 "
      f"projection verified machine-side)")
# B tail projected REFUSED by the W38 row -- the refusal facts must be
# exactly the registry tail point p4_folk=43_000 (forced-skip proof,
# r307 wave-band tail law: skip is FORCED, never a free pick).
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [43_000], \
    f"leg1-B failed: expected forced refusal [43_000] (p4_folk tail " \
    f"point), got {b_hits}"
assert science_gates.SEED_REGISTRY.get("p4_folk") == 43_000, \
    "leg1-B failed: p4_folk refusal fact identity drift"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED by "
      f"{b_hits} (SEED_REGISTRY p4_folk tail point -- forced skip per "
      f"r307 wave-band tail law, refusal facts machine-proven)")

# --- leg 2: first clean window (A == arithmetic; B == machine-derived skip) --
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
assert first_a == W39_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W39_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = None
for lo in range(ARITH_B[0], ARITH_B[0] + 20 * WIDTH_B):
    first_b = clean(lo, WIDTH_B, extra=(W39_A,))
    if first_b is not None:
        break
assert first_b == W39_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W39_B} (forced-skip window must be DERIVED, never " \
    "prose-copied -- r307/r535)"
assert W39_B[0] == 43_000 + 1, \
    "leg2-B failed: skip must land immediately past the refusal point"
print(f"leg2-B machine-derived first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (forced skip past 43_000, derived not picked)")
assert not overlaps(W39_A, W39_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W39_A), ("B", W39_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 39:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W39-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W39-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W39-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W39-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W39-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W39-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W39-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W39-{tag} (r335 leg)")
# canon cross-check: the landed W39 row must equal the derived candidate
assert N1_BANDS[39]["a"] == W39_A and N1_BANDS[39]["b_exit"] == W39_B, \
    "leg3 failed: canon W39 row drift vs derived candidate"
assert N1_BANDS[39]["engine_owner"] == "bm-c", "leg3 failed: W39 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "39: {\"a\": (121_004" not in out, \
    "leg3 failed: a W39 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W39 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W39 ADMIT: A {W39_A[0]}..{W39_A[1]} (arithmetic continuation, no "
      f"skip) + B {W39_B[0]}..{W39_B[1]} (FORCED SKIP past "
      f"SEED_REGISTRY p4_folk=43_000, first clean window machine-derived "
      f"per r307 wave-band tail law) both clean vs 36 registered rows + "
      f"N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-c (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; zero-gap relay after the W37 "
      f"full closeout same window r342; origin slot vacancy machine-"
      f"checked).")

# --- W40+ projection (warning text for the law table row) --------------------
w40_a = (W39_A[1] + 1, W39_A[1] + WIDTH_A)
w40_b = (W39_B[1] + 1, W39_B[1] + WIDTH_B)
a_hits40 = sorted(p for p in points if w40_a[0] <= p <= w40_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w40_a)]
b_hits40 = sorted(p for p in points if w40_b[0] <= p <= w40_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w40_b)]
print(f"W40+ projection: A arithmetic +2_000 = {w40_a[0]}..{w40_a[1]} "
      f"-> {'CLEAN (verify at W40 prereg)' if not a_hits40 else 'REFUSED ' + str(a_hits40)}; "
      f"B +200 from W39 end = {w40_b[0]}..{w40_b[1]} "
      f"-> {'CLEAN (verify at W40 prereg)' if not b_hits40 else 'REFUSED ' + str(b_hits40)}")
