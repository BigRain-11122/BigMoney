# 这本书缺了什么：死掉的基金

> 数据截止 2026-10-30｜判定 **HOLE_CANNOT_EXPLAIN_THE_EDGE**

the pool census already found 2 symbols that stop printing (0.12% of the eligible pool) and says the funds the source never served are invisible in every panel byte; priced off the panel's own 20-bar 1st percentile a death costs 19% of that position (1.6% of the book), so the book absorbs 45% of its held names dying every year before the 8.46% return is gone -- the residual hole is a ceiling on the tail, not the source of the return

## 1. 存量普查已经数过的那一半（引用，不重算）

`scripts/etf_pool_survival.py`（bm-c r1319）已经数过「面板里哪些符号停止打印」。本面不重做这份分类（两套阈值=同一个缺陷的第二份拷贝，E289），直接引用：

| 项 | 值 |
|---|---|
| 来源 | results\etf_pool_survival.json @ 2026-10-30 |
| 在册文件 / 可用池 | 1725 / 1661 |
| 停止打印（dead） | 2（占可用池 0.12%） |
| 仅滞后（stale） | 6 |
| 停止打印的符号 | sh512390, 510880_t73 |

普查自己就写清了它的边界：**funds the source never served (invisible in every panel byte)** 数不到。这句边界正是本面要定价的东西。
## 2. 窗口打开时能买的 vs 面板总数

| 项 | 值 |
|---|---|
| 面板总列数 | 1504 |
| 2020-01-01 已存在 | 193 |
| 窗口内才上市 | 1311（87.2%） |

## 3. 能看到的那一半：可交易性流失

流动性门 ¥2000 万（20 日中位成交额）下的真实流失：

| 项 | 值 |
|---|---|
| 窗口首日过门 | 67 |
| 截止日仍在门内 | 610 |
| 离开门并再没回来 | 18（占 2020 宇宙 26.9%） |
| 这些流失标的的中位实现收益 | 42.0% |

这是缺口的下限而不是全貌：**清盘的基金根本不在表里，所以数不到**。

## 4. 一次死亡值多少钱（从面板自己的尾巴读，不假设）

| 项 | 值 |
|---|---|
| 观测数（过门 × 20 bar） | 557599 |
| p0.1 | -29.5% |
| **p1（用作 LGD）** | **-18.9%** |
| p5 | -11.7% |
| 中位 | 0.1% |

## 5. 敞口与死亡预算

| 项 | 值 |
|---|---|
| 手臂 | declared fill (score held one bar back, close t -> open t+1), vol target 8% |
| 年化 / 夏普 / 回撤 | 8.46% / 0.87 / -16.6% |
| 决策次数 / 每次换手 | 1652 / 0.953 |
| 每年持有的名-年 | 12.0（= 12 名 × 每年 252 次 × 20 bar） |
| 单名权重 | 0.083 |

每次再平衡持 12 名、跑 20 bar，所以跑一年正好是 12 个名-年；一次死亡损失 LGD×(1/12) 的账面，于是**年化拖累 = 每年每名死亡次数 × LGD**，与持几名无关。

| 假设每年每名死亡 | 年化拖累 | 拖累后 CAGR |
|---|---|---|
| 0.5% | 0.09pp | 8.37% |
| 1.0% | 0.19pp | 8.27% |
| 2.0% | 0.38pp | 8.08% |
| 5.0% | 0.94pp | 7.52% |
| 10.0% | 1.89pp | 6.57% |

**打平死亡率 = 44.8% 每年每名**（超过 100% = 每一年持仓全部死一遍）。

## 6. 判定与它不解决的问题

判定：**HOLE_CANNOT_EXPLAIN_THE_EDGE**。

这个面能把缺口定成预算，不能把它定成事实：面板里没有死亡样本，所以真实的清盘率来自面板外部（这里没有引用任何外部数字，也不编）。它给出的是一句话——「本书要被打平，需要每年持仓的 45% 全部清盘」，读者可以拿任何自己相信的清盘率去对这条线。

它同时给出两条正向读法：①死亡只压尾巴、不改均值——本书是横截面 top-12 相对排名，差基金进不了排名前列，所以「多了一个死基金」几乎不改变选股；②真正被高估的是**持有期内发生的死亡**，而持有期只有 20 个交易日，暴露窗很短。

## 复跑

```
python scripts/etf_book_survivorship_hole.py run
python scripts/etf_book_survivorship_hole.py --check
python scripts/etf_book_survivorship_hole.py --selftest
```
