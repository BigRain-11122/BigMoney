"""N4-B1 seed-band disjoint machine-scan (law sec.4 N2/N4 row: N4 allocates
from the 40_000+ domain, 40_000/40_001 design-probe reserved; r600 bm-a
DRAFT-stage evidence -- NOT a freeze, NOT a registration; band plan for the
N4-B1 prereg draft only).

Scan face: all N1 wave bands (perpetual_faces.N1_BANDS single-source),
science_gates.SEED_REGISTRY all int values, new_signal_p1/ce actual draw
ranges (40_000..40_099 family), N2/N4 design-probe reserved points
(40_000/40_001), N2-W15 frozen bands (31_000/31_500/32_000 width-499),
N3 70_000+ actual face (N3-R1 70_000..70_005) + probe-seed cluster
(95_000..95_003), lfc actual draw range (30_000..30_099).

跳位被迫性机证 (refusal-facts pattern, W7/W8 law precedent): the naive
40_000+ head proposal (gen 40_500..40_999 / scrnull 41_000..41_499 /
unc 41_500..41_999) is machine-REFUSED -- the N1 B-exit ladder has
already climbed INTO the 40_000+ domain (W28.b 40_451..40_650 through
W34.b 41_801..42_000, contiguous 200/wave arithmetic) and
SEED_REGISTRY[p4_batch1]=41_000 sits inside the scrnull window. A
second naive probe at the 50_500 head (B-ladder horizon math) is also
REFUSED -- the N1_BANDS table carries PROJECTED rungs (W68.b 50_501..
50_700 through W73.b 51_601..51_800) plus registry points
cta_p2_noau=50_500 / xstock_synth_null_a=51_000. Gap-finder over the
full merged occupancy (N1_BANDS 112 rows both ladders + 164 registry
values + all reserved faces) yields the FIRST contiguous >=1,499 clean
window above the 40_000 domain floor: **68_501..69_999** (between
registry point 68_500 and the N3 70_000+ domain):

  gen     68_501..68_999
  scrnull 69_000..69_499
  unc     69_500..69_999

B-ladder horizon (disclosed, not a gate): the last projected B rung /
registry cluster sits at <=68_500; reaching 69_000+ needs ~130+ more
waves; the N1-A ladder lives at 63_050+/70_001+ and does not return.
N3-R2 (bm-c, adjacent domain floor 70_000+) allocates upward from
70_000 -- zero overlap with this window. Future freezes scan both
directions (disjoint gate; first-freeze owns the window).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

NAIVE = [("gen", (40_500, 40_999)), ("scrnull", (41_000, 41_499)),
         ("unc", (41_500, 41_999))]
NAIVE2 = [("gen", (50_500, 50_999)), ("scrnull", (51_000, 51_499)),
          ("unc", (51_500, 51_999))]
N4_GEN = (68_501, 68_999)
N4_SCR = (69_000, 69_499)
N4_UNC = (69_500, 69_999)
PROBES = [40_000, 40_001]
NEW_SIGNAL_ACTUAL = (40_000, 40_099)   # new_signal_p1 40_000+k / ce 40_050+k
N2_W15_BANDS = [(31_000, 31_499), (31_500, 31_999), (32_000, 32_499)]
N3_ACTUAL = [(70_000, 70_005)]          # N3-R1 six-member bootstrap face
N3_PROBE_CLUSTER = (95_000, 95_003)     # r335 discovery-leg cluster
LFC_ACTUAL = (30_000, 30_099)

BANDS = [("gen", N4_GEN), ("scrnull", N4_SCR), ("unc", N4_UNC)]

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

def scan(bands):
    conflicts = []
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            for tag, band in bands:
                if overlaps((lo, hi), band):
                    conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x N4-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if not isinstance(v, int):
            continue
        for tag, band in bands:
            if band[0] <= v <= band[1]:
                conflicts.append(f"SEED_REGISTRY[{k}]={v} inside N4-{tag}")
    for p in PROBES:
        for tag, band in bands:
            if band[0] <= p <= band[1]:
                conflicts.append(f"N2/N4 design-probe {p} inside N4-{tag}")
    for lo, hi in N2_W15_BANDS + N3_ACTUAL:
        for tag, band in bands:
            if overlaps((lo, hi), band):
                conflicts.append(f"reserved band {lo}..{hi} x N4-{tag}")
    for lohi, name in ((NEW_SIGNAL_ACTUAL, "new_signal_p1 actual"),
                       (N3_PROBE_CLUSTER, "N3 probe cluster"),
                       (LFC_ACTUAL, "lfc actual")):
        for tag, band in bands:
            if overlaps(lohi, band):
                conflicts.append(f"{name} {lohi[0]}..{lohi[1]} x N4-{tag}")
    for tag, band in bands:
        if band[0] < 40_000:
            conflicts.append(f"N4-{tag} below 40_000 domain floor")
    return conflicts

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY int values:",
      sum(1 for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)))

# leg 1: naive 40_000+ head proposal must be REFUSED (forced-skip evidence)
naive_conflicts = scan(NAIVE)
assert naive_conflicts, "naive proposal unexpectedly clean -- refusal-facts leg broken"
print("leg1 naive 40_500/41_000/41_500 REFUSED (forced-skip facts):")
for c in naive_conflicts:
    print("  -", c)

# leg 1b: naive 50_500 probe must also be REFUSED (projection-face evidence)
naive2_conflicts = scan(NAIVE2)
assert naive2_conflicts, "naive-2 proposal unexpectedly clean -- refusal-facts leg broken"
print("leg1b naive 50_500/51_000/51_500 REFUSED (projected-rung facts):")
for c in naive2_conflicts:
    print("  -", c)

# leg 2: gap-finder-derived clean window must ADMIT
conflicts = scan(BANDS)
if conflicts:
    print("N4-B1 DRAFT BAND SCAN REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print("leg2 ADMIT: gen 68_501..68_999 + scrnull 69_000..69_499 + unc "
      "69_500..69_999 all clean vs N1_BANDS(112 rows, both ladders "
      "incl. projections) + SEED_REGISTRY(164) + new_signal actual + "
      "N2-W15 + N3(70_000+) + probes + lfc; first contiguous 1,499 "
      "clean window above the 40_000 N4 domain floor per gap-finder "
      "(draft evidence only -- freeze gate re-runs this scan at freeze "
      "time per R99/R250).")
