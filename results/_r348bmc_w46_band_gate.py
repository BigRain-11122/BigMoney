"""W46 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W46 = THIRTY-SIXTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's FOURTEENTH owned wave after W14/W17/W20/W23/
W26/W29/W32/W37/W39/W41/W42/W43; the W44 same-number draft YIELDED to
bm-a's r553 canonical freeze -- identical bands, r530 deterministic law,
r511 commit-order yield). FREEZE AUTHORITY = never-dry supply law standing
step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2 own-continuous-series:
bm-c's RESIDENT engine queue is EMPTY (W43 closed same-window r346:
freeze b3411b7c9 -> 12/12 no-restart burn -> finalize one-pass K=92,520,
ledger 457,140; W44 draft yielded; W45 = bm-a-owned per the r554 freeze,
not claimable by the bm-c engine per the cmd_supply owner skip gate).
Wave 46 = FIRST FREE NUMBER after W45's landed claim (bm-a r554 freeze
03:59:59 on origin).

r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W46 slot vacant on origin (no N1_BANDS 46 row, no canon
wave-46 row; machine-checked at leg3 + the vacancy tool).

UPSTREAM W45 IN FLIGHT at this freeze (W7/W10/W12 in-flight dep
precedent, r307 two-state law): bm-a's W45 burn runs on their tick
engine, finalize NOT yet landed; W46 finalize chain-order is
FAIL-CLOSED on the W45 output at run time. W46's OWN burn has zero
dependency on W45 (bands disjoint, both tails arithmetic continuations).

The W45 row's W46+ WARNING projects BOTH SIDES CLEAN:
A arithmetic 135_004..137_003 / B arithmetic 44_601..44_800.
r335 lesson (projections can carry scanning-universe blind spots) +
r535 law (clean-projection claims must be machine-derived, never
prose-copied): this gate re-derives from the live registry, never
trusts the prose. Both sides are expected NO-SKIP arithmetic
continuations (R250 no-repick discipline intact: W46 bands were
never assigned).

Machine-verified against: all registered N1 wave bands W2..W45 (43
rows, W42/W43/W44/W45 included), the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 bm-a mandatory leg), the runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg --
mandatory on every gate receipt from W26 on), v1-in-use + W1 ext
bands, SEED_REGISTRY live values, N2/N4 design-probe points
(40_000/40_001), N2-W15 draft probe points (31_000/31_500/32_000),
lfc actual draw (30_000..30_099) AND options_wave2 actual draw
(63_000..63_049).

r348 bm-c freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W46_A = (135_004, 137_003)             # law sec.4 W46 row (arithmetic, no skip)
W46_B = (44_601, 44_800)               # arithmetic continuation, no skip
                                        # (W45 row W46+ WARNING projects CLEAN)

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

# --- reserved universe (W46 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 46:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (43 pre-W46 rows + the candidate) ------------------
assert 45 in N1_BANDS and N1_BANDS[45]["engine_owner"] == "bm-a", \
    "leg0 failed: W45 (bm-a) row must be present (r554 freeze 03:59:59; " \
    "finalize IN FLIGHT at this freeze -- burn on the bm-a tick engine; " \
    "W46 finalize chain-order FAIL-CLOSED on the W45 output at run time)"
assert 44 in N1_BANDS and N1_BANDS[44]["engine_owner"] == "bm-a", \
    "leg0 failed: W44 (bm-a) rows must be present (r553 freeze; finalize " \
    "landed same-window r554 K=94,720 ledger 459,340)"
assert 43 in N1_BANDS and N1_BANDS[43]["engine_owner"] == "bm-c", \
    "leg0 failed: W43 (bm-c) rows must be present (r346 freeze; finalize " \
    "landed K=92,520 ledger 457,140)"
assert 42 in N1_BANDS and N1_BANDS[42]["engine_owner"] == "bm-c", \
    "leg0 failed: W42 (bm-c) rows must be present (r345 freeze; finalize " \
    "landed K=90,320 ledger 454,940)"
pre_w46 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
assert sorted(N1_BANDS) == pre_w46, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"43 registered rows + the W46 candidate)"

# --- leg 0b: W45 row's W46+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "135_004..137_003" in canon and "44_601..44_800" in canon, \
    "leg0b failed: W45 row W46+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W45 row W46+ WARNING prose present (published projection "
      "= first-free-number projection basis; machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[45]["a"][1] + 1, N1_BANDS[45]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[45]["b_exit"][1] + 1,
           N1_BANDS[45]["b_exit"][1] + WIDTH_B)
# A tail projected CLEAN by the W45 row -- verify machine-side:
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W45 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W45 "
      f"projection verified machine-side)")
# B tail projected CLEAN by the W45 row -- verify machine-side:
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W45 row projected " \
    f"CLEAN but arithmetic window is dirty machine-side -- projection " \
    f"drift, re-derive before landing)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W45 "
      f"projection verified machine-side)")

# --- leg 2: first clean window (A == arithmetic; B == arithmetic) -----------
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
assert first_a == W46_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W46_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# B: arithmetic position expected CLEAN (no skip family) -- if dirty,
# scan forward past every offending point (r307 tail law) until clean:
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
assert first_b == W46_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W46_B} (machine-derived, not picked -- r307/r535)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (no-skip arithmetic continuation from W45 B end)")
assert not overlaps(W46_A, W46_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W46_A), ("B", W46_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 46:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W46-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W46-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W46-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W46-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W46-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W46-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W46-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W46-{tag} (r335 leg)")
# canon cross-check: the landed W46 row must equal the derived candidate
assert N1_BANDS[46]["a"] == W46_A and N1_BANDS[46]["b_exit"] == W46_B, \
    "leg3 failed: canon W46 row drift vs derived candidate"
assert N1_BANDS[46]["engine_owner"] == "bm-c", "leg3 failed: W46 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "46: {\"a\": (135_004" not in out, \
    "leg3 failed: a W46 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W46 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W46 ADMIT: A {W46_A[0]}..{W46_A[1]} (arithmetic continuation, no "
      f"skip) + B {W46_B[0]}..{W46_B[1]} (arithmetic continuation, no "
      f"skip) both clean vs 43 registered rows + N3-R1 used-seed band + "
      f"probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-c (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2; zero-gap relay after the W43 full closeout "
      f"r346 + W44 same-number draft yield r530/r511; upstream W45 "
      f"in-flight disclosed, W46 finalize FAIL-CLOSED on W45 output at "
      f"run time; origin slot vacancy machine-checked).")

# --- W47+ projection (warning text for the law table row) --------------------
w47_a = (W46_A[1] + 1, W46_A[1] + WIDTH_A)
w47_b = (W46_B[1] + 1, W46_B[1] + WIDTH_B)
a_hits47 = sorted(p for p in points if w47_a[0] <= p <= w47_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w47_a)]
b_hits47 = sorted(p for p in points if w47_b[0] <= p <= w47_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w47_b)]
print(f"W47+ projection: A arithmetic +2_000 = {w47_a[0]}..{w47_a[1]} "
      f"-> {'CLEAN (verify at W47 prereg)' if not a_hits47 else 'REFUSED ' + str(a_hits47)}; "
      f"B +200 from W46 end = {w47_b[0]}..{w47_b[1]} "
      f"-> {'CLEAN (verify at W47 prereg)' if not b_hits47 else 'REFUSED ' + str(b_hits47)}")
