# -*- coding: utf-8 -*-
"""W112 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W112 candidate = first FREE number after the REGISTERED W111 row (bm-b r589
freeze e0a103ec1, bands A 265_004..267_003 / B 61_401..61_600). SINGLE STATE
zero seat gap: W2..W111 all registered (W110 bm-a ff0b1869b + W111 bm-b
e0a103ec1). Own seat MSG-20261002-1922-bma published=reserved, pushed to
origin e9f157e25 BEFORE this freeze per r565 law (surgical push over bm-b
r589 closing 3b7da8dfe, payload=1 seat MSG, deletion-set EMPTY).

Bands (machine-derived, NOT transcribed -- r335/r535/r587 law):
  A 267_004..269_003  (arithmetic continuation from the registered W111 A tail)
  B 61_601..61_800    (arithmetic continuation from the registered W111 B tail)

r590 bm-a freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W112_A = (267_004, 269_003)
W112_B = (61_601, 61_800)
W111_TAIL_A = (265_004, 267_003)   # registered W111 (bm-b r589, live table tail)
W111_TAIL_B = (61_401, 61_600)
OWN_SEAT = "MSG-20261002-1922-bma"

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

subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True, creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)

# --- leg 0: registry shape + registered-tail parity ---------------------------
keys = sorted(N1_BANDS)
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 112))
assert keys == expect_keys, f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[110]["a"] == (263_004, 265_003) and \
    N1_BANDS[110]["b_exit"] == (61_201, 61_400) and \
    N1_BANDS[110].get("engine_owner") == "bm-a", "leg0 failed: W110 row drift"
assert N1_BANDS[111]["a"] == W111_TAIL_A and \
    N1_BANDS[111]["b_exit"] == W111_TAIL_B and \
    N1_BANDS[111].get("engine_owner") == "bm-b", "leg0 failed: W111 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 101, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 101)"
assert len(bma_rows) == 31, f"leg0 failed: bm-a rows {len(bma_rows)} (expect 31)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W111 bm-b registered); "
      f"engine_owner rows={len(owner_rows)} + candidate -> W112 = 102nd engine wave, "
      f"bm-a {len(bma_rows) + 1}th owned wave by machine-derive")

# --- leg 0b: NO peer W112 seat claim on origin (own seat allowed; r374 dual-dir) -
peer_claims = []
own_seen = False
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w112" in _ln.lower() and "seat" in _ln.lower():
            if OWN_SEAT in _ln:
                own_seen = True
            else:
                peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W112 seat MSG on origin: {peer_claims}"
assert own_seen, "leg0b failed: own W112 seat MSG NOT on origin (r565 missing)"
print(f"leg0b: zero PEER W112 seat MSGs on origin (inbox+processed dual-dir r374); "
      f"own seat {OWN_SEAT} on origin confirmed (r565 law)")

# --- leg 1: first-clean-window derive ------------------------------------------
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
pub_bands = []

def first_clean(start, width, tag):
    lo = start; hops = 0
    while True:
        hi = lo + width - 1
        hit = None
        for p in points:
            if lo <= p <= hi:
                hit = p; break
        if hit is None:
            for b in bands + pub_bands + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
                if overlaps((lo, hi), b):
                    hit = f"band {b}"; break
        if hit is None:
            return (lo, hi), hops
        nxt = (hit + 1) if isinstance(hit, int) else hi + 1
        print(f"  refusal-scan {tag}: window {lo}..{hi} refused at {hit} -> restart {nxt} (D-20261002-05)")
        lo = nxt; hops += 1
        assert hops < 50, "refusal scan runaway"

ca, hops_a = first_clean(W111_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W111_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W112_A, f"leg1-A failed: derived {ca} != {W112_A}"
assert cb == W112_B, f"leg1-B failed: derived {cb} != {W112_B}"
print(f"leg1: A {W112_A[0]}..{W112_A[1]} CLEAN + B {W112_B[0]}..{W112_B[1]} CLEAN "
      f"(arithmetic continuation from the registered W111 tails; hops A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ------------------
conflicts = []
for tag, band in (("A", W112_A), ("B", W112_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W112-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W112-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W112-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W112-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W112-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W112-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W112-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W112-{tag} (r335 leg)")
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "112: {\"a\": (267_004" not in out, "leg2 failed: W112 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W112"' not in outn1, "leg2 failed: W112 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W112_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W112 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W112 REFUSED:")
    for c in conflicts: print("  -", c)
    sys.exit(1)
print(f"W112 ADMIT: A {W112_A[0]}..{W112_A[1]} + B {W112_B[0]}..{W112_B[1]} "
      f"(arithmetic continuation from the registered W111 tails) -- clean vs all "
      f"registered rows + registry + probes/actuals -- engine_owner=bm-a (own seat "
      f"MSG-20261002-1922-bma on origin BEFORE this freeze per r565, surgical "
      f"e9f157e25). NOT a re-pick (R250: W112 bands were never assigned).")

# --- W113+ projection ----------------------------------------------------------
w113_a = (W112_A[1] + 1, W112_A[1] + WIDTH_A)
w113_b = (W112_B[1] + 1, W112_B[1] + WIDTH_B)
(fc113_a, h113a) = first_clean(w113_a[0], WIDTH_A, "W113-A")
(fc113_b, h113b) = first_clean(w113_b[0], WIDTH_B, "W113-B")
who113 = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 62_000]
print(f"W113+ projection: A first-clean {fc113_a[0]}..{fc113_a[1]} hops={h113a} "
      f"-> CLEAN (verify at W113 prereg); "
      f"B arithmetic {w113_b[0]}..{w113_b[1]} REFUSED at SEED_REGISTRY "
      f"{who113}=62_000 (D-20261002-05 jump law) -> first-clean {fc113_b[0]}..{fc113_b[1]} "
      f"hops={h113b} (verify at W113 prereg)")
