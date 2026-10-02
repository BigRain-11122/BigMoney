# -*- coding: utf-8 -*-
"""W113 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W113 candidate = first FREE number after the REGISTERED W112 row (bm-a r590
freeze 0c4d67910, bands A 267_004..269_003 / B 61_601..61_800). SINGLE STATE
zero seat gap: W2..W112 all registered (W111 bm-b e0a103ec1 + W112 bm-a
0c4d67910). Own seat MSG-20261002-1949-bmc published=reserved, pushed to
origin baa0c3888 BEFORE this freeze per r565 law (clean single-file push,
deletion-set EMPTY).

Bands (machine-derived, NOT transcribed -- r335/r535/r587 law):
  A 269_004..271_003  (arithmetic continuation from the registered W112 A tail)
  B 62_001..62_200    (jump-past-hit window: arithmetic 61_801..62_000 refused
                       at SEED_REGISTRY cta_wave1=62_000, D-20261002-05)

r382 bm-c freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W113_A = (269_004, 271_003)
W113_B = (62_001, 62_200)
W112_TAIL_A = (267_004, 269_003)   # registered W112 (bm-a r590, live table tail)
W112_TAIL_B = (61_601, 61_800)
OWN_SEAT = "MSG-20261002-1949-bmc"

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
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 113))
assert keys == expect_keys, f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[109]["a"] == (261_004, 263_003) and \
    N1_BANDS[109]["b_exit"] == (61_001, 61_200) and \
    N1_BANDS[109].get("engine_owner") == "bm-b", "leg0 failed: W109 row drift"
assert N1_BANDS[110]["a"] == (263_004, 265_003) and \
    N1_BANDS[110]["b_exit"] == (61_201, 61_400) and \
    N1_BANDS[110].get("engine_owner") == "bm-a", "leg0 failed: W110 row drift"
assert N1_BANDS[111]["a"] == (265_004, 267_003) and \
    N1_BANDS[111]["b_exit"] == (61_401, 61_600) and \
    N1_BANDS[111].get("engine_owner") == "bm-b", "leg0 failed: W111 row drift"
assert N1_BANDS[112]["a"] == W112_TAIL_A and \
    N1_BANDS[112]["b_exit"] == W112_TAIL_B and \
    N1_BANDS[112].get("engine_owner") == "bm-a", "leg0 failed: W112 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(owner_rows) == 102, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 102)"
assert len(bmc_rows) == 32, f"leg0 failed: bm-c rows {len(bmc_rows)} (expect 32)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W112 bm-a registered); "
      f"engine_owner rows={len(owner_rows)} + candidate -> W113 = 103rd engine wave, "
      f"bm-c {len(bmc_rows) + 1}th owned wave by machine-derive")

# --- leg 0b: NO peer W113 seat claim on origin (own seat allowed; r374 dual-dir) -
peer_claims = []
own_seen = False
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w113" in _ln.lower() and "seat" in _ln.lower():
            if OWN_SEAT in _ln:
                own_seen = True
            else:
                peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W113 seat MSG on origin: {peer_claims}"
assert own_seen, "leg0b failed: own W113 seat MSG NOT on origin (r565 missing)"
print(f"leg0b: zero PEER W113 seat MSGs on origin (inbox+processed dual-dir r374); "
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

ca, hops_a = first_clean(W112_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W112_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W113_A, f"leg1-A failed: derived {ca} != {W113_A}"
assert cb == W113_B, f"leg1-B failed: derived {cb} != {W113_B}"
print(f"leg1: A {W113_A[0]}..{W113_A[1]} CLEAN + B {W113_B[0]}..{W113_B[1]} CLEAN "
      f"(A = arithmetic continuation from the registered W112 A tail; B = "
      f"jump-past-hit window over SEED_REGISTRY cta_wave1=62_000 window-tail "
      f"endpoint, D-20261002-05; hops A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ------------------
conflicts = []
for tag, band in (("A", W113_A), ("B", W113_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W113-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W113-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W113-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W113-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W113-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W113-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W113-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W113-{tag} (r335 leg)")
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT, encoding="utf-8")
assert "113: {\"a\": (269_004" not in out, "leg2 failed: W113 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT, encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W113"' not in outn1, "leg2 failed: W113 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W113_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W113 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W113 REFUSED:")
    for c in conflicts: print("  -", c)
    sys.exit(1)
print(f"W113 ADMIT: A {W113_A[0]}..{W113_A[1]} + B {W113_B[0]}..{W113_B[1]} "
      f"(arithmetic continuation A + jump-past-hit B per D-20261002-05) -- clean vs all "
      f"registered rows + registry + probes/actuals -- engine_owner=bm-c (own seat "
      f"MSG-20261002-1949-bmc on origin BEFORE this freeze per r565, clean push "
      f"baa0c3888). NOT a re-pick (R250: W113 bands were never assigned).")

# --- W114+ projection ----------------------------------------------------------
w114_a = (W113_A[1] + 1, W113_A[1] + WIDTH_A)
w114_b = (W113_B[1] + 1, W113_B[1] + WIDTH_B)
(fc114_a, h114a) = first_clean(w114_a[0], WIDTH_A, "W114-A")
(fc114_b, h114b) = first_clean(w114_b[0], WIDTH_B, "W114-B")
print(f"W114+ projection: A first-clean {fc114_a[0]}..{fc114_a[1]} hops={h114a} "
      f"-> CLEAN (verify at W114 prereg); "
      f"B first-clean {fc114_b[0]}..{fc114_b[1]} hops={h114b} "
      f"-> CLEAN (verify at W114 prereg)")
