# -*- coding: utf-8 -*-
"""W93 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W93 candidate = first FREE number after the registered W92 row (bm-c r370,
table tail). NO peer W93 seat MSG on origin (checked leg0b). SINGLE STATE:
W91 bm-b + W92 bm-c both registered (zero published-but-unregistered seats
in flight).

Bands (machine-derived, NOT transcribed -- r335/r535 law; the bm-c W92
freeze commit's W93+ projection prose is a hint only, re-derived here):
  A 229_004..231_003  arithmetic continuation from W92 A end 229_003 + 1,
                      width 2_000, CLEAN (machine-verified).
  B 57_101..57_300    DOUBLE MEDIAN-HIT PIN CHAIN per D-20261002-05:
                      arithmetic 56_901..57_100 REFUSED in-band at
                      SEED_REGISTRY xstock_tilt_h20=57_000 (position 99/199
                      = median, non-endpoint; xstock_tilt_h10=57_100 at the
                      upper-edge endpoint 199) -> past-hit restart
                      57_001..57_200 -> REFUSED again in-band at
                      xstock_tilt_h10=57_100 (position 99/199 = median,
                      non-endpoint) -> past-hit restart 57_101..57_300
                      CLEAN. BOTH READINGS CONVERGE at 57_101 (chained-skip
                      from the first window start 56_901 + 200 = 57_101;
                      past-hit from the second hit 57_100 + 1 = 57_101) --
                      zero fork face, W74-B/W81-B edge-convergent family.

Machine-verified against: all registered N1 wave bands (W2..W92), N3-R1
used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options actuals.

r580 bm-a freeze-window run. READ-ONLY vs the live table + origin.
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

W93_A = (229_004, 231_003)
W93_B = (57_101, 57_300)
W92_TAIL_A = (227_004, 229_003)   # registered W92 (bm-c r370, table tail)
W92_TAIL_B = (56_701, 56_900)

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

# --- leg 0: registry shape (single state: W92 registered tail) ----------------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 93)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[92]["a"] == W92_TAIL_A and \
    N1_BANDS[92]["b_exit"] == W92_TAIL_B and \
    N1_BANDS[92].get("engine_owner") == "bm-c", "leg0 failed: W92 row drift"
assert 91 in N1_BANDS and N1_BANDS[91].get("engine_owner") == "bm-b", \
    "leg0 failed: W91 row/owner drift"
assert 90 in N1_BANDS and N1_BANDS[90].get("engine_owner") == "bm-a", \
    "leg0 failed: W90 row/owner drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 82, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 82)"
assert len(bma_rows) == 24, f"leg0 failed: bm-a rows {len(bma_rows)} (expect 24)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W92 bm-c r370); "
      f"engine_owner rows={len(owner_rows)} + candidate; bm-a rows={len(bma_rows)} "
      f"-> W93 = bm-a 25th owned, EIGHTY-THIRD engine wave by machine-derive")

# --- leg 0b: NO peer W93 seat claim on origin (vacancy of seat MSGs) ----------
seat_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w93" in _ln.lower():
            seat_claims.append(_pfx + _ln)
assert not seat_claims, f"leg0b failed: peer W93 seat MSG on origin: {seat_claims}"
print("leg0b: zero W93 seat MSGs on origin (inbox+processed scanned) -- "
      "W93 vacancy confirmed; own seat MSG to be pushed BEFORE this freeze "
      "(r565 early-visibility law)")

# --- leg 1: arithmetic positions vs reserved universe -------------------------
tail = N1_BANDS[92]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == (229_004, 231_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (56_901, 57_100), f"leg1-B drift: {ARITH_B}"
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
a_pt_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert not a_band_hits and not a_pt_hits, \
    f"leg1-A failed: arithmetic window not clean: {a_band_hits} {a_pt_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero band/point hits)")
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
b_pt_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert not b_band_hits, f"leg1-B failed: band hits {b_band_hits}"
assert b_pt_hits == [57_000, 57_100], \
    f"leg1-B failed: expect exactly [57_000, 57_100] point refusal, got {b_pt_hits}"
reg57 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 57_000]
reg57b = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 57_100]
assert reg57 == ["xstock_tilt_h20"], f"leg1-B failed: 57_000 key {reg57}"
assert reg57b == ["xstock_tilt_h10"], f"leg1-B failed: 57_100 key {reg57b}"
# median non-endpoint check for the FIRST hit (position 99 of 200-wide window)
assert ARITH_B[0] < 57_000 < ARITH_B[1], "leg1-B: first hit must be in-band non-endpoint"
assert 57_100 == ARITH_B[1], "leg1-B: second hit at the upper-edge endpoint (edge family)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED in-band at "
      f"SEED_REGISTRY xstock_tilt_h20=57_000 (median position 99/199, non-endpoint; "
      f"xstock_tilt_h10=57_100 at the upper-edge endpoint 199) -> D-20261002-05 "
      f"pin: PAST-HIT start-window hit+1")
# second window of the pin chain
R1_B = (57_000 + 1, 57_000 + WIDTH_B)
assert R1_B == (57_001, 57_200), f"leg1-B2 drift: {R1_B}"
r1_band = [b for b in bands + actual if overlaps(b, R1_B)]
r1_pt = sorted(p for p in points if R1_B[0] <= p <= R1_B[1])
assert not r1_band, f"leg1-B2 failed: band hits {r1_band}"
assert r1_pt == [57_100], \
    f"leg1-B2 failed: expect exactly [57_100] in the restart window, got {r1_pt}"
assert R1_B[0] < 57_100 < R1_B[1], "leg1-B2: hit must be in-band non-endpoint (median)"
print(f"leg1-B2 past-hit restart {R1_B[0]}..{R1_B[1]} REFUSED again in-band at "
      f"xstock_tilt_h10=57_100 (median position 99/199, non-endpoint) -> "
      f"D-20261002-05 pin chain second step")
R2_B = (57_100 + 1, 57_100 + WIDTH_B)
assert R2_B == W93_B, f"leg1-B3 drift: {R2_B}"
r2_band = [b for b in bands + actual if overlaps(b, R2_B)]
r2_pt = sorted(p for p in points if R2_B[0] <= p <= R2_B[1])
assert not r2_band and not r2_pt, \
    f"leg1-B3 failed: second restart window not clean: {r2_band} {r2_pt}"
print(f"leg1-B3 past-hit restart {R2_B[0]}..{R2_B[1]} CLEAN "
      f"(BOTH READINGS CONVERGE at 57_101: chained-skip 56_901+200 == "
      f"past-hit 57_100+1 -- zero fork face, W74-B/W81-B edge-convergent family)")

# --- leg 2: first clean window == candidate (scan-forward, hit+1 law) ---------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first_a = clean(W92_TAIL_A[1] + 1, WIDTH_A)
assert first_a == W93_A, f"leg2-A failed: {first_a} != {W93_A}"
start_b = W92_TAIL_B[1] + 1
first_b = None
lo = start_b
while first_b is None and lo < start_b + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W93_B, f"leg2-B failed: {first_b} != {W93_B} (scan-forward hit+1)"
print(f"leg2: A first-clean {W93_A[0]}..{W93_A[1]} == candidate; "
      f"B first-clean {W93_B[0]}..{W93_B[1]} == candidate (hit+1 scan law)")
assert not overlaps(W93_A, W93_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W93_A), ("B", W93_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W93-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W93-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W93-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W93-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W93-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W93-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W93-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W93-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "93: {\"a\": (229_004" not in out, \
    "leg3 failed: W93 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W93"' not in outn1, \
    "leg3 failed: W93 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W93_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: W93 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | single-state (W92 tail)")
if conflicts:
    print("W93 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W93 ADMIT: A {W93_A[0]}..{W93_A[1]} + B {W93_B[0]}..{W93_B[1]} "
      f"(refusal facts: B double median-hit pin chain -- arithmetic "
      f"56_901..57_100 refused at xstock_tilt_h20=57_000 median + "
      f"xstock_tilt_h10=57_100 endpoint; restart 57_001..57_200 refused at "
      f"57_100 median; second restart 57_101..57_300 CLEAN, both readings "
      f"converge -- zero fork face) -- clean vs all registered rows "
      f"+ registry + probes/actuals -- engine_owner=bm-a (seat MSG to be "
      f"pushed BEFORE this freeze per r565). NOT a re-pick (R250: W93 bands "
      f"were never assigned).")

# --- W94+ projection (warning text for the law table row) --------------------
w94_a = (W93_A[1] + 1, W93_A[1] + WIDTH_A)
w94_b = (W93_B[1] + 1, W93_B[1] + WIDTH_B)
a_hits94 = sorted(p for p in points if w94_a[0] <= p <= w94_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w94_a)]
b_hits94 = sorted(p for p in points if w94_b[0] <= p <= w94_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w94_b)]
print(f"W94+ projection: A arithmetic +2_000 = {w94_a[0]}..{w94_a[1]} "
      f"-> {'CLEAN (verify at W94 prereg)' if not a_hits94 else 'REFUSED ' + str(a_hits94)}; "
      f"B +200 from W93 end = {w94_b[0]}..{w94_b[1]} "
      f"-> {'CLEAN (verify at W94 prereg)' if not b_hits94 else 'REFUSED ' + str(b_hits94)}")
