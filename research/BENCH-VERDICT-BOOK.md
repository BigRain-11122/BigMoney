generated 2026-11-26T16:43:37+08:00
evidence_cutoff 2026-11-25

门票面 33 张 → 判词行 96 行

| 处置 | 行数 | 意思 |
|---|---|---|
| EXHAUSTED | 75 | 同一配方跑过并给出了负结论——再跑一遍买的是第二个负结论 |
| CANDIDATE | 6 | 还活着，值得往钱的方向推 |
| DATA_GAP | 2 | 没算，缺面板 |
| REVALIDATED | 1 | 复验通行证，不是策略 |
| OTHER | 12 | 判词不在这四类里，按原词读 |

## A 股选股（astock）· 4 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| astock_lowvol | - | NO_EDGE | EXHAUSTED | 6.12% | 0.93pp | - | - | 4/5 缺 H5_excess_ge_2pct_t_ge_1.5 | results/bench_astock_lowvol.json @a8854f45ed69 |
| astock_resid_industry_reuse | arm1 | ONE_YEAR_STORY | OTHER | 3.76% | - | - | - | - | results/astock_rankind_stability.json @6507fdcbb65b |
| astock_resid_industry_reuse | arm2 | ONE_YEAR_STORY | OTHER | 3.76% | - | - | - | - | results/astock_rankind_stability.json @6507fdcbb65b |
| astock_resid_industry_reuse | arm3 | ONE_YEAR_STORY | OTHER | 3.76% | - | - | - | - | results/astock_rankind_stability.json @6507fdcbb65b |

## basis（basis）· 3 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| basis_capacity | - | CAPACITY_OK_AND_SIZED | OTHER | - | - | - | - | 3/3 | results/bench_basis_capacity.json @167a0b375b0e |
| basis_timing_size | - | GO | CANDIDATE | - | - | - | - | - | results/bench_basis_timing_size.json @47d863b7d056 |
| basis_timing_perm | - | SIGNIFICANT | CANDIDATE | - | - | - | - | - | results/bench_basis_timing_perm.json @2a737315a04b |

## 国债/债券（bond）· 7 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| bond_curve | T-TF:zrev | NO_EDGE | EXHAUSTED | 1.77% | - | 0.443 | -12.6% | 1/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct | results/bench_bond_curve.json @24f82971ef40 |
| bond_curve | T-TF:trend | NO_EDGE | EXHAUSTED | -1.84% | - | -0.406 | -19.27% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @24f82971ef40 |
| bond_curve | T-TS:zrev | NO_EDGE | EXHAUSTED | -1.06% | - | -0.167 | -21.37% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @24f82971ef40 |
| bond_curve | T-TS:trend | NO_EDGE | EXHAUSTED | -1.97% | - | -0.332 | -27.96% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @24f82971ef40 |
| bond_curve | TF-TS:zrev | NO_EDGE | EXHAUSTED | -0.74% | - | -0.171 | -12.42% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @24f82971ef40 |
| bond_curve | TF-TS:trend | NO_EDGE | EXHAUSTED | -3.62% | - | -0.913 | -28.83% | 0/5 缺 H1_full_ge_4pct,H2_oos_ge_3pct_and_sr_ge_0.4,H3_both_halves_positive,H4_drop_best_year_ge_1.5pct,H5_control_p_lt_0.05 | results/bench_bond_curve.json @24f82971ef40 |
| bond_defensive | - | NO_EDGE | EXHAUSTED | - | - | - | - | 4/5 缺 H3_positive_in_both_bear_years | results/bench_bond_defensive.json @866c6dc4e4c5 |

## cb（cb）· 2 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| cb_dual_low_reuse | - | NO_EDGE | EXHAUSTED | 7.64% | - | - | - | - | results/cb_dual_low.json @0a6ae4c7d691 |
| cb_floor | - | CLOSED_AT_POWER | OTHER | - | - | - | - | 0/5 缺 H1_excess_ge_2pp,H2_both_halves_positive,H3_mde_le_5pp,H4_beats_random_control,H5_survives_double_cost | results/bench_cb_floor.json @951d0cf1b532 |

