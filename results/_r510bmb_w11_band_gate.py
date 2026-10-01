"""W11 band disjoint machine-gate (law sec.4 tail law: verify before landing).

Checks W11 candidate bands (A 36_100..38_099 arithmetic = W10 A end + 1,
B 28_900..29_099 arithmetic = W10 B end + 1 -- per the W10 row's W11+
WARNING projection) against every reserved face: all N1 wave bands (law
mirror, currently W2..W10), v1 in-use, W1 ext, science_gates.SEED_REGISTRY
all values, and the lfc actual draw range. SECOND engine-owned wave
(T-2026-10-01-141 s1 lineage, engine_owner=bm-b).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W11_A = (36_100, 38_099)
W11_B = (28_900, 29_099)
LFC_ACTUAL = (30_000, 30_099)

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

conflicts = []
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        for tag, band in (("A", W11_A), ("B", W11_B)):
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W11-{tag}")

for k, v in science_gates.SEED_REGISTRY.items():
    if not isinstance(v, int):
        continue  # 'policy' prose key
    for tag, band in (("A", W11_A), ("B", W11_B)):
        if band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W11-{tag}")
# lfc actual draw range avoidance (W8 leg-3e family)
for tag, band in (("A", W11_A), ("B", W11_B)):
    if overlaps(LFC_ACTUAL, band):
        conflicts.append(f"lfc actual draw range 30_000..30_099 x W11-{tag}")

# W12+ projection (law tail law: pre-announce the next arithmetic tails):
# W12 A +2_000 = 38_100..40_099 contains the N2/N4 design-probe reserved
# points 40_000/40_001 (law sec.4 N2/N4 row) -- projected COLLISION, W12
# prereg must skip-position A per the r307/r309 law; W12 B +200 =
# 29_100..29_299 projects clean but still machine-verified at that time.
W12_A = (38_100, 40_099)
w12_hits = sorted(v for v in (40_000, 40_001)
                  if isinstance(v, int) and W12_A[0] <= v <= W12_A[1])

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
if conflicts:
    print("W11 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print("W11 ADMIT: A 36_100..38_099 + B 28_900..29_099 both clean "
      "(arithmetic tails land free, no skip needed -- matches the W10 "
      "row's projection; still machine-verified per law tail law).")
print("W12+ projection: A arithmetic 38_100..40_099 hits N2/N4 "
      f"design-probe points {w12_hits} -> W12 A skip forced (law sec.4 "
      "N2/N4 yield row); B 29_100..29_299 projects clean, verify at "
      "W12 prereg time.")
