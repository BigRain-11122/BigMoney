# -*- coding: utf-8 -*-
"""W75 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W75 = SIXTY-FOURTH ENGINE-OWNED WAVE candidate, bm-c's TWENTY-FOURTH owned
per machine-derive (engine_owner==bm-c rows 23 + candidate). Freeze authority
= never-dry supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series. W73 (bm-a r570) = table tail; W74 = seat
PUBLISHED=RESERVED to bm-b (heartbeat 2026-10-02T10:41:53 declared intent
"next bm-b wave W74"; r565 seat etiquette -- this machine yields the number
AND the seat's derived bands, zero touch).

Bands = FIRST-CLEAN WINDOW SKIPPING the W74 PUBLISHED-PROJECTION SEAT
(r518-1 yield-rebase precedent: the machine gate writes the published
projection band into the reserved universe and emits REFUSAL FACTS whose
identity IS the published seat). The W74 projection re-derived from the
registered W73 row (== the W73 canon row W74+ WARNING projection verbatim,
incl. its REFUSED face):
  A 191_004..193_003 = W73 A tail (191_003 + 1) + 2_000 width  -- CLEAN
  B  51_801..52_000  = W73 B tail (51_800 + 1) + 200 width
     REFUSED: SEED_REGISTRY xstock_synth_null_b = 52_000 sits at the
     window END -> W74 DERIVED window = 52_001..52_200 (single reading:
     hit+1 window == window-step window, both converge because the hit
     is the window's last element -- r566 W63 divergence analysis, the
     W73 row warning carries the same derivation).
  W75 candidates (published-projection seat tail + 1):
      A 193_004..195_003   B 52_201..52_400
Divergence disclosure: if bm-b registers W74 == the derived projection
=> bitwise zero overlap with W75; any other W74 band = abort face
(re-derive W75 before freeze, r566-3 law).

Two-state (r307 law): if W74 is ALREADY registered at gate time, its bands
must equal the derived projection (else ABORT -- re-derive W75 first).

Machine-verified against: all 71 registered N1 wave bands W2..W73, the W74
published-projection seat (arithmetic + derived windows, reserved), N3-R1
used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points, N2-W15
draft probe points, lfc actual draw, options_wave2 actual draw.

r363 bm-c freeze-window run. READ-ONLY against the 71-row table + origin
(candidate passed as parameter; local insertion happens in the freeze
edits tool with FIX-A/B/C hardening, MSG-0640 lineage).
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

# --- candidate (pre-insertion gate: parameter, not local row) ----------------
W75_A = (193_004, 195_003)              # W74 published-projection A tail + 1
W75_B = (52_201, 52_400)                # W74 DERIVED B window tail + 1

N3R1_USED = (70_000, 70_005)
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

# --- fresh tail check (r511 law: fetch before any freeze action) -------------
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))   # MSG-183x leg
points |= set(PROBE_SEEDS)                              # r335 discovery leg
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (71 registered rows, NO W75 locally yet) -----------
base_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 74))
expected_keys = base_rows + ([74] if 74 in N1_BANDS else [])
assert sorted(N1_BANDS) == expected_keys, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 71 registered rows W2..W73 (+74 two-state if bm-b landed))"
assert 73 in N1_BANDS and N1_BANDS[73]["engine_owner"] == "bm-a", \
    "leg0 failed: W73 (bm-a) table-tail row must be present (r570 freeze)"
assert 72 in N1_BANDS and N1_BANDS[72]["engine_owner"] == "bm-b", \
    "leg0 failed: W72 (bm-b) row must be present"
assert 71 in N1_BANDS and N1_BANDS[71]["engine_owner"] == "bm-c", \
    "leg0 failed: W71 (bm-c) row must be present (finalize landed r362)"
assert N1_BANDS[73]["a"] == (189_004, 191_003) and \
    N1_BANDS[73]["b_exit"] == (51_601, 51_800), \
    "leg0 failed: W73 band drift vs canon row"
assert N1_BANDS[72]["a"] == (187_004, 189_003) and \
    N1_BANDS[72]["b_exit"] == (51_401, 51_600), \
    "leg0 failed: W72 band drift vs canon row"
assert N1_BANDS[71]["a"] == (185_004, 187_003) and \
    N1_BANDS[71]["b_exit"] == (51_201, 51_400), \
    "leg0 failed: W71 band drift vs canon row"
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(bmc_rows) == 23, f"leg0 failed: bm-c rows {bmc_rows} (expect 23)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{max(N1_BANDS)} "
      f"({N1_BANDS[max(N1_BANDS)]['engine_owner']}), "
      "candidate W75 not local (pre-insertion gate), "
      f"bm-c rows={len(bmc_rows)}"
      + (" (+W74 registered two-state)" if 74 in N1_BANDS else ""))

# --- leg 0b: W73 row W74+ WARNING projection prose present in canon ----------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
assert "191_004..193_003" in canon, \
    "leg0b failed: W73 row W74+ A projection prose not found in canon"
assert "51_801..52_000" in canon, \
    "leg0b failed: W73 row W74+ B projection prose not found in canon"
assert "52_001..52_200" in canon, \
    "leg0b failed: W73 row W74+ derived-window prose not found in canon"
assert "xstock_synth_null_b" in canon, \
    "leg0b failed: W73 row refusal-identity prose not found in canon"
print("leg0b: W73 row W74+ WARNING prose present (A CLEAN / B REFUSED + "
      "derived window; this gate re-derives from the live registry, never "
      "trusts prose -- r335/r535/r302)")

# --- W74 published-projection seat (reserved universe, r518-1 law) ---------
PROJ74_A = (N1_BANDS[73]["a"][1] + 1, N1_BANDS[73]["a"][1] + WIDTH_A)
PROJ74_B_ARITH = (N1_BANDS[73]["b_exit"][1] + 1,
                  N1_BANDS[73]["b_exit"][1] + WIDTH_B)
assert PROJ74_A == (191_004, 193_003), f"projection drift: {PROJ74_A}"
assert PROJ74_B_ARITH == (51_801, 52_000), f"projection drift: {PROJ74_B_ARITH}"
# A side: projection window must be clean of everything EXCEPT the seat
# itself (with W74 registered == projection, the seat band IS the window
# -- excluded by identity, everything else must stay clear)
seat_a_band = tuple(N1_BANDS[74]["a"]) if 74 in N1_BANDS else PROJ74_A
a_seed_hits = sorted(p for p in points if PROJ74_A[0] <= p <= PROJ74_A[1])
a_other = [b for b in bands + actual
           if overlaps(b, PROJ74_A) and b != seat_a_band]
assert a_seed_hits == [] and a_other == [], \
    f"leg1-A failed: W74 A projection window not clean beyond the seat " \
    f"{a_seed_hits} {a_other}"
# B side: arithmetic window MACHINE-REFUSED by xstock_synth_null_b=52_000
b_arith_hits = sorted(p for p in points
                      if PROJ74_B_ARITH[0] <= p <= PROJ74_B_ARITH[1])
assert b_arith_hits == [52_000], \
    f"leg1-B failed: W74 B arithmetic refusal identity drifted: {b_arith_hits} " \
    f"(expect exactly [52000] = SEED_REGISTRY xstock_synth_null_b, the W73 " \
    f"row warning face)"
b_arith_other = [b for b in bands + actual if overlaps(b, PROJ74_B_ARITH)]
assert b_arith_other == [], \
    f"leg1-B failed: W74 B arithmetic window has band hits {b_arith_other}"
# W74 DERIVED B window (single reading, both converge -- hit = window
# end); with W74 registered, the seat band may BE this window (excluded
# by identity -- everything else must stay clear)
PROJ74_B = (52_000 + 1, 52_000 + WIDTH_B)
assert PROJ74_B == (52_001, 52_200), f"derived window drift: {PROJ74_B}"
seat_b_band = tuple(N1_BANDS[74]["b_exit"]) if 74 in N1_BANDS else PROJ74_B
b_seed_hits = sorted(p for p in points if PROJ74_B[0] <= p <= PROJ74_B[1])
b_other = [b for b in bands + actual
           if overlaps(b, PROJ74_B) and b != seat_b_band]
assert b_seed_hits == [] and b_other == [], \
    f"leg1-B failed: W74 DERIVED window not clean beyond the seat " \
    f"{b_seed_hits} {b_other}"
if 74 in N1_BANDS:
    assert tuple(N1_BANDS[74]["a"]) == PROJ74_A and \
        tuple(N1_BANDS[74]["b_exit"]) == PROJ74_B, \
        "leg0 failed: W74 registered DIVERGENT from the derived projection " \
        "-- ABORT, re-derive W75 bands before freeze (r566-3 law)"
    print("leg0b-2state: W74 already registered == derived projection "
          "(bands consistent, single reading preserved)")
print(f"leg1: W74 published-projection seat machine-derived: A "
      f"{PROJ74_A[0]}..{PROJ74_A[1]} CLEAN / B arithmetic "
      f"{PROJ74_B_ARITH[0]}..{PROJ74_B_ARITH[1]} REFUSED by "
      f"xstock_synth_null_b=52_000 (window-end point) -> W74 DERIVED B "
      f"{PROJ74_B[0]}..{PROJ74_B[1]} (single reading: hit+1 == window-step, "
      f"both converge -- W73 row warning carries the same derivation)")

# --- leg 2: first clean window (skip the reserved seat windows) --------------
def clean(lo, width, extra=()):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual + list(extra):
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

assert clean(PROJ74_A[0], WIDTH_A, extra=(PROJ74_A,)) is None and \
    clean(PROJ74_B_ARITH[0], WIDTH_B, extra=(PROJ74_B,)) is None and \
    clean(PROJ74_B[0], WIDTH_B, extra=(PROJ74_B,)) is None, \
    "leg2 failed: reserved W74 windows must be refused by the seat bands"
skip_a = (PROJ74_A[1] + 1, PROJ74_A[1] + WIDTH_A)
skip_b = (PROJ74_B[1] + 1, PROJ74_B[1] + WIDTH_B)
first_a = clean(skip_a[0], WIDTH_A)
first_b = clean(skip_b[0], WIDTH_B)
assert first_a == W75_A == skip_a, \
    f"leg2-A failed: first clean window {first_a} != candidate {W75_A}"
assert first_b == W75_B == skip_b, \
    f"leg2-B failed: first clean window {first_b} != candidate {W75_B}"
print(f"leg2: A first-clean == projection-tail continuation == candidate "
      f"{W75_A[0]}..{W75_A[1]}; B first-clean == derived-seat-tail "
      f"continuation == candidate {W75_B[0]}..{W75_B[1]} (seat-reservation "
      f"skip, single reading; if bm-b lands W74 == projection the overlap "
      f"with W75 is bitwise zero; any other W74 = abort/re-derive face)")
assert not overlaps(W75_A, W75_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W75_A), ("B", W75_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W75-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W75-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W75-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W75-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W75-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W75-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W75-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W75-{tag} (r335 leg)")
    for nm, r in (("W74-seat-A", PROJ74_A), ("W74-seat-B-arith", PROJ74_B_ARITH),
                  ("W74-seat-B-derived", PROJ74_B)):
        if overlaps(r, band):
            conflicts.append(f"{nm} {r[0]}..{r[1]} x W75-{tag} (seat overlap!)")
# origin slot vacancy (r511 tail-lock): no W75 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "75: {\"a\": (193_004" not in out, \
    "leg3 failed: a W75 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "N1 \u6ce275\uff08" not in out, "leg3 failed: canon W75 row exists on origin"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W75"' not in outn1, \
    "leg3 failed: a W75 WAVE_CONFIGS entry ALREADY exists on origin"
w74_on_origin = "74: {\"a\":" in out
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]} | W74 on origin: {w74_on_origin}")
if conflicts:
    print("W75 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W75 ADMIT: A {W75_A[0]}..{W75_A[1]} + B {W75_B[0]}..{W75_B[1]} "
      f"(first-clean window SKIPPING the W74 published-projection seat: A "
      f"projection 191_004..193_003 CLEAN + B arithmetic 51_801..52_000 "
      f"REFUSED [xstock_synth_null_b=52_000] -> derived 52_001..52_200, "
      f"single reading; r518-1 reservation law; refusal-facts identity = "
      f"the published seat) -- clean vs {len(N1_BANDS)} registered rows "
      f"+ N3-R1 used-"
      f"seed band + probe-seed cluster + registry values + probes/actuals -- "
      f"engine_owner=bm-c (first-free-number law under O-20261001-2355 "
      f"de-throttle sec.2 + r565 seat etiquette; origin slot vacancy "
      f"machine-checked; seat declaration published=reserved in this "
      f"window MSG-20261002-1105-bmc).")

# --- W76+ projection (warning text for the law table row) --------------------
w76_a = (W75_A[1] + 1, W75_A[1] + WIDTH_A)
w76_b = (W75_B[1] + 1, W75_B[1] + WIDTH_B)
a_hits76 = sorted(p for p in points if w76_a[0] <= p <= w76_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w76_a)]
b_hits76 = sorted(p for p in points if w76_b[0] <= p <= w76_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w76_b)]
print(f"W76+ projection: A arithmetic +2_000 = {w76_a[0]}..{w76_a[1]} "
      f"-> {'CLEAN (verify at W76 prereg)' if not a_hits76 else 'REFUSED ' + str(a_hits76)}; "
      f"B +200 from W75 end = {w76_b[0]}..{w76_b[1]} "
      f"-> {'CLEAN (verify at W76 prereg)' if not b_hits76 else 'REFUSED ' + str(b_hits76)}")
