"""W12 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W12 = THIRD ENGINE-OWNED WAVE (engine_owner=bm-b, never-dry supply law
standing step, T-2026-10-01-141 s1 lineage).

A band forced-skip chain (machine-determined, NOT a free pick, R250):
  1. arithmetic +2_000 tail 38_100..40_099 (W11 A end + 1) REFUSED --
     contains the N2/N4 design-probe reserved points 40_000/40_001;
  2. first post-clush candidate 40_002..42_001 REFUSED -- contains
     registered values 40_050 (new_signal_p1_ce) and 41_000 (p4_batch1);
  3. the 41_000..43_000 gap holds only 1,999 free integers
     (41_001..42_999) -- one short of the 2,000-window requirement;
  4. the 40_000+ zone is the registered divergent seed space (values at
     ~every 500..2,000: 43_000/44_000/.../62_500/63_000) -- no 2,000
     free window exists until the 63_000..66_000 gap (2,999 free);
  5. ADMIT window = 63_001..65_000 (first free 2,000-window past all
     reserved faces, W5/W8 skip-over precedent family).
B band: 29_100..29_299 arithmetic (= W11 B end + 1), projected clean on
the registry face per the W11 row's W12+ WARNING -- machine-verified here.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

W12_A_ARITH = (38_100, 40_099)   # arithmetic tail -- REFUSED (probes)
W12_A_CAND1 = (40_002, 42_001)   # first post-clash candidate -- REFUSED (registry)
W12_A_SKIP  = (63_001, 65_000)   # first free 2,000-window past ALL reserved faces
W12_B       = (29_100, 29_299)   # arithmetic = W11 B end + 1
LFC_ACTUAL  = (30_000, 30_099)
PROBE_POINTS = (40_000, 40_001)  # N2/N4 design-probe reserved (law sec.4)

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

reg_vals = sorted(v for v in science_gates.SEED_REGISTRY.values()
                  if isinstance(v, int))

# ---- leg 1: REFUSED facts chain (forced-skip proof, R250) ----
hits_arith = sorted(p for p in PROBE_POINTS
                    if W12_A_ARITH[0] <= p <= W12_A_ARITH[1])
assert hits_arith == [40_000, 40_001], "arithmetic A tail must hit BOTH probes"
hits_cand1 = sorted(v for v in reg_vals
                    if W12_A_CAND1[0] <= v <= W12_A_CAND1[1])
assert hits_cand1 == [40_050, 41_000], "first post-clash candidate must hit registry"
print(f"REFUSED facts (forced-skip chain):")
print(f"  1. W12 A arithmetic 38_100..40_099 hits N2/N4 design-probe points "
      f"{hits_arith} (law sec.4 N2/N4 row).")
print(f"  2. first post-clash candidate 40_002..42_001 hits SEED_REGISTRY "
      f"{hits_cand1} (new_signal_p1_ce / p4_batch1).")
print(f"  3. gap 41_001..42_999 holds only 1,999 free integers -- one short "
      f"of the 2,000-window requirement (near-miss documented).")

# ---- leg 2: exhaustive first-free-window scan from W11 A end + 1 ----
reserved = set(reg_vals) | set(PROBE_POINTS)
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        reserved.update(range(lo, hi + 1))
# lfc actual draw range (W8 leg-3e family)
reserved.update(range(LFC_ACTUAL[0], LFC_ACTUAL[1] + 1))

start = W12_A_ARITH[0]
first_window = None
v = start
while v <= 63_001:  # scan bound: window known to exist starting at 63_001
    if v in reserved:
        v += 1
        continue
    # v is free: try to fit a 2,000-window starting at v
    if all((v + i) not in reserved for i in range(2_000)):
        first_window = (v, v + 1_999)
        break
    # else advance past this free run
    while v not in reserved:
        v += 1
assert first_window == (63_001, 65_000), \
    f"first free 2,000-window scan mismatch: {first_window}"
print(f"  4. exhaustive scan from 38_100 over registry+N1 bands+lfc+probes: "
      f"first free 2,000-window = {first_window[0]}..{first_window[1]} "
      f"(40_000+ registered divergent zone has no earlier fit).")

# ---- leg 3: ADMIT check for the skip A + arithmetic B ----
conflicts = []
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        for tag, band in (("A-skip", W12_A_SKIP), ("B", W12_B)):
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W12-{tag}")
for k, val in science_gates.SEED_REGISTRY.items():
    if not isinstance(val, int):
        continue
    for tag, band in (("A-skip", W12_A_SKIP), ("B", W12_B)):
        if band[0] <= val <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={val} inside W12-{tag}")
for p in PROBE_POINTS:
    for tag, band in (("A-skip", W12_A_SKIP), ("B", W12_B)):
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe point {p} inside W12-{tag}")
for tag, band in (("A-skip", W12_A_SKIP), ("B", W12_B)):
    if overlaps(LFC_ACTUAL, band):
        conflicts.append(f"lfc actual draw range 30_000..30_099 x W12-{tag}")

# window sizing sanity (law W2..W11 A=2,000 / B=200 precedent)
assert W12_A_SKIP[1] - W12_A_SKIP[0] + 1 == 2_000, "A window must be 2,000"
assert W12_B[1] - W12_B[0] + 1 == 200, "B window must be 200"
assert W12_A_SKIP[0] > W12_A_ARITH[1], "skip window must sit past the clash"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY values: "
      f"{len(science_gates.SEED_REGISTRY)}")
if conflicts:
    print("W12 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print("W12 ADMIT: A 63_001..65_000 (forced skip-over, first free window "
      "past ALL reserved faces) + B 29_100..29_299 (arithmetic) both clean.")

# ---- leg 4: W13+ projection (law tail law: pre-announce next tails) ----
W13_A = (W12_A_SKIP[1] + 1, W12_A_SKIP[1] + 2_000)   # 65_001..67_000
W13_B = (W12_B[1] + 1, W12_B[1] + 200)               # 29_300..29_499
w13_hits = []
for wname, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        if overlaps((lo, hi), W13_A):
            w13_hits.append(f"N1_BANDS W{wname}.{key} x W13-A")
        if overlaps((lo, hi), W13_B):
            w13_hits.append(f"N1_BANDS W{wname}.{key} x W13-B")
for k, val in science_gates.SEED_REGISTRY.items():
    if isinstance(val, int) and (W13_A[0] <= val <= W13_A[1]
                                or W13_B[0] <= val <= W13_B[1]):
        w13_hits.append(f"SEED_REGISTRY[{k}]={val} x W13")
for p in PROBE_POINTS:
    if W13_A[0] <= p <= W13_A[1] or W13_B[0] <= p <= W13_B[1]:
        w13_hits.append(f"probe {p} x W13")
w13_verdict = (f"HITS {sorted(set(w13_hits))} -> W13 A must skip-position "
               "per law (machine gate at W13 prereg time)"
               if w13_hits else
               "both project clean on the current face, machine-verify at "
               "W13 prereg time (registry face may have grown).")
print("W13+ projection: A +2_000 = 65_001..67_000 (W12 A end + 1), "
      f"B +200 = 29_300..29_499 -- {w13_verdict}")

"""YIELD ADDENDUM (r511 bm-b, post-freeze): this receipt documented the
bm-b draft-window ADMIT for A=63_001..65_000. bm-a r523 delivered the W12
freeze suite on origin FIRST (A=63_050..65_049, engine_owner=bm-a); per
r239 commit-order law bm-b yielded -- the frozen W12 law row is bm-a's,
and this window was never burned into any finalize. Kept as collision
evidence + exhaustive-scan pattern reference (the scan law itself stands).
"""
