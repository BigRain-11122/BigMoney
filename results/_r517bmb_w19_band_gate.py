"""W19 band disjoint machine-gate v3 (law sec.4 tail law: verify before landing).

v3 = the r518 YIELD + RE-BAND receipt. History: the r517 freeze window drafted
W19 blind to bm-c's same-window W17 freeze (both machines deterministic-same-
verdict the W16 table-tail continuation: A 76_001..78_000 + B skip-over
38_100..38_299); bm-c's W17 rows reached origin first (r328, ~18:23) vs bm-b's
surgical 5f18511ce (18:28:34) -- bm-b is the latercomer and YIELDS per the r511
commit-order law and MSG-20261001-184x (bm-c kill-advice + adjudication). The
old-band W19 products (12/12 burned -- the engine finished shards 9-11 at
18:30-18:32 before the truncation could land; finalize NEVER ran) are ALL
discarded at yield: zero science-ledger pollution (r523 discard precedent,
audit.machine=bm-b verified per-file, r525 ownership law).

RE-BAND (MSG-184x yield option (a) "re-band, keep wave number"): W19 is the
EIGHTH ENGINE-OWNED WAVE, engine_owner=bm-b (sovereignty rotation law
F-20261001-01 slot W19=bm-b; wave number 18 unfrozen, gap notes, r516 derive
law). The table-tail arithmetic position from W17 (A 78_001..80_000 = W17 A
end + 1 / B 38_300..38_499 = W17 B end + 1) is machine-CLEAN vs every
registered face BUT it is W18's PUBLISHED PROJECTION (rotation slot W18=bm-a;
published in the W17 row's W18+ WARNING + bm-a r529 "W18 gate projection
CLEAN pending-W17"). Taking it for W19 would manufacture a THIRD collision
against bm-a's slot -- the r511 lesson makes published projections RESERVED
FACES (exhaustive reservation scan). So W19 re-bases past W18's projection:
A 80_001..82_000 (== W18 projected A end + 1), B 38_500..38_699 (== W18
projected B end + 1) -- BOTH arithmetic continuation, NO skip (the W16-tail
forced skip-over was consumed by W17's B re-base). NOT a re-pick (R250: the
pre-yield W19 assignment is voided by the collision; the measurement face
has zero results to fish -- finalize never ran, ledger +0).

Machine-verified here against: all registered N1 wave bands W2..W17 (15 rows,
W17 included -- the healed origin set), W18's PUBLISHED PROJECTION bands
(78_001..80_000 / 38_300..38_499), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg: "W17/W18/W19 band-gate receipts must
include the N3 used-seed-band leg"), v1 in-use + W1 ext bands, SEED_REGISTRY
live values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

r518 bm-b yield-reband-window run (v3; supersedes the r517 v1 receipt for the
voided old-band assignment and the never-committed half-done v2 draft whose
bands 78_001..80_000/38_300..38_499 would have collided with bm-a's W18
slot).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W19_A = (80_001, 82_000)                # law sec.4 W19 row (re-based)
W19_B = (38_500, 38_699)

# --- the table-tail arithmetic position from W17 (leg-1 subject) ------------
W17_TAIL_A_ARITH = (78_001, 80_000)     # W17 A end + 1 .. +2_000
W17_TAIL_B_ARITH = (38_300, 38_499)     # W17 B end + 1 .. +200

# --- W18 PUBLISHED PROJECTION (reserved face, slot W18=bm-a) -----------------
# Published in the law sec.4 W17 row's W18+ WARNING ("A 78_001..80_000 and B
# 38_300..38_499 project clean -- verify at W18 prereg, rotation slot
# W18=bm-a") + bm-a r529 "W18 gate projection CLEAN pending-W17" (MSG-183x).
W18_PROJ_A = (78_001, 80_000)
W18_PROJ_B = (38_300, 38_499)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)            # six bootstrap-CI member seeds

LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)        # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)      # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe (W19 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 19:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT + [W18_PROJ_A, W18_PROJ_B]  # projections reserved
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

assert 17 in N1_BANDS and N1_BANDS[17]["engine_owner"] == "bm-c", \
    "leg0 failed: W17 (bm-c) rows must be present (healed origin set)"
assert 18 not in N1_BANDS, \
    "leg0 failed: W18 unfrozen at this window (published projection only)"
assert sorted(N1_BANDS) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19], \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"

# --- leg 1: W17-tail arithmetic position = machine-CLEAN but W18-RESERVED ---
a_hits = sorted(p for p in points if W17_TAIL_A_ARITH[0] <= p <= W17_TAIL_A_ARITH[1])
b_hits = sorted(p for p in points if W17_TAIL_B_ARITH[0] <= p <= W17_TAIL_B_ARITH[1])
assert not a_hits, f"leg1-A failed: W17-tail point hits {a_hits}"
assert not b_hits, f"leg1-B failed: W17-tail point hits {b_hits}"
reg_conflicts = []
for b in bands + actual:
    if b in (W18_PROJ_A, W18_PROJ_B):
        continue                         # the projection IS the position (leg1
                                          # subject); reserved-ness handled below
    if overlaps(b, W17_TAIL_A_ARITH) or overlaps(b, W17_TAIL_B_ARITH):
        reg_conflicts.append(f"band {b}")
assert not reg_conflicts, \
    f"leg1 failed: W17-tail position dirty vs registered faces: {reg_conflicts}"
# the position IS W18's published projection -> REFUSED for W19 (slot bm-a)
assert W17_TAIL_A_ARITH == W18_PROJ_A and W17_TAIL_B_ARITH == W18_PROJ_B, \
    "leg1 failed: W17-tail arithmetic position must equal W18's projection"

# --- leg 2: re-based continuation = first clean window past W18 projection ---
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first = None
x = W18_PROJ_A[1] + 1                    # scan from W18 projected A end + 1
while x < 20_260_000:
    r = clean(x, WIDTH_A)
    if r:
        first = r
        break
    x += 1
assert first, "no clean 2,000-window found below 20260000"
assert first == W19_A, \
    f"leg2-A failed: first clean window {first} != canon W19 A {W19_A} " \
    "(re-derive, do not free-pick; R250)"
firstb = None
x = W18_PROJ_B[1] + 1                    # scan from W18 projected B end + 1
while x < 20_260_000:
    r = clean(x, WIDTH_B, extra=(W19_A,))
    if r:
        firstb = r
        break
    x += 1
assert firstb, "no clean 200-window found below 20260000"
assert firstb == W19_B, \
    f"leg2-B failed: first clean window {firstb} != canon W19 B {W19_B}"
assert not overlaps(W19_A, W19_B), "A/B overlap after re-band"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ---------------
conflicts = []
for tag, band in (("A", W19_A), ("B", W19_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 19:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W19-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W19-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W19-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W19-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W19-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W19-{tag}")
    for nm, proj in (("W18-proj-A", W18_PROJ_A), ("W18-proj-B", W18_PROJ_B)):
        if overlaps(proj, band):
            conflicts.append(f"{nm} {proj[0]}..{proj[1]} x W19-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0], N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W19-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W19 row must equal the derived candidate
assert N1_BANDS[19]["a"] == W19_A and N1_BANDS[19]["b_exit"] == W19_B, \
    "leg3 failed: canon W19 row drift vs derived candidate"
assert N1_BANDS[19]["engine_owner"] == "bm-b", "leg3 failed: W19 owner drift"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg)")
print(f"leg1 W17-tail arithmetic position {W17_TAIL_A_ARITH[0]}..{W17_TAIL_A_ARITH[1]} / "
      f"{W17_TAIL_B_ARITH[0]}..{W17_TAIL_B_ARITH[1]} machine-CLEAN vs all registered "
      f"faces BUT == W18 published projection (slot W18=bm-a) -> REFUSED for W19")
print(f"leg2 re-based continuation (first clean windows past W18 projection): "
      f"A {first[0]}..{first[1]} == canon, B {firstb[0]}..{firstb[1]} == canon "
      f"(both arithmetic, no skip, R250)")
if conflicts:
    print("W19 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W19 ADMIT (v3 yield re-band): A {W19_A[0]}..{W19_A[1]} + B "
      f"{W19_B[0]}..{W19_B[1]} both clean vs 15 registered rows + W18 "
      f"published projection + N3-R1 used-seed band + registry/probes/actuals "
      f"-- engine_owner=bm-b (rotation law slot W19=bm-b; number 18 unfrozen, "
      f"gap noted). Old-band products discarded at yield (12/12, finalize "
      f"never ran, zero ledger pollution).")

# --- W20+ projection (warning text for the law table row) -------------------
w20_a = (W19_A[1] + 1, W19_A[1] + WIDTH_A)
w20_b = (W19_B[1] + 1, W19_B[1] + WIDTH_B)
a_hits20 = sorted(p for p in points if w20_a[0] <= p <= w20_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w20_a)]
b_hits20 = sorted(p for p in points if w20_b[0] <= p <= w20_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w20_b)]
print(f"W20+ projection: A arithmetic +2_000 = {w20_a[0]}..{w20_a[1]} "
      f"-> {'CLEAN (verify at W20 prereg)' if not a_hits20 else 'REFUSED ' + str(a_hits20)}; "
      f"B +200 = {w20_b[0]}..{w20_b[1]} "
      f"-> {'CLEAN (verify at W20 prereg)' if not b_hits20 else 'REFUSED ' + str(b_hits20)}")
