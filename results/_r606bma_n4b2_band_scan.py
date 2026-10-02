"""N4-B2 seed-band disjoint machine-scan (r606 bm-a DRAFT-stage evidence
for the B2 freeze gate condition 3; family-window re-proof + explicit
B2 consumption window 68_701..68_900).

Scan face (r600 script family, re-run at B2 freeze time per R99/R250 --
tables moved since the r602 B1 freeze): all N1 wave bands
(perpetual_faces.N1_BANDS single-source), science_gates.SEED_REGISTRY all
int values, new_signal_p1/ce actual draw ranges (40_000..40_099),
N2/N4 design-probe reserved points (40_000/40_001), N2-W15 frozen bands,
N3 70_000+ actual face + probe-seed cluster (95_000..95_003), lfc actual.

Legs:
  1. family window (gen 68_501..68_999 / scrnull 69_000..69_499 /
     unc 69_500..69_999) must ADMIT vs the CURRENT tables.
  2. B2 consumption window (gen 68_701..68_900) must ADMIT and must not
     overlap the B1 burned span 68_501..68_700 (K-bound arithmetic).
  3. family own base (perpetual_n4_b1=68_501) is the only allowed
     in-window registry hit.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

FAMILY = [("gen", (68_501, 68_999)), ("scrnull", (69_000, 69_499)),
          ("unc", (69_500, 69_999))]
B2_GEN = (68_701, 68_900)
B1_BURNED = (68_501, 68_700)
PROBES = [40_000, 40_001]
NEW_SIGNAL_ACTUAL = (40_000, 40_099)
N2_W15_BANDS = [(31_000, 31_499), (31_500, 31_999), (32_000, 32_499)]
N3_ACTUAL = [(70_000, 70_005)]
N3_PROBE_CLUSTER = (95_000, 95_003)
LFC_ACTUAL = (30_000, 30_099)


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


def scan(bands, own_base):
    conflicts = []
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            for tag, band in bands:
                if overlaps((lo, hi), band):
                    conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x {tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if not isinstance(v, int):
            continue
        for tag, band in bands:
            if band[0] <= v <= band[1] and v != own_base:
                conflicts.append(f"SEED_REGISTRY[{k}]={v} inside {tag} (own base exempt)")
    for p in PROBES:
        for tag, band in bands:
            if band[0] <= p <= band[1]:
                conflicts.append(f"design-probe {p} inside {tag}")
    for lo, hi in N2_W15_BANDS + N3_ACTUAL:
        for tag, band in bands:
            if overlaps((lo, hi), band):
                conflicts.append(f"reserved band {lo}..{hi} x {tag}")
    for lohi, name in ((NEW_SIGNAL_ACTUAL, "new_signal_p1 actual"),
                       (N3_PROBE_CLUSTER, "N3 probe cluster"),
                       (LFC_ACTUAL, "lfc actual")):
        for tag, band in bands:
            if overlaps(lohi, band):
                conflicts.append(f"{name} x {tag}")
    for tag, band in bands:
        if band[0] < 40_000:
            conflicts.append(f"{tag} below 40_000 domain floor")
    return conflicts


print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY int values:",
      sum(1 for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)))
own = science_gates.SEED_REGISTRY.get("perpetual_n4_b1")
assert own == 68_501, f"family base perpetual_n4_b1 must be 68_501, got {own}"

# leg 1: family window re-proof vs CURRENT tables
c1 = scan(FAMILY, own)
assert not c1, "family window no longer clean -- B2 freeze REFUSED:\n" + "\n".join(c1)
print("leg1 ADMIT: family window 68_501..69_999 (all three bands) clean vs "
      f"current tables (N1_BANDS {len(N1_BANDS)} rows + SEED_REGISTRY "
      f"{sum(1 for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int))} ints)")

# leg 2: B2 consumption window clean + disjoint from B1 burned span
c2 = scan([("b2_gen", B2_GEN)], own)
assert not c2, "B2 gen window refused:\n" + "\n".join(c2)
assert not overlaps(B2_GEN, B1_BURNED), "B2 window overlaps B1 burned span"
assert B2_GEN[1] <= 68_999, "B2 window must stay inside family gen band"
print(f"leg2 ADMIT: B2 gen {B2_GEN[0]}..{B2_GEN[1]} clean, disjoint from "
      f"B1 burned {B1_BURNED[0]}..{B1_BURNED[1]}, inside family band")

# leg 3: K-bound arithmetic (seed base + K - 1 == window top)
assert B2_GEN[0] + 200 - 1 == B2_GEN[1], "K=200 arithmetic mismatch"
print("leg3 ADMIT: K=200 arithmetic exact (68_701 + 199 == 68_900)")
print("N4-B2 BAND SCAN: ADMIT (family re-proof + B2 window + arithmetic)")
