#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2097 (bm-c) honest correction: the S6 chain IS running this round.

I first wrote "S6 链本窗未跑" into the round report because I had decided not to run it; then
`python Tools/s6_chain_bmc.py 2097 --list` turned out to take no --list flag and started a real
legs run (pid 94296, 19:05:46), which is still alive and writing results/. A report that says
"not run" while a writer is in flight is exactly the shape of lie this repo keeps punishing,
so the correction goes in as its own line rather than as a silent edit of the earlier one.
"""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-25T19:3x+08:00 | r2097-correction | bm-c | **勘误**：上面 r2097 行写的「S6 链本窗未跑」在收尾时已不成立。"
    "经过：我先用 `python Tools\\s6_chain_bmc.py 2097 --list` 想列腿，而该驱动不认 `--list`——它把参数当成别的意思并**起了一次真实腿跑**"
    "（pid 94296，19:05:46 起，19:29 仍在推进，已过 idx_fut_carry_capital_ladder / sizing_spec / open_capital / margin 等腿）。"
    "后果两面：①工作树脏面从 1,795 涨到 1,896，新增部分**是链的合法产物**不是对端遗留，故本窗一律不提交；"
    "②本面（r2097 决定面）消费的上游四张面可能被链重写，届时 `check` 会按设计报 **STALE**——这是正确的，"
    "下一轮第一件事就是链停稳后 `python scripts\\idx_fut_carry_decision_face.py run` 重派生（本面目前无链腿，不会自动重算，"
    "这是已知缺口，接线排在下一轮）。教训记一行：**列腿不是这么列的**——驱动只认 `--round N --all/--only ...`，"
    "任何拿不准的参数先看脚本头部 Usage，别在活仓里试。| 记账：本行 1 处（累计 5）"
)


def main():
    text = io.open(PATH, encoding="utf-8", newline="").read()
    if "| r2097-correction |" in text:
        print("already appended")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    io.open(PATH, "w", encoding="utf-8", newline="").write(text + LINE + "\n")
    print("appended %d chars" % len(LINE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
