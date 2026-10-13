# -*- coding: utf-8 -*-
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
b = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C",
                    r"K:\Fluxgroup\FluxGroup\quant\bigmoney", "show",
                    "a3a7aa632:research/PERPETUAL_N1_W232_PREREG.md"],
                   capture_output=True).stdout.decode("utf-8")
for x in ["r966 窗 13:2x", "二百二十九", "525_004..527_003", "525_004..525_203",
          "r966 窗", "2026-10-13 13:5x", "r966 窗实跑"]:
    print(b.count(x), "|", x)
