# -*- coding: utf-8 -*-
"""r735 bm-a W130 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W130 candidate = first FREE number after the REGISTERED W129 row (bm-a
r734 freeze; W129 finalize landed same-window r735, ledger head 679,811,
merged pool K=281,720). Derivation faces:
  A  arithmetic continuation from the registered W129 A tail 303_003 + 1,
     stride 2_000 -> 303_004..305_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W129 B tail 68_400 + 1,
     stride 200 -> 68_401..68_600, honest forward walk (W129 gate-tail
     projection: A 303_004..305_003 CLEAN hops=0 / B first-clean
     68_502..68_701 hops=1 past-hit restart, re-derived never
     transcribed r587).
Machine-verified against: all registered N1 wave bands (W2..W14, W16..W129),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), cross-face probe points 95_004/95_006 (r602 leg),
v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4 probe points,
N2-W15 draft probe points, lfc/options actual draw ranges.
Bloodline: r734 _r734bma_w129_probe.py verbatim + W130 facts
(B arithmetic window 68_401..68_600 carries SEED_REGISTRY refusal points
68_500 t19_phantom_p1 + 68_501 perpetual_n4_b1 -> past-hit restart).
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
W129_A_TAIL = 303_003
W129_B_TAIL = 68_400
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

# --- leg 0: registry shape (single state: W129 registered, tail=W129) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 130))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[127]["a"] == (297_004, 299_003) and \
    N1_BANDS[127]["b_exit"] == (67_601, 67_800) and \
    N1_BANDS[127].get("engine_owner") == "bm-a", "leg0 failed: W127 row drift"
assert N1_BANDS[128]["a"] == (299_004, 301_003) and \
    N1_BANDS[128]["b_exit"] == (68_001, 68_200) and \
    N1_BANDS[128].get("engine_owner") == "bm-a", "leg0 failed: W128 row drift"
assert N1_BANDS[129]["a"] == (301_004, W129_A_TAIL) and \
    N1_BANDS[129]["b_exit"] == (68_201, W129_B_TAIL) and \
    N1_BANDS[129].get("engine_owner") == "bm-a", "leg0 failed: W129 row drift"
MODE = "B130 (registered W129, bm-a r734 freeze; W129 finalize landed r735)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W130 = bm-a "
      f"{len(bma_rows) + 1}th owned; W130 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 119 and len(bma_rows) == 45, "leg0 ordinal drift"

# --- leg 1: honest forward walk from the registered W129 tails ----------------
ARITH_A = (W129_A_TAIL + 1, W129_A_TAIL + WIDTH_A)
ARITH_B = (W129_B_TAIL + 1, W129_B_TAIL + WIDTH_B)
assert ARITH_A == (303_004, 305_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (68_401, 68_600), f"leg1-B drift: {ARITH_B}"


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

W130_A = fc_a
W130_B = fc_b

# --- leg 1b: cross-window convergence with the r734 gate-tail projection (r587) --
assert W130_A == (303_004, 305_003) and hops_a == 0, \
    f"leg1b failed: A fork vs W129 gate-tail projection: {W130_A}"
assert W130_B == (68_502, 68_701) and hops_b == 1, \
    f"leg1b failed: B fork vs W129 gate-tail projection: {W130_B}"
assert sorted(fB) == [(68_500, 't19_phantom_p1'), (68_501, 'perpetual_n4_b1')], \
    f"leg1b failed: B refusal identity drift: {fB}"
print("leg1b: derive converges bit-for-bit with the r734 W129 gate-tail "
      "W130+ projection (r587 re-derive-never-transcribe law held); "
      "B refusal identity machine-disclosed: SEED_REGISTRY 68_500 "
      "t19_phantom_p1 + 68_501 perpetual_n4_b1 (D-20261002-05 past-hit "
      "restart: window restarts at 68_502)")

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W130_A), ("B", W130_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W130-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W130-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W130-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W130-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W130-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W130-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W130-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W130-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W130-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '130: {"a": (303_004' not in out, \
    "leg2 failed: W130 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W130"' not in outn1, \
    "leg2 failed: W130 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W130_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W130 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w130_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w130" in ln.lower() and "seat" in ln.lower()]
assert not w130_seats, f"leg2 failed: W130 seat already published: {w130_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W130 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W130 ADMIT-derive: A {W130_A[0]}..{W130_A[1]} hops={hops_a} + "
      f"B {W130_B[0]}..{W130_B[1]} hops={hops_b} "
      f"(mode={MODE}; A = arithmetic continuation from the registered "
      "W129 A tail CLEAN; B = first-clean past-hit restart window after "
      "the REFUSED arithmetic continuation 68_401..68_600, refusal "
      "identity SEED_REGISTRY 68_500 t19_phantom_p1 + 68_501 "
      "perpetual_n4_b1) -- clean vs all registered rows + registry + "
      "probes/actuals -- publish seat MSG with these bands, then full "
      "gate with leg0b seat-on-origin check.")

# --- W131+ projection (warning text for the law table row) --------------------
(fc131_a, h131a) = first_clean(W130_A[1] + 1, WIDTH_A)
(fc131_b, h131b) = first_clean(W130_B[1] + 1, WIDTH_B)
f131a = refusal_facts(fc131_a)
f131b = refusal_facts(fc131_b)
print(f"W131+ projection: A first-clean {fc131_a[0]}..{fc131_a[1]} hops={h131a} "
      f"-> {'CLEAN (verify at W131 prereg)' if not f131a else 'REFUSED ' + str(f131a)}; "
      f"B first-clean {fc131_b[0]}..{fc131_b[1]} hops={h131b} "
      f"-> {'CLEAN (verify at W131 prereg)' if not f131b else 'REFUSED ' + str(f131b)}")
