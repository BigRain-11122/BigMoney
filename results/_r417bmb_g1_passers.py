# -*- coding: utf-8 -*-
"""r417 bm-b: G1 passer lists for W2/W3/W5 (read-only)."""
import json
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"E:\Fluxgroup\FluxGroup\quant\bigmoney\results"
for n in (2, 3, 5):
    j = json.load(io.open(os.path.join(R, f"trial_labor_w{n}", f"w{n}_judge.json"), encoding="utf-8"))
    passes = [c for c in j["cells"] if c.get("g1_pass")]
    print(f"== W{n} g1_pass={len(passes)}")
    for c in passes:
        print("  ", c.get("candidate_id"), "sharpe=", c.get("legL_sharpe_full"),
              "module=", c.get("module"), "fn=", c.get("fn"),
              "stop=", c.get("stop_face"), "gate=", c.get("gate_face"),
              "vol=", c.get("vol_face"), "yang=", c.get("yang_face"),
              "dsr=", (c.get("dsr") or {}).get("dsr"))
