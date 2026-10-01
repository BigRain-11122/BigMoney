"""W55 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W55 = first FREE number after the registered W53 row PLUS the bm-a
PUBLISHED W54 declaration (r518-1 published=reserved law, W48/W49
precedent): bm-a MSG-20261002-0615 addendum declares "bm-a next own
target = W54 (A 151_004..153_003 / B 46_601..46_800)" -- the declared
bands enter the reserved universe even before registration, so wave
54 is NOT free. bm-b yields its same-window W54 freeze to that
declaration (local commit 6b2bc5e9f abandoned, 2 re-burn shards
discarded, zero ledger face) and takes W55.

bm-b's SIXTEENTH owned claim (fifteen delivered: W10/W11/W13/W16/W19/
W22/W25/W28/W31/W34/W36/W38/W40/W47/W49; W51 yielded r558, W53
yielded r559 -- both same-band double-freezes vs bm-c; W54 yielded
r559 to the bm-a published declaration). FREEZE AUTHORITY = never-dry
supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series. r511 tail-lock: fetch + table-tail check
performed at this freeze window -- W55 slot vacant on origin
(machine-checked at leg3); W54 declared (bm-a) or registered
(adaptivity: if 54 IS in N1_BANDS at gate time, the registered row
must equal the declared bands and carry engine_owner=bm-a).

BAND DERIVATION (both sides = scan-forward first-clean past the
W54 published reservation + the 47_000 registry point):
- A side: the arithmetic tail from W53 (151_004..153_003) IS the
  bm-a declared W54 A band -> REFUSED by the published=reserved face
  -> scan-forward first clean window = 153_004..155_003 (declared
  W54 A end + 1, arithmetic continuation of the reservation tail --
  W19-A re-base family, r518-1).
- B side: the arithmetic tail from W53 (46_601..46_800) IS the bm-a
  declared W54 B band -> REFUSED; the next window 46_801..47_000 is
  REFUSED at its tail point by the live SEED_REGISTRY point
  xlib_synth_null_b = 47_000 -> first clean window = 47_001..47_200
  (W51-B re-base family: xlib_synth_null_a=46_000 forced the W51
  skip; xlib_synth_null_b=47_000 forces the W55 skip).

Machine-verified against: all registered N1 wave bands W2..W53 (51
rows) + the bm-a declared W54 bands, the N3-R1 USED-SEED BAND
70_000..70_005 (MSG-183x r529 mandatory leg), the runner design-probe
seed cluster 95_000..95_003 (r335 discovery leg -- mandatory on every
gate receipt from W26 on), v1-in-use + W1 ext bands, live
SEED_REGISTRY values, N2/N4 design-probe points (40_000/40_001),
N2-W15 draft probe points (31_000/31_500/32_000), lfc actual draw
(30_000..30_099) AND options_wave2 actual draw (63_000..63_049).

TWO-MODE: 55 NOT in N1_BANDS -> derive-only print (exit 0); 55 in
N1_BANDS -> full ADMIT receipt (leg3 cross-checks the landed canon
row == derived candidate).

r559 bm-b freeze-window run (de-throttle order O-20261001-2355 sec.2).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

# --- candidates (derive-only mode prints; ADMIT mode asserts these) ---------
W55_A = (153_004, 155_003)             # first clean past the bm-a declared
                                        # W54 A band (published=reserved)
W55_B = (47_001, 47_200)               # first clean past the bm-a declared
                                        # W54 B band AND the SEED_REGISTRY
                                        # point xlib_synth_null_b=47_000

# --- bm-a published W54 declaration (MSG-20261002-0615-bm-a addendum) ------
W54_DECLARED_A = (151_004, 153_003)
W54_DECLARED_B = (46_601, 46_800)

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

# --- leg 0: registry shape (51 registered rows W2..W53, no 15; W54 may be
#     registered by bm-a mid-window -- adaptivity, declared==registered) ---
registered = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
              48, 49, 50, 51, 52, 53]
if 54 in N1_BANDS:
    assert N1_BANDS[54]["engine_owner"] == "bm-a", \
        "leg0 failed: W54 registered by someone other than bm-a (the " \
        "published declarer -- r518-1 violation face)"
    assert tuple(N1_BANDS[54]["a"]) == W54_DECLARED_A, \
        "leg0 failed: registered W54 A drifts from the bm-a declaration"
    assert tuple(N1_BANDS[54]["b_exit"]) == W54_DECLARED_B, \
        "leg0 failed: registered W54 B drifts from the bm-a declaration"
    reg_expected = registered + [54]
else:
    reg_expected = registered
if 55 in N1_BANDS:
    assert sorted(N1_BANDS) == reg_expected + [55], \
        f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)}"
else:
    assert sorted(N1_BANDS) == reg_expected, \
        f"leg0 failed (derive mode): unexpected registry keys {sorted(N1_BANDS)}"
assert N1_BANDS[53]["engine_owner"] == "bm-c", "leg0: W53 owner drift"
assert N1_BANDS[52]["engine_owner"] == "bm-c", "leg0: W52 owner drift"
assert N1_BANDS[49]["engine_owner"] == "bm-b", "leg0: W49 owner drift"
assert N1_BANDS[48]["engine_owner"] == "bm-a", "leg0: W48 owner drift"

# --- reserved universe (W55 itself EXCLUDED -- it is the candidate;
#     the bm-a declared W54 bands enter when unregistered, r518-1) -----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 55:
        continue                         # candidate wave, not a reserved face
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
if 54 not in N1_BANDS:
    bands += [("declared-W54-A", )]      # placeholder replaced below
    bands.pop()
    bands.append(W54_DECLARED_A)         # published=reserved face (r518-1)
    bands.append(W54_DECLARED_B)
declared_band_tags = [] if 54 in N1_BANDS else \
    [f"bm-a declared W54 A {W54_DECLARED_A[0]}..{W54_DECLARED_A[1]}",
     f"bm-a declared W54 B {W54_DECLARED_B[0]}..{W54_DECLARED_B[1]}"]
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: arithmetic tails from the REGISTERED W53 tail and their
#     refusal facts (machine-derived, not prose) ------------------------------
ARITH_A = (N1_BANDS[53]["a"][1] + 1, N1_BANDS[53]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[53]["b_exit"][1] + 1,
           N1_BANDS[53]["b_exit"][1] + WIDTH_B)
# A: the arithmetic window IS the bm-a declared W54 A band -> refused
a_hit_decl = overlaps(W54_DECLARED_A, ARITH_A) and ARITH_A == W54_DECLARED_A
assert a_hit_decl, \
    f"leg1-A failed: the W53 arithmetic tail {ARITH_A} must equal the " \
    f"bm-a declared W54 A band {W54_DECLARED_A} (published=reserved face)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} REFUSED = bm-a "
      f"declared W54 A band (MSG-0615 addendum, published=reserved "
      f"r518-1 -- same-window W54 freeze yielded, local 6b2bc5e9f "
      f"abandoned)")
# B: the arithmetic window IS the bm-a declared W54 B band -> refused
b_hit_decl = ARITH_B == W54_DECLARED_B
assert b_hit_decl, \
    f"leg1-B failed: the W53 arithmetic tail {ARITH_B} must equal the " \
    f"bm-a declared W54 B band {W54_DECLARED_B}"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED = bm-a "
      f"declared W54 B band (published=reserved r518-1)")
# B second refusal: the NEXT window after the declared band hits the
# SEED_REGISTRY point 47_000 at its tail
NEXT_B = (W54_DECLARED_B[1] + 1, W54_DECLARED_B[1] + WIDTH_B)
next_b_hits = sorted(p for p in points if NEXT_B[0] <= p <= NEXT_B[1])
assert next_b_hits == [47_000], \
    f"leg1-B2 failed: post-declaration window {NEXT_B} refusal facts " \
    f"drift {next_b_hits} (must be exactly [47_000] per the live " \
    f"SEED_REGISTRY point xlib_synth_null_b=47_000)"
b_key = [k for k, v in science_gates.SEED_REGISTRY.items()
         if isinstance(v, int) and v == 47_000]
print(f"leg1-B2 post-declaration window {NEXT_B[0]}..{NEXT_B[1]} REFUSED "
      f"[SEED_REGISTRY[{b_key}]=47_000] (W51-B re-base family: "
      f"xlib_synth_null_a=46_000 -> xlib_synth_null_b=47_000 ladder)")

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

# A: scan forward past the declared W54 A band
first_a = first_clean(ARITH_A[0], WIDTH_A)
assert first_a == W55_A, \
    f"leg2-A failed: machine-derived first clean window {first_a} != " \
    f"candidate {W55_A} (scan past the bm-a declared W54 A band, " \
    f"machine-derived, not picked -- r307/r535/r518-1)"
print(f"leg2-A first clean window {first_a[0]}..{first_a[1]} == candidate "
      f"(scan-forward past the bm-a declared W54 A band, "
      f"W19-A re-base family)")
# B: scan forward past the declared W54 B band + the 47_000 point
first_b = first_clean(ARITH_B[0], WIDTH_B)
assert first_b == W55_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W55_B} (scan past the declared W54 B band AND the " \
    f"SEED_REGISTRY point 47_000, machine-derived)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} == candidate "
      f"(scan-forward past the declared W54 B band + SEED_REGISTRY "
      f"xlib_synth_null_b=47_000, W51-B re-base family)")
assert not overlaps(W55_A, W55_B), "A/B overlap"

# --- leg 0b: bm-a W54 declaration prose present in the adopted MSG file ----
msg = open(os.path.join(ROOT, "fleet", "inbox",
                        "MSG-20261002-0615-bm-a.md"),
           encoding="utf-8").read()
assert "bm-a next own target = **W54**" in msg, \
    "leg0b failed: bm-a W54 declaration prose missing from " \
    "MSG-20261002-0615-bm-a.md"
assert "151_004..153_003" in msg and "46_601..46_800" in msg, \
    "leg0b failed: declared W54 band values missing from the MSG prose"
print("leg0b bm-a W54 declaration prose present in "
      "fleet/inbox/MSG-20261002-0615-bm-a.md (published=reserved face)")

# --- derive-only mode: print and exit ---------------------------------------
if 55 not in N1_BANDS:
    print(f"DERIVE-ONLY: W55 candidate A {W55_A[0]}..{W55_A[1]} (scan past "
          f"bm-a declared W54 A) / B {W55_B[0]}..{W55_B[1]} (scan past "
          f"declared W54 B + SEED_REGISTRY 47_000) -- land the canon row "
          f"then re-run this gate for the full ADMIT receipt")
    sys.exit(0)

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W55_A), ("B", W55_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 55:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W55-{tag}")
    if 54 not in N1_BANDS:
        for nm, db in (("declared-W54-A", W54_DECLARED_A),
                      ("declared-W54-B", W54_DECLARED_B)):
            if overlaps(db, band):
                conflicts.append(f"{nm} {db[0]}..{db[1]} x W55-{tag} "
                                 f"(published=reserved r518-1)")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W55-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W55-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W55-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W55-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W55-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                         f"x W55-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W55-{tag} (r335 leg)")
# canon cross-check: the landed W55 row must equal the derived candidate
assert N1_BANDS[55]["a"] == W55_A and N1_BANDS[55]["b_exit"] == W55_B, \
    "leg3 failed: canon W55 row drift vs derived candidate"
assert N1_BANDS[55]["engine_owner"] == "bm-b", "leg3 failed: W55 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "55: {" not in out, \
    "leg3 failed: a W55 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

w54_face = ("REGISTERED (bm-a)" if 54 in N1_BANDS
            else "DECLARED (published=reserved r518-1, bands in universe)")
print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg) | "
      f"W54 face: {w54_face}")
if conflicts:
    print("W55 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W55 ADMIT: A {W55_A[0]}..{W55_A[1]} (scan past the bm-a declared "
      f"W54 A band) + B {W55_B[0]}..{W55_B[1]} (scan past the declared "
      f"W54 B band AND the SEED_REGISTRY point xlib_synth_null_b=47_000, "
      f"W51-B re-base family) both clean vs 51-52 registered/declared rows "
      f"+ N3-R1 used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-b (first FREE number after the "
      f"registered W53 row and the bm-a declared W54 slot; origin slot "
      f"vacancy machine-checked).")

# --- W56+ projection (warning text for the law table row) --------------------
w56_a = (W55_A[1] + 1, W55_A[1] + WIDTH_A)
w56_b = (W55_B[1] + 1, W55_B[1] + WIDTH_B)
a_hits56 = sorted(p for p in points if w56_a[0] <= p <= w56_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w56_a)]
b_hits56 = sorted(p for p in points if w56_b[0] <= p <= w56_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w56_b)]
print(f"W56+ projection: A +2_000 from W55 end = {w56_a[0]}..{w56_a[1]} "
      f"-> {'CLEAN (verify at W56 prereg)' if not a_hits56 else 'REFUSED ' + str(a_hits56)}; "
      f"B +200 from W55 end = {w56_b[0]}..{w56_b[1]} "
      f"-> {'CLEAN (verify at W56 prereg)' if not b_hits56 else 'REFUSED ' + str(b_hits56)}")
