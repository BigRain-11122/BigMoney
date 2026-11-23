# VERIFIED_LINES_MONEY_YEAR

三本书、同一个年份轴、同一笔 100 万。生成 2026-11-23T18:04:16+08:00；证据截止 2026-11-20。

这不是第四条策略，也不是组合回测。三条线的成本口径、成交时点、票池都不同（10 / 8 / 1.5 bp 每边；次日开盘 vs 当日收盘 vs 调仓日等权；票池分别是 ETF、全 A 股、股指期货）。「每样三分之一」是三笔钱、每年一月初重新分配，不是一台引擎跑出来的组合。

## 一、逐年钱表（100 万，年初进、年末出）

| 年 | ETF复合书 | A股残差黑名单 | 期货carry | 三线等权（几条线在算） | 等权年末市值 |
|---|---|---|---|---|---|
| 2020 | +4.75% | -9.56%（未满年） | +12.18% | +2.46%（3 条） | 1,024,567 元 |
| 2021 | +6.15% | +27.85% | +7.58% | +13.86%（3 条） | 1,138,603 元 |
| 2022 | +3.15% | +2.50% | +6.62% | +4.09%（3 条） | 1,040,888 元 |
| 2023 | +2.78% | -1.38% | +4.42% | +1.94%（3 条） | 1,019,421 元 |
| 2024 | +12.44% | +11.10% | +5.52% | +9.68%（3 条） | 1,096,845 元 |
| 2025 | +42.42% | +60.83% | +10.46% | +37.90%（3 条） | 1,379,034 元 |
| 2026 | +2.87%（未满年） | -16.38%（未满年） | +6.19%（未满年） | -2.44%（3 条） | 975,570 元 |

## 二、它们有没有一起亏过

- 判过的年份：7 年（2020..2026）
- **三条线同时亏钱的年份：0 个**
- 三条线同时赚钱的年份：2021、2022、2024、2025
- 方向一致率：57.1%
- 7 个年份点算不出相关系数（样本太短）；这一行只回答「它们有没有一起亏过」，那才是把钱放进去的人真正感受到的事

## 三、每条线最差的一年（读者真正会在意的那一格）

- ETF bond-free composite (production candidate)：2023 年 +2.78%
- A-share residual veto (arm B: pool minus top 20% residual)：2026 年 -16.38%
- Index-futures basis carry, four arms equal weight：2023 年 +4.42%

三线等权最差一年：**2026 年 -2.44%**（100 万变成 975,570 元）
三线等权最好一年：**2025 年 +37.90%**（100 万变成 1,379,034 元）

## 四、每条线的口径（不可相加的原因写在这里）

### ETF bond-free composite (production candidate)

- 成本：10.0 bp / 边
- 成交：decide at close t, own from open t+1 (entry_lag=1)
- 票池：equity + commodity + convertible ETFs (no bond/money)
- 名数：5
- 网格：20；叠加：8% vol target, de-lever only
- 出处：scripts/etf_nobond_vt.py + scripts/etf_robust_pf.py::open_to_open_equity

### A-share residual veto (arm B: pool minus top 20% residual)

- 成本：8.0 bp / 边
- 成交：equal weight on the rebalance date's eligible pool
- 票池：A-share panel, 5,181 symbols, liquidity >= 20m CNY 20d
- 名数：whole eligible pool minus the top 20% residual names
- 网格：20；叠加：none
- 出处：scripts/astock_resid_veto_layer.py::run

### Index-futures basis carry, four arms equal weight

- 成本：1.5 bp / 边
- 成交：close-to-close on the daily bar
- 票池：IC/IM/IF/IH long futures
- 名数：4
- 网格：weights change only when the book re-sizes；叠加：none (margin account, see idx_fut_leverage_washout)
- 出处：scripts/idx_fut_carry_portfolio.py

## 五、结论

**THREE_LINES_NEVER_LOST_TOGETHER**

判读边界：①三条线窗口不同（ETF/A股 2020 起、carry 2017 起，本页只取 2020 起对齐）；②2026 年三条线都未满年（截止 2026-11-20）；③7 个年份点算不出相关系数，本页只报方向一致率；④A股残差线是 5,000+ 只等权，实盘要按流动性切；⑤carry 是保证金账户，单品种档位会爆仓（见 idx_fut_leverage_washout），本页的 carry 收益没有计追缴。
