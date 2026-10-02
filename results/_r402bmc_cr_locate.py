# -*- coding: utf-8 -*-
import subprocess
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
for p in ["CODELY.md", "research/pit-pool.md"]:
    wt = open(ROOT + "\\" + p.replace('/', '\\'), 'rb').read()
    blob = subprocess.check_output(["git", "-C", ROOT, "show",
                                    "HEAD:" + p])
    for label, data in [("worktree", wt), ("HEAD-blob", blob)]:
        for i in range(len(data)):
            if data[i:i+1] == b"\r" and data[i+1:i+2] != b"\n":
                print(f"{p} {label}: lone CR at {i}: "
                      f"{data[max(0,i-50):i+50]!r}")
