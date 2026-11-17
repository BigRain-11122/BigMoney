# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261116.json` → `LIVE-BOOK-20261117.json`
- 价格依据：2026-11-16（前一天 2026-11-16）｜数据截止：2026-11-16（前一天 2026-11-16）
- 判决：**UNEXPLAINED_MOVES**

## 一句话
两天**是同一根 bar**（没有新数据进来），这页有 **265** 个数变了；其中 **6** 个是钟面（机器多久没说话之类，本来就该走）、**236** 个能给出解释（旧数还在页上／口径句改了／这一节换了代／这一节换了定价的输入／这个数只是转抄别面）、**23** 个没解释。新增 **17** 个数字叶子、消失 **3** 个。

## 动的数（全部 265 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/admission/prior/top2_share` | 0.7039 | 0.7084 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/authority/owner_silent_h` | 68.4 | 11.2 | CLOCK |  |
| `/causal_rebuild/elapsed_sec` | 118.9 | 82.4 | CLOCK |  |
| `/derisk/instrument/dd_brake/distance_to_line_pp` | 4.1 | 4.33 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/dd_brake/spread_pp` | 17.71 | 17.36 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/dd_brake/top2_max` | 0.9181 | 0.9169 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/dd_brake/top2_min` | 0.741 | 0.7433 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/loss_cond_vt/distance_to_line_pp` | 2.0 | 1.71 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/loss_cond_vt/spread_pp` | 24.45 | 23.76 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/loss_cond_vt/top2_max` | 0.9245 | 0.9205 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/loss_cond_vt/top2_min` | 0.68 | 0.6829 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/trend_brake/distance_to_line_pp` | 1.29 | 1.12 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/trend_brake/spread_pp` | 21.36 | 21.01 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/trend_brake/top2_max` | 0.9007 | 0.8989 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/trend_brake/top2_min` | 0.6871 | 0.6888 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/vt08/distance_to_line_pp` | 3.79 | 3.15 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/vt08/spread_pp` | 12.39 | 11.2 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/vt08/top2_max` | 0.786 | 0.7805 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/instrument/vt08/top2_min` | 0.6621 | 0.6685 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/0/annual_sum_pp` | 81.8427 | 81.3254 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/0/delta_annual_sum_pp` | -29.498 | -29.3843 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/0/delta_top2` | 0.022 | 0.0226 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/0/top2_share` | 0.7039 | 0.7084 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/1/annual_sum_pp` | 88.3893 | 88.0953 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/1/delta_annual_sum_pp` | -22.9514 | -22.6144 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/1/delta_top2` | 0.0702 | 0.0689 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/1/top2_share` | 0.7521 | 0.7547 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/2/annual_sum_pp` | 102.6126 | 102.0988 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/2/delta_annual_sum_pp` | -8.7281 | -8.6109 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/2/delta_top2` | 0.0538 | 0.0536 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/2/top2_share` | 0.7357 | 0.7394 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/3/annual_sum_pp` | 87.1348 | 86.5039 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/3/delta_annual_sum_pp` | -24.2059 | -24.2058 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/3/delta_top2` | 0.1131 | 0.115 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/derisk/mechanism/3/top2_share` | 0.795 | 0.8008 | SECTION_ADVANCED | 这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/one_open_late/mean_cny` | -1798.153765058916 | -1782.9320396821006 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/one_open_late/median_cny` | -932.3031683309355 | -929.179677596404 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/one_open_late/share_late_helps` | 0.41247002398081534 | 0.4138755980861244 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/one_open_late/t` | -4.570838936445422 | -4.551322911619218 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/1/cost_cny_vs_today` | 1798.15 | 1782.93 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/1/mean_cny` | -1798.153765058916 | -1782.9320396821006 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/1/share_late_helps` | 0.41247002398081534 | 0.4138755980861244 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/1/t` | -4.570838936445422 | -4.551322911619218 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/2/cost_cny_vs_today` | 2637.54 | 2628.37 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/2/mean_cny` | -2637.535644581885 | -2628.365344486415 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/2/share_late_helps` | 0.41586538461538464 | 0.4172661870503597 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/2/t` | -4.822231717315911 | -4.818043693212478 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/3/cost_cny_vs_today` | 2912.47 | 2882.08 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/3/mean_cny` | -2912.473314066595 | -2882.084463921774 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/3/share_late_helps` | 0.43132530120481927 | 0.4326923076923077 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/do_or_wait/table/3/t` | -4.231648631666141 | -4.205498567925245 | SECTION_ADVANCED | 这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/family_coherence/floor_extrapolation/gap_pp` | 0.145 | 0.05 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/floor_extrapolation/observed_pp` | 0.365 | 0.385 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/floor_extrapolation/predicted_pp` | 0.22 | 0.335 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/floor_extrapolation/tolerance_pp` | 0.081 | 0.172 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/signflip/arms/2/cells_positive` | 0 | 3 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/signflip/n_reject_standing` | 3 | 2 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/fleet/rows/0/age_h` | 66.91 | 3.45 | CLOCK |  |
| `/fleet/rows/1/age_h` | 413.39 | 419.73 | CLOCK |  |
| `/fleet/rows/2/age_h` | 1.09 | 1.35 | CLOCK |  |
| `/floor_provenance/grid/full|all/bars` | 1663 | 1664 | SECTION_ADVANCED | 这一节自己换了代：`floor_provenance` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/floor_provenance/grid/full|graded/bars` | 1663 | 1664 | SECTION_ADVANCED | 这一节自己换了代：`floor_provenance` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/floor_provenance/issuing_cell/bars` | 1663 | 1664 | SECTION_ADVANCED | 这一节自己换了代：`floor_provenance` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/beta` | 0.07453700153927338 | 0.07447081363455153 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/capital_for_one_lot` | 11001515.798404276 | 11047549.500899909 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/corr` | 0.14152934655175411 | 0.14138168578950164 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/maxdd_delta_pp` | -0.05412128425121843 | -0.053068306339809634 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/min_unit_notional` | 820020.0 | 822720.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/sharpe_delta` | -0.020547817217357878 | -0.020974735979811476 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/unit_over_target` | 11.001515798404277 | 11.04754950089991 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/variance_removable_pct` | 2.0030555935366516 | 1.998878107668137 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/vol_delta_pp` | -0.10119817508366241 | -0.10097200878734364 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/dsharpe` | -0.020547817217357878 | -0.020974735979811476 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/dsharpe_hi` | 0.0707691125152359 | 0.07410021845492577 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/dsharpe_lo` | -0.09881020082682476 | -0.09867847461663937 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/share_above_uncond` | 0.9605 | 0.9685 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/tail_ci_hi` | 0.8328393159433894 | 0.8414217707501334 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/tail_ci_lo` | 0.10957277748333087 | 0.12206311855461444 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/uncond_beta` | 0.07453700153927338 | 0.07447081363455153 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/margin_pct_of_capital` | 3.8 | 3.7 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital` | 2.24 | 2.21 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital_by_mask/calendar` | 3.12 | 3.08 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital_by_mask/published` | 2.24 | 2.21 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital_by_mask/strictest` | 3.12 | 3.08 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/notional_x_capital_on_tier` | 0.26 | 0.25 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/one_lot_notional_cny` | 1275000.0 | 1243680.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/stress_loss_pct_of_capital` | 10.7 | 10.4 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/vol_contrib_pct` | 5.7 | 5.6 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/notional_x_capital_on_tier` | 0.4 | 0.39 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/one_lot_notional_cny` | 1186980.0 | 1181700.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/2/net_pct_of_capital_by_mask/calendar` | 2.23 | 2.24 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/2/one_lot_notional_cny` | 820020.0 | 822720.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/2/stress_loss_pct_of_capital` | 12.4 | 12.5 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/margin_pct_of_capital` | 3.8 | 3.7 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital` | 2.68 | 2.65 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/calendar` | 3.51 | 3.45 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/published` | 2.68 | 2.65 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/strictest` | 3.51 | 3.45 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/notional_x_capital_on_tier` | 0.25 | 0.24 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/one_lot_notional_cny` | 1255360.0 | 1221000.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/stress_loss_pct_of_capital` | 10.4 | 10.2 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/vol_contrib_pct` | 6.3 | 6.1 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/notional_per_lot_cny` | 1275000.0 | 1243680.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/1/notional_per_lot_cny` | 1186980.0 | 1181700.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/2/notional_per_lot_cny` | 820020.0 | 822720.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/3/notional_per_lot_cny` | 1255360.0 | 1221000.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/gap/elapsed_sec` | 118.4 | 76.4 | CLOCK |  |
| `/k_gap/account_base_gap_cny` | 28483.4 | 28525.2 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/lots_at_rule` | 774 | 766 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/lots_ordered` | 726 | 719 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/next_lot_dk_pp` | 0.0007 | 0.0165 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/price` | 1.189 | 1.201 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/short_cny` | 5707.2 | 5644.7 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/short_lots` | 48 | 47 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/cheapest_next_lot/short_shares` | 4800 | 4700 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/lots_at_rule` | 728 | 734 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/lots_ordered` | 684 | 689 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/next_lot_dk_pp` | 0.0383 | 0.0435 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/price` | 1.263 | 1.254 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/short_cny` | 5557.2 | 5643.0 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/short_lots` | 44 | 45 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/0/short_shares` | 4400 | 4500 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/lots_at_rule` | 774 | 766 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/lots_ordered` | 726 | 719 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/next_lot_dk_pp` | 0.0007 | 0.0165 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/price` | 1.189 | 1.201 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/short_cny` | 5707.2 | 5644.7 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/short_lots` | 48 | 47 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/1/short_shares` | 4800 | 4700 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/lots_at_rule` | 459 | 467 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/lots_ordered` | 431 | 438 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/next_lot_dk_pp` | 0.0669 | 0.022 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/price` | 2.004 | 1.97 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/short_cny` | 5611.2 | 5713.0 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/short_lots` | 28 | 29 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/2/short_shares` | 2800 | 2900 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/3/lots_at_rule` | 803 | 800 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/3/lots_ordered` | 754 | 751 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/3/next_lot_dk_pp` | 0.0043 | 0.0205 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/3/price` | 1.145 | 1.15 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/3/short_cny` | 5610.5 | 5635.0 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/4/lots_at_rule` | 528 | 525 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/4/lots_ordered` | 496 | 493 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/4/next_lot_dk_pp` | 0.0444 | 0.0302 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/4/price` | 1.741 | 1.751 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/rows/4/short_cny` | 5571.2 | 5603.2 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/short_share_of_book_pct` | 6.0961 | 6.1355 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/k_gap/short_total_cny` | 28057.3 | 28238.9 | SECTION_ADVANCED | 这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/AU` | 2796666.666666667 | 2768533.3333333335 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IC` | 4250000.0 | 4145600.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IF` | 3956600.0 | 3939000.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IH` | 2733400.0 | 2742400.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IM` | 4184533.3333333335 | 4070000.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/SC` | 2085000.0 | 2069333.3333333335 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/T` | 3668166.666666667 | 3658500.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/TF` | 3558666.666666667 | 3555333.3333333335 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/TS` | 6842400.0 | 6842133.333333334 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/AU` | 0.839 | 0.83056 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IC` | 1.275 | 1.24368 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IF` | 1.18698 | 1.1817 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IH` | 0.82002 | 0.82272 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IM` | 1.25536 | 1.221 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/SC` | 0.6255 | 0.6208 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/T` | 1.10045 | 1.09755 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/TF` | 1.0676 | 1.0666 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/TS` | 2.05272 | 2.05264 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/permission/allowed_cny` | 431770.0 | 431728.0 | SECTION_ADVANCED | 这一节自己换了代：`permission` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/permission/ordered_cny` | 431769.6 | 431727.8 | SECTION_ADVANCED | 这一节自己换了代：`permission` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/cny_total` | 3627.42 | 2795.26 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/0/amount_cny` | 86389.2 | 86400.6 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/0/latest_pctile` | 3.8127090301003346 | 1.2032085561497325 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/0/same_bucket_move_cny` | 841.3711283890027 | 841.4821565136252 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/1/amount_cny` | 86321.4 | 86351.9 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/1/latest_pctile` | 17.900262467191602 | 59.28646379853095 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/1/mean_pct` | 0.3792060133771917 | 0.1136316784152153 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/1/n` | 353 | 770 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/1/same_bucket_move_cny` | 327.3359396313791 | 98.12311331342829 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/1/t` | 1.087252826971886 | 0.38385105751885035 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/2/amount_cny` | 86372.4 | 86286.0 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/2/latest_pctile` | 96.64292980671414 | 90.7520325203252 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/2/mean_pct` | 0.2489448117886486 | 0.23910384745233929 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/2/n` | 266 | 267 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/2/same_bucket_move_cny` | 215.01960861733872 | 206.31314581272548 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/2/t` | 0.915981747529712 | 0.8825032886927169 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/3/amount_cny` | 86333.0 | 86365.0 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/3/latest_pctile` | 11.80451127819549 | 19.30879038317055 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/3/same_bucket_move_cny` | 460.222132074456 | 460.3927169982555 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/4/amount_cny` | 86353.6 | 86324.3 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/4/latest_pctile` | 6.338939197930142 | 14.728682170542635 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/4/mean_pct` | 2.065312175367106 | 1.3772998496472701 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/4/n` | 107 | 172 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/4/same_bucket_move_cny` | 1783.4714146678095 | 1188.9444541090584 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/premium_forward/rows/4/t` | 3.899475787273565 | 4.544192330848934 | SECTION_ADVANCED | 这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/roster_audit/local_copies/0/laneside/value` | 187 | 185 | QUOTED_FROM_SOURCE | 这个数不是这页算的：`results/ah_panel_status.json:fresh_pairs` 现在读 185，与今天印的 185 相同——页只是转抄，动的是被引用的那张面 |
| `/vol_target_gate/arms/0/cagr_pct` | 14.16 | 14.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/0/sharpe` | 0.943 | 0.938 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/1/cagr_pct` | 8.51 | 8.43 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/1/sharpe` | 0.884 | 0.877 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/2/cagr_pct` | 6.44 | 6.3 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/2/sharpe` | 0.849 | 0.842 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/3/cagr_pct` | 4.32 | 4.22 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/3/sharpe` | 0.819 | 0.812 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/4/cagr_pct` | 3.25 | 3.19 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/4/sharpe` | 0.819 | 0.812 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/5/cagr_pct` | 2.18 | 2.13 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/arms/5/sharpe` | 0.819 | 0.812 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/capacity_cny` | 39783633.0 | 27645948.0 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/max_abs_delta` | 0.852698 | 0.85295 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_by_arm/unscaled` | 4.665973 | 4.654482 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_by_arm/vt02` | 4.60859 | 4.623249 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_by_arm/vt03` | 4.567272 | 4.570829 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_by_arm/vt04` | 4.581703 | 4.603678 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_by_arm/vt06` | 4.853644 | 4.874988 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_by_arm/vt08` | 4.974762 | 4.995503 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_target_gate/shape/effective_years/median_range` | 0.40749 | 0.424674 | SECTION_ADVANCED | 这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_ladder/best_sharpe/cagr_pct` | 0.1155 | 0.1145 | SECTION_ADVANCED | 这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_ladder/best_sharpe/sharpe` | 1.137 | 1.129 | SECTION_ADVANCED | 这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_ladder/tightest_admit/cagr_pct` | 0.1429 | 0.1417 | SECTION_ADVANCED | 这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_ladder/tightest_admit/sharpe` | 0.993 | 0.987 | SECTION_ADVANCED | 这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/answer/reference_top2_median` | 1.5307 | 1.5952 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/0/margin_to_line` | -0.0806 | -0.0757 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/0/spread` | 0.101 | 0.0962 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/0/top2_max` | 0.7806 | 0.7757 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/0/top2_min` | 0.6796 | 0.6795 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/0/top2_vs_reference` | 0.51 | 0.4863 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/1/margin_to_line` | -0.1717 | -0.164 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/1/spread` | 0.1678 | 0.1556 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/1/top2_max` | 0.8717 | 0.864 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/1/top2_min` | 0.7039 | 0.7084 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/1/top2_vs_reference` | 0.5695 | 0.5416 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/2/margin_to_line` | -0.1848 | -0.1768 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/2/spread` | 0.1669 | 0.1542 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/2/top2_max` | 0.8848 | 0.8768 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/2/top2_min` | 0.7179 | 0.7226 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/2/top2_vs_reference` | 0.578 | 0.5496 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/3/margin_to_line` | -0.1833 | -0.1759 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/3/spread` | 0.1703 | 0.1583 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/3/top2_max` | 0.8833 | 0.8759 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/3/top2_min` | 0.713 | 0.7176 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/3/top2_vs_reference` | 0.5771 | 0.5491 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/4/margin_to_line` | -0.146 | -0.1399 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/4/spread` | 0.1728 | 0.1625 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/4/top2_max` | 0.846 | 0.8399 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/4/top2_min` | 0.6732 | 0.6774 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/4/top2_vs_reference` | 0.5527 | 0.5265 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/5/margin_to_line` | -0.1004 | -0.0953 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/5/spread` | 0.1329 | 0.1238 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/5/top2_max` | 0.8004 | 0.7953 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/5/top2_min` | 0.6675 | 0.6715 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/5/top2_vs_reference` | 0.5229 | 0.4986 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/6/margin_to_line` | -0.0908 | -0.0858 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/6/spread` | 0.1113 | 0.1056 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/6/top2_max` | 0.7908 | 0.7858 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/6/top2_min` | 0.6795 | 0.6802 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/books/6/top2_vs_reference` | 0.5166 | 0.4926 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/drop_two/book_retained_max` | 0.7032 | 0.6957 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/drop_two/book_retained_min` | 0.1029 | 0.1114 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/drop_two/reference_retained/0` | -0.6185 | -0.7362 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/drop_two/reference_retained/1` | -0.6116 | -0.7274 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/drop_two/reference_retained/2` | -0.5849 | -0.6934 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/drop_two/reference_retained/3` | -0.5732 | -0.6786 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/reference/cagr_pct` | 0.0428 | 0.0399 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/reference/top2_max` | 1.5464 | 1.6134 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/reference/top2_median` | 1.5307 | 1.5952 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vt_phases/reference/top2_min` | 1.5112 | 1.5724 | SECTION_ADVANCED | 这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |

