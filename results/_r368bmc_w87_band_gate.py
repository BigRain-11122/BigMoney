# -*- coding: utf-8 -*-
"""W87 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W87 candidate = first FREE number after the registered W86 row (bm-a r576
five-face freeze landed, 12/12 products delivered, finalize pending behind
the in-flight W85 bm-b upstream seat). NO seat-published-but-unregistered
wave exists at gate time; bm-a's W86 seat MSG W87+ projection (A
217_004..219_003 CLEAN; B 55_401..55_600 refused in-band at SEED_REGISTRY
grid_p1=55_500 MEDIAN hit) is re-derived here, never transcribed (r335
law; projection face disclosed for the next freezer, machine-checked).

B-side reading-fork face (F-20261002-03 family, first mid-band case with
D-20261002-05 pin in force): arithmetic window 55_401..55_600 hits
SEED_REGISTRY grid_p1=55_500 MID-BAND (non-endpoint) -> two readings
diverge (past-hit start 55_501..55_700 vs window-step-chain 55_601..55_800)
-> D-20261002-05 group pin: PAST-HIT START-WINDOW is canonical ->
B = 55_501..55_700; the chain reading is BANNED by the pin and
negative-asserted below (precedent W68-B; W63-B history face not re-picked).

Machine-verified against: all registered N1 wave bands (W2..W86),
SEED_REGISTRY live values, N3-R1 used-seed band 70_000..70_005 (MSG-183x
r529 mandatory leg), probe cluster 95_000..95_003 (r335 leg), v1 in-use +
W1 ext bands, N2/N4 probe points, N2-W15 draft probe points, lfc/options
actual draws. Foreign W87 seat MSG vacancy checked on origin (r565
early-visibility / r518-1 published=reserved).

r368 bm-c freeze-window run. READ-ONLY vs the live table + origin.
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

# --- leg 0: registry shape + tail + owner counts (r359 machine-derive) ------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 87)), \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert 87 not in N1_BANDS, "leg0 failed: W87 already registered locally"
assert N1_BANDS[86]["a"] == W86_TAIL_A and \
    N1_BANDS[86]["b_exit"] == W86_TAIL_B and \
    N1_BANDS[86].get("engine_owner") == "bm-a", "leg0 failed: W86 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(owner_rows) == 76, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 76)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == len(owner_rows), \
    "leg0 failed: owner partition drift"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W86 bm-a, "
      f"12/12 burned, finalize pending); engine_owner rows={len(owner_rows)} "
      f"+ candidate -> W87 = SEVENTY-SEVENTH engine wave, bm-c's "
      f"{len(bmc_rows) + 1}th owned (bm-c rows={len(bmc_rows)}+candidate; "
      f"bm-a={len(bma_rows)}, bm-b={len(bmb_rows)})")

# --- leg 0b: foreign W87 seat MSG vacancy on origin (r565/r518-1) ------------
tree = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], encoding="utf-8")
foreign_w87 = [ln for ln in tree.splitlines()
               if "w87-seat" in ln and "bmc" not in ln]
assert not foreign_w87, \
    f"leg0b failed: FOREIGN W87 seat MSG already on origin -> yield " \
    f"(r518-1 published=reserved): {foreign_w87}"
print("leg0b: zero foreign W87 seat MSGs on origin (inbox + processed "
      "scanned) -> seat VACANT for bm-c")

# --- leg 1: arithmetic derivation + D-20261002-05 mid-band pin face ---------
ARITH_A = (W86_TAIL_A[1] + 1, W86_TAIL_A[1] + WIDTH_A)
assert ARITH_A == W87_A, f"leg1-A drift: {ARITH_A}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert not a_hits and not a_band_hits, \
    f"leg1-A failed: arithmetic A refused {a_hits} {a_band_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(== W86 A end + 1, stride {WIDTH_A})")
ARITH_B = (W86_TAIL_B[1] + 1, W86_TAIL_B[1] + WIDTH_B)
assert ARITH_B == (55_401, 55_600), f"leg1-B drift: {ARITH_B}"
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [55_500], \
    f"leg1-B failed: expect exactly [55_500] refusal point, got {b_hits}"
reg55 = sorted(k for k, v in science_gates.SEED_REGISTRY.items() if v == 55_500)
assert reg55 == ["grid_p1"], \
    f"leg1-B failed: 55_500 registry key drift, got {reg55}"
assert ARITH_B[0] < 55_500 < ARITH_B[1], \
    "leg1-B failed: 55_500 must be a MID-BAND (non-endpoint) hit"
assert [b for b in bands if overlaps(b, ARITH_B)] == [], \
    f"leg1-B failed: arithmetic B must be refused by the point only, " \
    f"got band hits {[b for b in bands if overlaps(b, ARITH_B)]}"
PIN_B = (55_500 + 1, 55_500 + WIDTH_B)          # past-hit start window
CHAIN_B = (ARITH_B[1] + 1, ARITH_B[1] + WIDTH_B)  # window-step-chain (BANNED)
assert PIN_B == W87_B, f"leg1-B pin drift: {PIN_B}"
assert CHAIN_B == (55_601, 55_800) and CHAIN_B != W87_B, \
    "leg1-B failed: window-step-chain reading must NOT be the candidate " \
    "(D-20261002-05 pin: past-hit start-window is canonical; chain reading " \
    "55_601..55_800 BANNED)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED in-band at "
      f"SEED_REGISTRY {reg55[0]}=55_500 MID-BAND hit (fork face "
      f"F-20261002-03) -> D-20261002-05 pin: past-hit start "
      f"{PIN_B[0]}..{PIN_B[1]} ADMITTED; chain reading "
      f"{CHAIN_B[0]}..{CHAIN_B[1]} BANNED (negative-asserted)")

# --- leg 2: first clean window == candidate (both sides, scan-forward) ------
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
first_b = None
lo = W86_TAIL_B[1] + 1
while first_b is None and lo < W86_TAIL_B[1] + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W87_B, f"leg2-B failed: {first_b} != {W87_B} (hit+1 restart)"
print(f"leg2: A first-clean {W87_A[0]}..{W87_A[1]} == candidate; "
      f"B first-clean {W87_B[0]}..{W87_B[1]} == candidate "
      f"(scan-forward past-hit restart, D-20261002-05 pin)")
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
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W87 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W87 ADMIT: A {W87_A[0]}..{W87_A[1]} + B {W87_B[0]}..{W87_B[1]} "
      f"(refusal facts: B arithmetic 55_401..55_600 refused in-band at "
      f"grid_p1=55_500 mid-band -> D-20261002-05 pin past-hit start; "
      "zero band hits, zero probe hits) -- clean vs all 84 registered rows "
      "+ registry + probes/actuals -- engine_owner=bm-c (seat MSG to be "
      "pushed BEFORE this freeze per r565 early-visibility law). NOT a "
      "re-pick (R250: W87 bands were never assigned).")

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
