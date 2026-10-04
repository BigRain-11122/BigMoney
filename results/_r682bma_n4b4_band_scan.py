# -*- coding: utf-8 -*-
"""r682 bm-a N4-B4 seed-band gap-finder scan (law sec.4 N2/N4 row: N4 allocates
from the 40_000+ domain; B4 = FIRST NEW FAMILY WINDOW after the B1-owned
window 68_501..69_999 is fully consumed by B1(200)+B2(200)+B3(99)=499 gen).

DRAFT-stage evidence -- NOT a freeze, NOT a registration; band plan for the
N4-B4 prereg draft only (R99/R250: freeze gate re-runs at freeze time).

Occupancy faces (merged, full universe):
  - all N1 wave bands (perpetual_faces.N1_BANDS single-source, 113 rows,
    both ladders incl. projected rungs)
  - science_gates.SEED_REGISTRY all int values (live read)
  - new_signal_p1/ce actual draws 40_000..40_099
  - N2-W15 frozen bands (31_000/31_500/32_000 width-499 trio) + probe points
  - N3 actuals: R1 70_000..70_005 + any registry-labeled N3 values
  - N3 probe cluster 95_000..95_003
  - lfc actual 30_000..30_099
  - options_wave2 actual 63_000..63_049
  - N4 family window 68_501..69_999 (B1-owned: gen 68_501..68_999 consumed
    B1-B3; scrnull 69_000..69_499 + unc 69_500..69_999 = family reserved
    control domain, B1 freeze comment law)
  - N2/N4 design-probe reserved points 40_000/40_001

Find: first contiguous >=1,499 clean window ABOVE the family window
(lo >= 70_000), mirror the B1 three-band family shape:
  gen <W>..<W+498> / scrnull <W+499>..<W+998> / unc <W+999>..<W+1497>
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

PROBES = [40_000, 40_001]
NEW_SIGNAL_ACTUAL = (40_000, 40_099)
N2_W15_BANDS = [(31_000, 31_499), (31_500, 31_999), (32_000, 32_499)]
N2_W15_PROBE_POINTS = [31_000, 31_500, 32_000]
N3_R1_ACTUAL = (70_000, 70_005)
N3_PROBE_CLUSTER = (95_000, 95_003)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N4_FAMILY_WINDOW = (68_501, 69_999)   # B1-owned (gen+scrnull+unc, incl. reserve)
DOMAIN_FLOOR = 40_000
WIDTH = 499                           # per-band family width (B1 shape)
FAMILY_TOTAL = 3 * WIDTH              # 1,497 contiguous values per family window

# --- occupancy assembly (points and bands kept distinct) ---------------------
points = set(PROBES) | set(N2_W15_PROBE_POINTS)
points |= {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(range(N3_R1_ACTUAL[0], N3_R1_ACTUAL[1] + 1))
points |= set(range(N3_PROBE_CLUSTER[0], N3_PROBE_CLUSTER[1] + 1))

bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += N2_W15_BANDS
bands += [NEW_SIGNAL_ACTUAL, LFC_ACTUAL, OPTIONS_ACTUAL, N4_FAMILY_WINDOW]

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")

# disclosure: registry-labeled occupancy at/above the family window tail
above = sorted(p for p in points if p >= 70_000)
print("registry/actual points >= 70_000 (disclosure):", above)
n1_above = sorted(b for b in bands if b[0] >= 69_000)
print("N1/reserved bands starting >= 69_000 (disclosure):", n1_above)


def clean(lo, hi):
    for p in points:
        if lo <= p <= hi:
            return f"point {p}"
    for b in bands:
        if not (hi < b[0] or b[1] < lo):
            return f"band {b}"
    return None


def gap_find(start_lo):
    """First contiguous FAMILY_TOTAL-wide clean window at/after start_lo."""
    lo = start_lo
    hops = 0
    while True:
        hit = clean(lo, lo + FAMILY_TOTAL - 1)
        if hit is None:
            return (lo, lo + FAMILY_TOTAL - 1), hops
        # advance past the hit (band -> band hi+1; point -> point+1)
        if hit.startswith("band"):
            b = eval(hit.split(" ", 1)[1])
            lo = b[1] + 1
        else:
            lo = int(hit.split(" ", 1)[1]) + 1
        hops += 1
        assert hops < 500, "gap-finder runaway"


# leg 1: refusal-facts at the family-window tail +1 (naive 70_000 proposal)
naive_hit = clean(70_000, 70_000 + FAMILY_TOTAL - 1)
assert naive_hit is not None, "naive 70_000 head unexpectedly clean"
print(f"leg1 naive 70_000 head REFUSED at {naive_hit} (forced-skip facts, N3-R1 domain)")

# leg 2: gap-finder above the family window
(win, hops) = gap_find(70_000)
gen = (win[0], win[0] + WIDTH - 1)
scr = (win[0] + WIDTH, win[0] + 2 * WIDTH - 1)
unc = (win[0] + 2 * WIDTH, win[1])
print(f"leg2 ADMIT-derive: family window {win[0]}..{win[1]} (hops={hops})")
print(f"  gen     {gen[0]}..{gen[1]}")
print(f"  scrnull {scr[0]}..{scr[1]}")
print(f"  unc     {unc[0]}..{unc[1]}")

# leg 3: verify each band clean vs the full merged occupancy (mirror B1 scan)
def scan_band(tag, band):
    conf = []
    if band[0] < DOMAIN_FLOOR:
        conf.append("below 40_000 domain floor")
    for p in points:
        if band[0] <= p <= band[1]:
            conf.append(f"point {p} inside {tag}")
    for b in bands:
        if not (band[1] < b[0] or b[1] < band[0]):
            conf.append(f"band {b} x {tag}")
    return conf

allconf = []
for tag, band in (("gen", gen), ("scrnull", scr), ("unc", unc)):
    allconf += scan_band(tag, band)
# family window disjointness vs the B1-owned window (first-freeze-owns law)
if not (win[1] < N4_FAMILY_WINDOW[0] or N4_FAMILY_WINDOW[1] < win[0]):
    allconf.append("B4 window overlaps the B1-owned family window")
if allconf:
    print("N4-B4 DRAFT BAND SCAN REFUSED:")
    for c in allconf:
        print("  -", c)
    sys.exit(1)
print("leg3 ADMIT: all three B4 bands clean vs N1_BANDS(113 rows both ladders "
      "incl. projections) + SEED_REGISTRY(live) + new_signal/lfc/options "
      "actuals + N2-W15 bands + N3-R1 domain + probe cluster + the B1-owned "
      "family window reserve -- first contiguous >=1,497 clean window above "
      "the B1 family window per gap-finder (draft evidence only -- freeze "
      "gate re-runs this scan at freeze time per R99/R250).")
