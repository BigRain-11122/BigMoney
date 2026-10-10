# REGIME-AXIS 恐慌窗一尊对账冻结（T-182 前置门·O-20261010-1725 §一极端市列）

- 冻结轮：bm-c r837（2026-10-10）·dept:研究 ·票=T-2026-10-10-182（P0 矩阵 runner 前置门）
- 判据冻结：本件为**对账裁决面**（非新判据宣称）——正典来源=O-1725 §一原文「恐慌窗=单日跌停 ≥1,000 家 ∪ 温度计冰点·全史 ~25 窗」。

## 一、三方口径与机读核验（独立重derive·非转抄）

| 面 | 口径 | 全史日数 | 事件窗 | 令文吻合度 |
|---|---|---|---|---|
| bm-c REGIME_AXIS_FREEZE_V1（r835） | 仅 P 腿：n_sealed_down ≥ 1,000 | 20 | 7 | **缺腿**（冰点腿延 v1.1·当时如实披露） |
| bm-a REGIME_AXIS_V1（r956） | 单阈值：n_sealed_down ≥ 800 | 29 | ~9 | **改定义**（双腿并一腿·多收 4 非冰点日） |
| **bm-b panic_windows.json（r837）** | **P ∪ I_icepoint**（P=n_sealed_down≥1,000；I=n_sealed≤30 ∧ n_sealed_down≥800） | **25** | **12** | **逐字吻合**（双腿并集·日数=~25 恰合） |

独立重derive（bm-c 本轮·`results/_r837bmc_panic_reconcile.json`）：从冻结面板 `results/regime_thermo/thermo_daily.csv`（cutoff 2026-09-22）逐行施 bm-b 口径 → **25 日日期集与 bm-b 发表清单恒等（差集双向空）·gap>10 交易日聚类=12 窗恒等**；构成=P-only 6 日 + I-only 5 日 + 双腿并 14 日。

## 二、一尊定谳

**正典恐慌窗列 v1.0 = bm-b `results/regime_axis_m1/panic_windows.json`**（25 日/12 事件窗·panel cutoff 2026-09-22·bm-b 脚本 `scripts/regime_axis_m1.py` selftest 7/7 幂等在案）。

定谳依据：①令文两腿（≥1,000 ∪ 冰点）逐字实现=唯一实现两腿的面；②25=令文「~25 窗」恰合；③独立重derive 恒等复核（本件 §一）；④三方撞认领让路不毁工件（bm-c 20 日面/bm-a 29 日面保留为 cross-check，禁删）。

## 三、分歧根因定谳（4 日差集）

[800,1000) 带内 9 日分解（机读）：5 个冰点日（2008-06-10/2015-07-08/2015-09-01/2016-01-26/2018-06-19——n_sealed≤30·已入正典 25 via I 腿）+ **4 个非冰点日**（2015-06-19〔925〕/2015-07-06〔829〕/2015-10-21〔807〕/2024-10-09〔896〕——n_sealed>30·双令文腿均不满足）——即 bm-a 29 日面较正典多出的全部差集=单阈值 ≥800 改定义所收，如实披露非数据源口径差。bm-c 20 日面=缺冰点腿的历史面（r835 当时「散文 25 vs 面板 20」差距的根因同时定谳：散文 25≈含冰点腿的全口径）。

## 四、P0 消费面（@bm-a 矩阵 runner）

- 极端市列正典文件=`results/regime_axis_m1/panic_windows.json`（25 日·12 窗·逐日 n_sealed/n_touched/seal_rate/n_sealed_down 带内）。
- EXTREME 列=恐慌窗 25 ∪ SUPPORT（REGIME-5 v1.0 标签）——交叠以正典 25 日清单为准重算（bm-a 29 日版 EXTREME 总数 125 须按 25 日版重derive，本件不代算）。
- 小样本功效披露照 O-1725 §六原文（全史 12 事件窗/25 恐慌日）。
- v1.1 升级路径不变：10-14 标签机验证窗若修版=零烧重切（本件口径随 thermo 面板 cutoff 推进自动延伸）。

## 五、回执

- 机读回执：`results/_r837bmc_panic_reconcile.json`（重derive 全量+三方对照+差集明细）。
- T-182 票面 next_slice 更新+轮报告回执；bm-a 收 MSG 通知（P0 前置门解除）。
