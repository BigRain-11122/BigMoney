# -*- coding: utf-8 -*-
"""r740 bm-a W135 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W135 candidate = first FREE number after the REGISTERED W134 row (bm-a
r739 freeze d6b64dddd; W134 finalize landed same-window r740, ledger head
690,811, merged pool K=292,720). Derivation faces:
  A  arithmetic continuation from the registered W134 A tail 313_003 + 1,
     stride 2_000 -> 313_004..315_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W134 B tail 69_501 + 1,
     stride 200 -> 69_502..69_701, honest forward walk (r739 seat/gate
     W135+ tail projection: A 313_004..315_003 CLEAN hops=0 /
     B 69_502..69_701 CLEAN hops=0 -- double-CLEAN window, re-derived
     never transcribed r587).
Machine-verified against: all registered N1 wave bands (W2..W14,
W16..W134), N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg),
probe cluster 95_000..95_003 (r335 leg), cross-face probe points
95_004/95_006 (r602 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options
actual draw ranges.
Bloodline: r739 _r739bma_w134_probe.py verbatim + W135 facts
(double-CLEAN arithmetic continuation window from the registered W134
tails).
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
W134_A_TAIL = 313_003
W134_B_TAIL = 69_501
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

# --- leg 0: registry shape (single state: W134 registered, tail=W134) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 135))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[134]["a"] == (311_004, W134_A_TAIL) and \
    N1_BANDS[134]["b_exit"] == (69_302, W134_B_TAIL) and \
    N1_BANDS[134].get("engine_owner") == "bm-a", "leg0 failed: W134 row drift"
assert N1_BANDS[132]["a"] == (307_004, 309_003) and \
    N1_BANDS[132]["b_exit"] == (68_902, 69_101) and \
    N1_BANDS[132].get("engine_owner") == "bm-a", "leg0 failed: W132 row drift"
assert N1_BANDS[133]["a"] == (309_004, 311_003) and \
    N1_BANDS[133]["b_exit"] == (69_102, 69_301) and \
    N1_BANDS[133].get("engine_owner") == "bm-a", "leg0 failed: W133 row drift"
MODE = "B135 (registered W134, bm-a r739 freeze d6b64dddd; W134 finalize landed same-window r740, ledger head 690,811, merged pool K=292,720)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W135 = bm-a "
      f"{len(bma_rows) + 1}th owned; W135 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 124 and len(bma_rows) == 50, "leg0 ordinal drift"

# --- leg 1: honest forward walk from the registered W134 tails ----------------
ARITH_A = (W134_A_TAIL + 1, W134_A_TAIL + WIDTH_A)
ARITH_B = (W134_B_TAIL + 1, W134_B_TAIL + WIDTH_B)
assert ARITH_A == (313_004, 315_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (69_502, 69_701), f"leg1-B drift: {ARITH_B}"


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

W135_A = fc_a
W135_B = fc_b

# --- leg 1b: cross-window convergence with the r739 W134 seat/gate projection (r587) --
assert W135_A == (313_004, 315_003) and hops_a == 0, \
    f"leg1b failed: A fork vs W134 gate-tail projection: {W135_A}"
assert W135_B == (69_502, 69_701) and hops_b == 0, \
    f"leg1b failed: B fork vs W134 gate-tail projection: {W135_B}"
assert not fA and not fB, \
    f"leg1b failed: double-CLEAN window refusal facts drift: A={fA} B={fB}"
print("leg1b: derive converges bit-for-bit with the r739 W134 seat MSG-1857 "
      "W135+ projection (r587 re-derive-never-transcribe law held); "
      "double-CLEAN window: both A and B arithmetic continuations CLEAN "
      "hops=0")

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W135_A), ("B", W135_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W135-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W135-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W135-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W135-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W135-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W135-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W135-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W135-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W135-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '135: {"a": (313_004' not in out, \
    "leg2 failed: W135 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W135"' not in outn1, \
    "leg2 failed: W135 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W135_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W135 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w135_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w135" in ln.lower() and "seat" in ln.lower()]
assert not w135_seats, f"leg2 failed: W135 seat already published: {w135_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W135 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W135 ADMIT-derive: A {W135_A[0]}..{W135_A[1]} hops={hops_a} + "
      f"B {W135_B[0]}..{W135_B[1]} hops={hops_b} "
      f"(mode={MODE}; double-CLEAN: A and B both arithmetic continuations "
      "from the registered W134 tails, hops=0) -- clean vs all registered "
      "rows + registry + probes/actuals -- publish seat MSG with these "
      "bands, then full gate with leg0b seat-on-origin check.")

# --- W136+ projection (warning text for the law table row) --------------------
(fc136_a, h136a) = first_clean(W135_A[1] + 1, WIDTH_A)
(fc136_b, h136b) = first_clean(W135_B[1] + 1, WIDTH_B)
f136a = refusal_facts(fc136_a)
f136b = refusal_facts(fc136_b)
print(f"W136+ projection: A first-clean {fc136_a[0]}..{fc136_a[1]} hops={h136a} "
      f"-> {'CLEAN (verify at W136 prereg)' if not f136a else 'REFUSED ' + str(f136a)}; "
      f"B first-clean {fc136_b[0]}..{fc136_b[1]} hops={h136b} "
      f"-> {'CLEAN (verify at W136 prereg)' if not f136b else 'REFUSED ' + str(f136b)}")
