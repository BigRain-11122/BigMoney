"""r221 one-shot probe: production-form build_masks on real loaded panels
(close-only = the exact M_close shard input form that crashed at first fire).
No ICs, no batch work -- mask construction only. Deleted after use."""
import sys
sys.path.insert(0, "scripts")
import p1e_ic_batch as B

idx, syms, meta, panels = B.load_panels({"close"})
masks = B.build_masks(panels)
print("panel keys:", sorted(panels.keys()))
print("mask keys:", sorted(masks.keys()))
mc = masks["M_close"]
print("M_close cells:", int(mc.sum().sum()), "share:",
      round(int(mc.sum().sum()) / float(mc.size), 4))
assert set(masks.keys()) == {"M_close"}, masks.keys()
print("PROBE PASS: production-form build_masks OK")
