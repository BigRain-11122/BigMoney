# -*- coding: utf-8 -*-
"""Append the r2103 round line to logs/iteration-loop/round_reports-bm-c.md.

Idempotent: if a line already carries the r2103 tag it does nothing.  Written as
a script (not an inline append) so the text that was added is itself in git.
"""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = [os.path.join(ROOT, "round_reports-bm-c.md"),
           os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")]
TAG = "| r2103 |"

LINE = (
    "2026-11-25T22:3x+08:00 | r2103 | bm-c | **CONTENTION 轮**"
    "（证据 `results/_repo_write_contention.bm-c.json`：rc3 CONTENTION，3 宿主存活"
    "〔85312@20:01 / 98008@20:02 两个 interactive + 本窗 97320@21:40〕，"
    "开工前 24 张共享面已被别宿主写过、重叠窗内不可归因 2 张；工作树脏 1,949 件）"
    "→ 按 r1907 只落新增文件面，禁改共享面、禁重跑 S6 链、不跑全量冒烟；"
    "state/心跳为多宿主共写态面，本窗不碰。watermark verdict=**绿**"
    "（`results/watermark_red.json` red=false lane=healthy）。"
    "**PRODUCT**：把 `research/STRATEGY-20261125.md` 第四节那张「写死」的触发表做成了**可执行的合同**"
    "——`scripts/policy_trigger_audit.py` 逐条对照 文档/引擎常量/今日输出/实测风险 四源，"
    "判决 **4_TRIGGER_CONTRACT_FINDINGS**：①同一风险目标写成两个数（§1 7%、§3 9%，引擎取 7%），"
    "按文档自己的预算合出 5.78%/6.05%/6.56%（ρ=0/0.1/0.3），要落 9% 得把预算放大 1.487 倍=L1 6.84%+L2 5.20%；"
    "②名义上限在常量里是袖子的 2.5×NAV，代码却按腿各发一份，目标合计 **4.758× NAV**"
    "（今天被保证金降档遮住：目标保证金 537,763→落地 268,882≤350,000，实际名义 2.241×）；"
    "③6%/10% 回撤阶梯喂的是 **carry 一条腿**的累计序列而不是组合（书自身 MDD −10.556%、当前水下 75 根）；"
    "④`单腿 60 日 carry < −2pp` 这条线第一次有了价格：按实测漂移/波动，一条**正常**腿在 "
    "IC 8.1%、IM 9.7% 的 60 日窗里会掉到线下（十年三四次误停），要 2.5% 尾部应写 **IC −3.6pp / IM −4.2pp**。"
    "验证：selftest **11/11**、`--check` rc0（幂等）、负控 **9/9**（逐个污染源文件证明四条发现各自会消失，"
    "含 2.5 倍名义上限与组合净值喂阶梯两条反向证）。**本窗自捕**：我先把文档 `−2pp` 的 U+2212 负号在 GBK 控制台读成 "
    "`?2pp`，按「占位符」写了一版结论；负控跑红后用 `ascii()` 核字节，改判为「写了但太紧」——读带负号的规格行必须过 repr。"
    "实物：`scripts/policy_trigger_audit.py` / `results/policy_trigger_audit.json` / "
    "`research/POLICY_TRIGGER_AUDIT.md` / `qa/policy-trigger-audit-r2103.md` / "
    "`results/_r2103bmc_trigger_audit_negative.py`。"
    "下轮指针（干净树首件事）：①把本面接进 `Tools/s6_chain_bmc.py`（check-only 腿，漂移文案自称 STALE）；"
    "②把 −3.6/−4.2pp 的建议值与引擎实际读的变量对上（改引擎=共享面，需无竞争轮）；"
    "③回撤阶梯改喂组合净值属策略作者决定，本面只留证据。"
    "孤儿面=0；本地未达 origin commit 数=0（送达核验见下一条）。"
)


def main():
    wrote = []
    for path in TARGETS:
        if not os.path.exists(path):
            continue
        text = io.open(path, "r", encoding="utf-8").read()
        if TAG in text:
            print("SKIP already tagged: %s" % os.path.relpath(path, ROOT))
            continue
        with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(("\n" if not text.endswith("\n") else "") + LINE + "\n")
        wrote.append(os.path.relpath(path, ROOT))
    print("appended: %s" % (", ".join(wrote) if wrote else "nothing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
