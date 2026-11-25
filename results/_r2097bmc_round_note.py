#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2097 (bm-c) round-report append. Kept as the runnable evidence of the bookkeeping
line rather than a hand-pasted shell one-liner (CJK + backslashes in a shell string is
exactly the shape that silently mangles, r1984-style)."""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-25T19:1x+08:00 | r2097 | bm-c | **PRODUCT**：水位 verdict=**绿**"
    "（results/watermark_red.json red=false healthy）。竞争探针 rc=0 CLEAN（只有本窗宿主 pid=96336 存活，18:55 起；"
    "前三轮的对端交互宿主 pid 93460 已死亡，最后一次写盘 18:48:51）→ 共享面恢复可写，但**轮首工作树脏 1,795 件**"
    "（对端未提交半成品：Tools/s6_chain_bmc.py、fleet/machines/bm-c.json、research/QUANT-BLOCK-BOARD.md、"
    "data/daily 全量刷新面）→ 按轮首脏规只落新增文件面并定向 add，禁把半成品一起提交。产出＝"
    "**把「哪把尺子算数」从文风问题变成闸**：r2094 报三把尺子 6.92pp 分歧并拒绝挑一把，r2096 证明 IC 的移仓日台阶是后付"
    "（次日回吐 0.170/0.159、移仓后 8 日比前 8 日低 3.96/5.29pp、p=0.026/0.030）——那么把台阶记成当日收益的尺子不是"
    "「最差的一把」而是**错的一把**，此前把它平均进区间正是「利率被尺子绑住」的成因。新面 "
    "`scripts/idx_fut_carry_decision_face.py`（selftest **26/26**）冻结准入规则"
    "（verdict==COST_BOOKED_BY_LATER_CARRY 才可报）并重算：**IC 可报区间从 6.92pp 塌到 0.03pp"
    "（9.65–9.68% 年化，净超额 113,698–114,059 元/年）**；**IM 一把都不采信 → 无可报数**"
    "（两把有样本的尺子给出不同种类的解释：calendar PARTIAL_REVERSAL p=0.607 / strictest REAL_COST p=0.421，"
    "样本量不是瓶颈，51/60 对已过 min_pairs=30 → 加钱也不动这道门）。判词 **NO_ORDER_ON_BOTH_LEGS**："
    "IC=NO_ORDER_CAPITAL_BELOW_FIRST_RUNG（一档 1,129,565.88 元 vs 账面 1,000,000 元，差 129,566 元=12.96%）；"
    "IM=NO_ORDER_ACCOUNTING_UNSETTLED。先决次序声明为 accounting>capital>liquidity>order"
    "（会计有争议的书不能写成「资金到位即可下单」）。"
    "｜证据：`python scripts\\idx_fut_carry_decision_face.py --selftest` **26/26**；`check` **CHECK_OK rc0**"
    "（cutoff 2026-11-23）；负控 `python results\\_r2097bmc_decision_face_negative.py` **11/11**"
    "（手改→CHECK FAILED 且不含 STALE 字样〔词是合同〕/输入动→STALE/缺面→DATA_BLOCKED 不默认 0/"
    "IC 会计翻面→连区间都没有/补足本金→IC 过资本门但 IM 仍卡会计/0.4 手→流动性门/发布面绝不给无口径品种一个数）"
    "｜面 `results/idx_fut_carry_decision_face.json`、文档 `research/IDX_FUT_CARRY_DECISION_FACE.md`、"
    "QA `qa/decision-face-r2097.md`"
    "｜未做（如实）：本面**无链腿无冒烟腿**（接线要改 Tools/s6_chain_bmc.py 与 smoke_test.py，两者在本轮开工时"
    "都是对端未提交脏面）；全量冒烟未跑；一手以上收益衰减仍未测"
    "｜S0.5 双扫：fleet/orders **117 件** / 心跳 orders_ack（去 .md 归一）**258 条** → **未回执 0**；"
    "集团 `origin/main:docs/decisions.md` 原生字节 **250,586B sha256 79e3083b85c130b8…** == 自持水位 → 零新决策；"
    "orders.md 字节已变（sha 25d37786…，自持 6bd40fec…）→ 新增行是 MV0001 交付到 bm-c 收件口"
    "（`100.123.74.104:11436`，车道=bm-a）→ 本机只做接收侧核验：**端口 LISTEN pid=37836**、"
    "`media/inbox/intake` 只有 2026-11-24 22:41 的自测文件、**bm-a 侧 20h 零文件落地**（如实上报，非本司车道不改）；"
    "fleet/inbox 空"
    "｜S7：orphan_face_probe（py_faces=3 / orphans=0 / resident_servers=2）；attrition 账本本窗未跑（无账本改动）；"
    "Bigmoney-IterationLoop / Watchdog 本窗未触碰（修红与自愈留待无脏树轮）"
    "｜**本地未达 origin commit 数**：commit 前实测 **0/0**"
    "｜**CEO 三行**：当前活＝把四张 carry 面收敛成一个决定（今天不做，做之前差什么）"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_DECISION_FACE.md`"
    "（2026-11-25T19:0x·IC 可报区间 9.65–9.68%·差本金 129,566 元·IM 无可报数）"
    "｜下个里程碑＝把本面接进 S6 链与冒烟腿（等共享面脏树清干净，≤48h）"
    "| 记账：轮报告 1 处 + 文档 1 件 + QA 1 件 = 3"
)


def main():
    text = io.open(PATH, encoding="utf-8", newline="").read()
    if "| r2097 |" in text:
        print("already appended")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    io.open(PATH, "w", encoding="utf-8", newline="").write(text + LINE + "\n")
    print("appended %d chars" % len(LINE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
