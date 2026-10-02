# -*- coding: utf-8 -*-
"""W89 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W89 candidate = first FREE number skipping the bm-a-declared W87 seat
(MSG-20261002-1345-bma-w87-seat) and the bm-c-declared W88 seat
(MSG-20261002-135x-bmc, origin-first vs our superseded W88 seat -- bm-b
yielded W88 to bm-c per r511 commit-order law, yield-then-reoccupy r565).

TRI-STATE gate (bm-a W87 / bm-c W88 registrations may land mid-window);
every state converges on the same final bands:
  A 221_004..223_003 (skip-past-published chain W86 tail -> W87 pub -> W88
     pub -> first clean, width 2_000, CLEAN)
  B 56_001..56_200   (chain: 55_401..55_600 doubly refused [W87 pub overlap
     + SEED_REGISTRY grid_p1=55_500 median] -> W87 pub 55_501..55_700 ->
     W88 pub 55_701..55_900 -> 55_901..56_100 REFUSED at SEED_REGISTRY
     ths_agg_p1=56_000 in-window MEDIAN hit (zero-indexed 99/199, non-edge)
     -> D-20261002-05 pinned semantics: hit+1 restart 56_001..56_200 CLEAN;
     window-step chain reading 56_101..56_300 disclosed NOT taken per the
     pinned law)

Machine-verified against: all registered N1 wave bands (W2..W86 [+W87/W88
in whichever state]), the W87+W88 published projections, N3-R1 used-seed
band 70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options draws.

r577 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W89_A = (221_004, 223_003)
W89_B = (56_001, 56_200)
W87_PUB_A = (217_004, 219_003)   # bm-a seat MSG-20261002-1345-bma-w87-seat
W87_PUB_B = (55_501, 55_700)
W88_PUB_A = (219_004, 221_003)   # bm-c seat MSG (origin-first r511)
W88_PUB_B = (55_701, 55_900)

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
tails = {86: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 87)),
         87: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 88)),
         88: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 89))}
REG87 = 87 in N1_BANDS
REG88 = 88 in N1_BANDS
assert keys == tails[86] or keys == tails[87] or keys == tails[88], \
    f"leg0 failed: unexpected registry keys tail {keys[-4:]}"
if REG87:
    assert N1_BANDS[87]["a"] == W87_PUB_A and \
        N1_BANDS[87]["b_exit"] == W87_PUB_B and \
        N1_BANDS[87].get("engine_owner") == "bm-a", "leg0 failed: W87 drift"
    bands.append(W87_PUB_A); bands.append(W87_PUB_B)
if REG88:
    assert N1_BANDS[88]["a"] == W88_PUB_A and \
        N1_BANDS[88]["b_exit"] == W88_PUB_B and \
        N1_BANDS[88].get("engine_owner") == "bm-c", "leg0 failed: W88 drift"
    bands.append(W88_PUB_A); bands.append(W88_PUB_B)
if not REG87:
    bands.append(W87_PUB_A); bands.append(W87_PUB_B)
if not REG88:
    bands.append(W88_PUB_A); bands.append(W88_PUB_B)
MODE = ("B87" if REG87 else "A87") + ("+B88" if REG88 else "+A88") + \
    " (" + ("registered" if REG87 else "seat-published") + " W87 / " + \
    ("registered" if REG88 else "seat-published") + " W88)"
assert N1_BANDS[86]["a"] == (215_004, 217_003) and \
    N1_BANDS[86]["b_exit"] == (55_201, 55_400) and \
    N1_BANDS[86].get("engine_owner") == "bm-a", "leg0 failed: W86 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} (+W87/W88 seats in flight) "
      f"+ candidate; bm-b rows={len(bmb_rows)} -> W89 = bm-b "
      f"{len(bmb_rows) + 1}th owned")

# --- leg 0b: seat MSGs on origin (published=reserved face) --------------------
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
_bmc_body = _seat_on_origin(_bmc, ["219_004..221_003", "55_701..55_900"])
print(f"leg0b: bm-a W87 + bm-c W88 seat MSGs verified on origin "
      f"(published=reserved r518-1); bm-c seat = {_bmc}")

# --- leg 1: skip-past-published chain (mode-aware) ----------------------------
if REG88:
    tail = N1_BANDS[88]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W89_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == (55_901, 56_100), f"leg1-B drift: {ARITH_B}"
elif REG87:
    tail = N1_BANDS[87]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W88_PUB_A and ARITH_B == W88_PUB_B, \
        f"leg1 drift vs W88 published: {ARITH_A} {ARITH_B}"
    print(f"leg1: arithmetic {ARITH_A[0]}..{ARITH_A[1]} / "
          f"{ARITH_B[0]}..{ARITH_B[1]} REFUSED by the W88 published "
          f"projection (reserved face r518-1) -> skip-past-published")
else:
    tail = N1_BANDS[86]
    ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
    ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
    assert ARITH_A == W87_PUB_A, f"leg1-A drift: {ARITH_A}"
    assert ARITH_B == (55_401, 55_600), f"leg1-B drift: {ARITH_B}"
    a_ref = [b for b in bands if overlaps(b, ARITH_A) and b != W87_PUB_A]
    b_band_ref = [b for b in bands if overlaps(b, ARITH_B)]
    b_point_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
    assert not a_ref, f"leg1-A failed: {a_ref}"
    assert b_band_ref == [W87_PUB_B] and b_point_hits == [55_500], \
        f"leg1-B failed: {b_band_ref} {b_point_hits}"
    print(f"leg1: arithmetic {ARITH_A[0]}..{ARITH_A[1]} / "
          f"{ARITH_B[0]}..{ARITH_B[1]} REFUSED by the W87 published face "
          f"(B doubly refused: W87-pub overlap + grid_p1=55_500 median hit) "
          f"-> skip-past-published chain")

# chain walk (all states): from the W86 registered tail, walk A and B
# forward past every published/registered band, applying the hit+1 pin.
def next_band_a(after_hi):
    return (after_hi + 1, after_hi + WIDTH_A)

def next_band_b(after_hi):
    return (after_hi + 1, after_hi + WIDTH_B)

pub_a = sorted({W87_PUB_A, W88_PUB_A} | {
    tuple(N1_BANDS[w]["a"]) for w in (87, 88) if w in N1_BANDS})
pub_b = sorted({W87_PUB_B, W88_PUB_B} | {
    tuple(N1_BANDS[w]["b_exit"]) for w in (87, 88) if w in N1_BANDS})
cur_a = N1_BANDS[86]["a"]
for pb in pub_a:
    cand = next_band_a(cur_a[1])
    a_ref = [b for b in bands if overlaps(b, cand) and b != pb]
    assert not a_ref, f"leg1 chain-A failed at {cand}: {a_ref}"
    assert cand == pb, f"leg1 chain-A drift: {cand} != {pb} (published face)"
    cur_a = pb
final_a = next_band_a(cur_a[1])
assert final_a == W89_A, f"leg1 chain-A final drift: {final_a}"
a_fin_hits = sorted(p for p in points if final_a[0] <= p <= final_a[1]) or \
    [b for b in bands + actual if overlaps(b, final_a)]
assert not a_fin_hits, f"leg1 chain-A final not clean: {a_fin_hits}"
print(f"leg1 chain-A: W86 tail -> W87 pub -> W88 pub -> "
      f"{final_a[0]}..{final_a[1]} CLEAN (skip-past-published, r518-1)")

cur_lo = N1_BANDS[86]["b_exit"][1] + 1
chain_b_steps = []
final_b = None
guard = 0
while final_b is None:
    guard += 1
    assert guard < 50, "leg1 chain-B scan did not converge"
    w = (cur_lo, cur_lo + WIDTH_B - 1)
    pt = sorted(p for p in points if w[0] <= p <= w[1])
    bd = [b for b in bands if overlaps(b, w)]
    if not pt and not bd:
        final_b = w
        chain_b_steps.append(f"{w[0]}..{w[1]} CLEAN (first clean window)")
        break
    if pt:
        chain_b_steps.append(
            f"{w[0]}..{w[1]} REFUSED at SEED_REGISTRY point {pt} "
            f"-> D-20261002-05 pinned hit+1 restart {pt[0] + 1}")
        cur_lo = pt[0] + 1
    else:
        tagpb = "W87 published" if bd[0] in (W87_PUB_B,) else \
            ("W88 published" if bd[0] in (W88_PUB_B,) else f"band {bd[0]}")
        chain_b_steps.append(
            f"{w[0]}..{w[1]} REFUSED by {tagpb} band "
            f"{bd[0][0]}..{bd[0][1]} -> skip-past-published")
        cur_lo = bd[0][1] + 1
for s in chain_b_steps:
    print(f"leg1 chain-B: {s}")
arith_b = (55_901, 56_100)
b_hits = sorted(p for p in points if arith_b[0] <= p <= arith_b[1])
b_band_ref = [b for b in bands + actual if overlaps(b, arith_b)]
assert b_hits == [56_000] and not b_band_ref, \
    f"leg1 chain-B final-window failed: expect [56_000], got {b_hits} {b_band_ref}"
reg56 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 56_000]
assert reg56 == ["ths_agg_p1"], f"leg1 chain-B: 56_000 key drift {reg56}"
pos = 56_000 - arith_b[0]  # zero-indexed position inside the window
assert pos == 99 and arith_b[1] - arith_b[0] == 199, \
    f"leg1 chain-B: 56_000 must be the in-window MEDIAN (99/199), got pos {pos}"
pinned_b = (56_000 + 1, 56_000 + WIDTH_B)
assert final_b == pinned_b == W89_B, \
    f"leg1 chain-B pin drift: {final_b} != {pinned_b}"
print(f"leg1 chain-B: final window {arith_b[0]}..{arith_b[1]} REFUSED at "
      f"SEED_REGISTRY ths_agg_p1=56_000 in-window MEDIAN hit (99/199 "
      f"non-edge) -> D-20261002-05 pinned: hit+1 restart "
      f"{pinned_b[0]}..{pinned_b[1]} (window-step chain reading 56_101.."
      f"56_300 disclosed NOT taken per the pinned law)")

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

start_a = (W88_PUB_A[1] + 1)
first_a = clean(start_a, WIDTH_A)
assert first_a == W89_A, f"leg2-A failed: {first_a} != {W89_A}"
start_b = 56_001
first_b = None
lo = start_b
while first_b is None and lo < start_b + 10 * WIDTH_B:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
    else:
        hit = [p for p in points if lo <= p <= lo + WIDTH_B - 1]
        lo = (hit[0] + 1) if hit else lo + WIDTH_B
assert first_b == W89_B, f"leg2-B failed: {first_b} != {W89_B} (hit+1 chain)"
print(f"leg2: A first-clean {W89_A[0]}..{W89_A[1]} == candidate; "
      f"B first-clean {W89_B[0]}..{W89_B[1]} == candidate (hit+1 restart)")
assert not overlaps(W89_A, W89_B), "A/B overlap"

# --- leg 3: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W89_A), ("B", W89_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W89-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W89-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W89-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W89-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W89-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W89-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W89-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W89-{tag} (r335 leg)")
    for nm, pb in (("W87pub", (W87_PUB_A if tag == "A" else W87_PUB_B)),
                   ("W88pub", (W88_PUB_A if tag == "A" else W88_PUB_B))):
        if overlaps(pb, band):
            conflicts.append(f"{nm} band x W89-{tag}")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "89: {\"a\": (221_004" not in out, \
    "leg3 failed: W89 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W89"' not in outn1, \
    "leg3 failed: W89 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W89_PREREEG.md", "research/PERPETUAL_N1_W89_PREREG.md"],
    encoding="utf-8").strip()
assert not outpre, "leg3 failed: W89 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W89 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W89 ADMIT: A {W89_A[0]}..{W89_A[1]} + B {W89_B[0]}..{W89_B[1]} "
      f"(mode={MODE}; refusal facts: W87+W88 published skip-past chain + "
      "SEED_REGISTRY ths_agg_p1=56_000 in-window median hit, D-20261002-05 "
      "pinned hit+1 restart) -- clean vs all registered rows + W87/W88 "
      "reserved faces + registry + probes/actuals -- engine_owner=bm-b "
      "(yield receipt + seat published=reserved pushed BEFORE this freeze "
      "per r565 early-visibility law). NOT a re-pick (R250: W89 bands were "
      "never assigned).")

# --- W90+ projection (warning text for the law table row) --------------------
w90_a = (W89_A[1] + 1, W89_A[1] + WIDTH_A)
w90_b = (W89_B[1] + 1, W89_B[1] + WIDTH_B)
a_hits90 = sorted(p for p in points if w90_a[0] <= p <= w90_a[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w90_a)]
b_hits90 = sorted(p for p in points if w90_b[0] <= p <= w90_b[1]) or \
    [f"band {b}" for b in bands + actual if overlaps(b, w90_b)]
print(f"W90+ projection: A arithmetic +2_000 = {w90_a[0]}..{w90_a[1]} "
      f"-> {'CLEAN (verify at W90 prereg)' if not a_hits90 else 'REFUSED ' + str(a_hits90)}; "
      f"B +200 from W89 end = {w90_b[0]}..{w90_b[1]} "
      f"-> {'CLEAN (verify at W90 prereg)' if not b_hits90 else 'REFUSED ' + str(b_hits90)}")
