# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261117.json` → `LIVE-BOOK-20261118.json`
- 价格依据：2026-11-17（前一天 2026-11-17）｜数据截止：2026-11-17（前一天 2026-11-17）
- 判决：**UNEXPLAINED_MOVES**

## 一句话
两天**是同一根 bar**（没有新数据进来），这页有 **98** 个数变了；其中 **6** 个是钟面（机器多久没说话之类，本来就该走）、**80** 个能给出解释（旧数还在页上／口径句改了／这一节换了代／这一节换了定价的输入／这个数只是转抄别面）、**12** 个没解释。新增 **17** 个数字叶子、消失 **3** 个。

## 动的数（全部 98 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/authority/owner_silent_h` | 23.8 | 25.5 | CLOCK |  |
| `/causal_rebuild/elapsed_sec` | 129.9 | 81.5 | CLOCK |  |
| `/family_coherence/floor_extrapolation/gap_pp` | -0.398 | -0.085 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、0d5a9cdcf2beffd5 定价、今天按 0d5a9cdcf2beffd5 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/floor_extrapolation/predicted_pp` | 0.908 | 0.595 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、0d5a9cdcf2beffd5 定价、今天按 0d5a9cdcf2beffd5 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/family_coherence/floor_extrapolation/tolerance_pp` | 2.42 | 2.582 | INPUT_IDENTITY_CHANGED | 这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、0d5a9cdcf2beffd5 定价、今天按 0d5a9cdcf2beffd5 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数 |
| `/fleet/rows/0/age_h` | 20.65 | 24.53 | CLOCK |  |
| `/fleet/rows/1/age_h` | 439.58 | 443.46 | CLOCK |  |
| `/fleet/rows/2/age_h` | 1.98 | 0.56 | CLOCK |  |
| `/futures_hedge/beta` | 0.07447081363455153 | 0.07458300567364223 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/capital_for_one_lot` | 11047549.500899909 | 10979444.882970085 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/corr` | 0.14138168578950164 | 0.1415643988218339 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/maxdd_delta_pp` | -0.053068306339809634 | -0.05485315943003499 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/min_unit_notional` | 822720.0 | 818880.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/sharpe_delta` | -0.020974735979811476 | -0.020536000001067034 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/unit_over_target` | 11.04754950089991 | 10.979444882970085 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/variance_removable_pct` | 1.998878107668137 | 2.004047901378724 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge/vol_delta_pp` | -0.10097200878734364 | -0.10122922788117772 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/dsharpe` | -0.020974735979811476 | -0.020536000001067034 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/dsharpe_hi` | 0.07410021845492577 | 0.0719002244924948 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/dsharpe_lo` | -0.09867847461663937 | -0.0964202006837476 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/share_above_uncond` | 0.9685 | 0.9695 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/tail_ci_hi` | 0.8414217707501334 | 0.8405742148706478 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/tail_ci_lo` | 0.12206311855461444 | 0.13021062460324065 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_hedge_tail/uncond_beta` | 0.07447081363455153 | 0.07458300567364223 | SECTION_ADVANCED | 这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IC/calendar_ann_pct` | 9.793 | 9.805 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IC/gap_pp` | 6.898 | 6.927 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IC/kept_by_both_ann_pct` | 9.837 | 9.848 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IC/missed_roll_days_ann_pct` | -144.773 | -145.466 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IC/published_ann_pct` | 2.895 | 2.878 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IC/strictest_ann_pct` | 9.837 | 9.848 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IF/calendar_ann_pct` | 5.795 | 5.843 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IF/gap_pp` | 3.872 | 3.967 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IF/kept_by_both_ann_pct` | 6.5 | 6.548 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IF/missed_roll_days_ann_pct` | -91.585 | -93.598 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IF/published_ann_pct` | 1.923 | 1.876 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IF/strictest_ann_pct` | 6.5 | 6.548 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IH/calendar_ann_pct` | 5.324 | 5.39 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IH/gap_pp` | 3.707 | 3.829 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IH/kept_by_both_ann_pct` | 5.135 | 5.202 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IH/missed_roll_days_ann_pct` | -72.838 | -75.52 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IH/published_ann_pct` | 1.617 | 1.561 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IH/strictest_ann_pct` | 5.135 | 5.202 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IM/calendar_ann_pct` | 11.954 | 12.013 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IM/gap_pp` | 6.026 | 6.131 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IM/kept_by_both_ann_pct` | 11.562 | 11.623 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IM/missed_roll_days_ann_pct` | -126.203 | -128.902 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IM/published_ann_pct` | 5.928 | 5.882 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/dilution/pairs/IM/strictest_ann_pct` | 11.562 | 11.623 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital` | 2.22 | 2.21 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital_by_mask/calendar` | 3.08 | 3.07 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital_by_mask/published` | 2.22 | 2.21 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/net_pct_of_capital_by_mask/strictest` | 3.08 | 3.07 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/0/one_lot_notional_cny` | 1243680.0 | 1238960.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/net_pct_of_capital` | 1.42 | 1.4 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/net_pct_of_capital_by_mask/calendar` | 2.55 | 2.56 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/net_pct_of_capital_by_mask/published` | 1.42 | 1.4 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/one_lot_notional_cny` | 1181700.0 | 1175460.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/1/stress_loss_pct_of_capital` | 18.0 | 17.9 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/2/one_lot_notional_cny` | 822720.0 | 818880.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/2/stress_loss_pct_of_capital` | 12.5 | 12.4 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/margin_pct_of_capital` | 3.7 | 3.6 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital` | 2.66 | 2.63 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/calendar` | 3.45 | 3.42 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/published` | 2.66 | 2.63 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/strictest` | 3.45 | 3.42 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/one_lot_notional_cny` | 1221000.0 | 1204600.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/stress_loss_pct_of_capital` | 10.2 | 10.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/carry_caliber/calendar_ann_pct` | 9.793 | 9.805 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/0/carry_caliber/published_ann_pct` | 2.895 | 2.878 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/0/carry_caliber/spread_pp` | 6.898 | 6.927 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/1/carry_caliber/calendar_ann_pct` | 5.795 | 5.843 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/1/carry_caliber/published_ann_pct` | 1.923 | 1.876 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/1/carry_caliber/spread_pp` | 3.872 | 3.967 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/2/carry_caliber/calendar_ann_pct` | 5.324 | 5.39 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/2/carry_caliber/published_ann_pct` | 1.617 | 1.561 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/2/carry_caliber/spread_pp` | 3.707 | 3.829 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/3/carry_caliber/calendar_ann_pct` | 11.954 | 12.013 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/3/carry_caliber/published_ann_pct` | 5.928 | 5.882 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_sleeve/rows/3/carry_caliber/spread_pp` | 6.026 | 6.131 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/gap/elapsed_sec` | 82.4 | 81.8 | CLOCK |  |
| `/lot_floor/capital_needed/AU` | 2768533.3333333335 | 2782200.0 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/IC` | 4145600.0 | 4129866.666666667 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/IF` | 3939000.0 | 3918200.0 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/IH` | 2742400.0 | 2729600.0 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/IM` | 4070000.0 | 4015333.3333333335 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/SC` | 2069333.3333333335 | 1938000.0 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/T` | 3658500.0 | 3667000.0 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/TF` | 3555333.3333333335 | 3559333.3333333335 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/capital_needed/TS` | 6842133.333333334 | 6843066.666666667 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/AU` | 0.83056 | 0.83466 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/IC` | 1.24368 | 1.23896 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/IF` | 1.1817 | 1.17546 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/IH` | 0.82272 | 0.81888 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/IM` | 1.221 | 1.2046 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/SC` | 0.6208 | 0.5814 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/T` | 1.09755 | 1.1001 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/TF` | 1.0666 | 1.0678 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lot_floor/shares_at_1m/TS` | 2.05264 | 2.05292 | SECTION_ADVANCED | 这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |

