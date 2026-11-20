# 两个活宽度放同一把尺子（r1356 bm-c）

面：`results/etf_book_live_width_ruler.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --live-widths`｜源面：`results/etf_book_phase_atlas.json` + `results/etf_capacity_frontier.json` + `results/etf_book_order/TICKET-*.json`｜cutoff 2026-11-20

生产卡跑 12 名（vol_target），可执行单跑 5 名（beta），都是 R20。

| 面 | 名数 | 规则 | 中位 CAGR | 本格 band | 相位 |
|---|---|---|---|---|---|
| card | 12 | vol_target | +9.19pp | 7.32pp | 20 |
| ticket | 5 | beta | +9.07pp | 6.49pp | 20 |

## 一、逐相位配对（同一台引擎、同一批 20 个决策起点）

中位差 **+0.030pp**，均值 +0.177pp，区间 -2.000..+2.830pp（跨度 4.830，sd 1.276），方向 10 上 / 10 下。

**这把尺子自己的分辨下限**：20 个相位、逐相位差 sd 1.276pp，在 80% 功效（双侧 5%）下能分辨的最小差值 = **0.799pp**；本次 +0.030pp 是它下限的 4% —— 低于自己的分辨下限：所以「两者没差别」也不是结论，结论是这把尺子分不开。

**聚合假象**：阶梯上的这一格是「两个中位数相减」= +0.115pp，同一件事按逐相位配对取中位数 = +0.030pp —— 差的 0.085pp（74%）是聚合方式，不是书。

## 二、两台引擎在同一级上的分歧（唯一可比的量：差减差）

| 引擎 | 5 -> 12 这一级 |
|---|---|
| atlas（相位图，vol 规则） | +0.115pp |
| capacity（容量面，自有宇宙） | -1.530pp |

分歧 **1.645pp**，符号相反 = True。两面对同一条阶梯连方向都不一致，所以这一级本身不可裁决。

同宽度的**水平差**（N12 4.84pp, N5 6.49pp）只作披露、不作判据：水平差与「级差」不是同一个单位，拿 6pp 的水平差去卡 0.1pp 的级差就是 r1292 那一族。

## 三、两张面「照发出去的样子」（同时动了两个旋钮，不是宽度）

| 规则 \ 名数 | 5 | 12 |
|---|---|---|
| beta | +10.38pp | +9.10pp |
| vol | +10.73pp | +11.13pp |

对角差 +0.75pp，但宽度效应在 beta 规则下是 -1.28pp、在 vol 规则下是 +0.40pp，交互项 +1.68pp 大于任一主效应。两条分解路径分别得 +0.75 / +0.75（一致 = True）。


Verdict: **COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT**

- 20 paired phases of one R20 cycle (need >= 20)
- paired gap +0.030pp (median of 20 phase differences; range -2.000..+2.830, sd 1.276)
- direction splits 10/10 (sign agreement 0.500; floor 0.60)
- the same rung costs +0.115pp on the atlas engine and -1.530pp on the capacity engine, a disagreement of 1.645pp with the sign flipping = True
- difference of medians +0.115pp vs median of differences +0.030pp: the ladder's rung is 74% aggregation
- gap is 1.8% of the engine disagreement and 0.4% of the atlas ruler 6.80pp
- this pairing's own resolution is 0.799pp at 80% power (20 phases, sd 1.276), so a gap of +0.030pp is 4% of what it could have detected -- below its own ruler, so 'no difference' is not the finding either
- the two live widths are not separated by their own phases AND the engine disagreement on the same rung is wider than the gap: no part of the difference between card and ticket is quotable as a width effect
- as issued the two faces print 11.13pp vs 10.38pp (+0.75pp diagonal), but the 2x2 moves two knobs at once: width effect -1.28pp under the beta rule and +0.40pp under the vol rule, with an interaction of +1.68pp (bigger than both width effects = True)
