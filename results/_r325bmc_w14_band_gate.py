"""W14 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W14 = FIFTH ENGINE-OWNED WAVE and bm-c's FIRST owned engine wave, assigned
by the engine-wave sovereignty rotation law (r524 bm-a, F-20261001-01:
W13=bm-b [anchored] / W14=bm-c / W15=bm-a / W16=bm-b cycle). Freeze
trigger = never-dry supply law standing step + watermark red
runnable-work-idle-low-cpu (16:50 probe, py tail 0.1/1.1/0 -- engine
alive, queue 0, board clear). W13 finalize landed (bm-b r513, K=28,720,
ledger 395,348) -> rotation slot W14 is bm-c's to freeze + ignite.

The W13 row's W14+ WARNING projects BOTH arithmetic tails clean:
  A +2_000 tail (72_001..74_000, W13 A end + 1) and
  B +200 tail (29_500..29_699, W13 B end + 1).
This gate machine-verifies that projection against the FULL derived
reserved universe (no hardcoded snapshots, r511 law): N1_BANDS rows
W2..W13, v1 in-use + W1 ext bands, SEED_REGISTRY all int values,
N2/N4 design-probe points, lfc actual draw 30_000..30_099 AND
options_wave2 actual draw 63_000..63_049. If a tail is refused the
skip is FORCED (first clean window scan, W5/W8/W12/W13 family), never
a re-pick (R250); if clean the stride is kept verbatim.

r325 bm-c freeze-window run.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W13_A = N1_BANDS[13]["a"]                    # 70_001..72_000 (landed)
W13_B = N1_BANDS[13]["b_exit"]              # 29_300..29_499 (landed)
W14_A_ARITH = (W13_A[1] + 1, W13_A[1] + 2_000)   # 72_001..74_000 projected clean
W14_B = (W13_B[1] + 1, W13_B[1] + 200)           # 29_500..29_699 projected clean
LFC_ACTUAL = (30_000, 30_099)           # leg-3e family: actual draw ranges
OPTIONS_ACTUAL = (63_000, 63_049)        # options_wave2 K=50 (63_000+k, k<50)
N24_PROBE_POINTS = (40_000, 40_001)     # law sec.4 N2/N4 design-probe row
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH = 2_000

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

def clean(lo, width=WIDTH):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None
    for b in bands + actual:
        if overlaps((lo, hi), b):
            return None
    return (lo, hi)

# --- reserved universe (fully derived, no snapshots) ------------------------
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS)
bands = []
for cfg in N1_BANDS.values():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: arithmetic A tail check (ADMIT or FORCED skip) ------------------
arith_hits = sorted(p for p in points
                   if W14_A_ARITH[0] <= p <= W14_A_ARITH[1])
if arith_hits:
    print(f"leg1 arithmetic A tail {W14_A_ARITH[0]}..{W14_A_ARITH[1]}: "
          f"REFUSED (hits {arith_hits}) -> FORCED skip scan (W5/W8/W12/W13 family)")
    x = W14_A_ARITH[0]
    first = None
    while x < 20_260_000:
        r = clean(x)
        if r:
            first = r
            break
        x += 1
    assert first, "no clean 2,000-window found below 20260000"
    W14_A = first
    print(f"leg2 first clean {WIDTH}-wide window from {W14_A_ARITH[0]}: "
          f"{first[0]}..{first[1]}")
else:
    band_hit = [b for b in bands + actual if overlaps(b, W14_A_ARITH)]
    if band_hit:
        print(f"leg1 arithmetic A tail REFUSED (band overlap {band_hit}) -> "
              f"FORCED skip scan (W5/W8/W12/W13 family)")
        x = W14_A_ARITH[0]
        first = None
        while x < 20_260_000:
            r = clean(x)
            if r:
                first = r
                break
            x += 1
        assert first, "no clean 2,000-window found below 20260000"
        W14_A = first
        print(f"leg2 first clean {WIDTH}-wide window from {W14_A_ARITH[0]}: "
              f"{first[0]}..{first[1]}")
    else:
        W14_A = W14_A_ARITH
        print(f"leg1 arithmetic A tail {W14_A_ARITH[0]}..{W14_A_ARITH[1]}: "
              f"ADMIT (clean as the W13 row projected -- stride kept, NO skip)")

# --- leg 3: candidate ADMIT checks (both bands vs full universe) ------------
conflicts = []
for tag, band in (("A", W14_A), ("B", W14_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W14-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W14-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual {rng[0]}..{rng[1]} x W14-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W14-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} {r[0]}..{r[1]} x W14-{tag}")

print("N1_BANDS rows:", len(N1_BANDS), "| SEED_REGISTRY values:",
      len(science_gates.SEED_REGISTRY))
if conflicts:
    print("W14 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W14 ADMIT: A {W14_A[0]}..{W14_A[1]} + "
      f"B {W14_B[0]}..{W14_B[1]} both clean -- engine_owner=bm-c "
      f"(sovereignty rotation law, F-20261001-01: W14=bm-c slot).")
print("W15+ projection (W15=bm-a slot): A arithmetic +2_000 = "
      f"{W14_A[1] + 1}..{W14_A[1] + 2_000} (verify at W15 prereg); "
      f"B +200 = {W14_B[1] + 1}..{W14_B[1] + 200} (verify at W15 prereg).")
