# -*- coding: utf-8 -*-
"""r383 bm-c W115 pre-seat probe -- read-only band derivation before seat MSG
publication (r565 early-visibility law; r587 own-machine derive, never
transcribe).

W115 candidate = first FREE number after the PUBLISHED W114 seat (bm-a
MSG-20261002-2014-bma-w114-seat, published=reserved r518-1; W114 not yet
registered at probe time -- if bm-a registers mid-window the derivation
converges identical, W108 dual-state precedent).
  A  skip-past-published W114 (271_004..273_003), stride 2_000 from the
     published tail -> 273_004..275_003, honest forward walk to first clean.
  B  skip-past-published W114 (62_201..62_400), stride 200 -> 62_401..62_600.
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
W114_PUB_A = (271_004, 273_003)
W114_PUB_B = (62_201, 62_400)
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
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
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]
pub_seat_bands = [W114_PUB_A, W114_PUB_B]  # published=reserved (r518-1)

# --- leg 0: registry shape + published-W114 dual-state check -------------------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 114))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[113]["a"] == (269_004, 271_003) and \
    N1_BANDS[113]["b_exit"] == (62_001, 62_200) and \
    N1_BANDS[113].get("engine_owner") == "bm-c", "leg0 failed: W113 row drift"
w114_registered = 114 in N1_BANDS
if w114_registered:
    # bm-a froze W114 mid-window: registered-continuation state (convergent)
    assert N1_BANDS[114]["a"] == W114_PUB_A and \
        N1_BANDS[114]["b_exit"] == W114_PUB_B, "leg0: W114 reg != published"
    pub_note = "W114 REGISTERED mid-window (convergent state)"
else:
    pub_note = "W114 published-unregistered (skip-past-published state)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
ord_total = len(owner_rows) + (0 if w114_registered else 1) + 1
ord_bmc = len(bmc_rows) + 1
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, {pub_note}")
print(f"leg0: engine_owner rows={len(owner_rows)} + W114 candidate + this "
      f"candidate -> W115 ordinal = {ord_total}th engine wave by machine-derive; "
      f"bm-c rows={len(bmc_rows)} -> W115 = bm-c {ord_bmc}th owned")
assert len(owner_rows) == 103 and len(bmc_rows) == 33 and len(bma_rows) == 32, \
    "leg0 ordinal drift"

# --- leg 1: honest forward walk skipping the published W114 bands --------------
ARITH_A = (W114_PUB_A[1] + 1, W114_PUB_A[1] + WIDTH_A)
ARITH_B = (W114_PUB_B[1] + 1, W114_PUB_B[1] + WIDTH_B)
assert ARITH_A == (273_004, 275_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (62_401, 62_600), f"leg1-B drift: {ARITH_B}"


def refusal_facts(band):
    facts = []
    for p in sorted(points):
        if band[0] <= p <= band[1]:
            who = [k for k, v in science_gates.SEED_REGISTRY.items() if v == p]
            facts.append((p, who[0] if who else "probe/actual point"))
    for b in bands + actual + (pub_seat_bands if not w114_registered else []):
        if overlaps(b, band):
            facts.append((b, "registered band/actual/published-seat"))
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
        if not w114_registered:
            bad_bands += [b for b in pub_seat_bands if overlaps((lo, hi), b)]
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

W115_A = fc_a
W115_B = fc_b

# --- leg 2: ADMIT-derivation vs full reserved universe + origin vacancy ---------
conflicts = []
for tag, band in (("A", W115_A), ("B", W115_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W115-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W115-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W115-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W115-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W115-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W115-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W115-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W115-{tag} (r335 leg)")
    if not w114_registered:
        for r in pub_seat_bands:
            if overlaps(r, band):
                conflicts.append(f"published W114 seat band x W115-{tag} (r518-1)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '115: {"a": (273_004' not in out, \
    "leg2 failed: W115 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W115"' not in outn1, \
    "leg2 failed: W115 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W115_PREREG.md"], cwd=ROOT,
    encoding="utf-8").strip()
assert not outpre, "leg2 failed: W115 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w115_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w115" in ln.lower() and "seat" in ln.lower()]
assert not w115_seats, f"leg2 failed: W115 seat already published: {w115_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W115 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W115 ADMIT-derive: A {W115_A[0]}..{W115_A[1]} hops={hops_a} + "
      f"B {W115_B[0]}..{W115_B[1]} hops={hops_b} "
      f"({pub_note}; skip-past-published W114 per r518-1, refusal facts "
      "machine-disclosed) -- clean vs all registered rows + registry + "
      "published seat + probes/actuals -- publish seat MSG with these bands.")

# --- W116+ projection (for the next freezer's cross-check) ----------------------
(fc116_a, h116a) = first_clean(W115_A[1] + 1, WIDTH_A)
(fc116_b, h116b) = first_clean(W115_B[1] + 1, WIDTH_B)
f116a = refusal_facts(fc116_a)
f116b = refusal_facts(fc116_b)
print(f"W116+ projection: A first-clean {fc116_a[0]}..{fc116_a[1]} hops={h116a} "
      f"-> {'CLEAN (verify at W116 prereg)' if not f116a else 'REFUSED ' + str(f116a)}; "
      f"B first-clean {fc116_b[0]}..{fc116_b[1]} hops={h116b} "
      f"-> {'CLEAN (verify at W116 prereg)' if not f116b else 'REFUSED ' + str(f116b)}")
