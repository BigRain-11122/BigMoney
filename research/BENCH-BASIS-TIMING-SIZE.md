# 基差按分位定仓位 vs 常驻持有（bench cell 7）

generated 2026-11-25T22:22:39+08:00 | 判决 **GO**

规则：权重 = clamp((80−分位)/60, 0, 1)；分位只用过去 250 日（因果）；成本 1.5bp/边；carry=期货−指数，移仓日剔除。

| 品种 | 加权 carry/年 | 常驻 carry/年 | 差 | 加权回撤 | 常驻回撤 | 前后半 | 样本外加权/常驻 | 判决 |
|---|---|---|---|---|---|---|---|---|
| IC | +10.07% | +2.69% | +7.38pp | -1.89% | -3.81% | [12.12, 8.05] | +9.19% / +5.21% | **GO** |
| IM | +9.35% | +5.60% | +3.75pp | -3.05% | -5.11% | [5.76, 13.06] | +11.67% / +8.06% | **GO** |

## 读数

- IC：平均权重 0.497、空仓日占 22.2%、年换手 46.66、判据 {"H1_margin_over_always_on": true, "H2_both_halves_positive": true, "H3_drawdown_not_worse": true, "H4_oos_not_worse": true}
- IM：平均权重 0.53、空仓日占 21.9%、年换手 35.65、判据 {"H1_margin_over_always_on": true, "H2_both_halves_positive": true, "H3_drawdown_not_worse": true, "H4_oos_not_worse": true}

## 没有回答的问题

- 只做了 IC/IM 两个品种；IF/IH 的贴水更薄，规则可能不适用。
- 没有建模保证金占用与资金成本：carry 是毛口径。
- 分位窗口 250 日是冻结值，未做敏感性扫描（换窗口属于新格）。
