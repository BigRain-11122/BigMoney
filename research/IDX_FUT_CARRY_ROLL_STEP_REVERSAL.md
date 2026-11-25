# 移仓日到底算不算 carry —— 一次会计裁决（IC/IM · cutoff 2026-11-24）

generated 2026-11-25T18:2x+08:00 · r2096 bm-c · 工具 `scripts/idx_fut_carry_roll_step_reversal.py`
· 面 `results/idx_fut_carry_roll_step_reversal.json` · selftest 12/12

## 为什么做这个

三个面连着发了三轮，全建立在一个**从未验证的前提**上：

| 面 | 判词 | 隐含前提 |
|---|---|---|
| `bench_basis_timing_size_masks` | SIZING_EDGE_IS_A_MASK_ARTIFACT | 置 0 的移仓日不产生收益 |
| `idx_fut_carry_always_on_price` | PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND | 同上（只报区间，不裁） |
| `idx_fut_carry_capacity_lots` | MARKET_IS_NOT_THE_GATE | 同上 |

`carry_curve` 写的是 `np.where(roll, 0.0, w*spread)`：移仓日既不记收益也不记成本。
如果那天的 spread 只是连续合约拼接两价格的**账面跳空**，置 0 正确；如果那是这本书每月
真付的**账单**，置 0 就是在删成本。两种答案把同一本书定价成 2.73%/年 或 9.62%/年。

## 怎么判（跑之前冻结）

账面跳空是一次性重定价：两条腿之后恢复常态关系，所以**次日应当回吐**。真实成本没有
回吐的理由：下月合约就是更贵，贴水继续更深。

1. **回吐检验**：`T = 移仓日次日 spread 均值 − 非移仓日 spread 均值`（年化 pp），
   `give = −次日均值 / 移仓日均值`。置换 5,000 次（随机非移仓日）。
2. **后付检验**（决定性）：移仓日**后 8 天**均值 − **前 8 天**均值。若后段显著更负，
   说明账单已由后续每日 carry 支付，则置 0 是正确会计。零分布=符号翻转 5,000 次
   （配对，不从别的日子抽样——台阶后的日子本身被位移，跨样本会污染零分布）。

判据：`BOOKKEEPING_JUMP`（give≥0.5 且 p<0.01）／`COST_BOOKED_BY_LATER_CARRY`
（后前差 ≤ −2pp 且 p<0.05）／`REAL_COST`／`PARTIAL_REVERSAL`／`DATA_BLOCKED`。

## 读数

| 产品/尺子 | 移仓日数 | 回吐比 give | 次日超额 T | p | 后 8 日 − 前 8 日 | p | 判决 |
|---|---|---|---|---|---|---|---|
| IC / calendar | 118 | 0.170 | +21.69pp | 0.0026 | **−3.96pp** | 0.026 | COST_BOOKED_BY_LATER_CARRY |
| IC / strictest | 128 | 0.159 | +17.32pp | 0.0024 | **−5.29pp** | 0.030 | COST_BOOKED_BY_LATER_CARRY |
| IM / calendar | 51 | 0.218 | +38.01pp | 0.0020 | −1.76pp | 0.607 | PARTIAL_REVERSAL |
| IM / strictest | 60 | 0.073 | +1.89pp | 0.4213 | −5.57pp | 0.252 | REAL_COST |
| IC/IM / published | 22/18 | — | — | — | — | — | DATA_BLOCKED（<30 对） |

## 结论

**IC：移仓日的台阶既不是当日收益，也不是当日成本——它是价格的永久下移，账单由之后每一天
更深的贴水逐日支付。** 两条腿互相印证：回吐只有 16-17%（不是"次日还回来"的记账假象），
而后 8 天比前 8 天低 3.96/5.29pp/年（p=0.026/0.030，账单确实后付）。

因此 `np.where(roll, 0.0, …)` 是**有证据支持的会计处理**，不是随手写法：
- 把移仓日放进 spread 的 published 口径（2.73% 那一路），等于把一次合约切换的账面跳空
  当成一天的可实现收益——这是错的；
- cell 7 的 GO（+7.36pp/年）里，5.68pp 来自这个错误口径，`SIZING_EDGE_IS_A_MASK_ARTIFACT`
  的判词**第一次有了独立证据**（此前只靠"换掩码后差额缩小"间接推断）。

**IM：证据不足，不许下判词。** 面板只有 1,051 根 bar（51-60 个移仓日），后前差 −1.76/−5.57pp
但 p=0.607/0.252。`MIXED_BY_PRODUCT` 的读法是"IM 还没测够"，不是"IM 反着来"。

## 这会改变什么

- IC 常驻真值按排除口径报：**9.62% / 9.68%**（calendar / strictest），不是 2.73%。
- cell 7 的定仓增益按 1.68pp 报（strictest），并注明"published 的 7.36pp 已判为掩码产物"。
- IM 侧所有 carry 数字继续按区间报，禁单点；等 IM 面板再长 ~12 个月（移仓日 ≥120）重跑本面。

## 未做（如实）

- 本面**无链腿无冒烟腿**（接线要改 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`，竞争窗禁改共享面）。
- published 掩码只有 22/18 天，凑不够 30 对 → 诚实记 DATA_BLOCKED，没有为凑样本放宽门槛。
- 后付检验只测了 8 日窗；21 日窗在每月移仓节奏下前后互叠（首版实测差值被自我抵消到 −0.38pp，
  已废弃并记入自检腿），更长的窗要改用"距下次移仓的斜率"另起一格。
