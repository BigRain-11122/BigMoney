import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import mass_trial_w1 as mt

# find the p5c import members + _load_leg source
src = open(os.path.join(ROOT, "scripts", "mass_trial_w1.py"), encoding="utf-8").read()
for line in src.splitlines():
    if "p5c_virtual_timepoint import" in line or line.strip().startswith("from p5c"):
        print("IMPORT LINE:", line)
import inspect
print("has _load_leg:", hasattr(mt, "_load_leg"))
if hasattr(mt, "_load_leg"):
    print(inspect.getsource(mt._load_leg)[:800])

# leg-L index
raw, P, idx, listed, cen = mt._leg_raw("L")
print("leg-L idx len:", len(idx), "first:", idx[0], "last:", idx[-1])
print("census:", cen, "frozen:", mt.FROZEN_CENSUS["L"])
print("listed floor check ok, members:", len(raw))

# trial labor w1 curve machinery GRAMMAR dependency
import trial_labor_w1 as tl1
print("tl1 has GRAMMAR attr:", hasattr(tl1, "GRAMMAR"), type(getattr(tl1, "GRAMMAR", None)).__name__)
sig = inspect.signature(tl1.run_candidate_curve)
print("run_candidate_curve sig:", sig)
print("tl1.B_LAYER_MASK:", tl1.B_LAYER_MASK if hasattr(tl1, "B_LAYER_MASK") else "absent")
print("tl1 CUTOFF:", getattr(tl1, "CUTOFF", None))
import trial_labor_w2 as tl2
# _d6_admit_core source head for exact behavior
print(inspect.getsource(tl2._d6_admit_core)[:1500])
