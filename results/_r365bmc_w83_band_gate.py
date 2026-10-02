# -*- coding: utf-8 -*-
"""W83 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W83 = SEVENTY-THIRD ENGINE-OWNED WAVE candidate (ordinal by MACHINE-DERIVE:
engine_owner rows 72 + candidate; the live prose comment sequence carried a
-1 drift at least since W80 -- machine count: W80=70th, W81=71st,
W82=72nd=bm-b r574 SEVENTY-SECOND was CORRECT, bm-a r574's "off-by-one
correction" was itself the wrong side; this gate machine-derives the count,
r359 counts-from-gate law),
bm-c's TWENTY-SIXTH owned per machine-derive (engine_owner==bm-c rows 25 +
candidate). First free number after the registered W82 row (bm-b r574
freeze, landed origin). Seat published=reserved MSG-20261002-1231-bmc
PUSHED to origin BEFORE this freeze per r565 early-visibility law.

Bands (r535 machine-derive law; live-registry derived):
  A 209_004..211_003 = W82 A tail (209_003 + 1) + 2_000 width
  B  54_401..54_600 = W82 B tail (54_400 + 1) + 200 width
  Both sides arithmetic continuation, expected CLEAN (machine-verified
  below vs the full reserved universe; W82 row's disclosed projection
  A 209_004..211_003 CLEAN / B 54_401..54_600 CLEAN cross-checked --
  prose is cross-check ONLY, the machine gate is the sole derive face,
  r302 law).

Machine-verified against: all 80 registered N1 wave bands W2..W82,
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points,
N2-W15 draft probe points, lfc actual draw, options_wave2 actual draw.

r365 bm-c freeze-window run. READ-ONLY against the 80-row table + origin
(candidate passed as parameter; local insertion happens in the freeze
edits tool with FIX-A/B/C hardening, MSG-0640 lineage).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

# --- candidate (pre-insertion gate: parameter, not local row) ----------------
W83_A = (209_004, 211_003)              # arithmetic continuation, W82 A tail +1
W83_B = (54_401, 54_600)                # arithmetic continuation, W82 B tail +1

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"
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

# --- fresh tail check (r511 law: fetch before any freeze action) -------------
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (80 registered rows, NO W83 locally yet) ----------
base_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 83))
assert sorted(N1_BANDS) == base_rows, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 80 registered rows W2..W14, W16..W82)"
assert 82 in N1_BANDS and N1_BANDS[82]["engine_owner"] == "bm-b", \
    "leg0 failed: W82 (bm-b r574) table-tail row must be present"
assert 81 in N1_BANDS and N1_BANDS[81]["engine_owner"] == "bm-a", \
    "leg0 failed: W81 (bm-a r574) row must be present"
assert 80 in N1_BANDS and N1_BANDS[80]["engine_owner"] == "bm-c", \
    "leg0 failed: W80 (bm-c r364) row must be present"
assert N1_BANDS[82]["a"] == (207_004, 209_003) and \
    N1_BANDS[82]["b_exit"] == (54_201, 54_400), \
    "leg0 failed: W82 band drift vs canon row (bm-b r574)"
assert N1_BANDS[81]["a"] == (205_004, 207_003) and \
    N1_BANDS[81]["b_exit"] == (54_001, 54_200), \
    "leg0 failed: W81 band drift vs canon row (bm-a r574)"
assert N1_BANDS[80]["a"] == (203_004, 205_003) and \
    N1_BANDS[80]["b_exit"] == (53_601, 53_800), \
    "leg0 failed: W80 band drift vs canon row (bm-c r364)"
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(bmc_rows) == 25, f"leg0 failed: bm-c rows {bmc_rows} (expect 25)"
engine_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
assert len(engine_rows) == 72, \
    f"leg0 failed: engine-owned rows {len(engine_rows)} (expect 72; " \
    "W83 candidate = SEVENTY-THIRD engine wave by machine-derive -- NOTE " \
    "prose comment-sequence ordinals drifted -1 vs machine count at least " \
    "since W80 (machine: W80=70th, W81=71st, W82=72nd=bm-b r574 correct, " \
    "bm-a r574 'correction' was itself the wrong side); r359 law: gate " \
    "machine output is the sole count authority)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W82 bm-b (r574), "
      f"candidate W83 not local, bm-c rows={len(bmc_rows)}, "
      f"engine-owned rows={len(engine_rows)} -> W83 = 73rd engine wave, "
      f"bm-c 26th owned")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[82]["a"][1] + 1, N1_BANDS[82]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[82]["b_exit"][1] + 1,
           N1_BANDS[82]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (209_004, 211_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (54_401, 54_600), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts {a_hits} {a_band_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero hits -- no skip)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [] and not b_band_hits, \
    f"leg1-B failed: refusal facts {b_hits} {b_band_hits}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN (zero hits -- no skip)")

# --- leg 2: first clean window == candidate (both sides) ---------------------
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
assert first_a == W83_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W83_A}"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W83_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W83_B}"
print(f"leg2: A first-clean == arithmetic == candidate {W83_A[0]}..{W83_A[1]}; "
      f"B first-clean == arithmetic == candidate {W83_B[0]}..{W83_B[1]} "
      "(BOTH SIDES arithmetic continuation zero skip, single reading, "
      "no fork face -- F-20261002-03 not triggered)")
assert not overlaps(W83_A, W83_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W83_A), ("B", W83_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W83-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W83-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W83-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W83-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W83-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W83-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W83-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W83-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W83 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "83: {\"a\": (209_004" not in out, \
    "leg3 failed: a W83 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W83"' not in outn1, \
    "leg3 failed: a W83 WAVE_CONFIGS entry ALREADY exists on origin"
outpr = subprocess.check_output(
    ["git", "show", "origin/main:research/PERPETUAL_N1_W82_PREREG.md"],
    encoding="utf-8", stderr=subprocess.DEVNULL) if True else ""
try:
    subprocess.check_output(
        ["git", "cat-file", "-e", "origin/main:research/PERPETUAL_N1_W83_PREREG.md"],
        stderr=subprocess.DEVNULL)
    sys.exit("leg3 failed: research/PERPETUAL_N1_W83_PREREG.md ALREADY exists "
             "on origin (slot not vacant)")
except subprocess.CalledProcessError:
    pass  # expected: file absent on origin

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W83 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W83 ADMIT: A {W83_A[0]}..{W83_A[1]} + B {W83_B[0]}..{W83_B[1]} "
      "(BOTH SIDES arithmetic continuation zero skip) -- clean vs the "
      f"{len(N1_BANDS)} registered rows + N3-R1 used-seed band + "
      "probe-seed cluster + registry values + probes/actuals -- "
      "engine_owner=bm-c (seat published=reserved MSG-20261002-1231-bmc "
      "PUSHED to origin before this freeze, r565 early-visibility law).")

# --- W84+ projection (warning text for the law table row) --------------------
w84_a = (W83_A[1] + 1, W83_A[1] + WIDTH_A)
w84_b = (W83_B[1] + 1, W83_B[1] + WIDTH_B)
a_hits84 = sorted(p for p in points if w84_a[0] <= p <= w84_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w84_a)]
b_hits84 = sorted(p for p in points if w84_b[0] <= p <= w84_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w84_b)]
print(f"W84+ projection: A arithmetic +2_000 = {w84_a[0]}..{w84_a[1]} "
      f"-> {'CLEAN (verify at W84 prereg)' if not a_hits84 else 'REFUSED ' + str(a_hits84)}; "
      f"B +200 from W83 end = {w84_b[0]}..{w84_b[1]} "
      f"-> {'CLEAN (verify at W84 prereg)' if not b_hits84 else 'REFUSED ' + str(b_hits84)}")
