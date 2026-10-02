# -*- coding: utf-8 -*-
"""W84 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W84 = SEVENTY-FOURTH ENGINE-OWNED WAVE candidate per machine-derive
(engine_owner rows 73 + candidate), bm-a's TWENTY-FIRST owned per
machine-derive (engine_owner==bm-a rows 20 + candidate). First free
number after the registered W83 row (bm-c r365 freeze, landed origin).
Seat published=reserved MSG-20261002-124x-bma PUSHED to origin BEFORE
this freeze per r565 early-visibility law.

Bands (r535 machine-derive law; live-registry derived):
  A 211_004..213_003 = W83 A tail (211_003 + 1) + 2_000 width
     -> arithmetic continuation, expected CLEAN
  B 54_601..54_800 = W83 B tail (54_600 + 1) + 200 width
     -> arithmetic continuation, expected CLEAN (both sides zero skip,
        no fork face -- F-20261002-03 not triggered)

Machine-verified against: all 81 registered N1 wave bands W2..W83,
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points,
N2-W15 draft probe points, lfc actual draw, options_wave2 actual draw.

r575 bm-a freeze-window run. READ-ONLY against the 81-row table + origin
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
W84_A = (211_004, 213_003)              # arithmetic continuation, W83 A tail +1
W84_B = (54_601, 54_800)                # arithmetic continuation, W83 B tail +1

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

# --- leg 0: registry shape (81 registered rows, NO W84 locally yet) --------
base_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 84))
assert sorted(N1_BANDS) == base_rows, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 81 registered rows W2..W14, W16..W83)"
assert 83 in N1_BANDS and N1_BANDS[83]["engine_owner"] == "bm-c", \
    "leg0 failed: W83 (bm-c r365) table-tail row must be present"
assert 82 in N1_BANDS and N1_BANDS[82]["engine_owner"] == "bm-b", \
    "leg0 failed: W82 (bm-b r574) row must be present"
assert 81 in N1_BANDS and N1_BANDS[81]["engine_owner"] == "bm-a", \
    "leg0 failed: W81 (bm-a r574) row must be present"
assert N1_BANDS[83]["a"] == (209_004, 211_003) and \
    N1_BANDS[83]["b_exit"] == (54_401, 54_600), \
    "leg0 failed: W83 band drift vs canon row (bm-c r365)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
assert len(owner_rows) == 73, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 73 -> W84 = 74th)"
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(bma_rows) == 20, f"leg0 failed: bm-a rows {bma_rows} (expect 20)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W83 bm-c (r365), "
      f"candidate W84 not local, engine_owner rows={len(owner_rows)} "
      f"(W84 = 74th), bm-a rows={len(bma_rows)} (W84 = bm-a 21st owned)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[83]["a"][1] + 1, N1_BANDS[83]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[83]["b_exit"][1] + 1,
           N1_BANDS[83]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (211_004, 213_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (54_601, 54_800), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts {a_hits} {a_band_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero hits -- no skip)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [] and b_band_hits == [], \
    f"leg1-B failed: arithmetic position must be CLEAN, got {b_hits} {b_band_hits}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN (zero hits -- no skip)")

# --- leg 2: first clean window == candidate (both sides, zero-skip face) -----
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
assert first_a == W84_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W84_A}"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W84_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W84_B}"
print(f"leg2: A first-clean == arithmetic == candidate {W84_A[0]}..{W84_A[1]}; "
      f"B first-clean == arithmetic == candidate {W84_B[0]}..{W84_B[1]} "
      "(BOTH SIDES zero-skip arithmetic continuation -- no fork face, "
      "F-20261002-03 not triggered)")
assert not overlaps(W84_A, W84_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W84_A), ("B", W84_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W84-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W84-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W84-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W84-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W84-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W84-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W84-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W84-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W84 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "84: {\"a\": (211_004" not in out, \
    "leg3 failed: a W84 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W84"' not in outn1, \
    "leg3 failed: a W84 WAVE_CONFIGS entry ALREADY exists on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W84_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: a W84 per-wave prereg ALREADY exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W84 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W84 ADMIT: A {W84_A[0]}..{W84_A[1]} + B {W84_B[0]}..{W84_B[1]} "
      "(BOTH SIDES arithmetic continuation zero skip, both CLEAN) -- clean vs "
      f"the {len(N1_BANDS)} registered rows + N3-R1 used-seed band + "
      "probe-seed cluster + registry values + probes/actuals -- "
      "engine_owner=bm-a (seat published=reserved MSG-20261002-124x-bma "
      "PUSHED to origin before this freeze, r565 early-visibility law).")

# --- W85+ projection (warning text for the law table row) --------------------
w85_a = (W84_A[1] + 1, W84_A[1] + WIDTH_A)
w85_b = (W84_B[1] + 1, W84_B[1] + WIDTH_B)
a_hits85 = sorted(p for p in points if w85_a[0] <= p <= w85_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w85_a)]
b_hits85 = sorted(p for p in points if w85_b[0] <= p <= w85_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w85_b)]
print(f"W85+ projection: A arithmetic +2_000 = {w85_a[0]}..{w85_a[1]} "
      f"-> {'CLEAN (verify at W85 prereg)' if not a_hits85 else 'REFUSED ' + str(a_hits85)}; "
      f"B +200 from W84 end = {w85_b[0]}..{w85_b[1]} "
      f"-> {'CLEAN (verify at W85 prereg)' if not b_hits85 else 'REFUSED ' + str(b_hits85)}")
