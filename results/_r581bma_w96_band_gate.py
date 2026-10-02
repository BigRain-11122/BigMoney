# -*- coding: utf-8 -*-
"""W96 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W96 candidate = first FREE number after the registered W95 row (bm-b r580
freeze, landed origin 70b32c101). SINGLE STATE (W95 registered, no seat
gap): arithmetic continuation from the W95 tails; refusal scan per the
D-20261002-05 pin semantics if any point hits.

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 235_004..237_003  (W95 A tail 235_003 + 1, stride 2_000) -- verify CLEAN
  B 57_701..57_900    (W95 B tail 57_700 + 1, stride 200) -- verify CLEAN

Machine-verified against: all registered N1 wave bands (W2..W95 live),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), probe
cluster 95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, live
SEED_REGISTRY values, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actuals, and the bm-a W96 seat MSG-20261002-1531 (own, on
origin per r565; NO peer W96 seat allowed).

r581 bm-a freeze-window run. READ-ONLY vs the live table + origin.
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

W96_A = (235_004, 237_003)        # candidate (derived, gate must confirm)
W96_B = (57_701, 57_900)
W95_TAIL_A = (233_004, 235_003)   # registered W95 (bm-b r580, live table tail)
W95_TAIL_B = (57_501, 57_700)
OWN_SEAT = "MSG-20261002-1531-bma"   # own W96 seat MSG (pushed pre-freeze r565)

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

# --- leg 0: registry shape + registered-tail parity ---------------------------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 96)), \
    f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[95]["a"] == W95_TAIL_A and \
    N1_BANDS[95]["b_exit"] == W95_TAIL_B and \
    N1_BANDS[95].get("engine_owner") == "bm-b", "leg0 failed: W95 row drift"
assert N1_BANDS[94]["a"] == (231_004, 233_003) and \
    N1_BANDS[94]["b_exit"] == (57_301, 57_500) and \
    N1_BANDS[94].get("engine_owner") == "bm-a", "leg0 failed: W94 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 85, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 85)"
assert len(bma_rows) == 25, \
    f"leg0 failed: bm-a rows {len(bma_rows)} (expect 25)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W95 bm-b, "
      f"single state zero seat gap); engine_owner rows={len(owner_rows)} + "
      f"candidate -> W96 = bm-a 26th owned, EIGHTY-SIXTH engine wave by "
      f"machine-derive (85 registered + candidate)")

# --- leg 0b: NO peer W96 seat claim on origin (own seat allowed) ---------------
peer_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w96" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W96 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
assert OWN_SEAT in _r.stdout.decode("utf-8", "replace"), \
    "leg0b failed: own W96 seat MSG NOT on origin (r565 pre-freeze push missing)"
print("leg0b: zero PEER W96 seat MSGs on origin (inbox+processed scanned); "
      "own seat MSG-20261002-1531-bma on origin confirmed (r565 law)")

# --- leg 0c: W95 seat MSG on origin (upstream published seat) ------------------
_names = _r.stdout.decode("utf-8", "replace")
assert "MSG-20261002-1536-bmb" in _names, \
    "leg0c failed: bm-b W95 seat MSG not on origin (upstream published seat missing)"
print("leg0c: bm-b W95 seat MSG on origin confirmed (upstream published seat)")

# --- leg 1: first-clean-window derive (arithmetic continuation + refusal scan) -
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))

def first_clean(start, width, tag):
    lo = start
    hops = 0
    while True:
        hi = lo + width - 1
        hit = None
        for p in points:
            if lo <= p <= hi:
                hit = p
                break
        if hit is None:
            for b in bands + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
                if overlaps((lo, hi), b):
                    hit = f"band {b}"
                    break
        if hit is None:
            return (lo, hi), hops
        # D-20261002-05 pinned semantics: past-hit restart (hit + 1)
        nxt = (hit + 1) if isinstance(hit, int) else (b[1] + 1 if False else hi + 1)
        print(f"  refusal-scan {tag}: window {lo}..{hi} refused at {hit} -> "
              f"past-hit restart {nxt} (D-20261002-05)")
        lo = nxt
        hops += 1
        assert hops < 50, "refusal scan runaway"

ca, hops_a = first_clean(W95_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W95_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W96_A, f"leg1-A failed: derived first-clean {ca} != {W96_A}"
assert cb == W96_B, f"leg1-B failed: derived first-clean {cb} != {W96_B}"
print(f"leg1: A {W96_A[0]}..{W96_A[1]} CLEAN + B {W96_B[0]}..{W96_B[1]} CLEAN "
      f"(arithmetic continuation from the W95 tails, single state; refusal "
      f"hops A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W96_A), ("B", W96_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W96-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W96-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W96-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W96-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W96-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W96-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W96-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W96-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "96: {\"a\": (235_004" not in out, \
    "leg2 failed: W96 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W96"' not in outn1, \
    "leg2 failed: W96 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W96_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W96 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W96 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W96 ADMIT: A {W96_A[0]}..{W96_A[1]} + B {W96_B[0]}..{W96_B[1]} "
      f"(arithmetic continuation from the registered W95 tails, single "
      f"state; zero refusal points both sides) -- clean vs all registered "
      f"rows + registry + probes/actuals -- engine_owner=bm-a (own seat "
      f"MSG-20261002-1531-bma on origin BEFORE this freeze per r565). "
      f"NOT a re-pick (R250: W96 bands were never assigned).")

# --- W97+ projection (warning text for the law table row) --------------------
w97_a = (W96_A[1] + 1, W96_A[1] + WIDTH_A)
w97_b = (W96_B[1] + 1, W96_B[1] + WIDTH_B)
a_hits97 = sorted(p for p in points if w97_a[0] <= p <= w97_a[1]) or \
    [f"band {b}" for b in bands if overlaps(b, w97_a)]
b_hits97 = sorted(p for p in points if w97_b[0] <= p <= w97_b[1]) or \
    [f"band {b}" for b in bands if overlaps(b, w97_b)]
print(f"W97+ projection: A arithmetic +2_000 = {w97_a[0]}..{w97_a[1]} "
      f"-> {'CLEAN (verify at W97 prereg)' if not a_hits97 else 'REFUSED ' + str(a_hits97)}; "
      f"B +200 from W96 end = {w97_b[0]}..{w97_b[1]} "
      f"-> {'CLEAN (verify at W97 prereg)' if not b_hits97 else 'REFUSED ' + str(b_hits97)}")
