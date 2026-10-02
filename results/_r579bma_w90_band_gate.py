# -*- coding: utf-8 -*-
"""W90 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W90 candidate = first FREE number skipping the bm-b-declared W89 seat
(MSG-20261002-1358-bmb-w89-seat, published=reserved r518-1). W87 (bm-a
r577) and W88 (bm-c r368) are REGISTERED rows at this window; W88 burn
in flight (finalize pending), W89 seat-published unregistered (bm-b
freeze window in flight).

TRI-STATE gate (bm-b W89 registration may land mid-window); every state
converges on the same final bands (DUAL-STATE CONVERGENT, W88 precedent
r368):
  A 223_004..225_003 (state B: arithmetic continuation from the
     registered W89 tail; state A: skip-past-published chain W88
     registered tail -> W89 published band -> first clean, width 2_000,
     CLEAN zero refusal points)
  B 56_201..56_400   (both states: +200 from the W89 published/
     registered tail 56_200; CLEAN zero refusal points)

Machine-verified against: all registered N1 wave bands (W2..W88 [+W89
in whichever state]), the W89 published projection (bm-b gate receipt
_r577bmb_w89_band_gate.py), N3-R1 used-seed band 70_000..70_005
(MSG-183x r529 mandatory leg), probe cluster 95_000..95_003 (r335
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
probe points, N2-W15 draft probe points, lfc/options draws.

r579 bm-a freeze-window run. READ-ONLY vs the live table + origin.
NOT a re-pick (R250: W90 bands were never assigned).
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

W90_A = (223_004, 225_003)
W90_B = (56_201, 56_400)
W87_A = (217_004, 219_003)      # bm-a r577 REGISTERED
W87_B = (55_501, 55_700)
W88_A = (219_004, 221_003)      # bm-c r368 REGISTERED
W88_B = (55_701, 55_900)
W89_PUB_A = (221_004, 223_003)  # bm-b seat MSG-20261002-1358-bmb-w89-seat
W89_PUB_B = (56_001, 56_200)

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
tails = {88: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 89)),
         89: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 90))}
REG89 = 89 in N1_BANDS
assert keys == tails[88] or keys == tails[89], \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
assert N1_BANDS[87]["a"] == W87_A and \
    N1_BANDS[87]["b_exit"] == W87_B and \
    N1_BANDS[87].get("engine_owner") == "bm-a", "leg0 failed: W87 drift"
assert N1_BANDS[88]["a"] == W88_A and \
    N1_BANDS[88]["b_exit"] == W88_B and \
    N1_BANDS[88].get("engine_owner") == "bm-c", "leg0 failed: W88 drift"
bands.append(W87_A); bands.append(W87_B)
bands.append(W88_A); bands.append(W88_B)
if REG89:
    assert N1_BANDS[89]["a"] == W89_PUB_A and \
        N1_BANDS[89]["b_exit"] == W89_PUB_B and \
        N1_BANDS[89].get("engine_owner") == "bm-b", "leg0 failed: W89 drift"
    bands.append(W89_PUB_A); bands.append(W89_PUB_B)
    print("leg0: W89 REGISTERED mid-window (state B)")
else:
    bands.append(W89_PUB_A); bands.append(W89_PUB_B)
    print("leg0: W89 seat-published unregistered (state A)")
MODE = ("B89 (registered)" if REG89 else "A89 (seat-published)") + \
    " -- dual-state convergent (W88 r368 precedent)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} (+W89 seat in flight) "
      f"+ candidate; bm-a rows={len(bma_rows)} -> W90 = bm-a "
      f"{len(bma_rows) + 1}th owned (machine-derive; prose ordinal drift "
      "disclosed since W80, r359 law -- machine count authoritative)")

# --- leg 0b: seat MSGs on origin (published=reserved face) -------------------
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

_seat_on_origin("fleet/inbox/MSG-20261002-1345-bma-w87-seat.md",
                ["217_004..219_003", "55_501..55_700"])
_bmc = None
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True)
for _ln in _r.stdout.decode("utf-8").splitlines():
    if "bmc" in _ln and "w88" in _ln.lower():
        _bmc = _ln.strip()
        break
if _bmc is None:
    _r = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
         "fleet/inbox/processed/"], capture_output=True)
    for _ln in _r.stdout.decode("utf-8").splitlines():
        if "bmc" in _ln and "w88" in _ln.lower():
            _bmc = _ln.strip()
            break
assert _bmc is not None, "leg0b failed: bm-c W88 seat MSG not found on origin"
_seat_on_origin(_bmc, ["219_004..221_003", "55_701..55_900"])
_seat_on_origin("fleet/inbox/MSG-20261002-1358-bmb-w89-seat.md",
                ["221_004..223_003", "56_001..56_200"])
print("leg0b: bm-a W87 + bm-c W88 + bm-b W89 seat MSGs verified on origin "
      "(published=reserved r518-1)")

# --- leg 1: arithmetic continuation + skip-past-published chain --------------
if REG89:
    tail = N1_BANDS[89]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W90_A and ARITH_B == W90_B, \
        f"leg1 failed: state B arithmetic drift {ARITH_A} {ARITH_B}"
    print(f"leg1: state B arithmetic continuation from the registered W89 "
          f"tails -> A {ARITH_A[0]}..{ARITH_A[1]} / B {ARITH_B[0]}.."
          f"{ARITH_B[1]} (both CLEAN below)")
else:
    tail = N1_BANDS[88]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == (221_004, 223_003) and ARITH_B == (55_901, 56_100), \
        f"leg1 failed: W88-tail arithmetic drift {ARITH_A} {ARITH_B}"
    a_ref = [b for b in bands if overlaps(b, ARITH_A) and b != W89_PUB_A]
    assert a_ref == [W89_PUB_A] or not [x for x in a_ref if x != W89_PUB_A], \
        f"leg1-A failed: unexpected refs {a_ref}"
    assert ARITH_A == W89_PUB_A, "leg1-A: W88-tail arithmetic != W89 published"
    # A chain: W88-tail arithmetic == W89 published -> skip-past-published
    final_a = (W89_PUB_A[1] + 1, W89_PUB_A[1] + WIDTH_A)
    assert final_a == W90_A, f"leg1 chain-A final drift: {final_a}"
    a_hits = sorted(p for p in points if final_a[0] <= p <= final_a[1]) or \
        [b for b in bands + actual if overlaps(b, final_a)]
    assert not a_hits, f"leg1 chain-A final not clean: {a_hits}"
    print(f"leg1: state A chain: W88-tail arithmetic {ARITH_A[0]}.."
          f"{ARITH_A[1]} == W89 published band -> skip-past-published -> "
          f"A {final_a[0]}..{final_a[1]} CLEAN (r518-1)")
    # B chain: W88-tail arithmetic 55_901..56_100 refused in-band at
    # SEED_REGISTRY ths_agg_p1=56_000 (median 99/199) -> pin 56_001..56_200
    # == W89 published -> skip-past-published -> 56_201..56_400
    w0 = (55_901, 56_100)
    pt = sorted(p for p in points if w0[0] <= p <= w0[1])
    assert pt == [56_000], f"leg1 chain-B refusal-face drift: {pt}"
    reg56 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 56_000]
    assert reg56 == ["ths_agg_p1"], f"leg1 chain-B: 56_000 key drift {reg56}"
    assert 56_000 - 55_901 == 99, "56_000 must sit at median 99/199 non-edge"
    pinned = (56_001, 56_200)
    assert pinned == W89_PUB_B, "leg1 chain-B: pin restart != W89 published"
    final_b = (pinned[1] + 1, pinned[1] + WIDTH_B)
    assert final_b == W90_B, f"leg1 chain-B final drift: {final_b}"
    b_hits = sorted(p for p in points if final_b[0] <= p <= final_b[1]) or \
        [b for b in bands + actual if overlaps(b, final_b)]
    assert not b_hits, f"leg1 chain-B final not clean: {b_hits}"
    print(f"leg1: state A chain: B arithmetic 55_901..56_100 REFUSED at "
          f"ths_agg_p1=56_000 in-window MEDIAN (99/199) -> D-20261002-05 "
          f"pin restart 56_001..56_200 == W89 published -> skip-past-"
          f"published -> B {final_b[0]}..{final_b[1]} CLEAN")

# --- leg 2: first clean window == candidate (both sides) --------------------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

start_a = (W89_PUB_A[1] + 1)
first_a = clean(start_a, WIDTH_A)
assert first_a == W90_A, f"leg2-A failed: {first_a} != {W90_A}"
start_b = (W89_PUB_B[1] + 1)
first_b = clean(start_b, WIDTH_B)
assert first_b == W90_B, f"leg2-B failed: {first_b} != {W90_B}"
print(f"leg2: A first-clean {W90_A[0]}..{W90_A[1]} == candidate; "
      f"B first-clean {W90_B[0]}..{W90_B[1]} == candidate")
assert not overlaps(W90_A, W90_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ---------------------------------
conflicts = []
for tag, band in (("A", W90_A), ("B", W90_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W90-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W90-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W90-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W90-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W90-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W90-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W90-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W90-{tag} (r335 leg)")
    for nm, pb in (("W89pub", (W89_PUB_A if tag == "A" else W89_PUB_B)),
                   ("W87reg", (W87_A if tag == "A" else W87_B)),
                   ("W88reg", (W88_A if tag == "A" else W88_B))):
        if overlaps(pb, band):
            conflicts.append(f"{nm} band x W90-{tag}")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "90: {\"a\": (223_004" not in out, \
    "leg3 failed: W90 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W90"' not in outn1, \
    "leg3 failed: W90 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W90_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg3 failed: W90 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W90 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W90 ADMIT: A {W90_A[0]}..{W90_A[1]} + B {W90_B[0]}..{W90_B[1]} "
      f"(mode={MODE}; refusal facts: W89 published skip-past chain [state A "
      "face: ths_agg_p1=56_000 median pin under the W89-published window] "
      "disclosed NOT taken for W90 -- W90 starts past the W89 published "
      "tails on BOTH sides, arithmetic continuation zero skip) -- clean vs "
      "all registered rows + W89 reserved face + registry + probes/actuals "
      "-- engine_owner=bm-a (seat published=reserved MSG-20261002-1415-bma "
      "PUSHED to origin BEFORE this freeze per r565 early-visibility law). "
      "NOT a re-pick (R250: W90 bands were never assigned).")

# --- W91+ projection (warning text for the law table row) --------------------
w91_a = (W90_A[1] + 1, W90_A[1] + WIDTH_A)
w91_b = (W90_B[1] + 1, W90_B[1] + WIDTH_B)
a_hits91 = sorted(p for p in points if w91_a[0] <= p <= w91_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w91_a)]
b_hits91 = sorted(p for p in points if w91_b[0] <= p <= w91_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w91_b)]
print(f"W91+ projection: A arithmetic +2_000 = {w91_a[0]}..{w91_a[1]} "
      f"-> {'CLEAN (verify at W91 prereg)' if not a_hits91 else 'REFUSED ' + str(a_hits91)}; "
      f"B +200 from W90 end = {w91_b[0]}..{w91_b[1]} "
      f"-> {'CLEAN (verify at W91 prereg)' if not b_hits91 else 'REFUSED ' + str(b_hits91)}")
if b_hits91:
    p91 = b_hits91[0]
    regk91 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == p91]
    pos91 = p91 - w91_b[0]
    edge = "EDGE-endpoint (two readings converge, W74/W81 family)" \
        if pos91 in (0, w91_b[1] - w91_b[0]) else \
        f"in-window MEDIAN ({pos91}/{w91_b[1] - w91_b[0]} non-edge -> " \
        "D-20261002-05 pin restart for the W91 freezer)"
    print(f"W91+ projection note: B refusal point {p91} key={regk91} = {edge}")
