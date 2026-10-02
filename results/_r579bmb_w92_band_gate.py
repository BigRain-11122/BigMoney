# -*- coding: utf-8 -*-
"""W92 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W92 candidate = first FREE number after the registered W91 row (bm-b r578
freeze, commit a0d6d8287 lineage; W90 bm-a r579 registered, W91 bm-b r578
registered -- BOTH in the live table, single state).

  A 227_004..229_003 (W91 tail 227_003 + 1, width 2_000, arithmetic
     continuation, expected CLEAN zero refusal points)
  B 56_701..56_900   (W91 B end 56_700 + 1, width 200, arithmetic
     continuation, expected CLEAN zero refusal points)

Machine-verified against: all registered N1 wave bands (W2..W14, W16..W91),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options draws.

r579 bm-b freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W92_A = (227_004, 229_003)
W92_B = (56_701, 56_900)

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster frozen)"
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

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

# --- leg 0: registry shape (single state: W90 AND W91 both registered) -------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \
    list(range(16, 92)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[89]["a"] == (221_004, 223_003) and \
    N1_BANDS[89]["b_exit"] == (56_001, 56_200) and \
    N1_BANDS[89].get("engine_owner") == "bm-b", "leg0 failed: W89 row drift"
assert N1_BANDS[90]["a"] == (223_004, 225_003) and \
    N1_BANDS[90]["b_exit"] == (56_201, 56_400) and \
    N1_BANDS[90].get("engine_owner") == "bm-a", "leg0 failed: W90 row drift"
assert N1_BANDS[91]["a"] == (225_004, 227_003) and \
    N1_BANDS[91]["b_exit"] == (56_501, 56_700) and \
    N1_BANDS[91].get("engine_owner") == "bm-b", "leg0 failed: W91 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, "
      f"single state (W90 bm-a + W91 bm-b both registered)")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-b "
      f"rows={len(bmb_rows)} -> W92 = bm-b {len(bmb_rows) + 1}th owned; "
      f"W92 ordinal = {len(owner_rows) + 1}th engine wave by machine-derive")

# --- leg 0b: W92 seat vacancy on origin ----------------------------------------
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], capture_output=True)
w92_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
             if "w92" in ln.lower() and "seat" in ln.lower()]
assert not w92_seats, f"leg0b failed: W92 seat already declared {w92_seats}"
print("leg0b: W92 seat vacancy machine-checked (zero W92 seat MSGs on "
      "origin, inbox + processed/)")

# --- leg 1: arithmetic continuation from the W91 tails (no skips expected) ---
tail = N1_BANDS[91]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W92_A and ARITH_B == W92_B, \
    f"leg1 drift: {ARITH_A} {ARITH_B} vs candidate {W92_A} {W92_B}"
a_hits = sorted(p for p in points if W92_A[0] <= p <= W92_A[1])
a_band_ref = [b for b in bands + actual if overlaps(b, W92_A)]
assert not a_hits and not a_band_ref, \
    f"leg1 chain-A not clean: {a_hits} {a_band_ref}"
b_hits = sorted(p for p in points if W92_B[0] <= p <= W92_B[1])
b_band_ref = [b for b in bands + actual if overlaps(b, W92_B)]
assert not b_hits and not b_band_ref, \
    f"leg1 chain-B not clean: {b_hits} {b_band_ref}"
print(f"leg1: A arithmetic continuation {W92_A[0]}..{W92_A[1]} CLEAN "
      f"(zero refusal points, no skip); B arithmetic continuation "
      f"{W92_B[0]}..{W92_B[1]} CLEAN (zero refusal points, no skip)")

# --- leg 2: first clean window == candidate (both sides) ----------------------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first_a = clean(W92_A[0], WIDTH_A)
assert first_a == W92_A, f"leg2-A failed: {first_a} != {W92_A}"
first_b = clean(W92_B[0], WIDTH_B)
assert first_b == W92_B, f"leg2-B failed: {first_b} != {W92_B}"
print(f"leg2: A first-clean {W92_A[0]}..{W92_A[1]} == candidate; "
      f"B first-clean {W92_B[0]}..{W92_B[1]} == candidate")
assert not overlaps(W92_A, W92_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy -----------------------------------
conflicts = []
for tag, band in (("A", W92_A), ("B", W92_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W92-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W92-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W92-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W92-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W92-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W92-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W92-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W92-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "92: {\"a\": (227_004" not in out, \
    "leg3 failed: W92 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W92"' not in outn1, \
    "leg3 failed: W92 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W92_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W92 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | single state (W90+W91 registered)")
if conflicts:
    print("W92 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W92 ADMIT: A {W92_A[0]}..{W92_A[1]} + B {W92_B[0]}..{W92_B[1]} "
      f"(single state; refusal facts: NONE -- pure arithmetic continuation "
      "from the registered W91 tails, both sides zero refusal points) -- "
      "clean vs all registered rows + registry + probes/actuals -- "
      "engine_owner=bm-b (seat published=reserved pushed BEFORE this "
      "freeze per r565 early-visibility law). NOT a re-pick (R250: W92 "
      "bands were never assigned).")

# --- W93+ projection (warning text for the law table row) ---------------------
w93_a = (W92_A[1] + 1, W92_A[1] + WIDTH_A)
w93_b = (W92_B[1] + 1, W92_B[1] + WIDTH_B)
a_hits93 = sorted(p for p in points if w93_a[0] <= p <= w93_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w93_a)]
b_hits93 = sorted(p for p in points if w93_b[0] <= p <= w93_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w93_b)]
print(f"W93+ projection: A arithmetic +2_000 = {w93_a[0]}..{w93_a[1]} "
      f"-> {'CLEAN (verify at W93 prereg)' if not a_hits93 else 'REFUSED ' + str(a_hits93)}; "
      f"B +200 from W92 end = {w93_b[0]}..{w93_b[1]} "
      f"-> {'CLEAN (verify at W93 prereg)' if not b_hits93 else 'REFUSED ' + str(b_hits93)}")
