# -*- coding: utf-8 -*-
"""W66 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W66 = FIFTY-FIFTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTY-FIRST owned wave, machine-derived:
20 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (MSG-20261002-0940-bmb, r518-1 law; zero-gap
relay one wave after the W64 same-band yield, W65 burned 12/12
local same-session chain-pending W64 finalize).

With W65 registered (engine_owner=bm-b, bands A 173_004..175_003 /
B 49_601..49_800) and W63 finalize LANDED (bm-c r358, K=136,520,
ledger head 503,148; W64 bm-a burn in flight 4/12+, W65 bm-b burned
12/12 local, finalize chain-pending FAIL-CLOSED r307), this gate
re-derives BOTH SIDES from the live registry, never trusting the
prose (r335 lesson + r535 law):
  A = 175_004..177_003 (W65 A end + 1, width 2_000, no skip, CLEAN)
  B = 50_001..50_200   (arithmetic 49_801..50_000 REFUSED at
      SEED_REGISTRY cta_p1=50_000 -> first clean window; single
      end-point hit so past-hit and window-stride readings COINCIDE
      -- no r566-bm-a skip-semantics divergence this wave)

Machine-verified against: all registered N1 wave bands W2..W65,
the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory
leg), the runner design-probe seed cluster 95_000..95_003 (r335
discovery leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points, N2-W15 draft probe points, lfc
actual draw and options_wave2 actual draw.

r567 bm-b freeze-window run (never-dry standing step,
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
W66_A = (175_004, 177_003)              # law sec.4 W66 row (arithmetic, no skip)
W66_B = (50_001, 50_200)                # law sec.4 W66 row (skip family, first clean)

# --- registered W65 row (bm-b r566 freeze, registered tail) -----------------
W65_REGISTERED_A = (173_004, 175_003)
W65_REGISTERED_B = (49_601, 49_800)

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

# --- leg 0-hold: zero-gap relay (W65 must be REGISTERED before ADMIT) -------
if 65 not in N1_BANDS:
    print("HOLD: W65 row not yet registered in the live registry. W66 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock). "
          "Seat reservation for W66 stands (MSG-20261002-0940-bmb, "
          "published=reserved).")
    sys.exit(3)

assert N1_BANDS[65]["a"] == W65_REGISTERED_A and \
    N1_BANDS[65]["b_exit"] == W65_REGISTERED_B and \
    N1_BANDS[65].get("engine_owner") == "bm-b", \
    "leg0 failed: registered W65 row != expected registered bands " \
    "(A 173_004..175_003 / B 49_601..49_800, bm-b r566 c97e04a49) -- " \
    "derivation basis invalidated, RE-DERIVE the W66 candidates"

# --- reserved universe (W66 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 66:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (64 pre-W66 registered rows + the candidate) -----
assert 64 in N1_BANDS and N1_BANDS[64]["engine_owner"] == "bm-a", \
    "leg0 failed: W64 (bm-a) row must be present (registered f41a9009d, " \
    "burn in flight -- finalize chain-pending FAIL-CLOSED r307)"
assert 65 in N1_BANDS and N1_BANDS[65]["engine_owner"] == "bm-b", \
    "leg0 failed: W65 (bm-b) row must be present (registered c97e04a49, " \
    "burned 12/12 local, finalize chain-pending FAIL-CLOSED r307)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w63_results.json")), \
    "leg0 failed: W63 finalize product missing (landed 4de45c3e0 -- " \
    "fetch/ff freshness; it stays the S5 anchor while W64/W65 finalizes " \
    "are in flight)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 21, \
    "leg0 failed: bm-b owned-row count != 21 (20 pre-candidate + the " \
    "landed W66 candidate -- machine-derive basis for the TWENTY-FIRST " \
    "owned wave claim)"
pre_w66 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66]
assert sorted(N1_BANDS) == pre_w66, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 64 " \
    f"registered rows + the W66 candidate)"

# --- leg 0b: W65 row's W66+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "175_004..177_003" in canon and "49_801..50_000 REFUSED" in canon \
    and "50_001..50_200" in canon, \
    "leg0b failed: W65 row W66+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W65 row W66+ WARNING prose present (published projection "
      "basis; machine-derived per r535; registered W65 bm-b row bands "
      "cross-checked verbatim)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[65]["a"][1] + 1, N1_BANDS[65]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[65]["b_exit"][1] + 1,
           N1_BANDS[65]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W65 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W65 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
# refusal fact MUST be the single SEED_REGISTRY point cta_p1=50_000 (window END)
assert b_hits == [50_000], \
    f"leg1-B failed: refusal facts drift {b_hits} (expected the single " \
    f"end-point hit [50000] = SEED_REGISTRY cta_p1 -- re-derive if drift)"
_cta = [k for k, v in science_gates.SEED_REGISTRY.items()
        if v == 50_000 and isinstance(v, int)]
assert _cta == ["cta_p1"], \
    f"leg1-B failed: the 50_000 registry key is {_cta} (expected cta_p1)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED at "
      f"SEED_REGISTRY cta_p1=50_000 (single end-point hit -- refusal "
      f"fact machine-proven; forced skip family)")

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
assert first_a == W66_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W66_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# B: walk past hits from the arithmetic start (past-hit reading; single
# end-point hit 50_000 makes past-hit == window-stride here -- both give
# 50_001..50_200, no r566-bm-a skip-semantics divergence this wave).
lo = ARITH_B[0]
first_b = None
while True:
    w = clean(lo, WIDTH_B)
    if w:
        first_b = w
        break
    hits = sorted(p for p in points if lo <= p <= lo + WIDTH_B - 1)
    assert hits, "leg2-B walk stall (no hits but window unclean -- band face?)"
    lo = max(hits) + 1
assert first_b == W66_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W66_B} " \
    "(forced skip past 50_000; R250/r518 machine-derived)"
assert W66_B[0] == 50_001 == 50_000 + 1 and W66_B[1] == 50_200, \
    "leg2-B failed: skip-window arithmetic (50_001..50_200) drift"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} == "
      f"arithmetic (no skip) / B {first_b[0]}..{first_b[1]} == first "
      f"clean past the 50_000 refusal (single end-point hit: past-hit "
      f"and window-stride readings COINCIDE -- skip family, no "
      f"semantics divergence)")
assert not overlaps(W66_A, W66_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W66_A), ("B", W66_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 66:
            continue
        for key in ("a", "b_exit"):
            lo2, hi2 = cfg[key]
            if overlaps((lo2, hi2), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo2}..{hi2} x W66-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W66-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W66-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W66-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W66-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W66-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W66-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W66-{tag} (r335 leg)")
# canon cross-check: the landed W66 row must equal the derived candidate
assert N1_BANDS[66]["a"] == W66_A and N1_BANDS[66]["b_exit"] == W66_B, \
    "leg3 failed: canon W66 row drift vs derived candidate"
assert N1_BANDS[66]["engine_owner"] == "bm-b", "leg3 failed: W66 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-b") == 21, \
    "leg3 failed: post-land bm-b owned rows must be exactly 21 (TWENTY-FIRST " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "66: {\"a\": (175_004" not in out, \
    "leg3 failed: a W66 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "65: {\"a\": (173_004" in out, \
    "leg3 failed: the registered W65 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W66 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W66 ADMIT: A {W66_A[0]}..{W66_A[1]} ARITHMETIC CONTINUATION from "
      f"the registered W65 tail (zero skip, CLEAN == the W65 row W66+ "
      f"published projection verbatim) + B {W66_B[0]}..{W66_B[1]} FORCED "
      f"SKIP past SEED_REGISTRY cta_p1=50_000 (arithmetic 49_801..50_000 "
      f"REFUSED; first clean window 50_001..50_200 machine-derived; single "
      f"end-point hit so past-hit == window-stride, no r566-bm-a semantics "
      f"divergence) -- clean vs 64 registered rows + N3-R1 used-seed band "
      f"+ probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-b (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2; seat declared published=reserved "
      f"MSG-20261002-0940-bmb; W64 bm-a + W65 bm-b = TWO in-flight "
      f"upstream seats for the W66 finalize chain, coexist per r531, "
      f"finalize FAIL-CLOSED r307; origin slot vacancy machine-checked).")

# --- W67+ projection (warning text for the law table row) --------------------
w67_a = (W66_A[1] + 1, W66_A[1] + WIDTH_A)
w67_b = (W66_B[1] + 1, W66_B[1] + WIDTH_B)
a_hits67 = sorted(p for p in points if w67_a[0] <= p <= w67_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w67_a)]
b_hits67 = sorted(p for p in points if w67_b[0] <= p <= w67_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w67_b)]
def _first_clean(lo, width):
    while True:
        w = clean(lo, width)
        if w:
            return w
        hits = sorted(p for p in points if lo <= p <= lo + width - 1)
        lo = max(hits) + 1
print(f"W67+ projection: A arithmetic +2_000 = {w67_a[0]}..{w67_a[1]} "
      f"-> {'CLEAN (verify at W67 prereg)' if not a_hits67 else 'REFUSED ' + str(a_hits67)}; "
      f"B +200 from W66 end = {w67_b[0]}..{w67_b[1]} "
      f"-> {'CLEAN (verify at W67 prereg)' if not b_hits67 else 'REFUSED ' + str(b_hits67) + ' -> first clean ' + str(_first_clean(w67_b[0], WIDTH_B))}")
