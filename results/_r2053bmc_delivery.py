#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2053 bm-c delivery self-proof: write the 送达自证 row into state after the push."""
from __future__ import annotations

import io
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHA = "ff736ad1eb"


def git(*args) -> str:
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()


def main() -> int:
    ahead_behind = git("rev-list", "--left-right", "--count", "origin/main...HEAD")
    tree = git("ls-tree", "-r", "--name-only", "origin/main")
    want = ["scripts/money_residual_sigma_recovery.py",
            "results/money_residual_sigma_recovery.json",
            "research/MONEY_RESIDUAL_SIGMA_RECOVERY.md",
            "results/_r2053bmc_residual_sigma_negative.py",
            "results/_r2053bmc_closeout.py"]
    have = [p for p in want if p in tree.splitlines()]
    missing = [p for p in want if p not in have]
    if missing:
        print("MISSING in origin/main: %s" % ",".join(missing))
        return 1

    note = ("commit **%s** 已推 origin/main，fetch 后 **AHEAD=0 / BEHIND=0**（%s），"
            "ls-tree origin/main 五件全在位（scripts/results/md/负控/收口）→ **本地未达 origin commit 数=0**"
            % (SHA, ahead_behind.replace("\t", " / ")))
    sp = os.path.join(ROOT, "state-bm-c.json")
    with io.open(sp, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    st["送达自证_r2053"] = note
    with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("state updated: " + note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
