import importlib.util
import json
import sys

import numpy as np

spec = importlib.util.spec_from_file_location("reh_fv", "scripts/fund_value_p1.py")
m = importlib.util.module_from_spec(spec)
sys.modules["reh_fv"] = m
spec.loader.exec_module(m)

m._init_worker()
m._firing_months()
lo = m._G["_t0_pos"]
hi = len(m._G["idx"]) - 1
print("t0_pos:", lo, "date:", m._G["idx"][lo])
u = m._month_universe(lo)
for k, v in u.items():
    if isinstance(v, (list, np.ndarray)):
        print(f"  {k}: len={len(v)}")
    else:
        print(f"  {k}: {v}")
# probe the firing-months structure
fm = m._G.get("_firing_months") or m._G.get("_firing")
if fm is not None:
    try:
        first = fm[0] if isinstance(fm, (list, tuple)) else list(fm)[0]
        print("first firing pos:", first, "date:", m._G["idx"][first])
    except Exception as e:
        print("firing introspect err:", e)
# scan: first pos (>=lo) where base_j non-empty
found = None
for pos in range(lo, min(lo + 400, hi)):
    u2 = m._month_universe(pos)
    if len(u2["base_j"]) > 0:
        found = pos
        break
print("first non-empty base_j at pos:", found,
      "date:", m._G["idx"][found] if found is not None else None)
if found is not None:
    u3 = m._month_universe(found)
    print("  base_j len:", len(u3["base_j"]))
