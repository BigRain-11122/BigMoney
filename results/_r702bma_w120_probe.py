# -*- coding: utf-8 -*-
"""r702 bm-a W120 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W120 candidate = first FREE number after the REGISTERED W119 row (bm-a
r701 freeze 907e1e187). Derivation faces:
  A  arithmetic continuation from the registered W119 A tail 283_003 + 1,
     stride 2_000 -> 283_004..285_003, honest forward walk to first clean.
  B  arithmetic window 65_650..65_849 from the registered W119 B tail
     65_649 + 1, stride 200, honest forward walk with the pinned
     D-20261002-05 past-hit restart semantics (law sec.4).
Machine-verified against: all registered N1 wave bands (W2..W14, W16..W119),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), cross-face probe points 95_004/95_006 (r602 leg),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 probe points,
N2-W15 draft probe points, lfc/options actual draw ranges.
W119 gate-tail projection (r701 907e1e187): A 283_004..285_003 CLEAN /
B first-clean 65_650..65_849 hops=0 -- this probe re-derives, never
transcribes (r587 law).
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
W119_A_TAIL = 283_003
W119_B_TAIL = 65_649
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

# --- leg 0: registry shape (single state: W119 registered, tail=W119) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 120))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[117]["a"] == (277_004, 279_003) and \
    N1_BANDS[117]["b_exit"] == (65_050, 65_249) and \
    N1_BANDS[117].get("engine_owner") == "bm-a", "leg0 failed: W117 row drift"
assert N1_BANDS[118]["a"] == (279_004, 281_003) and \
    N1_BANDS[118]["b_exit"] == (65_250, 65_449) and \
    N1_BANDS[118].get("engine_owner") == "bm-b", "leg0 failed: W118 row drift"
assert N1_BANDS[119]["a"] == (281_004, W119_A_TAIL) and \
    N1_BANDS[119]["b_exit"] == (65_450, W119_B_TAIL) and \
    N1_BANDS[119].get("engine_owner") == "bm-a", "leg0 failed: W119 row drift"
MODE = "B120 (registered W119, bm-a r701 907e1e187)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W120 = bm-a "
      f"{len(bma_rows) + 1}th owned; W120 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 109 and len(bma_rows) == 35, "leg0 ordinal drift"

# --- leg 1: honest forward walk from the registered W119 tails ----------------
ARITH_A = (W119_A_TAIL + 1, W119_A_TAIL + WIDTH_A)
ARITH_B = (W119_B_TAIL + 1, W119_B_TAIL + WIDTH_B)
assert ARITH_A == (283_004, 285_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (65_650, 65_849), f"leg1-B drift: {ARITH_B}"


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

W120_A = fc_a
W120_B = fc_b

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W120_A), ("B", W120_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W120-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W120-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W120-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W120-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W120-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W120-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W120-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W120-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W120-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '120: {"a": (283_004' not in out, \
    "leg2 failed: W120 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W120"' not in outn1, \
    "leg2 failed: W120 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W120_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W120 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w120_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w120" in ln.lower() and "seat" in ln.lower()]
assert not w120_seats, f"leg2 failed: W120 seat already published: {w120_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W120 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W120 ADMIT-derive: A {W120_A[0]}..{W120_A[1]} hops={hops_a} + "
      f"B {W120_B[0]}..{W120_B[1]} hops={hops_b} "
      f"(mode={MODE}; A = arithmetic continuation from the registered "
      "W119 A tail; B refusal facts machine-disclosed) -- clean vs all "
      "registered rows + registry + probes/actuals -- publish seat MSG with "
      "these bands, then full gate with leg0b seat-on-origin check.")

# --- W121+ projection (warning text for the law table row) ---------------------
(fc121_a, h121a) = first_clean(W120_A[1] + 1, WIDTH_A)
(fc121_b, h121b) = first_clean(W120_B[1] + 1, WIDTH_B)
f121a = refusal_facts(fc121_a)
f121b = refusal_facts(fc121_b)
print(f"W121+ projection: A first-clean {fc121_a[0]}..{fc121_a[1]} hops={h121a} "
      f"-> {'CLEAN (verify at W121 prereg)' if not f121a else 'REFUSED ' + str(f121a)}; "
      f"B first-clean {fc121_b[0]}..{fc121_b[1]} hops={h121b} "
      f"-> {'CLEAN (verify at W121 prereg)' if not f121b else 'REFUSED ' + str(f121b)}")
