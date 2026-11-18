# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261117.json` → `LIVE-BOOK-20261118.json`
- 价格依据：2026-11-17（前一天 2026-11-17）｜数据截止：2026-11-17（前一天 2026-11-17）
- 判决：**UNEXPLAINED_MOVES**

## 一句话
两天**是同一根 bar**（没有新数据进来），这页有 **67** 个数变了；其中 **5** 个是钟面（机器多久没说话之类，本来就该走）、**1** 个能给出解释（旧数还在页上／口径句改了／这一节换了代／这一节换了定价的输入／这个数只是转抄别面）、**61** 个没解释。新增 **260** 个数字叶子、消失 **0** 个。

## 动的数（全部 67 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/cash_caliber/control_error_bp` | 0.0043 | 0.1143 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/annual_cny` | 10067.0 | 10073.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/gap_vs_spot_bp` | -59.7 | -59.81 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/gap_vs_spot_cny` | -3392.0 | -3398.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/pct` | 1.772 | 1.7731 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/book/cny` | 579.0 | 580.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/book/pct` | 1.772 | 1.7731 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/gap_bp` | 85.77 | 85.88 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/gap_bp_gross` | 59.7 | 59.81 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/gap_cny` | 280.0 | 281.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/causal_rebuild/elapsed_sec` | 50.0 | 81.5 | CLOCK |  |
| `/fleet/rows/0/age_h` | 1.24 | 0.24 | CLOCK |  |
| `/fleet/rows/1/age_h` | 441.79 | 451.8 | CLOCK |  |
| `/fleet/rows/2/age_h` | 4.18 | 0.44 | CLOCK |  |
| `/futures_hedge/beta` | 0.07185718963947142 | 0.07458300567364223 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/capital_for_one_lot` | 11395936.91471321 | 10979444.882970085 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/corr` | 0.1373365917783091 | 0.1415643988218339 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/maxdd_delta_pp` | 1.5453866010586514 | -0.05485315943003499 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/sharpe_delta` | 0.005735999804863057 | -0.020536000001067034 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/splice_days_dropped` | 1 | 85 | RECOVERED_OLD_VALUE | 昨天的 1 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_pairs`（改名，不是重算） |
| `/futures_hedge/unit_over_target` | 11.395936914713209 | 10.979444882970085 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/variance_removable_pct` | 1.8861339441281915 | 2.004047901378724 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/vol_delta_pp` | -0.09457028960696418 | -0.10122922788117772 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/dsharpe` | 0.005735999804863057 | -0.020536000001067034 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/dsharpe_hi` | 0.09446056903527693 | 0.0719002244924948 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/dsharpe_lo` | -0.06366444689345857 | -0.0964202006837476 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/share_above_uncond` | 0.968 | 0.9695 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_beta` | 0.6115545672996576 | 0.6126419583867959 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_ci_hi` | 0.8343491781619469 | 0.8405742148706478 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_ci_lo` | 0.12672451800387655 | 0.13021062460324065 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_n` | 57 | 52 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/uncond_beta` | 0.07185718963947142 | 0.07458300567364223 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_ladder/declared/cash_rate_pct` | 1.326 | 1.327 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
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
| `/gap/elapsed_sec` | 48.7 | 81.8 | CLOCK |  |
| `/idle_cash/vehicle_net_pct` | 1.772 | 1.7731 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/cny_total` | 3322.86 | 3913.6 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/0/latest_pctile` | 15.6312625250501 | 0.5344021376085505 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/0/mean_pct` | 0.5223345213939685 | 0.9739309177408781 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/0/n` | 262 | 134 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/0/same_bucket_move_cny` | 451.0243678642211 | 840.967920989058 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/0/t` | 1.9314301221169548 | 2.48618543532154 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/1/latest_pctile` | 63.188253801782906 | 78.91976927110645 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/1/mean_pct` | 0.1136316784152153 | 0.3459749989108973 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/1/n` | 770 | 394 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/1/same_bucket_move_cny` | 98.20186006657005 | 298.9957457587844 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/1/t` | 0.38385105751885035 | 0.9685142995814702 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/2/latest_pctile` | 87.10659898477158 | 82.74111675126903 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/3/latest_pctile` | 19.894894894894893 | 14.33933933933934 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_forward/rows/4/latest_pctile` | 13.161290322580646 | 11.741935483870968 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/defects/0/disk_n` | 5222 | 5221 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/0/declared_n` | 210 | 211 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/0/laneside/local_disk_n` | 186 | 187 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/0/local_disk_n` | 186 | 187 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/1/laneside/local_disk_n` | 27 | 1 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/1/local_disk_n` | 27 | 1 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |

## 今天新出现的数（260 个）落在这几块上

- `/alias_stability/crosscheck`
- `/alias_stability/families`
- `/alias_stability/stability`
- `/capacity_edge/criteria`
- `/capacity_edge/summary`
- `/capacity_ticket/one_lot_floor_cny`
- `/capacity_ticket/rungs`
- `/capacity_ticket/shortfall_to_typical_cny`
- `/derisk/instrument`
- `/derisk/n_phases`
- `/supply_capacity/ceiling_cny`
- `/supply_capacity/floor_cny`
- `/supply_capacity/gap_cny`
- `/supply_capacity/share_of_floor`
- `/width_fit/line_pct`
- `/width_fit/min_width`
- `/width_fit/rows`

