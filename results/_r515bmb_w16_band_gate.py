"""W16 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W16 = SIXTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage, engine_owner=bm-b
-- bm-b's FOURTH owned wave after W10/W11/W13). Sovereignty rotation law
F-20261001-01 slot: W13=bm-b anchored, +3 -> W16=bm-b. Unified wave number
15 is concurrently held by bm-a's N2-W15 (DRAFT on origin; seed domain =
N2/N4 30_000+/40_000+ per law sec.4 N2/N4 row -- disjoint from the N1
74_001+ domain), so the N1 face numbering continues at 波16 with NO 波15
row (honest skip note in the table row).

The W14 row's W15+ WARNING projection fires: BOTH arithmetic tails land
clean (A 74_001..76_000 == W14 A end + 1; B 29_700..29_899 == W14 B end +
1) -- NO forced skip this wave. Machine-verified here against: all N1 wave
bands W2..W14 (W14 included this freeze), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 design-probe points (40_000/40_001),
N2-W15 draft probe points (31_000/31_500/32_000), lfc actual draw
(30_000..30_099) AND options_wave2 actual draw (63_000..63_049).

r515 bm-b freeze-window run. Freeze trigger = never-dry supply law standing
step (watermark red runnable-work-idle-low-cpu, same adjudicated family:
engine alive, queue 0, pool claimable 0, W14-GENERATE single shard owned by
bm-a per owner-scan, board negative adjudicated) -- anti-idle root fix per
standing CEO full-mobilization law O-20260930-1858 / O-20260930-2054.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W16_A_ARITH = (74_001, 76_000)          # arithmetic tail: projected CLEAN
W16_B_ARITH = (29_700, 29_899)          # arithmetic tail: projected CLEAN
LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)       # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)  # N2-W15 draft probe facts
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH = 2_000

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# --- reserved universe ------------------------------------------------------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
bands = []
for cfg in N1_BANDS.values():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def clean(lo, width=WIDTH):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# --- leg 1: BOTH arithmetic tails CLEAN (ADMIT machine evidence) -----------
for tag, cand in (("A", W16_A_ARITH), ("B", W16_B_ARITH)):
    hits = sorted(p for p in points if cand[0] <= p <= cand[1])
    assert not hits, f"leg1 failed: {tag} arithmetic tail dirty {hits}"
# --- leg 2: first clean window from the arithmetic start == arithmetic -----
first = None
x = W16_A_ARITH[0]
while x < 20_260_000:
    r = clean(x)
    if r:
        first = r
        break
    x += 1
assert first, "no clean 2,000-window found below 20260000"
assert first == W16_A_ARITH, \
    f"leg2 failed: first clean window {first} != arithmetic {W16_A_ARITH} " \
    "(skip would be FORCED -- re-derive, do not free-pick)"
W16_A = first

# --- leg 3: candidate ADMIT checks ------------------------------------------
conflicts = []
for tag, band in (("A", W16_A), ("B", W16_B_ARITH)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W16-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W16-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W16-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W16-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W16-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W16-{tag}")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
print(f"leg1 BOTH arithmetic tails CLEAN: A {W16_A_ARITH[0]}..{W16_A_ARITH[1]} "
      f"(W14 A end + 1), B {W16_B_ARITH[0]}..{W16_B_ARITH[1]} (W14 B end + 1)")
print(f"leg2 first clean {WIDTH}-wide window from {W16_A_ARITH[0]}: "
      f"{first[0]}..{first[1]} == arithmetic start (no forced skip, R250)")
if conflicts:
    print("W16 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W16 ADMIT: A {W16_A[0]}..{W16_A[1]} + B {W16_B_ARITH[0]}.."
      f"{W16_B_ARITH[1]} both clean -- engine_owner=bm-b "
      "(rotation law slot W16=bm-b; number 15 held by bm-a's N2-W15 draft).")

# --- W17+ projection (warning text for the law table row) ------------------
w17_a = (W16_A[1] + 1, W16_A[1] + WIDTH)
w17_b = (W16_B_ARITH[1] + 1, W16_B_ARITH[1] + 200)
a_hits = sorted(p for p in points if w17_a[0] <= p <= w17_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w17_a)]
b_hits = sorted(p for p in points if w17_b[0] <= p <= w17_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w17_b)]
print(f"W17+ projection: A arithmetic +2_000 = {w17_a[0]}..{w17_a[1]} "
      f"-> {'CLEAN (verify at W17 prereg)' if not a_hits else 'REFUSED ' + str(a_hits)}; "
      f"B +200 = {w17_b[0]}..{w17_b[1]} "
      f"-> {'CLEAN (verify at W17 prereg)' if not b_hits else 'REFUSED ' + str(b_hits)}")
