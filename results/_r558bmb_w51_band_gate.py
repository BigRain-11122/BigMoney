"""W51 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W51 = next free number after the registered W50 row (r350 bm-c freeze);
bm-b's SIXTEENTH owned wave after W10/W11/W13/W16/W19/W22/W25/W28/W31/
W34/W36/W38/W40/W47/W49. FREEZE AUTHORITY = never-dry supply law
standing step + CEO DE-THROTTLE ORDER O-20261001-2355 sec.2
own-continuous-series: bm-b's TICK engine queue is EMPTY (W49 closed
r556 same-window full lifecycle: freeze 4e4f1469a -> 12/12 burn ->
finalize one-pass K=103,520 ledger 470,148, delivered to origin by
r558 S0 surgical e488e8008). r511 tail-lock: fetch + table-tail check
performed at this freeze window -- W51 slot vacant on origin (no
N1_BANDS 51 row, no canon wave-51 row; machine-checked at leg3).

BAND DERIVATION (the ONE root cause of the B-side forced skip):
- A side = ARITHMETIC CONTINUATION from the W50 row tail
  (145_004..147_003 = W50 A end 145_003 + 1), CLEAN vs the full
  reserved universe. The W50 row's W51+ WARNING projects exactly this
  window CLEAN (r350 bm-c gate legs) -- same-position cross-validation,
  NOT a reservation: bm-c declared no wave-number sovereignty for W51
  (first-free-number law -- r518-① published=reserved applies to a
  PUBLISHED NEXT-OWN-WAVE face like the bm-a W48 declaration, which is
  already covered here by the registered W48 row bands).
- B side = ARITHMETIC CONTINUATION from the W50 row tail
  (45_801..46_000 = W50 B end 45_800 + 1) is REFUSED by the live
  SEED_REGISTRY point xlib_synth_null_a = 46_000 (the exact refusal
  fact the W50 row's W51+ WARNING published: "B 45_801..46_000 REFUSED
  [SEED_REGISTRY xlib_synth_null_a=46_000]") -> scan-forward first
  clean window (W19-B re-base family). Skip is FORCED, not a free pick
  (R250: W51 bands were never assigned).

Machine-verified against: all registered N1 wave bands W2..W50 (49
rows, W48/W49/W50 included), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 bm-a mandatory leg), the runner design-probe seed
cluster 95_000..95_003 (r335 discovery leg -- mandatory on every gate
receipt from W26 on), v1-in-use + W1 ext bands, live SEED_REGISTRY
values, N2/N4 design-probe points (40_000/40_001), N2-W15 draft probe
points (31_000/31_500/32_000), lfc actual draw (30_000..30_099) AND
options_wave2 actual draw (63_000..63_049).

TWO-MODE: 51 NOT in N1_BANDS -> derive-only print (exit 0, candidate
printed for the canon landing); 51 in N1_BANDS -> full ADMIT receipt
(leg3 cross-checks the landed canon row == derived candidate).

r558 bm-b freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidates (derive-only mode prints; ADMIT mode asserts these) ---------
W51_A = (145_004, 147_003)             # arithmetic continuation (W50 A end + 1)
W51_B = (46_001, 46_200)               # FORCED SKIP past the SEED_REGISTRY
                                        # point xlib_synth_null_a=46_000
                                        # (W50 row W51+ WARNING refusal face)

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

# --- leg 0: registry shape (49 registered rows W2..W50, no 15) ---------------
registered = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
              48, 49, 50]
if 51 in N1_BANDS:
    assert sorted(N1_BANDS) == registered + [51], \
        f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"
else:
    assert sorted(N1_BANDS) == registered, \
        f"leg0 failed (derive mode): unexpected registry keys {sorted(N1_BANDS)}"
assert N1_BANDS[50]["engine_owner"] == "bm-c", "leg0: W50 owner drift"
assert N1_BANDS[49]["engine_owner"] == "bm-b", "leg0: W49 owner drift"
assert N1_BANDS[48]["engine_owner"] == "bm-a", "leg0: W48 owner drift"

# --- reserved universe (W51 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 51:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: arithmetic positions DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[50]["a"][1] + 1, N1_BANDS[50]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[50]["b_exit"][1] + 1,
           N1_BANDS[50]["b_exit"][1] + WIDTH_B)
assert ARITH_A == W51_A, f"leg1: A arithmetic {ARITH_A} != candidate {W51_A}"
assert ARITH_B == (45_801, 46_000), \
    f"leg1: B arithmetic {ARITH_B} != expected 45_801..46_000"
# A: arithmetic window must be point-clean and band-clean (ADMIT direct):
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], f"leg1-A failed: point hits {a_hits}"
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_band_hits == [], f"leg1-A failed: band hits {a_band_hits}"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (ADMIT direct -- "
      f"W50 row W51+ WARNING projected this exact window CLEAN, "
      f"same-position cross-validation r350 bm-c gate legs)")
# B: arithmetic window REFUSED by the live SEED_REGISTRY point 46_000:
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [46_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (must be exactly [46_000] " \
    f"per the W50 row W51+ WARNING published refusal face)"
b_key = [k for k, v in science_gates.SEED_REGISTRY.items()
         if isinstance(v, int) and v == 46_000]
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED refusal facts "
      f"= [SEED_REGISTRY[{b_key}]={b_hits[0]}] (W50 row W51+ WARNING "
      f"published refusal face -- FORCED skip, W19-B re-base family)")

# --- leg 2: first clean windows (scan-forward for B; A is arithmetic) -------
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# B: scan forward past the refusal point:
start = ARITH_B[0]
first_b = None
for _ in range(200):
    win = clean(start, WIDTH_B)
    if win is not None:
        first_b = win
        break
    blockers = [p for p in points if start <= p <= start + WIDTH_B - 1]
    blockers += [b for b in bands + actual
                 if overlaps((start, start + WIDTH_B - 1), b)]
    assert blockers, f"leg2-B failed: window {start}.. unclean with no blocker"
    if any(isinstance(x, tuple) for x in blockers):
        nxt = max(b[1] for b in blockers if isinstance(b, tuple))
        start = max(start, nxt) + 1
    else:
        start = max(blockers) + 1
assert first_b == W51_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W51_B} (forced scan-forward past the SEED_REGISTRY " \
    f"point 46_000, machine-derived, not picked -- r307/r535)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"(forced scan-forward past SEED_REGISTRY 46_000, W19-B re-base "
      f"family)")
# A: the arithmetic window IS the first clean window (assert via the
# scanner itself so A is machine-derived, not hand-asserted):
first_a = clean(ARITH_A[0], WIDTH_A)
assert first_a == ARITH_A == W51_A, \
    f"leg2-A failed: scanner {first_a} != arithmetic {ARITH_A} != candidate"
print(f"leg2-A arithmetic window {W51_A[0]}..{W51_A[1]} == scanner-clean "
      f"== candidate (ADMIT direct)")
assert not overlaps(W51_A, W51_B), "A/B overlap"

# --- leg 0b: W50 row W51+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "45_801..46_000" in canon and "46_000" in canon, \
    "leg0b failed: W50 row W51+ WARNING (published B refusal face) prose " \
    "not found in the canon file"
print("leg0b W50 row W51+ WARNING prose present (B refusal face "
      "45_801..46_000 [SEED_REGISTRY xlib_synth_null_a=46_000] in canon)")

# --- derive-only mode: print and exit ---------------------------------------
if 51 not in N1_BANDS:
    print(f"DERIVE-ONLY: W51 candidate A {W51_A[0]}..{W51_A[1]} (arithmetic "
          f"continuation, CLEAN) / B {W51_B[0]}..{W51_B[1]} (forced skip "
          f"past SEED_REGISTRY 46_000) -- land the canon row then re-run "
          f"this gate for the full ADMIT receipt")
    sys.exit(0)

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W51_A), ("B", W51_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 51:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W51-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W51-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W51-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W51-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W51-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W51-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W51-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W51-{tag} (r335 leg)")
# canon cross-check: the landed W51 row must equal the derived candidate
assert N1_BANDS[51]["a"] == W51_A and N1_BANDS[51]["b_exit"] == W51_B, \
    "leg3 failed: canon W51 row drift vs derived candidate"
assert N1_BANDS[51]["engine_owner"] == "bm-b", "leg3 failed: W51 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "51: {\"a\": (145_004" not in out, \
    "leg3 failed: a W51 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg) | "
      f"W50 row W51+ WARNING: B 45_801..46_000 REFUSED "
      f"[SEED_REGISTRY xlib_synth_null_a=46_000]")
if conflicts:
    print("W51 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W51 ADMIT: A {W51_A[0]}..{W51_A[1]} (arithmetic continuation, "
      f"CLEAN) + B {W51_B[0]}..{W51_B[1]} (FORCED SKIP past the "
      f"SEED_REGISTRY point 46_000 per the W50 row W51+ WARNING "
      f"published refusal face, W19-B re-base family) both clean vs "
      f"49 registered rows + N3-R1 used-seed band + probe-seed cluster "
      f"+ registry values + probes/actuals -- engine_owner=bm-b "
      f"(next free number after W50; zero-gap relay after the W49 "
      f"full closeout r556/r558; origin slot vacancy machine-checked).")

# --- W52+ projection (warning text for the law table row) --------------------
w52_a = (W51_A[1] + 1, W51_A[1] + WIDTH_A)
w52_b = (W51_B[1] + 1, W51_B[1] + WIDTH_B)
a_hits52 = sorted(p for p in points if w52_a[0] <= p <= w52_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w52_a)]
b_hits52 = sorted(p for p in points if w52_b[0] <= p <= w52_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w52_b)]
print(f"W52+ projection: A arithmetic +2_000 = {w52_a[0]}..{w52_a[1]} "
      f"-> {'CLEAN (verify at W52 prereg)' if not a_hits52 else 'REFUSED ' + str(a_hits52)}; "
      f"B +200 from W51 end = {w52_b[0]}..{w52_b[1]} "
      f"-> {'CLEAN (verify at W52 prereg)' if not b_hits52 else 'REFUSED ' + str(b_hits52)}")