## 今天没有了的数（3 个，列前 40）

- `/family_coherence/panels_detail/1/bars`
- `/family_coherence/panels_detail/1/bars_fewer_than_newest`
- `/family_coherence/panels_detail/1/columns`

## 今天新出现的数（17 个）落在这几块上

- `/admission/concentration_caliber`
- `/admission/reads`

## 钱的两处（同一根 bar 上改了定价口径）

- `/admission/prior/top2_share`：**0.7039 → 0.7084**（差 0.0045）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/derisk/instrument/dd_brake/distance_to_line_pp`：**4.1 → 4.33**（差 0.23）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/dd_brake/spread_pp`：**17.71 → 17.36**（差 -0.35）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/dd_brake/top2_max`：**0.9181 → 0.9169**（差 -0.0012）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/dd_brake/top2_min`：**0.741 → 0.7433**（差 0.0023）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/loss_cond_vt/distance_to_line_pp`：**2.0 → 1.71**（差 -0.29）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/loss_cond_vt/spread_pp`：**24.45 → 23.76**（差 -0.69）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/loss_cond_vt/top2_max`：**0.9245 → 0.9205**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/loss_cond_vt/top2_min`：**0.68 → 0.6829**（差 0.0029）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/trend_brake/distance_to_line_pp`：**1.29 → 1.12**（差 -0.17）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/trend_brake/spread_pp`：**21.36 → 21.01**（差 -0.35）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/trend_brake/top2_max`：**0.9007 → 0.8989**（差 -0.0018）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/trend_brake/top2_min`：**0.6871 → 0.6888**（差 0.0017）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/vt08/distance_to_line_pp`：**3.79 → 3.15**（差 -0.64）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/vt08/spread_pp`：**12.39 → 11.2**（差 -1.19）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/vt08/top2_max`：**0.786 → 0.7805**（差 -0.0055）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/instrument/vt08/top2_min`：**0.6621 → 0.6685**（差 0.0064）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/0/annual_sum_pp`：**81.8427 → 81.3254**（差 -0.5173）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/0/delta_annual_sum_pp`：**-29.498 → -29.3843**（差 0.1137）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/0/delta_top2`：**0.022 → 0.0226**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/0/top2_share`：**0.7039 → 0.7084**（差 0.0045）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/1/annual_sum_pp`：**88.3893 → 88.0953**（差 -0.294）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/1/delta_annual_sum_pp`：**-22.9514 → -22.6144**（差 0.337）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/1/delta_top2`：**0.0702 → 0.0689**（差 -0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/1/top2_share`：**0.7521 → 0.7547**（差 0.0026）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/2/annual_sum_pp`：**102.6126 → 102.0988**（差 -0.5138）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/2/delta_annual_sum_pp`：**-8.7281 → -8.6109**（差 0.1172）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/2/delta_top2`：**0.0538 → 0.0536**（差 -0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/2/top2_share`：**0.7357 → 0.7394**（差 0.0037）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/3/annual_sum_pp`：**87.1348 → 86.5039**（差 -0.6309）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/3/delta_annual_sum_pp`：**-24.2059 → -24.2058**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/3/delta_top2`：**0.1131 → 0.115**（差 0.0019）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/derisk/mechanism/3/top2_share`：**0.795 → 0.8008**（差 0.0058）｜SECTION_ADVANCED｜这一节自己换了代：`derisk` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/one_open_late/mean_cny`：**-1798.153765058916 → -1782.9320396821006**（差 15.221725）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/one_open_late/median_cny`：**-932.3031683309355 → -929.179677596404**（差 3.123491）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/one_open_late/share_late_helps`：**0.41247002398081534 → 0.4138755980861244**（差 0.001406）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/one_open_late/t`：**-4.570838936445422 → -4.551322911619218**（差 0.019516）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/1/cost_cny_vs_today`：**1798.15 → 1782.93**（差 -15.22）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/1/mean_cny`：**-1798.153765058916 → -1782.9320396821006**（差 15.221725）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/1/share_late_helps`：**0.41247002398081534 → 0.4138755980861244**（差 0.001406）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/1/t`：**-4.570838936445422 → -4.551322911619218**（差 0.019516）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/2/cost_cny_vs_today`：**2637.54 → 2628.37**（差 -9.17）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/2/mean_cny`：**-2637.535644581885 → -2628.365344486415**（差 9.1703）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/2/share_late_helps`：**0.41586538461538464 → 0.4172661870503597**（差 0.001401）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/2/t`：**-4.822231717315911 → -4.818043693212478**（差 0.004188）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/3/cost_cny_vs_today`：**2912.47 → 2882.08**（差 -30.39）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/3/mean_cny`：**-2912.473314066595 → -2882.084463921774**（差 30.38885）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/3/share_late_helps`：**0.43132530120481927 → 0.4326923076923077**（差 0.001367）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/do_or_wait/table/3/t`：**-4.231648631666141 → -4.205498567925245**（差 0.02615）｜SECTION_ADVANCED｜这一节自己换了代：`do_or_wait` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/family_coherence/floor_extrapolation/gap_pp`：**0.145 → 0.05**（差 -0.095）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/floor_extrapolation/observed_pp`：**0.365 → 0.385**（差 0.02）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/floor_extrapolation/predicted_pp`：**0.22 → 0.335**（差 0.115）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/floor_extrapolation/tolerance_pp`：**0.081 → 0.172**（差 0.091）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/signflip/arms/2/cells_positive`：**0 → 3**（差 3）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/signflip/n_reject_standing`：**3 → 2**（差 -1）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、e6f9d0e81a64ec75 定价、今天按 0988c6530a481fa1 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/floor_provenance/grid/full|all/bars`：**1663 → 1664**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`floor_provenance` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/floor_provenance/grid/full|graded/bars`：**1663 → 1664**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`floor_provenance` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/floor_provenance/issuing_cell/bars`：**1663 → 1664**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`floor_provenance` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/beta`：**0.07453700153927338 → 0.07447081363455153**（差 -6.6e-05）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/capital_for_one_lot`：**11001515.798404276 → 11047549.500899909**（差 46033.702496）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/corr`：**0.14152934655175411 → 0.14138168578950164**（差 -0.000148）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/maxdd_delta_pp`：**-0.05412128425121843 → -0.053068306339809634**（差 0.001053）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/min_unit_notional`：**820020.0 → 822720.0**（差 2700.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/sharpe_delta`：**-0.020547817217357878 → -0.020974735979811476**（差 -0.000427）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/unit_over_target`：**11.001515798404277 → 11.04754950089991**（差 0.046034）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/variance_removable_pct`：**2.0030555935366516 → 1.998878107668137**（差 -0.004177）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/vol_delta_pp`：**-0.10119817508366241 → -0.10097200878734364**（差 0.000226）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/dsharpe`：**-0.020547817217357878 → -0.020974735979811476**（差 -0.000427）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/dsharpe_hi`：**0.0707691125152359 → 0.07410021845492577**（差 0.003331）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/dsharpe_lo`：**-0.09881020082682476 → -0.09867847461663937**（差 0.000132）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/share_above_uncond`：**0.9605 → 0.9685**（差 0.008）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/tail_ci_hi`：**0.8328393159433894 → 0.8414217707501334**（差 0.008582）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/tail_ci_lo`：**0.10957277748333087 → 0.12206311855461444**（差 0.01249）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/uncond_beta`：**0.07453700153927338 → 0.07447081363455153**（差 -6.6e-05）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/margin_pct_of_capital`：**3.8 → 3.7**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital`：**2.24 → 2.21**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital_by_mask/calendar`：**3.12 → 3.08**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital_by_mask/published`：**2.24 → 2.21**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital_by_mask/strictest`：**3.12 → 3.08**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/notional_x_capital_on_tier`：**0.26 → 0.25**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/one_lot_notional_cny`：**1275000.0 → 1243680.0**（差 -31320.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/stress_loss_pct_of_capital`：**10.7 → 10.4**（差 -0.3）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/vol_contrib_pct`：**5.7 → 5.6**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/notional_x_capital_on_tier`：**0.4 → 0.39**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/one_lot_notional_cny`：**1186980.0 → 1181700.0**（差 -5280.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/2/net_pct_of_capital_by_mask/calendar`：**2.23 → 2.24**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/2/one_lot_notional_cny`：**820020.0 → 822720.0**（差 2700.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/2/stress_loss_pct_of_capital`：**12.4 → 12.5**（差 0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/margin_pct_of_capital`：**3.8 → 3.7**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital`：**2.68 → 2.65**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/calendar`：**3.51 → 3.45**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/published`：**2.68 → 2.65**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/strictest`：**3.51 → 3.45**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/notional_x_capital_on_tier`：**0.25 → 0.24**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/one_lot_notional_cny`：**1255360.0 → 1221000.0**（差 -34360.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/stress_loss_pct_of_capital`：**10.4 → 10.2**（差 -0.2）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/vol_contrib_pct`：**6.3 → 6.1**（差 -0.2）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/notional_per_lot_cny`：**1275000.0 → 1243680.0**（差 -31320.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/1/notional_per_lot_cny`：**1186980.0 → 1181700.0**（差 -5280.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/2/notional_per_lot_cny`：**820020.0 → 822720.0**（差 2700.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/3/notional_per_lot_cny`：**1255360.0 → 1221000.0**（差 -34360.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/k_gap/account_base_gap_cny`：**28483.4 → 28525.2**（差 41.8）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/lots_at_rule`：**774 → 766**（差 -8）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/lots_ordered`：**726 → 719**（差 -7）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/next_lot_dk_pp`：**0.0007 → 0.0165**（差 0.0158）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/price`：**1.189 → 1.201**（差 0.012）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/short_cny`：**5707.2 → 5644.7**（差 -62.5）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/short_lots`：**48 → 47**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/cheapest_next_lot/short_shares`：**4800 → 4700**（差 -100）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/lots_at_rule`：**728 → 734**（差 6）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/lots_ordered`：**684 → 689**（差 5）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/next_lot_dk_pp`：**0.0383 → 0.0435**（差 0.0052）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/price`：**1.263 → 1.254**（差 -0.009）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/short_cny`：**5557.2 → 5643.0**（差 85.8）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/short_lots`：**44 → 45**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/0/short_shares`：**4400 → 4500**（差 100）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/lots_at_rule`：**774 → 766**（差 -8）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/lots_ordered`：**726 → 719**（差 -7）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/next_lot_dk_pp`：**0.0007 → 0.0165**（差 0.0158）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/price`：**1.189 → 1.201**（差 0.012）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/short_cny`：**5707.2 → 5644.7**（差 -62.5）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/short_lots`：**48 → 47**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/1/short_shares`：**4800 → 4700**（差 -100）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/lots_at_rule`：**459 → 467**（差 8）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/lots_ordered`：**431 → 438**（差 7）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/next_lot_dk_pp`：**0.0669 → 0.022**（差 -0.0449）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/price`：**2.004 → 1.97**（差 -0.034）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/short_cny`：**5611.2 → 5713.0**（差 101.8）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/short_lots`：**28 → 29**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/2/short_shares`：**2800 → 2900**（差 100）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/3/lots_at_rule`：**803 → 800**（差 -3）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/3/lots_ordered`：**754 → 751**（差 -3）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/3/next_lot_dk_pp`：**0.0043 → 0.0205**（差 0.0162）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/3/price`：**1.145 → 1.15**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/3/short_cny`：**5610.5 → 5635.0**（差 24.5）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/4/lots_at_rule`：**528 → 525**（差 -3）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/4/lots_ordered`：**496 → 493**（差 -3）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/4/next_lot_dk_pp`：**0.0444 → 0.0302**（差 -0.0142）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/4/price`：**1.741 → 1.751**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/rows/4/short_cny`：**5571.2 → 5603.2**（差 32.0）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/short_share_of_book_pct`：**6.0961 → 6.1355**（差 0.0394）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/k_gap/short_total_cny`：**28057.3 → 28238.9**（差 181.6）｜SECTION_ADVANCED｜这一节自己换了代：`k_gap` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/AU`：**2796666.666666667 → 2768533.3333333335**（差 -28133.333333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IC`：**4250000.0 → 4145600.0**（差 -104400.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IF`：**3956600.0 → 3939000.0**（差 -17600.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IH`：**2733400.0 → 2742400.0**（差 9000.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IM`：**4184533.3333333335 → 4070000.0**（差 -114533.333333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/SC`：**2085000.0 → 2069333.3333333335**（差 -15666.666667）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/T`：**3668166.666666667 → 3658500.0**（差 -9666.666667）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/TF`：**3558666.666666667 → 3555333.3333333335**（差 -3333.333333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/TS`：**6842400.0 → 6842133.333333334**（差 -266.666667）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/AU`：**0.839 → 0.83056**（差 -0.00844）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IC`：**1.275 → 1.24368**（差 -0.03132）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IF`：**1.18698 → 1.1817**（差 -0.00528）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IH`：**0.82002 → 0.82272**（差 0.0027）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IM`：**1.25536 → 1.221**（差 -0.03436）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/SC`：**0.6255 → 0.6208**（差 -0.0047）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/T`：**1.10045 → 1.09755**（差 -0.0029）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/TF`：**1.0676 → 1.0666**（差 -0.001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/TS`：**2.05272 → 2.05264**（差 -8e-05）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/permission/allowed_cny`：**431770.0 → 431728.0**（差 -42.0）｜SECTION_ADVANCED｜这一节自己换了代：`permission` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/permission/ordered_cny`：**431769.6 → 431727.8**（差 -41.8）｜SECTION_ADVANCED｜这一节自己换了代：`permission` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/cny_total`：**3627.42 → 2795.26**（差 -832.16）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/0/amount_cny`：**86389.2 → 86400.6**（差 11.4）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/0/latest_pctile`：**3.8127090301003346 → 1.2032085561497325**（差 -2.6095）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/0/same_bucket_move_cny`：**841.3711283890027 → 841.4821565136252**（差 0.111028）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/1/amount_cny`：**86321.4 → 86351.9**（差 30.5）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/1/latest_pctile`：**17.900262467191602 → 59.28646379853095**（差 41.386201）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/1/mean_pct`：**0.3792060133771917 → 0.1136316784152153**（差 -0.265574）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/1/n`：**353 → 770**（差 417）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/1/same_bucket_move_cny`：**327.3359396313791 → 98.12311331342829**（差 -229.212826）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/1/t`：**1.087252826971886 → 0.38385105751885035**（差 -0.703402）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/2/amount_cny`：**86372.4 → 86286.0**（差 -86.4）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/2/latest_pctile`：**96.64292980671414 → 90.7520325203252**（差 -5.890897）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/2/mean_pct`：**0.2489448117886486 → 0.23910384745233929**（差 -0.009841）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/2/n`：**266 → 267**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/2/same_bucket_move_cny`：**215.01960861733872 → 206.31314581272548**（差 -8.706463）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/2/t`：**0.915981747529712 → 0.8825032886927169**（差 -0.033478）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/3/amount_cny`：**86333.0 → 86365.0**（差 32.0）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/3/latest_pctile`：**11.80451127819549 → 19.30879038317055**（差 7.504279）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/3/same_bucket_move_cny`：**460.222132074456 → 460.3927169982555**（差 0.170585）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/4/amount_cny`：**86353.6 → 86324.3**（差 -29.3）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/4/latest_pctile`：**6.338939197930142 → 14.728682170542635**（差 8.389743）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/4/mean_pct`：**2.065312175367106 → 1.3772998496472701**（差 -0.688012）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/4/n`：**107 → 172**（差 65）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/4/same_bucket_move_cny`：**1783.4714146678095 → 1188.9444541090584**（差 -594.526961）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/premium_forward/rows/4/t`：**3.899475787273565 → 4.544192330848934**（差 0.644717）｜SECTION_ADVANCED｜这一节自己换了代：`premium_forward` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/roster_audit/local_copies/0/laneside/value`：**187 → 185**（差 -2）｜QUOTED_FROM_SOURCE｜这个数不是这页算的：`results/ah_panel_status.json:fresh_pairs` 现在读 185，与今天印的 185 相同——页只是转抄，动的是被引用的那张面
- `/vol_target_gate/arms/0/cagr_pct`：**14.16 → 14.05**（差 -0.11）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/0/sharpe`：**0.943 → 0.938**（差 -0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/1/cagr_pct`：**8.51 → 8.43**（差 -0.08）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/1/sharpe`：**0.884 → 0.877**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/2/cagr_pct`：**6.44 → 6.3**（差 -0.14）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/2/sharpe`：**0.849 → 0.842**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/3/cagr_pct`：**4.32 → 4.22**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/3/sharpe`：**0.819 → 0.812**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/4/cagr_pct`：**3.25 → 3.19**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/4/sharpe`：**0.819 → 0.812**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/5/cagr_pct`：**2.18 → 2.13**（差 -0.05）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/arms/5/sharpe`：**0.819 → 0.812**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/capacity_cny`：**39783633.0 → 27645948.0**（差 -12137685.0）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/max_abs_delta`：**0.852698 → 0.85295**（差 0.000252）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_by_arm/unscaled`：**4.665973 → 4.654482**（差 -0.011491）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_by_arm/vt02`：**4.60859 → 4.623249**（差 0.014659）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_by_arm/vt03`：**4.567272 → 4.570829**（差 0.003557）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_by_arm/vt04`：**4.581703 → 4.603678**（差 0.021975）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_by_arm/vt06`：**4.853644 → 4.874988**（差 0.021344）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_by_arm/vt08`：**4.974762 → 4.995503**（差 0.020741）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_target_gate/shape/effective_years/median_range`：**0.40749 → 0.424674**（差 0.017184）｜SECTION_ADVANCED｜这一节自己换了代：`vol_target_gate` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_ladder/best_sharpe/cagr_pct`：**0.1155 → 0.1145**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_ladder/best_sharpe/sharpe`：**1.137 → 1.129**（差 -0.008）｜SECTION_ADVANCED｜这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_ladder/tightest_admit/cagr_pct`：**0.1429 → 0.1417**（差 -0.0012）｜SECTION_ADVANCED｜这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_ladder/tightest_admit/sharpe`：**0.993 → 0.987**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vt_ladder` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/answer/reference_top2_median`：**1.5307 → 1.5952**（差 0.0645）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/0/margin_to_line`：**-0.0806 → -0.0757**（差 0.0049）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/0/spread`：**0.101 → 0.0962**（差 -0.0048）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/0/top2_max`：**0.7806 → 0.7757**（差 -0.0049）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/0/top2_min`：**0.6796 → 0.6795**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/0/top2_vs_reference`：**0.51 → 0.4863**（差 -0.0237）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/1/margin_to_line`：**-0.1717 → -0.164**（差 0.0077）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/1/spread`：**0.1678 → 0.1556**（差 -0.0122）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/1/top2_max`：**0.8717 → 0.864**（差 -0.0077）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/1/top2_min`：**0.7039 → 0.7084**（差 0.0045）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/1/top2_vs_reference`：**0.5695 → 0.5416**（差 -0.0279）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/2/margin_to_line`：**-0.1848 → -0.1768**（差 0.008）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/2/spread`：**0.1669 → 0.1542**（差 -0.0127）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/2/top2_max`：**0.8848 → 0.8768**（差 -0.008）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/2/top2_min`：**0.7179 → 0.7226**（差 0.0047）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/2/top2_vs_reference`：**0.578 → 0.5496**（差 -0.0284）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/3/margin_to_line`：**-0.1833 → -0.1759**（差 0.0074）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/3/spread`：**0.1703 → 0.1583**（差 -0.012）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/3/top2_max`：**0.8833 → 0.8759**（差 -0.0074）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/3/top2_min`：**0.713 → 0.7176**（差 0.0046）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/3/top2_vs_reference`：**0.5771 → 0.5491**（差 -0.028）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/4/margin_to_line`：**-0.146 → -0.1399**（差 0.0061）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/4/spread`：**0.1728 → 0.1625**（差 -0.0103）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/4/top2_max`：**0.846 → 0.8399**（差 -0.0061）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/4/top2_min`：**0.6732 → 0.6774**（差 0.0042）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/4/top2_vs_reference`：**0.5527 → 0.5265**（差 -0.0262）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/5/margin_to_line`：**-0.1004 → -0.0953**（差 0.0051）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/5/spread`：**0.1329 → 0.1238**（差 -0.0091）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/5/top2_max`：**0.8004 → 0.7953**（差 -0.0051）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/5/top2_min`：**0.6675 → 0.6715**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/5/top2_vs_reference`：**0.5229 → 0.4986**（差 -0.0243）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/6/margin_to_line`：**-0.0908 → -0.0858**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/6/spread`：**0.1113 → 0.1056**（差 -0.0057）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/6/top2_max`：**0.7908 → 0.7858**（差 -0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/6/top2_min`：**0.6795 → 0.6802**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/books/6/top2_vs_reference`：**0.5166 → 0.4926**（差 -0.024）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/drop_two/book_retained_max`：**0.7032 → 0.6957**（差 -0.0075）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/drop_two/book_retained_min`：**0.1029 → 0.1114**（差 0.0085）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/drop_two/reference_retained/0`：**-0.6185 → -0.7362**（差 -0.1177）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/drop_two/reference_retained/1`：**-0.6116 → -0.7274**（差 -0.1158）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/drop_two/reference_retained/2`：**-0.5849 → -0.6934**（差 -0.1085）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/drop_two/reference_retained/3`：**-0.5732 → -0.6786**（差 -0.1054）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/reference/cagr_pct`：**0.0428 → 0.0399**（差 -0.0029）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/reference/top2_max`：**1.5464 → 1.6134**（差 0.067）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/reference/top2_median`：**1.5307 → 1.5952**（差 0.0645）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vt_phases/reference/top2_min`：**1.5112 → 1.5724**（差 0.0612）｜SECTION_ADVANCED｜这一节自己换了代：`vt_phases` 2026-11-13 → 2026-11-16（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json

