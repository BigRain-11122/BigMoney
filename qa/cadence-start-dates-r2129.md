# 冬天之外还站得住吗 —— 20→10 调仓的起跑日检验（r2129）

- 轮次：r2129（bm-c）
- 时间：2026-11-26 12:0x-12:2x
- 产品件：`scripts/etf_book_cadence_start_dates.py`、`results/etf_book_cadence_start_dates.json`、`research/ETF_BOOK_CADENCE_START_DATES.md`
- 结论一句话：**站不住**。冬天的 +0.76 pp 是 2020 年一个起跑日分布给的；挪到 2021/2023/2025 起跑，中位 −2.64 pp、只有三分之一的起跑日为正（且那三分之一主要是同一段行情被重复计数），一年近互斥尺子上 −0.21 pp ≈ 零。

## 1. 本轮为什么做这个

r2128 留下了自己答不了的话：本族所有相位书的起跑日都落在 2020-01-02..2020-03-05，所以「格内带宽」量的是一个冬天。r2127 的 `CADENCE_LADDER_IS_K_ROBUST` 与 r2128 的 +0.76 pp 都在那个冬天里。续作点原文里写着「需要在样本后半段复跑少量格，把日历项变成跨年度的分布」。本面用最便宜的构造做完了它，没有解冻相位网格。

## 2. 做了什么（可复算）

```
python scripts/etf_book_cadence_start_dates.py selftest   # 24/24
python scripts/etf_book_cadence_start_dates.py run        # rc0，73s，42 cells
python scripts/etf_book_cadence_start_dates.py check      # rc0，48s，CHECK OK
```

- 22 个季度锚点（2020-06-01..2025-09-01），每个锚点跑 R10 与 R20 各一次，n_hold=5，收盘决策→次日开盘，各自付自己的换手成本（8bp 与 1bp 两档）：21 个锚点可用，**2025-09-01 因只剩 298 根 bar 被具名排除**（不是 0）。
- 三把尺子：TO_CUTOFF（嵌套）、252（一年）、504（两年，3 个锚点具名成洞）。
- 引擎、面板、分类三件全部 import 家族既有实现（`fast_next_open` / `build_panel` / `classify`），零重实现。

## 3. 读数

| 尺子 | n | 中位 | 为正 | 四分位差 |
|---|---|---|---|---|
| TO_CUTOFF | 21 | −2.64 pp | 33% | 8.54 pp |
| 252 一年 | 21 | −0.21 pp | 48% | 12.11 pp |
| 504 两年 | 18 | −5.80 pp | 28% | 9.60 pp |
| 1bp/边 TO_CUTOFF | 21 | −1.46 pp | 33% | 8.73 pp |
| 1bp/边 一年 | 21 | +0.86 pp | 57% | 12.32 pp |

长窗/短窗拆分：≥1000 根 10 个里 **1 个为正**（中位 −3.98）；<1000 根 11 个里 6 个为正。三个大正数（2023-09 +12.08、2024-09 +15.32、2024-12 +12.06）全部落在那段 2024-09 起的行情里——同一段行情被三个起跑日各数一次。

## 4. 自我检查（这一条最容易被漏）

- **嵌套不等于独立**：所有书跑到同一 cutoff，晚起的是早起的严格子窗。第一版只发了 TO_CUTOFF 一把尺子，读到「33% 为正」会把它读成 21 个独立证据。发现后补了 252/504 固定 horizon 尺子（同一趟跑的头部切片，`F.metrics` 自带按切片首值归一，不会把水平当收益），并写进 R5 与 `honest` 栏。
- **判词由数字算，不由手写**：`words_for()` 是纯函数，`check` 用存储的 cells 重算 pooled 与判词，两边不一致即 CHECK FAILED（不带 STALE 字样，区别于面板字节移动）。
- **面板一动报 STALE**：`fingerprint()` 记 cutoff/bars/cols/末行价格的 sha1，`check` 重建面板后比 sha1；移动报 STALE（rc3），同输入数字不等报 CHECK FAILED（rc1，r1934 判词合同）。
- **成本两档并列**，不把 1bp 的 +0.86 pp 拿来当结论：它在四分位差 12.32 pp 里，且 TO_CUTOFF 同档是 −1.46 pp。

## 5. 没有做的（如实记）

- **无 S6 链腿、无 smoke 腿**：`Tools/s6_chain_bmc.py` 与 `smoke_test.py` 都是共享面，本轮竞争探针 rc=3（另有 interactive 宿主在写共享面），按 r1907 只落新增文件。接线挂账，见 `carrier_debt_r2129`。
- **没跑全量冒烟**：同上（全量套件读的正是对端在改的面），因此本轮不宣称任何套件总数；可引用读数仍是 r2125 的 773/781 PASS 10 FAIL 那一趟。
- **没解冻相位网格**：本面只挪起跑日，不重烧 atlas 面板（零重烧，73s 全是既有面板上的计算）。
- **没动票面**：`etf_book_rebal_adoption` = PHASE_DEPENDENT 不变；本面只收紧「节奏阶梯允许说的一句话」。

## 6. 下一轮的精确续作点

1. 无竞争窗：S6 链腿接在 `etf_book_cadence_comparable` 之后（先 check 48s，STALE 才付费重跑 73s）；smoke 一条腿（面自洽 + 面板 sha1 移动报 STALE）。
2. 同一构造平移查 `etf_book_cadence_comparable` 的「格内带宽」：既然起跑日分布能翻符号，凡发布带宽的面都应报跨起跑日分布，而不是一个冬天内部的四分位。
3. 仍挂账的旧件：`Tools/money_rounding_gap_fix.py --apply`（r2126）、`etf_book_phase_atlas_k_axis` 接线（r2127）、`etf_book_cadence_comparable` 接线（r2128）。
