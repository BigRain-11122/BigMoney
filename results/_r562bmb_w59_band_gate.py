"""W59 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W59 = first FREE number after the registered W58 row (bm-c r354, same-
window double-freeze with this machine's yielded r562 W58 -- commit-
order yield per r511; W58 belongs to bm-c). De-throttle law
O-20261001-2355 sec.2 own-continuous-series, first-free-number law.
r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W58 is the LAST registered row (bm-c r354 37450fcef, 10/12
shard products delivered to origin, finalize not landed); W59 slot
VACANT on origin (machine-checked at leg3); no fleet MSG declares a
W59 reservation.

bm-b's NINETEENTH owned claim (W58 same-number double-freeze yielded
to bm-c r354 this same window per r511 commit-order law; bands were
bitwise identical = deterministic cross-validation, zero arbitration).
FREEZE AUTHORITY = never-dry supply law standing step + CEO
DE-THROTTLE ORDER O-20261001-2355 sec.2.

BAND DERIVATION:
- A side: W58 A end 161_003 + 1 = 161_004..163_003 (width 2_000) --
  the W58 row W59+ WARNING projects CLEAN; machine re-derived here
  (r535 law: machine-derived, not prose-copied).
- B side: FORCED SKIP family -- arithmetic continuation
  47_801..48_000 is REFUSED at the SEED_REGISTRY point 48_000
  (p4_pairs / p1d_gdhs_quarterly, dual-key single value), exactly as
  the W58 row W59+ WARNING and BOTH independent r562/r354 gate
  projections disclosed; scan-forward first clean window
  48_001..48_200 (W39-B/W43-B/W47-B skip family; not a free pick --
  R250: W59 bands were never assigned).

Machine-verified against: all registered N1 wave bands W2..W58 (57
rows), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg), v1 in-use + W1 ext bands, live SEED_REGISTRY
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft
probe points (31_000/31_500/32_000), lfc actual draw (30_000..30_099)
AND options_wave2 actual draw (63_000..63_049).

TWO-MODE: 59 NOT in N1_BANDS -> derive-only print (exit 0); 59 in
N1_BANDS -> full ADMIT receipt (leg3 cross-checks the landed canon
row == derived candidate + origin vacancy).

r562 bm-b freeze-window run.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidates (derive-only mode prints; ADMIT mode asserts these) ---------
W59_A = (161_004, 163_003)             # W58 A end 161_003 + 1, width 2_000
W59_B = (48_001, 48_200)               # first clean window past 48_000

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

# --- leg 0: registry shape (57 registered rows W2..W58, no 15) ----------------
registered = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
              48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]
if 59 in N1_BANDS:
    assert sorted(N1_BANDS) == registered + [59], \
        f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"
else:
    assert sorted(N1_BANDS) == registered, \
        f"leg0 failed (derive mode): unexpected registry keys {sorted(N1_BANDS)}"
assert N1_BANDS[53]["engine_owner"] == "bm-c", "leg0: W53 owner drift"
assert N1_BANDS[54]["engine_owner"] == "bm-a", "leg0: W54 owner drift"
assert N1_BANDS[55]["engine_owner"] == "bm-b", "leg0: W55 owner drift"
assert N1_BANDS[56]["engine_owner"] == "bm-b", "leg0: W56 owner drift"
assert N1_BANDS[57]["engine_owner"] == "bm-a", "leg0: W57 owner drift"
assert N1_BANDS[58]["engine_owner"] == "bm-c", "leg0: W58 owner drift"
assert N1_BANDS[58]["a"] == (159_004, 161_003) and \
    N1_BANDS[58]["b_exit"] == (47_601, 47_800), \
    "leg0: W58 band drift vs the bm-c r354 registered row"

# --- reserved universe (W59 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 59:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1-A: arithmetic continuation from the REGISTERED W58 tail must be
#     CLEAN (zero-skip A side, machine-derived, not prose) --------------------
ARITH_A = (N1_BANDS[58]["a"][1] + 1, N1_BANDS[58]["a"][1] + WIDTH_A)
assert ARITH_A == W59_A, \
    f"leg1-A failed: W58 arithmetic tail {ARITH_A} != candidate {W59_A}"
a_blockers = [p for p in points if ARITH_A[0] <= p <= ARITH_A[1]]
a_blockers += [f"band {b}" for b in bands + actual if overlaps(b, ARITH_A)]
assert not a_blockers, \
    f"leg1-A failed: arithmetic window {ARITH_A} refusal facts {a_blockers}"
print(f"leg1-A arithmetic continuation {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"== candidate (W58 A end 161_003 + 1, zero skip, machine-derived "
      f"per r535 law -- the W58 row W59+ WARNING projection verified)")

# --- leg 1-B: arithmetic window must be REFUSED at 48_000 (forced-skip
#     proof, W39-B/W43-B/W47-B family; not a free pick -- R250) ----------------
ARITH_B = (N1_BANDS[58]["b_exit"][1] + 1,
           N1_BANDS[58]["b_exit"][1] + WIDTH_B)
assert ARITH_B == (47_801, 48_000), \
    f"leg1-B failed: W58 arithmetic tail {ARITH_B} != expected 47_801..48_000"
b_blockers = [p for p in points if ARITH_B[0] <= p <= ARITH_B[1]]
b_blockers += [f"band {b}" for b in bands + actual if overlaps(b, ARITH_B)]
assert b_blockers == [48_000], \
    f"leg1-B failed: arithmetic window {ARITH_B} refusal facts {b_blockers} " \
    f"-- expected exactly the SEED_REGISTRY point 48_000 (forced skip " \
    f"family, W58 row W59+ WARNING machine-proof)"
print(f"leg1-B arithmetic continuation 47_801..48_000 REFUSED "
      f"[48_000=p4_pairs/p1d_gdhs_quarterly] -- forced skip proven "
      f"machine-side (W39-B/W43-B/W47-B family; R250: not a free pick)")

# --- leg 2: first clean windows (scan-forward, both sides) --------------------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

def first_clean(start, width):
    s = start
    for _ in range(300):
        win = clean(s, width)
        if win is not None:
            return win
        blockers = [p for p in points if s <= p <= s + width - 1]
        blockers += [b for b in bands + actual
                     if overlaps((s, s + width - 1), b)]
        assert blockers, f"leg2 failed: window {s}.. unclean, no blocker"
        if any(isinstance(x, tuple) for x in blockers):
            nxt = max(b[1] for b in blockers if isinstance(b, tuple))
            s = max(s, nxt) + 1
        else:
            s = max(blockers) + 1
    raise AssertionError("leg2 failed: no clean window in scan range")

first_a = first_clean(ARITH_A[0], WIDTH_A)
assert first_a == W59_A, \
    f"leg2-A failed: machine-derived first clean window {first_a} != " \
    f"candidate {W59_A} (zero-skip A side: arithmetic == first clean, " \
    f"machine-derived, not picked -- r307/r535)"
first_b = first_clean(ARITH_B[0], WIDTH_B)
assert first_b == W59_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W59_B}"
print(f"leg2-A first clean window {first_a[0]}..{first_a[1]} == candidate "
      f"(== arithmetic continuation, zero skip)")
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"(== scan-forward past the refused 48_000 point, forced skip)")
assert not overlaps(W59_A, W59_B), "A/B overlap"

# --- leg 0b: W58 row W59+ WARNING prose present in canon ----------------------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "W59+ 警示" in canon, \
    "leg0b failed: W58 row W59+ WARNING prose missing from canon"
assert "161_004..163_003" in canon and "47_801..48_000" in canon and \
    "48_000" in canon, \
    "leg0b failed: W59+ projected band values missing from the W58 row"
print("leg0b W58 row W59+ WARNING prose present in canon "
      "(projection verified machine-side this gate, r535 law)")

# --- derive-only mode: print and exit ---------------------------------------
if 59 not in N1_BANDS:
    print(f"DERIVE-ONLY: W59 candidate A {W59_A[0]}..{W59_A[1]} / "
          f"B {W59_B[0]}..{W59_B[1]} (A = arithmetic continuation from the "
          f"registered W58 tail zero skip; B = forced skip past the "
          f"SEED_REGISTRY point 48_000) -- land the canon row then "
          f"re-run this gate for the full ADMIT receipt")
    sys.exit(0)

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W59_A), ("B", W59_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 59:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W59-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W59-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W59-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W59-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W59-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W59-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W59-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W59-{tag} (r335 leg)")
# canon cross-check: the landed W59 row must equal the derived candidate
assert N1_BANDS[59]["a"] == W59_A and N1_BANDS[59]["b_exit"] == W59_B, \
    "leg3 failed: canon W59 row drift vs derived candidate"
assert N1_BANDS[59]["engine_owner"] == "bm-b", "leg3 failed: W59 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "59: {" not in out, \
    "leg3 failed: a W59 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W59 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W59 ADMIT: A {W59_A[0]}..{W59_A[1]} arithmetic continuation from the "
      f"registered W58 tail (zero skip, machine-derived == the W58 row "
      f"W59+ WARNING) + B {W59_B[0]}..{W59_B[1]} FORCED SKIP past the "
      f"SEED_REGISTRY point 48_000 (47_801..48_000 refused machine-proven; "
      f"first clean window scan-derived, W39-B/W43-B/W47-B family; R250: "
      f"not a free pick) -- both clean vs 57 registered rows + N3-R1 "
      f"used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-b (first FREE number after the "
      f"registered W58 row; origin slot vacancy machine-checked).")

# --- W60+ projection (warning text for the law table row) --------------------
w60_a = (W59_A[1] + 1, W59_A[1] + WIDTH_A)
w60_b = (W59_B[1] + 1, W59_B[1] + WIDTH_B)
a_hits60 = sorted(p for p in points if w60_a[0] <= p <= w60_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w60_a)]
b_hits60 = sorted(p for p in points if w60_b[0] <= p <= w60_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w60_b)]
print(f"W60+ projection: A +2_000 from W59 end = {w60_a[0]}..{w60_a[1]} "
      f"-> {'CLEAN (verify at W60 prereg)' if not a_hits60 else 'REFUSED ' + str(a_hits60)}; "
      f"B +200 from W59 end = {w60_b[0]}..{w60_b[1]} "
      f"-> {'CLEAN (verify at W60 prereg)' if not b_hits60 else 'REFUSED ' + str(b_hits60)}")
