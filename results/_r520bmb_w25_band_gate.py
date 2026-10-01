"""W25 band disjoint machine-gate (law sec.4 tail law: verify before landing).

FOURTEENTH engine-owned wave, sovereignty rotation law F-20261001-01 slot
W25=bm-b (per the law sec.4 W24 row verbatim slot assignment; W22=bm-b
anchor, mod-3 continuation 22+3=25; bm-b's SEVENTH owned wave after
W10/W11/W13/W16/W19/W22). Never-dry supply law standing step (engine alive
rc0, queue 0, board negatives closed -- no idle-waiting).

Bands (BOTH arithmetic continuation, NO skip on either side, exactly as
the W24 row's W25+ WARNING projected -- and that projection is for THIS
machine's own slot, so it is not a third-party reserved face):
  A      92_001..94_000  == W24 A end + 1  (+2_000 tail)
  B_exit 39_700..39_899  == W24 B end + 1  (+200 tail, 39k-segment
                              continuation; W21 crossed into 39k first)

Machine-verified here against: all registered N1 wave bands W2..W24
(23 rows, the full pre-W25 table), the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 mandatory leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 design-probe points (40_000/40_001),
N2-W15 draft probe points (31_000/31_500/32_000), lfc actual draw
(30_000..30_099) AND options_wave2 actual draw (63_000..63_049).

Not a re-pick (R250: W25 bands were never assigned; the measurement face
has no result to fish).  Freeze-window legitimacy: fetch-verified table
tail carries the W24 row and no W25/W26 rows (r511 table-row lock law);
W23 (bm-c, burning) and W24 (bm-a, burn pending) coexist by band
disjointness, not commit order (r531 law).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W25_A = (92_001, 94_000)                # law sec.4 W25 row
W25_B = (39_700, 39_899)

# --- the table-tail arithmetic position from W24 (leg-1 subject) -----------
W24_TAIL_A_ARITH = (92_001, 94_000)    # W24 A end + 1 .. +2_000
W24_TAIL_B_ARITH = (39_700, 39_899)    # W24 B end + 1 .. +200

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

# --- reserved universe (W25 itself EXCLUDED -- it is the candidate) ---------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 25:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

assert 24 in N1_BANDS and N1_BANDS[24]["engine_owner"] == "bm-a", \
    "leg0 failed: W24 (bm-a r535) rows must be present"
assert 23 in N1_BANDS and N1_BANDS[23]["engine_owner"] == "bm-c", \
    "leg0 failed: W23 (bm-c r332) rows must be present"
assert 25 in N1_BANDS, \
    "leg0 failed: W25 candidate row must be landed (canon cross-check leg3)"
assert sorted(k for k in N1_BANDS if k != 25) == \
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21,
     22, 23, 24], \
    f"leg0 failed: unexpected pre-W25 registry keys {sorted(N1_BANDS)}"

# --- leg 1: W24-tail arithmetic position = machine-CLEAN --------------------
a_hits = sorted(p for p in points if W24_TAIL_A_ARITH[0] <= p <= W24_TAIL_A_ARITH[1])
b_hits = sorted(p for p in points if W24_TAIL_B_ARITH[0] <= p <= W24_TAIL_B_ARITH[1])
assert not a_hits, f"leg1-A failed: W24-tail point hits {a_hits}"
assert not b_hits, f"leg1-B failed: W24-tail point hits {b_hits}"
reg_conflicts = []
for b in bands + actual:
    if overlaps(b, W24_TAIL_A_ARITH) or overlaps(b, W24_TAIL_B_ARITH):
        reg_conflicts.append(f"band {b}")
assert not reg_conflicts, \
    f"leg1 failed: W24-tail position dirty vs registered faces: {reg_conflicts}"
# the position equals the W24 row's W25+ published projection, whose slot
# owner is bm-b == THIS machine (own-slot projection, not a reserved face)
assert W24_TAIL_A_ARITH == (N1_BANDS[24]["a"][1] + 1,
                            N1_BANDS[24]["a"][1] + WIDTH_A), \
    "leg1 failed: A position must be the registry-derived W24 tail"
assert W24_TAIL_B_ARITH == (N1_BANDS[24]["b_exit"][1] + 1,
                            N1_BANDS[24]["b_exit"][1] + WIDTH_B), \
    "leg1 failed: B position must be the registry-derived W24 tail"

# --- leg 2: arithmetic continuation = FIRST clean window (no free pick) -----
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
x = N1_BANDS[24]["a"][1] + 1            # scan from W24 registered A end + 1
while x < 20_260_000:
    r = clean(x, WIDTH_A)
    if r:
        first = r
        break
    x += 1
assert first, "no clean 2,000-window found below 20260000"
assert first == W25_A, \
    f"leg2-A failed: first clean window {first} != canon W25 A {W25_A} " \
    "(re-derive, do not free-pick; R250)"
firstb = None
x = N1_BANDS[24]["b_exit"][1] + 1       # scan from W24 registered B end + 1
while x < 20_260_000:
    r = clean(x, WIDTH_B, extra=(W25_A,))
    if r:
        firstb = r
        break
    x += 1
assert firstb, "no clean 200-window found below 20260000"
assert firstb == W25_B, \
    f"leg2-B failed: first clean window {firstb} != canon W25 B {W25_B}"
assert not overlaps(W25_A, W25_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ---------------
conflicts = []
for tag, band in (("A", W25_A), ("B", W25_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 25:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W25-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W25-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W25-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W25-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W25-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W25-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0], N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W25-{tag} (MSG-183x mandatory leg)")
# canon cross-check: the landed W25 row must equal the derived candidate
assert N1_BANDS[25]["a"] == W25_A and N1_BANDS[25]["b_exit"] == W25_B, \
    "leg3 failed: canon W25 row drift vs derived candidate"
assert N1_BANDS[25]["engine_owner"] == "bm-b", "leg3 failed: W25 owner drift"

print("N1_BANDS rows (pre-W25 table):", len(bands) // 2,
      "| SEED_REGISTRY values:", len(science_gates.SEED_REGISTRY),
      "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg)")
print(f"leg1 W24-tail arithmetic position {W24_TAIL_A_ARITH[0]}..{W24_TAIL_A_ARITH[1]} / "
      f"{W24_TAIL_B_ARITH[0]}..{W24_TAIL_B_ARITH[1]} machine-CLEAN vs all "
      f"registered faces == own-slot published projection (slot W25=bm-b)")
print(f"leg2 first-clean-window scan from W24 registered tails: "
      f"A {first[0]}..{first[1]} == canon, B {firstb[0]}..{firstb[1]} == canon "
      f"(both arithmetic, no skip, R250)")
if conflicts:
    print("W25 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W25 ADMIT: A {W25_A[0]}..{W25_A[1]} + B {W25_B[0]}..{W25_B[1]} both "
      f"clean vs 22 registered rows + N3-R1 used-seed band + registry/probes/"
      f"actuals -- engine_owner=bm-b (rotation law slot W25=bm-b per W24 row "
      f"verbatim; FOURTEENTH engine-owned wave).")

# --- W26+ projection (warning text for the law table row) -------------------
w26_a = (W25_A[1] + 1, W25_A[1] + WIDTH_A)
w26_b = (W25_B[1] + 1, W25_B[1] + WIDTH_B)
a_hits26 = sorted(p for p in points if w26_a[0] <= p <= w26_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w26_a)]
b_hits26 = sorted(p for p in points if w26_b[0] <= p <= w26_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w26_b)]
print(f"W26+ projection: A arithmetic +2_000 = {w26_a[0]}..{w26_a[1]} "
      f"-> {'CLEAN (verify at W26 prereg)' if not a_hits26 else 'REFUSED ' + str(a_hits26)}; "
      f"B +200 = {w26_b[0]}..{w26_b[1]} "
      f"-> {'CLEAN (verify at W26 prereg)' if not b_hits26 else 'REFUSED ' + str(b_hits26)} "
      f"(rotation slot W26=bm-c; B jump family W5/W6/W8/W12/W17 precedent "
      f"if REFUSED)")
