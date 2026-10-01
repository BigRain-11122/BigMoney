"""W60 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W60 = first FREE number after the registered W59 row (bm-b r562, finalize
landed r563 one-pass ledger 494,348). De-throttle law O-20261001-2355
sec.2 own-continuous-series, first-free-number law.
r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W59 is the LAST registered row (r562 bm-b, 12/12 burned,
finalize landed this r563 window); W60 slot VACANT on origin
(machine-checked at leg3); no fleet MSG declares a W60 reservation.

bm-b's TWENTIETH owned claim (W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/
W36/W38/W40/W47/W49/W55/W56/W59 = nineteen delivered; r558 W51/r559 W53
same-band double-freeze yields to bm-c + r559 W54 declared-slot yield to
bm-a + r562 W58 same-number double-freeze yield to bm-c per r511
commit-order law, honest notes). FREEZE AUTHORITY = never-dry supply law
standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2.

BAND DERIVATION (r535 law: machine-derived, not prose-copied):
- A side: W59 A end 163_003 + 1 = 163_004..165_003 (width 2_000) --
  the W59 row W60+ WARNING defers to this gate's projection leg;
  machine re-derived here.
- B side: W59 B end 48_200 + 1 = 48_201..48_400 (width 200) --
  arithmetic continuation, machine-checked CLEAN/REFUSED here.

Machine-verified against: all registered N1 wave bands W2..W59 (58
rows), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg), v1 in-use + W1 ext bands, live SEED_REGISTRY
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft
probe points (31_000/31_500/32_000), lfc actual draw (30_000..30_099)
AND options_wave2 actual draw (63_000..63_049).

TWO-MODE: 60 NOT in N1_BANDS -> derive-only print (exit 0); 60 in
N1_BANDS -> full ADMIT receipt (leg3 cross-checks the landed canon
row == derived candidate + origin vacancy).

r563 bm-b freeze-window run.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidates (derive-only mode prints; ADMIT mode asserts these) ---------
W60_A = (163_004, 165_003)             # W59 A end 163_003 + 1, width 2_000
W60_B = (48_201, 48_400)               # W59 B end 48_200 + 1, width 200

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

# --- leg 0: registry shape (58 registered rows W2..W59, no 15) ----------------
registered = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
              48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
if 60 in N1_BANDS:
    assert sorted(N1_BANDS) == registered + [60], \
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
assert N1_BANDS[59]["engine_owner"] == "bm-b", "leg0: W59 owner drift"
assert N1_BANDS[59]["a"] == (161_004, 163_003) and \
    N1_BANDS[59]["b_exit"] == (48_001, 48_200), \
    "leg0: W59 band drift vs the r562 registered row"

# --- reserved universe (W60 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 60:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1-A: arithmetic continuation from the REGISTERED W59 tail must be
#     CLEAN (zero-skip A side, machine-derived, not prose) --------------------
ARITH_A = (N1_BANDS[59]["a"][1] + 1, N1_BANDS[59]["a"][1] + WIDTH_A)
assert ARITH_A == W60_A, \
    f"leg1-A failed: W59 arithmetic tail {ARITH_A} != candidate {W60_A}"
a_blockers = [p for p in points if ARITH_A[0] <= p <= ARITH_A[1]]
a_blockers += [f"band {b}" for b in bands + actual if overlaps(b, ARITH_A)]
assert not a_blockers, \
    f"leg1-A failed: arithmetic window {ARITH_A} refusal facts {a_blockers}"
print(f"leg1-A arithmetic continuation {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"== candidate (W59 A end 163_003 + 1, zero skip, machine-derived "
      f"per r535 law -- the W59 row W60+ WARNING projection verified)")

# --- leg 1-B: arithmetic continuation from the REGISTERED W59 tail --
#     machine-checked CLEAN or REFUSED (zero-skip family if clean) -----------
ARITH_B = (N1_BANDS[59]["b_exit"][1] + 1,
           N1_BANDS[59]["b_exit"][1] + WIDTH_B)
assert ARITH_B == (48_201, 48_400), \
    f"leg1-B failed: W59 arithmetic tail {ARITH_B} != expected 48_201..48_400"
b_blockers = [p for p in points if ARITH_B[0] <= p <= ARITH_B[1]]
b_blockers += [f"band {b}" for b in bands + actual if overlaps(b, ARITH_B)]
if b_blockers:
    print(f"leg1-B arithmetic continuation 48_201..48_400 REFUSED "
          f"{b_blockers} -- forced-skip family (scan-forward, R250: "
          f"not a free pick)")
else:
    print(f"leg1-B arithmetic continuation 48_201..48_400 CLEAN "
          f"(zero-skip B side, machine-derived per r535 law)")

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
assert first_a == W60_A, \
    f"leg2-A failed: machine-derived first clean window {first_a} != " \
    f"candidate {W60_A} (zero-skip A side: arithmetic == first clean, " \
    f"machine-derived, not picked -- r307/r535)"
first_b = first_clean(ARITH_B[0], WIDTH_B)
assert first_b == W60_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W60_B}"
print(f"leg2-A first clean window {first_a[0]}..{first_a[1]} == candidate "
      f"(== arithmetic continuation, zero skip)")
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"({'== arithmetic continuation, zero skip' if not b_blockers else 'scan-forward past refused points, forced skip'})")
assert not overlaps(W60_A, W60_B), "A/B overlap"

# --- leg 0b: W59 row W60+ WARNING prose present in canon ----------------------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "W60+ 警示" in canon, \
    "leg0b failed: W59 row W60+ WARNING prose missing from canon"
assert "163_004..165_003" in canon and "48_201..48_400" in canon, \
    "leg0b failed: W60+ projected band values missing from the W59 row"
print("leg0b W59 row W60+ WARNING prose present in canon "
      "(projection verified machine-side this gate, r535 law)")

# --- derive-only mode: print and exit ---------------------------------------
if 60 not in N1_BANDS:
    print(f"DERIVE-ONLY: W60 candidate A {W60_A[0]}..{W60_A[1]} / "
          f"B {W60_B[0]}..{W60_B[1]} (A = arithmetic continuation from the "
          f"registered W59 tail zero skip; B = {'arithmetic continuation zero skip' if not b_blockers else 'forced skip scan-forward'}) "
          f"-- land the canon row then re-run this gate for the full "
          f"ADMIT receipt")
    sys.exit(0)

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W60_A), ("B", W60_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 60:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W60-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W60-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W60-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W60-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W60-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W60-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W60-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W60-{tag} (r335 leg)")
# canon cross-check: the landed W60 row must equal the derived candidate
assert N1_BANDS[60]["a"] == W60_A and N1_BANDS[60]["b_exit"] == W60_B, \
    "leg3 failed: canon W60 row drift vs derived candidate"
assert N1_BANDS[60]["engine_owner"] == "bm-b", "leg3 failed: W60 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "60: {" not in out, \
    "leg3 failed: a W60 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W60 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W60 ADMIT: A {W60_A[0]}..{W60_A[1]} + B {W60_B[0]}..{W60_B[1]} "
      f"{'BOTH ARITHMETIC CONTINUATION zero skip' if not b_blockers else 'A arithmetic / B forced skip'} "
      f"from the registered W59 tail (machine-derived == the W59 row "
      f"W60+ WARNING projection; R250: not a free pick) -- both clean vs "
      f"58 registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-b (first FREE "
      f"number after the registered W59 row; origin slot vacancy "
      f"machine-checked).")

# --- W61+ projection (warning text for the law table row) --------------------
w61_a = (W60_A[1] + 1, W60_A[1] + WIDTH_A)
w61_b = (W60_B[1] + 1, W60_B[1] + WIDTH_B)
a_hits61 = sorted(p for p in points if w61_a[0] <= p <= w61_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w61_a)]
b_hits61 = sorted(p for p in points if w61_b[0] <= p <= w61_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w61_b)]
print(f"W61+ projection: A +2_000 from W60 end = {w61_a[0]}..{w61_a[1]} "
      f"-> {'CLEAN (verify at W61 prereg)' if not a_hits61 else 'REFUSED ' + str(a_hits61)}; "
      f"B +200 from W60 end = {w61_b[0]}..{w61_b[1]} "
      f"-> {'CLEAN (verify at W61 prereg)' if not b_hits61 else 'REFUSED ' + str(b_hits61)}")
