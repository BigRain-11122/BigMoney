#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Append round 2110's report line to round_reports-bm-c.md (single append, LF-preserving).

Written as a file rather than a shell one-liner because the line carries pipes, backticks
and percent signs, and a shell heredoc on this host has already mangled such content once.
"""
from __future__ import annotations

import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGET = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-26T00:1x+08:00 | r2110 | bm-c | **CONTENTION 轮**（证据 "
    "`results/_repo_write_contention.bm-c.json`：rc3 CONTENTION，2 宿主存活"
    "（98008@20:02 interactive + 本窗 19996@00:00），开工前 23 张共享面已被别宿主写过、"
    "重叠窗内不可归因 3 张；工作树脏 1,957 件）→ 按 r1907 只落新增文件面，禁改共享面、"
    "禁重跑 S6 链、不跑全量冒烟；state/心跳为多宿主共写态面（对端持有），本窗不碰。"
    "watermark verdict=**绿**（`results/watermark_red.json` red=false lane=healthy）。"
    "**PRODUCT**：把 8 % 风险预算第一次摊到实测波动上——`idx_fut_carry_sizing_spec` 说"
    "「1 手需要 1,132,145 元」，那是拿声明 8.963 % 除的；实测块波动 **13.636 %**，"
    "1 块要 **1,704,500 元**，100 万的书**只能开 0.59 块**。五把尺子：声明 0.8926 块 / "
    "全样本 0.5867 / 120 日中位 0.6843 / p95 **0.3259** / max 0.3238。桌面那张 **4 块票**"
    "在最乐观的尺子上也花 **4.48 倍**预算，压力窗 **12.27 倍**；历史上 933 个 120 日窗里"
    "只有 **27.97 %** 开得起整 1 块、**0 %** 开得起 2 块——**这本书从来没有开满 2 块**。"
    "跨面对账：stability 面 full-sample 13.636 % 逐位相同（CROSS_FACE_MATCHES）；"
    "sizing 面 1,132,145 元是「1 手 IC 用 IF 对冲的残差」= 另一本书，已点名不取平均"
    "（DIFFERENT_BOOK_NAMED）。｜证据：`--selftest` **15/15**（腿数动态计数，r2043 判例）；"
    "`check` **CHECK_OK 5 rulers / 933 windows**（输入漂移说 STALE、同输入不符说 CHECK "
    "FAILED 且**不含 STALE**）；负控 `python results/_r2110bmc_vol_sized_negative.py` "
    "**20/20 ALL_CONTROLS_PASS**（手改 ruler→CHECK FAILED 无 STALE／手改 history→CHECK "
    "FAILED／翻判词→CHECK FAILED／改 inputs sha→STALE 无 CHECK FAILED／页面必印三判词与"
    "跨面状态／恒等式 blocks×vol==target 五尺子全中／复原字节恒等）。面 "
    "`results/idx_fut_carry_vol_sized_lots.json`、页面 `research/IDX_FUT_CARRY_VOL_SIZED_LOTS.md`、"
    "QA `qa/vol-sized-lots-r2110.md`。｜本轮自捕两枚：①页面表头的 `%` 没转义"
    "（`\"| 块波动 % | ... | %d 块票 |\"` → `ValueError: unsupported format character '|'`）"
    "——r2109 已犯过它的镜像（无格式化 add 里写 `%%`），同一张页面上 `%` 的写法取决于"
    "这一行走不走格式化；②自检腿数硬编码 12 而实际断言 15 条，改动态计数。｜未做（如实）："
    "①未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面）；"
    "②未改 8 % 目标与桌面票（选择面在 sizing 面，本面只读）；③全量冒烟未跑；"
    "④state/心跳未写（多宿主共写态面）。｜S0.5 双扫：fleet/orders **117 件** vs 归一回执 "
    "**331 条** → **未回执 0**；集团 `origin/main:docs/decisions.md` 原生字节 **250,586 B "
    "sha256 79e3083b85c130b8…** == 自持水位 → **零新决策零动作**（`cat-file blob > file` "
    "直落字节、不带 2>&1、不经 PS 字符串往返）。｜S7：孤儿面=**0**（`py_faces=9` / "
    "resident_servers=2，`results/_orphan_face_probe.bm-c.json`）；attrition tripwire 本窗"
    "未跑（无账本改动）；IterationLoop / Watchdog / hooks 未触碰（脏树轮不做自愈）。｜"
    "**本地未达 origin commit 数=0**（commit **06acef67fa** 直推 origin/main "
    "54d62920c8..06acef67fa，非 FF 未发生；fetch 后 `git rev-list --left-right --count "
    "origin/main...HEAD` = **0/0**；`git ls-tree` 核验 **5/5** 件在位）。｜**CEO 三行**："
    "当前活＝把 8 % 风险预算摊到实测波动上，回答「100 万的书到底能开几块价差仓」｜"
    "最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_VOL_SIZED_LOTS.md`"
    "（2026-11-26T00:1x·声明 8.963 % vs 实测 13.636 %·100 万只能开 0.59 块·4 块票在压力窗"
    "花 12.27 倍预算·历史上从没开满 2 块）｜下个里程碑＝把「按滚动波动定块数」接成可执行"
    "仓位规则并接进链与冒烟腿（需独占窗，≤48h）| 记账：轮报告 1 处 + 页面 1 件（脚本渲染）"
    "+ QA 1 件 = 3"
)


def main():
    with io.open(TARGET, "rb") as f:
        raw = f.read()
    prefix = b"" if raw.endswith(b"\n") else b"\n"
    with io.open(TARGET, "ab") as f:
        f.write(prefix + LINE.encode("utf-8") + b"\n")
    with io.open(TARGET, "rb") as f:
        after = f.read()
    assert after.startswith(raw), "append must not rewrite existing bytes"
    print("appended %d bytes; file %d -> %d" % (len(LINE.encode("utf-8")) + len(prefix),
                                                len(raw), len(after)))


if __name__ == "__main__":
    main()
