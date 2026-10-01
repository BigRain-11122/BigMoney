"""W51 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W51 = FOURTIETH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's FIFTEENTH owned wave). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series: bm-c's previous wave W50
was frozen + burned 12/12 in this same window (r350: freeze b6142842d
-> no-restart per-tick re-read ignition -> 12/12 shards) -> zero-gap
relay, wave number 51 = FIRST FREE NUMBER after the registered W50
row (W48/W49/W50 all registered, their finalizes chain-ordered and
pending).

The W50 row's W51+ WARNING projects: A arithmetic CLEAN
(145_004..147_003 = W50 A end + 1) but B arithmetic (45_801..46_000)
REFUSED -- SEED_REGISTRY[xlib_synth_null_a]=46_000 tail point inside
the window; W51-B must machine-derive the first clean window
(projected 46_001..46_200, W26-A/W39-B/W43-B skip family). r335
lesson + r535 law: this gate re-derives from the live registry, never
trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W50 (47
rows, incl. W48 bm-a r557 + W49 bm-b r556 + W50 bm-c r350 -- all
in-flight finalizes coexist by band disjointness per r531 law), the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw.

r350 bm-c freeze-window run (de-throttle order O-20261001-2355 sec.2).
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
W51_A = (145_004, 147_003)              # law sec.4 W51 row (arithmetic, no skip)
W51_B = (46_001, 46_200)                # machine-derived first clean window
                                        # (arithmetic 45_801..46_000 REFUSED)

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

# --- reserved universe (W51 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 51:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (47 pre-W51 rows + the candidate) ------------------
assert 50 in N1_BANDS and N1_BANDS[50]["engine_owner"] == "bm-c", \
    "leg0 failed: W50 (bm-c) row must be present (r350 freeze this window, " \
    "burn 12/12, finalize chain-pending)"
assert 49 in N1_BANDS and N1_BANDS[49]["engine_owner"] == "bm-b", \
    "leg0 failed: W49 (bm-b) row must be present (r556 freeze, finalize pending)"
assert 48 in N1_BANDS and N1_BANDS[48]["engine_owner"] == "bm-a", \
    "leg0 failed: W48 (bm-a) row must be present (r557 freeze, finalize pending)"
assert 47 in N1_BANDS and N1_BANDS[47]["engine_owner"] == "bm-b", \
    "leg0 failed: W47 (bm-b) row must be present (r556 finalize landed " \
    "same-window K=101,320 ledger 467,948)"
pre_w51 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51]
assert sorted(N1_BANDS) == pre_w51, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 47 " \
    f"registered rows + the W51 candidate)"

# --- leg 0b: W50 row's W51+ WARNING prose present in the canon law file ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "145_004..147_003" in canon and "45_801..46_000" in canon \
    and "46_001..46_200" in canon, \
    "leg0b failed: W50 row W51+ WARNING (published projection + forced-skip " \
    "projection) prose not found in the canon file"
print("leg0b W50 row W51+ WARNING prose present (published projection basis; "
      "machine-derived per r535)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[50]["a"][1] + 1, N1_BANDS[50]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[50]["b_exit"][1] + 1,
           N1_BANDS[50]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W50 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W50 "
      f"projection verified machine-side)")
# B tail projected REFUSED (SEED_REGISTRY xlib_synth_null_a=46_000) --
# machine-prove the skip is FORCED (not a free choice, R250 discipline):
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits != [], \
    "leg1-B failed: W50 row projected REFUSED but arithmetic window is " \
    "CLEAN machine-side -- projection drift, re-derive before landing"
assert 46_000 in b_hits, \
    f"leg1-B failed: expected SEED_REGISTRY[xlib_synth_null_a]=46_000 in " \
    f"refusal facts, got {b_hits} (W50 row W51+ WARNING identity drift)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED -- "
      f"refusal facts {b_hits} (skip FORCED machine-proven, W50 row "
      f"WARNING verified; not a free pick)")

# --- leg 2: first clean window (A == arithmetic; B == machine-derived) ------
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
assert first_a == W51_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W51_A} " \
    "(no skip expected; R250/r518 machine-derived)"
start = ARITH_B[0]
first_b = None
for _ in range(200):
    win = clean(start, WIDTH_B)
    if win is not None:
        first_b = win
        break
    blockers = [p for p in points if start <= p <= start + WIDTH_B - 1]
    assert blockers, \
        f"leg2-B failed: window {start}.. unclean with no point blocker " \
        "(band overlap must not occur in the B ladder -- investigate)"
    start = max(blockers) + 1
assert first_b == W51_B, \
    f"leg2-B failed: machine-derived first clean window {first_b} != " \
    f"candidate {W51_B} (forced-skip derivation, not picked -- r307/r535; " \
    f"W26-A/W39-B/W43-B skip family precedent)"
print(f"leg2-B first clean window {first_b[0]}..{first_b[1]} "
      f"== candidate (forced-skip derivation past 46_000, not picked)")
assert not overlaps(W51_A, W51_B), "A/B overlap"

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
assert N1_BANDS[51]["engine_owner"] == "bm-c", "leg3 failed: W51 owner drift"
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
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W51 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W51 ADMIT: A {W51_A[0]}..{W51_A[1]} (arithmetic continuation from "
      f"W50 tail, no skip) + B {W51_B[0]}..{W51_B[1]} (forced-skip first "
      f"clean window past SEED_REGISTRY[xlib_synth_null_a]=46_000) both "
      f"clean vs 47 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-c "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"zero-gap relay after the W50 freeze+burn this same window; "
      f"W48/W49/W50 in-flight finalizes coexist per r531; origin slot "
      f"vacancy machine-checked).")

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
