# -*- coding: utf-8 -*-
"""W86 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W86 candidate = first FREE number skipping the bm-b-declared W85 seat
(published=reserved r518-1, MSG-20261002-1258-bmb, W49/W55/W65 family).
DUAL-STATE gate (bm-b W85 registration may land mid-window):
  state A (W85 unregistered, 82 rows tail=W84): arithmetic positions from
    the W84 tail are REFUSED by the W85 PUBLISHED projection bands
    (reserved face) -> skip-past-published windows.
  state B (W85 registered, 83 rows tail=W85): W86 = arithmetic
    continuation from the registered W85 tail.
Both states converge on the same final bands:
  A 215_004..217_003 (W85 A end 215_003 + 1, width 2_000, CLEAN)
  B 55_201..55_400   (W85 B end 55_200 + 1, width 200, CLEAN;
     both sides arithmetic zero-refusal = single-reading, no fork face,
     F-20261002-03 not triggered, D-20261002-05 pin not triggered)

Machine-verified against: all registered N1 wave bands (W2..W84 [+W85 in
state B]), the W85 published projection (state A), N3-R1 used-seed band
70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster 95_000..95_003
(r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
probe points, N2-W15 draft probe points, lfc/options actual draws.

r576 bm-a freeze-window run. READ-ONLY vs the live table + origin.
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

W86_A = (215_004, 217_003)
W86_B = (55_201, 55_400)
W85_PUB_A = (213_004, 215_003)   # bm-b seat MSG-20261002-1258-bmb
W85_PUB_B = (55_001, 55_200)
W84_TAIL_A = (211_004, 213_003)  # registered W84 (bm-a r575, table tail state A)
W84_TAIL_B = (54_601, 54_800)

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
    or keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 86)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
STATE_B = 85 in N1_BANDS
if STATE_B:
    assert N1_BANDS[85]["a"] == W85_PUB_A and \
        N1_BANDS[85]["b_exit"] == W85_PUB_B, \
        "leg0 failed: registered W85 != published seat bands (drift)"
    assert N1_BANDS[85].get("engine_owner") == "bm-b", "W85 owner drift"
    bands.append(W85_PUB_A); bands.append(W85_PUB_B)
    MODE = "B (W85 registered -- arithmetic continuation from W85 tail)"
else:
    bands.append(W85_PUB_A); bands.append(W85_PUB_B)
    MODE = "A (W85 seat-published, unregistered -- skip-past-published face)"
assert N1_BANDS[84]["a"] == W84_TAIL_A and \
    N1_BANDS[84]["b_exit"] == W84_TAIL_B and \
    N1_BANDS[84].get("engine_owner") == "bm-a", "leg0 failed: W84 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(bma_rows) == 21, f"leg0 failed: bm-a rows {len(bma_rows)} (expect 21)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} (+bm-b W85 seat in flight in "
      f"state A) + candidate; bm-a rows={len(bma_rows)} -> W86 = bm-a 22nd owned")

# --- leg 0b: bm-b W85 seat MSG on origin (published=reserved face) ------------
# r575/r576 closeout move: seat MSG may be archived to inbox/processed/ --
# accept either live or processed location (bm-b r576 gate leg0b patch law).
seat = None
for _p in ("fleet/inbox/MSG-20261002-1258-bmb-w85-seat.md",
           "fleet/inbox/processed/MSG-20261002-1258-bmb-w85-seat.md"):
    _r = subprocess.run(["git", "show", f"origin/main:{_p}"],
                        capture_output=True, creationflags=CREAT)
    if _r.returncode == 0:
        seat = _r.stdout.decode("utf-8")
        break
assert seat is not None, "leg0b failed: bm-b W85 seat MSG not on origin (either path)"
assert "A-ext seed=213_004..215_003" in seat and \
    "B-ext exit seed=55_001..55_200" in seat, \
    "leg0b failed: bm-b W85 seat MSG bands not found on origin (r518-1 face)"
assert "215_004..217_003" in seat and "55_201..55_400" in seat, \
    "leg0b failed: seat MSG W86+ projection disclosure missing"
print("leg0b: bm-b W85 seat MSG verified on origin (published=reserved r518-1); "
      "its W86+ projection prose matches this gate's machine derivation")

# --- leg 1: arithmetic positions vs reserved universe (mode-aware) -----------
if STATE_B:
    tail = N1_BANDS[85]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W86_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == W86_B, f"leg1-B drift: {ARITH_B}"
else:
    tail = N1_BANDS[84]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W85_PUB_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == (54_801, 55_000), f"leg1-B drift: {ARITH_B}"
    a_ref = [b for b in bands if overlaps(b, ARITH_A) and b != W85_PUB_A] or \
        [f"point {p}" for p in points if ARITH_A[0] <= p <= ARITH_A[1]]
    assert [b for b in bands if overlaps(b, ARITH_A)] == [W85_PUB_A] and not a_ref, \
        f"leg1-A failed: arithmetic position must be refused ONLY by the W85 " \
        f"published band, got {a_ref}"
    b_ref = [b for b in bands if overlaps(b, ARITH_B) and b != W85_PUB_B] or \
        [f"point {p}" for p in points if ARITH_B[0] <= p <= ARITH_B[1]]
    # B side: arithmetic window hits the SEED_REGISTRY point FIRST (not the
    # W85 published band) -> hit+1 restart (D-20261002-05 pin), the restart
    # window is then the W85 published band itself (reserved face).
    assert [p for p in points if ARITH_B[0] <= p <= ARITH_B[1]] == [55_000], \
        f"leg1-B failed: expect exactly [55_000] point refusal, got {b_ref}"
    reg55 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 55_000]
    assert reg55 and not [b for b in bands if overlaps(b, ARITH_B)], \
        "leg1-B failed: B arithmetic window must be refused by the 55_000 " \
        f"point only, got band hits {[b for b in bands if overlaps(b, ARITH_B)]}"
    print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} REFUSED by W85 published "
          f"projection (reserved face r518-1) -> skip-past-published")
    print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED at SEED_REGISTRY "
          f"{reg55[0]}=55_000 upper-edge endpoint (edge-endpoint family W74-B/W81; "
          f"both readings converge -> hit+1 restart)")
    ARITH_A2 = (W85_PUB_A[1] + 1, W85_PUB_A[1] + WIDTH_A)
    ARITH_B2 = (55_001, 55_200)   # hit+1 restart window == W85 published band
    assert ARITH_A2 == W86_A, f"leg1-A2 drift: {ARITH_A2}"
    assert ARITH_B2 == W85_PUB_B, f"leg1-B2 drift: {ARITH_B2}"
    a_hits = sorted(p for p in points if ARITH_A2[0] <= p <= ARITH_A2[1])
    a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A2)]
    assert not a_hits and not a_band_hits, f"leg1-A2 failed: {a_hits} {a_band_hits}"
    print(f"leg1-A2 skip-past-published {ARITH_A2[0]}..{ARITH_A2[1]} CLEAN")
    # B2 (55_001..55_200) is the W85 published band: assert it is refused by
    # exactly that band (reserved face) and nothing else, then skip past it.
    b2_band_hits = [b for b in bands if overlaps(b, ARITH_B2)]
    assert b2_band_hits == [W85_PUB_B], \
        f"leg1-B2 failed: restart window must collide ONLY with the W85 " \
        f"published band, got {b2_band_hits}"
    b2_extra_hits = [p for p in points if ARITH_B2[0] <= p <= ARITH_B2[1]]
    assert not b2_extra_hits, f"leg1-B2 failed: extra point hits {b2_extra_hits}"
    print(f"leg1-B2 restart window {ARITH_B2[0]}..{ARITH_B2[1]} REFUSED by W85 "
          f"published projection (reserved face r518-1) -> skip-past-published")
    ARITH_B3 = (W85_PUB_B[1] + 1, W85_PUB_B[1] + WIDTH_B)
    assert ARITH_B3 == W86_B, f"leg1-B3 drift: {ARITH_B3}"
    b3_hits = sorted(p for p in points if ARITH_B3[0] <= p <= ARITH_B3[1])
    b3_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B3)]
    assert not b3_hits and not b3_band_hits, \
        f"leg1-B3 failed: {b3_hits} {b3_band_hits}"
    print(f"leg1-B3 skip-past-published {ARITH_B3[0]}..{ARITH_B3[1]} CLEAN "
          f"(zero refusal points, single reading)")

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

start_a = (W85_PUB_A[1] + 1)
first_a = clean(start_a, WIDTH_A)
assert first_a == W86_A, f"leg2-A failed: {first_a} != {W86_A}"
start_b = (W85_PUB_B[1] + 1)
first_b = None
lo = start_b
while first_b is None and lo < start_b + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W86_B, f"leg2-B failed: {first_b} != {W86_B} (scan-forward hit+1)"
print(f"leg2: A first-clean {W86_A[0]}..{W86_A[1]} == candidate; "
      f"B first-clean {W86_B[0]}..{W86_B[1]} == candidate (zero-skip arithmetic)")
assert not overlaps(W86_A, W86_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W86_A), ("B", W86_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W86-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W86-{tag}")
    if overlaps(W85_PUB_A, band) or (tag == "A" and overlaps(band, W85_PUB_A)):
        conflicts.append(f"W85 published A x W86-{tag}")
    if tag == "B" and overlaps(band, W85_PUB_B):
        conflicts.append(f"W85 published B x W86-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W86-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W86-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W86-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W86-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W86-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W86-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "86: {\"a\": (215_004" not in out, \
    "leg3 failed: W86 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W86"' not in outn1, \
    "leg3 failed: W86 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W86_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: W86 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W86 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W86 ADMIT: A {W86_A[0]}..{W86_A[1]} + B {W86_B[0]}..{W86_B[1]} "
      f"(mode={MODE}; refusal facts: W85 published bands [state A] only -- "
      "zero band hits, zero registry points, zero probe hits) -- clean vs all "
      f"registered rows + W85 reserved face + registry + probes/actuals -- "
      "engine_owner=bm-a (seat published=reserved to be pushed BEFORE this "
      "freeze per r565 early-visibility law). NOT a re-pick (R250: W86 bands "
      "were never assigned).")

# --- W87+ projection (warning text for the law table row) --------------------
w87_a = (W86_A[1] + 1, W86_A[1] + WIDTH_A)
w87_b = (W86_B[1] + 1, W86_B[1] + WIDTH_B)
a_hits87 = sorted(p for p in points if w87_a[0] <= p <= w87_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w87_a)]
b_hits87 = sorted(p for p in points if w87_b[0] <= p <= w87_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w87_b)]
print(f"W87+ projection: A arithmetic +2_000 = {w87_a[0]}..{w87_a[1]} "
      f"-> {'CLEAN (verify at W87 prereg)' if not a_hits87 else 'REFUSED ' + str(a_hits87)}; "
      f"B +200 from W86 end = {w87_b[0]}..{w87_b[1]} "
      f"-> {'CLEAN (verify at W87 prereg)' if not b_hits87 else 'REFUSED ' + str(b_hits87)}")
