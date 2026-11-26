# 基准和臂必须是同一本书：`bench_generic.buy_and_hold()` 口径修复

generated 2026-11-26 · evidence_cutoff 2026-11-26 · 正身 `scripts/bench_generic.py` · 面 `results/bench_*.json` · 审计 `results/bench_go_ruler_audit.json`

## 一句话

基准的仓位规模过去被写死成波动目标 0.10，而 13 张面上的臂用的是 0.06/0.08。两本书大小不同，年化相减没有意义；本轮把基准改成**按每张面自己 `cfg.target_vol` 计价**，13 张面重算，基准下调 0.12~0.95pp/年，9 张面「臂与基准的口径差」归零。

## 改了什么

| 位置 | 改前 | 改后 |
|---|---|---|
| `buy_and_hold()` | `vol_weighted_positions(..., target_vol=0.10)` 写死 | 形参 `target_vol`，调用处传 `cfg.get("target_vol", 0.10)` |
| 每个臂 | 只有绝对年化 | 新增 `excess_vs_bench_pp`、`excess_clears_mde`（超额须过自己的 MDE 才算「看见过」）、`bench_target_vol` |
| 面元数据 | 无 | `benchmark_sizing{target_vol, same_yardstick, arms_excess_clears_own_mde}` |
| 页面 | 10 列 | 11 列，新增「超额vs同口径基准」，低于 MDE 的标 `(below MDE)` |

判决（`verdict`）语义**未改**：这是把尺子摆正，不是换判据。翻不翻案另议。

## 重算结果（17 张 bench_generic 面全跑，6.5s/面）

基准年化变化（新 − 旧，pp/年）：

| 面 | 臂 target_vol | 基准 旧→新 | 变化 |
|---|---|---|---|
| pair_all10_60d | 0.08 | 5.78 → 4.83 | −0.95 |
| pair_commodity_60d | 0.08 | 4.62 → 3.80 | −0.82 |
| reversal_commodity_5d | 0.08 | 4.62 → 3.80 | −0.82 |
| robust_tsmom_commodity | 0.08 | 4.62 → 3.80 | −0.82 |
| pair_index_60d | 0.06 | 2.36 → 1.64 | −0.72 |
| reversal_index_5d | 0.06 | 2.36 → 1.64 | −0.72 |
| census_bond_futures | 0.06 | 5.50 → 4.86 | −0.64 |
| pair_bond_curve_60d | 0.06 | 5.50 → 4.86 | −0.64 |
| robust_ma_index | 0.08 | 2.36 → 1.93 | −0.43 |
| census_index_futures | 0.08 | 2.05 → 1.93 | −0.12 |
| robust_donchian_index | 0.08 | 2.05 → 1.93 | −0.12 |
| census_commodity | 0.08 | 3.80 → 3.80 | 0.00（本轮窗口内已先修） |
| trend_single_T_long | 0.06 | 3.19 → 3.27 | +0.08 |

**内建对照（本来就是 0.10 的四面，基准不该因本次改法而系统性移动）**：
AU −0.05pp、IC −0.16pp、RB +0.07pp、SC +0.03pp —— 全在 r2136 量出的 0.18pp 噪声地板内，移动来自面板推进到今天，不来自改法。

## 结论面：4 条 GO 仍然过不了自己的 MDE

| 面 | 臂 | 全期年化 | 同口径基准 | 超额 | MDE | 过线 |
|---|---|---|---|---|---|---|
| census_commodity | tsmom 120/21 ls | 4.99% | 3.80% | 1.19pp | 3.78pp | 否 |
| census_commodity | tsmom 250/21 ls | 5.19% | 3.80% | 1.39pp | 3.66pp | 否 |
| robust_tsmom_commodity | 120d | 4.99% | 3.80% | 1.19pp | 3.78pp | 否 |
| robust_tsmom_commodity | 250d | 5.19% | 3.80% | 1.39pp | 3.66pp | 否 |

四张卡、两条独立测量（同一 rule/lookback 在两个面上各测一次）。审计面 `bench_go_ruler_audit.json` 重算后：`size_mismatch` **9 → 0**，`n_go=4 / n_go_backed=0 / n_go_unsupported=4` 不变。判词仍是 `GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS`——现在这个判词背后的两个数已经同口径。

## 为什么不在这一轮改判决

改判决要动 `verdict_of()` 与其他 21 张面/historical 卡的解读口径，属于立法+翻案，按 P1 新方向与「不改判据」纪律，本轮只交付「尺子摆正 + 超额列」，把翻案做成下一轮的**预注册**决定：
候选方案 = 把 `H1_full_ge` 从「绝对 ≥4%」改为「超额 ≥ 自己的 MDE」，即 4 条 GO 自动降为 `UNINFORMATIVE_AT_TARGET`（此方案会同时影响 21 面 85 臂，需单独立案）。

## 复现

```
python scripts\bench_generic.py --config research\cells\<cell_id>.json   # 单面，~6.5s
python scripts\bench_go_ruler_audit.py                                  # 审计，1.6s
python scripts\bench_verdict_book.py --verify                           # 判决书逐字节自洽
```
