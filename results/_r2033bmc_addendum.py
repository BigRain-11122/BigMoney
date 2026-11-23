"""r2033 addendum: append the delivery receipt row and stamp the state with it."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
SHA = "6c59fcc113"

ROW = (
    "| 2026-11-24 07:2x | r2033 **addendum**（送达核验） | commit **%s** 已推 origin/main "
    "（7b88e6fc80..%s），fetch 后 **AHEAD=0 / BEHIND=0**，`git ls-tree -r --name-only origin/main` "
    "六件全在位（scripts/astock_veto_hedge_carrier.py / results/astock_veto_hedge_carrier.json / "
    "research/ASTOCK_VETO_HEDGE_CARRIER.md / 负控 results/_r2033bmc_carrier_negative.py / "
    "收口 _r2033bmc_closeout.py、_r2033bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例）"
    "→ **本地未达 origin commit 数=0**。**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**"
    "（116 令 / 329 回执 / unacked=[]）；集团 decisions.md 原字节 sha256 仍 **79e3083b85c130b8** → "
    "零新决策；`attrition_ledger_guard scan` **CLEAN**（4 账本 / 4 处 healed）；"
    "`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，首燃 07:15）；"
    "`Tools/heartbeat_write.py apply` rc0（ack 前后均 329，未缩）；fleet/inbox 0 件。"
    "记账：本行 1 处（轮报告 addendum），本轮合计 4。 |"
)


def main() -> int:
    with open(REPORT, "r", encoding="utf-8", newline="") as fh:
        body = fh.read()
    if "r2033 **addendum**" in body:
        print("addendum already present")
    else:
        if not body.endswith("\n"):
            body += "\n"
        body += ROW.rstrip("\n") + "\n"
        with open(REPORT, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
        print("addendum appended")

    with open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    state["送达自证_r2033"] = (
        "commit **6c59fcc113** 已推 origin/main（7b88e6fc80..6c59fcc113），fetch 后 "
        "**AHEAD=0 / BEHIND=0**，git ls-tree -r origin/main 六件 blob 全在位"
        "（scripts/astock_veto_hedge_carrier.py / results/astock_veto_hedge_carrier.json / "
        "research/ASTOCK_VETO_HEDGE_CARRIER.md / 负控 results/_r2033bmc_carrier_negative.py / "
        "收口 _r2033bmc_closeout.py、_r2033bmc_hb_fields.json）→ **本地未达 origin commit 数=0**。"
    )
    state["last_seen"] = NOW
    state["updated_at"] = NOW
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("state stamped 送达自证_r2033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