## census（census）· 39 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| census_index_futures | variant=ma_cross|{'fast': 20, 'slow': 60}|long | NO_EDGE | EXHAUSTED | 1.42% | - | 0.195 | -28.73% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 20, 'slow': 60}|ls | NO_EDGE | EXHAUSTED | -0.27% | - | 0.041 | -28.23% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 100}|long | NO_EDGE | EXHAUSTED | 4.12% | - | 0.461 | -29.96% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 100}|ls | UNINFORMATIVE_AT_TARGET | OTHER | 5.31% | - | 0.479 | -25.51% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 3.98% | - | 0.454 | -22.69% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 50, 'slow': 200}|ls | UNINFORMATIVE_AT_TARGET | OTHER | 6.58% | - | 0.586 | -17.6% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 100, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 2.48% | - | 0.3 | -22.84% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=ma_cross|{'fast': 100, 'slow': 200}|ls | NO_EDGE | EXHAUSTED | 3.58% | - | 0.353 | -23.36% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=tsmom|{'lookback': 60, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 3.26% | - | 0.388 | -30.47% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=tsmom|{'lookback': 60, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 3.45% | - | 0.341 | -27.95% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=tsmom|{'lookback': 120, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.76% | - | 0.333 | -30.45% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=tsmom|{'lookback': 120, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 3.37% | - | 0.333 | -26.02% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=tsmom|{'lookback': 250, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.39% | - | 0.301 | -15.83% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=tsmom|{'lookback': 250, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 3.35% | - | 0.337 | -24.17% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=donchian|{'entry': 20, 'exit': 10}|long | NO_EDGE | EXHAUSTED | -4.14% | - | -0.227 | -46.89% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=donchian|{'entry': 20, 'exit': 10}|ls | NO_EDGE | EXHAUSTED | -4.14% | - | -0.227 | -46.89% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=donchian|{'entry': 40, 'exit': 15}|long | NO_EDGE | EXHAUSTED | -4.22% | - | -0.235 | -47.33% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=donchian|{'entry': 40, 'exit': 15}|ls | NO_EDGE | EXHAUSTED | -4.22% | - | -0.235 | -47.33% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=donchian|{'entry': 55, 'exit': 20}|long | NO_EDGE | EXHAUSTED | -3.92% | - | -0.215 | -47.06% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_index_futures | variant=donchian|{'entry': 55, 'exit': 20}|ls | NO_EDGE | EXHAUSTED | -3.92% | - | -0.215 | -47.06% | - | results/bench_census_index_futures.json @ad34c8b02832 |
| census_commodity | variant=tsmom|{'lookback': 60, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.76% | - | 0.45 | -20.15% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=tsmom|{'lookback': 60, 'skip': 21}|ls | NO_EDGE | EXHAUSTED | 1.53% | - | 0.221 | -20.51% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=tsmom|{'lookback': 120, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 4.42% | - | 0.714 | -16.13% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=tsmom|{'lookback': 120, 'skip': 21}|ls | GO | CANDIDATE | 5.01% | - | 0.626 | -21.74% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=tsmom|{'lookback': 250, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 4.56% | - | 0.754 | -13.7% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=tsmom|{'lookback': 250, 'skip': 21}|ls | GO | CANDIDATE | 5.24% | - | 0.671 | -18.88% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=ma_cross|{'fast': 20, 'slow': 60}|long | NO_EDGE | EXHAUSTED | 3.03% | - | 0.476 | -19.95% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=ma_cross|{'fast': 20, 'slow': 60}|ls | NO_EDGE | EXHAUSTED | 2.48% | - | 0.324 | -26.49% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=ma_cross|{'fast': 50, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 4.35% | - | 0.69 | -22.28% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=ma_cross|{'fast': 50, 'slow': 200}|ls | NO_EDGE | EXHAUSTED | 4.09% | - | 0.503 | -21.5% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=donchian|{'entry': 20, 'exit': 10}|long | NO_EDGE | EXHAUSTED | -4.54% | - | -0.471 | -69.29% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=donchian|{'entry': 20, 'exit': 10}|ls | NO_EDGE | EXHAUSTED | -4.54% | - | -0.471 | -69.29% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=donchian|{'entry': 55, 'exit': 20}|long | NO_EDGE | EXHAUSTED | -4.27% | - | -0.433 | -69.41% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_commodity | variant=donchian|{'entry': 55, 'exit': 20}|ls | NO_EDGE | EXHAUSTED | -4.27% | - | -0.433 | -69.41% | - | results/bench_census_commodity.json @ceb1dc433d20 |
| census_bond_futures | variant=tsmom|{'lookback': 60, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 3.2% | - | 0.523 | -11.64% | - | results/bench_census_bond_futures.json @bf94bdff478e |
| census_bond_futures | variant=tsmom|{'lookback': 120, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 3.2% | - | 0.511 | -13.59% | - | results/bench_census_bond_futures.json @bf94bdff478e |
| census_bond_futures | variant=tsmom|{'lookback': 250, 'skip': 21}|long | NO_EDGE | EXHAUSTED | 2.83% | - | 0.453 | -14.48% | - | results/bench_census_bond_futures.json @bf94bdff478e |
| census_bond_futures | variant=ma_cross|{'fast': 20, 'slow': 60}|long | NO_EDGE | EXHAUSTED | 1.92% | - | 0.34 | -17.89% | - | results/bench_census_bond_futures.json @bf94bdff478e |
| census_bond_futures | variant=ma_cross|{'fast': 50, 'slow': 200}|long | NO_EDGE | EXHAUSTED | 4.01% | - | 0.627 | -11.22% | - | results/bench_census_bond_futures.json @bf94bdff478e |

## 期货趋势族（fut）· 5 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| fut_trend | tsmom | NO_EDGE | EXHAUSTED | 6.21% | - | 0.51 | -23.05% | 4/5 缺 H5_control_p_lt_0.05 | results/bench_fut_trend.json @e0d45f23b1db |
| fut_trend | ma_cross | NO_EDGE_REPACKAGES_BETA | EXHAUSTED | 13.43% | - | 0.993 | -20.86% | 5/5 | results/bench_fut_trend.json @e0d45f23b1db |
| fut_trend | donchian | NO_EDGE | EXHAUSTED | -13.35% | - | -0.914 | -81.03% | 0/5 缺 H1_full_ge_6pct,H2_oos_ge_4pct_and_sr_ge_0.5,H3_both_halves_positive,H4_drop_best_year_ge_2pct,H5_control_p_lt_0.05 | results/bench_fut_trend.json @e0d45f23b1db |
| fut_trend | reversal | NO_EDGE | EXHAUSTED | -0.58% | - | 0.026 | -36.05% | 0/5 缺 H1_full_ge_6pct,H2_oos_ge_4pct_and_sr_ge_0.5,H3_both_halves_positive,H4_drop_best_year_ge_2pct,H5_control_p_lt_0.05 | results/bench_fut_trend.json @e0d45f23b1db |
| fut_trend | xs_mom | NO_EDGE | EXHAUSTED | 3.79% | - | 0.319 | -30.9% | 3/5 缺 H1_full_ge_6pct,H5_control_p_lt_0.05 | results/bench_fut_trend.json @e0d45f23b1db |

## idx（idx）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| idx_fut_basis_reuse | - | {"IC_net_carry_pp": 4.15, "IF_net_carry_pp": 0.74, "IH_net_carry_pp": 1.74, "IM_net_carry_pp": 5.89, "booked": "IC/IF/IM admitted at default cost (idx_fut_real_nav: booked)", "kind": "reuse"} | OTHER | - | - | - | - | - | results/idx_fut_basis.json @c6e3433adbfa |

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
| pair_index_60d | arm1 | NO_EDGE | EXHAUSTED | 2.92% | - | 0.269 | -37.8% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_index_60d.json @a519bbc7512d |
| pair_all10_60d | arm1 | NO_EDGE | EXHAUSTED | 1.32% | - | 0.163 | -58.88% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_all10_60d.json @2db2428d5089 |
| pair_commodity_60d | arm1 | NO_EDGE | EXHAUSTED | 1.23% | - | 0.163 | -58.88% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_commodity_60d.json @44352bb0c6e2 |
| pair_bond_curve_60d | arm1 | NO_EDGE | EXHAUSTED | -1.9% | - | -0.297 | -20.52% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_pair_bond_curve_60d.json @0e7e9e89423e |

## paper（paper）· 1 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| paper_basis_timing | - | TRACKING | OTHER | - | - | - | - | - | results/paper_basis_timing/STATE.json @ae09358d9b36 |

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
| revalidate | - | ALL_HOLD | REVALIDATED | - | - | - | - | - | results/bench_revalidate.json @bbb160e43afd |

## reversal（reversal）· 2 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| reversal_index_5d | arm1 | NO_EDGE | EXHAUSTED | 2.43% | - | 0.307 | -19.72% | 4/5 缺 H1_full_ge | results/bench_reversal_index_5d.json @43bde7a5d78a |
| reversal_commodity_5d | arm1 | NO_EDGE | EXHAUSTED | -4.22% | - | -0.454 | -59.71% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_reversal_commodity_5d.json @9e5129815157 |

## robust（robust）· 9 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| robust_ma_index | variant=20_50 | NO_EDGE | EXHAUSTED | -1.15% | - | -0.032 | -32.65% | 1/5 缺 H1_full_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_ma_index.json @8c0043bbdf11 |
| robust_ma_index | variant=50_100 | UNINFORMATIVE_AT_TARGET | OTHER | 5.31% | - | 0.479 | -25.51% | 5/5 | results/bench_robust_ma_index.json @8c0043bbdf11 |
| robust_ma_index | variant=50_200 | UNINFORMATIVE_AT_TARGET | OTHER | 6.58% | - | 0.586 | -17.6% | 5/5 | results/bench_robust_ma_index.json @8c0043bbdf11 |
| robust_tsmom_commodity | variant=60d | NO_EDGE | EXHAUSTED | 1.53% | - | 0.221 | -20.51% | 2/5 缺 H1_full_ge,H2_oos_ge,H5_control | results/bench_robust_tsmom_commodity.json @6c4868a251b3 |
| robust_tsmom_commodity | variant=120d | GO | CANDIDATE | 5.01% | - | 0.626 | -21.74% | 5/5 | results/bench_robust_tsmom_commodity.json @6c4868a251b3 |
| robust_tsmom_commodity | variant=250d | GO | CANDIDATE | 5.24% | - | 0.671 | -18.88% | 5/5 | results/bench_robust_tsmom_commodity.json @6c4868a251b3 |
| robust_donchian_index | variant=20_10 | NO_EDGE | EXHAUSTED | -4.14% | - | -0.227 | -46.89% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_donchian_index.json @a2c38825c96c |
| robust_donchian_index | variant=40_15 | NO_EDGE | EXHAUSTED | -4.22% | - | -0.235 | -47.33% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_donchian_index.json @a2c38825c96c |
| robust_donchian_index | variant=55_20 | NO_EDGE | EXHAUSTED | -3.92% | - | -0.215 | -47.06% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_robust_donchian_index.json @a2c38825c96c |

## 单品种趋势（trend）· 5 行

| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| trend_single_IC_long | arm1 | NO_EDGE | EXHAUSTED | 2.99% | - | 0.408 | -18.98% | 2/5 缺 H1_full_ge,H4_drop_best,H5_control | results/bench_trend_single_IC_long.json @c42bfa8c5151 |
| trend_single_AU_long | arm1 | NO_EDGE | EXHAUSTED | 7.95% | - | 0.941 | -29.21% | 4/5 缺 H5_control | results/bench_trend_single_AU_long.json @cefb151a363c |
| trend_single_T_long | arm1 | NO_EDGE | EXHAUSTED | 3.09% | - | 0.706 | -5.65% | 4/5 缺 H5_control | results/bench_trend_single_T_long.json @d1781f159e83 |
| trend_single_RB_long | arm1 | NO_EDGE | EXHAUSTED | 0.5% | - | 0.106 | -32.33% | 1/5 缺 H1_full_ge,H2_oos_ge,H4_drop_best,H5_control | results/bench_trend_single_RB_long.json @43963dd9b87a |
| trend_single_SC_long | arm1 | NO_EDGE | EXHAUSTED | -1.05% | - | -0.111 | -26.96% | 0/5 缺 H1_full_ge,H2_oos_ge,H3_both_halves,H4_drop_best,H5_control | results/bench_trend_single_SC_long.json @469c4c284069 |

## 已问过的问题（同一问别付两次钱）

- 本册内没有相似度 ≥ 0.80 的重复问句；跨册查重仍需按问题文本自行比对。

## 缺证据的行

- 无：每张有结果路径的卡都能打开并取到字节摘要。

读法：EXHAUSTED 的行是本司已经付过钱的知识，它的价值不是「再试一次」而是「写下一张卡时先看这里」。CANDIDATE 的 0 行如果一直不动，说明钱不在银行这一侧——在赚钱线（基差 carry/容量/时点）那一侧。
