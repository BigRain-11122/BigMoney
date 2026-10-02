# -*- coding: utf-8 -*-
"""W109 band disjoint machine-gate (law sec.4: verify before landing; value-
collision jump-to-first-clean-window per the W5 precedent family).

W109 candidate = first FREE number after the REGISTERED W108 row (bm-c r378
freeze 3a3c51b73). SINGLE STATE zero seat gap (W2..W108 all registered).
Seat published=reserved MSG-20261002-1817-bmb rev.B pushed to origin 99e29877c
BEFORE this freeze per r565 law (rev.B: first draft B projection 60_801..61_000
corrected pre-push -- bm-c W108 landed mid-window; zero prior visibility; the
W108 gate tail disclosure "B 60_801..61_000 REFUSED [61_000]" cross-verified
by this machine's own probe: refusal point = SEED_REGISTRY wild_route_s1=61000).

  A 261_004..263_003 (arithmetic continuation from the registered W108 A
     tail 261_003, width 2_000, hops=0 at freeze state)  CLEAN
  B 61_001..61_200   (arithmetic window 60_801..61_000 hits SEED_REGISTRY
     wild_route_s1=61_000 -> jump to the first clean window per law sec.4
     W5 value-collision precedent, hops=1, refusal facts machine-disclosed)
Machine-verified against: all registered N1 wave bands (W2..W14, W16..W108),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options draws.

r587 bm-b freeze-window run. READ-ONLY vs the live table + origin.
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

W109_A = (261_004, 263_003)
W109_B = (61_001, 61_200)

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
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: W108 registered, tail=W108) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 109))
assert keys == base_keys, \
    f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[103]["a"] == (249_004, 251_003) and \
    N1_BANDS[103]["b_exit"] == (59_401, 59_600) and \
    N1_BANDS[103].get("engine_owner") == "bm-b", "leg0 failed: W103 row drift"
assert N1_BANDS[104]["a"] == (251_004, 253_003) and \
    N1_BANDS[104]["b_exit"] == (59_601, 59_800) and \
    N1_BANDS[104].get("engine_owner") == "bm-a", "leg0 failed: W104 row drift"
assert N1_BANDS[105]["a"] == (253_004, 255_003) and \
    N1_BANDS[105]["b_exit"] == (60_001, 60_200) and \
    N1_BANDS[105].get("engine_owner") == "bm-c", "leg0 failed: W105 row drift"
assert N1_BANDS[106]["a"] == (255_004, 257_003) and \
    N1_BANDS[106]["b_exit"] == (60_201, 60_400) and \
    N1_BANDS[106].get("engine_owner") == "bm-b", "leg0 failed: W106 row drift"
assert N1_BANDS[107]["a"] == (257_004, 259_003) and \
    N1_BANDS[107]["b_exit"] == (60_401, 60_600) and \
    N1_BANDS[107].get("engine_owner") == "bm-a", "leg0 failed: W107 row drift"
assert N1_BANDS[108]["a"] == (259_004, 261_003) and \
    N1_BANDS[108]["b_exit"] == (60_601, 60_800) and \
    N1_BANDS[108].get("engine_owner") == "bm-c", "leg0 failed: W108 row drift"
MODE = "B109 (registered W108)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-b "
      f"rows={len(bmb_rows)} -> W109 = bm-b "
      f"{len(bmb_rows) + 1}th owned; W109 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 98 and len(bmb_rows) == 36, "leg0 ordinal drift"

# --- leg 0b: own W109 seat MSG on origin + zero foreign W109 seats -----------


def _seat_on_origin(path, musts):
    for _sp in (path, path.replace("fleet/inbox/", "fleet/inbox/processed/")):
        _r = subprocess.run(["git", "show", f"origin/main:{_sp}"],
                            cwd=ROOT, capture_output=True)
        if _r.returncode == 0:
            body = _r.stdout.decode("utf-8")
            for m in musts:
                assert m in body, f"leg0b failed: {m} not in {_sp}"
            return body
    raise AssertionError(f"leg0b failed: {path} not on origin")


OWN_SEAT = "fleet/inbox/MSG-20261002-1817-bmb-w109-seat.md"
_seat_on_origin(OWN_SEAT, ["261_004..263_003", "61_001..61_200", "bm-b", "W109"])
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w109_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w109" in ln.lower() and "seat" in ln.lower()]
assert w109_seats == [OWN_SEAT], \
    f"leg0b failed: W109 seat set must be exactly this machine's own " \
    f"published seat, got {w109_seats}"
print("leg0b: W109 seat = this machine's OWN published declaration rev.B "
      "(verified on origin with the frozen bands incl. the 61_001..61_200 "
      "value-collision jump; zero foreign W109 seat MSGs)")

# --- leg 1: honest forward walk from the registered W108 tails ---------------
tail = N1_BANDS[108]
ARITH_A = (tail["a"][1] + 1, tail["a"][1] + WIDTH_A)
ARITH_B = (tail["b_exit"][1] + 1, tail["b_exit"][1] + WIDTH_B)
assert ARITH_A == (261_004, 263_003), f"leg1-A drift: {ARITH_A}"


def refusal_facts(band):
    """Machine-disclosed refusal facts for a candidate window."""
    facts = []
    for p in sorted(points):
        if band[0] <= p <= band[1]:
            who = [k for k, v in science_gates.SEED_REGISTRY.items() if v == p]
            facts.append((p, who[0] if who else "probe/actual point"))
    for b in bands + actual:
        if overlaps(b, band):
            facts.append((b, "registered band/actual"))
    return facts


B_ARITH_FACTS = refusal_facts(ARITH_B)
assert B_ARITH_FACTS == [(61_000, "wild_route_s1")], \
    f"leg1-B refusal-facts drift: {B_ARITH_FACTS}"
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN hops=0; "
      f"B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED facts="
      f"{B_ARITH_FACTS} -> value-collision jump per law sec.4 W5 precedent")


def first_clean(lo, width):
    """First clean window at/after lo (honest forward walk, W5 jump law:
    contiguous window steps, one hop per refused window -- the 跳位 counts
    skipped windows, not slide increments, per W5/W108 precedent family)."""
    hops = 0
    while True:
        hi = lo + width - 1
        bad = [p for p in points if lo <= p <= hi]
        bad += [b for b in bands + actual if overlaps((lo, hi), b)]
        if not bad:
            return (lo, hi), hops
        lo += width
        hops += 1


(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B)
assert fc_a == W109_A and hops_a == 0, f"leg1-A failed: {fc_a} hops={hops_a}"
assert fc_b == W109_B and hops_b == 1, f"leg1-B failed: {fc_b} hops={hops_b}"
print(f"leg1: A first-clean {W109_A[0]}..{W109_A[1]} hops={hops_a} == "
      f"candidate; B first-clean {W109_B[0]}..{W109_B[1]} hops={hops_b} == "
      f"candidate (jump past refusal point 61_000)")
assert not overlaps(W109_A, W109_B), "A/B overlap"

# --- leg 2: candidate ADMIT + origin vacancy ----------------------------------
conflicts = []
for tag, band in (("A", W109_A), ("B", W109_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W109-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W109-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W109-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W109-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W109-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W109-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W109-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W109-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '109: {"a": (261_004' not in out, \
    "leg2 failed: W109 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W109"' not in outn1, \
    "leg2 failed: W109 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W109_PREREG.md"], cwd=ROOT,
    encoding="utf-8").strip()
assert not outpre, "leg2 failed: W109 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | mode={MODE}")
if conflicts:
    print("W109 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W109 ADMIT: A {W109_A[0]}..{W109_A[1]} + B {W109_B[0]}..{W109_B[1]} "
      f"(mode={MODE}; A: arithmetic continuation from the registered W108 "
      "A tail hops=0; B: arithmetic window 60_801..61_000 REFUSED by "
      "SEED_REGISTRY wild_route_s1=61_000 -> first-clean-window jump to "
      "61_001..61_200 hops=1 per law sec.4 W5 value-collision precedent, "
      "refusal facts machine-disclosed) -- clean vs all registered rows + "
      "registry + probes/actuals -- engine_owner=bm-b (W109 seat "
      "published=reserved MSG-20261002-1817-bmb rev.B pushed to origin "
      "99e29877c BEFORE this freeze per r565 early-visibility law). "
      "NOT a re-pick (R250: W109 bands were never assigned).")

# --- W110+ projection (warning text for the law table row) --------------------
(fc110_a, h110a) = first_clean(W109_A[1] + 1, WIDTH_A)
(fc110_b, h110b) = first_clean(W109_B[1] + 1, WIDTH_B)
f110a = refusal_facts(fc110_a)
f110b = refusal_facts(fc110_b)
print(f"W110+ projection: A first-clean {fc110_a[0]}..{fc110_a[1]} hops={h110a} "
      f"-> {'CLEAN (verify at W110 prereg)' if not f110a else 'REFUSED ' + str(f110a)}; "
      f"B first-clean {fc110_b[0]}..{fc110_b[1]} hops={h110b} "
      f"-> {'CLEAN (verify at W110 prereg)' if not f110b else 'REFUSED ' + str(f110b)}")
