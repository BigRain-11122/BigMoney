# -*- coding: utf-8 -*-
"""r2022 addendum: delivery receipt for round 2022 (dfbc2ee002)."""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

ROW = (
    "| 2026-11-24 03:5x | r2022 **addendum**（送达核验） | commit **dfbc2ee002** 已推 origin/main"
    "（e860d6088c..dfbc2ee002），fetch 后 **AHEAD=0 / BEHIND=0**，`git ls-tree -r origin/main` 七件 blob 全在位"
    "（scripts/astock_veto_hedgeable_beta.py / results/astock_veto_hedgeable_beta.json / "
    "research/ASTOCK_VETO_HEDGEABLE_BETA.md / 负控 results/_r2022bmc_hedge_negative.py / 收口 "
    "_r2022bmc_closeout.py 与 _r2022bmc_round_report.py、_r2022bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` "
    "既有惯例）→ **本地未达 origin commit 数=0**。**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**"
    "（116 令 / 329 回执 / unacked=[]）；`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed "
    "注记照录）；`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 "
    "--no-verify；`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/24 03:35 "
    "未动）；fleet/inbox 0 件。**轮号处置**：本轮取 **r2022** 不取 2021——2021 是本树另一宿主（pid 51252）在飞的轮"
    "（`results/_r2021bmc_*` 于 03:10 落盘），`state-bm-c.json` 的 `round_no_note` 已留痕，后续轮看到跳号应按此查"
    "而不是按「丢了一轮」查。记账：本行 1 处（轮报告 addendum），本轮合计 4。 |\n"
)


def main() -> int:
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if "r2022 **addendum**" in text[-6000:]:
        print("addendum already present")
        return 0
    sep = "" if text.endswith("\n") else "\n"
    new = text + sep + ROW
    with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(new)
    print("addendum appended (%d -> %d bytes)" % (len(text), len(new)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
