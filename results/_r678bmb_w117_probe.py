# -*- coding: utf-8 -*-
"""r678 bm-b W117 pre-seat probe -- read-only band derivation before seat MSG
publication (r565 early-visibility law; r587 own-machine derive, never
transcribe).

W117 candidate = first FREE number after the REGISTERED W116 row (bm-b
r677 freeze bc1e82773; W2..W116 all registered, SINGLE STATE).
  A  arithmetic continuation from the registered W116 A tail 277_003+1,
     stride 2_000 -> 277_004..279_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W116 B tail 62_900+1,
     stride 200 -> 62_901..63_100, honest forward walk to first clean
     (r677 gate projection: refused at options actual + registered A-band
     overlap -> first-clean 65_050..65_249 hops=1; MUST re-derive here).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
W116_A = (275_004, 277_003)
W116_B = (62_701, 62_900)
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)  # r602: N2-W15 / N4-B1 disclosed probes
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

# --- leg 0: registry shape (single state W2..W116 all registered) ---------------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 117))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[116]["a"] == W116_A and \
    N1_BANDS[116]["b_exit"] == W116_B and \
    N1_BANDS[116].get("engine_owner") == "bm-b", "leg0 failed: W116 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
ord_total = len(owner_rows) + 1
ord_bmb = len(bmb_rows) + 1
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, "
      f"SINGLE STATE (W2..W116 all registered, zero published seat gap)")
print(f"leg0: engine_owner rows={len(owner_rows)} + this candidate -> "
      f"W117 ordinal = {ord_total}th engine wave by machine-derive; "
      f"bm-b rows={len(bmb_rows)} -> W117 = bm-b {ord_bmb}th owned")
assert len(owner_rows) == 106 and len(bmb_rows) == 39 and \
    len(bmc_rows) == 34 and len(bma_rows) == 33, "leg0 ordinal drift"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == len(owner_rows), \
    "leg0 owner split mismatch"

# --- leg 1: honest forward walk from the registered W116 tails ------------------
ARITH_A = (W116_A[1] + 1, W116_A[1] + WIDTH_A)
ARITH_B = (W116_B[1] + 1, W116_B[1] + WIDTH_B)
assert ARITH_A == (277_004, 279_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (62_901, 63_100), f"leg1-B drift: {ARITH_B}"


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
    """First clean window scanning from lo per D-20261002-05 pin: cross the
    hit -- restart at max(hit)+1 (mid-band) / band_end+1 (band overlap);
    edge hits converge with window-stepping by construction (W74/W81)."""
    hops = 0
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in bands + actual if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        restarts = [p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands]
        lo = max(restarts)
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

W117_A = fc_a
W117_B = fc_b

# --- leg 2: ADMIT-derivation vs full reserved universe + origin vacancy ---------
conflicts = []
for tag, band in (("A", W117_A), ("B", W117_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W117-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W117-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W117-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W117-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W117-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W117-{tag} (r602)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W117-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W117-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W117-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '117: {"a": (277_004' not in out, \
    "leg2 failed: W117 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W117"' not in outn1, \
    "leg2 failed: W117 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W117_PREREG.md"], cwd=ROOT,
    encoding="utf-8").strip()
assert not outpre, "leg2 failed: W117 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w117_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w117" in ln.lower() and "seat" in ln.lower()]
assert not w117_seats, f"leg2 failed: W117 seat already published: {w117_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W117 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W117 ADMIT-derive: A {W117_A[0]}..{W117_A[1]} hops={hops_a} + "
      f"B {W117_B[0]}..{W117_B[1]} hops={hops_b} "
      f"(single state W2..W116 all registered; refusal facts "
      "machine-disclosed) -- clean vs all registered rows + registry + "
      "probes/actuals -- publish seat MSG with these bands.")

# --- W118+ projection (for the next freezer's cross-check) ----------------------
(fc118_a, h118a) = first_clean(W117_A[1] + 1, WIDTH_A)
(fc118_b, h118b) = first_clean(W117_B[1] + 1, WIDTH_B)
f118a = refusal_facts(fc118_a)
f118b = refusal_facts(fc118_b)
print(f"W118+ projection: A first-clean {fc118_a[0]}..{fc118_a[1]} hops={h118a} "
      f"-> {'CLEAN (verify at W118 prereg)' if not f118a else 'REFUSED ' + str(f118a)}; "
      f"B first-clean {fc118_b[0]}..{fc118_b[1]} hops={h118b} "
      f"-> {'CLEAN (verify at W118 prereg)' if not f118b else 'REFUSED ' + str(f118b)}")
