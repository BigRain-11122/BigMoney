# -*- coding: utf-8 -*-
"""W95 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W95 candidate = first FREE number after the registered W94 row (post-heal
registry: W2..W14, W16..W94 all registered, zero seat gaps; W92 bm-c /
W93 bm-b / W94 bm-a). Seat published=reserved MSG-20261002-1536-bmb pushed
to origin BEFORE this freeze per r565 law.

  A 233_004..235_003 (arithmetic continuation from the registered W94 A
     tail 233_003, width 2_000)
  B 57_501..57_700   (arithmetic continuation from the registered W94 B
     tail 57_500, width 200)

Machine-verified against: all registered N1 wave bands (W2..W14, W16..W94),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options draws.

r580 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W95_A = (233_004, 235_003)
W95_B = (57_501, 57_700)

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

# --- leg 0: registry shape (single state: W94 registered, tail=W94) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 95))
assert keys == base_keys, \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[92]["a"] == (227_004, 229_003) and \
    N1_BANDS[92]["b_exit"] == (56_701, 56_900) and \
    N1_BANDS[92].get("engine_owner") == "bm-c", "leg0 failed: W92 row drift"
assert N1_BANDS[93]["a"] == (229_004, 231_003) and \
    N1_BANDS[93]["b_exit"] == (57_101, 57_300) and \
    N1_BANDS[93].get("engine_owner") == "bm-b", "leg0 failed: W93 row drift"
assert N1_BANDS[94]["a"] == (231_004, 233_003) and \
    N1_BANDS[94]["b_exit"] == (57_301, 57_500) and \
    N1_BANDS[94].get("engine_owner") == "bm-a", "leg0 failed: W94 row drift"
MODE = "B94 (registered W94)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-b "
      f"rows={len(bmb_rows)} -> W95 = bm-b "
      f"{len(bmb_rows) + 1}th owned; W95 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")

# --- leg 0b: own W95 seat MSG on origin + zero foreign W95 seats --------------
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

OWN_SEAT = "fleet/inbox/MSG-20261002-1536-bmb-w95-seat.md"
_seat_on_origin(OWN_SEAT, ["233_004..235_003", "57_501..57_700", "bm-b", "W95"])
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], capture_output=True)
w95_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
             if "w95" in ln.lower() and "seat" in ln.lower()]
assert w95_seats == [OWN_SEAT], \
    f"leg0b failed: W95 seat set must be exactly this machine's own " \
    f"published seat, got {w95_seats}"
print("leg0b: W95 seat = this machine's OWN published declaration "
      "(verified on origin with the frozen bands; zero foreign W95 seat "
      "MSGs)")

# --- leg 1: arithmetic continuation from the registered W94 tails ------------
tail = N1_BANDS[94]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W95_A, f"leg1-A drift: {ARITH_A} != {W95_A}"
assert ARITH_B == W95_B, f"leg1-B drift: {ARITH_B} != {W95_B}"
for tag, w in (("A", ARITH_A), ("B", ARITH_B)):
    pt_hits = sorted(p for p in points if w[0] <= p <= w[1])
    band_ref = [b for b in bands + actual if overlaps(b, w)]
    assert not pt_hits and not band_ref, \
        f"leg1 failed: W95-{tag} arithmetic window {w[0]}..{w[1]} not clean: " \
        f"points={pt_hits} bands={band_ref}"
print(f"leg1: arithmetic {ARITH_A[0]}..{ARITH_A[1]} / {ARITH_B[0]}.."
      f"{ARITH_B[1]} == candidate BOTH SIDES CLEAN (honest forward walk, "
      f"zero refusal points, no skip, no pin chain -- W92 r370 precedent "
      f"family)")
assert not overlaps(W95_A, W95_B), "A/B overlap"

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

first_a = clean(W95_A[0], WIDTH_A)
assert first_a == W95_A, f"leg2-A failed: {first_a} != {W95_A}"
first_b = clean(W95_B[0], WIDTH_B)
assert first_b == W95_B, f"leg2-B failed: {first_b} != {W95_B}"
print(f"leg2: A first-clean {W95_A[0]}..{W95_A[1]} == candidate; "
      f"B first-clean {W95_B[0]}..{W95_B[1]} == candidate")

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W95_A), ("B", W95_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W95-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W95-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W95-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W95-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W95-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W95-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W95-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W95-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "95: {\"a\": (233_004" not in out, \
    "leg3 failed: W95 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W95"' not in outn1, \
    "leg3 failed: W95 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W95_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W95 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W95 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W95 ADMIT: A {W95_A[0]}..{W95_A[1]} + B {W95_B[0]}..{W95_B[1]} "
      f"(mode={MODE}; refusal facts: NONE -- both-sides arithmetic "
      "continuation from the registered W94 tails clean vs all registered "
      "rows + registry + probes/actuals -- engine_owner=bm-b (W95 seat "
      "published=reserved pushed BEFORE this freeze per r565 "
      "early-visibility law). NOT a re-pick (R250: W95 bands were never "
      "assigned).")

# --- W96+ projection (warning text for the law table row) ---------------------
w96_a = (W95_A[1] + 1, W95_A[1] + WIDTH_A)
w96_b = (W95_B[1] + 1, W95_B[1] + WIDTH_B)
a_hits96 = sorted(p for p in points if w96_a[0] <= p <= w96_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w96_a)]
b_hits96 = sorted(p for p in points if w96_b[0] <= p <= w96_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w96_b)]
print(f"W96+ projection: A arithmetic +2_000 = {w96_a[0]}..{w96_a[1]} "
      f"-> {'CLEAN (verify at W96 prereg)' if not a_hits96 else 'REFUSED ' + str(a_hits96)}; "
      f"B +200 from W95 end = {w96_b[0]}..{w96_b[1]} "
      f"-> {'CLEAN (verify at W96 prereg)' if not b_hits96 else 'REFUSED ' + str(b_hits96)}")
