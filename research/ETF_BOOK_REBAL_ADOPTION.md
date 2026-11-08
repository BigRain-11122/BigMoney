# 把调仓改成 10 日？——先给这条规则做采纳轮

> 面：`results/etf_book_rebal_adoption.json` ｜ 脚本：`scripts/etf_book_rebal_adoption.py` ｜ 面板截止：2026-11-06 ｜ 判据在首跑前冻结

## 一句话

PHASE_DEPENDENT —— the gate passes on only 40% of 5 phase cells (floor 60%); the control book passes 20% of the same calendars, so the verdict word itself moves with the phase；the return effect itself is +0.75pp median and positive in 100% of cells, so the lever is not what fails -- the gate pass is；at 20bp/side the same change is -0.38pp median, so the return edge is a cost assumption as well；the faster grid trades +9.88 more units per year, which at the 10bp step costs 0.99pp -- against an edge of +0.75pp (the fee is the same size as the edge)

## 控制臂复现

| 项 | 值 |
| --- | --- |
| 本轮控制臂 CAGR | 11.4600% |
| 已发布 nobond_vt08 | 11.4900% |
| 逐年行逐位相等 | 是 |

## 相位 × 成本网格

| 成本 | 相位数 | 候选过 Y4 占比 | 控制过 Y4 占比 | 中位 ΔCAGR | 最差 ΔCAGR | 收益不降占比 | 中位 ΔSharpe | 中位 Δ年换手 | 中位 Δ每决策换手 | 候选 top-2 相位 IQR | 中位到线距离 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10bp | 5 | 40% | 20% | +0.75pp | +0.24pp | 100% | +0.105 | +9.884 | -0.1370 | 0.0703 | +4.13pp |
| 20bp | 5 | 0% | 0% | -0.38pp | -0.87pp | 40% | -0.009 | +9.884 | -0.1370 | 0.0744 | +13.85pp |

**成本算术**：更快的网格每年多交易 +9.88 个单位，按 10bp 的假设差就是 0.99pp——而这条规则在 10bp 下的中位收益优势是 +0.75pp（手续费与优势同量级）；实测两档成本间的中位 CAGR 位移是 +1.13pp。

逐相位行见 JSON 的 `summary.by_cost.<bp>.rows`。

## 判据（首跑前冻结）

- `control` = {'rebal': 20, 'n_hold': 5, 'cost': 0.001, 'vol_target': 0.08}
- `candidate_rebal` = 10
- `phase_rebal` = 10
- `n_phases` = 5
- `costs_bp` = [10, 20]
- `pass_share_min` = 0.6
- `return_share_min` = 0.75
- `return_floor_pp` = -0.15
- `median_floor_pp` = -0.25
- `min_phases_per_cost` = 3
- `frozen` = 'written before the first run; `check` refuses a face that echoes other numbers'
- `units` = {'cagr_pct': 'percent per year', 'turnover': 'sum |dw| per rebalance, fraction of book', 'delta_cagr_pp': 'percentage points of CAGR, candidate minus control on the same phase and cost', 'top2_distance_pp': '(top-2 share - 0.70) * 100: positive means the gate is failed', 'phase': 'decision-grid start bar inside one 10-bar cycle'}

## 这份回执不主张什么

- no cell is a forecast: every yearly row is that cell's own realised return
- the 2026 row is partial and counted raw by the frozen gate (r1418 convention)
- phases shift the decision calendar only; the judged window is the same panel
- 10bp and 20bp are two assumptions, not two realities: the pass share at each cost is printed side by side
- the change is a schedule constant, not a size: the permission/floor arc is untouched
- the control book itself passes Y4 on 20% of the same calendars: a verdict word about this gate is a phase draw before it is a property of a book

## 结论对票面的意义

对票面：不改。pass 只在部分决策日历上出现，换一个月末起点就消失，那不是规则。
