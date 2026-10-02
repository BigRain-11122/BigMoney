# -*- coding: utf-8 -*-
"""W114 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W114 candidate = first FREE number after the REGISTERED W113 row (bm-c r382
freeze eeb062290, bands A 269_004..271_003 / B 62_001..62_200). SINGLE STATE
zero seat gap: W2..W113 all registered (W112 bm-a 0c4d67910 + W113 bm-c
eeb062290). Own seat MSG-20261002-2014-bma published=reserved, pushed to
origin 2cd67216a BEFORE this freeze per r565 law (one r589 reset-FF-reland
loop over the bm-c appender 3-shard mid-window advance; payload=1 seat MSG,
deletion-set EMPTY, rev.A = only published face).

Bands (machine-derived, NOT transcribed -- r335/r535/r587 law):
  A 271_004..273_003  (arithmetic continuation from the registered W113 A tail)
  B 62_201..62_400    (arithmetic continuation from the registered W113 B tail)

r592 bm-a freeze-window run. READ-ONLY vs the live table + origin.
Pinned skip semantics (D-20261002-05): mid-window hits restart at hit+1
(越 hit 起窗), NOT window-step-chain -- the first_clean below implements the
pinned law (mirror of the r382 bm-c gate).
"""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W114_A = (271_004, 273_003)
W114_B = (62_201, 62_400)
W113_TAIL_A = (269_004, 271_003)   # registered W113 (bm-c r382, live table tail)
W113_TAIL_B = (62_001, 62_200)
OWN_SEAT = "MSG-20261002-2014-bma"

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
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 114))
assert keys == expect_keys, f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[110]["a"] == (263_004, 265_003) and \
    N1_BANDS[110]["b_exit"] == (61_201, 61_400) and \
    N1_BANDS[110].get("engine_owner") == "bm-a", "leg0 failed: W110 row drift"
assert N1_BANDS[111]["a"] == (265_004, 267_003) and \
    N1_BANDS[111]["b_exit"] == (61_401, 61_600) and \
    N1_BANDS[111].get("engine_owner") == "bm-b", "leg0 failed: W111 row drift"
assert N1_BANDS[112]["a"] == (267_004, 269_003) and \
    N1_BANDS[112]["b_exit"] == (61_601, 61_800) and \
    N1_BANDS[112].get("engine_owner") == "bm-a", "leg0 failed: W112 row drift"
assert N1_BANDS[113]["a"] == W113_TAIL_A and \
    N1_BANDS[113]["b_exit"] == W113_TAIL_B and \
    N1_BANDS[113].get("engine_owner") == "bm-c", "leg0 failed: W113 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 103, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 103)"
assert len(bma_rows) == 32, f"leg0 failed: bm-a rows {len(bma_rows)} (expect 32)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W113 bm-c registered); "
      f"engine_owner rows={len(owner_rows)} + candidate -> W114 = 104th engine wave, "
      f"bm-a {len(bma_rows) + 1}th owned wave by machine-derive")

# --- leg 0b: NO peer W114 seat claim on origin (own seat allowed; r374 dual-dir) -
peer_claims = []
own_seen = False
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w114" in _ln.lower() and "seat" in _ln.lower():
            if OWN_SEAT in _ln:
                own_seen = True
            else:
                peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W114 seat MSG on origin: {peer_claims}"
assert own_seen, "leg0b failed: own W114 seat MSG NOT on origin (r565 missing)"
print(f"leg0b: zero PEER W114 seat MSGs on origin (inbox+processed dual-dir r374); "
      f"own seat {OWN_SEAT} on origin confirmed (r565 law)")

# --- leg 1: first-clean-window derive (pinned D-20261002-05: mid-window hit -> hit+1) --
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

ca, hops_a = first_clean(W113_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W113_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W114_A, f"leg1-A failed: derived {ca} != {W114_A}"
assert cb == W114_B, f"leg1-B failed: derived {cb} != {W114_B}"
print(f"leg1: A {W114_A[0]}..{W114_A[1]} CLEAN + B {W114_B[0]}..{W114_B[1]} CLEAN "
      f"(both = arithmetic continuation from the registered W113 tails; "
      f"hops A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ------------------
conflicts = []
for tag, band in (("A", W114_A), ("B", W114_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W114-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W114-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W114-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W114-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W114-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W114-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W114-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W114-{tag} (r335 leg)")
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT, encoding="utf-8")
assert "114: {\"a\": (271_004" not in out, "leg2 failed: W114 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT, encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W114"' not in outn1, "leg2 failed: W114 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W114_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W114 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W114 REFUSED:")
    for c in conflicts: print("  -", c)
    sys.exit(1)
print(f"W114 ADMIT: A {W114_A[0]}..{W114_A[1]} + B {W114_B[0]}..{W114_B[1]} "
      f"(both = arithmetic continuation from the registered W113 tails) -- clean vs all "
      f"registered rows + registry + probes/actuals -- engine_owner=bm-a (own seat "
      f"MSG-20261002-2014-bma on origin BEFORE this freeze per r565, push "
      f"2cd67216a via one r589 reset-FF-reland loop). NOT a re-pick (R250: W114 "
      f"bands were never assigned).")

# --- W115+ projection (pinned D-20261002-05 semantics: mid-window hit -> hit+1) --
w115_a = (W114_A[1] + 1, W114_A[1] + WIDTH_A)
w115_b = (W114_B[1] + 1, W114_B[1] + WIDTH_B)
(fc115_a, h115a) = first_clean(w115_a[0], WIDTH_A, "W115-A")
(fc115_b, h115b) = first_clean(w115_b[0], WIDTH_B, "W115-B")
who115b = [k for k, v in science_gates.SEED_REGISTRY.items() if v in
           range(w115_b[0], w115_b[1] + 1)]
print(f"W115+ projection (pinned law): A first-clean {fc115_a[0]}..{fc115_a[1]} "
      f"hops={h115a} -> CLEAN (verify at W115 prereg); "
      f"B arithmetic {w115_b[0]}..{w115_b[1]} REFUSED at SEED_REGISTRY "
      f"{who115b} (mid-window hit family) -> pinned past-hit restart "
      f"{fc115_b[0]}..{fc115_b[1]} hops={h115b} CLEAN (verify at W115 prereg). "
      f"Honest two-state note: the W114 seat MSG advisory tail line disclosed "
      f"62_601..62_800 (window-step-chain reading from the pre-seat probe's "
      f"stride-walk first_clean); the pinned D-20261002-05 law supersedes it for "
      f"mid-window hits -- zero impact on the W114 candidate bands (both readings "
      f"converge at hops=0; disclosed, not rewritten).")
