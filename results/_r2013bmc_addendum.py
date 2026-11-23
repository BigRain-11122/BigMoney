# -*- coding: utf-8 -*-
"""r2013 addendum: delivery receipt + S0.5 double-sweep at close."""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

SHA = "d43ff8846a"
DELIVERY = (
    "commit %s 已推 origin/main (54b1b4203b..%s)；fetch 后 AHEAD=0 / BEHIND=0；"
    "ls-tree origin/main 七件 blob 在位（scripts/astock_veto_cash_leg.py、results/astock_veto_cash_leg.json、"
    "research/ASTOCK_VETO_CASH_LEG.md、负控 results/_r2013bmc_cash_leg_negative.py 与收口三件 "
    "`_r2013bmc_*`（`git add -f` 走既有 `_r[0-9]*` 惯例））；本地未达 origin commit 数=0"
) % (SHA, SHA)

with io.open(STATE, encoding="utf-8") as fh:
    s = json.load(fh)
s["送达自证_r2013"] = DELIVERY
io.open(STATE, "w", encoding="utf-8", newline="").write(json.dumps(s, ensure_ascii=False, indent=1))

LINE = (
    f"| 2026-11-23 23:5x | r2013 **addendum**（送达核验 + 一处口径说明） | "
    f"commit **{SHA}** 已推 origin/main（54b1b4203b..{SHA}），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r origin/main` 七件 blob 在位 → **本地未达 origin commit 数=0**。"
    "**口径说明（读者会追问的两个数）**：①表里 1,000,000 一档的判词是 `EDGE_LOST_TO_ROUNDING`（比 0.317），"
    "而 5M/10M 是 `EDGE_DEGRADES_UNDER_ROUNDING`——这不是三档判词在打架，而是**100 万时这本书根本不存在**："
    "A 臂只有 3.79% 的钱在场、B 臂 7.41%，两臂各自被迫买成一批 240 只、中位价 2.77 元的便宜股，"
    "「整手 vs 分数」的差在这里读的是**两个不同组合**的差，不是原策略残留的边（r2012 已用同样的口径声明过）。"
    "②现金腿让**比值**变差（0.854→0.825）却让**绝对收益**变好（B 11.38→11.71%、A 8.84→9.26%）——"
    "两者不矛盾：比值是 B−A 除以分数口径的 B−A，分子分母都动了，而 B 臂现金更少（22.83% vs 29.62%），"
    "所以同一个 GC001 利率对 A 的抬升比对 B 多 0.09pp/年。**S7 实况**：`& Tools/register_loop_task.ps1` "
    "**phase ok**（machine=bm-c pin=0 current=0，首燃 11/23 23:45 未动）；`attrition_ledger_guard scan` **CLEAN**；"
    "`pre-commit` / `pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 --no-verify。"
    "**未验证（承上条）**：全量 smoke 与 S6 链未跑（竞争窗，`smoke_test.py` / `logs/smoke_legs.json` / "
    "`Tools/s6_chain_bmc.py` 为对端写的共享面）；本面尚未接 smoke 两腿与 S6 腿。|\n"
)

with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
    fh.write(LINE)
print("addendum written")
