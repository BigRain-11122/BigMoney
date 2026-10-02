# -*- coding: utf-8 -*-
"""W101 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W101 candidate = first FREE number after bm-b's PUBLISHED W100 seat
(MSG-20261002-1615-bmb, bands A 243_004..245_003 / B 58_751..58_950,
published=reserved r518-1). Registered tail = W99 (bm-c r374, A
241_004..243_003 / B 58_551..58_750). Skip-past-published chain from the
W99 tails, then D-20261002-05 pinned refusal scan.

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 245_004..247_003  (skip-past-published W100 A, stride 2_000)
  B 59_001..59_200    (skip-past-published W100 B -> 58_951..59_150 refused
                       at 59_000 in-window -> past-hit restart)

Machine-verified against: all registered N1 wave bands (W2..W99 live),
bm-b W100 PUBLISHED seat bands (reserved face), N3-R1 used-seed band
70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, live SEED_REGISTRY
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options
actuals, and the bm-a W101 seat MSG-20261002-1625 (own, on origin per
r565; NO peer W101 seat allowed).

r583 bm-a freeze-window run. READ-ONLY vs the live table + origin.
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

W101_A = (245_004, 247_003)      # candidate (derived, gate must confirm)
W101_B = (59_001, 59_200)
W99_TAIL_A = (241_004, 243_003)   # registered W99 (bm-c r374, live table tail)
W99_TAIL_B = (58_551, 58_750)
W100_PUB_A = (243_004, 245_003)   # bm-b PUBLISHED seat bands (reserved face)
W100_PUB_B = (58_751, 58_950)
OWN_SEAT = "MSG-20261002-1625-bma"   # own W101 seat MSG (pushed pre-freeze r565)
UPSTREAM_SEAT = "MSG-20261002-1615-bmb"  # bm-b W100 seat MSG

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
w100_registered = 100 in N1_BANDS
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 100 + (1 if w100_registered else 0)))
assert keys == expect_keys, \
    f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[99]["a"] == W99_TAIL_A and \
    N1_BANDS[99]["b_exit"] == W99_TAIL_B and \
    N1_BANDS[99].get("engine_owner") == "bm-c", "leg0 failed: W99 row drift"
if w100_registered:
    assert N1_BANDS[100]["a"] == W100_PUB_A and \
        N1_BANDS[100]["b_exit"] == W100_PUB_B and \
        N1_BANDS[100].get("engine_owner") == "bm-b", "leg0 failed: W100 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == (90 if w100_registered else 89), \
    f"leg0 failed: engine_owner rows {len(owner_rows)}"
assert len(bma_rows) == 27, \
    f"leg0 failed: bm-a rows {len(bma_rows)} (expect 27)"
ordinal = len(owner_rows) + 1
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} "
      f"({'W100 bm-b registered same-window' if w100_registered else 'W100 bm-b seat-published NOT yet registered'}); "
      f"engine_owner rows={len(owner_rows)} + candidate -> W101 = bm-a 28th owned, "
      f"{ordinal}th engine wave by machine-derive")

# --- leg 0b: NO peer W101 seat claim on origin (own seat allowed) ---------------
peer_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w101" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W101 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
_names = _r.stdout.decode("utf-8", "replace")
assert OWN_SEAT in _names, \
    "leg0b failed: own W101 seat MSG NOT on origin inbox (r565 pre-freeze push missing)"
print("leg0b: zero PEER W101 seat MSGs on origin (inbox+processed scanned); "
      "own seat MSG-20261002-1625-bma on origin confirmed (r565 law)")

# --- leg 0c: bm-b W100 seat MSG on origin (upstream published seat) ------------
assert UPSTREAM_SEAT in _names, \
    "leg0c failed: bm-b W100 seat MSG not on origin (upstream published seat missing)"
print("leg0c: bm-b W100 seat MSG on origin confirmed (upstream published seat, "
      "reserved face per r518-1)")

# --- leg 1: first-clean-window derive (skip-past-published + refusal scan) ------
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
# published seat bands join the reserved universe for the skip chain
pub_bands = [W100_PUB_A, W100_PUB_B] if not w100_registered else []

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
            for b in bands + pub_bands + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
                if overlaps((lo, hi), b):
                    hit = f"band {b}"
                    break
        if hit is None:
            return (lo, hi), hops
        # D-20261002-05 pinned semantics: past-hit restart (hit + 1)
        nxt = (hit + 1) if isinstance(hit, int) else hi + 1
        print(f"  refusal-scan {tag}: window {lo}..{hi} refused at {hit} -> "
              f"past-hit restart {nxt} (D-20261002-05)")
        lo = nxt
        hops += 1
        assert hops < 50, "refusal scan runaway"

ca, hops_a = first_clean(W99_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W99_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W101_A, f"leg1-A failed: derived first-clean {ca} != {W101_A}"
assert cb == W101_B, f"leg1-B failed: derived first-clean {cb} != {W101_B}"
print(f"leg1: A {W101_A[0]}..{W101_A[1]} CLEAN + B {W101_B[0]}..{W101_B[1]} CLEAN "
      f"(skip-past-published W100 + refusal scan; hops A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W101_A), ("B", W101_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W101-{tag}")
    for nm, bb in (("W100-pub-A", [W100_PUB_A]), ("W100-pub-B", [W100_PUB_B])):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W101-{tag} (published=reserved r518-1)")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W101-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W101-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W101-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W101-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W101-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W101-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W101-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "101: {\"a\": (245_004" not in out, \
    "leg2 failed: W101 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W101"' not in outn1, \
    "leg2 failed: W101 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W101_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W101 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W101 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W101 ADMIT: A {W101_A[0]}..{W101_A[1]} + B {W101_B[0]}..{W101_B[1]} "
      f"(skip-past-published W100 from the registered W99 tails; B past-hit "
      f"restart per D-20261002-05 pin) -- clean vs all registered rows + "
      f"W100 published seat + registry + probes/actuals -- engine_owner=bm-a "
      f"(own seat MSG-20261002-1625-bma on origin BEFORE this freeze per "
      f"r565). NOT a re-pick (R250: W101 bands were never assigned).")

# --- W102+ projection (warning text for the law table row) --------------------
w102_a = (W101_A[1] + 1, W101_A[1] + WIDTH_A)
w102_b = (W101_B[1] + 1, W101_B[1] + WIDTH_B)
a_hits = sorted(p for p in points if w102_a[0] <= p <= w102_a[1]) or \
    [f"band {b}" for b in bands + pub_bands if overlaps(b, w102_a)]
b_hits = sorted(p for p in points if w102_b[0] <= p <= w102_b[1]) or \
    [f"band {b}" for b in bands + pub_bands if overlaps(b, w102_b)]
print(f"W102+ projection: A arithmetic +2_000 = {w102_a[0]}..{w102_a[1]} "
      f"-> {'CLEAN (verify at W102 prereg)' if not a_hits else 'REFUSED ' + str(a_hits)}; "
      f"B +200 from W101 end = {w102_b[0]}..{w102_b[1]} "
      f"-> {'CLEAN (verify at W102 prereg)' if not b_hits else 'REFUSED ' + str(b_hits)}")
