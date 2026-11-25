#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Append the r2106 bm-c round report line to round_reports-bm-c.md (UTF-8, newline)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOC = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-25T22:5x+08:00 | r2106 | bm-c | **CONTENTION 轮**"
    "（证据 `results/_repo_write_contention.bm-c.json`：rc3，2 宿主存活〔98008@20:02 interactive "
    "+ 本窗 99764@22:40〕，开工前 44 张共享面已被别宿主写过、重叠窗内不可归因 0 张；工作树脏 "
    "1,949 件）→ 按 r1907 只落新增文件面，禁改共享面、禁重跑 S6 链、不跑全量冒烟；"
    "state/心跳为多宿主共写态面（心跳 22:38 由对端写过），本窗不碰。watermark verdict=**绿**"
    "（`results/watermark_red.json` red=false lane=healthy）。**PRODUCT**：把 r2105 的风险面从"
    "「回撤多深」翻译成「客户实际体验」——同一 16 档 rung 日序列，按客户看月结单的单位重算："
    "**最差月、正收益月占比、最长水下 bar 数、最大回撤回本期、Calmar（年化/|MDD| 痛感）**。"
    "指令档 1/1（IC1+IM1）：最差月 **−5.03%**、**78%** 月份为正、最长水下 **120 bar**、"
    "回撤 **114 bar** 回本、Calmar **2.430**。带内唯一合法档 0/1（只买 IM 一手，期望 9.05%）："
    "最差月 **−1.34%**（浅 3.7pp）、回本 **11 bar**（快 10 倍）、Calmar **2.953**（最高），"
    "但正收益月 76.5%（略低）与最长水下 135 bar（略长）——判决 **BAND_CUT_MIXED_EXPERIENCE**"
    "（5 轴中 3 轴利带：最差月/回本/Calmar；2 轴利指令：正收益月/水下时长）。"
    "**本窗跨面自捕（重要）**：r2105 风险面把权益袖**双重缩放**——先 `m=k*sleeve` 再乘 `k`"
    "（=k²·sleeve，权重 0.189 而非 0.435），三向实证同 1052 天网格：单 k（正确）1/1 年化 "
    "**26.667%**/MDD **−10.975%** vs 双 k（r2105 发布版）22.336%/−11.063%，差 4.33pp 恰等于"
    "权益袖重加权（k·11.054%=4.80% vs k²·11.054%=2.09%）。按竞争窗纪律**不改对端共享面**，"
    "只在本面 `cross_face` 块记录偏离与成因（读者永不被同时告知同一本书两个年化而无解释）。"
    "**验证**：`--selftest` **64/64**；`check` **CHECK_OK rc0**（16 档）；负控 "
    "`results\\_r2106bmc_drawdown_experience_negative.py` **8/8 ALL_CONTROLS_PASS**"
    "（手改 Calmar→CHECK FAILED 且**不含 STALE 字样**〔词是合同〕/ladder 漂移→STALE/"
    "cross-face 漂移→STALE/权益臂漂移→STALE/rung 截到 10 bar→CHECK FAILED/缺 ladder→STALE "
    "不假绿/发布面自身绿/判词 token 冻结）。面 `results/idx_fut_carry_drawdown_experience.json`、"
    "页面 `research/IDX_FUT_CARRY_DRAWDOWN_EXPERIENCE.md`、QA `qa/drawdown-experience-r2106.md`。"
    "｜未做（如实）：①**未修 r2105 的 k² 缺陷**（对端共享面，需独占窗）；②未接进 "
    "`Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面）；③全量冒烟未跑"
    "（570+ 腿，竞争窗）；④state-bm-c.json / 心跳未写（多宿主共写态面，对端 22:38 仍持有）。"
    "｜S0.5 双扫：fleet/orders **117 件** vs 心跳 orders_ack **273 条**（state 读数）→ 最新令 "
    "O-20261124-2300 已回执、无未回执；集团 `origin/main:docs/decisions.md` 原生字节 sha256 "
    "**79e3083b…** == 自持水位 → 零新决策零动作（`git cat-file blob` 直落字节，不经 PS 字符串"
    "往返）。｜S7：orphan_face_probe（py_faces=8 / **orphans=0** / resident_servers=1，清 1 残留）；"
    "attrition 账本本窗未跑（无账本改动）；IterationLoop / Watchdog 未触碰（脏树轮不做自愈）。"
    "｜**本地未达 origin commit 数**：见下方送达行。｜**CEO 三行**：当前活＝把风险面从「回撤多深」"
    "翻成「持有它每个月多难受、水下多久、多久回本」｜最近实物="
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_DRAWDOWN_EXPERIENCE.md`"
    "（2026-11-25T22:5x·指令档最差月−5.03%·带内 IM 一手最差月−1.34% 回本快 10 倍·Calmar 最高）"
    "｜下个里程碑＝修 r2105 的 k² 双重缩放并把本面接进链与冒烟腿（需独占窗，≤48h）| "
    "记账：轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3\n"
)


def main():
    with io.open(DOC, "r", encoding="utf-8") as f:
        existing = f.read()
    if "r2106 | bm-c" in existing.split("2026-11-25")[-1][:200] and "r2106 | bm-c" in existing[-4000:]:
        print("SKIP: r2106 line already present")
        return 0
    with io.open(DOC, "a", encoding="utf-8", newline="\n") as f:
        f.write(LINE)
    print("APPENDED r2106 line (%d chars)" % len(LINE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
