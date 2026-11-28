generated 2026-11-28T17:04:58+08:00
evidence_cutoff 2026-11-28

门票面 33 张 → 判词行 96 行

| 处置 | 行数 | 意思 |
|---|---|---|
| EXHAUSTED | 75 | 同一配方跑过并给出了负结论——再跑一遍买的是第二个负结论 |
| CANDIDATE | 6 | 还活着，值得往钱的方向推 |
| DATA_GAP | 2 | 没算，缺面板 |
| REVALIDATED | 1 | 复验通行证，不是策略 |
| OTHER | 12 | 判词不在这四类里，按原词读 |

## 还活着的结论（6 行压成 4 个问题）

| 问题卡 | 臂 | 判词 | 证据 |
|---|---|---|---|
| basis_timing_perm | - | SIGNIFICANT | results/bench_basis_timing_perm.json @725f58b4ed40 |
| basis_timing_size | - | GO | results/bench_basis_timing_size.json @7b40930c05d4 |
| census_commodity | variant=tsmom|{'lookback': 120, 'skip': 21}|ls, variant=tsmom|{'lookback': 250, 'skip': 21}|ls | GO | results/bench_census_commodity.json @439853fc21b0 |
| robust_tsmom_commodity | variant=120d, variant=250d | GO | results/bench_robust_tsmom_commodity.json @e0b474690ec9 |

这一节只搬判词与证据，不追加任何新判定；行级数字与关卡在上面的分族表里。

## A 股选股（astock）· 4 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| astock_lowvol | - | NO_EDGE | EXHAUSTED | 6.12% | 0.93pp | - | - | 4/5 缺 H5_excess_ge_2pct_t_ge_1.5 | results/bench_astock_lowvol.json @eea9e094a2c0 |
| astock_resid_industry_reuse | arm1 | ONE_YEAR_STORY | OTHER | 3.76% | - | - | - | - | results/astock_rankind_stability.json @6507fdcbb65b |
| astock_resid_industry_reuse | arm2 | ONE_YEAR_STORY | OTHER | 3.76% | - | - | - | - | results/astock_rankind_stability.json @6507fdcbb65b |
| astock_resid_industry_reuse | arm3 | ONE_YEAR_STORY | OTHER | 3.76% | - | - | - | - | results/astock_rankind_stability.json @6507fdcbb65b |

## basis（basis）· 3 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| basis_capacity | - | CAPACITY_OK_AND_SIZED | OTHER | - | - | - | - | 3/3 | results/bench_basis_capacity.json @230ddce7bbeb |
| basis_timing_size | - | GO | CANDIDATE | - | - | - | - | - | results/bench_basis_timing_size.json @7b40930c05d4 |
| basis_timing_perm | - | SIGNIFICANT | CANDIDATE | - | - | - | - | - | results/bench_basis_timing_perm.json @725f58b4ed40 |

## 国债/债券（bond）· 7 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| bond_curve | T-TF:zrev | NO_EDGE | EXHAUSTED | 1.77% | - | 0.443 | -12.6% | 1/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct | results/bench_bond_curve.json @5359064cfe3e |
| bond_curve | T-TF:trend | NO_EDGE | EXHAUSTED | -1.84% | - | -0.406 | -19.27% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @5359064cfe3e |
| bond_curve | T-TS:zrev | NO_EDGE | EXHAUSTED | -1.06% | - | -0.166 | -21.37% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @5359064cfe3e |
| bond_curve | T-TS:trend | NO_EDGE | EXHAUSTED | -1.97% | - | -0.333 | -27.96% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @5359064cfe3e |
| bond_curve | TF-TS:zrev | NO_EDGE | EXHAUSTED | -0.73% | - | -0.17 | -12.42% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @5359064cfe3e |
| bond_curve | TF-TS:trend | NO_EDGE | EXHAUSTED | -3.62% | - | -0.913 | -28.83% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @5359064cfe3e |
| bond_defensive | - | NO_EDGE | EXHAUSTED | - | - | - | - | 4/5 缺 H3_positive_in_both_bear_years | results/bench_bond_defensive.json @725429ea8f8f |

