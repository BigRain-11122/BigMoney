import json

ROW = (
    "| 2026-11-24 04:4x | r2024 **addendum**（送达核验） | "
    "commit **9f8664d3b7** 已推 origin/main（f0405d2dab..9f8664d3b7），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree origin/main` 四件 blob 全在位（scripts/astock_veto_hedge_daily.py d8a621ca65 / "
    "results/astock_veto_hedge_daily.json cd3a307a55 / research/ASTOCK_VETO_HEDGE_DAILY.md 4307baf3ef / "
    "负控 results/_r2024bmc_hedge_daily_negative.py 007aeaa255，`_r[0-9]*` 走 `git add -f` 既有惯例）→ "
    "**本地未达 origin commit 数=0**。"
    "**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "`attrition_ledger_guard scan` **CLEAN**；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0）；"
    "fleet/inbox 0 件。记账：本行 1 处（轮报告 addendum），本轮合计 4。 |\n"
)

path = "fleet/round_reports-bm-c.md"
with open(path, encoding="utf-8") as fh:
    body = fh.read()
assert body.endswith("\n")
with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(body + ROW)

st = json.load(open("state-bm-c.json", encoding="utf-8"))
st["送达自证_r2024"] = ("commit 9f8664d3b7 已推 origin/main (f0405d2dab..9f8664d3b7)；fetch 后 AHEAD=0 / BEHIND=0；"
                     "ls-tree origin/main 四件 blob 在位（scripts/astock_veto_hedge_daily.py d8a621ca65、"
                     "results/astock_veto_hedge_daily.json cd3a307a55、research/ASTOCK_VETO_HEDGE_DAILY.md 4307baf3ef、"
                     "负控 results/_r2024bmc_hedge_daily_negative.py 007aeaa255）；本地未达 origin commit 数=0")
json.dump(st, open("state-bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("addendum appended; state updated")
