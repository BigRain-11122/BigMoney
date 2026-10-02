# -*- coding: utf-8 -*-
"""W97 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W97 candidate = first FREE number after the registered W96 row (bm-a r581,
commit 16d7e71e2). SINGLE STATE zero seat gap. Seat published=reserved
MSG-20261002-1545-bmb pushed to origin a47ad46dd BEFORE this freeze per
r565 law.

  A 237_004..239_003 (arithmetic continuation from the registered W96 A
     tail 237_003, width 2_000, CLEAN)
  B 58_001..58_200   (arithmetic 57_901..58_100 REFUSED at SEED_REGISTRY
     im_ic_pair=58_000 in-window MEDIAN hit (zero-indexed 99/199,
     non-edge) -> D-20261002-05 pinned semantics: hit+1 restart
     58_001..58_200 CLEAN; window-step chain reading 58_101..58_300
     disclosed NOT taken per the pinned law; frozen precedent = W68-B
     arithmetic 50_401..50_600 hit 50_500 -> registered 50_501..50_700)

Machine-verified against: all registered N1 wave bands (W2..W14,
W16..W96), N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg),
probe cluster 95_000..95_003 (r335 leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 probe points, N2-W15 draft probe
points, lfc/options draws.

r581 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W97_A = (237_004, 239_003)
W97_B = (58_001, 58_200)

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

# --- leg 0: registry shape (single state: W96 registered, tail=W96) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 97))
assert keys == base_keys, \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[95]["a"] == (233_004, 235_003) and \
    N1_BANDS[95]["b_exit"] == (57_501, 57_700) and \
    N1_BANDS[95].get("engine_owner") == "bm-b", "leg0 failed: W95 row drift"
assert N1_BANDS[96]["a"] == (235_004, 237_003) and \
    N1_BANDS[96]["b_exit"] == (57_701, 57_900) and \
    N1_BANDS[96].get("engine_owner") == "bm-a", "leg0 failed: W96 row drift"
MODE = "B96 (registered W96)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-b "
      f"rows={len(bmb_rows)} -> W97 = bm-b "
      f"{len(bmb_rows) + 1}th owned; W97 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")

# --- leg 0b: own W97 seat MSG on origin + zero foreign W97 seats --------------


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


OWN_SEAT = "fleet/inbox/MSG-20261002-1545-bmb-w97-seat.md"
_seat_on_origin(OWN_SEAT, ["237_004..239_003", "58_001..58_200", "bm-b", "W97"])
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], capture_output=True)
w97_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
             if "w97" in ln.lower() and "seat" in ln.lower()]
assert w97_seats == [OWN_SEAT], \
    f"leg0b failed: W97 seat set must be exactly this machine's own " \
    f"published seat, got {w97_seats}"
print("leg0b: W97 seat = this machine's OWN published declaration "
      "(verified on origin with the frozen bands; zero foreign W97 seat "
      "MSGs)")

# --- leg 1: arithmetic continuation from the registered W96 tails ------------
tail = N1_BANDS[96]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W97_A, f"leg1-A drift: {ARITH_A} != {W97_A}"
assert ARITH_B == (57_901, 58_100), f"leg1-B arithmetic drift: {ARITH_B}"
a_pt_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_ref = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert not a_pt_hits and not a_band_ref, \
    f"leg1 failed: W97-A arithmetic window {ARITH_A[0]}..{ARITH_A[1]} " \
    f"not clean: points={a_pt_hits} bands={a_band_ref}"
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} == candidate CLEAN "
      f"(honest forward walk, zero refusal points)")
# B side: arithmetic window REFUSED at the median, then D-20261002-05 pin
b_pt_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_ref = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_pt_hits == [58_000] and not b_band_ref, \
    f"leg1 failed: W97-B arithmetic window refusal facts drift: " \
    f"points={b_pt_hits} bands={b_band_ref}"
reg58 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 58_000]
assert reg58 == ["im_ic_pair"], \
    f"leg1 failed: 58_000 SEED_REGISTRY key drift {reg58}"
pos = 58_000 - ARITH_B[0]  # zero-indexed position inside the window
assert pos == 99 and ARITH_B[1] - ARITH_B[0] == 199, \
    f"leg1 failed: 58_000 must be the in-window MEDIAN (99/199), got {pos}"
pinned_b = (58_000 + 1, 58_000 + WIDTH_B)
assert pinned_b == W97_B, f"leg1 failed: W97-B pin drift: {pinned_b} != {W97_B}"
pin_pt = sorted(p for p in points if W97_B[0] <= p <= W97_B[1])
pin_band = [b for b in bands + actual if overlaps(b, W97_B)]
assert not pin_pt and not pin_band, \
    f"leg1 failed: W97-B pinned window not clean: {pin_pt} {pin_band}"
print(f"leg1 chain-B: {ARITH_B[0]}..{ARITH_B[1]} REFUSED at SEED_REGISTRY "
      f"im_ic_pair=58_000 in-window MEDIAN hit (99/199 non-edge) -> "
      f"D-20261002-05 pinned: hit+1 restart {W97_B[0]}..{W97_B[1]} CLEAN "
      f"(window-step chain reading 58_101..58_300 disclosed NOT taken per "
      f"the pinned law; frozen precedent W68-B 50_501..50_700)")
assert not overlaps(W97_A, W97_B), "A/B overlap"


# --- leg 2: first clean window == candidate (both sides) ----------------------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)


first_a = clean(W97_A[0], WIDTH_A)
assert first_a == W97_A, f"leg2-A failed: {first_a} != {W97_A}"
first_b = clean(58_000 + 1, WIDTH_B)  # past-hit restart per the pinned law
assert first_b == W97_B, f"leg2-B failed: {first_b} != {W97_B}"
print(f"leg2: A first-clean {W97_A[0]}..{W97_A[1]} == candidate; "
      f"B first-clean past-hit restart {W97_B[0]}..{W97_B[1]} == candidate")

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W97_A), ("B", W97_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W97-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W97-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W97-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W97-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W97-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W97-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W97-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W97-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert '97: {"a": (237_004' not in out, \
    "leg3 failed: W97 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W97"' not in outn1, \
    "leg3 failed: W97 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W97_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W97 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W97 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W97 ADMIT: A {W97_A[0]}..{W97_A[1]} + B {W97_B[0]}..{W97_B[1]} "
      f"(mode={MODE}; refusal facts: SEED_REGISTRY im_ic_pair=58_000 "
      "in-window median hit on the B arithmetic window 57_901..58_100, "
      "D-20261002-05 pinned hit+1 restart 58_001..58_200) -- clean vs all "
      "registered rows + registry + probes/actuals -- engine_owner=bm-b "
      "(W97 seat published=reserved MSG-20261002-1545-bmb pushed BEFORE "
      "this freeze per r565 early-visibility law). NOT a re-pick (R250: "
      "W97 bands were never assigned).")

# --- W98+ projection (warning text for the law table row) ---------------------
w98_a = (W97_A[1] + 1, W97_A[1] + WIDTH_A)
w98_b = (W97_B[1] + 1, W97_B[1] + WIDTH_B)
a_hits98 = sorted(p for p in points if w98_a[0] <= p <= w98_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w98_a)]
b_hits98 = sorted(p for p in points if w98_b[0] <= p <= w98_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w98_b)]
print(f"W98+ projection: A arithmetic +2_000 = {w98_a[0]}..{w98_a[1]} "
      f"-> {'CLEAN (verify at W98 prereg)' if not a_hits98 else 'REFUSED ' + str(a_hits98)}; "
      f"B +200 from W97 end = {w98_b[0]}..{w98_b[1]} "
      f"-> {'CLEAN (verify at W98 prereg)' if not b_hits98 else 'REFUSED ' + str(b_hits98)}")
