# 2020 年能不能真的跑这本书？——窗口收益落在哪个票池上

证据件：`results/etf_book_universe_lock.json`（evidence cutoff 2026-10-30，4 个决策相位，58.5s）。

## 为什么问这一句

本线对外印的两个数（as coded 9.60%、declared fill 8.46%）都是在**今天**的 1504 只基金上算出来的。这些基金里约三分之一在窗口开始时还不存在；今天真正在手的 12 个名字里 **11 个**在 2019-12-31 之后才上市。

所以这些数字回答的是一个没人能执行的问题：「假如 2020 年就能买到后面才上市的基金」。这一轮把同一格规则放到冻结在那一天的票池上重跑。

## 结果（declared fill，四个决策相位）

| 相位 | 起点 | 全票池 1504 只 | 锁定 2019-12-31（193 只） | 差额 |
|---|---|---|---|---|
| 0 | 2020-01-02 | 8.46% | 7.96% | +0.50 pp |
| 1 | 2020-01-09 | 7.94% | 7.04% | +0.90 pp |
| 2 | 2020-01-16 | 8.09% | 7.29% | +0.80 pp |
| 3 | 2020-01-23 | 5.93% | 8.17% | -2.24 pp |

**MIXED_ACROSS_PHASES**：平均差额 -0.01 pp/年（2/4 个相位达到 0.57 pp 的material线，最差 -2.24、最好 +0.90）。

怎么读这一句：三个相位说冻结要花掉 0.5–0.9 pp（在material线附近或之上），第四个相位反过来说冻结多赚 2.2 pp——**平均为零，而跨相位的摆幅比这条线测过的任何一个效应都大**。所以正确的对外说法不是「窗口收益靠新基金」，也不是「完全无关」，而是：**选券依赖的是「票池要够宽」，不是「票池要够新」**；这条依赖在下面那张梯子上才看得见（61 只的 2015 年票池只有 5.35%）。

同一臂上的对照（把票池一路放宽）：

| 票池锁定日 | 基金数 | 年化 | 夏普 | 最大回撤 | 已实现波动 |
|---|---|---|---|---|---|
| unlocked | 1504 | 8.46% | 0.874 | -16.56% | 10.28% |
| 2014-12-31 | 61 | 5.35% | 0.576 | -19.52% | 10.36% |
| 2019-12-31 | 193 | 7.96% | 0.837 | -16.05% | 10.14% |
| 2022-12-31 | 663 | 8.98% | 0.907 | -16.56% | 10.49% |

## 手里的书

在手的这一本（决策日 2026-10-14）：159501、159263、159307、513690、159547、159207、515100、513100、159696、159659、513630、563020。

其中 **11/12** 在 2019-12-31 之后才上市（159207 2025-04-09；159263 2025-07-08；159307 2024-04-25；159501 2023-06-14；159547 2024-02-06；159659 2023-04-25；159696 2023-08-25；513100 2013-07-31；513630 2023-12-08；513690 2021-05-20；515100 2020-07-03；563020 2023-12-14）。整个窗口 996 个决策持仓位里有 374 个（37.5%）落在这类「窗口内新上市」的名字上。

## 控制闸

引用任何锁定数之前，本面先用同一引擎复现卡片公开的两条臂：

- as_coded：发布 0.0960 / 本面重算 0.0960（差 0.00 pp，容差 0.5 pp）→ PASS
- declared：发布 0.0846 / 本面重算 0.0846（差 0.00 pp，容差 0.5 pp）→ PASS

## 边界

- locked arms rebuild the score on their own universe; every other knob (n_hold/rebal/cost/vol target/vol window/engine/fill) is identical
- the lock test is 'first valid bar on or before the lock date' on the panel the book is priced on, so a fund whose history starts after the lock cannot be held
- survivorship is still in: funds that existed in 2020 and were later delisted are absent from the panel, so the locked arm is an upper bound on what was available
- the pick census counts decision slots, not money-weighted exposure: a name held for two years counts once per decision it appears in

复现：

```
python scripts/etf_book_universe_lock.py run        # ~58s
python scripts/etf_book_universe_lock.py --check
python scripts/etf_book_universe_lock.py --selftest
```
