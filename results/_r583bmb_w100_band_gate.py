# -*- coding: utf-8 -*-
"""W100 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W100 candidate = first FREE number after the registered W99 row (bm-c r374,
commit a0d9cabd3). SINGLE STATE zero seat gap (W2..W99 all registered).
Seat published=reserved MSG-20261002-1615-bmb pushed to origin 6b8c9fa7c
(r582) BEFORE this freeze per r565 law.

  A 243_004..245_003 (arithmetic continuation from the registered W99 A
     tail 243_003, width 2_000, CLEAN)
  B 58_751..58_950   (arithmetic continuation from the registered W99 B
     tail 58_750, width 200, CLEAN -- both sides arithmetic continuation,
     no pin chain, no skip; W92 r370 precedent family)

Machine-verified against: all registered N1 wave bands (W2..W14,
W16..W99), N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg),
probe cluster 95_000..95_003 (r335 leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 probe points, N2-W15 draft probe
points, lfc/options draws.

r583 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W100_A = (243_004, 245_003)
W100_B = (58_751, 58_950)

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

# --- leg 0: registry shape (single state: W99 registered, tail=W99) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 100))
assert keys == base_keys, \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[97]["a"] == (237_004, 239_003) and \
    N1_BANDS[97]["b_exit"] == (58_001, 58_200) and \
    N1_BANDS[97].get("engine_owner") == "bm-b", "leg0 failed: W97 row drift"
assert N1_BANDS[98]["a"] == (239_004, 241_003) and \
    N1_BANDS[98]["b_exit"] == (58_201, 58_400) and \
    N1_BANDS[98].get("engine_owner") == "bm-a", "leg0 failed: W98 row drift"
assert N1_BANDS[99]["a"] == (241_004, 243_003) and \
    N1_BANDS[99]["b_exit"] == (58_551, 58_750) and \
    N1_BANDS[99].get("engine_owner") == "bm-c", "leg0 failed: W99 row drift"
MODE = "B99 (registered W99)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-b "
      f"rows={len(bmb_rows)} -> W100 = bm-b "
      f"{len(bmb_rows) + 1}th owned; W100 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")

# --- leg 0b: own W100 seat MSG on origin + zero foreign W100 seats -------------


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


OWN_SEAT = "fleet/inbox/MSG-20261002-1615-bmb-w100-seat.md"
_seat_on_origin(OWN_SEAT, ["243_004..245_003", "58_751..58_950", "bm-b", "W100"])
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], capture_output=True)
w100_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w100" in ln.lower() and "seat" in ln.lower()]
assert w100_seats == [OWN_SEAT], \
    f"leg0b failed: W100 seat set must be exactly this machine's own " \
    f"published seat, got {w100_seats}"
print("leg0b: W100 seat = this machine's OWN published declaration "
      "(verified on origin with the frozen bands; zero foreign W100 seat "
      "MSGs)")

# --- leg 1: arithmetic continuation from the registered W99 tails ------------
tail = N1_BANDS[99]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W100_A, f"leg1-A drift: {ARITH_A} != {W100_A}"
assert ARITH_B == W100_B, f"leg1-B arithmetic drift: {ARITH_B} != {W100_B}"
for tag, band in (("A", ARITH_A), ("B", ARITH_B)):
    pt_hits = sorted(p for p in points if band[0] <= p <= band[1])
    band_ref = [b for b in bands + actual if overlaps(b, band)]
    assert not pt_hits and not band_ref, \
        f"leg1 failed: W100-{tag} arithmetic window {band[0]}..{band[1]} " \
        f"not clean: points={pt_hits} bands={band_ref}"
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} == candidate CLEAN; "
      f"B arithmetic {ARITH_B[0]}..{ARITH_B[1]} == candidate CLEAN "
      f"(honest forward walk both sides, zero refusal points, zero skips "
      f"-- W92 r370 precedent family)")
assert not overlaps(W100_A, W100_B), "A/B overlap"


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


first_a = clean(W100_A[0], WIDTH_A)
assert first_a == W100_A, f"leg2-A failed: {first_a} != {W100_A}"
first_b = clean(W100_B[0], WIDTH_B)
assert first_b == W100_B, f"leg2-B failed: {first_b} != {W100_B}"
print(f"leg2: A first-clean {W100_A[0]}..{W100_A[1]} == candidate; "
      f"B first-clean {W100_B[0]}..{W100_B[1]} == candidate")

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W100_A), ("B", W100_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W100-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W100-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W100-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W100-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W100-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W100-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W100-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W100-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert '100: {"a": (243_004' not in out, \
    "leg3 failed: W100 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W100"' not in outn1, \
    "leg3 failed: W100 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W100_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W100 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W100 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W100 ADMIT: A {W100_A[0]}..{W100_A[1]} + B {W100_B[0]}..{W100_B[1]} "
      f"(mode={MODE}; zero refusal facts: both sides arithmetic "
      "continuation from the registered W99 tails, honest forward walk) -- "
      "clean vs all registered rows + registry + probes/actuals -- "
      "engine_owner=bm-b (W100 seat published=reserved MSG-20261002-1615-"
      "bmb pushed BEFORE this freeze per r565 early-visibility law). "
      "NOT a re-pick (R250: W100 bands were never assigned).")

# --- W101+ projection (warning text for the law table row) --------------------
w101_a = (W100_A[1] + 1, W100_A[1] + WIDTH_A)
w101_b = (W100_B[1] + 1, W100_B[1] + WIDTH_B)
a_hits101 = sorted(p for p in points if w101_a[0] <= p <= w101_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w101_a)]
b_hits101 = sorted(p for p in points if w101_b[0] <= p <= w101_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w101_b)]
print(f"W101+ projection: A arithmetic +2_000 = {w101_a[0]}..{w101_a[1]} "
      f"-> {'CLEAN (verify at W101 prereg)' if not a_hits101 else 'REFUSED ' + str(a_hits101)}; "
      f"B +200 from W100 end = {w101_b[0]}..{w101_b[1]} "
      f"-> {'CLEAN (verify at W101 prereg)' if not b_hits101 else 'REFUSED ' + str(b_hits101)}")
