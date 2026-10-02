# -*- coding: utf-8 -*-
"""W88 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W88 candidate = first FREE number skipping the bm-a-declared W87 seat
(published=reserved r518-1, MSG-20261002-1345-bma-w87-seat, W49/W55/W65
family). DUAL-STATE gate (bm-a W87 registration may land mid-window):
  state A (W87 unregistered, 85 rows): arithmetic positions from the W86
    tail are REFUSED by the W87 PUBLISHED projection bands (reserved face)
    -- the B-side arithmetic 55_401..55_600 is doubly refused (overlaps
    the W87 published B band AND carries the in-window SEED_REGISTRY
    grid_p1=55_000 median hit per the W86 row W87+ disclosure) -> both
    readings converge on skip-past-published (D-20261002-05 pin chain:
    55_500 hit+1 restart 55_501..55_700 == the W87 published band, then
    skip-past-published).
  state B (W87 registered, 86 rows): W88 = arithmetic continuation from
    the registered W87 tail.
Both states converge on the same final bands:
  A 219_004..221_003 (W87 A end 219_003 + 1, width 2_000, CLEAN)
  B 55_701..55_900   (W87 B end 55_700 + 1, width 200, CLEAN)

Machine-verified against: all registered N1 wave bands (W2..W86 [+W87 in
state B]), the W87 published projection (state A), N3-R1 used-seed band
70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster 95_000..95_003
(r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
probe points, N2-W15 draft probe points, lfc/options actual draws.

r577 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W88_A = (219_004, 221_003)
W88_B = (55_701, 55_900)
W87_PUB_A = (217_004, 219_003)   # bm-a seat MSG-20261002-1345-bma-w87-seat
W87_PUB_B = (55_501, 55_700)

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
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 87)) \
    or keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 88)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
STATE_B = 87 in N1_BANDS
if STATE_B:
    assert N1_BANDS[87]["a"] == W87_PUB_A and \
        N1_BANDS[87]["b_exit"] == W87_PUB_B, \
        "leg0 failed: registered W87 != published seat bands (drift)"
    assert N1_BANDS[87].get("engine_owner") == "bm-a", "W87 owner drift"
    bands.append(W87_PUB_A); bands.append(W87_PUB_B)
    MODE = "B (W87 registered -- arithmetic continuation from W87 tail)"
else:
    bands.append(W87_PUB_A); bands.append(W87_PUB_B)
    MODE = "A (W87 seat-published, unregistered -- skip-past-published face)"
assert N1_BANDS[86]["a"] == (215_004, 217_003) and \
    N1_BANDS[86]["b_exit"] == (55_201, 55_400) and \
    N1_BANDS[86].get("engine_owner") == "bm-a", "leg0 failed: W86 row drift"
assert N1_BANDS[85]["a"] == (213_004, 215_003) and \
    N1_BANDS[85]["b_exit"] == (55_001, 55_200) and \
    N1_BANDS[85].get("engine_owner") == "bm-b", "leg0 failed: W85 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(bmb_rows) == 28, f"leg0 failed: bm-b rows {len(bmb_rows)} (expect 28)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} (+bm-a W87 seat in flight in "
      f"state A) + candidate; bm-b rows={len(bmb_rows)} -> W88 = bm-b 29th owned")

# --- leg 0b: bm-a W87 seat MSG on origin (published=reserved face) ------------
# archive-move tolerance: the seat MSG may already sit in processed/ if a
# later closeout consumed it (r322 dual-path law).
_seat_paths = ["fleet/inbox/MSG-20261002-1345-bma-w87-seat.md",
               "fleet/inbox/processed/MSG-20261002-1345-bma-w87-seat.md"]
seat = None
for _sp in _seat_paths:
    _r = subprocess.run(["git", "show", f"origin/main:{_sp}"],
                        capture_output=True)
    if _r.returncode == 0:
        seat = _r.stdout.decode("utf-8")
        break
assert seat is not None, \
    "leg0b failed: bm-a W87 seat MSG not found on origin (inbox or processed)"
assert "217_004..219_003" in seat and "55_501..55_700" in seat, \
    "leg0b failed: bm-a W87 seat MSG bands not found on origin (r518-1 face)"
assert "W88" in seat, \
    "leg0b failed: seat MSG W88+ projection disclosure missing"
print("leg0b: bm-a W87 seat MSG verified on origin (published=reserved r518-1); "
      "its W88+ projection prose matches this gate's machine derivation")

# --- leg 1: arithmetic positions vs reserved universe (mode-aware) -----------
if STATE_B:
    tail = N1_BANDS[87]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W88_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == W88_B, f"leg1-B drift: {ARITH_B}"
else:
    tail = N1_BANDS[86]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W87_PUB_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == (55_401, 55_600), f"leg1-B drift: {ARITH_B}"
    a_ref = [b for b in bands if overlaps(b, ARITH_A) and b != W87_PUB_A] or \
        [f"point {p}" for p in points if ARITH_A[0] <= p <= ARITH_A[1]]
    assert [b for b in bands if overlaps(b, ARITH_A)] == [W87_PUB_A] and not a_ref, \
        f"leg1-A failed: arithmetic position must be refused ONLY by the W87 " \
        f"published band, got {a_ref}"
    b_band_ref = [b for b in bands if overlaps(b, ARITH_B)]
    b_point_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
    assert b_band_ref == [W87_PUB_B] and b_point_hits == [55_500], \
        f"leg1-B failed: expect refusal by W87 published band + in-window " \
        f"grid_p1=55_500 median hit, got {b_band_ref} {b_point_hits}"
    reg55 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 55_500]
    assert reg55 == ["grid_p1"], \
        f"leg1-B failed: 55_000 registry key drift: {reg55}"
    print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} REFUSED by W87 published "
          f"projection (reserved face r518-1) -> skip-past-published")
    print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED by W87 published "
          f"B band overlap + SEED_REGISTRY grid_p1=55_500 in-window median hit "
          f"(D-20261002-05 pin: hit+1 restart 55_501..55_700 == the W87 "
          f"published band itself -> skip-past-published; both readings "
          f"converge, no fork face)")
    ARITH_A2 = (W87_PUB_A[1] + 1, W87_PUB_A[1] + WIDTH_A)
    ARITH_B2 = (W87_PUB_B[1] + 1, W87_PUB_B[1] + WIDTH_B)
    assert ARITH_A2 == W88_A, f"leg1-A2 drift: {ARITH_A2}"
    assert ARITH_B2 == W88_B, f"leg1-B2 drift: {ARITH_B2}"
    a_hits = sorted(p for p in points if ARITH_A2[0] <= p <= ARITH_A2[1])
    a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A2)]
    assert not a_hits and not a_band_hits, f"leg1-A2 failed: {a_hits} {a_band_hits}"
    print(f"leg1-A2 skip-past-published {ARITH_A2[0]}..{ARITH_A2[1]} CLEAN")
    b2_hits = sorted(p for p in points if ARITH_B2[0] <= p <= ARITH_B2[1])
    b2_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B2)]
    assert not b2_hits and not b2_band_hits, \
        f"leg1-B2 failed: expect clean window, got {b2_hits} {b2_band_hits}"
    print(f"leg1-B2 skip-past-published {ARITH_B2[0]}..{ARITH_B2[1]} CLEAN")

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

start_a = (W87_PUB_A[1] + 1)
first_a = clean(start_a, WIDTH_A)
assert first_a == W88_A, f"leg2-A failed: {first_a} != {W88_A}"
start_b = (W87_PUB_B[1] + 1)
first_b = None
lo = start_b
while first_b is None and lo < start_b + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W88_B, f"leg2-B failed: {first_b} != {W88_B} (scan-forward hit+1)"
print(f"leg2: A first-clean {W88_A[0]}..{W88_A[1]} == candidate; "
      f"B first-clean {W88_B[0]}..{W88_B[1]} == candidate (hit+1 restart chain)")
assert not overlaps(W88_A, W88_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W88_A), ("B", W88_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W88-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W88-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W88-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W88-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W88-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W88-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W88-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W88-{tag} (r335 leg)")
    if overlaps(W87_PUB_A, band) or overlaps(W87_PUB_B, band):
        conflicts.append(f"W87 published band x W88-{tag}")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "88: {\"a\": (219_004" not in out, \
    "leg3 failed: W88 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W88"' not in outn1, \
    "leg3 failed: W88 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W88_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: W88 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W88 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W88 ADMIT: A {W88_A[0]}..{W88_A[1]} + B {W88_B[0]}..{W88_B[1]} "
      f"(mode={MODE}; refusal facts: W87 published bands [state A] + "
      "SEED_REGISTRY grid_p1=55_500 median hit inside the B arithmetic "
      "window, D-20261002-05 pin) -- clean vs all registered rows + W87 "
      "reserved face + registry + probes/actuals -- engine_owner=bm-b "
      "(seat published=reserved to be pushed BEFORE this freeze per r565 "
      "early-visibility law). NOT a re-pick (R250: W88 bands were never "
      "assigned).")

# --- W89+ projection (warning text for the law table row) --------------------
w89_a = (W88_A[1] + 1, W88_A[1] + WIDTH_A)
w89_b = (W88_B[1] + 1, W88_B[1] + WIDTH_B)
a_hits89 = sorted(p for p in points if w89_a[0] <= p <= w89_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w89_a)]
b_hits89 = sorted(p for p in points if w89_b[0] <= p <= w89_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w89_b)]
print(f"W89+ projection: A arithmetic +2_000 = {w89_a[0]}..{w89_a[1]} "
      f"-> {'CLEAN (verify at W89 prereg)' if not a_hits89 else 'REFUSED ' + str(a_hits89)}; "
      f"B +200 from W88 end = {w89_b[0]}..{w89_b[1]} "
      f"-> {'CLEAN (verify at W89 prereg)' if not b_hits89 else 'REFUSED ' + str(b_hits89)}")
