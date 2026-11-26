# 成本戳普查 · 每格能不能说出自己的成本

generated 2026-11-26T15:07:15+08:00 | 队列口径 cutoff 2026-11-25T22:22:55+08:00 | 谓词同源 `block_board.cost_stamp_problem`

**结论**：合格格 26 / 共 26，缺戳 0 —— board 交叉核对 一致。

| 格 | 结果面 | 状态 | 说明 |
|---|---|---|---|
| fut_trend | results/bench_fut_trend.json | STAMPED |  |
| bond_curve | results/bench_bond_curve.json | STAMPED |  |
| astock_lowvol | results/bench_astock_lowvol.json | STAMPED |  |
| bond_defensive | results/bench_bond_defensive.json | STAMPED |  |
| basis_timing_size | results/bench_basis_timing_size.json | STAMPED |  |
| repo_ladder | results/bench_repo_ladder.json | STAMPED |  |
| cb_floor | results/bench_cb_floor.json | STAMPED |  |
| pair_index_60d | results/bench_pair_index_60d.json | STAMPED |  |
| pair_all10_60d | results/bench_pair_all10_60d.json | STAMPED |  |
| pair_commodity_60d | results/bench_pair_commodity_60d.json | STAMPED |  |
| trend_single_IC_long | results/bench_trend_single_IC_long.json | STAMPED |  |
| trend_single_AU_long | results/bench_trend_single_AU_long.json | STAMPED |  |
| trend_single_T_long | results/bench_trend_single_T_long.json | STAMPED |  |
| reversal_index_5d | results/bench_reversal_index_5d.json | STAMPED |  |
| robust_ma_index | results/bench_robust_ma_index.json | STAMPED |  |
| robust_tsmom_commodity | results/bench_robust_tsmom_commodity.json | STAMPED |  |
| robust_donchian_index | results/bench_robust_donchian_index.json | STAMPED |  |
| census_index_futures | results/bench_census_index_futures.json | STAMPED |  |
| census_commodity | results/bench_census_commodity.json | STAMPED |  |
| basis_timing_perm | results/bench_basis_timing_perm.json | STAMPED |  |
| census_bond_futures | results/bench_census_bond_futures.json | STAMPED |  |
| pair_bond_curve_60d | results/bench_pair_bond_curve_60d.json | STAMPED |  |
| trend_single_RB_long | results/bench_trend_single_RB_long.json | STAMPED |  |
| trend_single_SC_long | results/bench_trend_single_SC_long.json | STAMPED |  |
| reversal_commodity_5d | results/bench_reversal_commodity_5d.json | STAMPED |  |
| paper_basis_timing | results/paper_basis_timing/STATE.json | STAMPED |  |

无需修复：每个已跑格都带着成本率。

本面只读普查，不改任何格的结果面；修复按处方落到各格脚本后重跑该格。
