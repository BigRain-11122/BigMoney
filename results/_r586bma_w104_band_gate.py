# -*- coding: utf-8 -*-
"""W104 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W104 candidate = first FREE number after the REGISTERED W103 row
(bm-b r584 freeze fbbde996f, bands A 249_004..251_003 / B 59_401..59_600,
registered tail = W103). SINGLE STATE zero seat gap: no published-but-
unregistered seat rows exist beyond W103 (own W104 seat
MSG-20261002-1712-bma published=reserved r518-1, on origin per r565).

Seat-prose ordinal drift disclosed (r359 law, W102 r375 precedent): the
seat MSG hand-count said "engine_owner==bm-a rows 30 + candidate" but the
live registry machine-count is bm-a rows 28 -> W104 = bm-a 29th owned
wave (gate leg0 output is authoritative). Engine ordinal 94th
(engine_owner rows 93 + candidate) matches the seat MSG.

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 251_004..253_003  (arithmetic continuation from the registered W103
                       A tail 251_003 + 1, stride 2_000)
  B 59_601..59_800    (arithmetic continuation from the registered W103
                       B tail 59_600 + 1, stride 200)

Machine-verified against: all registered N1 wave bands (W2..W103 live),
live SEED_REGISTRY values, N3-R1 used-seed band 70_000..70_005
(MSG-183x r529 mandatory leg), probe cluster 95_000..95_003 (r335 leg),
v1 in-use + W1 ext bands, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actuals, and the bm-a W104 seat MSG-20261002-1712 (own, on
origin per r565; NO peer W104 seat allowed).

r586 bm-a freeze-window run. READ-ONLY vs the live table + origin.
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

W104_A = (251_004, 253_003)      # candidate (derived, gate must confirm)
W104_B = (59_601, 59_800)
W103_TAIL_A = (249_004, 251_003)  # registered W103 (bm-b r584, live table tail)
W103_TAIL_B = (59_401, 59_600)
OWN_SEAT = "MSG-20261002-1712-bma"   # own W104 seat MSG (pushed pre-freeze r565)

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
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 104))
assert keys == expect_keys, \
    f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[103]["a"] == W103_TAIL_A and \
    N1_BANDS[103]["b_exit"] == W103_TAIL_B and \
    N1_BANDS[103].get("engine_owner") == "bm-b", "leg0 failed: W103 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 93, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 93)"
assert len(bma_rows) == 28, \
    f"leg0 failed: bm-a rows {len(bma_rows)} (expect 28; seat prose said 30 -- \
r359 drift to disclose)"
ordinal = len(owner_rows) + 1
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W103 bm-b "
      f"registered); engine_owner rows={len(owner_rows)} + candidate -> W104 "
      f"= 94th engine wave, bm-a {len(bma_rows) + 1}th owned wave by "
      f"machine-derive (seat prose '31st' hand-drift disclosed per r359, "
      f"W102 precedent)")

# --- leg 0b: NO peer W104 seat claim on origin (own seat allowed) ---------------
peer_claims = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w104" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W104 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
_names = _r.stdout.decode("utf-8", "replace")
assert OWN_SEAT in _names, \
    "leg0b failed: own W104 seat MSG NOT on origin inbox (r565 pre-freeze push missing)"
print("leg0b: zero PEER W104 seat MSGs on origin (inbox+processed scanned); "
      "own seat MSG-20261002-1712-bma on origin confirmed (r565 law)")

# --- leg 1: first-clean-window derive (arithmetic continuation + refusal scan) -
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
pub_bands = []  # single state: no published-unregistered peer seats

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

ca, hops_a = first_clean(W103_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W103_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W104_A, f"leg1-A failed: derived first-clean {ca} != {W104_A}"
assert cb == W104_B, f"leg1-B failed: derived first-clean {cb} != {W104_B}"
print(f"leg1: A {W104_A[0]}..{W104_A[1]} CLEAN + B {W104_B[0]}..{W104_B[1]} CLEAN "
      f"(arithmetic continuation from the registered W103 tails; hops "
      f"A={hops_a} B={hops_b})")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W104_A), ("B", W104_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W104-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W104-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W104-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W104-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W104-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W104-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W104-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W104-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "104: {\"a\": (251_004" not in out, \
    "leg2 failed: W104 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W104"' not in outn1, \
    "leg2 failed: W104 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W104_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W104 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W104 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W104 ADMIT: A {W104_A[0]}..{W104_A[1]} + B {W104_B[0]}..{W104_B[1]} "
      f"(arithmetic continuation from the registered W103 tails) -- clean vs "
      f"all registered rows + registry + probes/actuals -- engine_owner=bm-a "
      f"(own seat MSG-20261002-1712-bma on origin BEFORE this freeze per "
      f"r565). NOT a re-pick (R250: W104 bands were never assigned).")

# --- W105+ projection (warning text for the law table row) --------------------
w105_a = (W104_A[1] + 1, W104_A[1] + WIDTH_A)
w105_b = (W104_B[1] + 1, W104_B[1] + WIDTH_B)
a_hits = sorted(p for p in points if w105_a[0] <= p <= w105_a[1]) or \
    [f"band {b}" for b in bands + pub_bands if overlaps(b, w105_a)]
b_hits = sorted(p for p in points if w105_b[0] <= p <= w105_b[1]) or \
    [f"band {b}" for b in bands + pub_bands if overlaps(b, w105_b)]
print(f"W105+ projection: A arithmetic +2_000 = {w105_a[0]}..{w105_a[1]} "
      f"-> {'CLEAN (verify at W105 prereg)' if not a_hits else 'REFUSED ' + str(a_hits)}; "
      f"B +200 from W104 end = {w105_b[0]}..{w105_b[1]} "
      f"-> {'CLEAN (verify at W105 prereg)' if not b_hits else 'REFUSED ' + str(b_hits)}")
