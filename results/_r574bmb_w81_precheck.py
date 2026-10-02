# -*- coding: utf-8 -*-
"""r574 bm-b W81 band pre-check (seat-MSG accuracy, gate will re-derive)."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

assert N1_BANDS[80]["a"] == (203_004, 205_003) and N1_BANDS[80]["b_exit"] == (53_601, 53_800), \
    "W80 registered row drift vs bm-c freeze (A 203_004..205_003 / B 53_601..53_800)"
assert N1_BANDS[80]["engine_owner"] == "bm-c", "W80 owner drift"
print("W80 registered row verified (bm-c r364 freeze, origin-first)")

ARITH_A = (N1_BANDS[80]["a"][1] + 1, N1_BANDS[80]["a"][1] + 2000)
ARITH_B = (N1_BANDS[80]["b_exit"][1] + 1, N1_BANDS[80]["b_exit"][1] + 200)
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
a_hits = sorted(p for p in points if ARITH_A[0] <= p <= ARITH_A[1])
b_hits = sorted(p for p in points if ARITH_B[0] <= p <= ARITH_B[1])
print("W81 ARITH A %d..%d hits: %s" % (ARITH_A[0], ARITH_A[1], a_hits))
print("W81 ARITH B %d..%d hits: %s" % (ARITH_B[0], ARITH_B[1], b_hits))
print("SEED_REGISTRY key @54_000:", [k for k, v in science_gates.SEED_REGISTRY.items() if v == 54_000])
# past-hit restart window (W74-B upper-edge family)
RESTART_B = (54_001, 54_200)
rb_hits = sorted(p for p in points if RESTART_B[0] <= p <= RESTART_B[1])
print("W81 RESTART B 54_001..54_200 hits: %s" % (rb_hits,))
# full bands overlap check vs all registered waves
def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])
for w, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        if overlaps(tuple(cfg[key]), ARITH_A):
            print("A overlap with W%d.%s!" % (w, key))
        if overlaps(tuple(cfg[key]), RESTART_B):
            print("B-restart overlap with W%d.%s!" % (w, key))
print("bm-b owned rows now:", sum(1 for c in N1_BANDS.values() if c.get("engine_owner") == "bm-b"))
print("registry keys:", len(N1_BANDS), "| tail:", sorted(N1_BANDS)[-3:])
