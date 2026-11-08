# 削减能撑几个决策 bar

- 判定：**NO_TRIM_SIZED_DROPS_IN_HISTORY**
- 削减幅度（gap_k，来自 results/etf_book_cut_order_gap.json）：**6.7180%**
- 票据 k=0.460253 ／ 许可 k=0.393073 ／ 最后一个决策 bar（2026-10-23）k=0.460253
- 面板末 bar：2026-11-06 ｜ β 目标 0.20 ｜ 市场腿 510300

## 一句话

No historical decision bar dropped k by as much as the 6.72pp trim (largest drop in 33 same-window steps was 0.61pp), so the record never tested whether such a cut holds; on the observed step law it takes about 10 upward steps of 0.69pp (mean) / 22 steps of 0.31pp (median) to walk the slack back -- but the largest single upward step (6.76pp over 19 up-steps) exceeds the whole cut, so the trim can be erased in one decision bar; walking it back at the mean step takes 10 bars. Nothing in the schedule remembers the floor, so it has to be re-applied every decision bar.

## k 的步伐（相邻决策 bar 差）

| 读数 | 值 |
|---|---|
| 步数 | 33 |
| 中位 \|Δk\| | 0.003071 |
| 均值 \|Δk\| | 0.004965 |
| p90 \|Δk\| | 0.006055 |
| 最大 \|Δk\| | 0.067573 |
| 上行步数 | 19 |
| 上行步均值 | 0.006851 |
| 最大单步上行 | 0.067573 |
| 上行步中 ≥ 削减幅度的步数 | 1 / 19 |
| 步长 ≥ 削减幅度的占比 | 3.03% |

## 削减寿命（回补到跌前水平需要几个决策 bar）

| 读数 | 值 |
|---|---|
| 同规模下跌事件 | 0 / 33 步（0.00%）
| 已回补 | 0 |
| 样本内未回补（censored，非 0） | 0 |
| 中位回补 bar 数 | — |
| 均值回补 bar 数 | — |
| 最长回补 bar 数 | — |

## 无同规模先例时的派生读数（算术期望，非模拟）

| 读数 | 值 |
|---|---|
| 样本内最大单步下跌 | 0.61% |
| slack / 均值上行步 | 10 决策 bar |
| slack / 中位步长 | 22 决策 bar |
| 口径 | slack / observed step; an expectation on the step law, not a simulation |

## 控制臂（本面量的排程必须是票据标的排程）

| 读数 | 值 |
|---|---|
| 排程末决策 bar k | 0.460253（2026-10-23） |
| 票据 k（2026-11-11） | 0.460253 |
| 差 | 0.0e+00 ｜ 复现=OK |

## 读法

- 回补口径=从跌后那一根起数到 k 重新 ≥ 跌前水平的决策 bar 数；结束时仍未回补的记 censored，写 0 会让削减看起来比实际更快被抹平。
- 许可的读取面（r1455 实读）：`permission_enforcers` = ['scripts/etf_book_order.py']；本面不重算，直接引用。
- 本面只量「同一个 k 排程自己抹平一次削减有多快」，不评价 11-11 该不该减、也不改任何定量线。
