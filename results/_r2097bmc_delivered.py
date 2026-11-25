#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2097 (bm-c) delivery note append."""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-25T19:2x+08:00 | r2097-delivered | bm-c | 送达补记：commit **ff75b4c604** 已直推 origin/main"
    "（acf194c29e..ff75b4c604，无 non-FF）；fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0/0**；"
    "`git ls-tree --name-only origin/main` 五件全在位（scripts/idx_fut_carry_decision_face.py、"
    "results/idx_fut_carry_decision_face.json、research/IDX_FUT_CARRY_DECISION_FACE.md、qa/decision-face-r2097.md、"
    "results/_r2097bmc_decision_face_negative.py）→ **本地未达 origin commit 数=0**。"
    "提交前的两处自捕：①心跳被 pre-commit 爪拦下（GPU 面自相矛盾，19 个 free 键差 921.6 MiB = r1413 族）→ "
    "`python Tools/gpu_face.py apply` 单探针重述 33 键、`audit` 返回 []，重 stage 后过闸（禁 --no-verify 的正确解法）；"
    "②两枚 `results/_r2097bmc_*` 被 .gitignore 规则 `_r[0-9]*` 忽略，按前轮同族先例 `git add -f` 入库。"
    "S6 链本窗**未跑**：驱动件 Tools/s6_chain_bmc.py 是对端未提交脏面，跑了产出也无法归属（列入下轮待办）。"
    "| 记账：本行 1 处（累计 4）"
)


def main():
    text = io.open(PATH, encoding="utf-8", newline="").read()
    if "| r2097-delivered |" in text:
        print("already appended")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    io.open(PATH, "w", encoding="utf-8", newline="").write(text + LINE + "\n")
    print("appended %d chars" % len(LINE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