## 钱的两处（同一根 bar 上改了定价口径）

- `/cash_caliber/control_error_bp`：**0.0043 → 0.1143**（差 0.11）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/annual_cny`：**10067.0 → 10073.0**（差 6.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/gap_vs_spot_bp`：**-59.7 → -59.81**（差 -0.11）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/gap_vs_spot_cny`：**-3392.0 → -3398.0**（差 -6.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/pct`：**1.772 → 1.7731**（差 0.0011）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/book/cny`：**579.0 → 580.0**（差 1.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/book/pct`：**1.772 → 1.7731**（差 0.0011）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/gap_bp`：**85.77 → 85.88**（差 0.11）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/gap_bp_gross`：**59.7 → 59.81**（差 0.11）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/gap_cny`：**280.0 → 281.0**（差 1.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/beta`：**0.07185718963947142 → 0.07458300567364223**（差 0.002726）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/capital_for_one_lot`：**11395936.91471321 → 10979444.882970085**（差 -416492.031743）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/corr`：**0.1373365917783091 → 0.1415643988218339**（差 0.004228）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/maxdd_delta_pp`：**1.5453866010586514 → -0.05485315943003499**（差 -1.60024）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/sharpe_delta`：**0.005735999804863057 → -0.020536000001067034**（差 -0.026272）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/splice_days_dropped`：**1 → 85**（差 84）｜RECOVERED_OLD_VALUE｜昨天的 1 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_pairs`（改名，不是重算）
- `/futures_hedge/unit_over_target`：**11.395936914713209 → 10.979444882970085**（差 -0.416492）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/variance_removable_pct`：**1.8861339441281915 → 2.004047901378724**（差 0.117914）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/vol_delta_pp`：**-0.09457028960696418 → -0.10122922788117772**（差 -0.006659）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/dsharpe`：**0.005735999804863057 → -0.020536000001067034**（差 -0.026272）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/dsharpe_hi`：**0.09446056903527693 → 0.0719002244924948**（差 -0.02256）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/dsharpe_lo`：**-0.06366444689345857 → -0.0964202006837476**（差 -0.032756）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/share_above_uncond`：**0.968 → 0.9695**（差 0.0015）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_beta`：**0.6115545672996576 → 0.6126419583867959**（差 0.001087）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_ci_hi`：**0.8343491781619469 → 0.8405742148706478**（差 0.006225）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_ci_lo`：**0.12672451800387655 → 0.13021062460324065**（差 0.003486）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_n`：**57 → 52**（差 -5）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/uncond_beta`：**0.07185718963947142 → 0.07458300567364223**（差 0.002726）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_ladder/declared/cash_rate_pct`：**1.326 → 1.327**（差 0.001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
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
- `/idle_cash/vehicle_net_pct`：**1.772 → 1.7731**（差 0.0011）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/cny_total`：**3322.86 → 3913.6**（差 590.74）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/0/latest_pctile`：**15.6312625250501 → 0.5344021376085505**（差 -15.09686）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/0/mean_pct`：**0.5223345213939685 → 0.9739309177408781**（差 0.451596）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/0/n`：**262 → 134**（差 -128）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/0/same_bucket_move_cny`：**451.0243678642211 → 840.967920989058**（差 389.943553）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/0/t`：**1.9314301221169548 → 2.48618543532154**（差 0.554755）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/1/latest_pctile`：**63.188253801782906 → 78.91976927110645**（差 15.731515）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/1/mean_pct`：**0.1136316784152153 → 0.3459749989108973**（差 0.232343）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/1/n`：**770 → 394**（差 -376）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/1/same_bucket_move_cny`：**98.20186006657005 → 298.9957457587844**（差 200.793886）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/1/t`：**0.38385105751885035 → 0.9685142995814702**（差 0.584663）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/2/latest_pctile`：**87.10659898477158 → 82.74111675126903**（差 -4.365482）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/3/latest_pctile`：**19.894894894894893 → 14.33933933933934**（差 -5.555556）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_forward/rows/4/latest_pctile`：**13.161290322580646 → 11.741935483870968**（差 -1.419355）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/defects/0/disk_n`：**5222 → 5221**（差 -1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/0/declared_n`：**210 → 211**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/0/laneside/local_disk_n`：**186 → 187**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/0/local_disk_n`：**186 → 187**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/1/laneside/local_disk_n`：**27 → 1**（差 -26）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/1/local_disk_n`：**27 → 1**（差 -26）｜UNEXPLAINED｜没有旧值留存，也没有口径声明

同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；没有这两条说明的，就是这页偷偷换了数。

## 还有哪些节在同 bar 上改了数（61 个）

- `premium_forward`：14 个
- `futures_sleeve`：12 个
- `cash_money`：9 个
- `futures_hedge_tail`：9 个
- `futures_hedge`：8 个
- `roster_audit`：6 个
- `cash_caliber`：1 个
- `futures_ladder`：1 个
- `idle_cash`：1 个

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
