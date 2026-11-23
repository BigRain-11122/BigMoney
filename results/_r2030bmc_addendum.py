"""r2030 addendum: delivery receipt line for fleet/round_reports-bm-c.md (new file)."""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

LINE = (
    "| 2026-11-24 06:2x | r2030 **addendum**（送达核验） | commit **60a4b8820a** 已推 "
    "origin/main（ede3da0903..60a4b8820a），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r --name-only origin/main` 六件全在位（scripts/astock_veto_hedge_walkforward.py / "
    "results/astock_veto_hedge_walkforward.json / research/ASTOCK_VETO_HEDGE_WALKFORWARD.md / "
    "负控 results/_r2030bmc_walkforward_negative.py / 收口 _r2030bmc_closeout.py、_r2030bmc_hb_fields.json，"
    "`_r[0-9]*` 走 `git add -f` 既有惯例）→ **本地未达 origin commit 数=0**。"
    "**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本 / 1 处 healed）；"
    "`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0）；fleet/inbox 0 件。"
    "记账：本行 1 处（轮报告 addendum），本轮合计 4。 |\n"
)


def main() -> int:
    with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(LINE)
    print("addendum appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
