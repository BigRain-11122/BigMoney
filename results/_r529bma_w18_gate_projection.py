"""W18 band-gate PROJECTION self-check (bm-a r529 -- sequence-held prep,
NOT a freeze; rotation law "本波不属己=零冻结动作" holds until bm-c freezes
W17, so this receipt projects + pre-clears the W18 landing face only).

Rotation law F-20261001-01: W17=bm-c slot (unfrozen at receipt time --
observation note), W18=bm-a slot (mod-3 from anchor W13=bm-b).
W18 A projection = arithmetic +2_000 tail of W17's PROJECTED arithmetic A
(76_001..78_000, projected CLEAN by the W16 receipt's W17+ warning face)
=> 78_001..80_000. W18 B = INDETERMINATE until W17's B skip-over lands
(W17 B arithmetic 29_900..30_099 is REFUSED on the lfc actual flow) --
honest leg, no projection burned.

Scan face (law sec.4 norm + r529 canon amendment):
  all N1 bands W2..W16 (law mirror), v1 in-use + W1 ext bands,
  SEED_REGISTRY live values, N2/N4 design-probe points (40_000/40_001),
  N2-W15 draft probe points (31_000/31_500/32_000), lfc actual draw
  30_000..30_099, options_wave2 actual draw 63_000..63_049, AND the
  NEW N3-R1 seed-band leg (70_000..70_005 -- r529 disclosure row; every
  future N1/N2/N4 band gate must carry this leg), plus the conditional
  projected W17 A band (disclosed member).

r529 bm-a run. Zero network, read-only, deterministic.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W18_A_PROJ = (78_001, 80_000)          # IF W17 takes arithmetic A (76_001..78_000)
W17_A_PROJ = (76_001, 78_000)          # conditional face member (disclosed)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
N3_R1_SEEDS = (70_000, 70_005)         # r529 canon amendment leg (NEW)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH = 2_000

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3_R1_SEEDS[0], N3_R1_SEEDS[1] + 1))
bands = []
for cfg in N1_BANDS.values():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: W17 observation (sequence hold fact) ----------------------------
w17_frozen = 17 in N1_BANDS
print(f"leg1 W17 observation: frozen={w17_frozen} "
      f"(slot owner bm-c per rotation law; bm-a sequence-holds W18 -- "
      f"no freeze action this round, projection face only)")

# --- leg 2: W18 A projection vs the FULL face (incl. new N3 leg) -----------
conflicts = []
band = W18_A_PROJ
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        if overlaps((lo, hi), band):
            conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W18-A")
for k, v in science_gates.SEED_REGISTRY.items():
    if isinstance(v, int) and band[0] <= v <= band[1]:
        conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W18-A")
for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
    if overlaps(rng, band):
        conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W18-A")
for p in N24_PROBE_POINTS:
    if band[0] <= p <= band[1]:
        conflicts.append(f"N2/N4 probe point {p} inside W18-A")
for p in N2_W15_PROBE_POINTS:
    if band[0] <= p <= band[1]:
        conflicts.append(f"N2-W15 draft probe point {p} inside W18-A")
for v in range(N3_R1_SEEDS[0], N3_R1_SEEDS[1] + 1):
    if band[0] <= v <= band[1]:
        conflicts.append(f"N3-R1 seed {v} inside W18-A (r529 leg)")
for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
    for r in bb:
        if overlaps(r, band):
            conflicts.append(f"{nm} {r[0]}..{r[1]} x W18-A")
if overlaps(W17_A_PROJ, band):
    conflicts.append(f"projected W17 A {W17_A_PROJ} x W18-A")

# --- leg 3: W18 B honest INDETERMINATE note + W17 B skip-over helper ------
x = 29_900
first_b = None
while x < 20_260_000:
    hi = x + 199
    ok = not any(x <= p <= hi for p in points)
    ok = ok and not any(overlaps((x, hi), b) for b in bands + actual)
    if ok:
        first_b = (x, hi)
        break
    x += 1

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
print(f"leg2 W18 A projection {band[0]}..{band[1]} vs full face "
      f"(incl. N3-R1 seed leg + conditional W17-A): "
      f"{'CLEAN-PROJECTED' if not conflicts else 'DIRTY'}")
if conflicts:
    for c in conflicts:
        print("  -", c)
print(f"leg3 W18 B: INDETERMINATE until W17 B skip-over lands "
      f"(helper: first clean 200-window from W17 B arithmetic start "
      f"29_900 under the CURRENT face = {first_b} -- bm-c's W17 gate "
      f"re-derives at freeze time; W18 B = W17 B end + 1 when it lands)")
if conflicts:
    sys.exit(1)
print("verdict: W18-A PROJECTION CLEAN (conditional on W17 taking its "
      "projected arithmetic A; re-verify at W18 freeze time after the "
      "W17 row lands -- this receipt is prep, not a freeze).")
