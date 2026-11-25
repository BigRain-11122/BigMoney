#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""append r2107's round-report line (fresh read, never a whole-file rewrite)."""
import datetime
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "{ts} | r2107 | bm-c | **CONTENTION 轮**（证据 `results/_repo_write_contention.bm-c.json`：rc3，"
    "2 宿主存活〔98008@20:02 interactive + 本窗 97228@23:05〕，开工前 39 张共享面已被别宿主写过、"
    "重叠窗内不可归因 0 张；工作树脏 ~1,950 件）→ 按 r1907 只落新增文件面，禁改共享面、禁重跑 S6 链、"
    "不跑全量冒烟；state/心跳为多宿主共写态面（心跳 21:32 由对端持有），本窗不碰。"
    "watermark verdict=**绿**（`results/watermark_red.json` red=false lane=healthy）。"
    "**PRODUCT**：把梯子从「整段 1052 根当一块」翻到「哪一年赚的」——第一张逐年面。"
    "指令档 1/1 **26.67 %/年**，最好年 2025（+52.55 %）占全部复利增长的 **41.4 %**，砍掉那一年的 bar"
    "同一条书只剩 **19.73 %/年**（判 `SOME_YEARS_CARRY_MORE_THAN_OTHERS`，占 CAGR 26.0 %）；"
    "**样本内没有任何一个日历年亏钱**，指令档最差年=2023 **+10.65 %**；带内档（0/1）最差年 +7.53 %，"
    "按**单位风险**比反而更好（收益/波动 0.905 vs 0.758）——第一版用裸 pp 比会得出相反结论（两档是不同大小的书）。"
    "第三件=逐年归因：2025 的 42.98 pp 加总里权益袖 15.90 pp + IC 12.36 pp + IM 14.71 pp，"
    "袖子是每一档共享的部分，手数才是变量。｜证据：`--selftest` **25/25**；`check` **CHECK_OK**"
    "（16 档×5 年，每张年表复利回本档全期 CAGR）；负控 `python results/_r2107bmc_ladder_years_negative.py` "
    "**10/10 ALL_CONTROLS_PASS**（含词纪律：篡改数字=CHECK FAILED 且**不含 STALE**／上游摘要动=STALE）；"
    "跨面对照：本面 1/1 重建 **26.67 %/年** vs 兄弟面发布 22.34 %/年，差 4.33 pp **正是 k² 袖子权重**，"
    "记在 `cross_face` 不修（共享面，竞争窗）。｜未做（如实）：①`Tools/s6_chain_bmc.py` 与 `smoke_test.py` "
    "接线（两件均为对端未提交脏面）；②r2105 k² 修复与三张 11-23 carry 面重生（共享面写）；③全量冒烟未跑；"
    "④state/心跳未写（多宿主共写态面）。｜S0.5 双扫：fleet/orders **117 件** vs 心跳 orders_ack 归 **258 条**"
    " → **未回执 0**；集团 `origin/main:docs/decisions.md` 原生字节 **250,586 B sha256 79e3083b…** == 自持水位"
    " → **零新决策零动作**（`git cat-file blob` 直落字节，不经 PS 字符串往返、不带 2>&1）。｜S7：孤儿面=**0**"
    "（`py_faces=9` / resident_servers=2）；attrition tripwire **CLEAN**（4 账本，三处历史缩行 healed 照录）；"
    "IterationLoop / Watchdog 未触碰（脏树轮不做自愈）。｜**本地未达 origin commit 数**：见送达行。"
    "｜**CEO 三行**：当前活＝把 carry 梯子的收益按年拆开，回答「钱是哪一年赚的、是不是一年撑起全部」"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_LADDER_YEARS.md`"
    "（2026-11-25T23:2x·指令档 26.67 %/年·2025 一年占 41.4 % 增长·样本内无亏损年·2025 里袖子 15.9 pp/两腿 27.1 pp）"
    "｜下个里程碑＝把本面接进链与冒烟腿、并修 r2105 的 k²（需独占窗，≤48h）"
    "| 记账：轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3"
)


def main():
    ts = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(timespec="minutes")
    with io.open(PATH, encoding="utf-8") as f:
        body = f.read()
    if not body.endswith("\n"):
        body += "\n"
    with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(body + LINE.format(ts=ts) + "\n")
    print("appended r2107 line at %s" % ts)


if __name__ == "__main__":
    main()
