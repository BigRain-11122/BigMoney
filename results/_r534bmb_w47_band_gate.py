"""W47 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W47 = THIRTY-SEVENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's FOURTEENTH owned wave after W10/W11/W13/W16/
W19/W22/W25/W28/W31/W34/W36/W38/W40; the dead r533 session's W42/W44
same-number drafts YIELDED to bm-c r345 / bm-a r553 canonical freezes --
identical bands, r530 deterministic law, r511 commit-order yield; zero
science pollution disclosed in MSG-20261002-0530). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series: bm-b's TICK engine queue
is EMPTY (W40 closed r532: freeze -> 12/12 burn -> finalize one-pass
K=85,920, ledger 450,540; W41..W46 closed by bm-c/bm-a; the LOWAMP-P3
family closed judged-negative r533). Wave 47 = FIRST FREE NUMBER after
W46's landed claim (bm-c r348 same-window full closeout, K=99,120,
ledger 465,748 on origin).

r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W47 slot vacant on origin (no N1_BANDS 47 row, no canon
wave-47 row; machine-checked at leg3).

UPSTREAM: FULLY CAUGHT UP at this freeze -- W45 (bm-a r554, K=96,920,
ledger 463,548) and W46 (bm-c r348, K=99,120, ledger 465,748) BOTH
FINALIZED before this freeze. ZERO in-flight upstream faces (first
fully caught-up freeze window) -- W47 finalize chain-order prev
derives from the live origin head at run time (r518 origin-timing
law, no manual copying).

The W46 row's W47+ WARNING projects: A arithmetic 137_004..139_003
CLEAN; B arithmetic 44_801..45_000 REFUSED at SEED_REGISTRY
pc_l2_ic=45_000 (W39-B/W43-B forced-skip family) -> scan-forward
first clean window. r335 lesson (projections can carry scanning-
universe blind spots) + r535 law (clean-projection claims must be
machine-derived, never prose-copied): this gate re-derives from the
live registry, never trusts the prose. A = NO-SKIP arithmetic
continuation; B = FORCED SKIP (not a free pick -- R250 discipline
intact: W47 bands were never assigned).

Machine-verified against: all registered N1 wave bands W2..W46 (44
rows, W42/W43/W44/W45/W46 included), the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 bm-a mandatory leg), the runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg --
mandatory on every gate receipt from W26 on), v1-in-use + W1 ext
bands, SEED_REGISTRY live values, N2/N4 design-probe points
(40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r534 bm-b freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W47_A = (137_004, 139_003)             # law sec.4 W47 row (arithmetic, no skip)
W47_B = (45_001, 45_200)               # FORCED SKIP past pc_l2_ic=45_000
                                        # (W46 row W47+ WARNING projects
                                        # REFUSED at 45_000 -- skip family)

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

# --- reserved universe (W47 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 47:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (44 pre-W47 rows + the candidate) -----------------
assert 46 in N1_BANDS and N1_BANDS[46]["engine_owner"] == "bm-c", \
    "leg0 failed: W46 (bm-c) row must be present (r348 freeze; finalize " \
    "landed same-window K=99,120 ledger 465,748 -- FULLY CAUGHT UP)"
assert 45 in N1_BANDS and N1_BANDS[45]["engine_owner"] == "bm-a", \
    "leg0 failed: W45 (bm-a) row must be present (r554 freeze; finalize " \
    "landed K=96,920 ledger 463,548)"
assert 44 in N1_BANDS and N1_BANDS[44]["engine_owner"] == "bm-a", \
    "leg0 failed: W44 (bm-a) rows must be present (r553 freeze; finalize " \
    "landed same-window r554 K=94,720 ledger 459,340)"
assert 43 in N1_BANDS and N1_BANDS[43]["engine_owner"] == "bm-c", \
    "leg0 failed: W43 (bm-c) rows must be present (r346 freeze; finalize " \
    "landed K=92,520 ledger 457,140)"
assert 42 in N1_BANDS and N1_BANDS[42]["engine_owner"] == "bm-c", \
    "leg0 failed: W42 (bm-c) rows must be present (r345 freeze; finalize " \
    "landed K=90,320 ledger 454,940)"
pre_w47 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
assert sorted(N1_BANDS) == pre_w47, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"44 registered rows + the W47 candidate)"

# --- leg 0b: W46 row's W47+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "137_004..139_003" in canon and "44_801..45_000" in canon, \
    "leg0b failed: W46 row W47+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W46 row W47+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[46]["a"][1] + 1, N1_BANDS[46]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[46]["b_exit"][1] + 1,
           N1_BANDS[46]["b_exit"][1] + WIDTH_B)
# A tail projected CLEAN by the W46 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W46 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W46 "
      f"projection verified machine-side)")
# B tail projected REFUSED by the W46 row (45_000 = pc_l2_ic) --
# capture the refusal facts and assert their identity (skip is
# FORCED, not a free pick; W39-B/W43-B family):
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [45_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (W46 row projected " \
    f"REFUSED at [45000] -- machine refusal must match the projection " \
    f"exactly, r307 tail law)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"refusal facts {b_hits} == [45_000] (SEED_REGISTRY pc_l2_ic "
      f"hit -- FORCED skip, W39-B/W43-B skip family, projection "
      f"verified machine-side)")

# --- leg 2: first clean window (A == arithmetic; B == scan-forward) ---------
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
assert first_a == W47_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W47_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# B: arithmetic position REFUSED (45_000) -- scan forward past every
# offending point (r307 tail law) until clean:
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
assert first_b == W47_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W47_B} (machine-derived, not picked -- r307/r535)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (forced scan-forward past 45_000, W26-A/W39-B/"
      f"W43-B skip family)")
assert not overlaps(W47_A, W47_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W47_A), ("B", W47_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 47:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W47-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W47-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W47-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W47-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W47-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W47-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W47-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W47-{tag} (r335 leg)")
# canon cross-check: the landed W47 row must equal the derived candidate
assert N1_BANDS[47]["a"] == W47_A and N1_BANDS[47]["b_exit"] == W47_B, \
    "leg3 failed: canon W47 row drift vs derived candidate"
assert N1_BANDS[47]["engine_owner"] == "bm-b", "leg3 failed: W47 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "47: {\"a\": (137_004" not in out, \
    "leg3 failed: a W47 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W47 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W47 ADMIT: A {W47_A[0]}..{W47_A[1]} (arithmetic continuation, no "
      f"skip) + B {W47_B[0]}..{W47_B[1]} (forced scan-forward past "
      f"pc_l2_ic=45_000, W39-B/W43-B skip family) both clean vs 44 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-b "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"zero-gap relay after the fleet chain catch-up: W45/W46 both "
      f"finalized, ZERO in-flight upstream faces -- first fully "
      f"caught-up freeze window; origin slot vacancy machine-checked).")

# --- W48+ projection (warning text for the law table row) --------------------
w48_a = (W47_A[1] + 1, W47_A[1] + WIDTH_A)
w48_b = (W47_B[1] + 1, W47_B[1] + WIDTH_B)
a_hits48 = sorted(p for p in points if w48_a[0] <= p <= w48_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w48_a)]
b_hits48 = sorted(p for p in points if w48_b[0] <= p <= w48_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w48_b)]
print(f"W48+ projection: A arithmetic +2_000 = {w48_a[0]}..{w48_a[1]} "
      f"-> {'CLEAN (verify at W48 prereg)' if not a_hits48 else 'REFUSED ' + str(a_hits48)}; "
      f"B +200 from W47 end = {w48_b[0]}..{w48_b[1]} "
      f"-> {'CLEAN (verify at W48 prereg)' if not b_hits48 else 'REFUSED ' + str(b_hits48)}")
