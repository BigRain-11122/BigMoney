# 试用劳动力 reform 通道方向审计

- 判词：**DIRECTION_BLIND_MEMBERS_NAMED**
- 生成口径：5 张 reform 面；admitted=2、负向=2、正向=0、读不出=0
- evidence_cutoff：2026-09-22

## 为什么会有这张面

g2_reform_fdr4d's p-values are two-sided (tl2._dual_nulls_w2: p = mean(|perms| >= |mu|)) and reform_composite_scores are batch-internal percentiles, so a reliably-losing arm passes FDR and ranks inside the batch. No sign test exists anywhere in the reform funnel.

## 逐波读数

| wave | admitted | 负 | 正 | 读不出 | 上名单的负向 cell | cutoff |
|---|---|---|---|---|---|---|
| TRIAL_LABOR_W17 | 0 | 0 | 0 | 0 | — | 2026-09-22 |
| TRIAL_LABOR_W18 | 0 | 0 | 0 | 0 | — | 2026-09-22 |
| TRIAL_LABOR_W19 | 0 | 0 | 0 | 0 | — | 2026-09-22 |
| TRIAL_LABOR_W20 | 2 | 2 | 0 | 0 | W20-A-0003, W20-B-0019 | 2026-09-22 |
| TRIAL_LABOR_W21 | 0 | 0 | 0 | 0 | — | 2026-09-22 |

## 负向成员逐笔

| wave | cell | sharpe_full_L | annualized | composite | BH q | 在名单上 |
|---|---|---|---|---|---|---|
| TRIAL_LABOR_W20 | W20-A-0003 | -1.2957 | -0.108139 | 0.2397677419354839 | 0.006200000000000001 | 是 |
| TRIAL_LABOR_W20 | W20-B-0019 | -1.4119 | -0.124493 | 0.23718709677419356 | 0.0 | 是 |

## 边界（如实）

- 只读：不改任何已冻结判决、不碰 reform 门、不改 intake 面。
- 判据只读 `ret.sharpe_full_L` / `ret.annualized_ret_L` 两块，不重算成本、不重算 null —— 方向是这张面唯一要回答的问题。
- `sharpe == 0` 记 FLAT 不计入负向（本窗口未出现）。
- 修不修 = 科学门改动（给 prereg 模板加方向门），须 GM 署名，不在本脚本射程。

