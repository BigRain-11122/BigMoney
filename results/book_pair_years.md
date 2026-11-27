# book_pair_years — 钱包的每一年：哪一年会考验你，30/70 扛不扛得住

面：`results/book_pair_years.json` ｜ 截止：**2026-11-26** ｜ 生成：2026-11-27T16:15:42+08:00

问题：which year tests the wallet, and does the 30/70 split hold in it?

## 读数

| 列 | 最差年 | 最好年 | 负年数 | 年平均 |
|---|---|---|---|---|
| 转债书 | -20.76% | +33.25% | 3 | +6.85% |
| ETF 书 | +0.86% | +42.47% | 0 | +10.24% |
| 30/70 组合 | -6.04% | +30.23% | 1 | +9.11% |

判词：**DIVERSIFICATION_CUSHIONS_CB_DOWN_YEARS**

> The split held through every bad year cb had (3 of 3: 2022, 2023, 2026), but etf lost nothing in any of the 7 years in this window, so the blend has never been tested against an etf down year -- that half of the defensive claim is open.

## 逐年（三列同一起点）

* 同一起点 = 该年三列中最后一列首个 bar 的那天。括号里是各列自己起点的原值，差值就是起点不同的代价。
* `†` 部分年：交易日不足整年的 95%，年化折算只为防误读，不是观测值。

| 年 | 起始 | 转债 | ETF | 30/70 | 组合比转债 | 组合比最好单书 |
|---|---|---|---|---|---|---|
| **2020** | 2020-01-06 | +9.96% (+10.76%) | +5.54% (+4.75%) | +7.29% (+7.29%) | -2.67pp | -2.67pp |
| **2021** | 2021-01-04 | +33.25% (+33.25%) | +5.17% (+5.17%) | +13.18% (+13.18%) | -20.07pp | -20.07pp |
| **2022** | 2022-01-04 | -4.87% (-4.87%) | +2.88% (+2.88%) | +0.71% (+0.71%) | +5.58pp | -2.17pp |
| **2023** | 2023-01-03 | -2.18% (-2.18%) | +2.38% (+2.38%) | +1.11% (+1.11%) | +3.29pp | -1.27pp |
| **2024** | 2024-01-02 | +27.79% (+27.79%) | +12.41% (+12.41%) | +17.31% (+17.31%) | -10.48pp | -10.48pp |
| **2025** | 2025-01-02 | +4.79% (+4.79%) | +42.47% (+42.47%) | +30.23% (+30.23%) | +25.45pp | -12.24pp |
| **2026** † | 2026-01-05 | -20.76% (-20.76%) | +0.86% (+0.86%) | -6.04% (-6.04%) | +14.71pp | -6.90pp |

### 部分年不能当整年读

* **2026**：217 个 bar（整年 242-243），到 2026-11-26 为止。组合 -6.04%，折算年化约 -6.77%——**这不是一年亏那么多**，是 10.7 个月的读数。

## 组合在转债书的坏年里

| 年 | 转债 | 30/70 | 补回来 |
|---|---|---|---|
| 2022 | -4.87% | +0.71% | +5.58pp |
| 2023 | -2.18% | +1.11% | +3.29pp |
| 2026 | -20.76% | -6.04% | +14.71pp |

## 起点不同的代价（为什么不能直接抄父面的逐年）

同年三列起点最大差落在 **2020**（起始 2020-01-06）：转债书由 +10.76% 变 +9.96%，差 -0.80pp——直接并排父面的逐年，读者会把这一天读成 0.8pp 的业绩。

## 口径（继承父面，不新造）

* **cb**：signal at close t, filled at close t+1
* **etf**：decide at close t, own from the open of t+1
* **same_cost_floor**：each parent already pays its own 10bp per side; the blend adds no rebalancing cost between books (not modelled -- a reader who moves money between them pays it)
* **ann_days**：244.0
* **overlap_assets**：the etf book keeps a convertible sleeve, so a few convertible ETFs sit in both wallets -- the correlation is not independent by construction and is not claimed to be

## 未验证（如实）

* the two sleeves' rebalancing cost between wallets is not modelled (each parent's own 10bp is inside its series)
* the overlap is 6.9 of cb's 19.4 years -- every number here is a recent-window number
* 30/70 is the blend face's in-sample best, not a law: this face inherits that optimism
* etf has no down year in this window, so the blend's behaviour inside an etf down year is unobserved

## 与父面的对账

`raw` 列必须逐字等于父面已发布的逐年（差异 ≤1e-6）；不一致=本面读的不是父面发布的那本书。本轮不一致 0 处。

