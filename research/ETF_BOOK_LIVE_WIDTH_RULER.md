# 两个活宽度放同一把尺子（r1356 bm-c）

面：`results/etf_book_live_width_ruler.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --live-widths`｜源面：`results/etf_book_phase_atlas.json` + `results/etf_capacity_frontier.json` + `results/etf_book_order/TICKET-*.json`｜cutoff 2026-11-17

生产卡跑 12 名（vol_target），可执行单跑 5 名（beta），都是 R20。

| 面 | 名数 | 规则 | 中位 CAGR | 本格 band | 相位 |
|---|---|---|---|---|---|
| card | 12 | vol_target | +9.43pp | 7.45pp | 20 |
| ticket | 5 | beta | +8.87pp | 6.40pp | 20 |

## 一、逐相位配对（同一台引擎、同一批 20 个决策起点）

中位差 **+0.315pp**，均值 +0.222pp，区间 -3.270..+2.870pp（跨度 6.140，sd 1.567），方向 11 上 / 9 下。

**这把尺子自己的分辨下限**：20 个相位、逐相位差 sd 1.567pp，在 80% 功效（双侧 5%）下能分辨的最小差值 = **0.982pp**；本次 +0.315pp 是它下限的 32% —— 低于自己的分辨下限：所以「两者没差别」也不是结论，结论是这把尺子分不开。

**聚合假象**：阶梯上的这一格是「两个中位数相减」= +0.565pp，同一件事按逐相位配对取中位数 = +0.315pp —— 差的 0.250pp（44%）是聚合方式，不是书。

## 二、两台引擎在同一级上的分歧（唯一可比的量：差减差）

| 引擎 | 5 -> 12 这一级 |
|---|---|
| atlas（相位图，vol 规则） | +0.565pp |
| capacity（容量面，自有宇宙） | -1.530pp |

分歧 **2.095pp**，符号相反 = True。两面对同一条阶梯连方向都不一致，所以这一级本身不可裁决。

同宽度的**水平差**（N12 4.60pp, N5 6.70pp）只作披露、不作判据：水平差与「级差」不是同一个单位，拿 6pp 的水平差去卡 0.1pp 的级差就是 r1292 那一族。

## 三、两张面「照发出去的样子」（同时动了两个旋钮，不是宽度）

| 规则 \ 名数 | 5 | 12 |
|---|---|---|
| beta | +10.89pp | +9.52pp |
| vol | +11.57pp | +12.04pp |

对角差 +1.15pp，但宽度效应在 beta 规则下是 -1.37pp、在 vol 规则下是 +0.47pp，交互项 +1.84pp 大于任一主效应。两条分解路径分别得 +1.15 / +1.15（一致 = True）。


Verdict: **COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT**

- 20 paired phases of one R20 cycle (need >= 20)
- paired gap +0.315pp (median of 20 phase differences; range -3.270..+2.870, sd 1.567)
- direction splits 11/9 (sign agreement 0.550; floor 0.60)
- the same rung costs +0.565pp on the atlas engine and -1.530pp on the capacity engine, a disagreement of 2.095pp with the sign flipping = True
- difference of medians +0.565pp vs median of differences +0.315pp: the ladder's rung is 44% aggregation
- gap is 15.0% of the engine disagreement and 4.4% of the atlas ruler 7.12pp
- this pairing's own resolution is 0.982pp at 80% power (20 phases, sd 1.567), so a gap of +0.315pp is 32% of what it could have detected -- below its own ruler, so 'no difference' is not the finding either
- the two live widths are not separated by their own phases AND the engine disagreement on the same rung is wider than the gap: no part of the difference between card and ticket is quotable as a width effect
- as issued the two faces print 12.04pp vs 10.89pp (+1.15pp diagonal), but the 2x2 moves two knobs at once: width effect -1.37pp under the beta rule and +0.47pp under the vol rule, with an interaction of +1.84pp (bigger than both width effects = True)
