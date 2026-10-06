# -*- coding: utf-8 -*-
import io
src = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
A2 = ('"shard_subdir": "n1_w153", "out_name": "n1_w153_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n'
      '                       }')
A3 = ('    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face')
A4 = ('"results/_r766bma_w153_band_gate.json, law sec.4 W153 row, "\r\n'
      '          "r766 bm-a] "\r\n'
      '          "+ T-141 s2 "')
pf = io.open(r"scripts\perpetual_faces.py", encoding="utf-8", newline="").read()
A1 = ('    153: {"a": (351_404, 353_403), "b_exit": (353_404, 353_603),\r\n'
      '         "engine_owner": "bm-a"},\r\n}')
for tag, a in (("a1", A1), ("a2", A2), ("a3", A3), ("a4", A4)):
    print(tag, pf.count(a) if tag == "a1" else src.count(a))
