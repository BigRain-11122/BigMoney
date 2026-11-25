# -*- coding: utf-8 -*-
"""r2095 delivery addendum: append after the push, asserting file state first."""
import io

P = "round_reports-bm-c.md"
LINE = (
    "2026-11-25T18:0x+08:00 | r2095-delivered | bm-c | 送达补记：commit **eb90035682** 已直推 "
    "origin/main（8ef1c81c88..eb90035682，无 non-FF）；fetch 后 `git rev-list --left-right --count "
    "origin/main...HEAD` = **0/0**；`git ls-tree -r --name-only origin/main` 八件新增面全在位"
    "（scripts/idx_fut_carry_capacity_lots.py、results/idx_fut_carry_capacity_lots.json、"
    "research/IDX_FUT_CARRY_CAPACITY_LOTS.md、qa/capacity-lots-r2095.md、四枚 `_r2095bmc_*` 探针/负控/收口件）"
    "→ **本地未达 origin commit 数=0**。state/心跳仍由对端宿主写，本窗未碰。"
    "| 记账：本行 1 处（累计 4）\n"
)

text = io.open(P, encoding="utf-8", newline="").read()
assert text.endswith("\n"), "ledger does not end with a newline"
io.open(P, "w", encoding="utf-8", newline="").write(text + LINE)
print("appended %d chars" % len(LINE))
