"""W18 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W18 = EIGHTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-a
-- bm-a's SECOND owned N1 wave after W12). Sovereignty rotation law
F-20261001-01 slot: W17=bm-c landed (r328, frozen 7e03101fb, finalized K=35,320
ledger 401,948), W18=bm-a per the law sec.4 W17 row verbatim ("W18=bm-a slot,
rotation law; 17+3=20 goes to bm-c"). Freeze window opened only AFTER the
W17xW19 same-band double-freeze adjudication landed (MSG-184x/185x commit-time
ruling: W17 stands, bm-b W19 yields; mirrors healed by bm-c r328-heal
6efed57b6 -- selftests n1 8/8 + engine 36/36 green on healed set).

The W17 row's W18+ WARNING projects BOTH tails clean:
  A +2_000 arithmetic tail (78_001..80_000 == W17 A end + 1) -- projected
  CLEAN, stride kept verbatim (no skip);
  B +200 arithmetic tail (38_300..38_499 == W17 B end + 1) -- projected
  CLEAN, stride kept verbatim (no skip). First wave since the B-band
  re-basing family (W5/W6/W8/W12/W17) where BOTH tails pack arithmetic.

Machine-verified against: all N1 wave bands W2..W17 (W17 included, this
freeze reads the 15-row pre-W18 table), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 design-probe points (40_000/40_001),
N2-W15 draft probe points (31_000/31_500/32_000), lfc actual draw
(30_000..30_099), options_wave2 actual draw (63_000..63_049), AND the
r529 law-mandated N3 actual-seed-set leg (N3-R1 = 70_000..70_005,
single-source derived from perpetual_faces_n3.SEED_BASE + FAMILIES --
per the r529 seed-domain adjudication row every N1/N2/N4 band gate MUST
carry the N3 used-seed-set leg).

r530 bm-a freeze-window run. Freeze trigger = never-dry supply law standing
step (TRIAL_LABOR_LAW sec.4: engine alive, queue 0 after W17 close, board
negative adjudicated, rotation slot W18=bm-a -- anti-idle root fix per
standing CEO full-mobilization law O-20260930-1858 / O-20260930-2054).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W18_A_ARITH = (78_001, 80_000)          # arithmetic tail: projected CLEAN
W18_B_ARITH = (38_300, 38_499)          # arithmetic tail: projected CLEAN
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

# --- N3 actual-seed-set leg (r529 adjudication row: single-source derive) ---
import perpetual_faces_n3 as n3
n3_base = n3.SEED_BASE
n3_names = sorted(n3.FAMILIES)
assert n3_names, "N3 FAMILIES empty"
N3_R1_SEEDS = set(range(n3_base, n3_base + len(n3_names)))
print(f"leg-0 N3-R1 actual seed set (r529 leg): base={n3_base} "
      f"members={len(n3_names)} values={min(N3_R1_SEEDS)}..{max(N3_R1_SEEDS)}")

# --- reserved universe ------------------------------------------------------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= N3_R1_SEEDS
bands = []
for cfg in N1_BANDS.values():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# --- leg 1: BOTH arithmetic tails CLEAN (no skip forced on either side) ----
a_hits = sorted(p for p in points if W18_A_ARITH[0] <= p <= W18_A_ARITH[1])
assert not a_hits, f"leg1-A failed: arithmetic tail dirty {a_hits}"
a_band_hits = [b for b in bands + actual if overlaps(b, W18_A_ARITH)]
assert not a_band_hits, f"leg1-A failed: band overlap {a_band_hits}"
b_hits = sorted(p for p in points if W18_B_ARITH[0] <= p <= W18_B_ARITH[1])
assert not b_hits, f"leg1-B failed: arithmetic tail dirty {b_hits}"
b_band_hits = [b for b in bands + actual if overlaps(b, W18_B_ARITH)]
assert not b_band_hits, f"leg1-B failed: band overlap {b_band_hits}"

# --- leg 2: first clean window == arithmetic on BOTH sides (no skip) -------
first_a = None
x = W18_A_ARITH[0]
while x < 20_260_000:
    r = clean(x, WIDTH_A)
    if r:
        first_a = r
        break
    x += 1
assert first_a, "no clean 2,000-window found below 20260000"
assert first_a == W18_A_ARITH, \
    f"leg2-A failed: first clean window {first_a} != arithmetic {W18_A_ARITH} " \
    "(skip would be FORCED -- re-derive, do not free-pick)"
W18_A = first_a

first_b = None
x = W18_B_ARITH[0]
while x < 20_000_000:
    hi = x + WIDTH_B - 1
    ok = True
    for p in points:
        if x <= p <= hi:
            ok = False
            break
    if ok:
        for b in bands + actual + [W18_A]:
            if overlaps((x, hi), b):
                ok = False
                break
    if ok:
        first_b = (x, hi)
        break
    x += 1
assert first_b, "no clean 200-window found below 20000000"
assert first_b == W18_B_ARITH, \
    f"leg2-B failed: first clean window {first_b} != arithmetic {W18_B_ARITH} " \
    "(skip would be FORCED -- re-derive, do not free-pick)"
W18_B = first_b

# --- leg 3: candidate ADMIT checks ------------------------------------------
conflicts = []
for tag, band in (("A", W18_A), ("B", W18_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W18-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W18-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W18-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W18-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W18-{tag}")
    for p in N3_R1_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N3-R1 actual seed {p} inside W18-{tag} (r529 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W18-{tag}")
assert not overlaps(W18_A, W18_B), "leg3 failed: W18 A/B self-overlap"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
print(f"leg1-A arithmetic tail CLEAN: A {W18_A_ARITH[0]}..{W18_A_ARITH[1]} "
      f"(W17 A end + 1) -- stride kept verbatim")
print(f"leg1-B arithmetic tail CLEAN: B {W18_B_ARITH[0]}..{W18_B_ARITH[1]} "
      f"(W17 B end + 1) -- stride kept verbatim (both-tails-arithmetic first "
      "since the W5/W6/W8/W12/W17 B-skip family)")
print(f"leg2-A first clean {WIDTH_A}-wide window from {W18_A_ARITH[0]}: "
      f"{W18_A[0]}..{W18_A[1]} == arithmetic start (no skip)")
print(f"leg2-B first clean {WIDTH_B}-wide window from {W18_B_ARITH[0]}: "
      f"{W18_B[0]}..{W18_B[1]} == arithmetic start (no skip)")
if conflicts:
    print("W18 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W18 ADMIT: A {W18_A[0]}..{W18_A[1]} + B {W18_B[0]}..{W18_B[1]} "
      "both arithmetic-clean -- engine_owner=bm-a (rotation law slot "
      "W18=bm-a, law sec.4 W17 row).")

# --- W19+ projection (warning text for the law table row) ------------------
w19_a = (W18_A[1] + 1, W18_A[1] + WIDTH_A)
w19_b = (W18_B[1] + 1, W18_B[1] + WIDTH_B)
a_hits19 = sorted(p for p in points if w19_a[0] <= p <= w19_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w19_a)]
b_hits19 = sorted(p for p in points if w19_b[0] <= p <= w19_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w19_b)]
print(f"W19+ projection: A +2_000 = {w19_a[0]}..{w19_a[1]} "
      f"-> {'CLEAN (verify at W19 prereg)' if not a_hits19 else 'REFUSED ' + str(a_hits19)}; "
      f"B +200 = {w19_b[0]}..{w19_b[1]} "
      f"-> {'CLEAN (verify at W19 prereg)' if not b_hits19 else 'REFUSED ' + str(b_hits19)}; "
      "note: bm-b W19 yield re-band per MSG-184x option (a) projects onto "
      "78_001..80_000 / 38_300..38_499 -- THIS W18 freeze lands first, W19 "
      "re-band must machine-scan past it (post-to-yield rotation law).")
