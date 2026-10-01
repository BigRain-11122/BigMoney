"""W34 PRE-SCAN band gate (bm-b seat-readiness pre-check -- NOT a freeze).

W34 = TWENTY-THIRD ENGINE-OWNED WAVE, rotation slot W34=bm-b per the
law sec.4 W33 row verbatim (W31=bm-b real anchor -- finalize landed
bm-b r525, K=66,120; +3 -> W34=bm-b). This is bm-b's TENTH owned wave
after W10/W11/W13/W16/W19/W22/W25/W28/W31.

SEAT DISCIPLINE (r543 law, r544 discharge precedent): W34 freeze is
gated on the W33 seat completing (registered + burned 12/12 +
ledger-appended at the bm-a seat, W33 finalize can stay open -- r544
froze W33 with only W32 finalize pending). This pre-scan takes NO
freeze action, registers NO row, burns NOTHING (R99 zero-burn-before-
freeze). It machine-derives the W34 arithmetic projection from the
landed W33 registry row and collision-checks it against the full
reserved universe NOW, so that:
  (a) any new reservation landing on origin between rounds is caught
      before the seat round (r535 law: clean-projection claims must
      be machine-derived, never prose-copied -- the r544 WARNING prose
      is re-derived here against the CURRENT tree+registry);
  (b) the seat round (W33 12/12 -> W34 freeze) can consume this
      receipt as its leg-0 evidence base and re-run its own full gate
      fresh (this pre-scan does NOT substitute the freeze gate).

Machine-verified against: all registered N1 wave bands W2..W33 (31
rows incl. W33 -- a RESERVED face for this scan, not the candidate),
the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 bm-a mandatory
leg), the runner design-probe seed cluster 95_000..95_003 (r335
discovery leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values,
N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe points
(31_000/31_500/32_000), lfc actual draw (30_000..30_099) and
options_wave2 actual draw (63_000..63_049).

r527 bm-b pre-scan window run. Honest status lines (not assertions):
W33 burn completeness on origin + W32 finalize pending at bm-c seat.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (arithmetic continuation of the landed W33 row) --------------
W33_A = tuple(N1_BANDS[33]["a"])        # 109_004..111_003 (r544 freeze)
W33_B = tuple(N1_BANDS[33]["b_exit"])  # 41_601..41_800
WIDTH_A = 2_000
WIDTH_B = 200
W34_A = (W33_A[1] + 1, W33_A[1] + WIDTH_A)   # 111_004..113_003
W34_B = (W33_B[1] + 1, W33_B[1] + WIDTH_B)   # 41_801..42_000

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

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W34 itself NOT in registry -- seat not reached) ------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 34:
        continue                         # candidate wave (must not exist yet)
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (31 registered rows, W34 absent -- no queue-jump)
pre_w34 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
           33]
assert sorted(N1_BANDS) == pre_w34, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expected 31 registered rows W2..W33, W34 ABSENT -- seat discipline)"
assert 34 not in N1_BANDS, "leg0 failed: W34 already registered (queue-jump?)"
assert N1_BANDS[33]["engine_owner"] == "bm-a", "leg0 failed: W33 owner drift"
assert N1_BANDS[31]["engine_owner"] == "bm-b", \
    "leg0 failed: W31 (bm-b) rows must be present (r525 freeze, finalized)"

# --- leg 0b: W33 row's W34+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "111_004..113_003" in canon and "41_801..42_000" in canon, \
    "leg0b failed: W33 row W34+ WARNING (published projection) prose " \
    "not found in the canon file"
print("leg0b W33 row W34+ WARNING prose present (published projection "
      "= reserved-face basis, r518; machine-re-derived below per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = W34_A
ARITH_B = W34_B
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts {a_hits} (W33 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, r544 "
      f"WARNING projection verified machine-side on current tree)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts {b_hits} (W33 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits -- no skip, r544 WARNING projection verified machine-side)")

# --- leg 2: first clean window == arithmetic position (NO skip either side) --
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
assert first_a == W34_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W34_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B, extra=(W34_A,))
assert first_b == W34_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W34_B} " \
    "(no skip expected; own A band reserved per W6 law)"
assert not overlaps(W34_A, W34_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W34_A), ("B", W34_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W34-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W34-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W34-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W34-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W34-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W34-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W34-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W34-{tag} (r335 leg)")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")

# --- honest seat status lines (informational, NOT assertions) ---------------
try:
    out = subprocess.check_output(
        ["git", "ls-tree", "origin/main", "results/p2cal_ext/n1_w33/"],
        text=True, cwd=ROOT).strip().splitlines()
    w33_done = len(out)
except Exception as exc:
    w33_done = -1
print(f"seat status: W33 (bm-a slot) origin shards = {w33_done}/12 "
      f"{'-- seat NOT reached, freeze waits (r543 discipline)' if w33_done < 12 else '-- seat REACHED, next bm-b round freezes W34'}"
      f"; W32 finalize pending at bm-c seat (consumes nothing W34 touches)")

if conflicts:
    print("W34 PRE-SCAN REFUSED (re-band at freeze):")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W34 PRE-SCAN ADMIT-READY: A {W34_A[0]}..{W34_A[1]} + B "
      f"{W34_B[0]}..{W34_B[1]} both clean vs 31 registered rows (incl. "
      f"W33) + N3-R1 used-seed band + probe-seed cluster + registry "
      f"values + probes/actuals -- rotation slot W34=bm-b (W33 row "
      f"verbatim); arithmetic continuation BOTH tails, no skip; freeze "
      f"gate must re-run fresh at the seat round (this receipt = leg-0 "
      f"evidence base, not a substitute).")
