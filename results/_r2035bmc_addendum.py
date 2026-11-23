"""r2035 addendum: record the delivery receipt on the round report (fresh read, single write)."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

ROW = (
    "| 2026-11-24 07:5x | r2035 **addendum**（送达核验） | commit **a0ce136252** 已推 origin/main"
    "（44a20c7ea4..a0ce136252），fetch 后 **AHEAD=0 / BEHIND=0**，`git ls-tree -r --name-only "
    "origin/main` 六件全在位（scripts/astock_veto_hedge_margin.py / results/astock_veto_hedge_margin.json / "
    "research/ASTOCK_VETO_HEDGE_MARGIN.md / 负控 results/_r2035bmc_margin_negative.py / 收口 "
    "_r2035bmc_closeout.py 与 _r2035bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例；"
    "同批带 state-bm-c.json / fleet/machines/bm-c.json / fleet/round_reports-bm-c.md 三件簿记）→ "
    "**本地未达 origin commit 数=0**。**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**"
    "（116 令 / 329 回执 / unacked=[]）；集团 `git cat-file blob origin/main:docs/decisions.md` "
    "原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；`attrition_ledger_guard scan` **CLEAN**"
    "（4 账本 / 4 处历史缩行 healed 注记照录）；`& Tools/register_loop_task.ps1` **phase ok**"
    "（pin=0 current=0，首燃 07:50 未动）；pre-commit / pre-push 爪与 `Tools/git-hooks/` 源同（MATCH/MATCH）；"
    "心跳 `heartbeat_write apply` rc0（ack 前后均 329 未缩，`heartbeat_epoch_utc` 为 int，"
    "gpu_probe util 3.0% / used 3,132 MiB）；fleet/inbox 0 件。记账：本行 1 处（轮报告 addendum），"
    "本轮合计 4。 |"
)


def main() -> int:
    with open(REPORT, "r", encoding="utf-8", newline="") as fh:
        body = fh.read()
    if "r2035 **addendum**" in body:
        print("addendum already present")
        return 0
    if not body.endswith("\n"):
        body += "\n"
    body += ROW.rstrip("\n") + "\n"
    with open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    print("addendum appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
