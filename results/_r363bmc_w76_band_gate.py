# -*- coding: utf-8 -*-
"""W76 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W76 = SIXTY-FIFTH ENGINE-OWNED WAVE candidate, bm-c's TWENTY-FOURTH owned
per machine-derive (engine_owner==bm-c rows 23 + candidate). Freeze authority
= never-dry supply law standing step + CEO DE-THROTTLE ORDER O-20261001-2355
sec.2 own-continuous-series + r565 yield-then-reoccupy law: this machine's
W75 draft (bands A 193_004..195_003 / B 52_201..52_400, gate ADMIT
results/_r363bmc_w75_band_gate.py) was yielded to bm-a r571 (commit 695312330
first-land per r511 commit-order; zero ignition zero push on this side =
zero-cost yield; the registered W75 bands are BITWISE-IDENTICAL to this
machine's gate-derived candidates = r530 family 10th deterministic
cross-validation). W76 = re-occupation in the yield-receipt window.

Bands = BOTH SIDES ARITHMETIC CONTINUATION from the registered W75 tail,
zero skip (r535 law):
  A 195_004..197_003 = W75 A tail (195_003 + 1) + 2_000 width
  B  52_401..52_600  = W75 B tail (52_400 + 1) + 200 width
Single reading (clean arithmetic windows, no refusal points -- verify
machine-side; the W75 canon row's W76+ WARNING projection, if carried,
must agree).

Machine-verified against: all 73 registered N1 wave bands W2..W75, N3-R1
used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), runner
design-probe seed cluster 95_000..95_003 (r335 discovery leg), v1 in-use +
W1 ext bands, SEED_REGISTRY live values, N2/N4 design-probe points, N2-W15
draft probe points, lfc actual draw, options_wave2 actual draw.

r363 bm-c freeze-window run (yield-then-reoccupy). READ-ONLY against the
73-row table + origin (candidate passed as parameter; local insertion
happens in the freeze edits tool with FIX-A/B/C hardening, MSG-0640 lineage).
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
W76_A = (195_004, 197_003)              # arithmetic continuation, W75 A tail +1
W76_B = (52_401, 52_600)                # arithmetic continuation, W75 B tail +1

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

# --- leg 0: registry shape (73 registered rows, NO W76 locally yet) -----------
base_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 76))
assert sorted(N1_BANDS) == base_rows, \
    f"leg0 failed: unexpected registry keys {sorted(N1_BANDS)} " \
    f"(expect the 73 registered rows W2..W14, W16..W75)"
assert 75 in N1_BANDS and N1_BANDS[75]["engine_owner"] == "bm-a", \
    "leg0 failed: W75 (bm-a r571) table-tail row must be present"
assert 74 in N1_BANDS and N1_BANDS[74]["engine_owner"] == "bm-b", \
    "leg0 failed: W74 (bm-b r571) row must be present"
assert N1_BANDS[75]["a"] == (193_004, 195_003) and \
    N1_BANDS[75]["b_exit"] == (52_201, 52_400), \
    "leg0 failed: W75 band drift vs canon row (bm-a r571 -- must equal this " \
    "machine's yielded draft bands bitwise, r530 family)"
assert N1_BANDS[74]["a"] == (191_004, 193_003) and \
    N1_BANDS[74]["b_exit"] == (52_001, 52_200), \
    "leg0 failed: W74 band drift vs canon row"
assert N1_BANDS[71]["a"] == (185_004, 187_003) and \
    N1_BANDS[71]["b_exit"] == (51_201, 51_400), \
    "leg0 failed: W71 band drift vs canon row"
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(bmc_rows) == 23, f"leg0 failed: bm-c rows {bmc_rows} (expect 23)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W75 bm-a (r571; bands "
      "bitwise == this machine's yielded W75 draft -- r530 family 10th "
      f"cross-validation), candidate W76 not local, bm-c rows={len(bmc_rows)}")

# --- leg 0b: W75 row W76+ WARNING projection prose (soft, W71 precedent) ------
canon = open(os.path.join(ROOT, "research", "PERPETUAL_FACES.md"),
             encoding="utf-8").read()
proj_a_in_canon = "195_004..197_003" in canon
proj_b_in_canon = "52_401..52_600" in canon
print(f"leg0b: W75 row W76+ projection prose present: A={proj_a_in_canon} "
      f"B={proj_b_in_canon} (soft check, W71 precedent -- this gate "
      "re-derives from the live registry, never trusts prose "
      "-- r335/r535/r302)")

# --- leg 1: arithmetic position DERIVED FROM THE REGISTRY (not prose) ---------
ARITH_A = (N1_BANDS[75]["a"][1] + 1, N1_BANDS[75]["a"][1] + WIDTH_A)
ARITH_B = (N1_BANDS[75]["b_exit"][1] + 1,
           N1_BANDS[75]["b_exit"][1] + WIDTH_B)
assert ARITH_A == (195_004, 197_003), f"leg1 drift: {ARITH_A}"
assert ARITH_B == (52_401, 52_600), f"leg1 drift: {ARITH_B}"
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
a_band_hits = [b for b in bands + actual if overlaps(b, ARITH_A)]
assert a_hits == [] and a_band_hits == [], \
    f"leg1-A failed: refusal facts {a_hits} {a_band_hits} (W75 row projected CLEAN)"
print(f"leg1-A arithmetic {ARITH_A[0]}..{ARITH_A[1]} CLEAN (zero hits -- no skip)")
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
b_band_hits = [b for b in bands + actual if overlaps(b, ARITH_B)]
assert b_hits == [] and b_band_hits == [], \
    f"leg1-B failed: refusal facts {b_hits} {b_band_hits} (W75 row projected CLEAN)"
print(f"leg1-B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN (zero hits -- no skip)")

# --- leg 2: first clean window -----------------------------------------------
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
assert first_a == W76_A == ARITH_A, \
    f"leg2-A failed: first clean window {first_a} != candidate {W76_A}"
first_b = clean(ARITH_B[0], WIDTH_B)
assert first_b == W76_B == ARITH_B, \
    f"leg2-B failed: first clean window {first_b} != candidate {W76_B}"
print(f"leg2: A first-clean == arithmetic == candidate {W76_A[0]}..{W76_A[1]}; "
      f"B first-clean == arithmetic == candidate {W76_B[0]}..{W76_B[1]} "
      f"(BOTH SIDES ARITHMETIC CONTINUATION, zero skip, single reading)")
assert not overlaps(W76_A, W76_B), "A/B overlap"

# --- leg 3: candidate ADMIT checks + origin vacancy --------------------------
conflicts = []
for tag, band in (("A", W76_A), ("B", W76_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W76-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W76-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W76-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W76-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 draft probe point {p} inside W76-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W76-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W76-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W76-{tag} (r335 leg)")
# origin slot vacancy (r511 tail-lock): no W76 row may exist on origin
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "76: {\"a\": (195_004" not in out, \
    "leg3 failed: a W76 row ALREADY exists on origin (slot not vacant -- " \
    "r511 tail-lock violation OR seat-declaration collision, abort before push)"
assert "N1 \u6ce276\uff08" not in out, "leg3 failed: canon W76 row exists on origin"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W76"' not in outn1, \
    "leg3 failed: a W76 WAVE_CONFIGS entry ALREADY exists on origin"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W76 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W76 ADMIT: A {W76_A[0]}..{W76_A[1]} + B {W76_B[0]}..{W76_B[1]} "
      f"(BOTH SIDES ARITHMETIC CONTINUATION from the registered W75 tail, "
      f"zero skip, single reading) -- clean vs 73 registered rows + N3-R1 "
      f"used-seed band + probe-seed cluster + registry values + "
      f"probes/actuals -- engine_owner=bm-c (r565 yield-then-reoccupy after "
      f"the W75 zero-cost yield to bm-a r571 695312330 per r511 "
      f"commit-order; seat published=reserved in this window "
      f"MSG-20261002-1145-bmc).")

# --- W77+ projection (warning text for the law table row) --------------------
w77_a = (W76_A[1] + 1, W76_A[1] + WIDTH_A)
w77_b = (W76_B[1] + 1, W76_B[1] + WIDTH_B)
a_hits77 = sorted(p for p in points if w77_a[0] <= p <= w77_a[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w77_a)]
b_hits77 = sorted(p for p in points if w77_b[0] <= p <= w77_b[1]) or [
    f"band {b}" for b in bands + actual if overlaps(b, w77_b)]
print(f"W77+ projection: A arithmetic +2_000 = {w77_a[0]}..{w77_a[1]} "
      f"-> {'CLEAN (verify at W77 prereg)' if not a_hits77 else 'REFUSED ' + str(a_hits77)}; "
      f"B +200 from W76 end = {w77_b[0]}..{w77_b[1]} "
      f"-> {'CLEAN (verify at W77 prereg)' if not b_hits77 else 'REFUSED ' + str(b_hits77)}")
