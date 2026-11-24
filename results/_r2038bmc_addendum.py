"""r2038 addendum: the delivery-verification row (r2038 main row was written before the push).

Usage
    python results/_r2038bmc_addendum.py
"""
from __future__ import annotations

import io
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

TZ = timezone(timedelta(hours=8))
STAMP = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")

LINE = (
    "| %s | r2038 **addendum**（送达核验） | commit **cfb2686601** 已推 origin/main"
    "（daf20831f4..cfb2686601），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r --name-only origin/main` 七件全在位"
    "（scripts/astock_veto_hedge_deploy_wait.py / results/astock_veto_hedge_deploy_wait.json / "
    "research/ASTOCK_VETO_HEDGE_DEPLOY_WAIT.md / 负控 results/_r2038bmc_deploy_wait_negative.py / "
    "收口 _r2038bmc_closeout.py、_r2038bmc_hb_fields.json、_r2038bmc_report.py，"
    "`_r[0-9]*` 走 `git add -f` 既有惯例；同批带 state-bm-c.json / "
    "fleet/machines/bm-c.json / fleet/round_reports-bm-c.md 三件簿记）→ "
    "**本地未达 origin commit 数=0**。"
    "**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 "
    "**79e3083b85c130b8** → 零新决策；`attrition_ledger_guard scan` **CLEAN**（4 账本）；"
    "`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，首燃 09:05 未动）；"
    "pre-commit / pre-push 爪与 `Tools/git-hooks/` 源同（MATCH/MATCH）；"
    "心跳 `heartbeat_write apply` rc0（ack 前后均 329 未缩，`heartbeat_epoch_utc` 为 int，"
    "gpu_probe util 2.0%% / used 1,716 MiB）；fleet/inbox 0 件。"
    "**坑录（本窗实弹两枚·已修）**："
    "①**函数默认参数在定义时求值**——`def check(json_path: str = OUT_JSON)` 在负控 `_swap` 改模块全局后"
    "读的仍是真件，于是 L1–L8 八条腿全假绿（rc0）；正法=函数体内 `json_path, md_path = OUT_JSON, OUT_MD` "
    "现取，负控才能把 check 指向临时副本（r2037 的 check 本来就是无参签名，本窗漏抄了）；"
    "②**content_sha256 检测不到「文件末尾加一个换行」**——按 `json.dumps(去 envelope 的 dict)` 算的哈希，"
    "加换行后 `json.load` 得到同一个 dict，哈希不变，负控 L4「父面动」假绿；正法=content 相同再比 "
    "file_sha256（字节面才是合同）。"
    "记账：本行 1 处（轮报告 addendum），本轮合计 4。 |"
)


def main() -> int:
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(LINE + "\n")
    print("appended r2038 addendum (%d chars)" % len(LINE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
