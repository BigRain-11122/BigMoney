# -*- coding: utf-8 -*-
"""W93 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W92 was declared by bm-c first (MSG-20261002-1447-bmc, origin 14:47; bm-b
r579 gate run 15:03 = later origin-visibility -> ZERO-COST YIELD per r511
commit-order law, receipt MSG same-window declares W93 per r565
yield-then-reoccupy law).

W93 candidate = first FREE number after the W92 seat (published, and/or
registered mid-window -- TRI-STATE, both converge):
  A 229_004..231_003 (W91 tail 227_003 -> W92 face 227_004..229_003
     (pub or registered) -> skip-past -> first clean, width 2_000, CLEAN)
  B 57_101..57_300   (chain: W91 B tail 56_700 -> 56_701..56_900 == W92
     face -> skip -> arithmetic 56_901..57_100 REFUSED in-window at
     SEED_REGISTRY [57_000, 57_100] (57_000 = median position 99/199
     non-edge; 57_100 = upper-edge endpoint of the refused window) ->
     past-hit restart from the first median hit: 57_001..57_200 contains
     57_100 at median position 99/199 -> REFUSED -> restart 57_101..57_300
     CLEAN; window-step-chain reading from the refused arithmetic window
     (57_101..57_300) CONVERGES -- 57_100 sits at the arithmetic window
     upper endpoint, both restart readings coincide, no fork face)

Machine-verified against: all registered N1 wave bands (W2..W14, W16..W91
[+W92 in whichever state]), the W92 published face, N3-R1 used-seed band
70_000..70_005 (MSG-183x r529 leg), probe cluster 95_000..95_003 (r335
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 probe
points, N2-W15 draft probe points, lfc/options draws.

r579 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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
W92_PUB_A = (227_004, 229_003)   # bm-c seat MSG-20261002-1447-bmc
W92_PUB_B = (56_701, 56_900)

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
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 92))
REG92 = 92 in N1_BANDS
assert keys == base_keys or keys == base_keys + [92], \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[90]["a"] == (223_004, 225_003) and \
    N1_BANDS[90]["b_exit"] == (56_201, 56_400) and \
    N1_BANDS[90].get("engine_owner") == "bm-a", "leg0 failed: W90 row drift"
assert N1_BANDS[91]["a"] == (225_004, 227_003) and \
    N1_BANDS[91]["b_exit"] == (56_501, 56_700) and \
    N1_BANDS[91].get("engine_owner") == "bm-b", "leg0 failed: W91 row drift"
if REG92:
    assert N1_BANDS[92]["a"] == W92_PUB_A and \
        N1_BANDS[92]["b_exit"] == W92_PUB_B and \
        N1_BANDS[92].get("engine_owner") == "bm-c", \
        "leg0 failed: W92 row drift vs the bm-c seat-declared bands (tri-state divergence)"
MODE = ("B92" if REG92 else "A92") + " (" + \
    ("registered" if REG92 else "seat-published") + " W92)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-b "
      f"rows={len(bmb_rows)} -> W93 = bm-b "
      f"{len(bmb_rows) + 1}th owned; W93 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")

# --- leg 0b: bm-c W92 seat MSG on origin + W93 vacancy ------------------------
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

_seat_on_origin("fleet/inbox/MSG-20261002-1447-bmc-w92-seat.md",
                ["227_004..229_003", "56_701..56_900", "bm-c"])
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], capture_output=True)
w93_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
             if "w93" in ln.lower() and "seat" in ln.lower()]
OWN_SEAT = "fleet/inbox/MSG-20261002-1510-bmb-w92-yield-w93-seat.md"
assert w93_seats == [OWN_SEAT], \
    f"leg0b failed: W93 seat set must be exactly this machine's own " \
    f"published seat, got {w93_seats}"
_seat_on_origin(OWN_SEAT, ["229_004..231_003", "57_101..57_300", "bm-b"])
print("leg0b: bm-c W92 seat MSG verified on origin (published=reserved "
      "r518-1; yield receipt per r565 law); W93 seat = this machine's OWN "
      "published declaration (r565 yield-then-reoccupy, verified on origin "
      "with the frozen bands; zero foreign W93 seat MSGs)")

# --- leg 1: skip-past chain (mode-aware) --------------------------------------
tail = N1_BANDS[91]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == W92_PUB_A and ARITH_B == W92_PUB_B, \
    f"leg1 drift vs W92 face: {ARITH_A} {ARITH_B}"
print(f"leg1: arithmetic {ARITH_A[0]}..{ARITH_A[1]} / {ARITH_B[0]}.."
      f"{ARITH_B[1]} REFUSED by the W92 face ({MODE}, reserved r518-1) "
      f"-> skip-past")

def next_band_a(after_hi):
    return (after_hi + 1, after_hi + WIDTH_A)

final_a = next_band_a(W92_PUB_A[1])
assert final_a == W93_A, f"leg1 chain-A final drift: {final_a}"
a_fin_hits = sorted(p for p in points if final_a[0] <= p <= final_a[1]) or \
    [b for b in bands + actual if overlaps(b, final_a)]
assert not a_fin_hits, f"leg1 chain-A final not clean: {a_fin_hits}"
print(f"leg1 chain-A: W91 tail -> W92 face -> {final_a[0]}..{final_a[1]} "
      f"CLEAN (skip-past, r518-1)")

# chain walk: B side -- W91 tail -> W92 face -> 56_901..57_100 double-hit pin
w_arith = (W92_PUB_B[1] + 1, W92_PUB_B[1] + WIDTH_B)
assert w_arith == (56_901, 57_100), f"leg1 chain-B arithmetic drift: {w_arith}"
b_hits = sorted(p for p in points if w_arith[0] <= p <= w_arith[1])
assert b_hits == [57_000, 57_100], \
    f"leg1 chain-B refused-window hits drift: expect [57_000, 57_100], got {b_hits}"
b_band_ref = [b for b in bands + actual if overlaps(b, w_arith)]
assert not b_band_ref, f"leg1 chain-B refused-window band overlap: {b_band_ref}"
reg57 = {k: v for k, v in science_gates.SEED_REGISTRY.items() if v in (57_000, 57_100)}
pos0 = 57_000 - w_arith[0]
pos1 = 57_100 - w_arith[0]
assert pos0 == 99 and pos1 == 199 and w_arith[1] - w_arith[0] == 199, \
    f"leg1 chain-B hit positions drift: {pos0}/{pos1} (expect median 99/199 + upper-edge 199/199)"
print(f"leg1 chain-B: {w_arith[0]}..{w_arith[1]} REFUSED at SEED_REGISTRY "
      f"{sorted(reg57.items())} (57_000 = in-window MEDIAN 99/199 non-edge; "
      f"57_100 = upper-edge ENDPOINT)")
# past-hit restart from the first (median) hit: 57_001..57_200 contains 57_100 again
w_re1 = (57_000 + 1, 57_000 + WIDTH_B)
assert w_re1 == (57_001, 57_200), f"leg1 chain-B restart-1 drift: {w_re1}"
r1_hits = sorted(p for p in points if w_re1[0] <= p <= w_re1[1])
assert r1_hits == [57_100], \
    f"leg1 chain-B restart-1 hits drift: expect [57_100], got {r1_hits}"
pos_r1 = 57_100 - w_re1[0]
assert pos_r1 == 99, f"leg1 chain-B restart-1: 57_100 must sit at median 99/199 again"
# past-hit restart from the second hit: 57_101..57_300; window-step-chain
# reading from the refused arithmetic window lands on the SAME window
w_re2 = (57_100 + 1, 57_100 + WIDTH_B)
w_chain = (w_arith[0] + WIDTH_B, w_arith[1] + WIDTH_B)
assert w_re2 == w_chain == W93_B, \
    f"leg1 chain-B convergence drift: {w_re2} / {w_chain} vs {W93_B}"
r2_hits = sorted(p for p in points if w_re2[0] <= p <= w_re2[1]) or \
    [b for b in bands + actual if overlaps(b, w_re2)]
assert not r2_hits, f"leg1 chain-B final window not clean: {r2_hits}"
print(f"leg1 chain-B: past-hit restart {w_re1[0]}..{w_re1[1]} REFUSED at "
      f"57_100 (median 99/199 again) -> restart {w_re2[0]}..{w_re2[1]} "
      f"CLEAN; window-step-chain reading from the refused arithmetic "
      f"window = {w_chain[0]}..{w_chain[1]} CONVERGES (57_100 = refused "
      f"window upper endpoint; both restart readings coincide, no fork "
      f"face)")

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

first_a = clean(W92_PUB_A[1] + 1, WIDTH_A)
assert first_a == W93_A, f"leg2-A failed: {first_a} != {W93_A}"
first_b = clean(57_100 + 1, WIDTH_B)
assert first_b == W93_B, f"leg2-B failed: {first_b} != {W93_B}"
print(f"leg2: A first-clean {W93_A[0]}..{W93_A[1]} == candidate; "
      f"B first-clean {W93_B[0]}..{W93_B[1]} == candidate (past-hit restart)")
assert not overlaps(W93_A, W93_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
scan_bands = list(bands)
if REG92:
    scan_bands = [b for b in scan_bands]  # W92 already inside bands via N1_BANDS
else:
    scan_bands += [W92_PUB_A, W92_PUB_B]  # reserved face leg
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
    for nm, pb in (("W92pub", (W92_PUB_A if tag == "A" else W92_PUB_B)),):
        if overlaps(pb, band):
            conflicts.append(f"{nm} band x W93-{tag}")
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
     "research/PERPETUAL_N1_W93_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W93 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W93 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W93 ADMIT: A {W93_A[0]}..{W93_A[1]} + B {W93_B[0]}..{W93_B[1]} "
      f"(mode={MODE}; refusal facts: W92 face skip-past chain + arithmetic "
      "56_901..57_100 REFUSED at SEED_REGISTRY [57_000, 57_100] "
      "(57_000 in-window median 99/199 + 57_100 upper-edge endpoint; "
      "past-hit restart 57_001..57_200 REFUSED again at 57_100 median -> "
      "restart 57_101..57_300 CLEAN; window-step-chain reading converges, "
      "no fork face) -- clean vs all registered rows + W92 reserved face "
      "+ registry + probes/actuals -- engine_owner=bm-b (yield receipt + "
      "W93 seat published=reserved pushed BEFORE this freeze per r565 "
      "early-visibility law). NOT a re-pick (R250: W93 bands were never "
      "assigned).")

# --- W94+ projection (warning text for the law table row) ---------------------
w94_a = (W93_A[1] + 1, W93_A[1] + WIDTH_A)
w94_b = (W93_B[1] + 1, W93_B[1] + WIDTH_B)
a_hits94 = sorted(p for p in points if w94_a[0] <= p <= w94_a[1]) or \
    [f"band {b}" for b in scan_bands + actual if overlaps(b, w94_a)]
b_hits94 = sorted(p for p in points if w94_b[0] <= p <= w94_b[1]) or \
    [f"band {b}" for b in scan_bands + actual if overlaps(b, w94_b)]
print(f"W94+ projection: A arithmetic +2_000 = {w94_a[0]}..{w94_a[1]} "
      f"-> {'CLEAN (verify at W94 prereg)' if not a_hits94 else 'REFUSED ' + str(a_hits94)}; "
      f"B +200 from W93 end = {w94_b[0]}..{w94_b[1]} "
      f"-> {'CLEAN (verify at W94 prereg)' if not b_hits94 else 'REFUSED ' + str(b_hits94)}")
