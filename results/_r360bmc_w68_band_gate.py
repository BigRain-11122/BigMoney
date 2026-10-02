# -*- coding: utf-8 -*-
"""W68 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W68 = FIFTY-SEVENTH ENGINE-OWNED WAVE (T-2026-10-01-141 s1 lineage,
engine_owner=bm-c -- bm-c's TWENTY-SECOND owned wave, machine-derived:
21 engine_owner==bm-c rows + this candidate). FREEZE AUTHORITY =
never-dry supply law standing step + CEO DE-THROTTLE ORDER
O-20261001-2355 sec.2 own-continuous-series + FIRST-FREE-NUMBER law
(wave 68 = first free number over the registered W67 row; seat lock =
the freeze commit itself per r511 table-tail lock, cross-notified
same-window via MSG).

Context: W63 (bm-c r357) finalize LANDED (K=136,520, ledger head
503,148, bm-c r358). FOUR in-flight upstream seats disclosed: W64 bm-a
(burn in flight), W65 bm-b (burned 12/12), W66 bm-c (burned 12/12),
W67 bm-b (burn in flight) -- W68 finalize stays FAIL-CLOSED on all
four until they land (r307 two-state law).

Band derivation (r535 machine-gate derive law -- never prose
transcription, r335 lesson): BOTH SIDES re-derived from the live
registry:
  A = 179_004..181_003  (W67 A end 179_003 + 1, width 2_000, no skip
                         -- arithmetic window CLEAN)
  B = 50_601..50_800    (arithmetic window 50_401..50_600 REFUSED --
                         SEED_REGISTRY cta_p2_noau=50_500 MID-window
                         hit; forced skip per r307 W26 precedent
                         (refusal-facts machine-proof: the arithmetic
                         window MUST show red -- skip is forced, not a
                         free pick). First clean CHAINED window
                         50_601..50_800 per the W63 REGISTERED
                         in-canon face (r357 leg2-B chained window
                         stepping; r566 ruling family "the registered
                         face governs"). FORK DISCLOSURE: the restart
                         reading gives 50_501..50_700 == bm-b's
                         W67-row prose projection (self-tagged
                         "re-verify at W68 prereg"); NOT adopted; both
                         candidate windows are clean vs everything
                         (zero disjointness difference); escalated to
                         HQ-FEEDBACK for a pinned sec.4 semantics line.

Machine-verified against: all registered N1 wave bands W2..W67, the
N3-R1 USED-SEED BAND 70_000..70_005 (MSG-183x r529 mandatory leg),
the runner design-probe seed cluster 95_000..95_003 (r335 discovery
leg), v1 in-use + W1 ext bands, SEED_REGISTRY live values, N2/N4
design-probe points, N2-W15 draft probe points, lfc actual draw and
options_wave2 actual draw. Origin slot vacancy machine-checked
(ANY W68 row on origin = abort).

r360 bm-c freeze-window run (never-dry standing step, O-20261001-2355
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

NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# --- candidate (must equal the landed canon row -- cross-checked at leg3) ---
W68_A = (179_004, 181_003)              # law sec.4 W68 row (arithmetic, no skip)
W68_B = (50_601, 50_800)                # law sec.4 W68 row (forced-skip, chained)

# --- registered W67 row (bm-b r567 freeze, registered tail) ----------------
W67_REGISTERED_A = (177_004, 179_003)
W67_REGISTERED_B = (50_201, 50_400)

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

# --- leg 0-hold: zero-gap relay (W67 must be REGISTERED before ADMIT) -------
if 67 not in N1_BANDS:
    print("HOLD: W67 row not yet registered in the live registry. W68 "
          "freeze is BLOCKED on the zero-gap relay (r511 tail-lock).")
    sys.exit(3)

assert N1_BANDS[67]["a"] == W67_REGISTERED_A and \
    N1_BANDS[67]["b_exit"] == W67_REGISTERED_B and \
    N1_BANDS[67].get("engine_owner") == "bm-b", \
    "leg0 failed: registered W67 row != expected registered bands " \
    "(A 177_004..179_003 / B 50_201..50_400, bm-b r567) -- derivation " \
    "basis invalidated, RE-DERIVE the W68 candidates"

# --- reserved universe (W68 itself EXCLUDED -- it is the candidate) ----------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    if wnum == 68:
        continue
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (66 pre-W68 registered rows + the candidate) -----
assert 63 in N1_BANDS and N1_BANDS[63]["engine_owner"] == "bm-c", \
    "leg0 failed: W63 (bm-c) row must be present (finalize landed " \
    "bm-c r358 K=136,520 ledger head 503,148)"
assert 64 in N1_BANDS and N1_BANDS[64]["engine_owner"] == "bm-a", \
    "leg0 failed: W64 (bm-a) registered row must be present"
assert 65 in N1_BANDS and N1_BANDS[65]["engine_owner"] == "bm-b", \
    "leg0 failed: W65 (bm-b) registered row must be present"
assert 66 in N1_BANDS and N1_BANDS[66]["engine_owner"] == "bm-c", \
    "leg0 failed: W66 (bm-c) registered row must be present (r359 " \
    "landed, burned 12/12)"
assert 67 in N1_BANDS and N1_BANDS[67]["engine_owner"] == "bm-b", \
    "leg0 failed: W67 (bm-b) registered row must be present (r567 landed)"
assert os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w63_results.json")), \
    "leg0 failed: W63 finalize product missing (landed -- fetch/ff " \
    "freshness)"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-c") == 22, \
    "leg0 failed: bm-c owned-row count != 22 (21 pre-candidate + the " \
    "landed W68 candidate -- machine-derive basis for the TWENTY-SECOND " \
    "owned wave claim)"
pre_w68 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
           32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
           64, 65, 66, 67, 68]
assert sorted(N1_BANDS) == pre_w68, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} (the 66 " \
    f"registered rows + the W68 candidate)"

# --- leg 0b: W67 row's W68+ WARNING prose present in the canon law file -----
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "179_004..181_003" in canon and "50_401..50_600" in canon, \
    "leg0b failed: W67 row W68+ WARNING (published projections) prose " \
    "not found in the canon file"
print("leg0b W67 row W68+ WARNING prose present (published projection "
      "basis; machine-derived per r535; registered W67 bm-b row bands "
      "cross-checked verbatim)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) -------
ARITH_A = (N1_BANDS[67]["a"][1] + 1, N1_BANDS[67]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[67]["b_exit"][1] + 1,
           N1_BANDS[67]["b_exit"][1] + WIDTH_B)
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
assert a_hits == [], \
    f"leg1-A failed: refusal facts drift {a_hits} (W67 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN "
      f"(zero hits vs points/probes/N3-R1/registry -- no skip, W67 row "
      f"projection verified machine-side)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
assert b_hits == [50_500], \
    f"leg1-B failed: arithmetic window 50_401..50_600 must show the " \
    f"REFUSAL hit [50500] (SEED_REGISTRY cta_p2_noau) -- got {b_hits}. " \
    f"Skip legitimacy is machine-derived (r307 W26 precedent: forced, " \
    f"not free-pick); an empty hit list here = refusal-facts drift, RE-DERIVE"
assert b_hits[-1] != ARITH_B[1], \
    "leg1-B fork-classification failed: hit must be MID-window (50_500 != " \
    "window tail 50_600) -- the two skip readings DIVERGE here (r566 W63 " \
    "fork family); the chained reading (W63 registered face) governs"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED hit={b_hits} "
      f"(SEED_REGISTRY cta_p2_noau=50_500 -- MID-window hit, forced-skip "
      f"family machine-proof, skip is NOT a free pick; MID position = "
      f"fork face, W63 registered chained reading governs)")

# --- leg 2: first clean windows (A == arithmetic; B == chained stepping) ----
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
assert first_a == W68_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W68_A} " \
    "(no skip expected; R250/r518 machine-derived)"
# B side: forced skip -- CHAINED WHOLE-WINDOW STEPPING (the W63
# registered in-canon face, r357 leg2-B precedent; r566 ruling family:
# the registered face governs). The divergent restart-at-hit+1 reading
# is computed for disclosure and asserted NOT equal (fork proof).
b_lo = ARITH_B[0]
first_b = None
while first_b is None:
    w = clean(b_lo, WIDTH_B)
    if w is not None:
        first_b = w
        break
    b_lo += WIDTH_B                     # chained window step (整窗步进)
r_lo = ARITH_B[0]
restart_b = None
while restart_b is None:
    w = clean(r_lo, WIDTH_B)
    if w is not None:
        restart_b = w
        break
    hit = min(p for p in points if r_lo <= p <= r_lo + WIDTH_B - 1)
    r_lo = hit + 1                      # restart-at-hit+1 (divergent reading)
assert first_b == W68_B == (50_601, 50_800), \
    f"leg2-B failed: first clean CHAINED window {first_b} != candidate " \
    f"{W68_B} (chained window-step reading per the W63 registered face)"
assert restart_b != W68_B, \
    f"leg2-B fork disclosure failed: restart reading {restart_b} must be " \
    f"reported as divergent (it equals bm-b's W67-row prose projection " \
    f"50_501..50_700, which was NOT adopted per r335 machine-derive law)"
print(f"leg2 first clean windows: A {first_a[0]}..{first_a[1]} == "
      f"arithmetic (no skip) / B {first_b[0]}..{first_b[1]} == CHAINED "
      f"window step (W63 registered face); divergent restart reading "
      f"{restart_b[0]}..{restart_b[1]} disclosed NOT adopted (fork "
      f"escalated to HQ-FEEDBACK for a pinned sec.4 semantics line)")
assert not overlaps(W68_A, W68_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks (incl. MSG-183x N3-R1 leg) ----------------
conflicts = []
for tag, band in (("A", W68_A), ("B", W68_B)):
    for wname, cfg in N1_BANDS.items():
        if wname == 68:
            continue
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W68-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W68-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W68-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W68-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W68-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W68-{tag}")
    if overlaps(N3R1_USED, band) or any(
            band[0] <= v <= band[1] for v in range(N3R1_USED[0],
                                                    N3R1_USED[1] + 1)):
        conflicts.append(f"N3-R1 used-seed band {N3R1_USED[0]}..{N3R1_USED[1]} "
                        f"x W68-{tag} (MSG-183x mandatory leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W68-{tag} (r335 leg)")
# canon cross-check: the landed W68 row must equal the derived candidate
assert N1_BANDS[68]["a"] == W68_A and N1_BANDS[68]["b_exit"] == W68_B, \
    "leg3 failed: canon W68 row drift vs derived candidate"
assert N1_BANDS[68]["engine_owner"] == "bm-c", "leg3 failed: W68 owner drift"
assert sum(1 for c in N1_BANDS.values()
           if c.get("engine_owner") == "bm-c") == 22, \
    "leg3 failed: post-land bm-c owned rows must be exactly 22 (TWENTY-SECOND " \
    "owned wave claim derives machine-side)"
# freeze legality: slot vacancy verified against origin before landing
# (ANY W68 row on origin = seat collision, r511 tail-lock violation)
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    encoding="utf-8", creationflags=NO_WIN)
assert '68: {"a": (' not in out, \
    "leg3 failed: a W68 row ALREADY exists on origin (ANY-band check -- " \
    "seat collision, abort before push)"
assert "68: {\"a\": (179_004" not in out, \
    "leg3 failed: exact-band double-check (redundant guard)"
assert "67: {\"a\": (177_004" in out, \
    "leg3 failed: the registered W67 row not found on origin blob " \
    "(fetch freshness -- re-run after git fetch)"

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY), "| N3-R1 used band:",
      f"{N3R1_USED[0]}..{N3R1_USED[1]} (MSG-183x leg) | probe-seed cluster:",
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} (r335 discovery leg)")
if conflicts:
    print("W68 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W68 ADMIT: A {W68_A[0]}..{W68_A[1]} ARITHMETIC CONTINUATION from "
      f"the registered W67 tail (zero skip, CLEAN == the W67 row W68+ "
      f"published projection verbatim) + B {W68_B[0]}..{W68_B[1]} FORCED-SKIP "
      f"FAMILY (arithmetic 50_401..50_600 REFUSED by SEED_REGISTRY "
      f"cta_p2_noau=50_500 MID-window hit; first clean CHAINED window "
      f"50_601..50_800 per the W63 registered in-canon face; divergent "
      f"restart reading 50_501..50_700 disclosed NOT adopted, r335 "
      f"machine-derive law, fork escalated to HQ-FEEDBACK) clean vs 66 "
      f"registered rows + N3-R1 used-seed band + probe-seed cluster + "
      f"registry values + probes/actuals -- engine_owner=bm-c (first-free-"
      f"number law under O-20261001-2355 de-throttle sec.2; W64 bm-a + "
      f"W65 bm-b + W66 bm-c + W67 bm-b = FOUR in-flight upstream seats, "
      f"finalize FAIL-CLOSED r307; origin slot vacancy machine-checked "
      f"ANY-band).")

# --- W69+ projection (warning text for the law table row) --------------------
w69_a = (W68_A[1] + 1, W68_A[1] + WIDTH_A)
w69_b = (W68_B[1] + 1, W68_B[1] + WIDTH_B)
a_hits69 = sorted(p for p in points if w69_a[0] <= p <= w69_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w69_a)]
b_hits69 = sorted(p for p in points if w69_b[0] <= p <= w69_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w69_b)]
print(f"W69+ projection: A arithmetic +2_000 = {w69_a[0]}..{w69_a[1]} "
      f"-> {'CLEAN (verify at W69 prereg)' if not a_hits69 else 'REFUSED ' + str(a_hits69)}; "
      f"B +200 from W68 end = {w69_b[0]}..{w69_b[1]} "
      f"-> {'CLEAN (verify at W69 prereg)' if not b_hits69 else 'REFUSED ' + str(b_hits69)}")
if b_hits69 and isinstance(b_hits69[-1], int):
    tail = (b_hits69[-1] == w69_b[1])
    c_lo = w69_b[0]
    while clean(c_lo, WIDTH_B) is None:
        c_lo += WIDTH_B
    print(f"W69 B hit position: {'TAIL (both readings coincide)' if tail else 'MID (fork face)'}; "
          f"chained first clean window: {c_lo}..{c_lo + WIDTH_B - 1}")
