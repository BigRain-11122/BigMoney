#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""append this round's row to round_reports-bm-c.md (r2101 bm-c)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ROW = (
    "\n2026-11-25T22:0x+08:00 | r2101 | bm-c | **CONTENTION 轮**（证据 `results/_repo_write_contention.bm-c.json`：rc3 3 宿主存活"
    "〔85312@20:01 / 98008@20:02 两个 interactive + 本窗 98724@21:10〕，开工前 82 张共享面已被别宿主写过、重叠窗不可归因 2 张；工作树脏 1,949+ 件）"
    "→ 按 r1907 只落新增文件面，禁改共享面、禁重跑 S6 链、不跑全量冒烟；state/心跳为多宿主共写态面，本窗不碰。watermark verdict=**绿**（`results/watermark_red.json` red=false lane=healthy）。"
    "**PRODUCT**：把 r2097 挂着的未做项「一手以上收益衰减仍未测」结掉——日线没有深度，所以不假装知道冲击是多少，而是把它拆成两个都能算的量："
    "①**预算**（纯算术）= carry 元/手·年 ÷（移仓次数/年 × 2 侧 × 名义）：IC published **32.9 bp/侧**（一次移仓 65.7 bp）、calendar **114.9**、strictest **115.2**；IM published **68.3**、calendar **142.4**、strictest **136.9**。"
    "②**对照**=声明过的平方根冲击律（k=0.5，列名 `rule_impact_bp`，不叫测量值）：交叉点 IC **35,573.5 手**、IM **197,466.9 手**。"
    "真正的产出是**关卡排序**（按手数）：IC 资本 2 手 → 1% ADV 线 468.4 → standing OI 1,706.5 → 冲击=预算 35,573.5；IM 2 → 752.1 → 2,798.6 → 197,466.9 —— 判决 **DECAY_DOES_NOT_BITE**：执行成本是最后一个关卡（IC 交叉点是 1% 线的 **76 倍**、standing OI 的 **20.8 倍**、桌面档位的 **17,787 倍**）。"
    "于是 r2100 阶梯里 41.785%（六手）那种格子**不是被成本否掉的，是被资本与名义上限否掉的**——这两件事此前在同一张面上从没分开过。测量 vs 声明严格分开：移仓 **4.20 次/年**（60 日窗内前月身份变动 1 次 ×252/60）、剔除移仓日的日波动 IC **194.3bp** / IM **215.1bp**（各 58 个干净收益）、ADV、容量点、standing OI 全部来自本仓面板；k / 平方根形状 / roll_days=3 / 252 / 「一侧预算=整次移仓的一半」/「绑定=最差尺子」全部声明在先。"
    "｜证据：`--selftest` **35/35**；`check` **CHECK_OK rc0**（verdict=DECAY_DOES_NOT_BITE ruler-legs=6 cutoff=2026-11-25）；"
    "负控 `python results\\_r2101bmc_impact_decay_negative.py` **8/8**（N1 手改预算→CHECK FAILED 且**不含 STALE 字样**〔词是合同〕；N2 输入摘要动→STALE；N3 关卡顺序反转→CHECK FAILED〔数都还在，顺序错了也是缺陷〕；N4 判决翻面→红；N5 缺上游面→DATA_BLOCKED 点名文件、不默认 0；N6 排序判据可证伪：1% 线放宽到交叉点 4 倍时冲击就不再是最后一道墙；N7 保留率>1→红；N8 发布面自身必须绿）。"
    "面 `results/idx_fut_carry_impact_decay.json`、页面 `research/IDX_FUT_CARRY_IMPACT_DECAY.md`、QA `qa/impact-decay-r2101.md`。"
    "｜未做（如实）：①未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面），本面暂为 check-only 独立腿；②仍未重生 11-23 那三张 carry 面（r2099 工单，CONTENTION 禁写共享面）；③全量冒烟未跑（570+ 腿，竞争窗）；④state/心跳未写。"
    "｜S0.5 双扫：fleet/orders **117 件** vs 心跳 orders_ack **331 条**（去 .md 归一）→ **未回执 0**（r2066 判例：2026-10-26 前的他机 lane 广播不逐令补 ack）；集团 `origin/main:docs/decisions.md` 原生字节 **250,586B sha256 79e3083b85c130b8…** == 自持水位 → **零新决策零动作**（`git cat-file blob` 直落字节，不经 PS 字符串往返）；`orders.md` sha **25d37786…** 与 r2097 同值 → 零新增行；fleet/inbox 空。"
    "｜S7：orphan_face_probe（py_faces=7 / **orphans=0** / resident_servers=1）；attrition 账本本窗未跑（无账本改动）；IterationLoop / Watchdog 未触碰（脏树轮不做自愈）。"
    "｜**本地未达 origin commit 数**：commit 前实测 **0/0**。"
    "｜**CEO 三行**：当前活＝给这本书算清「一次移仓最多能花多少 bp」，并把四个关卡按手数排队"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_IMPACT_DECAY.md`（2026-11-25T22:0x·预算 32.9bp/侧·冲击交叉 35,573 手=桌面档位的 17,787 倍·执行成本是最后一道墙）"
    "｜下个里程碑＝把本面接进 S6 链与冒烟腿，并重生 11-23 三张面让 one_lot_ruler 翻成 ONE_RULER（等共享面清干净，≤48h）| 记账：轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3\n")

path = os.path.join(ROOT, "round_reports-bm-c.md")
with io.open(path, "a", encoding="utf-8", newline="") as fh:
    fh.write(ROW)
print("appended %d chars" % len(ROW))
