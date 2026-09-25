# -*- coding: utf-8 -*-
"""r225 (bm-b) one-shot probe: production-form build_masks on real panels for
the M_arc class (close+tr+vwap = the exact MARC shard input form).
Mirrors _r224_mask_probe.py precedent (per-class load-form pairing leg,
r221 law). No ICs, no batch work -- mask construction only."""
import json
import sys

sys.path.insert(0, "scripts")
import p1e_ic_batch as B

idx, syms, meta, panels = B.load_panels({"close", "tr", "vwap"})
masks = B.build_masks(panels)
print("panel keys:", sorted(panels.keys()))
print("mask keys:", sorted(masks.keys()))
ma = masks["M_arc"]
cells = int(ma.sum().sum())
share = round(cells / float(ma.size), 4)
print("M_arc cells:", cells, "share:", share)

art = json.load(open("results/shortline/p1e_nulls_M_arc.json",
                     encoding="utf-8"))
print("artifact mask_cells:", art["mask_cells"],
      "mask_cell_share:", art["mask_cell_share"])
assert cells == art["mask_cells"], \
    f"BIT-MISMATCH: probe {cells} vs artifact {art['mask_cells']}"
assert abs(share - art["mask_cell_share"]) < 5e-4
assert set(masks.keys()) == {"M_close", "M_close_tr", "M_arc"}, masks.keys()
print("PROBE PASS: M_arc mask bit-match + per-class load-form pairing OK")
