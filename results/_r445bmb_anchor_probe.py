# -*- coding: utf-8 -*-
"""_r445bmb_anchor_probe.py -- W12 anchor pre-flight: dump the frozen
probe facts faces needed for the programmatic RSQR_ANCHOR build.
Read-only."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
pf = json.load(open("results/_r447bma_rsqr_w12_probe_facts.json",
                    encoding="utf-8"))
for k in ("cutoff", "rows", "first_date", "last_date",
          "rsqr20_decidable_days", "rsqr20_open_days",
          "rsqr20_open_rate_on_decidable", "rsqr10_decidable_days",
          "rsqr10_open_days", "rsqr10_open_rate_on_decidable",
          "nine_gate_512_cells_nonzero_count",
          "nine_gate_512_cells_empty_count",
          "nine_gate_512_cells_min_nonzero", "nine_gate_512_cells_max",
          "nine_gate_all_decidable_days"):
    print(k, "=", pf.get(k))
print("slope_split =", json.dumps(pf["rsqr20_open_slope_sign_split"]))
print("extreme_days =", json.dumps(pf["extreme_day_states"], indent=1))
adj = pf["adjacency"]
for k in ("rsqr20_vs_mad60", "rsqr20_vs_rsv60", "rsqr20_vs_downstreak",
          "rsqr20_vs_wide", "rsqr20_vs_mom", "rsqr20_vs_std20",
          "rsqr20_vs_std10", "rsqr10_vs_rsqr20", "rsqr20_vs_wild"):
    print("adj", k, "both_open =", adj[k]["both_open"],
          "a_only =", adj[k]["a_only_days"], "b_only =",
          adj[k]["b_open"] - adj[k]["both_open"])
cells = pf["nine_gate_cells"]
print("cells total", len(cells), "empty", sum(1 for v in cells.values() if v <= 0))
print("core48_rsqr20_open_rate =", json.dumps(pf["core48_rsqr20_open_rate"]))
print("grind =", json.dumps(pf["grind_face_forward_20d"]))
print("dir_split =", json.dumps(pf["direction_split_forward_20d"]))
