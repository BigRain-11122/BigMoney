# -*- coding: utf-8 -*-
"""W94 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W94 candidate = first FREE number after the bm-b W93 published seat
(MSG-20261002-1510-bmb, published=reserved r518-1). DUAL-STATE convergence
door (W90 r579 precedent):
  state A: W93 seat PUBLISHED but NOT yet registered in N1_BANDS ->
           skip-past-published chain from the W92 registered tail.
  state B: W93 registered (bm-b freeze landed) -> arithmetic continuation
           from the W93 registered tails.
  BOTH STATES must derive the SAME bands (bitwise) = DUAL-STATE CONVERGENT.

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 231_004..233_003  (state A: W93 published A end 231_003 + 1;
                       state B: W93 registered A tail + 1) CLEAN.
  B 57_301..57_500    (state A: W93 published B end 57_300 + 1;
                       state B: W93 registered B tail + 1) CLEAN.

Machine-verified against: all registered N1 wave bands (W2..W92 live,
W93 published seat), N3-R1 used-seed band 70_000..70_005 (MSG-183x r529
mandatory leg), probe cluster 95_000..95_003 (r335 leg), v1 in-use + W1
ext bands, SEED_REGISTRY live values, N2/N4 probe points, N2-W15 draft
probe points, lfc/options actuals.

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

W94_A = (231_004, 233_003)
W94_B = (57_301, 57_500)
W93_PUB_A = (229_004, 231_003)   # bm-b W93 seat MSG-20261002-1510-bmb (bitwise
W93_PUB_B = (57_101, 57_300)     # == my own r580 W93 gate ADMIT, cross-validated)
W92_TAIL_A = (227_004, 229_003)  # registered W92 (bm-c r370, live table tail)
W92_TAIL_B = (56_701, 56_900)

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
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

# --- leg 0: registry shape + state determination -----------------------------
keys = sorted(N1_BANDS)
assert keys[:13] == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] and \
    (len(keys) == 13 or keys[13] == 16), \
    f"leg0 failed: head keys drift {keys[:15]}"
w93_registered = 93 in N1_BANDS
if w93_registered:
    assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 94)), \
        f"leg0 failed: state-B keys tail {keys[-4:]}"
    assert N1_BANDS[93]["a"] == W93_PUB_A and \
        N1_BANDS[93]["b_exit"] == W93_PUB_B and \
        N1_BANDS[93].get("engine_owner") == "bm-b", \
        "leg0 failed: state-B W93 row drift vs published seat"
    STATE = "B"
else:
    assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 93)), \
        f"leg0 failed: state-A keys tail {keys[-4:]}"
    STATE = "A"
assert N1_BANDS[92]["a"] == W92_TAIL_A and \
    N1_BANDS[92]["b_exit"] == W92_TAIL_B and \
    N1_BANDS[92].get("engine_owner") == "bm-c", "leg0 failed: W92 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
exp_owner = 83 if STATE == "B" else 82
exp_bma = 24
assert len(owner_rows) == exp_owner, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect {exp_owner})"
assert len(bma_rows) == exp_bma, \
    f"leg0 failed: bm-a rows {len(bma_rows)} (expect {exp_bma})"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}; state {STATE} "
      f"(W93 {'REGISTERED' if w93_registered else 'seat-published-unregistered'}); "
      f"engine_owner rows={len(owner_rows)} + in-flight W93 (bm-b) + candidate; "
      f"bm-a rows={len(bma_rows)} -> W94 = bm-a 25th owned, EIGHTY-FOURTH "
      f"engine wave by machine-derive")

# --- leg 0b: NO peer W94 seat claim on origin (vacancy of seat MSGs) ----------
seat_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w94" in _ln.lower():
            seat_claims.append(_ln)
assert not seat_claims, f"leg0b failed: peer W94 seat MSG on origin: {seat_claims}"
print("leg0b: zero W94 seat MSGs on origin (inbox+processed scanned) -- "
      "W94 vacancy confirmed; own seat MSG pushed BEFORE this freeze "
      "(r565 early-visibility law)")

# --- leg 0c: W93 seat MSG on origin must be present (upstream published seat) --
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
_names = _r.stdout.decode("utf-8", "replace")
assert "MSG-20261002-1510-bmb" in _names, \
    "leg0c failed: bm-b W93 seat MSG not on origin (upstream published seat missing)"
print("leg0c: bm-b W93 seat MSG on origin confirmed (upstream published seat)")

# --- dual-state convergence: BOTH states must derive the same bands -----------
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands_pub = bands + [W93_PUB_A, W93_PUB_B]   # state-A reserved face (published seat)
bands_B = bands + [W93_PUB_A, W93_PUB_B]     # state-B: W93 already in bands list
bandsA_use = bands_pub if STATE == "A" else bands
bandsB_use = bands_B

# state A derive: skip-past-published chain from the W92 tail
sa_a_start = max(W93_PUB_A[1], W92_TAIL_A[1]) + 1
sa_b_start = max(W93_PUB_B[1], W92_TAIL_B[1]) + 1
# state B derive: arithmetic continuation from the W93 tails
sb_a_start = W93_PUB_A[1] + 1
sb_b_start = W93_PUB_B[1] + 1
assert sa_a_start == sb_a_start == 231_004, \
    f"convergence-A failed: stateA {sa_a_start} vs stateB {sb_a_start}"
assert sa_b_start == sb_b_start == 57_301, \
    f"convergence-B failed: stateA {sa_b_start} vs stateB {sb_b_start}"
print(f"convergence: state-A skip-past-published == state-B arithmetic "
      f"continuation: A start 231_004 / B start 57_301 (DUAL-STATE "
      f"CONVERGENT, W90 r579 precedent)")

def clean_in(lo, width, band_list):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in band_list + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

ca = clean_in(sa_a_start, WIDTH_A, bandsA_use)
cb = clean_in(sa_b_start, WIDTH_B, bandsB_use)
assert ca == W94_A, f"leg1-A failed: state-{STATE} first-clean {ca} != {W94_A}"
assert cb == W94_B, f"leg1-B failed: state-{STATE} first-clean {cb} != {W94_B}"
print(f"leg1: state-{STATE} A {W94_A[0]}..{W94_A[1]} CLEAN + "
      f"B {W94_B[0]}..{W94_B[1]} CLEAN (skip-past-published chain, zero "
      f"refusal points; dual-state convergent)")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W94_A), ("B", W94_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W94-{tag}")
    if overlaps(W93_PUB_A, band) or (tag == "A" and overlaps(W93_PUB_A, band)):
        conflicts.append(f"W93 published seat band x W94-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W94-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W94-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W94-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W94-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W94-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W94-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W94-{tag} (r335 leg)")
    # W93 published-seat disjointness (state-A reserved face, r518-1)
    for nm, pub in (("W93pubA", W93_PUB_A), ("W93pubB", W93_PUB_B)):
        if overlaps(pub, band):
            conflicts.append(f"{nm} published seat band x W94-{tag} (r518-1)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "94: {\"a\": (231_004" not in out, \
    "leg2 failed: W94 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W94"' not in outn1, \
    "leg2 failed: W94 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W94_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W94 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W94 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W94 ADMIT: A {W94_A[0]}..{W94_A[1]} + B {W94_B[0]}..{W94_B[1]} "
      f"(dual-state convergent skip-past-published chain from the W92 tail "
      f"over the bm-b W93 seat; zero refusal points both sides) -- clean vs "
      f"all registered rows + W93 published seat + registry + probes/actuals "
      f"-- engine_owner=bm-a (seat MSG pushed BEFORE this freeze per r565). "
      f"NOT a re-pick (R250: W94 bands were never assigned).")

# --- W95+ projection (warning text for the law table row) --------------------
w95_a = (W94_A[1] + 1, W94_A[1] + WIDTH_A)
w95_b = (W94_B[1] + 1, W94_B[1] + WIDTH_B)
a_hits95 = sorted(p for p in points if w95_a[0] <= p <= w95_a[1]) or \
    [f"band {b}" for b in bands + [W93_PUB_A, W93_PUB_B] if overlaps(b, w95_a)]
b_hits95 = sorted(p for p in points if w95_b[0] <= p <= w95_b[1]) or \
    [f"band {b}" for b in bands + [W93_PUB_A, W93_PUB_B] if overlaps(b, w95_b)]
print(f"W95+ projection: A arithmetic +2_000 = {w95_a[0]}..{w95_a[1]} "
      f"-> {'CLEAN (verify at W95 prereg)' if not a_hits95 else 'REFUSED ' + str(a_hits95)}; "
      f"B +200 from W94 end = {w95_b[0]}..{w95_b[1]} "
      f"-> {'CLEAN (verify at W95 prereg)' if not b_hits95 else 'REFUSED ' + str(b_hits95)}")
