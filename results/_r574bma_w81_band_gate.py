"""W81 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W81 = SEVENTIETH ENGINE-OWNED WAVE candidate (ordinal follows the live
comment sequence W78=67th, W79=68th, W80=69th), bm-a's TWENTIETH owned
per machine-derive (engine_owner==bm-a rows 19 + candidate). First free
number after the registered W80 row (bm-c r364 freeze, landed origin).
Seat published=reserved MSG-20261002-12xx-bma PUSHED to origin BEFORE
this freeze per r565 early-visibility law.

Bands (r535 machine-derive law; live-registry derived):
  A 205_004..207_003 = W80 A tail (205_003 + 1) + 2_000 width
     -> arithmetic continuation, expected CLEAN
  B arithmetic 53_801..54_000 REFUSED at SEED_REGISTRY point 54_000
     (band UPPER-EDGE endpoint hit, same family as W74-B 52_000 /
     W80-row W81+ projection) -> first clean window 54_001..54_200
     (hit+1 restart; edge-endpoint family => both readings converge,
     no fork face -- W74 precedent, unlike W63 mid-band dual hits)

Machine-verified against: all 79 registered N1 wave bands W2..W80,
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points,
N2-W15 draft probe points, lfc actual draw, options_wave2 actual draw.

r574 bm-a freeze-window run. READ-ONLY against the 79-row table + origin
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
W81_A = (205_004, 207_003)              # arithmetic continuation, W80 A tail +1
W81_B = (54_001, 54_200)                # hit+1 restart past SEED_REGISTRY 54_000

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

# --- leg 0: registry shape (79 registered rows, NO W81 locally yet) --------
base_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 81))
assert sorted(N1_BANDS) == base_rows, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 79 registered rows W2..W14, W16..W80)"
assert 80 in N1_BANDS and N1_BANDS[80]["engine_owner"] == "bm-c", \
    "leg0 failed: W80 (bm-c r364) table-tail row must be present"
assert 79 in N1_BANDS and N1_BANDS[79]["engine_owner"] == "bm-b", \
    "leg0 failed: W79 (bm-b r573) row must be present"
assert N1_BANDS[80]["a"] == (203_004, 205_003) and \
    N1_BANDS[80]["b_exit"] == (53_601, 53_800), \
    "leg0 failed: W80 band drift vs canon row (bm-c r364)"
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(bma_rows) == 19, f"leg0 failed: bm-a rows {bma_rows} (expect 19)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W80 bm-c (r364), "
      f"candidate W81 not local, bm-a rows={len(bma_rows)}")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[80]["a"][1] + 1, N1_BANDS[80]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[80]["b_exit"][1] + 1,
           N1_BANDS[80]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (205_004, 207_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (53_801, 54_000), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts {a_hits} {a_band_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero hits -- no skip)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
b_hit_keys = sorted(k for k, v in science_gates.SEED_REGISTRY.items()
                    if isinstance(v, int) and ARITH_B[0] <= v <= ARITH_B[1])
assert b_hits == [54_000] and b_band_hits == [], \
    f"leg1-B failed: arithmetic position must be REFUSED exactly at [54_000], " \
    f"got {b_hits} {b_band_hits}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED at "
      f"{b_hits} (SEED_REGISTRY {b_hit_keys} upper-edge endpoint -- "
      "W74-B 52_000 edge family; forced skip, not a free choice, R250)")

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
assert first_a == W81_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W81_A}"
first_b = clean(54_000 + 1, WIDTH_B)   # hit+1 restart (edge-endpoint family)
assert first_b == W81_B, \
    f"leg2-B failed: hit+1 first clean window {first_b} != candidate {W81_B}"
# fork-face disclosure: window-step chain reading from 54_001 also lands on
# the same window (both readings converge at the edge endpoint -- W74 family)
alt_b = clean(54_001, WIDTH_B)
assert alt_b == first_b, "leg2-B fork: the two readings must converge (W74 law)"
print(f"leg2: A first-clean == arithmetic == candidate {W81_A[0]}..{W81_A[1]}; "
      f"B hit+1 first-clean {first_b[0]}..{first_b[1]} == candidate "
      "== window-step reading (BOTH READINGS CONVERGE at edge endpoint "
      "54_000 -- no fork face, W74-B precedent family, F-20261002-03 n/a)")
assert not overlaps(W81_A, W81_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W81_A), ("B", W81_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W81-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W81-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W81-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W81-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W81-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W81-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W81-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W81-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W81 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "81: {\"a\": (205_004" not in out, \
    "leg3 failed: a W81 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W81"' not in outn1, \
    "leg3 failed: a W81 WAVE_CONFIGS entry ALREADY exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W81 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W81 ADMIT: A {W81_A[0]}..{W81_A[1]} (arithmetic continuation zero "
      f"skip) + B {W81_B[0]}..{W81_B[1]} (hit+1 forced skip at 54_000 "
      "edge-endpoint family, both readings converge) -- clean vs the "
      f"{len(N1_BANDS)} registered rows + N3-R1 used-seed band + "
      "probe-seed cluster + registry values + probes/actuals -- "
      "engine_owner=bm-a (seat published=reserved MSG-20261002-125x-bma "
      "PUSHED to origin before this freeze, r565 early-visibility law).")

# --- W82+ projection (warning text for the law table row) --------------------
w82_a = (W81_A[1] + 1, W81_A[1] + WIDTH_A)
w82_b = (W81_B[1] + 1, W81_B[1] + WIDTH_B)
a_hits82 = sorted(p for p in points if w82_a[0] <= p <= w82_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w82_a)]
b_hits82 = sorted(p for p in points if w82_b[0] <= p <= w82_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w82_b)]
print(f"W82+ projection: A arithmetic +2_000 = {w82_a[0]}..{w82_a[1]} "
      f"-> {'CLEAN (verify at W82 prereg)' if not a_hits82 else 'REFUSED ' + str(a_hits82)}; "
      f"B +200 from W81 end = {w82_b[0]}..{w82_b[1]} "
      f"-> {'CLEAN (verify at W82 prereg)' if not b_hits82 else 'REFUSED ' + str(b_hits82)}")