同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；没有这两条说明的，就是这页偷偷换了数。

## 还有哪些节在同 bar 上改了数（23 个）

- `lot_floor`：18 个
- `futures_sleeve`：4 个
- `admission`：1 个

这几节的位移**没有任何解释**（不是转抄、不是换输入、不是换代）。页要在同一根 bar 上改这些数，就得自己写出理由；写不出来，读的人就分不清「今天变了」和「口径变了」。

## 怎么读

- `CLOCK`＝钟面（`age_h`/`silent_h`/`lag_days` 这类）：没有新 bar 也该走，不构成问题；但它的存在说明「哪些数允许自己走」是**名单制**的，名单写在本脚本顶部，不由数据推出来。
- `DATA_ADVANCED`＝数据推进了，所有定价读数都允许动。
- `RECOVERED_OLD_VALUE`＝昨天那个数今天还在页上，只是换了名字——那是**改名**不是重算；读的人必须知道这一点，否则会把「口径换了」读成「今天变了」。
- `DECLARED_RULER`＝同一块里的口径句（`ruler`/`basis`/`convention`）改了，位移由它自己声明；句子改了而读者没看见，等于数被悄悄换了定义。
- `SECTION_ADVANCED`＝这一**节**自己换了代（标题那根 bar 两天相同，这一节不同，按 `results/live_book_section_bars.json` 判）：不是同 bar 重算漂移，而是页面里混着两代数据（页面本身另有 `PAGE_MIXES_BARS` 面在报）。
- `INPUT_IDENTITY_CHANGED`＝这一节**拿什么算**变了：它在自己身上写下的面板指纹（16 位十六进制）两天不同。族面是按「几个臂已重算」分批定价的，换一批臂，同一根 bar 上这一节的数就会动——这是它自己的输入变了，不是它在同一天改了口径。本档与 `DECLARED_RULER` 同一弱点：它信的是这一节自己的宣告，不独立复算。
- `QUOTED_FROM_SOURCE`＝这个数不是这页算的：它的块里写着 `source`（如`results/x.json:fresh_pairs`），而那个文件**现在**读到的值正好等于今天印的值。页只是转抄，动的是被引用的那张面（另一条车道）；写这张面的人不是改数的人。
- `UNEXPLAINED`＝既没有旧值留存、也没有口径声明——**这一档非零就是本面要报的事**。

## 未验证（如实）

- 只比**相邻两天**：更早的口径变更若在两页之前发生，本面看不见（可手工指定更多日页，未做）。
- 「旧值仍在」靠数值相等判定（相对 1e-9）：两个无关的数恰好相等的概率不低，所以 `RECOVERED_OLD_VALUE` 是**线索**不是证明，行里同时印出它在哪个键上，供人核。
- 钟面名单是写死的：新出现的钟面字段会被算成 `MOVED`，本面会如实报（宁可多报）。
- 本面不判「这个改动是否合理」，也不碰任何生产件；它只读已发布日页。
