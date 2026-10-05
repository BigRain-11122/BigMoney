# -*- coding: utf-8 -*-
"""r732 bm-a W127 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W127 candidate = first FREE number after the REGISTERED W126 row (bm-a
r731 freeze db9da0e92; W126 finalize landed same-window r732, ledger
head 673,211, merged pool K=275,120). Derivation faces:
  A  arithmetic continuation from the registered W126 A tail 297_003 + 1,
     stride 2_000 -> 297_004..299_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W126 B tail 67_600 + 1,
     stride 200 -> 67_601..67_800, honest forward walk (W126 gate-tail
     projection CLEAN hops=0 both sides, re-derived never transcribed r587).
Machine-verified against: all registered N1 wave bands (W2..W14, W16..W126),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), cross-face probe points 95_004/95_006 (r602 leg),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 probe points,
N2-W15 draft probe points, lfc/options actual draw ranges.
"""
import subprocess
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
W126_A_TAIL = 297_003
W126_B_TAIL = 67_600
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster frozen)"
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: W125 registered, tail=W125) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 127))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[124]["a"] == (291_004, 293_003) and \
    N1_BANDS[124]["b_exit"] == (66_601, 66_800) and \
    N1_BANDS[124].get("engine_owner") == "bm-a", "leg0 failed: W124 row drift"
assert N1_BANDS[125]["a"] == (293_004, 295_003) and \
    N1_BANDS[125]["b_exit"] == (67_201, 67_400) and \
    N1_BANDS[125].get("engine_owner") == "bm-a", "leg0 failed: W125 row drift"
assert N1_BANDS[126]["a"] == (295_004, W126_A_TAIL) and \
    N1_BANDS[126]["b_exit"] == (67_401, W126_B_TAIL) and \
    N1_BANDS[126].get("engine_owner") == "bm-a", "leg0 failed: W126 row drift"
MODE = "B127 (registered W126, bm-a r731 freeze db9da0e92; W126 finalize landed r732)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W127 = bm-a "
      f"{len(bma_rows) + 1}th owned; W127 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 116 and len(bma_rows) == 42, "leg0 ordinal drift"

# --- leg 1: honest forward walk from the registered W125 tails ----------------
ARITH_A = (W126_A_TAIL + 1, W126_A_TAIL + WIDTH_A)
ARITH_B = (W126_B_TAIL + 1, W126_B_TAIL + WIDTH_B)
assert ARITH_A == (297_004, 299_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (67_601, 67_800), f"leg1-B drift: {ARITH_B}"


def refusal_facts(band):
    facts = []
    for p in sorted(points):
        if band[0] <= p <= band[1]:
            who = [k for k, v in science_gates.SEED_REGISTRY.items() if v == p]
            facts.append((p, who[0] if who else "probe/actual point"))
    for b in bands + actual:
        if overlaps(b, band):
            facts.append((b, "registered band/actual"))
    return facts


def first_clean(lo, width):
    """First clean window at/after lo; pinned D-20261002-05 past-hit
    restart semantics (lo jumps past the refusing point/band, law sec.4)."""
    hops = 0
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in bands + actual if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        lo = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        hops += 1


fA = refusal_facts(ARITH_A)
fB = refusal_facts(ARITH_B)
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B)
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} "
      f"{'CLEAN' if not fA else 'REFUSED ' + str(fA)} -> first-clean "
      f"{fc_a[0]}..{fc_a[1]} hops={hops_a}")
print(f"leg1: B arithmetic {ARITH_B[0]}..{ARITH_B[1]} "
      f"{'CLEAN' if not fB else 'REFUSED ' + str(fB)} -> first-clean "
      f"{fc_b[0]}..{fc_b[1]} hops={hops_b}")
assert not overlaps(fc_a, fc_b), "A/B overlap"

W127_A = fc_a
W127_B = fc_b

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W127_A), ("B", W127_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W127-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W127-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W127-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W127-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W127-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W127-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W127-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W127-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W127-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '127: {"a": (297_004' not in out, \
    "leg2 failed: W127 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W127"' not in outn1, \
    "leg2 failed: W127 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W127_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W127 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w127_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w127" in ln.lower() and "seat" in ln.lower()]
assert not w127_seats, f"leg2 failed: W127 seat already published: {w127_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W127 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W127 ADMIT-derive: A {W127_A[0]}..{W127_A[1]} hops={hops_a} + "
      f"B {W127_B[0]}..{W127_B[1]} hops={hops_b} "
      f"(mode={MODE}; both sides = arithmetic continuation from the registered "
      "W126 tails; refusal facts machine-disclosed) -- clean vs all "
      "registered rows + registry + probes/actuals -- publish seat MSG with "
      "these bands, then full gate with leg0b seat-on-origin check.")

# --- W128+ projection (warning text for the law table row) ---------------------
(fc128_a, h128a) = first_clean(W127_A[1] + 1, WIDTH_A)
(fc128_b, h128b) = first_clean(W127_B[1] + 1, WIDTH_B)
f128a = refusal_facts(fc128_a)
f128b = refusal_facts(fc128_b)
print(f"W128+ projection: A first-clean {fc128_a[0]}..{fc128_a[1]} hops={h128a} "
      f"-> {'CLEAN (verify at W128 prereg)' if not f128a else 'REFUSED ' + str(f128a)}; "
      f"B first-clean {fc128_b[0]}..{fc128_b[1]} hops={h128b} "
      f"-> {'CLEAN (verify at W128 prereg)' if not f128b else 'REFUSED ' + str(f128b)}")
