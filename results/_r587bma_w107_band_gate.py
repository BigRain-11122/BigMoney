# -*- coding: utf-8 -*-
"""W107 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W107 candidate = first FREE number after the REGISTERED W106 row (bm-b r585
freeze d6b2952e3, bands A 255_004..257_003 / B 60_201..60_400). SINGLE STATE
zero seat gap: W2..W106 all registered (W104 bm-a union 48f6f2ff1 + W105 bm-c
f2db133c5 + W106 bm-b d6b2952e3). Own seat MSG-20261002-1759-bma published=
reserved, pushed to origin d548df902 BEFORE this freeze per r565 law.

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 257_004..259_003  (arithmetic continuation from the registered W106 A tail)
  B 60_401..60_600    (arithmetic continuation from the registered W106 B tail)

r587 bm-a freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W107_A = (257_004, 259_003)
W107_B = (60_401, 60_600)
W106_TAIL_A = (255_004, 257_003)   # registered W106 (bm-b r585, live table tail)
W106_TAIL_B = (60_201, 60_400)
OWN_SEAT = "MSG-20261002-1759-bma"

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
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 107))
assert keys == expect_keys, f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[106]["a"] == W106_TAIL_A and \
    N1_BANDS[106]["b_exit"] == W106_TAIL_B and \
    N1_BANDS[106].get("engine_owner") == "bm-b", "leg0 failed: W106 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 96, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 96)"
assert len(bma_rows) == 29, f"leg0 failed: bm-a rows {len(bma_rows)} (expect 29)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W106 bm-b registered); "
      f"engine_owner rows={len(owner_rows)} + candidate -> W107 = 97th engine wave, "
      f"bm-a {len(bma_rows) + 1}th owned wave by machine-derive")

# --- leg 0b: NO peer W107 seat claim on origin (own seat allowed) --------------
peer_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w107" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W107 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", "fleet/inbox/"],
                    capture_output=True, creationflags=CREAT)
_names = _r.stdout.decode("utf-8", "replace")
assert OWN_SEAT in _names, "leg0b failed: own W107 seat MSG NOT on origin inbox (r565 missing)"
print("leg0b: zero PEER W107 seat MSGs on origin; own seat MSG-20261002-1759-bma on origin confirmed (r565 law)")

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

ca, hops_a = first_clean(W106_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W106_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W107_A, f"leg1-A failed: derived {ca} != {W107_A}"
assert cb == W107_B, f"leg1-B failed: derived {cb} != {W107_B}"
print(f"leg1: A {W107_A[0]}..{W107_A[1]} CLEAN + B {W107_B[0]}..{W107_B[1]} CLEAN "
      f"(arithmetic continuation from the registered W106 tails; hops A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ------------------
conflicts = []
for tag, band in (("A", W107_A), ("B", W107_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W107-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W107-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W107-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W107-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W107-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W107-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W107-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W107-{tag}")
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "107: {\"a\": (257_004" not in out, "leg2 failed: W107 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W107"' not in outn1, "leg2 failed: W107 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W107_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W107 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W107 REFUSED:")
    for c in conflicts: print("  -", c)
    sys.exit(1)
print(f"W107 ADMIT: A {W107_A[0]}..{W107_A[1]} + B {W107_B[0]}..{W107_B[1]} "
      f"(arithmetic continuation from the registered W106 tails) -- clean vs all "
      f"registered rows + registry + probes/actuals -- engine_owner=bm-a (own seat "
      f"MSG-20261002-1759-bma on origin BEFORE this freeze per r565). NOT a re-pick "
      f"(R250: W107 bands were never assigned).")

# --- W108+ projection ----------------------------------------------------------
w108_a = (W107_A[1] + 1, W107_A[1] + WIDTH_A)
w108_b = (W107_B[1] + 1, W107_B[1] + WIDTH_B)
a_hits = sorted(p for p in points if w108_a[0] <= p <= w108_a[1]) or \
    [f"band {b}" for b in bands + pub_bands if overlaps(b, w108_a)]
b_hits = sorted(p for p in points if w108_b[0] <= p <= w108_b[1]) or \
    [f"band {b}" for b in bands + pub_bands if overlaps(b, w108_b)]
print(f"W108+ projection: A {w108_a[0]}..{w108_a[1]} "
      f"-> {'CLEAN (verify at W108 prereg)' if not a_hits else 'REFUSED ' + str(a_hits)}; "
      f"B {w108_b[0]}..{w108_b[1]} "
      f"-> {'CLEAN (verify at W108 prereg)' if not b_hits else 'REFUSED ' + str(b_hits)}")
