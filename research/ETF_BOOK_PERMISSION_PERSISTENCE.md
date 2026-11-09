# 削减能撑几个决策 bar

- 判定：**TRIM_ERASED_IN_ONE_CYCLE**
- 削减幅度（gap_k，来自 results/etf_book_cut_order_gap.json）：**-0.2251%**
- 票据 k=0.390822 ／ 许可 k=0.393073 ／ 最后一个决策 bar（2026-10-23）k=0.460253
- 面板末 bar：2026-11-06 ｜ β 目标 0.20 ｜ 市场腿 510300

## 一句话

A drop the size of the 11-11 trim (-0.23pp) is undone at the very next decision bar in half of the 22 historical events (median 1 bars); k moves 0.00pp in a typical step. The 445-lot trim is a per-bar constraint: unless the solver re-applies the floor every decision bar, the book is back over it twenty bars later.

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
| 上行步中 ≥ 削减幅度的步数 | 19 / 19 |
| 步长 ≥ 削减幅度的占比 | 100.00% |

## 削减寿命（回补到跌前水平需要几个决策 bar）

| 读数 | 值 |
|---|---|
| 同规模下跌事件 | 22 / 33 步（66.67%）
| 已回补 | 13 |
| 样本内未回补（censored，非 0） | 9 |
| 中位回补 bar 数 | 1 |
| 均值回补 bar 数 | 3.15 |
| 最长回补 bar 数 | 10 |

## 无同规模先例时的派生读数（算术期望，非模拟）

| 读数 | 值 |
|---|---|
| 样本内最大单步下跌 | 0.61% |
| slack / 均值上行步 | 0 决策 bar |
| slack / 中位步长 | 0 决策 bar |
| 口径 | slack / observed step; an expectation on the step law, not a simulation |

## 控制臂（本面量的排程必须是票据标的排程）

| 读数 | 值 |
|---|---|
| 排程末决策 bar k | 0.460253（2026-10-23） |
| 票据 k（2026-11-11） | 0.460253 |
| 差 | 0.0e+00 ｜ 复现=OK |

未回补的下跌日：2025-03-28, 2025-04-28, 2025-06-27, 2025-07-25, 2025-08-22, 2025-09-19, 2025-10-27, 2025-11-24, 2026-10-23

## 读法

- 回补口径=从跌后那一根起数到 k 重新 ≥ 跌前水平的决策 bar 数；结束时仍未回补的记 censored，写 0 会让削减看起来比实际更快被抹平。
- 许可的读取面（r1455 实读）：`permission_enforcers` = ['scripts/etf_book_ceo_page.py', 'scripts/etf_book_order.py']；本面不重算，直接引用。
- 本面只量「同一个 k 排程自己抹平一次削减有多快」，不评价 11-11 该不该减、也不改任何定量线。
