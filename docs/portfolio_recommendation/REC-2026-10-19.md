# 组合最优建议 + 证据链（阶段×风格 v1）

- 证据截止（as_of）：**2026-10-19**｜机：bm-b｜面：`PORTFOLIO-RECOMMENDATION`（RESEARCH_READOUT_ZERO_JUDGED_CLAIMS）
- 本页由 `scripts/portfolio_recommend.py` 确定性再生成；零新检验、零新判据。

## 1. 结论（最优组合建议）

**建议：`unconditional DIVLOWVOL-YIELDVOL sleeve (Top-20 by yield_ttm, low-vol half, EW, monthly)`**

- 依据：stage-conditioned selection was judged UNSUPPORTED; the unconditional sleeve dominates every combo cell
- 判据原文：prereg sec.3/4 P4: best combo sharpe >= U-divlowvol + 0.10
- 最好阶段组合 C1 夏普 1.083 vs 无条件 U-divlowvol 1.209（差 -0.126，P4 门槛未过）
- 归因：combo gains trace to the divlowvol sleeve it already holds; stage switching nets negative via turnover tax + cash legs missing the up-moves

## 2. 当前阶段与阶段读数（描述面）

- 当前阶段：**SUPPORT**（标签面 `results/regime5_labels/REGIME5-2026-10-19.json`，截止 2026-10-19）
- 近 20 个交易日阶段序列：GRIND/GRIND/GRIND/GRIND/GRIND/GRIND/GRIND/GRIND/GRIND/BEAR/BEAR/BEAR/BEAR/BEAR/BEAR/BEAR/BEAR/BEAR/SUPPORT/SUPPORT

| 阶段态 | 样本日 | 描述最优面 | 条件夏普 | 条件年化 | 态内回撤 |
|---|---:|---|---:|---:|---:|
| BEAR | 859 | U-divlowvol | 0.98 | 10.2% | -10.1% |
| GRIND | 83 | U-divlowvol | 1.12 | 5.0% | -3.0% |
| CHOP | 2004 | U-divlowvol | 1.28 | 13.1% | -15.8% |
| SUPPORT | 171 | C1 | 1.43 | 9.3% | -4.4% |
| BULL | 172 | U-divlowvol | 1.83 | 20.7% | -3.5% |

> descriptive readout on the allocation-regime view (label that governed each month's allocation); no judgment line is asserted by this table

## 3. 三族判决面（如实携带）

| 族 | 判决 | 夏普(全窗) | 被动等权夏普 | DSR | cutoff |
|---|---|---:|---:|---:|---|
| divlowvol | insufficient-sample | 0.894 | 0.448 | 0.675 | 2026-09-22 |
| value | insufficient-sample | 0.381 | 0.299 | 0.093 | 2026-09-22 |
| quality | insufficient-sample | -0.318 | 0.220 | 0.000 | 2026-09-22 |

- 同掩码 null 族（K=2000）：verdict=SUPPORT_ABOVE_NULL，z=3.2281，p=0.001（`results/divlowvol_nulls/NULLS-CONSUME-2026-09-22.json`）

## 4. 当前持仓面（冻结规则导出的 live 名单）

- 来源 `results/divlowvol_live/latest.json`｜as_of 2026-10-19｜入场月 2026-10-08｜20 只×5% 等权｜单向换手 35%
- 名单：000915, 002027, 002170, 002233, 002441, 002572, 002749, 002763, 002867, 300406, 300770, 300994, 600329, 600742, 600750, 600866, 601717, 603165, 603551, 603569

## 5. 证据链（文件 + sha16）

- `results/stagestyle_combo_p1/FINALIZE-SSCOMBO-P1.json` — 59af2b6215a5ccf3
- `results/fund_divlowvol_p1/fund_divlowvol_p1_results.json` — 5a3940c87777a494
- `results/fund_value_p1/fund_value_p1_results.json` — 94f1552af1280381
- `results/fund_quality_p1/fund_quality_p1_results.json` — 7b4484bb00bd0122
- `results/divlowvol_live/latest.json` — 0df6316af5c809ae
- `results/divlowvol_nulls/NULLS-CONSUME-2026-09-22.json` — 40077b280f8d7613
- `results/regime5_labels/REGIME5-2026-10-19.json` — 4058160df3373a73
- `results/stagestyle_combo_p1/STAGE-STYLE-MATRIX-v1.json` — c568e968f32e9b36

## 6. 诚实边界

- 本页是已冻结判决产物的汇总面：零新检验、零新判据、零 ledger 记账。
- 最优组合建议 = 判决面读数（无条件 divlowvol 优于三格阶段组合），不构成投资建议；公司自动实盘开闸仍须月界窗 + CEO 唯一门。
- 阶段表为描述性读数（格内日收益统计），不含活/判负判决线。
- 三族 P1 判决 verdict 均为 insufficient-sample，如实携带。
- P2 复活批（盈利质量过滤+出场轴）仍在冻结窗，面板重投为结构等待；本页不预设其结论。

sha16=04f8fce9856cb2e1
