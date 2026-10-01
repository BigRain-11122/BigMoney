"""W58 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W58 = first FREE number after the registered W57 row (de-throttle law
O-20261001-2355 sec.2 own-continuous-series, first-free-number law).
r511 tail-lock: fetch + table-tail check performed at this freeze
window -- W57 is the LAST registered row (bm-a r561, burning, zero
shards on origin at this window open); W58 slot VACANT on origin
(machine-checked at leg3: no canon W58 row, no PERPETUAL-N1-W58
anywhere in scripts/research on origin/main); no fleet MSG declares a
W58 reservation (inbox empty, zero unprocessed).

bm-b's EIGHTEENTH owned claim (seventeen delivered incl. W56 burned
12/12 + finalize landed r561, ledger chain W1..W56 caught up; W57 =
bm-a owned, in flight). FREEZE AUTHORITY = never-dry supply law
standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2.

BAND DERIVATION (both sides = ARITHMETIC CONTINUATION from the
REGISTERED W57 tail, zero skip):
- A side: W57 A end 159_003 + 1 = 159_004..161_003 (width 2_000) --
  the W57 row W58+ WARNING projects CLEAN (bm-a r561 gate projection
  leg); this gate machine re-derives it (r535 law: machine-derived,
  not prose-copied).
- B side: W57 B end 47_600 + 1 = 47_601..47_800 (width 200) --
  same WARNING projects CLEAN; machine re-derived here.

Machine-verified against: all registered N1 wave bands W2..W57 (56
rows), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg), v1 in-use + W1 ext bands, live SEED_REGISTRY
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft
probe points (31_000/31_500/32_000), lfc actual draw (30_000..30_099)
AND options_wave2 actual draw (63_000..63_049).

TWO-MODE: 58 NOT in N1_BANDS -> derive-only print (exit 0); 58 in
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
W58_A = (159_004, 161_003)             # W57 A end 159_003 + 1, width 2_000
W58_B = (47_601, 47_800)               # W57 B end 47_600 + 1, width 200

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

# --- leg 0: registry shape (56 registered rows W2..W57, no 15) ----------------
registered = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
              48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
if 58 in N1_BANDS:
    assert sorted(N1_BANDS) == registered + [58], \
        f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"
else:
    assert sorted(N1_BANDS) == registered, \
        f"leg0 failed (derive mode): unexpected registry keys {sorted(N1_BANDS)}"
assert N1_BANDS[53]["engine_owner"] == "bm-c", "leg0: W53 owner drift"
assert N1_BANDS[54]["engine_owner"] == "bm-a", "leg0: W54 owner drift"
assert N1_BANDS[55]["engine_owner"] == "bm-b", "leg0: W55 owner drift"
assert N1_BANDS[56]["engine_owner"] == "bm-b", "leg0: W56 owner drift"
assert N1_BANDS[57]["engine_owner"] == "bm-a", "leg0: W57 owner drift"
assert N1_BANDS[49]["engine_owner"] == "bm-b", "leg0: W49 owner drift"
assert N1_BANDS[48]["engine_owner"] == "bm-a", "leg0: W48 owner drift"

# --- reserved universe (W58 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 58:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: arithmetic continuation from the REGISTERED W57 tail must be
#     CLEAN (zero-skip wave, machine-derived, not prose) -----------------------
ARITH_A = (N1_BANDS[57]["a"][1] + 1, N1_BANDS[57]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[57]["b_exit"][1] + 1,
           N1_BANDS[57]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W58_A, \
    f"leg1-A failed: W57 arithmetic tail {ARITH_A} != candidate {W58_A}"
assert ARITH_B == W58_B, \
    f"leg1-B failed: W57 arithmetic tail {ARITH_B} != candidate {W58_B}"
a_blockers = [p for p in points if ARITH_A[0] <= p <= ARITH_A[1]]
a_blockers += [f"band {b}" for b in bands + actual if overlaps(b, ARITH_A)]
b_blockers = [p for p in points if ARITH_B[0] <= p <= ARITH_B[1]]
b_blockers += [f"band {b}" for b in bands + actual if overlaps(b, ARITH_B)]
assert not a_blockers, \
    f"leg1-A failed: arithmetic window {ARITH_A} refusal facts {a_blockers} " \
    f"(zero-skip expectation broken -- re-derive, do not land)"
assert not b_blockers, \
    f"leg1-B failed: arithmetic window {ARITH_B} refusal facts {b_blockers} " \
    f"(zero-skip expectation broken -- re-derive, do not land)"
print(f"leg1-A arithmetic continuation {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"== candidate (W57 A end 159_003 + 1, zero skip, machine-derived "
      f"per r535 law -- the W57 row W58+ WARNING projection verified)")
print(f"leg1-B arithmetic continuation {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"== candidate (W57 B end 47_600 + 1, zero skip, machine-derived)")

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
assert first_a == W58_A, \
    f"leg2-A failed: machine-derived first clean window {first_a} != " \
    f"candidate {W58_A} (zero-skip wave: arithmetic == first clean, " \
    f"machine-derived, not picked -- r307/r535)"
first_b = first_clean(ARITH_B[0], WIDTH_B)
assert first_b == W58_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W58_B}"
print(f"leg2-A first clean window {first_a[0]}..{first_a[1]} == candidate "
      f"(== arithmetic continuation, zero skip)")
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"(== arithmetic continuation, zero skip)")
assert not overlaps(W58_A, W58_B), "A/B overlap"

# --- leg 0b: W57 row W58+ WARNING prose present in canon ----------------------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "W58+ 警示" in canon, \
    "leg0b failed: W57 row W58+ WARNING prose missing from canon"
assert "159_004..161_003" in canon and "47_601..47_800" in canon, \
    "leg0b failed: W58+ projected band values missing from the W57 row"
print("leg0b W57 row W58+ WARNING prose present in canon "
      "(projection verified machine-side this gate, r535 law)")

# --- derive-only mode: print and exit ---------------------------------------
if 58 not in N1_BANDS:
    print(f"DERIVE-ONLY: W58 candidate A {W58_A[0]}..{W58_A[1]} / "
          f"B {W58_B[0]}..{W58_B[1]} (both arithmetic continuation from "
          f"the registered W57 tail, zero skip) -- land the canon row then "
          f"re-run this gate for the full ADMIT receipt")
    sys.exit(0)

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W58_A), ("B", W58_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 58:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W58-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W58-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W58-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W58-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W58-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W58-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W58-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W58-{tag} (r335 leg)")
# canon cross-check: the landed W58 row must equal the derived candidate
assert N1_BANDS[58]["a"] == W58_A and N1_BANDS[58]["b_exit"] == W58_B, \
    "leg3 failed: canon W58 row drift vs derived candidate"
assert N1_BANDS[58]["engine_owner"] == "bm-b", "leg3 failed: W58 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "58: {" not in out, \
    "leg3 failed: a W58 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W58 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W58 ADMIT: A {W58_A[0]}..{W58_A[1]} + B {W58_B[0]}..{W58_B[1]} both "
      f"ARITHMETIC CONTINUATION from the registered W57 tail (zero skip, "
      f"machine-derived == the W57 row W58+ WARNING) both clean vs 56 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-b (first FREE "
      f"number after the registered W57 row; origin slot vacancy "
      f"machine-checked).")

# --- W59+ projection (warning text for the law table row) --------------------
w59_a = (W58_A[1] + 1, W58_A[1] + WIDTH_A)
w59_b = (W58_B[1] + 1, W58_B[1] + WIDTH_B)
a_hits59 = sorted(p for p in points if w59_a[0] <= p <= w59_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w59_a)]
b_hits59 = sorted(p for p in points if w59_b[0] <= p <= w59_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w59_b)]
print(f"W59+ projection: A +2_000 from W58 end = {w59_a[0]}..{w59_a[1]} "
      f"-> {'CLEAN (verify at W59 prereg)' if not a_hits59 else 'REFUSED ' + str(a_hits59)}; "
      f"B +200 from W58 end = {w59_b[0]}..{w59_b[1]} "
      f"-> {'CLEAN (verify at W59 prereg)' if not b_hits59 else 'REFUSED ' + str(b_hits59)}")
