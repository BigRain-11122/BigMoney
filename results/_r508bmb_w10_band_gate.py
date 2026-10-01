"""W10 band disjoint machine-gate (law sec.4 tail law: verify before landing).

Checks W10 candidate bands (A 34_100..36_099 arithmetic, B 28_700..28_899
arithmetic -- per the W9 row's W10+ WARNING projection) against every
reserved face: all N1 wave bands (law mirror), v1 in-use, W1 ext,
science_gates.SEED_REGISTRY all values, and the lfc actual draw range.
First ENGINE-owned wave (T-2026-10-01-141 s1, engine_owner=bm-b).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W10_A = (34_100, 36_099)
W10_B = (28_700, 28_899)
LFC_ACTUAL = (30_000, 30_099)

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

conflicts = []
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        for tag, band in (("A", W10_A), ("B", W10_B)):
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W10-{tag}")

for k, v in science_gates.SEED_REGISTRY.items():
    if not isinstance(v, int):
        continue  # 'policy' prose key
    for tag, band in (("A", W10_A), ("B", W10_B)):
        if band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W10-{tag}")
# lfc actual draw range avoidance (W8 leg-3e family)
for tag, band in (("A", W10_A), ("B", W10_B)):
    if overlaps(LFC_ACTUAL, band):
        conflicts.append(f"lfc actual draw range 30_000..30_099 x W10-{tag}")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
if conflicts:
    print("W10 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print("W10 ADMIT: A 34_100..36_099 + B 28_700..28_899 both clean "
      "(arithmetic tails land free, no skip needed -- matches the W9 "
      "row's projection; still machine-verified per law tail law).")
