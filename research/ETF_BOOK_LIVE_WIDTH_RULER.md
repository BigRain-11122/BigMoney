# 两个活宽度放同一把尺子（r1356 bm-c）

面：`results/etf_book_live_width_ruler.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --live-widths`｜源面：`results/etf_book_phase_atlas.json` + `results/etf_capacity_frontier.json` + `results/etf_book_order/TICKET-*.json`｜cutoff 2026-10-29

生产卡跑 12 名（vol_target），可执行单跑 5 名（beta），都是 R20。

| 面 | 名数 | 规则 | 中位 CAGR | 本格 band | 相位 |
|---|---|---|---|---|---|
| card | 12 | vol_target | +9.64pp | 7.87pp | 20 |
| ticket | 5 | beta | +9.13pp | 6.25pp | 20 |

## 一、逐相位配对（同一台引擎、同一批 20 个决策起点）

中位差 **+0.090pp**，均值 +0.129pp，区间 -2.050..+2.890pp（跨度 4.940，sd 1.255），方向 10 上 / 10 下。

**聚合假象**：阶梯上的这一格是「两个中位数相减」= +0.515pp，同一件事按逐相位配对取中位数 = +0.090pp —— 差的 0.425pp（83%）是聚合方式，不是书。

## 二、两台引擎在同一级上的分歧（唯一可比的量：差减差）

| 引擎 | 5 -> 12 这一级 |
|---|---|
| atlas（相位图，vol 规则） | +0.515pp |
| capacity（容量面，自有宇宙） | -1.530pp |

分歧 **2.045pp**，符号相反 = True。两面对同一条阶梯连方向都不一致，所以这一级本身不可裁决。

同宽度的**水平差**（N12 4.38pp, N5 6.43pp）只作披露、不作判据：水平差与「级差」不是同一个单位，拿 6pp 的水平差去卡 0.1pp 的级差就是 r1292 那一族。

## 三、两张面「照发出去的样子」（同时动了两个旋钮，不是宽度）

| 规则 \ 名数 | 5 | 12 |
|---|---|---|
| beta | +11.33pp | +9.80pp |
| vol | +12.19pp | +12.51pp |

对角差 +1.18pp，但宽度效应在 beta 规则下是 -1.53pp、在 vol 规则下是 +0.32pp，交互项 +1.85pp 大于任一主效应。两条分解路径分别得 +1.18 / +1.18（一致 = True）。

> 巧合而告：the beta-rule width effect (-1.530pp) equals the capacity engine's 5->12 rung (-1.530pp) to the basis point. They are different quantities on different windows -- one is a live 2x2 cell difference, the other a second engine's rung. Recording the collision so nobody reads it as confirmation


Verdict: **COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT**

- 20 paired phases of one R20 cycle (need >= 20)
- paired gap +0.090pp (median of 20 phase differences; range -2.050..+2.890, sd 1.255)
- direction splits 10/10 (sign agreement 0.500; floor 0.60)
- the same rung costs +0.515pp on the atlas engine and -1.530pp on the capacity engine, a disagreement of 2.045pp with the sign flipping = True
- difference of medians +0.515pp vs median of differences +0.090pp: the ladder's rung is 83% aggregation
- gap is 4.4% of the engine disagreement and 1.3% of the atlas ruler 6.68pp
- the two live widths are not separated by their own phases AND the engine disagreement on the same rung is wider than the gap: no part of the difference between card and ticket is quotable as a width effect
- as issued the two faces print 12.51pp vs 11.33pp (+1.18pp diagonal), but the 2x2 moves two knobs at once: width effect -1.53pp under the beta rule and +0.32pp under the vol rule, with an interaction of +1.85pp (bigger than both width effects = True)
- COINCIDENCE, not agreement: the beta-rule width effect (-1.530pp) equals the capacity engine's 5->12 rung (-1.530pp) to the basis point. They are different quantities on different windows -- one is a live 2x2 cell difference, the other a second engine's rung. Recording the collision so nobody reads it as confirmation
