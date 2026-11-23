"""r2025 addendum: delivery receipt into the round report and the state face."""

from __future__ import annotations

import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")

NOTE = (
    "commit **9105a33ffb** 已推 origin/main（8c940b3eb8..9105a33ffb），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r --name-only origin/main` 七件 blob 全在位（scripts/astock_veto_hedge_picker.py / "
    "results/astock_veto_hedge_picker.json / research/ASTOCK_VETO_HEDGE_PICKER.md / 负控 "
    "results/_r2025bmc_picker_negative.py / 收口 _r2025bmc_closeout.py、_r2025bmc_round_report.py、"
    "_r2025bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例）→ **本地未达 origin commit 数=0**。"
)
LINE = (
    "| 2026-11-24 04:5x | r2025 **addendum**（送达核验） | " + NOTE +
    "**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "`attrition_ledger_guard scan` **CLEAN**；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0）；"
    "fleet/inbox 0 件。记账：本行 1 处（轮报告 addendum），本轮合计 4。 |\n"
)


def main() -> int:
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if not text.endswith("\n"):
        text += "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + LINE)

    st = json.load(open(STATE, encoding="utf-8"))
    st["送达自证_r2025"] = NOTE
    st["记账_r2025"] = "轮报告 2 处（正文 + addendum）+ state 1 处 + 心跳 1 处 = 4"
    st["本地未达 origin commit 数"] = 0
    st["本地未达origin"] = 0
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    print("addendum appended; state updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