## 今天没有了的数（3 个，列前 40）

- `/family_coherence/panels_detail/1/bars`
- `/family_coherence/panels_detail/1/bars_fewer_than_newest`
- `/family_coherence/panels_detail/1/columns`

## 今天新出现的数（17 个）落在这几块上

- `/capacity_ticket/one_lot_floor_cny`
- `/capacity_ticket/rungs`
- `/capacity_ticket/shortfall_to_typical_cny`

## 钱的两处（同一根 bar 上改了定价口径）

- `/family_coherence/floor_extrapolation/gap_pp`：**-0.398 → -0.085**（差 0.313）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、0d5a9cdcf2beffd5 定价、今天按 0d5a9cdcf2beffd5 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/floor_extrapolation/predicted_pp`：**0.908 → 0.595**（差 -0.313）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、0d5a9cdcf2beffd5 定价、今天按 0d5a9cdcf2beffd5 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/family_coherence/floor_extrapolation/tolerance_pp`：**2.42 → 2.582**（差 0.162）｜INPUT_IDENTITY_CHANGED｜这一节的输入身份变了：`family_coherence` 昨天按 0988c6530a481fa1、0d5a9cdcf2beffd5 定价、今天按 0d5a9cdcf2beffd5 定价——数字换的是「拿什么算的」，不是同一根 bar 上的读数
- `/futures_hedge/beta`：**0.07447081363455153 → 0.07458300567364223**（差 0.000112）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/capital_for_one_lot`：**11047549.500899909 → 10979444.882970085**（差 -68104.61793）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/corr`：**0.14138168578950164 → 0.1415643988218339**（差 0.000183）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/maxdd_delta_pp`：**-0.053068306339809634 → -0.05485315943003499**（差 -0.001785）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/min_unit_notional`：**822720.0 → 818880.0**（差 -3840.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/sharpe_delta`：**-0.020974735979811476 → -0.020536000001067034**（差 0.000439）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/unit_over_target`：**11.04754950089991 → 10.979444882970085**（差 -0.068105）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/variance_removable_pct`：**1.998878107668137 → 2.004047901378724**（差 0.00517）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/vol_delta_pp`：**-0.10097200878734364 → -0.10122922788117772**（差 -0.000257）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/dsharpe`：**-0.020974735979811476 → -0.020536000001067034**（差 0.000439）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/dsharpe_hi`：**0.07410021845492577 → 0.0719002244924948**（差 -0.0022）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/dsharpe_lo`：**-0.09867847461663937 → -0.0964202006837476**（差 0.002258）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/share_above_uncond`：**0.9685 → 0.9695**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/tail_ci_hi`：**0.8414217707501334 → 0.8405742148706478**（差 -0.000848）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/tail_ci_lo`：**0.12206311855461444 → 0.13021062460324065**（差 0.008148）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge_tail/uncond_beta`：**0.07447081363455153 → 0.07458300567364223**（差 0.000112）｜SECTION_ADVANCED｜这一节自己换了代：`futures_hedge_tail` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IC/calendar_ann_pct`：**9.793 → 9.805**（差 0.012）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IC/gap_pp`：**6.898 → 6.927**（差 0.029）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IC/kept_by_both_ann_pct`：**9.837 → 9.848**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IC/missed_roll_days_ann_pct`：**-144.773 → -145.466**（差 -0.693）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IC/published_ann_pct`：**2.895 → 2.878**（差 -0.017）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IC/strictest_ann_pct`：**9.837 → 9.848**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IF/calendar_ann_pct`：**5.795 → 5.843**（差 0.048）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IF/gap_pp`：**3.872 → 3.967**（差 0.095）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IF/kept_by_both_ann_pct`：**6.5 → 6.548**（差 0.048）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IF/missed_roll_days_ann_pct`：**-91.585 → -93.598**（差 -2.013）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IF/published_ann_pct`：**1.923 → 1.876**（差 -0.047）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IF/strictest_ann_pct`：**6.5 → 6.548**（差 0.048）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IH/calendar_ann_pct`：**5.324 → 5.39**（差 0.066）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IH/gap_pp`：**3.707 → 3.829**（差 0.122）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IH/kept_by_both_ann_pct`：**5.135 → 5.202**（差 0.067）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IH/missed_roll_days_ann_pct`：**-72.838 → -75.52**（差 -2.682）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IH/published_ann_pct`：**1.617 → 1.561**（差 -0.056）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IH/strictest_ann_pct`：**5.135 → 5.202**（差 0.067）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IM/calendar_ann_pct`：**11.954 → 12.013**（差 0.059）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IM/gap_pp`：**6.026 → 6.131**（差 0.105）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IM/kept_by_both_ann_pct`：**11.562 → 11.623**（差 0.061）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IM/missed_roll_days_ann_pct`：**-126.203 → -128.902**（差 -2.699）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IM/published_ann_pct`：**5.928 → 5.882**（差 -0.046）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/dilution/pairs/IM/strictest_ann_pct`：**11.562 → 11.623**（差 0.061）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital`：**2.22 → 2.21**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital_by_mask/calendar`：**3.08 → 3.07**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital_by_mask/published`：**2.22 → 2.21**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/net_pct_of_capital_by_mask/strictest`：**3.08 → 3.07**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/0/one_lot_notional_cny`：**1243680.0 → 1238960.0**（差 -4720.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/net_pct_of_capital`：**1.42 → 1.4**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/net_pct_of_capital_by_mask/calendar`：**2.55 → 2.56**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/net_pct_of_capital_by_mask/published`：**1.42 → 1.4**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/one_lot_notional_cny`：**1181700.0 → 1175460.0**（差 -6240.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/1/stress_loss_pct_of_capital`：**18.0 → 17.9**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/2/one_lot_notional_cny`：**822720.0 → 818880.0**（差 -3840.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/2/stress_loss_pct_of_capital`：**12.5 → 12.4**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/margin_pct_of_capital`：**3.7 → 3.6**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital`：**2.66 → 2.63**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/calendar`：**3.45 → 3.42**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/published`：**2.66 → 2.63**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/strictest`：**3.45 → 3.42**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/one_lot_notional_cny`：**1221000.0 → 1204600.0**（差 -16400.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/stress_loss_pct_of_capital`：**10.2 → 10.0**（差 -0.2）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/carry_caliber/calendar_ann_pct`：**9.793 → 9.805**（差 0.012）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/0/carry_caliber/published_ann_pct`：**2.895 → 2.878**（差 -0.017）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/0/carry_caliber/spread_pp`：**6.898 → 6.927**（差 0.029）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/1/carry_caliber/calendar_ann_pct`：**5.795 → 5.843**（差 0.048）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/1/carry_caliber/published_ann_pct`：**1.923 → 1.876**（差 -0.047）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/1/carry_caliber/spread_pp`：**3.872 → 3.967**（差 0.095）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/2/carry_caliber/calendar_ann_pct`：**5.324 → 5.39**（差 0.066）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/2/carry_caliber/published_ann_pct`：**1.617 → 1.561**（差 -0.056）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/2/carry_caliber/spread_pp`：**3.707 → 3.829**（差 0.122）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/3/carry_caliber/calendar_ann_pct`：**11.954 → 12.013**（差 0.059）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/3/carry_caliber/published_ann_pct`：**5.928 → 5.882**（差 -0.046）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_sleeve/rows/3/carry_caliber/spread_pp`：**6.026 → 6.131**（差 0.105）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/AU`：**2768533.3333333335 → 2782200.0**（差 13666.666667）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/IC`：**4145600.0 → 4129866.666666667**（差 -15733.333333）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/IF`：**3939000.0 → 3918200.0**（差 -20800.0）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/IH`：**2742400.0 → 2729600.0**（差 -12800.0）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/IM`：**4070000.0 → 4015333.3333333335**（差 -54666.666667）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/SC`：**2069333.3333333335 → 1938000.0**（差 -131333.333333）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/T`：**3658500.0 → 3667000.0**（差 8500.0）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/TF`：**3555333.3333333335 → 3559333.3333333335**（差 4000.0）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/capital_needed/TS`：**6842133.333333334 → 6843066.666666667**（差 933.333333）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/AU`：**0.83056 → 0.83466**（差 0.0041）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/IC`：**1.24368 → 1.23896**（差 -0.00472）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/IF`：**1.1817 → 1.17546**（差 -0.00624）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/IH`：**0.82272 → 0.81888**（差 -0.00384）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/IM`：**1.221 → 1.2046**（差 -0.0164）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/SC`：**0.6208 → 0.5814**（差 -0.0394）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/T`：**1.09755 → 1.1001**（差 0.00255）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/TF`：**1.0666 → 1.0678**（差 0.0012）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lot_floor/shares_at_1m/TS`：**2.05264 → 2.05292**（差 0.00028）｜SECTION_ADVANCED｜这一节自己换了代：`lot_floor` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json

同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；没有这两条说明的，就是这页偷偷换了数。

## 还有哪些节在同 bar 上改了数（12 个）

- `futures_sleeve`：12 个

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
