"""W64 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W64 = FIFTY-THIRD ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-a -- bm-a's FIFTEENTH owned per machine-derive:
engine_owner==bm-a rows 14 + candidate). FREEZE AUTHORITY = never-dry
supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series + SEAT DECLARED published=reserved
(MSG-20261002-0851-bma, r518-1 law; zero-gap relay after the W63
same-band yield to bm-c per r511 commit-order law -- my W63 freeze
unpushed, 2 divergent-B-seed shard replicas discarded, zero ledger
pollution). W63 bm-c r357 = ONE in-flight upstream seat at this
freeze (registered a9185ef96, burn pending on bm-c resident engine,
finalize not landed -> FAIL-CLOSED r307). W1..W62 finalizes ALL
LANDED (net chain head 500,948, K=134,320).

The W63 row's W64+ WARNING projects BOTH SIDES ARITHMETIC CLEAN:
A 171_004..173_003, B 49_401..49_600 -- bm-c r357 freeze gate
machine projection + this gate re-derives from the live registry,
never trusts the prose (r335 lesson + r535 law + r302 stale-pointer
law). Zero-skip wave (both sides arithmetic continuation).

Machine-verified against: all registered N1 wave bands W2..W63 (61
rows incl. W63 bm-c registered with finalize NOT landed = ONE
in-flight upstream seat -- coexist by band disjointness per r531
law), the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529
mandatory leg), the runner design-probe seed cluster 95_000..95_003
(r335 discovery leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points, N2-W15 draft probe points, lfc
actual draw and options_wave2 actual draw.

r566 bm-a freeze-window run (de-throttle order O-20261001-2355 sec.2).
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
W64_A = (171_004, 173_003)              # law sec.4 W64 row (arithmetic, no skip)
W64_B = (49_401, 49_600)                # law sec.4 W64 row (arithmetic, no skip)

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

# --- reserved universe (W64 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 64:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (61 pre-W64 rows + the candidate) -----------------
assert 63 in N1_BANDS and N1_BANDS[63]["engine_owner"] == "bm-c", \
    "leg0 failed: W63 (bm-c) row must be present (r357 freeze, in-flight seat)"
assert 62 in N1_BANDS and N1_BANDS[62]["engine_owner"] == "bm-a", \
    "leg0 failed: W62 (bm-a) row must be present (finalize landed c2d4fb7a9)"
assert 61 in N1_BANDS and N1_BANDS[61]["engine_owner"] == "bm-b", \
    "leg0 failed: W61 (bm-b) row must be present (finalize landed 2eb556a8f)"
assert 60 in N1_BANDS and N1_BANDS[60]["engine_owner"] == "bm-c", \
    "leg0 failed: W60 (bm-c) row must be present (finalize landed K=129,920)"
assert 57 in N1_BANDS and N1_BANDS[57]["engine_owner"] == "bm-a", \
    "leg0 failed: W57 (bm-a) row must be present (finalize landed K=123,320)"
pre_w64 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64]
assert sorted(N1_BANDS) == pre_w64, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 61 " \
    f"registered rows + the W64 candidate)"

# --- leg 0b: W63 row's W64+ WARNING prose present in the canon law file ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "171_004..173_003" in canon and "49_401..49_600" in canon, \
    "leg0b failed: W63 row W64+ WARNING (published projection) prose not " \
    "found in the canon file"
print("leg0b W63 row W64+ WARNING prose present (published projection basis; "
      "machine-derived per r535; bm-c r357 gate + this gate cross-checked)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) --------
ARITH_A = (N1_BANDS[63]["a"][1] + 1, N1_BANDS[63]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[63]["b_exit"][1] + 1,
           N1_BANDS[63]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W63 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W63 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [], \
    f"leg1-B failed: refusal facts drift {b_hits} (W63 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W63 row "
      f"projection verified machine-side)")

# --- leg 2: first clean window (both sides == arithmetic; zero-skip wave) ---
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
assert first_a == W64_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W64_A} " \
    "(no skip expected; R250/r518 machine-derived)"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W64_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W64_B} " \
    "(no skip expected; R250/r518 machine-derived)"
print("leg2 both sides: first clean window == arithmetic == candidate "
      "(zero-skip wave, both-sides arithmetic continuation)")
assert not overlaps(W64_A, W64_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W64_A), ("B", W64_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 64:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W64-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W64-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W64-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W64-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W64-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W64-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W64-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W64-{tag} (r335 leg)")
# canon cross-check: the landed W64 row must equal the derived candidate
assert N1_BANDS[64]["a"] == W64_A and N1_BANDS[64]["b_exit"] == W64_B, \
    "leg3 failed: canon W64 row drift vs derived candidate"
assert N1_BANDS[64]["engine_owner"] == "bm-a", "leg3 failed: W64 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "64: {\"a\": (171_004" not in out, \
    "leg3 failed: a W64 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W64 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W64 ADMIT: A {W64_A[0]}..{W64_A[1]} + B {W64_B[0]}..{W64_B[1]} both "
      f"ARITHMETIC CONTINUATION from the W63 tail (zero skip, both CLEAN "
      f"== the W63 row W64+ published projection verbatim, bm-c r357 gate "
      f"+ this gate cross-validated) clean vs 61 registered rows + N3-R1 "
      f"used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-a (first-free-number law under "
      f"O-20261001-2355 de-throttle sec.2; seat declared published=reserved "
      f"MSG-20261002-0851-bma; W63 bm-c = ONE in-flight upstream seat, "
      f"coexist per r531, finalize FAIL-CLOSED r307; origin slot vacancy "
      f"machine-checked).")

# --- W65+ projection (warning text for the law table row) --------------------
w65_a = (W64_A[1] + 1, W64_A[1] + WIDTH_A)
w65_b = (W64_B[1] + 1, W64_B[1] + WIDTH_B)
a_hits65 = sorted(p for p in points if w65_a[0] <= p <= w65_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w65_a)]
b_hits65 = sorted(p for p in points if w65_b[0] <= p <= w65_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w65_b)]
print(f"W65+ projection: A arithmetic +2_000 = {w65_a[0]}..{w65_a[1]} "
      f"-> {'CLEAN (verify at W65 prereg)' if not a_hits65 else 'REFUSED ' + str(a_hits65)}; "
      f"B +200 from W64 end = {w65_b[0]}..{w65_b[1]} "
      f"-> {'CLEAN (verify at W65 prereg)' if not b_hits65 else 'REFUSED ' + str(b_hits65)}")
