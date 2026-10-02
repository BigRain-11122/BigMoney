# -*- coding: utf-8 -*-
"""W91 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W91 candidate = first FREE number after the registered W89 row (bm-b r578
estate adoption, commit 27a8d9712) SKIPPING the bm-a-declared W90 seat
(MSG-20261002-1415-bma, published=reserved r518-1).

TRI-STATE gate (bm-a W90 freeze may land mid-window); every state converges:
  A 225_004..227_003 (W89 tail -> W90 pub 223_004..225_003 -> first clean,
     width 2_000, CLEAN)
  B 56_501..56_700   (chain: W89 B end 56_200 -> 56_201..56_400 == W90 pub
     -> skip-past-published -> 56_401..56_600 REFUSED at SEED_REGISTRY
     p4_batch3_dca=56_500 in-window MEDIAN hit (zero-indexed 99/199,
     non-edge) -> D-20261002-05 pinned semantics: hit+1 restart
     56_501..56_700 CLEAN; window-step chain reading 56_601..56_800
     disclosed NOT taken per the pinned law)

Machine-verified against: all registered N1 wave bands (W2..W89 [+W90 in
whichever state]), the W90 published projection, N3-R1 used-seed band
70_000..70_005 (MSG-183x r529 leg), probe cluster 95_000..95_003 (r335
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 probe
points, N2-W15 draft probe points, lfc/options draws.

r578 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W91_A = (225_004, 227_003)
W91_B = (56_501, 56_700)
W90_PUB_A = (223_004, 225_003)   # bm-a seat MSG-20261002-1415-bma-w90-seat
W90_PUB_B = (56_201, 56_400)

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

# --- leg 0: registry shape + tri-state mode detection ------------------------
keys = sorted(N1_BANDS)
tails = {89: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 90)),
         90: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 91))}
REG90 = 90 in N1_BANDS
assert keys == tails[89] or keys == tails[90], \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[89]["a"] == (221_004, 223_003) and \
    N1_BANDS[89]["b_exit"] == (56_001, 56_200) and \
    N1_BANDS[89].get("engine_owner") == "bm-b", "leg0 failed: W89 row drift"
for w in (87, 88):
    assert w in N1_BANDS, f"leg0 failed: W{w} must be registered"
if REG90:
    assert N1_BANDS[90]["a"] == W90_PUB_A and \
        N1_BANDS[90]["b_exit"] == W90_PUB_B and \
        N1_BANDS[90].get("engine_owner") == "bm-a", "leg0 failed: W90 drift"
    bands.append(W90_PUB_A); bands.append(W90_PUB_B)
else:
    bands.append(W90_PUB_A); bands.append(W90_PUB_B)
MODE = ("B90" if REG90 else "A90") + " (" + \
    ("registered" if REG90 else "seat-published") + " W90)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} (+W90 seat in flight) "
      f"+ candidate; bm-b rows={len(bmb_rows)} -> W91 = bm-b "
      f"{len(bmb_rows) + 1}th owned; W91 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")

# --- leg 0b: bm-a W90 seat MSG on origin + W91 vacancy ------------------------
def _seat_on_origin(path, musts):
    for _sp in (path, path.replace("fleet/inbox/", "fleet/inbox/processed/")):
        _r = subprocess.run(["git", "show", f"origin/main:{_sp}"],
                            capture_output=True)
        if _r.returncode == 0:
            body = _r.stdout.decode("utf-8")
            for m in musts:
                assert m in body, f"leg0b failed: {m} not in {_sp}"
            return body
    raise AssertionError(f"leg0b failed: {path} not on origin")

_seat_on_origin("fleet/inbox/MSG-20261002-1415-bma-w90-seat.md",
                ["223_004..225_003", "56_201..56_400", "bm-a"])
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], capture_output=True)
w91_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
             if "w91" in ln.lower() and "seat" in ln.lower()]
assert not w91_seats, f"leg0b failed: W91 seat already declared {w91_seats}"
print("leg0b: bm-a W90 seat MSG verified on origin (published=reserved "
      "r518-1); W91 seat vacancy machine-checked (zero W91 seat MSGs)")

# --- leg 1: skip-past-published chain (mode-aware) ----------------------------
tail = N1_BANDS[89]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W90_PUB_A and ARITH_B == W90_PUB_B, \
    f"leg1 drift vs W90 published: {ARITH_A} {ARITH_B}"
print(f"leg1: arithmetic {ARITH_A[0]}..{ARITH_A[1]} / {ARITH_B[0]}.."
      f"{ARITH_B[1]} REFUSED by the W90 published face "
      f"(reserved r518-1) -> skip-past-published")

# chain walk: A side from W89 tail past W90 (pub or registered) -> first clean
def next_band_a(after_hi):
    return (after_hi + 1, after_hi + WIDTH_A)

cur_a = tuple(N1_BANDS[89]["a"])
cand_a = next_band_a(cur_a[1])
assert cand_a == W90_PUB_A, f"leg1 chain-A drift: {cand_a}"
final_a = next_band_a(W90_PUB_A[1])
assert final_a == W91_A, f"leg1 chain-A final drift: {final_a}"
a_fin_hits = sorted(p for p in points if final_a[0] <= p <= final_a[1]) or \
    [b for b in bands + actual if overlaps(b, final_a)]
assert not a_fin_hits, f"leg1 chain-A final not clean: {a_fin_hits}"
print(f"leg1 chain-A: W89 tail -> W90 pub -> {final_a[0]}..{final_a[1]} "
      f"CLEAN (skip-past-published, r518-1)")

# chain walk: B side from W89 tail past W90 pub, then the 56_500 median pin
cur_lo = N1_BANDS[89]["b_exit"][1] + 1
assert (cur_lo, cur_lo + WIDTH_B - 1) == W90_PUB_B, "leg1 chain-B W90 step"
w_mid = (W90_PUB_B[1] + 1, W90_PUB_B[1] + WIDTH_B)
assert w_mid == (56_401, 56_600), f"leg1 chain-B drift: {w_mid}"
b_hits = sorted(p for p in points if w_mid[0] <= p <= w_mid[1])
b_band_ref = [b for b in bands + actual if overlaps(b, w_mid)]
assert b_hits == [56_500] and not b_band_ref, \
    f"leg1 chain-B mid-window failed: expect [56_500], got {b_hits} {b_band_ref}"
reg56 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 56_500]
assert reg56 == ["p4_batch3_dca"], \
    f"leg1 chain-B: 56_500 key drift {reg56}"
pos = 56_500 - w_mid[0]  # zero-indexed position inside the window
assert pos == 99 and w_mid[1] - w_mid[0] == 199, \
    f"leg1 chain-B: 56_500 must be the in-window MEDIAN (99/199), got pos {pos}"
pinned_b = (56_500 + 1, 56_500 + WIDTH_B)
assert pinned_b == W91_B, f"leg1 chain-B pin drift: {pinned_b}"
print(f"leg1 chain-B: {w_mid[0]}..{w_mid[1]} REFUSED at SEED_REGISTRY "
      f"p4_batch3_dca=56_500 in-window MEDIAN hit (99/199 non-edge) -> "
      f"D-20261002-05 pinned: hit+1 restart {pinned_b[0]}..{pinned_b[1]} "
      f"(window-step chain reading 56_601..56_800 disclosed NOT taken per "
      f"the pinned law)")

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

first_a = clean(W90_PUB_A[1] + 1, WIDTH_A)
assert first_a == W91_A, f"leg2-A failed: {first_a} != {W91_A}"
first_b = clean(56_500 + 1, WIDTH_B)  # past-hit restart from the pinned 56_500
assert first_b == W91_B, f"leg2-B failed: {first_b} != {W91_B}"
print(f"leg2: A first-clean {W91_A[0]}..{W91_A[1]} == candidate; "
      f"B first-clean {W91_B[0]}..{W91_B[1]} == candidate (hit+1 restart)")
assert not overlaps(W91_A, W91_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W91_A), ("B", W91_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W91-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W91-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W91-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W91-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W91-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W91-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W91-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W91-{tag} (r335 leg)")
    for nm, pb in (("W90pub", (W90_PUB_A if tag == "A" else W90_PUB_B)),):
        if overlaps(pb, band):
            conflicts.append(f"{nm} band x W91-{tag}")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "91: {\"a\": (225_004" not in out, \
    "leg3 failed: W91 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W91"' not in outn1, \
    "leg3 failed: W91 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W91_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W91 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W91 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W91 ADMIT: A {W91_A[0]}..{W91_A[1]} + B {W91_B[0]}..{W91_B[1]} "
      f"(mode={MODE}; refusal facts: W90 published skip-past chain + "
      "SEED_REGISTRY p4_batch3_dca=56_500 in-window median hit, "
      "D-20261002-05 pinned hit+1 restart) -- clean vs all registered rows "
      "+ W90 reserved face + registry + probes/actuals -- engine_owner=bm-b "
      "(seat published=reserved pushed BEFORE this freeze per r565 "
      "early-visibility law). NOT a re-pick (R250: W91 bands were never "
      "assigned).")

# --- W92+ projection (warning text for the law table row) --------------------
w92_a = (W91_A[1] + 1, W91_A[1] + WIDTH_A)
w92_b = (W91_B[1] + 1, W91_B[1] + WIDTH_B)
a_hits92 = sorted(p for p in points if w92_a[0] <= p <= w92_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w92_a)]
b_hits92 = sorted(p for p in points if w92_b[0] <= p <= w92_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w92_b)]
print(f"W92+ projection: A arithmetic +2_000 = {w92_a[0]}..{w92_a[1]} "
      f"-> {'CLEAN (verify at W92 prereg)' if not a_hits92 else 'REFUSED ' + str(a_hits92)}; "
      f"B +200 from W91 end = {w92_b[0]}..{w92_b[1]} "
      f"-> {'CLEAN (verify at W92 prereg)' if not b_hits92 else 'REFUSED ' + str(b_hits92)}")
