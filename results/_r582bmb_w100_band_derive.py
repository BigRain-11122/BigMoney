# r582 bm-b W100 band machine-derive (pre-seat; gate formal run at freeze window next round)
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True, creationflags=CREAT)

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A, WIDTH_B = 2_000, 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

# leg 0: registry shape -- W99 must be registered (bm-c r374), tail=W99
keys = sorted(N1_BANDS)
base_keys = [2,3,4,5,6,7,8,9,10,11,12,13,14] + list(range(16, 100))
assert keys == base_keys, f"leg0 registry shape drift: tail {keys[-4:]}"
assert N1_BANDS[99]["a"] == (241_004, 243_003), N1_BANDS[99]["a"]
assert N1_BANDS[99]["b_exit"] == (58_551, 58_750), N1_BANDS[99]["b_exit"]
assert N1_BANDS[99].get("engine_owner") == "bm-c", "leg0 W99 owner drift"
assert N1_BANDS[98].get("engine_owner") == "bm-a", "leg0 W98 owner drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} rows, tail=W{keys[-1]}, engine_owner rows={len(owner_rows)}, bm-b rows={len(bmb_rows)}")
print(f"leg0: W100 = bm-b {len(bmb_rows)+1}th owned; ordinal = {len(owner_rows)+1}th engine wave by machine-derive")

# leg 1: arithmetic continuation from registered W99 tails
tail = N1_BANDS[99]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == (243_004, 245_003), ARITH_A
assert ARITH_B == (58_751, 58_950), ARITH_B

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

def refusal(band):
    pt = sorted(p for p in points if band[0] <= p <= band[1])
    bd = [b for b in bands + actual if overlaps(b, band)]
    return pt, bd

for tag, band in (("A", ARITH_A), ("B", ARITH_B)):
    pt, bd = refusal(band)
    assert not pt and not bd, f"W100-{tag} REFUSED: points={pt} bands={bd}"
    print(f"leg1 {tag}: arithmetic {band[0]}..{band[1]} CLEAN (zero refusal points, honest forward walk)")

# leg 2: origin vacancy (W100 three-face check)
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert '100: {"a": (243_004' not in out, "W100 row ALREADY on origin"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W100"' not in outn1, "W100 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W100_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "W100 prereg ALREADY on origin"

# W101+ projection for the seat MSG
W101_A = (ARITH_A[1] + 1, ARITH_A[1] + WIDTH_A)
W101_B = (ARITH_B[1] + 1, ARITH_B[1] + WIDTH_B)
pa, ba = refusal(W101_A); pb, bb = refusal(W101_B)
print(f"W101+ projection: A {W101_A[0]}..{W101_A[1]} -> {'CLEAN' if not (pa or ba) else 'REFUSED ' + str(pa or ba)}; B {W101_B[0]}..{W101_B[1]} -> {'CLEAN' if not (pb or bb) else 'REFUSED ' + str(pb or bb)}")
print(f"W100 DERIVED: A {ARITH_A[0]}..{ARITH_A[1]} + B {ARITH_B[0]}..{ARITH_B[1]} -- ADMIT (draft; formal gate at freeze window)")
