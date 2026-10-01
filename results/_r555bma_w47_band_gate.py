"""W47 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W47 = THIRTY-SEVENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- bm-a's ELEVENTH owned wave after W12/W18/W21/W24/
W27/W30/W33/W35/W44/W45). FREEZE AUTHORITY = never-dry supply law standing
step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2 own-continuous-series:
bm-a's tick-architecture engine queue is EMPTY (queue_depth 0 at this
freeze window; the chain is FULLY caught up W1..W46: W45 bm-a r554
K=96,920 ledger 463,548; W46 bm-c r348 K=99,120 ledger 465,748 -- zero
pending upstream face), wave 47 = FIRST FREE NUMBER after W46's landed
claim.

r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W47 slot vacant on origin (no N1_BANDS 47 row, no canon
wave-47 row; machine-checked at leg3 + the vacancy tool).

The W46 row's W47+ WARNING projects: A arithmetic 137_004..139_003
CLEAN; B arithmetic 44_801..45_000 machine-REFUSED (SEED_REGISTRY
['pc_l2_ic'] = 45_000 falls inside -- W39-B/W43-B forced skip-over
family). r335 lesson (projections can carry scanning-universe blind
spots) + r535 law (clean-projection claims must be machine-derived,
never prose-copied): this gate re-derives from the live registry,
never trusts the prose. A = no-skip arithmetic continuation (R250
discipline intact: W47 bands were never assigned); B = r307 tail-law
scan-forward first clean window (NOT a free pick).

Machine-verified against: all registered N1 wave bands W2..W46 (44
rows, W44/W45/W46 included), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every gate
receipt from W26 on), v1 in-use + W1 ext bands, SEED_REGISTRY live
values (161 keys incl. pc_l2_ic=45_000 = the W47-B refusal fact),
N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe points
(31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r555 bm-a freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W47_A = (137_004, 139_003)             # law sec.4 W47 row (arithmetic, no skip)
W47_B = (45_001, 45_200)               # FORCED SKIP-OVER (r307 scan-forward)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) ---------
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

# --- reserved universe (W47 itself EXCLUDED -- it is the candidate) ---------
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

# --- leg 0: registry shape (44 pre-W47 rows + the candidate) ------------------
assert 46 in N1_BANDS and N1_BANDS[46]["engine_owner"] == "bm-c", \
    "leg0 failed: W46 (bm-c) rows must be present (r348 freeze; finalize " \
    "landed same-window K=99,120 ledger 465,748)"
assert 45 in N1_BANDS and N1_BANDS[45]["engine_owner"] == "bm-a", \
    "leg0 failed: W45 (bm-a) rows must be present (r554 freeze; finalize " \
    "landed K=96,920 ledger 463,548)"
assert 44 in N1_BANDS and N1_BANDS[44]["engine_owner"] == "bm-a", \
    "leg0 failed: W44 (bm-a) rows must be present (r553 freeze; finalize " \
    "landed K=94,720 ledger 459,340)"
pre_w47 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
assert sorted(N1_BANDS) == pre_w47, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the " \
    f"44 registered rows + the W47 candidate)"
print("leg0 registry shape OK: 44 pre-W47 rows (W15 vacant-by-design) "
      "+ W47 candidate registered")

# --- leg 0b: W46 row's W47+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "137_004..139_003" in canon and "44_801..45_000" in canon, \
    "leg0b failed: W46 row W47+ WARNING prose not found in the canon file"
assert "45_001..45_200" in canon, \
    "leg0b failed: W47 row (landed this freeze) must carry the B band prose"
print("leg0b W46 row W47+ WARNING prose + W47 row prose present "
      "(A projection CLEAN / B REFUSED disclosure in canon)")

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
# B tail projected REFUSED by the W46 row -- verify the refusal facts:
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [45_000], \
    f"leg1-B failed: expected refusal fact [45000] (SEED_REGISTRY " \
    f"['pc_l2_ic']), got {b_hits} -- refusal-facts drift, re-derive " \
    "before landing (r535 law)"
assert science_gates.SEED_REGISTRY.get("pc_l2_ic") == 45_000, \
    "leg1-B failed: refusal-fact attribution drift (pc_l2_ic != 45000)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED exactly on "
      f"{b_hits} (SEED_REGISTRY['pc_l2_ic'] -- W39-B/W43-B forced "
      f"skip-over family, refusal facts machine-proven)")

# --- leg 2: first clean window (A == arithmetic; B == scan-forward) -----------
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
# B: arithmetic position REFUSED (skip family) -- scan forward past every
# offending point (r307 tail law) until clean:
start = ARITH_B[0]
first_b = None
skips = 0
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
    skips += 1
assert first_b == W47_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W47_B} (machine-derived, not picked -- r307/r535)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"({skips} skip-over step(s) past the refusal point 45_000 -- "
      f"r307 scan-forward, not a free pick)")
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
assert N1_BANDS[47]["engine_owner"] == "bm-a", "leg3 failed: W47 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "47: {\"a\": (137_004" not in out, \
    "leg3 failed: a W47 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"
canon_origin = subprocess.check_output(
    ["git", "show", "origin/main:research/PERPETUAL_FACES.md"],
    encoding="utf-8")
assert "- N1 波47" not in canon_origin, \
    "leg3 failed: a W47 canon row ALREADY exists on origin (slot not " \
    "vacant -- r511 tail-lock violation, abort before push)"

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
      f"skip) + B {W47_B[0]}..{W47_B[1]} (FORCED SKIP-OVER past "
      f"SEED_REGISTRY['pc_l2_ic']=45_000, r307 scan-forward first clean "
      f"window -- W39-B/W43-B family) both clean vs 44 registered rows + "
      f"N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-a (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; zero-gap relay after the W46 "
      f"full closeout bm-c r348; origin slot vacancy machine-checked).")

# --- W48+ projection (warning text for the law table row) --------------------
proj_a = clean(W47_A[1] + 1, WIDTH_A)
proj_b = clean(W47_B[1] + 1, WIDTH_B)
print(f"W48+ projection: A +2_000 arithmetic {W47_A[1] + 1}.."
      f"{W47_A[1] + WIDTH_A} -> {'CLEAN' if proj_a else 'REFUSED'}; "
      f"B +200 arithmetic {W47_B[1] + 1}..{W47_B[1] + WIDTH_B} -> "
      f"{'CLEAN' if proj_b else 'REFUSED'} (projections only -- W48 "
      f"prereg gate derives, never prose-copies; r535 law)")
