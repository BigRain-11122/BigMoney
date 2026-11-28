# 袖级溢价：第二个尺子

**问题**：Does 'the cb sleeve is expensive' mean the same thing on the market's median premium as on the premium of the 20 bonds the sleeve actually holds?

## 为什么要有这把尺

r2183 把 30/70 的缓冲按**全市场**转债溢价中位数的分档切开，r2184 又把那个标签变成一条会下单的决定（标签 rich 时袖收现金）。可是这只袖不是市场：双低规则买的是`收盘价 + 转股溢价` 最小的 20 只，天然压在溢价分布的下端。市场口径的「贵」，对自己手里的 20 只可能只是平常一个月——若如此，页面会叫我们把一只并不贵的袖换成现金。

## 口径（parents imported, not rebuilt）

- 袖成员：`cb_dual_low._eligible` 同一套过滤（价 80~200、剔深度实值）+ 同一打分式（`close + conv_premium.fillna(50)`，取最小 20）+ 同一调仓网格（rebal=20/phase=0，信号在 t−1）
- 袖读数：当日所持券 `conv_premium` 的中位数；覆盖率低于 80% 的月份直接丢掉，不补值（缺读数不是零溢价）
- 两把尺的标签机械完全相同（各自历史的扩张窗三分位、只在上一月末读数、≥250 读数），差别只有尺本身；另加一把**近三年滚动窗**尺（750 读数），因为扩张窗对结构性下行的序列永远不会喊贵，两臂的「现金月数」不可直接相比
- 权重、cb/etf 两腿、成本、bootstrap 全部从父面 import（`book_pair_cushion_regime`）

## 读数

| 尺 | 现金月数 | 规则 CAGR | 规则夏普 | 规则 MDD | 一直持有夏普 | 每月边缘 | 区间 | 判词 |
|---|---|---|---|---|---|---|---|---|
| 市场口径 | 46/81 | 10.0% | +1.39 | -4.4% | +1.23 | +0.14 pp | +0.02 .. +0.27 | THE_RULE_BEATS_ITS_OWN_EXPOSURE |
| 袖自己的 20 只 | 3/81 | 9.4% | +1.25 | -7.9% | +1.23 | +0.01 pp | -0.03 .. +0.04 | RULE_EDGE_NOT_SEPARABLE_FROM_NOISE |
| 袖·近三年窗 | 28/81 | 9.3% | +1.26 | -6.6% | +1.23 | +0.05 pp | -0.06 .. +0.16 | RULE_EDGE_NOT_SEPARABLE_FROM_NOISE |

标签一致率（对市场尺）：袖自己 **28.4%**（同桶 23/81 月；市场说贵而袖不贵 **43** 个月，袖说贵而市场不贵 **0** 个月）；袖·近三年窗 **37.0%**。

今天：市场口径滞后标签 rich，当日读数 65.61%（自己的贵线 32.66%）；袖口径滞后标签 rich，当日读数 11.42%（自己的贵线 15.23%）。标签同向=True，**当日读数同向=False**。

## 判词的边界

- membership is rebuilt from the parent's pick formula, not read from the parent's holdings -- the parent does not publish them, so a formula change on its side would move this face without either side failing
- the sleeve's own premium jumps at rebalances (a pick turns over half the 20 bonds), so part of its month-end reading is 'which bonds we happen to hold', not only 'how expensive they are' -- the coverage gate cannot see that
- the sleeve ruler still has only one premium cycle in it (81 labelled months); a second cycle is what would tell us whether the two rulers converge in a genuinely cheap market
- an expanding-window tertile cannot call a structurally falling series rich: the sleeve reads rich in 3 of 81 months and the market in 46, so the two arms do not fire equally often -- the recent-window arm is published beside them for that reason, not as a tiebreak
- premium on a held bond can be stale on its last quoted day; the coverage gate drops a month below 80% coverage, it does not correct the rest
- the rule is priced on monthly switches only; intra-month runs are not modelled
- the cb arm and the etf arm are the parents' published arms -- this face does not re-test them

复跑：`python scripts/book_pair_sleeve_premium.py`（写入三件）／`check` 只判不写。
