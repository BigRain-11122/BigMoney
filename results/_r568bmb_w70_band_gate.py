# -*- coding: utf-8 -*-
"""W70 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W70 = FIFTY-NINTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTY-SECOND owned wave, machine-derived:
21 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (r518-1 law). W67 finalize LANDED this window
(bm-b r568, net chain head 511,948, K=145,320); W68 bm-a + W69 bm-c =
TWO in-flight upstream seats at this freeze (FAIL-CLOSED r307).

*** FORK FACE #3 (disclosed per the W69 row mandate: 裁定前=冻结方
机闸 derive+分叉披露强制; pin pending HQ-FEEDBACK F-20261002-03) ***

B-side arithmetic window 50_901..51_100 is REFUSED mid-band by the
SEED_REGISTRY point 51_000 (xstock_synth_null_a). The two in-canon
skip readings FORK (canon currently holds BOTH: W63 chained + W68
past-hit restart -- contradictory precedents):
  reading 1 (past-hit restart, 越hit起窗): 51_001..51_200
  reading 2 (window-step chain, 连锁整窗步进): 51_101..51_300
This gate machine-derives BOTH, verifies BOTH clean, and the freeze
CANDIDATE takes reading 1 (past-hit restart) per the SINGLE-mid-hit
precedent family majority (W26-A 95_004 restart + W68-B 50_501
restart; the W63-B chained precedent was a DOUBLE-hit case, not
single-hit) + the family gate tools' own _first_clean derivation
(lo = max(hits) + 1). The chained alternative is disclosed here and
in the canon row; the F-20261002-03 pin governs future waves.

A-side is plain arithmetic continuation (W69 A end 183_003 + 1),
machine-verified CLEAN against the full reserved universe.

Machine-verified against: all registered N1 wave bands W2..W69, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r568 bm-b freeze-window run (never-dry standing step,
O-20261001-2355 sec.2 own-series).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W70_A = (183_004, 185_003)              # law sec.4 W70 row (arithmetic, no skip)
W70_B = (51_001, 51_200)                # law sec.4 W70 row (past-hit RESTART, fork face #3)
W70_B_CHAINED = (51_101, 51_300)        # disclosed alternative reading (NOT taken)

# --- registered W69 row (bm-c r360 freeze fc4cb8a38, registered tail) --------
W69_REGISTERED_A = (181_004, 183_003)
W69_REGISTERED_B = (50_701, 50_900)

# --- N3-R1 used-seed band (MSG-183x r529 bm-a mandatory leg) -----------------
N3R1_USED = (70_000, 70_005)

# --- runner design-probe seeds (r335 discovery leg -- mandatory W26+) --------
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster is frozen)"

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

# --- leg 0-hold: zero-gap relay (W69 must be REGISTERED before ADMIT) -------
if 69 not in N1_BANDS:
    print("HOLD: W69 row not yet registered in the live registry. W70 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[69]["a"] == W69_REGISTERED_A and \
    N1_BANDS[69]["b_exit"] == W69_REGISTERED_B and \
    N1_BANDS[69].get("engine_owner") == "bm-c", \
    "leg0 failed: registered W69 row != expected registered bands " \
    "(A 181_004..183_003 / B 50_701..50_900, bm-c r360 fc4cb8a38) -- " \
    "derivation basis invalidated, RE-DERIVE the W70 candidates"

# --- reserved universe (W70 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 70:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (67 pre-W70 registered rows + the candidate) -----
assert 68 in N1_BANDS and N1_BANDS[68]["engine_owner"] == "bm-a", \
    "leg0 failed: W68 (bm-a) row must be present (registered 938d8bb54, " \
    "burn in flight -- finalize chain-pending FAIL-CLOSED r307)"
assert 69 in N1_BANDS and N1_BANDS[69]["engine_owner"] == "bm-c", \
    "leg0 failed: W69 (bm-c) row must be present (registered fc4cb8a38, " \
    "burn in flight -- finalize chain-pending FAIL-CLOSED r307)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w67_results.json")), \
    "leg0 failed: W67 finalize product missing (landed 77fd35e87 this " \
    "window, net chain head 511,948, K=145,320 -- it stays the S5 anchor " \
    "while W68/W69 finalizes are in flight)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 22, \
    "leg0 failed: bm-b owned-row count != 22 (21 pre-candidate + the " \
    "landed W70 candidate -- machine-derive basis for the TWENTY-SECOND " \
    "owned wave claim)"
pre_w70 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68, 69, 70]
assert sorted(N1_BANDS) == pre_w70, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 67 " \
    f"registered rows + the W70 candidate)"

# --- leg 0b: W69 row's W70+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
for prose in ("183_004..185_003", "50_901..51_100", "51_001..51_200",
              "51_101..51_300"):
    assert prose in canon, \
        f"leg0b failed: W69 row W70+ WARNING prose '{prose}' not found " \
        f"in the canon file"
print("leg0b W69 row W70+ WARNING prose present (fork-face projection "
      "basis; machine-derived per r535 by bm-c r360 probe; registered "
      "W69 bm-c row bands cross-checked verbatim; fork face #3 "
      "mandate = 裁定前机闸 derive+分叉披露强制)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[69]["a"][1] + 1, N1_BANDS[69]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[69]["b_exit"][1] + 1,
           N1_BANDS[69]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W69 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W69 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [51_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (W69 row projected " \
    f"REFUSED by exactly [51_000] mid-band)"
_keys51k = sorted(k for k, v in science_gates.SEED_REGISTRY.items()
                  if v == 51_000)
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED "
      f"mid-band by SEED_REGISTRY {b_hits} (key {_keys51k}) -- matches "
      f"the W69 row W70+ WARNING refusal facts verbatim (fork family)")

# --- leg 2: first clean windows -----------------------------------------------
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

first_a = clean(ARITH_A[0], WIDTH_A)
assert first_a == W70_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W70_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# reading 1: past-hit restart (lo = max(hits) + 1) -- the CANDIDATE
restart_b = clean(b_hits[-1] + 1, WIDTH_B)
assert restart_b == W70_B, \
    f"leg2-B failed: past-hit restart window {restart_b} != candidate " \
    f"{W70_B} (reading 1 derivation)"
# reading 2: window-step chain (arithmetic window start + width) -- DISCLOSED
chained_b = clean(ARITH_B[0] + WIDTH_B, WIDTH_B)
assert chained_b == W70_B_CHAINED, \
    f"leg2-B failed: chained-skip window {chained_b} != disclosed " \
    f"alternative {W70_B_CHAINED} (reading 2 derivation)"
print(f"leg2 FORK FACE #3 DISCLOSURE: reading 1 past-hit restart "
      f"{restart_b[0]}..{restart_b[1]} (TAKEN -- candidate; single-mid-hit "
      f"precedent family: W26-A 95_004 restart + W68-B 50_501 restart; "
      f"family gate _first_clean law lo=max(hits)+1) vs reading 2 "
      f"window-step chain {chained_b[0]}..{chained_b[1]} (DISCLOSED, NOT "
      f"taken; W63-B chained precedent was a DOUBLE-hit case); BOTH "
      f"machine-verified clean vs the full reserved universe; pin "
      f"pending HQ-FEEDBACK F-20261002-03 -- W70 冻结方按裁定行执行, "
      f"裁定前=机闸 derive+分叉披露强制 (W69 row mandate, satisfied)")
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} (arithmetic "
      f"continuation, no skip) / B {restart_b[0]}..{restart_b[1]} "
      f"(past-hit restart, fork disclosed)")
assert not overlaps(W70_A, W70_B), "A/B overlap"
assert W70_B != W70_B_CHAINED, \
    "fork readings coincide -- not a fork face (W69 row projection drift," \
    "re-derive before landing)"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W70_A), ("B", W70_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 70:
            continue
        for key in ("a", "b_exit"):
            lo2, hi2 = cfg[key]
            if overlaps((lo2, hi2), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo2}..{hi2} x W70-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W70-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W70-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W70-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W70-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W70-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W70-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W70-{tag} (r335 leg)")
# canon cross-check: the landed W70 row must equal the derived candidate
assert N1_BANDS[70]["a"] == W70_A and N1_BANDS[70]["b_exit"] == W70_B, \
    "leg3 failed: canon W70 row drift vs derived candidate"
assert N1_BANDS[70]["engine_owner"] == "bm-b", "leg3 failed: W70 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 22, \
    "leg3 failed: post-land bm-b owned rows must be exactly 22 (TWENTY-SECOND " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "70: {\"a\": (183_004" not in out, \
    "leg3 failed: a W70 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "69: {\"a\": (181_004" in out, \
    "leg3 failed: the registered W69 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W70 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W70 ADMIT: A {W70_A[0]}..{W70_A[1]} ARITHMETIC CONTINUATION from the "
      f"registered W69 tail (zero skip, CLEAN == the W69 row W70+ published "
      f"projection verbatim) + B {W70_B[0]}..{W70_B[1]} PAST-HIT RESTART "
      f"after the mid-band refusal 51_000 (fork face #3: reading 2 window-"
      f"step chain 51_101..51_300 disclosed NOT taken; single-mid-hit "
      f"precedent family W26-A/W68-B; pin pending F-20261002-03) clean "
      f"vs 67 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-b "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"seat declared published=reserved; W68 bm-a + W69 bm-c = TWO "
      f"in-flight upstream seats for the W70 finalize chain, coexist per "
      f"r531, finalize FAIL-CLOSED r307; origin slot vacancy "
      f"machine-checked).")

# --- W71+ projection (warning text for the law table row) --------------------
w71_a = (W70_A[1] + 1, W70_A[1] + WIDTH_A)
w71_b = (W70_B[1] + 1, W70_B[1] + WIDTH_B)
a_hits71 = sorted(p for p in points if w71_a[0] <= p <= w71_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w71_a)]
b_hits71 = sorted(p for p in points if w71_b[0] <= p <= w71_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w71_b)]
def _first_clean(lo, width):
    while True:
        w = clean(lo, width)
        if w:
            return w
        hits = sorted(p for p in points if lo <= p <= lo + width - 1)
        lo = max(hits) + 1
print(f"W71+ projection: A arithmetic +2_000 = {w71_a[0]}..{w71_a[1]} "
      f"-> {'CLEAN (verify at W71 prereg)' if not a_hits71 else 'REFUSED ' + str(a_hits71)}; "
      f"B +200 from W70 end = {w71_b[0]}..{w71_b[1]} "
      f"-> {'CLEAN (verify at W71 prereg)' if not b_hits71 else 'REFUSED ' + str(b_hits71) + ' -> first clean ' + str(_first_clean(w71_b[0], WIDTH_B))}")
