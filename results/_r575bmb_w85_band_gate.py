# -*- coding: utf-8 -*-
"""W85 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W85 candidate = first FREE number skipping the bm-a-declared W84 seat
(published=reserved r518-1, MSG-20261002-1245-bma, W49/W55/W65 family).
DUAL-STATE gate (bm-a W84 registration may land mid-window):
  state A (W84 unregistered, 81 rows): arithmetic positions from the W83
    tail are REFUSED by the W84 PUBLISHED projection bands (reserved face)
    -> skip-past-published windows.
  state B (W84 registered, 82 rows): W85 = arithmetic continuation from
    the registered W84 tail.
Both states converge on the same final bands:
  A 213_004..215_003 (W84 A end 213_003 + 1, width 2_000, CLEAN)
  B 55_001..55_200   (arithmetic 54_801..55_000 REFUSED at SEED_REGISTRY
     a158_truegap_ic=55_000 upper-edge endpoint -> hit+1 restart, both
     readings converge = no fork face, W74-B/W81 edge-endpoint family)

Machine-verified against: all registered N1 wave bands (W2..W83 [+W84 in
state B]), the W84 published projection (state A), N3-R1 used-seed band
70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster 95_000..95_003
(r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
probe points, N2-W15 draft probe points, lfc/options actual draws.

r575 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W85_A = (213_004, 215_003)
W85_B = (55_001, 55_200)
W84_PUB_A = (211_004, 213_003)   # bm-a seat MSG-20261002-1245-bma
W84_PUB_B = (54_601, 54_800)

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

# --- leg 0: registry shape + dual-state mode detection -----------------------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 85)) \
    or keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 84)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
STATE_B = 84 in N1_BANDS
if STATE_B:
    assert N1_BANDS[84]["a"] == W84_PUB_A and \
        N1_BANDS[84]["b_exit"] == W84_PUB_B, \
        "leg0 failed: registered W84 != published seat bands (drift)"
    assert N1_BANDS[84].get("engine_owner") == "bm-a", "W84 owner drift"
    bands.append(W84_PUB_A); bands.append(W84_PUB_B)
    MODE = "B (W84 registered -- arithmetic continuation from W84 tail)"
else:
    bands.append(W84_PUB_A); bands.append(W84_PUB_B)
    MODE = "A (W84 seat-published, unregistered -- skip-past-published face)"
assert N1_BANDS[83]["a"] == (209_004, 211_003) and \
    N1_BANDS[83]["b_exit"] == (54_401, 54_600) and \
    N1_BANDS[83].get("engine_owner") == "bm-c", "leg0 failed: W83 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(bmb_rows) == 27, f"leg0 failed: bm-b rows {len(bmb_rows)} (expect 27)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} (+bm-a W84 seat in flight in "
      f"state A) + candidate; bm-b rows={len(bmb_rows)} -> W85 = bm-b 28th owned")

# --- leg 0b: bm-a W84 seat MSG on origin (published=reserved face) ------------
# r576 patch: bm-a archived its seat MSG to processed/ after consumption
# (r365/r575 closeouts) -- accept EITHER path (same origin object,
# archive move disclosed in the r576 receipt).
_seat_paths = ["fleet/inbox/MSG-20261002-1245-bma-w84-seat.md",
               "fleet/inbox/processed/MSG-20261002-1245-bma-w84-seat.md"]
seat = None
for _sp in _seat_paths:
    _r = subprocess.run(["git", "show", f"origin/main:{_sp}"],
                        capture_output=True)
    if _r.returncode == 0:
        seat = _r.stdout.decode("utf-8")
        break
assert seat is not None, \
    "leg0b failed: bm-a W84 seat MSG not found on origin (inbox or processed)"
assert "A-ext seed=211_004..213_003" in seat and \
    "B-ext exit seed=54_601..54_800" in seat, \
    "leg0b failed: bm-a W84 seat MSG bands not found on origin (r518-1 face)"
assert "55_000" in seat and "55_001..55_200" in seat, \
    "leg0b failed: seat MSG W85+ B-side endpoint disclosure missing"
print("leg0b: bm-a W84 seat MSG verified on origin (published=reserved r518-1); "
      "its W85+ projection prose matches this gate's machine derivation")

# --- leg 1: arithmetic positions vs reserved universe (mode-aware) -----------
if STATE_B:
    tail = N1_BANDS[84]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W85_A, f"leg1-A drift: {ARITH_A}"
else:
    tail = N1_BANDS[83]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W84_PUB_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == W84_PUB_B, f"leg1-B drift: {ARITH_B}"
    a_ref = [b for b in bands if overlaps(b, ARITH_A) and b != W84_PUB_A] or \
        [f"point {p}" for p in points if ARITH_A[0] <= p <= ARITH_A[1]]
    assert [b for b in bands if overlaps(b, ARITH_A)] == [W84_PUB_A] and not a_ref, \
        f"leg1-A failed: arithmetic position must be refused ONLY by the W84 " \
        f"published band, got {a_ref}"
    b_ref = [b for b in bands if overlaps(b, ARITH_B) and b != W84_PUB_B] or \
        [f"point {p}" for p in points if ARITH_B[0] <= p <= ARITH_B[1]]
    assert [b for b in bands if overlaps(b, ARITH_B)] == [W84_PUB_B] and not b_ref, \
        f"leg1-B failed: arithmetic position must be refused ONLY by the W84 " \
        f"published band, got {b_ref}"
    print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} REFUSED by W84 published "
          f"projection (reserved face r518-1) -> skip-past-published")
    print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED by W84 published "
          f"projection (reserved face r518-1) -> skip-past-published")
    ARITH_A2 = (W84_PUB_A[1] + 1, W84_PUB_A[1] + WIDTH_A)
    ARITH_B2 = (W84_PUB_B[1] + 1, W84_PUB_B[1] + WIDTH_B)
    assert ARITH_A2 == W85_A, f"leg1-A2 drift: {ARITH_A2}"
    assert ARITH_B2 == (54_801, 55_000), f"leg1-B2 drift: {ARITH_B2}"
    a_hits = sorted(p for p in points if ARITH_A2[0] <= p <= ARITH_A2[1])
    a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A2)]
    assert not a_hits and not a_band_hits, f"leg1-A2 failed: {a_hits} {a_band_hits}"
    print(f"leg1-A2 skip-past-published {ARITH_A2[0]}..{ARITH_A2[1]} CLEAN")
    b2_hits = sorted(p for p in points if ARITH_B2[0] <= p <= ARITH_B2[1])
    b2_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B2)]
    assert b2_hits == [55_000] and not b2_band_hits, \
        f"leg1-B2 failed: expect exactly [55_000] refusal, got {b2_hits} {b2_band_hits}"
    reg55 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 55_000]
    assert reg55, "leg1-B2 failed: 55_000 not in SEED_REGISTRY"
    print(f"leg1-B2 window {ARITH_B2[0]}..{ARITH_B2[1]} REFUSED at upper-edge "
          f"endpoint SEED_REGISTRY {reg55[0]}=55_000 (edge-endpoint family "
          f"W74-B/W81; both readings converge -> hit+1 restart, no fork face)")

# --- leg 2: first clean window == candidate (both sides) ---------------------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

start_a = (W84_PUB_A[1] + 1)
first_a = clean(start_a, WIDTH_A)
assert first_a == W85_A, f"leg2-A failed: {first_a} != {W85_A}"
start_b = (W84_PUB_B[1] + 1)
first_b = None
lo = start_b
while first_b is None and lo < start_b + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W85_B, f"leg2-B failed: {first_b} != {W85_B} (scan-forward hit+1)"
print(f"leg2: A first-clean {W85_A[0]}..{W85_A[1]} == candidate; "
      f"B first-clean {W85_B[0]}..{W85_B[1]} == candidate (hit+1 restart chain)")
assert not overlaps(W85_A, W85_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W85_A), ("B", W85_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W85-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W85-{tag}")
    if overlaps(W84_PUB_A, band) or (tag == "A" and overlaps(band, W84_PUB_A)):
        conflicts.append(f"W84 published A x W85-{tag}")
    if tag == "B" and overlaps(band, W84_PUB_B):
        conflicts.append(f"W84 published B x W85-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W85-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W85-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W85-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W85-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W85-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W85-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "85: {\"a\": (213_004" not in out, \
    "leg3 failed: W85 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W85"' not in outn1, \
    "leg3 failed: W85 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W85_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: W85 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W85 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W85 ADMIT: A {W85_A[0]}..{W85_A[1]} + B {W85_B[0]}..{W85_B[1]} "
      f"(mode={MODE}; refusal facts: W84 published bands [state A] + "
      "SEED_REGISTRY a158_truegap_ic=55_000 edge endpoint) -- clean vs all "
      f"registered rows + W84 reserved face + registry + probes/actuals -- "
      "engine_owner=bm-b (seat published=reserved to be pushed BEFORE this "
      "freeze per r565 early-visibility law). NOT a re-pick (R250: W85 bands "
      "were never assigned).")

# --- W86+ projection (warning text for the law table row) --------------------
w86_a = (W85_A[1] + 1, W85_A[1] + WIDTH_A)
w86_b = (W85_B[1] + 1, W85_B[1] + WIDTH_B)
a_hits86 = sorted(p for p in points if w86_a[0] <= p <= w86_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w86_a)]
b_hits86 = sorted(p for p in points if w86_b[0] <= p <= w86_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w86_b)]
print(f"W86+ projection: A arithmetic +2_000 = {w86_a[0]}..{w86_a[1]} "
      f"-> {'CLEAN (verify at W86 prereg)' if not a_hits86 else 'REFUSED ' + str(a_hits86)}; "
      f"B +200 from W85 end = {w86_b[0]}..{w86_b[1]} "
      f"-> {'CLEAN (verify at W86 prereg)' if not b_hits86 else 'REFUSED ' + str(b_hits86)}")
