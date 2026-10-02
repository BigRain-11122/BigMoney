"""W64 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W64 = FIFTY-THIRD ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-b -- bm-b's TWENTIETH owned wave, machine-derived:
19 engine_owner==bm-b rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + SEAT DECLARED
published=reserved (MSG-20261002-0849-bmb, r518-1 law).

SEAT-COLLISION BAND AMENDMENT (honest disclosure): my seat MSG-0849
declared B-ext 49_301..49_500 on the basis of bm-a's MSG-0843
seat-declared W63 bands (B 49_101..49_300). The REGISTERED W63 row
landed as bm-c's freeze a9185ef96 (same-window seat collision:
bm-c's r357 engaged before seeing bm-a's declaration; r511
commit-order law -- the registered freeze is authoritative and
bm-a's in-flight W63 drafts yield pre-push). The registered W63
B-forced-skip window is 49_201..49_400 (window-advance scan
semantics, W26-A/W39-B/W43-B/W47-B/W51-B/W59-B skip family), so the
W64 arithmetic B position RE-DERIVES to 49_401..49_600 == the W63
row's published W64+ projection verbatim. My previously declared
49_301..49_500 is VOID (it would overlap the registered W63 B band
49_201..49_400) -- amendment carried by this freeze window's MSG
and canon row.

ZERO-GAP RELAY HOLD: this gate REFUSES to ADMIT while the W63 row
is not yet registered (exit 3 = hold state, not REFUSED) -- the W64
freeze may only land on a registered W63 tail so that no gap enters
the registry key space and no in-flight foreign gate leg0 is broken
by an unexpected extra key (r511 tail-lock + zero-gap relay).

With W63 registered (engine_owner=bm-c, bands A 169_004..171_003 /
B 49_201..49_400), this gate re-derives BOTH SIDES from the live
registry, never trusting the prose (r335 lesson + r535 law):
  A = 171_004..173_003 (W63 A end + 1, width 2_000, no skip)
  B = 49_401..49_600   (W63 B end + 1, width 200, no skip)

Machine-verified against: all registered N1 wave bands W2..W63,
the N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory
leg), the runner design-probe seed cluster 95_000..95_003 (r335
discovery leg), v1 in-use + W1 ext bands, SEED_REGISTRY live
values, N2/N4 design-probe points, N2-W15 draft probe points, lfc
actual draw and options_wave2 actual draw.

r565 bm-b freeze-window run (never-dry standing step, O-20261001-2355
sec.2 own-series; crashed-r564 recovery round).
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

# --- registered W63 row (bm-c r357 freeze a9185ef96, seat-collision winner) --
W63_REGISTERED_A = (169_004, 171_003)
W63_REGISTERED_B = (49_201, 49_400)

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

# --- leg 0-hold: zero-gap relay (W63 must be REGISTERED before ADMIT) --------
if 63 not in N1_BANDS:
    print("HOLD: W63 row not yet registered in the live registry "
          "(seat declared MSG-20261002-0843-bma, freeze in flight). W64 "
          "freeze is BLOCKED on the zero-gap relay: registry key space "
          "must stay gapless and no in-flight foreign gate leg0 may see "
          "an unexpected extra key. Exit 3 = hold state (not REFUSED). "
          "Seat reservation for W64 stands (MSG-20261002-0849-bmb, "
          "published=reserved).")
    sys.exit(3)

assert N1_BANDS[63]["a"] == W63_REGISTERED_A and \
    N1_BANDS[63]["b_exit"] == W63_REGISTERED_B and \
    N1_BANDS[63].get("engine_owner") == "bm-c", \
    "leg0 failed: registered W63 row != expected registered bands " \
    "(A 169_004..171_003 / B 49_201..49_400, bm-c a9185ef96) -- " \
    "derivation basis invalidated, RE-DERIVE the W64 candidates"

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

# --- leg 0: registry shape (61 pre-W64 registered rows + the candidate) ------
assert 62 in N1_BANDS and N1_BANDS[62]["engine_owner"] == "bm-a", \
    "leg0 failed: W62 (bm-a) row must be present (finalize landed " \
    "cross-machine bm-c r357 K=134,320 ledger head 500,948)"
assert 61 in N1_BANDS and N1_BANDS[61]["engine_owner"] == "bm-b", \
    "leg0 failed: W61 (bm-b) row must be present (freeze r564; " \
    "finalize landed bm-c r357 K=132,120)"
assert 60 in N1_BANDS and N1_BANDS[60]["engine_owner"] == "bm-c", \
    "leg0 failed: W60 (bm-c) row must be present (finalize landed " \
    "K=129,920)"
pre_w64 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64]
assert sorted(N1_BANDS) == pre_w64, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 61 " \
    f"registered rows + the W64 candidate)"

# --- leg 0b: W63 row's W64+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "171_004..173_003" in canon and "49_401..49_600" in canon, \
    "leg0b failed: W63 row W64+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W63 row W64+ WARNING prose present (published projection "
      "basis; machine-derived per r535; registered W63 bm-c row bands "
      "cross-checked verbatim")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
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

# --- leg 2: first clean windows (both sides == arithmetic, no skip) ----------
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
    "(no skip expected this wave; R250/r518 machine-derived)"
print(f"leg2 first clean windows == arithmetic positions both sides "
      f"(A {first_a[0]}..{first_a[1]} / B {first_b[0]}..{first_b[1]}, "
      f"no skip this wave)")
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
assert N1_BANDS[64]["engine_owner"] == "bm-b", "leg3 failed: W64 owner drift"
# freeze legality: slot vacancy verified against origin before landing
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8")
assert "64: {\"a\": (171_004" not in out, \
    "leg3 failed: a W64 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "63: {\"a\": (169_004" in out, \
    "leg3 failed: the registered W63 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

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
      f"ARITHMETIC CONTINUATION from the registered W63 tail (zero skip, "
      f"both CLEAN == the W63 row W64+ published projection verbatim, "
      f"bm-c r357 gate projection leg + this gate cross-validated) clean "
      f"vs 61 registered rows + N3-R1 used-seed band + probe-seed "
      f"cluster + registry values + probes/actuals -- engine_owner=bm-b "
      f"(first-free-number law under O-20261001-2355 de-throttle sec.2; "
      f"seat declared published=reserved MSG-20261002-0849-bmb with "
      f"B-band amendment to the registered W63 basis; W63 bm-c = ONE "
      f"in-flight upstream seat for the W64 finalize chain, coexist per "
      f"r531, finalize FAIL-CLOSED r307; origin slot vacancy "
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
