# -*- coding: utf-8 -*-
"""r382 bm-c W113 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W113 candidate = first FREE number after the REGISTERED W112 row (bm-a
r590 freeze 0c4d67910). Derivation faces:
  A  arithmetic continuation from the registered W112 A tail 269_003 + 1,
     stride 2_000 -> 269_004..271_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W112 B tail 61_800 + 1,
     stride 200 -> 61_801..62_000 REFUSED at SEED_REGISTRY cta_wave1=62_000
     (window-tail endpoint hit, W74/W81 family) -> jump-past-hit restart
     62_001 (D-20261002-05 pinned sec.4 skip semantics) -> 62_001..62_200.
Machine-verified against: all registered N1 wave bands (W2..W14, W16..W112),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options draws.
W112 gate-tail projection (bm-a r590): A 269_004..271_003 CLEAN /
B 62_001..62_200 hops=1 -- this probe re-derives, never transcribes (r587 law).
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
W112_A_TAIL = 269_003
W112_B_TAIL = 61_800
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster frozen)"
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

# --- leg 0: registry shape (single state: W112 registered, tail=W112) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 113))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[108]["a"] == (259_004, 261_003) and \
    N1_BANDS[108]["b_exit"] == (60_601, 60_800) and \
    N1_BANDS[108].get("engine_owner") == "bm-c", "leg0 failed: W108 row drift"
assert N1_BANDS[109]["a"] == (261_004, 263_003) and \
    N1_BANDS[109]["b_exit"] == (61_001, 61_200) and \
    N1_BANDS[109].get("engine_owner") == "bm-b", "leg0 failed: W109 row drift"
assert N1_BANDS[110]["a"] == (263_004, 265_003) and \
    N1_BANDS[110]["b_exit"] == (61_201, 61_400) and \
    N1_BANDS[110].get("engine_owner") == "bm-a", "leg0 failed: W110 row drift"
assert N1_BANDS[111]["a"] == (265_004, 267_003) and \
    N1_BANDS[111]["b_exit"] == (61_401, 61_600) and \
    N1_BANDS[111].get("engine_owner") == "bm-b", "leg0 failed: W111 row drift"
assert N1_BANDS[112]["a"] == (267_004, W112_A_TAIL) and \
    N1_BANDS[112]["b_exit"] == (61_601, W112_B_TAIL) and \
    N1_BANDS[112].get("engine_owner") == "bm-a", "leg0 failed: W112 row drift"
MODE = "B113 (registered W112)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-c "
      f"rows={len(bmc_rows)} -> W113 = bm-c "
      f"{len(bmc_rows) + 1}th owned; W113 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 102 and len(bmc_rows) == 32, "leg0 ordinal drift"

# --- leg 1: honest forward walk from the registered W112 tails ----------------
ARITH_A = (W112_A_TAIL + 1, W112_A_TAIL + WIDTH_A)
ARITH_B = (W112_B_TAIL + 1, W112_B_TAIL + WIDTH_B)
assert ARITH_A == (269_004, 271_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (61_801, 62_000), f"leg1-B drift: {ARITH_B}"


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
    """First clean window at/after lo; pinned sec.4 skip semantics
    (D-20261002-05): mid-band point hit = restart at hit+1 (jump-past-hit),
    band hit = restart at band tail+1. Window-tail endpoint hits give the
    identical window under both readings (W74/W81 family)."""
    hops = 0
    while True:
        hi = lo + width - 1
        hit = None
        for p in points:
            if lo <= p <= hi:
                hit = p
                break
        if hit is None:
            for b in bands + actual:
                if overlaps((lo, hi), b):
                    hit = ("band", b)
                    break
        if hit is None:
            return (lo, hi), hops
        if isinstance(hit, tuple):
            nxt = hi + 1
            print(f"  refusal-scan: window {lo}..{hi} refused at {hit} -> restart {nxt}")
        else:
            nxt = hit + 1
            who = [k for k, v in science_gates.SEED_REGISTRY.items() if v == hit]
            print(f"  refusal-scan: window {lo}..{hi} refused at SEED_REGISTRY "
                  f"{who[0] if who else hit}={hit} -> jump-past-hit restart {nxt} "
                  f"(D-20261002-05)")
        lo = nxt
        hops += 1
        assert hops < 50, "refusal scan runaway"


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

W113_A = fc_a
W113_B = fc_b

# --- leg 2: candidate ADMIT-derivation vs registry points/bands --------------
conflicts = []
for tag, band in (("A", W113_A), ("B", W113_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W113-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W113-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W113-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W113-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W113-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W113-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W113-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W113-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '113: {"a": (269_004' not in out, \
    "leg2 failed: W113 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W113"' not in outn1, \
    "leg2 failed: W113 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W113_PREREG.md"], cwd=ROOT,
    encoding="utf-8").strip()
assert not outpre, "leg2 failed: W113 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True,
    creationflags=CREAT)
w113_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w113" in ln.lower() and "seat" in ln.lower()]
assert not w113_seats, f"leg2 failed: W113 seat already published: {w113_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W113 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W113 ADMIT-derive: A {W113_A[0]}..{W113_A[1]} hops={hops_a} + "
      f"B {W113_B[0]}..{W113_B[1]} hops={hops_b} "
      f"(mode={MODE}; A = arithmetic continuation from the registered W112 "
      "A tail; B = jump-past-hit window after SEED_REGISTRY cta_wave1=62_000 "
      "window-tail endpoint hit, D-20261002-05 pinned skip semantics, "
      "W74/W81 endpoint family) -- clean vs all registered rows + registry + "
      "probes/actuals -- publish seat MSG with these bands, then full gate "
      "with leg0b seat-on-origin check.")

# --- W114+ projection (warning text for the law table row) ---------------------
(fc114_a, h114a) = first_clean(W113_A[1] + 1, WIDTH_A)
(fc114_b, h114b) = first_clean(W113_B[1] + 1, WIDTH_B)
f114a = refusal_facts(fc114_a)
f114b = refusal_facts(fc114_b)
print(f"W114+ projection: A first-clean {fc114_a[0]}..{fc114_a[1]} hops={h114a} "
      f"-> {'CLEAN (verify at W114 prereg)' if not f114a else 'REFUSED ' + str(f114a)}; "
      f"B first-clean {fc114_b[0]}..{fc114_b[1]} hops={h114b} "
      f"-> {'CLEAN (verify at W114 prereg)' if not f114b else 'REFUSED ' + str(f114b)}")
