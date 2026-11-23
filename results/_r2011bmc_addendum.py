#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r2011 bm-c addendum: delivery receipt + the two S7 facts found this round."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINE = (
    "| 2026-11-23 23:1x | r2011 **addendum**（送达核验） | commit **3fe5fe0a63** 已推 origin/main "
    "（b6bca64677..3fe5fe0a63），fetch 后 **AHEAD=0 / BEHIND=0**，`git ls-tree -r origin/main` 九件 blob 在位"
    "（scripts/astock_veto_adv_capacity.py / results/astock_veto_adv_capacity.json / research/ASTOCK_VETO_ADV_CAPACITY.md / "
    "负控 results/_r2011bmc_adv_negative.py 与收口 results/_r2011bmc_closeout.py（两者 `git add -f` 走既有 `_r[0-9]*` 惯例）/ "
    "轮报告与 state 面）→ **本地未达 origin commit 数=0**。"
    "**S7 实况**：`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/23 22:50 未动）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，bm-a 两行与主账一行历史缩行 healed 注记照录）；"
    "`pre-commit` / `pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 --no-verify。"
    "**诚实声明（口径）**：本面的 `adv20` 用决策日 t 自己的 20 日均成交额，所以它回答的是「按你那天看到的量能，这本书装得下多少」，"
    "不是「明天开盘那一刻真实能吃多少」；5% 的参与率是假设，2%/10% 的敏感性表结论不变但假设本身没被验证。"
    "**未验证（承上条）**：全量 smoke 与 S6 链未跑（竞争窗，`smoke_test.py` / `logs/smoke_legs.json` / `Tools/s6_chain_bmc.py` 为对端写的共享面）；"
    "本面尚未接 smoke 两腿与 S6 腿。|\n"
)


def main() -> int:
    path = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
    with open(path, "r", encoding="utf-8") as fh:
        body = fh.read()
    if "r2011 **addendum**" in body:
        print("addendum already present, refusing to duplicate")
        return 0
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(LINE)
    print("addendum appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
