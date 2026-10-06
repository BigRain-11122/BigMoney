# -*- coding: utf-8 -*-
"""r764 bm-a W152 freeze-anchor uniqueness pre-check (read-only)."""
import io

n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()

anchors_n1 = {
    "mat-leg (finally+T141)": '    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face',
    "w151-config-tail": '"shard_subdir": "n1_w151", "out_name": "n1_w151_results.json",\r\n                            "engine_owner": "bm-a"},\r\n                       }',
    "w151-snippet-tail": '"results/_r763bma_w151_band_gate.py, law sec.4 W151 row, "\r\n          "r763 bm-a] "\r\n          "+ T-141 s2 "',
}
for k, v in anchors_n1.items():
    print(n1.count(v), "|", k)

print(pf.count('151: {"a": (347_004, 349_003), "b_exit": (349_004, 349_203),\r\n         "engine_owner": "bm-a"},\r\n}'), "| pf w151-row+closing anchor")
