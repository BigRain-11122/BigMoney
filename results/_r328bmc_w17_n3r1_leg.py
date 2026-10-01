"""W17 x N3-R1 supplementary scan-face leg (MSG-183x r529 bm-a mandate).

The freeze-time band gate (results/_r328bmc_w17_band_gate.py, ADMIT receipt
of the r328 bm-c freeze window) predates the N3-R1 x W13 overlap ruling --
this supplementary receipt carries the mandated N3 leg for the W17 wave:
the W17 in-use bands must clear the N3-R1 actual seed band 70_000..70_005
(seed = SEED_BASE + member index, six members, r509 bm-a freeze).

Single source: bands derive from perpetual_faces.N1_BANDS[17] (the live
law mirror), never hand-copied. Post-freeze table state is read-only here
(the freeze-time arithmetic-tail derivation legs are window-bound facts of
the original receipt and do not re-derive post-freeze -- the same script
re-run post-freeze fails its own leg2 guard BY DESIGN, fail-closed).
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS

N3_R1_ACTUAL = (70_000, 70_005)  # MSG-183x: six-member bootstrap CI face

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

w17 = N1_BANDS[17]
assert w17["a"] == (76_001, 78_000), f"W17 A band drift: {w17['a']}"
assert w17["b_exit"] == (38_100, 38_299), f"W17 B band drift: {w17['b_exit']}"
for tag, band in (("A", w17["a"]), ("B", w17["b_exit"])):
    assert not overlaps(band, N3_R1_ACTUAL), \
        f"W17 {tag} band {band} overlaps N3-R1 actual seeds {N3_R1_ACTUAL}"
    inter = set(range(band[0], band[1] + 1)) & set(range(N3_R1_ACTUAL[0], N3_R1_ACTUAL[1] + 1))
    assert not inter, f"W17 {tag} intersection nonempty: {sorted(inter)}"
print(f"W17 x N3-R1 leg ADMIT: W17 A {w17['a'][0]}..{w17['a'][1]} + "
      f"B {w17['b_exit'][0]}..{w17['b_exit'][1]} clear the N3-R1 actual "
      f"seed band {N3_R1_ACTUAL[0]}..{N3_R1_ACTUAL[1]} (MSG-183x mandate, "
      "r328 bm-c supplementary receipt).")
