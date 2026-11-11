# 换仓日历该判哪一本书 —— 2026-11-10

> 问题：日历判**被审书**（nobond_vt08，书内 8% 波动目标）还是判**在跑的书**（beta 0.20，无波动目标）。本页只量，不猜。

## 结论

**PHASE_OFFSET** —— the two books tick on different dates, but by a single constant offset of 13 session(s) -- one rule with two phases, not two rules。

| 书 | 网格（20 根） | 决策日数 | 可被官方日历核实 | 最新规模 |
|---|---|---|---|---|
| 在跑的书（beta 0.20） | 相位 7 | 77 | 77 | k=0.460253 |
| 被审书（vt8.00） | 相位 0 | 83 | 83 | scale=0.696219 |

共同决策日 **0** 天；仅在跑书 **77** 天；仅被审书 **83** 天；恒定相位差 **13** 根。

## 下一个换仓日

面板最后一根 **2026-11-10**。

- 在跑的书：最近决策 2026-10-23，下一网格 bar **2026-11-20**
- 被审书：最近决策 2026-10-14，下一网格 bar **2026-11-11**

## 钱（同一根 bar 上两本书的规模差）

读在 **2026-11-10** 这根 bar 上。

| 书 | 规模 | 投入（NAV 1,000,000） |
|---|---|---|
| 在跑的书 | k=0.460253 | ￥460,253 |
| 被审书 | scale=0.696219 | ￥696,219 |

差额 **￥235,965**（235965.85 CNY less than the audited book on the same bar）。

## 页面印的那个决策 bar 属于哪本书

- 页面决策 bar：**读不到**（读取状态：malformed）
- 在跑的书网格：未核实；被审书网格：未核实

**UNKNOWN** —— the page's decision bar could not be read; the calendar question is not answered by guessing。

## 读法（三条判据）

1. 决策日由各自的既有实现产生（`etf_book_order.k_schedule` / `etf_robust_pf.open_to_open_equity(diag=...)`），本面无第二份网格实现。
2. 每个决策日都对官方日历核实；不在日历上的日期点名为不可读，不重编号。
3. 判决由两个日期集派生（SAME_GRID / PHASE_OFFSET / DIVERGENT / ONE_SIDED），`check` 重算臂比对数量与金额，手改即红。

## 边界

- 只读已发布引擎与面板，不改 target、不改票面、不改账本。
- 两本书的规模字段语义可并置（都是「投入资金比例」），但**不是**同一条规则；本页回答的是日历，规模差异的采纳走各自的预注册与转仓日决策。
- 面板为现存 ETF（幸存者偏差），起点由各引擎历史窗决定，前段不可比属正常。
