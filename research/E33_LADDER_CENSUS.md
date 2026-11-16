# 五只宽基等权 vs 510300：算完了没人读的 15 张面

> 数据截止 2026-10-20｜源 `results/e33_ladder_baseline/`（15 张面，只读聚合，零重算）

## 一句话

- **LADDER_WINS_NOT_SEPARABLE**：FULL window ladder +187.9bp/yr over 510300, monthly t=0.83 (< 2.0), and the start windows do not agree: 2016 -35.6bp, 2018 +640.0bp, FULL +187.9bp
- **SLOWER_CLOCK_WINS**：annual 6.19% vs monthly 5.27% = +92.0bp/yr, while annual's own commission is 2.9bp/yr
- **EDGE_IS_HINDSIGHT**：frozen five (quarterly) 5.74%/yr vs the same ladder built from a causal top-5-by-traded-value pick 0.64%/yr -- the rule keeps 11% of the book

## Q1 阶梯等权 vs 510300 买入持有

| 起点 | 成本 | 阶梯年化 | 夏普 | 510300 年化 | 夏普 | 超额(bp/年) | 月度均值(bp) | t |
|---|---|---|---|---|---|---|---|---|
| 2016-11-01 -> today | x1 | +1.84% | 0.191 | +2.29% | 0.215 | -35.6 | -0.5 | -0.02 |
| 2018-01-02 -> today | x1 | +5.48% | 0.370 | +0.18% | 0.107 | +640.0 | +45.4 | 1.61 |
| 2018-01-02 -> today | x3 | +5.39% | 0.366 | +0.18% | 0.107 | +632.1 | +44.8 | 1.59 |
| 2012-05-28 -> today | x1 | +5.27% | 0.347 | +3.43% | 0.263 | +187.9 | +18.3 | 0.83 |
| 2012-05-28 -> today | x3 | +5.19% | 0.343 | +3.43% | 0.263 | +179.8 | +17.6 | 0.80 |

按年代拆开（FULL 窗口，月度超额）：

- 2017-2020：-26.2bp/月（48 个月）
- 2021-2023：+28.8bp/月（36 个月）
- 2024-now：+29.9bp/月（34 个月）
- pre2017：+42.6bp/月（56 个月）

## Q2 多久调一次仓

| 节奏 | 年化 | 夏普 | 自身成本(bp/年) | 调仓次数 | 相对月度(bp/年) |
|---|---|---|---|---|---|
| annual | +6.19% | 0.385 | 2.9 | 13 | +92.0 |
| semiannual | +5.66% | 0.364 | 3.2 | 27 | +37.7 |
| quarterly | +5.74% | 0.367 | 3.5 | 54 | +45.8 |
| monthly | +5.27% | 0.347 | 4.2 | 160 | — |

## Q3 这五只是「选出来的」还是「事后知道的」

同一套规则（等权、按节奏调仓）换成**因果能选出来的前 5 只**（按成交额）：

| 方案 | 年化 | 夏普 | 成本(bp/年) |
|---|---|---|---|
| frozen5_monthly | +5.27% | 0.347 | 4.2 |
| frozen5_quarterly | +5.74% | 0.367 | 3.5 |
| top5_monthly | -0.23% | 0.035 | 17.4 |
| top5_quarterly | +0.64% | 0.114 | 13.4 |
| top5eq_monthly | +1.44% | 0.174 | 20.9 |
| top5eq_quarterly | +1.40% | 0.173 | 14.4 |

2018 起点复核（同一比较）：frozen5_monthly +5.48%；frozen5_quarterly +2.73%；top5_monthly -1.34%；top5_quarterly -0.46%；top5eq_monthly -2.20%；top5eq_quarterly -2.27%

## 怎么读

- 阶梯确实赢了指数，但**赢的量级在月度上分辨不出来**，而且从 2016 起算它是输的。
- 调仓越慢越好，不是因为省手续费（年度自身成本只有几个 bp），而是月度再平衡在不断把赢家换掉。
- 最关键的一条：同样规则换成人能提前选出来的前 5 只，收益几乎归零——这五只的年化里大部分是**事后才知道它们好**，不是规则能复现的能力。

## 诚实边界

- read-only over results/e33_ladder_baseline/*.json -- every number is the study's own; nothing is recomputed here
- the five funds are today's listings (survivorship); Q3 exists precisely to price that, and it says the causal rule cannot pick them
- monthly t is the study's own figure; this census only applies a frozen threshold to it
- no trial count is consumed and no gate is opened by this face
