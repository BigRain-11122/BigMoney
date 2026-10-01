"""W43 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W43 = THIRTY-THIRD ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's TWELFTH owned wave after W14/W17/W20/W23/
W26/W29/W32/W37/W39/W41/W42). FREEZE AUTHORITY = never-dry supply law
standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2
own-continuous-series: bm-c's previous wave W42 closed FULL-LIFECYCLE
in a single window by the r345 session (freeze -> 12/12 no-restart
burn -> finalize one-pass K=90,320, ledger 454,940 chain-linear,
products pushed to origin; r345 died before S7 bookkeeping, numbers
344/345 burned per r529 law, r346 resumes the series) -> zero-gap
relay, wave number 43 = FIRST FREE NUMBER after W42's landed claim.
The chain FULLY caught up at this freeze (W40 bm-b r532, W41 bm-c
r345, W42 bm-c r345 -- zero pending upstream face).

The W42 row's W43+ WARNING projects: A arithmetic CLEAN
(129_004..131_003) but B arithmetic (43_801..44_000) REFUSED --
SEED_REGISTRY p4_queue=44_000 tail point inside the window; W43-B
must machine-derive the first clean window (projected 44_001..44_200,
W39-B skip family). r335 lesson (projections can carry scanning-
universe blind spots) + r535 law (clean-projection claims must be
machine-derived, never prose-copied): this gate re-derives from the
live registry, never trusts the prose. The B skip is FORCED here --
leg1-B asserts the refusal facts (machine-proven, not a free choice,
R250 no-repick discipline intact: W43 bands were never assigned).

Machine-verified against: all registered N1 wave bands W2..W42 (40
rows, W40/W41/W42 included), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every gate
receipt from W26 on), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r346 bm-c freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W43_A = (129_004, 131_003)              # law sec.4 W43 row (arithmetic, no skip)
W43_B = (44_001, 44_200)                # machine-derived first clean window
                                        # (arithmetic 43_801..44_000 REFUSED)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)  # ext 95_000/95_001 + n1 95_002/95_003
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

# --- reserved universe (W43 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 43:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (40 pre-W43 rows + the candidate) ------------------
assert 42 in N1_BANDS and N1_BANDS[42]["engine_owner"] == "bm-c", \
    "leg0 failed: W42 (bm-c) rows must be present (r345 freeze; finalize " \
    "landed same-window K=90,320 ledger 454,940)"
assert 41 in N1_BANDS and N1_BANDS[41]["engine_owner"] == "bm-c", \
    "leg0 failed: W41 (bm-c) rows must be present (r344 freeze; finalize " \
    "landed r345 K=88,120 ledger 452,740)"
assert 40 in N1_BANDS and N1_BANDS[40]["engine_owner"] == "bm-b", \
    "leg0 failed: W40 (bm-b) rows must be present (r531 freeze; finalize " \
    "landed r532 K=85,920 ledger 450,540)"
pre_w43 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
assert sorted(N1_BANDS) == pre_w43, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"40 registered rows + the W43 candidate)"

# --- leg 0b: W42 row's W43+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "129_004..131_003" in canon and "44_001..44_200" in canon, \
    "leg0b failed: W42 row W43+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W42 row W43+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[42]["a"][1] + 1, N1_BANDS[42]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[42]["b_exit"][1] + 1,
           N1_BANDS[42]["b_exit"][1] + WIDTH_B)
# A tail projected CLEAN by the W42 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W42 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W42 "
      f"projection verified machine-side)")
# B tail projected REFUSED (SEED_REGISTRY p4_queue=44_000 tail point) --
# machine-prove the skip is FORCED (not a free choice, R250 discipline):
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits != [], \
    "leg1-B failed: W42 row projected REFUSED but arithmetic window is " \
    "CLEAN machine-side -- projection drift, re-derive before landing"
assert 44_000 in b_hits, \
    f"leg1-B failed: expected SEED_REGISTRY p4_queue=44_000 in refusal " \
    f"facts, got {b_hits} (W42 row W43+ WARNING identity drift)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED -- "
      f"refusal facts {b_hits} (skip FORCED machine-proven, W42 row "
      f"WARNING verified; not a free pick)")

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
assert first_a == W43_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W43_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# B: scan forward past every offending point (W26 A-skip / W39-B family
# precedent: next start = max offending point + 1) until a clean window:
start = ARITH_B[0]
first_b = None
for _ in range(200):
    win = clean(start, WIDTH_B)
    if win is not None:
        first_b = win
        break
    blockers = [p for p in points if start <= p <= start + WIDTH_B - 1]
    assert blockers, \
        f"leg2-B failed: window {start}.. unclean with no point blocker " \
        "(band overlap must not occur in the B ladder -- investigate)"
    start = max(blockers) + 1
assert first_b == W43_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W43_B} (forced-skip derivation, not picked -- r307/r535; " \
    f"W26 A-skip + W39-B skip family precedent)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (forced-skip derivation past 44_000, not picked)")
assert not overlaps(W43_A, W43_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W43_A), ("B", W43_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 43:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W43-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W43-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W43-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W43-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W43-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W43-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                          f"x W43-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W43-{tag} (r335 leg)")
# canon cross-check: the landed W43 row must equal the derived candidate
assert N1_BANDS[43]["a"] == W43_A and N1_BANDS[43]["b_exit"] == W43_B, \
    "leg3 failed: canon W43 row drift vs derived candidate"
assert N1_BANDS[43]["engine_owner"] == "bm-c", "leg3 failed: W43 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "43: {\"a\": (129_004" not in out, \
    "leg3 failed: a W43 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W43 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W43 ADMIT: A {W43_A[0]}..{W43_A[1]} (arithmetic continuation, no "
      f"skip) + B {W43_B[0]}..{W43_B[1]} (forced-skip first clean window "
      f"past refused 43_801..44_000 [44_000 registry tail point]) both "
      f"clean vs 40 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-c "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"zero-gap relay after the W42 full closeout r345; origin slot "
      f"vacancy machine-checked).")

# --- W44+ projection (warning text for the law table row) --------------------
w44_a = (W43_A[1] + 1, W43_A[1] + WIDTH_A)
w44_b = (W43_B[1] + 1, W43_B[1] + WIDTH_B)
a_hits44 = sorted(p for p in points if w44_a[0] <= p <= w44_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w44_a)]
b_hits44 = sorted(p for p in points if w44_b[0] <= p <= w44_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w44_b)]
print(f"W44+ projection: A arithmetic +2_000 = {w44_a[0]}..{w44_a[1]} "
      f"-> {'CLEAN (verify at W44 prereg)' if not a_hits44 else 'REFUSED ' + str(a_hits44)}; "
      f"B +200 from W43 end = {w44_b[0]}..{w44_b[1]} "
      f"-> {'CLEAN (verify at W44 prereg)' if not b_hits44 else 'REFUSED ' + str(b_hits44)}")
