# -*- coding: utf-8 -*-
"""r794 bm-a: print the FULL K-lift/se_mu chain lines from both frozen preregs."""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for sha, name in (("18231a529", "PERPETUAL_N1_W163_PREREG.md"),
                   ("f7d34e5a7", "PERPETUAL_N1_W164_PREREG.md")):
    raw = subprocess.run(
        ["git", "show", f"{sha}:research/{name}"], capture_output=True).stdout
    txt = raw.decode("utf-8")
    print(f"===== {name} =====")
    for ln in txt.split("\n"):
        if "K-lift 线移动幅度" in ln:
            print(ln)
            print()