## cb（cb）· 2 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| cb_dual_low_reuse | - | NO_EDGE | EXHAUSTED | 7.64% | - | - | - | - | results/cb_dual_low.json @f16b2a5b5190 |
| cb_floor | - | CLOSED_AT_POWER | OTHER | - | - | - | - | 0/5 缺 H1_excess_ge_2pp,H2_both_halves_positive,H3_mde_le_5pp,H4_beats_random_control,H5_survives_double_cost | results/bench_cb_floor.json @951d0cf1b532 |

## census（census）· 39 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| census_index_futures | variant=ma_cross|{'fast': 20, 'slow': 60}|long | NO_EDGE | EXHAUSTED | 1.42% | - | 0.195 | -28.73% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 20, 'slow': 60}|ls | NO_EDGE | EXHAUSTED | -0.08% | - | 0.056 | -28.23% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 100}|long | NO_EDGE | EXHAUSTED | 4.12% | - | 0.461 | -29.96% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 100}|ls | UNINFORMATIVE_AT_TARGET | OTHER | 5.5% | - | 0.494 | -25.51% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 3.98% | - | 0.453 | -22.69% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 200}|ls | UNINFORMATIVE_AT_TARGET | OTHER | 6.78% | - | 0.6 | -17.6% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 100, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 2.48% | - | 0.299 | -22.84% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=ma_cross|{'fast': 100, 'slow': 200}|ls | NO_EDGE | EXHAUSTED | 3.77% | - | 0.368 | -23.36% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=tsmom|{'lookback': 60, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 3.25% | - | 0.387 | -30.47% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=tsmom|{'lookback': 60, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 3.64% | - | 0.356 | -27.95% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=tsmom|{'lookback': 120, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.75% | - | 0.333 | -30.45% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=tsmom|{'lookback': 120, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 3.56% | - | 0.348 | -26.02% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=tsmom|{'lookback': 250, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.39% | - | 0.301 | -15.83% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=tsmom|{'lookback': 250, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 3.54% | - | 0.352 | -24.17% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=donchian|{'entry': 20, 'exit': 10}|long | NO_EDGE | EXHAUSTED | 0.75% | - | 0.122 | -30.44% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=donchian|{'entry': 20, 'exit': 10}|ls | NO_EDGE | EXHAUSTED | -2.93% | - | -0.185 | -44.43% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=donchian|{'entry': 40, 'exit': 15}|long | NO_EDGE | EXHAUSTED | 0.06% | - | 0.067 | -29.63% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=donchian|{'entry': 40, 'exit': 15}|ls | NO_EDGE | EXHAUSTED | -1.2% | - | -0.035 | -34.48% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=donchian|{'entry': 55, 'exit': 20}|long | NO_EDGE | EXHAUSTED | 1.4% | - | 0.174 | -25.53% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_index_futures | variant=donchian|{'entry': 55, 'exit': 20}|ls | NO_EDGE | EXHAUSTED | -0.11% | - | 0.052 | -26.41% | - | results/bench_census_index_futures.json @ea7da17c1f95 |
| census_commodity | variant=tsmom|{'lookback': 60, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.76% | - | 0.45 | -20.15% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=tsmom|{'lookback': 60, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 1.52% | - | 0.219 | -20.51% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=tsmom|{'lookback': 120, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 4.42% | - | 0.714 | -16.13% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=tsmom|{'lookback': 120, 'skip': 21}|ls | GO | CANDIDATE | 4.99% | - | 0.623 | -21.74% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=tsmom|{'lookback': 250, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 4.54% | - | 0.752 | -13.7% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=tsmom|{'lookback': 250, 'skip': 21}|ls | GO | CANDIDATE | 5.19% | - | 0.665 | -18.88% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=ma_cross|{'fast': 20, 'slow': 60}|long | NO_EDGE | EXHAUSTED | 3.02% | - | 0.476 | -19.95% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=ma_cross|{'fast': 20, 'slow': 60}|ls | NO_EDGE | EXHAUSTED | 2.46% | - | 0.322 | -26.49% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=ma_cross|{'fast': 50, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 4.35% | - | 0.691 | -22.28% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=ma_cross|{'fast': 50, 'slow': 200}|ls | NO_EDGE | EXHAUSTED | 4.09% | - | 0.502 | -21.5% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=donchian|{'entry': 20, 'exit': 10}|long | NO_EDGE | EXHAUSTED | 3.37% | - | 0.406 | -35.21% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=donchian|{'entry': 20, 'exit': 10}|ls | NO_EDGE | EXHAUSTED | 2.07% | - | 0.278 | -32.07% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=donchian|{'entry': 55, 'exit': 20}|long | NO_EDGE | EXHAUSTED | 2.08% | - | 0.27 | -30.41% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_commodity | variant=donchian|{'entry': 55, 'exit': 20}|ls | NO_EDGE | EXHAUSTED | 1.82% | - | 0.248 | -29.82% | - | results/bench_census_commodity.json @439853fc21b0 |
| census_bond_futures | variant=tsmom|{'lookback': 60, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 3.21% | - | 0.525 | -11.64% | - | results/bench_census_bond_futures.json @7711b8af20c3 |
| census_bond_futures | variant=tsmom|{'lookback': 120, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 3.21% | - | 0.512 | -13.59% | - | results/bench_census_bond_futures.json @7711b8af20c3 |
| census_bond_futures | variant=tsmom|{'lookback': 250, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.84% | - | 0.455 | -14.48% | - | results/bench_census_bond_futures.json @7711b8af20c3 |
| census_bond_futures | variant=ma_cross|{'fast': 20, 'slow': 60}|long | NO_EDGE | EXHAUSTED | 1.92% | - | 0.342 | -17.89% | - | results/bench_census_bond_futures.json @7711b8af20c3 |
| census_bond_futures | variant=ma_cross|{'fast': 50, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 4.02% | - | 0.629 | -11.22% | - | results/bench_census_bond_futures.json @7711b8af20c3 |

## 期货趋势族（fut）· 5 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| fut_trend | tsmom | NO_EDGE | EXHAUSTED | 6.21% | - | 0.51 | -23.05% | 4/5 缺 H5_control_p_lt_0.05 | results/bench_fut_trend.json @554b692fa91c |
| fut_trend | ma_cross | NO_EDGE_REPACKAGES_BETA | EXHAUSTED | 13.38% | - | 0.989 | -20.86% | 5/5 | results/bench_fut_trend.json @554b692fa91c |
| fut_trend | donchian | NO_EDGE | EXHAUSTED | -2.2% | - | -0.092 | -39.7% | 0/5 缺 H1_full_ge_6pct,H2_oos_ge_4pct_and_sr_ge_0.5,H3_both_halves_positive,H4_drop_best_year_ge_2pct,H5_control_p_lt_0.05 | results/bench_fut_trend.json @554b692fa91c |
| fut_trend | reversal | NO_EDGE | EXHAUSTED | -0.5% | - | 0.031 | -36.05% | 0/5 缺 H1_full_ge_6pct,H2_oos_ge_4pct_and_sr_ge_0.5,H3_both_halves_positive,H4_drop_best_year_ge_2pct,H5_control_p_lt_0.05 | results/bench_fut_trend.json @554b692fa91c |
| fut_trend | xs_mom | NO_EDGE | EXHAUSTED | 3.76% | - | 0.317 | -30.9% | 3/5 缺 H1_full_ge_6pct,H5_control_p_lt_0.05 | results/bench_fut_trend.json @554b692fa91c |

## idx（idx）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| idx_fut_basis_reuse | - | {"IC_net_carry_pp": 4.15, "IF_net_carry_pp": 0.74, "IH_net_carry_pp": 1.74, "IM_net_carry_pp": 5.89, "booked": "IC/IF/IM admitted at default cost (idx_fut_real_nav: booked)", "kind": "reuse"} | OTHER | - | - | - | - | - | results/idx_fut_basis.json @54f97f525abf |

## minute（minute）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| minute_intraday_reversal | - | - | DATA_GAP | - | - | - | - | - | - |

## options（options）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| options_vol_premium | - | - | DATA_GAP | - | - | - | - | - | - |

## 横截面配对（多最强空最弱）（pair）· 4 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| pair_index_60d | arm1 | NO_EDGE | EXHAUSTED | 2.97% | - | 0.273 | -37.8% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_index_60d.json @a023af61232b |
| pair_all10_60d | arm1 | NO_EDGE | EXHAUSTED | 1.41% | - | 0.17 | -58.88% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_all10_60d.json @5379b8b0fb88 |
| pair_commodity_60d | arm1 | NO_EDGE | EXHAUSTED | 1.3% | - | 0.169 | -58.88% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_commodity_60d.json @b8cf6cb6e60e |
| pair_bond_curve_60d | arm1 | NO_EDGE | EXHAUSTED | -1.91% | - | -0.299 | -20.52% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_bond_curve_60d.json @eec412e55ad2 |

## paper（paper）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| paper_basis_timing | - | TRACKING | OTHER | - | - | - | - | - | results/paper_basis_timing/STATE.json @0e1f08c739bf |

## repo（repo）· 11 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| repo_ladder | arm1 | BASELINE_REFERENCE | OTHER | - | - | - | - | 2/5 缺 H1_pickup,H2_both_halves,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm2 | NO_EDGE | EXHAUSTED | - | - | - | - | 2/5 缺 H1_pickup,H2_both_halves,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm3 | NO_EDGE | EXHAUSTED | - | - | - | - | 2/5 缺 H1_pickup,H2_both_halves,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm4 | NO_EDGE | EXHAUSTED | - | - | - | - | 3/5 缺 H1_pickup,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm5 | NO_EDGE | EXHAUSTED | - | - | - | - | 3/5 缺 H1_pickup,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm6 | NO_EDGE | EXHAUSTED | - | - | - | - | 3/5 缺 H1_pickup,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm7 | NO_EDGE | EXHAUSTED | - | - | - | - | 3/5 缺 H3_worst_year,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm8 | NO_EDGE | EXHAUSTED | - | - | - | - | 2/5 缺 H1_pickup,H3_worst_year,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm9 | NO_EDGE | EXHAUSTED | - | - | - | - | 1/5 缺 H1_pickup,H2_both_halves,H3_worst_year,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm10 | NO_EDGE | EXHAUSTED | - | - | - | - | 1/5 缺 H1_pickup,H2_both_halves,H3_worst_year,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |
| repo_ladder | arm11 | NO_EDGE | EXHAUSTED | - | - | - | - | 1/5 缺 H1_pickup,H2_both_halves,H3_worst_year,H5_double_fee | results/bench_repo_ladder.json @250aa773132d |

## 复验通行证（不是策略）（revalidate）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| revalidate | - | ALL_HOLD | REVALIDATED | - | - | - | - | - | results/bench_revalidate.json @ff0e8ffacbad |

## reversal（reversal）· 2 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| reversal_index_5d | arm1 | NO_EDGE | EXHAUSTED | 2.28% | - | 0.29 | -19.72% | 3/5 缺 H1_full_ge,H3_both_halves | results/bench_reversal_index_5d.json @64f1315dcf7a |
| reversal_commodity_5d | arm1 | NO_EDGE | EXHAUSTED | -4.2% | - | -0.452 | -59.71% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_reversal_commodity_5d.json @32194f3e4e12 |

## robust（robust）· 9 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| robust_ma_index | variant=20_50 | NO_EDGE | EXHAUSTED | -0.96% | - | -0.016 | -32.65% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_ma_index.json @cdca7c311909 |
| robust_ma_index | variant=50_100 | UNINFORMATIVE_AT_TARGET | OTHER | 5.5% | - | 0.494 | -25.51% | 5/5 | results/bench_robust_ma_index.json @cdca7c311909 |
| robust_ma_index | variant=50_200 | UNINFORMATIVE_AT_TARGET | OTHER | 6.78% | - | 0.6 | -17.6% | 5/5 | results/bench_robust_ma_index.json @cdca7c311909 |
| robust_tsmom_commodity | variant=60d | NO_EDGE | EXHAUSTED | 1.52% | - | 0.219 | -20.51% | 2/5 缺 H1_full_ge,H2_oos_ge,H5_control | results/bench_robust_tsmom_commodity.json @e0b474690ec9 |
| robust_tsmom_commodity | variant=120d | GO | CANDIDATE | 4.99% | - | 0.623 | -21.74% | 5/5 | results/bench_robust_tsmom_commodity.json @e0b474690ec9 |
| robust_tsmom_commodity | variant=250d | GO | CANDIDATE | 5.19% | - | 0.665 | -18.88% | 5/5 | results/bench_robust_tsmom_commodity.json @e0b474690ec9 |
| robust_donchian_index | variant=20_10 | NO_EDGE | EXHAUSTED | -2.93% | - | -0.185 | -44.43% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_donchian_index.json @c3f3cbff9b34 |
| robust_donchian_index | variant=40_15 | NO_EDGE | EXHAUSTED | -1.2% | - | -0.035 | -34.48% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_donchian_index.json @c3f3cbff9b34 |
| robust_donchian_index | variant=55_20 | NO_EDGE | EXHAUSTED | -0.11% | - | 0.052 | -26.41% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_donchian_index.json @c3f3cbff9b34 |

## 单品种趋势（trend）· 5 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| trend_single_IC_long | arm1 | NO_EDGE | EXHAUSTED | 2.99% | - | 0.408 | -18.98% | 2/5 缺 H1_full_ge,H4_drop_best,H5_control | results/bench_trend_single_IC_long.json @6ceb5065a1a4 |
| trend_single_AU_long | arm1 | NO_EDGE | EXHAUSTED | 7.95% | - | 0.941 | -29.21% | 4/5 缺 H5_control | results/bench_trend_single_AU_long.json @00469aff6b55 |
| trend_single_T_long | arm1 | NO_EDGE | EXHAUSTED | 3.09% | - | 0.706 | -5.65% | 4/5 缺 H5_control | results/bench_trend_single_T_long.json @a14718354323 |
| trend_single_RB_long | arm1 | NO_EDGE | EXHAUSTED | 0.5% | - | 0.106 | -32.33% | 1/5 缺 H1_full_ge,H2_oos_ge,H4_drop_best,H5_control | results/bench_trend_single_RB_long.json @3daec755a6f8 |
| trend_single_SC_long | arm1 | NO_EDGE | EXHAUSTED | -1.03% | - | -0.107 | -26.96% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_trend_single_SC_long.json @f0686b28611b |

## 已问过的问题（同一问别付两次钱）

- 本册内没有相似度 ≥ 0.80 的重复问句；跨册查重仍需按问题文本自行比对。

## 缺证据的行

- 无：每张有结果路径的卡都能打开并取到字节摘要。

读法：EXHAUSTED 的行是本司已经付过钱的知识，它的价值不是「再试一次」而是「写下一张卡时先看这里」。CANDIDATE 的 0 行如果一直不动，说明钱不在银行这一侧——在赚钱线（基差 carry/容量/时点）那一侧。
