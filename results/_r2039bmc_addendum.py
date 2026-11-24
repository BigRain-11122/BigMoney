"""r2039 addendum: delivery verification plus the two defects this round's own page caught.

Same guards as the round row: one source for the text, an explicit newline probe, and a
line-count assertion so a glued row cannot pass silently.
"""
from __future__ import annotations

import io
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)

ROW = (
    "| {ts} | r2039 **addendum**（送达核验 + 本窗两枚自捕坑） | "
    "commit **791df06629** 已推 origin/main（2ab01416b9..791df06629），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r --name-only origin/main` 七件新面孔全在位（scripts/astock_veto_hedge_wait_ladder.py / "
    "results/astock_veto_hedge_wait_ladder.json / research/ASTOCK_VETO_HEDGE_WAIT_LADDER.md / "
    "负控 results/_r2039bmc_ladder_negative.py / 收口 _r2039bmc_closeout.py、_r2039bmc_hb_fields.json / "
    "轮报告 _r2039bmc_report.py，`_r[0-9]*` 走 `git add -f` 既有惯例；同批带 state-bm-c.json / "
    "fleet/machines/bm-c.json / fleet/round_reports-bm-c.md 三件簿记）→ **本地未达 origin commit 数=0**。"
    "**交付后校正**：读渲染页时发现「百分比套百分比」——`_pct()` 按约定会乘 100，而阶梯/波动字段本身已是百分数，"
    "页面因此印出 `2734.3286%`。修法=新增 `_pp()` 只格式化不缩放，并把三条腿钉进自检（页面不得出现 `2734.`、"
    "必须出现 `27.3433%` 与 `10.763%`）——selftest 由 49 腿升到 **52/52 PASS**，`check` 仍 rc0，负控 **29/29 PASS**。"
    "**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本 / 3 处 healed 照录）；"
    "`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0）；pre-commit / pre-push 爪 MATCH/MATCH；"
    "心跳 ack 329（未缩）、`heartbeat_epoch_utc` int；fleet/inbox 0 件。"
    "**坑录（本窗实弹两枚·已修）**：①**格式化助手要按「输入是分数还是百分数」分两支**——`_pct(x)` 乘 100、"
    "`_pp(x)` 不乘，混用不会报错，只会在页面上把 27.343% 印成 2734.3%；这类错 selftest 抓不到，"
    "因为每条腿自己算的也是同一个错值——**只在渲染页上看得见，所以腿要钉在页面上**（本轮三条腿已钉）。"
    "②**用全局文本替换修 `%%` 必须限定到真在做 % 格式化的那个字符串**——本轮把一句话模板里的 `10.763%%` 一并改成单 %，"
    "该串随后被 `%` 运算符套用即 `TypeError: not enough arguments for format string`；"
    "同一文件里没被格式化的句子反而必须是单 %。判据=这一串后面有没有跟 `% (...)`。"
    "记账：本行 1 处（轮报告 addendum），本轮合计 4。 |"
)


def main() -> int:
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        before = fh.read()
    n_before = before.count("\n")
    prefix = "" if before.endswith("\n") else "\n"
    row = ROW.format(ts=NOW.strftime("%Y-%m-%d %H:%M"))
    with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(prefix + row + "\n")
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        after = fh.read()
    added = after.count("\n") - n_before
    print("newline guard used: %s" % bool(prefix))
    print("lines added: %d (expected 1)" % added)
    print("literal placeholder left: %s" % ("%s" in row))
    return 0 if added == 1 and "%s" not in row else 1


if __name__ == "__main__":
    raise SystemExit(main())
