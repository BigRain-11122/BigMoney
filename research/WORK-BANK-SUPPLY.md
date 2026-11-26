generated 2026-11-26T16:38:14+08:00
evidence_cutoff 2026-11-25

银行 20 张卡 · 队列 31 格 · 已答 18 / 在飞 0 / 未取 0 / 数据阻塞 2 / 悬空 0

供给判词 = **无题可取**（未取 0 + 在飞 0）。红是真的红，但它的意思不是「队列坏了」而是「没人写下第 21 张卡」。

朴素读法会把 18 张已答卡读成在飞（`queued` 一旦写下就再没人翻面），差 18 张。

| 卡 | 银行状态 | 格状态 | 判词 | 完成 |
|---|---|---|---|---|
| pair_index_60d | queued | done | NO_EDGE | 2026-11-24T21:24:50 |
| pair_all10_60d | queued | done | NO_EDGE | 2026-11-24T21:25:19 |
| pair_commodity_60d | queued | done | NO_EDGE | 2026-11-24T21:25:26 |
| trend_single_IC_long | queued | done | NO_EDGE | 2026-11-24T21:25:34 |
| trend_single_AU_long | queued | done | NO_EDGE | 2026-11-24T21:25:43 |
| trend_single_T_long | queued | done | NO_EDGE | 2026-11-24T21:25:51 |
| reversal_index_5d | queued | done | NO_EDGE | 2026-11-24T21:25:59 |
| robust_ma_index | queued | done | UNSTABLE_ACROSS_PARAMS | 2026-11-24T21:27:02 |
| robust_tsmom_commodity | queued | done | UNSTABLE_ACROSS_PARAMS | 2026-11-24T21:27:12 |
| robust_donchian_index | queued | done | UNSTABLE_ACROSS_PARAMS | 2026-11-24T21:27:22 |
| census_index_futures | queued | done | CENSUS_UNPOWERED | 2026-11-24T21:29:06 |
| census_commodity | queued | done | CENSUS_SIGN_MIXED | 2026-11-24T21:29:18 |
| census_bond_futures | queued | done | CENSUS_LEANS_POSITIVE | 2026-11-24T21:33:19 |
| pair_bond_curve_60d | queued | done | NO_EDGE | 2026-11-24T21:38:47 |
| trend_single_RB_long | queued | done | NO_EDGE | 2026-11-24T21:38:47 |
| trend_single_SC_long | queued | done | NO_EDGE | 2026-11-24T21:38:47 |
| reversal_commodity_5d | queued | done | NO_EDGE | 2026-11-24T21:38:47 |
| paper_basis_timing | queued | done | TRACKING | 2026-11-24T21:43:53 |
| options_vol_premium | blocked | - | - | - |
| minute_intraday_reversal | blocked | - | - | - |

队列里不属于银行的格 13 个——赚钱线（基差 carry/容量/时点）全在这一侧，银行里一张都没有，所以银行答完 18 张也不等于研究面见底。

| 格 | 状态 | 判词 | 完成 |
|---|---|---|---|
| fut_trend | done | {"tsmom": "NO_EDGE", "ma_cross": "NO_EDGE_REPACKAGES_BETA", "donchian": "NO_EDGE", "reversal": "NO_EDGE", "xs_mom": "NO_EDGE"} | 2026-11-22T23:10:08 |
| bond_curve | done | {"T-TF:zrev": "NO_EDGE", "T-TF:trend": "NO_EDGE", "T-TS:zrev": "NO_EDGE", "T-TS:trend": "NO_EDGE", "TF-TS:zrev": "NO_EDGE", "TF-TS:trend": "NO_EDGE"} | 2026-11-22T23:10:26 |
| astock_lowvol | done | {"verdict": "NO_EDGE", "H5_excess_ge_2pp": false, "ann_pct": 6.12, "excess_pp": 0.93, "excess_t": 0.45} | - |
| bond_defensive | done | NO_EDGE | 2026-11-22T23:10:28 |
| revalidate | done | ALL_HOLD | 2026-11-25T22:22:55 |
| idx_fut_basis_reuse | done | {"kind": "reuse", "IC_net_carry_pp": 4.15, "IM_net_carry_pp": 5.89, "IF_net_carry_pp": 0.74, "IH_net_carry_pp": 1.74, "booked": "IC/IF/IM admitted at default cost (idx_fut_real_nav: booked)"} | - |
| cb_dual_low_reuse | done | {"verdict": "NO_EDGE", "ann_pct": 7.64, "vs_equal_weight_pp": 0.83} | - |
| astock_resid_industry_reuse | done | {"verdict": "ONE_YEAR_STORY", "ann_pct": 3.76, "ex_best_year_pct": 0.14} | - |
| basis_capacity | done | {"verdict": "CAPACITY_OK_AND_SIZED", "IC_multiple": 1754.5, "IM_multiple": 2577.5, "total_multiple": 4332.0, "annual_cny_if_10m_each_leg": 1003400} | - |
| basis_timing_size | done | {"verdict": "GO", "IC_weighted": 10.09, "IC_always_on": 2.73, "IM_weighted": 9.3, "IM_always_on": 5.63} | - |
| repo_ladder | done | {"GC001": "BASELINE_REFERENCE", "GC003": "NO_EDGE", "GC004": "NO_EDGE", "GC007": "NO_EDGE", "GC014": "NO_EDGE", "GC028": "NO_EDGE", "GC091": "NO_EDGE", "GC182": "NO_EDGE", "R-001": "NO_EDGE", "R-003": "NO_EDGE", "R-007": "NO_EDGE"} | 2026-11-23T09:39:11 |
| cb_floor | done | CLOSED_AT_POWER | 2026-11-23T09:59:42 |
| basis_timing_perm | done | {"verdict": "SIGNIFICANT", "IC_pp": 7.36, "IM_pp": 3.64, "p": 0.0, "draws": 5000} | - |
