# -*- coding: utf-8 -*-
"""r2095: append one round-ledger line, asserting the file state first (r2091b lesson)."""
import io

P = "round_reports-bm-c.md"
LINE = (
    "2026-11-25T17:5x+08:00 | r2095 | bm-c | **PRODUCT（新文件面·竞争窗轮）**：竞争探针 "
    "rc=3 CONTENTION（对端交互宿主 pid 93460，15:54 起，本轮 17:41 仍持共享面含本机心跳）→ "
    "按 r1907 只落新增文件面（state/心跳/S6/冒烟均未碰）。产出＝**把 r2094 自己点出的洞补上："
    "一手以上从来没有容量面**。新工具 `scripts/idx_fut_carry_capacity_lots.py`（selftest **15/15**）"
    "用 ETF 容量面同一条 K1 尺子（1% of ADV·20 根中位·60 窗稳定性）量这本书：前月合约按当日最大持仓"
    "判定（无未来数据）；成交类三条腿=平时 20 根中位 / 窗口最弱一日 / **持仓量迁移日**；"
    "采信最紧的一条，持仓量只作参考界。读数：**IC 468 手、IM 752 手**（1% 线），按档位面的每手资本折成 "
    "**5.29 亿 / 8.72 亿元资本**；桌面已发布的最大档位是 2 手（226/232 万元），容量是它的 "
    "**234 / 376 倍** → 判决 **MARKET_IS_NOT_THE_GATE**：今天的墙是资本不是流动性。三条腿的差别才是真发现："
    "平时成交给 1,036/1,630 手、持仓量给 1,705/2,720 手，而**接上前月那一天只成交 46,845/75,215 手**、"
    "1% 只剩 468/752 手；同一把尺子摊到三天就回到 1,640/2,615 手——**移仓节奏是免费的容量**。"
    "容量放满的 carry 按尺子各印一遍（不许单点）：IC 54.5M（calendar 9.65%）/54.6M（strictest 9.68%）"
    "对 15.6M（published 2.76%）；IM 98.9M/102.9M 对 49.4M——容量大不等于收益率稳，r2094 的尺子问题照旧。"
    "｜证据：`python scripts\\idx_fut_carry_capacity_lots.py --selftest` **15/15**；`check` "
    "**CHECK_OK rc0**（cutoff 2026-11-23）；负控 `python results\\_r2095bmc_capacity_negative.py` **7/7**"
    "（N1 空面板拒算、N2 成交量减半→容量正好减半、N3 档位放大 30 倍→headroom 234x 跌到 7.81x 翻成 "
    "CAPACITY_BITES、N4 改数→CHECK FAILED 且**不含 STALE 字样**（r1850 词是合同）、N5 面板动→STALE、"
    "N6 拿中位腿当容量会高估 **2.21/2.17 倍**）；面 `results/idx_fut_carry_capacity_lots.json`、"
    "文档 `research/IDX_FUT_CARRY_CAPACITY_LOTS.md`、QA `qa/capacity-lots-r2095.md`"
    "｜未做（如实）：全量冒烟未跑（上读数 767 腿 760 PASS / 7 FAIL @15:05:57）；S6 链未跑（连续第 6 轮，"
    "竞争窗）；本面**无链腿无冒烟腿**（接线要改 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`，都是共享面）"
    "｜S0.5 双扫：fleet/orders **117 件** / 心跳 orders_ack **331 条** → **未回执 0**；集团 "
    "`origin/main:docs/decisions.md` 原生字节 **250,586B sha256 79e3083b85c130b8…** == 自持水位 → "
    "零新决策零动作；fleet/inbox 空｜S7：orphan_face_probe（py_faces=5 / orphans=0 / resident_servers=1）；"
    "attrition_ledger_guard scan **CLEAN**（4 账本·3 处历史缩行 healed 照录）；水位 **red=false healthy** "
    "@17:57；idle green_idle=false（无闲置档）；Bigmoney-IterationLoop / Watchdog 本窗未触碰（竞争窗）"
    "｜**本地未达 origin commit 数**：commit 前实测 **0/0**｜**CEO 三行**：当前活＝给 carry 书补上"
    "「最多能做多大」这张容量面（一手以上不再靠线性外推）｜最近实物="
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_CAPACITY_LOTS.md`"
    "（2026-11-25T17:5x·468/752 手 @1% 线·234/376 倍余量）｜下个里程碑＝竞争解除后把这面接进 S6 链与冒烟腿"
    "（≤48h）| 记账：轮报告 1 处 + 文档 1 件 + QA 1 件 = 3（state/心跳对端在写，本窗不改）\n"
)

text = io.open(P, encoding="utf-8", newline="").read()
assert text.endswith("\n"), "ledger does not end with a newline; fix before appending"
assert "\n\n" not in text[-3:], "unexpected blank tail"
io.open(P, "w", encoding="utf-8", newline="").write(text + LINE)
print("appended %d chars" % len(LINE))
