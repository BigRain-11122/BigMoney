"""W9 band disjoint machine-gate (law sec.4 tail law: verify before landing).

Checks W9 candidate bands (A 32_100..34_099 arithmetic, B 28_500..28_699
arithmetic -- per the W8 row's W9+ WARNING prediction) against every
reserved face: all N1 wave bands (law mirror), v1 in-use, W1 ext,
science_gates.SEED_REGISTRY all values, and the lfc actual draw range.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W9_A = (32_100, 34_099)
W9_B = (28_500, 28_699)
LFC_ACTUAL = (30_000, 30_099)

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

conflicts = []
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        for tag, band in (("A", W9_A), ("B", W9_B)):
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W9-{tag}")

for k, v in science_gates.SEED_REGISTRY.items():
    if not isinstance(v, int):
        continue  # 'policy' prose key
    for tag, band in (("A", W9_A), ("B", W9_B)):
        if band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W9-{tag}")
# lfc actual draw range avoidance (W8 leg-3e family)
for tag, band in (("A", W9_A), ("B", W9_B)):
    if overlaps(LFC_ACTUAL, band):
        conflicts.append(f"lfc actual draw range 30_000..30_099 x W9-{tag}")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
if conflicts:
    print("W9 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print("W9 ADMIT: A 32_100..34_099 + B 28_500..28_699 both clean "
      "(arithmetic tails land free, no skip needed -- matches the W8 "
      "row's prediction; still machine-verified per law tail law).")
