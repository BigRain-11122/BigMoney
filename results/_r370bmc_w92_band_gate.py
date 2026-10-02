# -*- coding: utf-8 -*-
"""W92 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W92 candidate = first FREE number after the registered W91 row (bm-b r578
freeze, commit 636dab137). Single-state gate: ALL rows W2..W91 registered
(W89 bm-b burned finalize-pending, W90 bm-a burning 6/12, W91 bm-b burned
finalize-pending = THREE in-flight upstream seats, no unregistered gap).

  A 227_004..229_003 (arithmetic continuation from the W91 A tail, width
     2_000, expected CLEAN)
  B 56_701..56_900   (arithmetic continuation from the W91 B tail, width
     200, expected CLEAN per the W91 gate W92+ projection -- re-derived
     here per r335 law: projection is a warning, never a transcription)

Machine-verified against: all registered N1 wave bands (W2..W91), the live
SEED_REGISTRY values, N3-R1 used-seed band 70_000..70_005 (MSG-183x r529
leg), probe cluster 95_000..95_003 (r335 leg), v1 in-use + W1 ext bands,
N2/N4 probe points, N2-W15 draft probe points, lfc/options actual draws.

r370 bm-c freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000  # CREATE_NO_WINDOW (zero desktop flash law)

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


def git(args, **kw):
    return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                          creationflags=CREAT, **kw)


git(["fetch", "origin"])

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

# --- leg 0: registry shape (single state: W2..W91 all registered) -------------
keys = sorted(N1_BANDS)
EXPECT = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 92))
assert keys == EXPECT, \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]} (W92 already registered by another machine? r511 tail-lock -> yield)"
assert N1_BANDS[91]["a"] == (225_004, 227_003) and \
    N1_BANDS[91]["b_exit"] == (56_501, 56_700) and \
    N1_BANDS[91].get("engine_owner") == "bm-b", "leg0 failed: W91 row drift"
for w in (88, 89, 90, 91):
    assert w in N1_BANDS, f"leg0 failed: W{w} must be registered"
assert N1_BANDS[90]["a"] == (223_004, 225_003) and \
    N1_BANDS[90]["b_exit"] == (56_201, 56_400) and \
    N1_BANDS[90].get("engine_owner") == "bm-a", "leg0 failed: W90 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (single state, "
      f"no seat gap)")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate -> W92 = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive; bm-c rows="
      f"{len(bmc_rows)} -> W92 = bm-c {len(bmc_rows) + 1}th owned "
      f"(prose ordinal -1 drift disclosed since W80, r359 law)")

# --- leg 0b: W92 seat vacancy on origin (before this machine's seat push) -----
_r = git(["ls-tree", "--name-only", "-r", "origin/main", "--",
          "fleet/inbox/", "fleet/inbox/processed/"])
w92_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
             if "w92" in ln.lower() and "seat" in ln.lower()]
assert not w92_seats, f"leg0b failed: W92 seat already declared {w92_seats} (r518-1 published=reserved -> yield)"
print("leg0b: W92 seat vacancy machine-checked (zero W92 seat MSGs on origin)")

# --- leg 1: arithmetic continuation from the registered W91 tails ------------
tail = N1_BANDS[91]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W92_A, f"leg1-A drift: {ARITH_A} != {W92_A}"
assert ARITH_B == W92_B, f"leg1-B drift: {ARITH_B} != {W92_B}"
print(f"leg1: arithmetic continuation A {ARITH_A[0]}..{ARITH_A[1]} / "
      f"B {ARITH_B[0]}..{ARITH_B[1]} from the W91 tails (227_003 / 56_700)")

# --- leg 2: first clean window == candidate (both sides, honest walk) --------
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
assert first_a == W92_A, f"leg2-A failed: first clean {first_a} != {W92_A}"
first_b = clean(W92_B[0], WIDTH_B)
assert first_b == W92_B, f"leg2-B failed: first clean {first_b} != {W92_B}"
print(f"leg2: A first-clean {W92_A[0]}..{W92_A[1]} == candidate; "
      f"B first-clean {W92_B[0]}..{W92_B[1]} == candidate (both arithmetic, "
      f"zero refusal points -- honest forward walk, no pin chain needed)")
assert not overlaps(W92_A, W92_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
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
out = git(["show", "origin/main:scripts/perpetual_faces.py"])
assert b'92: {"a": (227_004' not in out.stdout, \
    "leg3 failed: W92 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = git(["show", "origin/main:scripts/perpetual_faces_n1.py"])
assert b'"batch": "PERPETUAL-N1-W92"' not in outn1.stdout, \
    "leg3 failed: W92 WAVE_CONFIGS ALREADY on origin"
outpre = git(["ls-tree", "--name-only", "origin/main", "--",
              "research/PERPETUAL_N1_W92_PREREG.md"])
assert not outpre.stdout.strip(), \
    "leg3 failed: W92 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | single state (all rows registered)")
if conflicts:
    print("W92 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W92 ADMIT: A {W92_A[0]}..{W92_A[1]} + B {W92_B[0]}..{W92_B[1]} "
      f"(arithmetic continuation from the registered W91 tails, CLEAN zero "
      "refusal points vs all registered rows + registry + probes/actuals) "
      "-- engine_owner=bm-c (seat published=reserved to be pushed BEFORE "
      "this freeze per r565 early-visibility law). NOT a re-pick (R250: W92 "
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
