# -*- coding: utf-8 -*-
"""W87 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W87 candidate = first FREE number after the registered W86 row (bm-a r576,
table tail). NO peer seat MSG on origin for W87 (checked leg0b) and NO
dual-state face this window (W85 AND W86 both registered; no published-but-
unregistered seat in flight).

Bands (machine-derived, NOT transcribed -- r335 law; the r576 W86 gate
projection prose is a hint only, re-derived here):
  A 217_004..219_003  arithmetic continuation from W86 A end 217_003 + 1,
                      width 2_000, CLEAN (expected; machine-verified).
  B 55_501..55_700    arithmetic 55_401..55_600 REFUSED in-band at
                      SEED_REGISTRY grid_p1=55_500 (position 99/199 =
                      median, non-endpoint) -> D-20261002-05 pin:
                      past-hit start-window hit+1 = 55_501..55_700 CLEAN.
                      (Window-step-chain reading 55_601..55_800 is the
                      BANNED fork per the pin; W68-B positive anchor,
                      selftest pf.py leg-9 pin leg.)

Machine-verified against: all registered N1 wave bands (W2..W86), N3-R1
used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options actuals.

r577 bm-a freeze-window run. READ-ONLY vs the live table + origin.
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

W87_A = (217_004, 219_003)
W87_B = (55_501, 55_700)
W86_TAIL_A = (215_004, 217_003)   # registered W86 (bm-a r576, table tail)
W86_TAIL_B = (55_201, 55_400)

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

# --- leg 0: registry shape (single state: W86 registered tail) ----------------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 87)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[86]["a"] == W86_TAIL_A and \
    N1_BANDS[86]["b_exit"] == W86_TAIL_B and \
    N1_BANDS[86].get("engine_owner") == "bm-a", "leg0 failed: W86 row drift"
assert 85 in N1_BANDS and N1_BANDS[85].get("engine_owner") == "bm-b", \
    "leg0 failed: W85 row/owner drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 76, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 76)"
assert len(bma_rows) == 22, f"leg0 failed: bm-a rows {len(bma_rows)} (expect 22)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W86 bm-a r576); "
      f"engine_owner rows={len(owner_rows)} + candidate; bm-a rows={len(bma_rows)} "
      f"-> W87 = bm-a 23rd owned, SEVENTY-SEVENTH engine wave by machine-derive")

# --- leg 0b: NO peer W87 seat claim on origin (vacancy of seat MSGs) ----------
seat_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w87" in _ln.lower():
            seat_claims.append(_pfx + _ln)
assert not seat_claims, f"leg0b failed: peer W87 seat MSG on origin: {seat_claims}"
print("leg0b: zero W87 seat MSGs on origin (inbox+processed scanned) -- "
      "W87 vacancy confirmed; own seat MSG to be pushed BEFORE this freeze "
      "(r565 early-visibility law)")

# --- leg 1: arithmetic positions vs reserved universe -------------------------
tail = N1_BANDS[86]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == (217_004, 219_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (55_401, 55_600), f"leg1-B drift: {ARITH_B}"
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
a_pt_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert not a_band_hits and not a_pt_hits, \
    f"leg1-A failed: arithmetic window not clean: {a_band_hits} {a_pt_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero band/point hits)")
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
b_pt_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert not b_band_hits, f"leg1-B failed: band hits {b_band_hits}"
assert b_pt_hits == [55_500], \
    f"leg1-B failed: expect exactly [55_500] point refusal, got {b_pt_hits}"
reg55 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 55_500]
assert reg55 == ["grid_p1"], f"leg1-B failed: 55_500 key {reg55}"
# median non-endpoint check (position 99 of a 200-wide window)
assert ARITH_B[0] < 55_500 < ARITH_B[1], "leg1-B: hit must be in-band non-endpoint"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED in-band at "
      f"SEED_REGISTRY {reg55[0]}=55_500 (median position 99/199, non-endpoint) "
      f"-> D-20261002-05 pin: PAST-HIT start-window hit+1 (window-step-chain "
      f"reading 55_601..55_800 is the BANNED fork; W68-B positive anchor)")
RESTART_B = (55_500 + 1, 55_500 + WIDTH_B)
assert RESTART_B == W87_B, f"leg1-B2 drift: {RESTART_B}"
rb_band = [b for b in bands + actual if overlaps(b, RESTART_B)]
rb_pt = sorted(p for p in points if RESTART_B[0] <= p <= RESTART_B[1])
assert not rb_band and not rb_pt, \
    f"leg1-B2 failed: restart window not clean: {rb_band} {rb_pt}"
print(f"leg1-B2 past-hit restart {RESTART_B[0]}..{RESTART_B[1]} CLEAN")

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

first_a = clean(W86_TAIL_A[1] + 1, WIDTH_A)
assert first_a == W87_A, f"leg2-A failed: {first_a} != {W87_A}"
start_b = W86_TAIL_B[1] + 1
first_b = None
lo = start_b
while first_b is None and lo < start_b + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W87_B, f"leg2-B failed: {first_b} != {W87_B} (scan-forward hit+1)"
print(f"leg2: A first-clean {W87_A[0]}..{W87_A[1]} == candidate; "
      f"B first-clean {W87_B[0]}..{W87_B[1]} == candidate (hit+1 scan law)")
assert not overlaps(W87_A, W87_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W87_A), ("B", W87_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W87-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W87-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W87-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W87-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W87-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W87-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W87-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W87-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "87: {\"a\": (217_004" not in out, \
    "leg3 failed: W87 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W87"' not in outn1, \
    "leg3 failed: W87 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W87_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: W87 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | single-state (W86 tail)")
if conflicts:
    print("W87 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W87 ADMIT: A {W87_A[0]}..{W87_A[1]} + B {W87_B[0]}..{W87_B[1]} "
      f"(refusal facts: B arithmetic 55_401..55_600 median point-refusal at "
      f"grid_p1=55_500 only -- zero band hits, zero other points; "
      f"D-20261002-05 pin: past-hit restart) -- clean vs all registered rows "
      f"+ registry + probes/actuals -- engine_owner=bm-a (seat MSG to be "
      f"pushed BEFORE this freeze per r565). NOT a re-pick (R250: W87 bands "
      f"were never assigned).")

# --- W88+ projection (warning text for the law table row) --------------------
w88_a = (W87_A[1] + 1, W87_A[1] + WIDTH_A)
w88_b = (W87_B[1] + 1, W87_B[1] + WIDTH_B)
a_hits88 = sorted(p for p in points if w88_a[0] <= p <= w88_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w88_a)]
b_hits88 = sorted(p for p in points if w88_b[0] <= p <= w88_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w88_b)]
print(f"W88+ projection: A arithmetic +2_000 = {w88_a[0]}..{w88_a[1]} "
      f"-> {'CLEAN (verify at W88 prereg)' if not a_hits88 else 'REFUSED ' + str(a_hits88)}; "
      f"B +200 from W87 end = {w88_b[0]}..{w88_b[1]} "
      f"-> {'CLEAN (verify at W88 prereg)' if not b_hits88 else 'REFUSED ' + str(b_hits88)}")
