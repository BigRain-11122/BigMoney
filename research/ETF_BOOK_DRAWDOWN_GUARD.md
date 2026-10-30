# ETF 书：跌了怎么办（预置回撤响应规则的实测）

证据截止 **2026-10-30** · 面板 1652 根 bar · 本书口径 5 名 / beta 0.20 / 20 日换仓 / 8 bp

## 结论

**REJECT**。

四个决策日历 × 8 条规则，没有一条同时做到「回撤更浅」和「收益不掉」。跌的时候按预设阈值砍仓，在这本书上是花钱买安心，不是省钱。

而且要砍的那一刀多半砍不到：这本账**全窗最坏回撤只有 -6.93%**（beta 覆盖已经在做去杠杆），所以 8%/10%/15% 这三档「标准止损」整段历史一次都没触发过——它们是空规则，不是安全网。

判据（跑前冻结）：回撤改善的格数 ≥ 75%、收益不掉的格数 ≥ 75%、回撤中位改善 ≥ 1.0pp、收益中位代价 ≥ -0.25pp。

恒等控制：不干预的手臂与已发布引擎逐位一致（4 个日历，最大偏差 0）。

## 逐条规则（4 个决策日历合计）

| 规则 | 回撤中位改善 | 收益中位代价 | 夏普 | 回撤变浅的格 | 收益不掉的格 | 中位持仓 | 判词 |
|---|---|---|---|---|---|---|---|
| `linear:0.050` | +2.12pp | -3.10pp | -0.214 | 100% | 0% | 0.21 | **REJECT** |
| `linear:0.080` | +1.38pp | -1.98pp | -0.136 | 100% | 0% | 0.27 | **REJECT** |
| `linear:0.100` | +1.21pp | -1.59pp | -0.108 | 100% | 0% | 0.29 | **REJECT** |
| `linear:0.150` | +1.07pp | -1.04pp | -0.069 | 100% | 0% | 0.32 | **REJECT** |
| `switch:0.050` | +0.79pp | -5.31pp | -0.694 | 100% | 0% | 0.14 | **REJECT** |
| `switch:0.080` | +0.00pp | +0.00pp | +0.000 | 0% | 100% | 0.37 | **INERT** |
| `switch:0.100` | +0.00pp | +0.00pp | +0.000 | 0% | 100% | 0.37 | **INERT** |
| `switch:0.150` | +0.00pp | +0.00pp | +0.000 | 0% | 100% | 0.37 | **INERT** |

读法：回撤那一列是「比不干预浅多少」，正数才是变浅；收益那一列是代价，负数才是花钱。中位持仓 1.00 = 这条规则几乎从没动过手。

## 不干预时这本书自己是什么样（对照基线）

| 决策日历 | 年化 | 夏普 | 最大回撤 |
|---|---|---|---|
| mh126 | 6.54% | 1.06 | -6.91% |
| mh131 | 6.37% | 1.03 | -6.91% |
| mh136 | 6.41% | 1.04 | -6.93% |
| mh141 | 6.19% | 1.01 | -6.76% |

四个日历的年化落在 6.19%~6.54%（起点的 15 根 bar 之差不改结论），所以下面是整串历史，不是挑出来的一段。

## 为什么这条结论不能只跑一遍

同一个规则换一个决策日历（把 beta 表起点错开 0/5/10/15 根 bar），每一格都是一串不同的决策。只在其中一格赢的规则是运气，不是规则。

## 必须记住的

- one book (5 names, beta 0.20), one universe, one cost (8bp per unit traded); the guard is tested on this book's own return path, not on every published config
- the guard sees the book's own equity, which is what an operator sees; it never sees the market's next move
- cash left out of the book earns the observed repo rate, as in the published overlay
- a rule rejected here is rejected as a RETURN rule; it may still be worth having as a sleep-at-night rule, which this face does not price

*生成脚本 scripts/etf_book_drawdown_guard.py｜证据截止 2026-10-30*
