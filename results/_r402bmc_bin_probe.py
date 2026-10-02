# -*- coding: utf-8 -*-
import subprocess
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
for p in ["CODELY.md", "research/pit-pool.md",
          "fleet/tasks/T-2026-10-02-147-P1.json"]:
    wt = open(ROOT + "\\" + p.replace('/', '\\'), 'rb').read()
    nul = wt.count(b"\x00")
    lone_cr = len([i for i in range(len(wt))
                   if wt[i:i+1] == b"\r"
                   and wt[i+1:i+2] != b"\n"])
    head8k_nul = wt[:8000].count(b"\x00")
    print(f"{p}: NUL={nul} head8k_nul={head8k_nul} loneCR={lone_cr} "
          f"len={len(wt)}")
    idx = subprocess.check_output(["git", "-C", ROOT, "show", ":" + p])
    print(f"  index: len={len(idx)} CRLF={idx.count(b'\r\n')} "
          f"NUL={idx.count(b'\x00')} loneCR="
          f"{len([i for i in range(len(idx)) if idx[i:i+1]==b'\r' and idx[i+1:i+2]!=b'\n'])}")
