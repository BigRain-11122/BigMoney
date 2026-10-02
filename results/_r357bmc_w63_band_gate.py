"""W63 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W63 = FIFTY-SECOND ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's TWENTIETH owned wave per machine-derive).
FREEZE AUTHORITY = never-dry supply law standing step + CEO DE-THROTTLE
ORDER O-20261001-2355 sec.2 own-continuous-series. Wave number 63 =
FIRST FREE NUMBER after the registered W62 row (origin slot vacancy
machine-checked at leg3); chain FULLY CAUGHT UP W1..W62 at this freeze
-- ledger head 500,948, K=134,320 (W61+W62 both finalized one-pass by
bm-c r357 in this same window: 2eb556a8f + c2d4fb7a9), ZERO in-flight
upstream seats.

The W62 row's W63+ WARNING projects A 169_004..171_003 CLEAN and
B 48_801..49_000 REFUSED [SEED_REGISTRY p4_ext_tilt_q=49_000 +
p4_ext_tilt_d20=49_100]. r335 lesson + r535 law: this gate re-derives
from the live registry, never trusts the prose.

Machine-verified against: all registered N1 wave bands W2..W62 (60
rows, all finalizes landed), the N3-R1 USED-SEED BAND 70_000..70_005
(MSG-183x r529 mandatory leg), the runner design-probe seed cluster
95_000..95_003 (r335 discovery leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 design-probe points, N2-W15 draft
probe points, lfc actual draw and options_wave2 actual draw.

r357 bm-c freeze-window run (never-dry standing step, O-20261001-2355
sec.2 own-series).
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
W63_A = (169_004, 171_003)              # law sec.4 W63 row (arithmetic, no skip)
W63_B = (49_201, 49_400)                # forced skip first-clean window

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

# --- reserved universe (W63 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 63:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (60 pre-W63 rows + the candidate) ------------------
assert 62 in N1_BANDS and N1_BANDS[62]["engine_owner"] == "bm-a", \
    "leg0 failed: W62 (bm-a) row must be present (freeze landed r565; " \
    "12/12 burn bm-a tick engine; one-pass finalize bm-c r357 K=134,320 " \
    "ledger head 500,948)"
assert 61 in N1_BANDS and N1_BANDS[61]["engine_owner"] == "bm-b", \
    "leg0 failed: W61 (bm-b) row must be present (burned 12/12 bm-c " \
    "resident engine; finalize bm-c r357 K=132,120 ledger 498,748)"
assert 60 in N1_BANDS and N1_BANDS[60]["engine_owner"] == "bm-c", \
    "leg0 failed: W60 (bm-c) row must be present (finalize landed r355 " \
    "K=129,920 ledger 496,548)"
assert 59 in N1_BANDS and N1_BANDS[59]["engine_owner"] == "bm-b", \
    "leg0 failed: W59 (bm-b) row must be present (finalize landed r563 " \
    "K=127,720 ledger 494,348)"
pre_w63 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
assert sorted(N1_BANDS) == pre_w63, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 60 " \
    f"registered rows + the W63 candidate)"

# --- leg 0b: W62 row's W63+ WARNING prose present in the canon law file ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "169_004..171_003" in canon and "48_801..49_000" in canon, \
    "leg0b failed: W62 row W63+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W62 row W63+ WARNING prose present (published projection "
      "basis; machine-derived per r535; W62 bm-a r565 freeze + one-pass "
      "finalize receipt r357 bm-c confirms the W63 window state)")

# --- leg 1: arithmetic positions DERIVED FROM THE REGISTRY (not prose) ------
ARITH_A = (N1_BANDS[62]["a"][1] + 1, N1_BANDS[62]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[62]["b_exit"][1] + 1,
           N1_BANDS[62]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W62 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W62 "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [49_000], \
    f"leg1-B failed: expected refusal fact [49000] (p4_ext_tilt_q), " \
    f"got {b_hits} (W62 row projected REFUSED at 49_000)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED at "
      f"{b_hits} (p4_ext_tilt_q=49_000 per the W62 row W63+ WARNING -- "
      f"forced-skip family engaged, r307 wave-band tail law)")

# --- leg 2: first clean windows ----------------------------------------------
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
assert first_a == W63_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W63_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# B-side chained-skip scan: 48_801..49_000 refused at 49_000;
# 49_001..49_200 refused at 49_100 (p4_ext_tilt_d20); first clean
# thereafter must equal the candidate.
second = clean(ARITH_B[0] + WIDTH_B, WIDTH_B)
assert second is None and 49_100 in points, \
    "leg2-B failed: the 49_001..49_200 chained window must be refused " \
    "at p4_ext_tilt_d20=49_100 (W62 row WARNING face)"
first_b = clean(ARITH_B[0] + 2 * WIDTH_B, WIDTH_B)
assert first_b == W63_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W63_B} " \
    "(forced skip expected this wave; R250/r518 machine-derived)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} == "
      f"arithmetic (no skip) / B {first_b[0]}..{first_b[1]} == "
      f"machine-derived first clean (skip #2: 48_801..49_000 + "
      f"49_001..49_200 both refused)")
assert not overlaps(W63_A, W63_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W63_A), ("B", W63_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 63:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W63-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W63-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W63-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W63-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W63-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W63-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W63-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W63-{tag} (r335 leg)")
# canon cross-check: the landed W63 row must equal the derived candidate
assert N1_BANDS[63]["a"] == W63_A and N1_BANDS[63]["b_exit"] == W63_B, \
    "leg3 failed: canon W63 row drift vs derived candidate"
assert N1_BANDS[63]["engine_owner"] == "bm-c", "leg3 failed: W63 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "63: {\"a\": (169_004" not in out, \
    "leg3 failed: a W63 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W63 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W63 ADMIT: A {W63_A[0]}..{W63_A[1]} (arithmetic continuation from "
      f"the W62 tail, no skip) + B {W63_B[0]}..{W63_B[1]} (forced skip: "
      f"48_801..49_000 refused at p4_ext_tilt_q=49_000, 49_001..49_200 "
      f"refused at p4_ext_tilt_d20=49_100, first clean window "
      f"machine-derived) both clean vs 60 registered rows + N3-R1 "
      f"used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-c (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; chain FULLY CAUGHT UP W1..W62 "
      f"zero in-flight upstream seats (W61+W62 one-pass finalizes bm-c "
      f"r357 same window, ledger head 500,948); origin slot vacancy "
      f"machine-checked).")

# --- W64+ projection (warning text for the law table row) --------------------
w64_a = (W63_A[1] + 1, W63_A[1] + WIDTH_A)
w64_b = (W63_B[1] + 1, W63_B[1] + WIDTH_B)
a_hits64 = sorted(p for p in points if w64_a[0] <= p <= w64_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w64_a)]
b_hits64 = sorted(p for p in points if w64_b[0] <= p <= w64_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w64_b)]
print(f"W64+ projection: A arithmetic +2_000 = {w64_a[0]}..{w64_a[1]} "
      f"-> {'CLEAN (verify at W64 prereg)' if not a_hits64 else 'REFUSED ' + str(a_hits64)}; "
      f"B +200 from W63 end = {w64_b[0]}..{w64_b[1]} "
      f"-> {'CLEAN (verify at W64 prereg)' if not b_hits64 else 'REFUSED ' + str(b_hits64)}")
