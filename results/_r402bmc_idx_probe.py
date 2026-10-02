# -*- coding: utf-8 -*-
import subprocess
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
for p in ["CODELY.md", "research/pit-pool.md",
          "fleet/tasks/T-2026-10-02-147-P1.json",
          "round_reports-bm-c.md"]:
    idx = subprocess.check_output(
        ["git", "-C", ROOT, "show", ":" + p])
    print(f"{p}: index blob {len(idx)}B CRLF={idx.count(b'\r\n')} "
          f"LF={idx.count(chr(10).encode())}")
    wt = open(ROOT + "\\" + p.replace('/', '\\'), 'rb').read()
    print(f"    worktree {len(wt)}B CRLF={wt.count(b'\r\n')} "
          f"LF={wt.count(chr(10).encode())}")
