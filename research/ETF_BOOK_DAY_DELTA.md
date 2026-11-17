# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261117.json` → `LIVE-BOOK-20261118.json`
- 价格依据：2026-11-17（前一天 2026-11-17）｜数据截止：2026-11-17（前一天 2026-11-17）
- 判决：**UNEXPLAINED_MOVES**

## 一句话
两天**是同一根 bar**（没有新数据进来），这页有 **497** 个数变了；其中 **5** 个是钟面（机器多久没说话之类，本来就该走）、**268** 个能给出解释（旧数还在页上／口径句改了／这一节换了代／这一节换了定价的输入／这个数只是转抄别面）、**224** 个没解释。新增 **235** 个数字叶子、消失 **3** 个。

## 动的数（全部 497 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/alias_census/calibration/accepted_same_name/accepted_by_rule` | 169 | 402 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/1/drift_pp` | 0.51 | 0.307 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/1/share` | 0.1165 | 0.1687 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/2/drift_pp` | 0.118 | 0.316 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/2/share` | 0.1084 | 0.1647 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/3/drift_pp` | 0.837 | 0.005 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/3/share` | 0.1004 | 0.1606 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/4/drift_pp` | 0.445 | 0.284 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/4/share` | 0.0964 | 0.1526 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/5/drift_pp` | 0.816 | 0.815 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/5/share` | 0.0763 | 0.1526 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/6/drift_pp` | 0.469 | 0.719 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/6/share` | 0.0683 | 0.1486 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/7/drift_pp` | 0.475 | 0.857 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/7/share` | 0.0683 | 0.1446 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/8/drift_pp` | 0.588 | 0.628 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/8/share` | 0.0683 | 0.1446 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/9/drift_pp` | 0.573 | 0.171 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/accepted_pairs/9/share` | 0.0643 | 0.1365 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/by_gate/BOTH` | 3 | 28 | RECOVERED_OLD_VALUE | 昨天的 3 今天仍在这页上：`/premium_leak/nav_ruler_history/159655/n_obs`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/by_gate/DAY` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/by_gate/YEAR` | 148 | 439 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/drift_buckets/1.0-1.5` | 43 | 137 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/drift_buckets/1.5-2.0` | 45 | 109 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/drift_buckets/2.0-3.0` | 39 | 115 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/drift_buckets/3.0+` | 24 | 107 | RECOVERED_OLD_VALUE | 昨天的 24 今天仍在这页上：`/alias_stability/stability/by_trials/3/held_every_window`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/drift_max` | 10.925 | 19.879 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/drift_min` | 1.01 | 0.437 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/n` | 320 | 870 | RECOVERED_OLD_VALUE | 昨天的 320 今天仍在这页上：`/alias_stability/stability/per_window/2/measured`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/refused_by_rule` | 151 | 468 | RECOVERED_OLD_VALUE | 昨天的 151 今天仍在这页上：`/alias_stability/stability/per_window/1/refused_walks_apart`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/refused_pairs/0/drift_pp` | 10.925 | 19.879 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/0/share` | 0.2289 | 0.3052 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/1/drift_pp` | 7.816 | 15.331 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/1/share` | 0.0683 | 0.3494 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/2/drift_pp` | 7.549 | 14.557 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/2/share` | 0.0884 | 0.257 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/3/drift_pp` | 5.298 | 12.825 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/3/share` | 0.0482 | 0.2289 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/4/drift_pp` | 5.148 | 12.432 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/4/share` | 0.1486 | 0.3012 | RECOVERED_OLD_VALUE | 昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/refused_pairs/5/drift_pp` | 4.872 | 12.022 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/5/share` | 0.1486 | 0.1566 | RECOVERED_OLD_VALUE | 昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/refused_pairs/6/drift_pp` | 4.609 | 11.044 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/6/share` | 0.1486 | 0.2932 | RECOVERED_OLD_VALUE | 昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/refused_pairs/7/drift_pp` | 4.592 | 10.925 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/7/share` | 0.0723 | 0.2289 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/8/drift_pp` | 4.318 | 10.444 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/8/share` | 0.0924 | 0.2008 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/9/drift_pp` | 4.3 | 9.772 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/refused_pairs/9/share` | 0.0402 | 0.1205 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/share_max` | 0.2289 | 0.3655 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/share_median` | 0.0281 | 0.0321 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/0/drift_pp` | 10.925 | 19.879 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/0/share` | 0.2289 | 0.3052 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/1/drift_pp` | 7.816 | 15.331 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/1/share` | 0.0683 | 0.3494 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/2/drift_pp` | 7.549 | 14.557 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/2/share` | 0.0884 | 0.257 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/3/drift_pp` | 5.298 | 12.825 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/3/share` | 0.0482 | 0.2289 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/4/drift_pp` | 5.148 | 12.432 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/4/share` | 0.1486 | 0.3012 | RECOVERED_OLD_VALUE | 昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/5/drift_pp` | 4.872 | 12.022 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/5/share` | 0.1486 | 0.1566 | RECOVERED_OLD_VALUE | 昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/6/drift_pp` | 4.609 | 11.044 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/6/share` | 0.1486 | 0.2932 | RECOVERED_OLD_VALUE | 昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算） |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/7/drift_pp` | 4.592 | 10.925 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/7/share` | 0.0723 | 0.2289 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/8/drift_pp` | 4.318 | 10.444 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/8/share` | 0.0924 | 0.2008 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/9/drift_pp` | 4.3 | 9.772 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/accepted_same_name/year_killed_pairs/9/share` | 0.0402 | 0.1205 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/accepted_by_rule` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/by_gate/BOTH` | 21 | 110 | RECOVERED_OLD_VALUE | 昨天的 21 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/n_obs`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/by_gate/DAY` | 0 | 2 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/by_gate/YEAR` | 1 | 2 | RECOVERED_OLD_VALUE | 昨天的 1 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_pairs`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/drift_buckets/1.0-1.5` | 0 | 3 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/drift_buckets/1.5-2.0` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/drift_buckets/3.0+` | 21 | 109 | RECOVERED_OLD_VALUE | 昨天的 21 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/n_obs`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/drift_max` | 21.741 | 41.243 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/drift_min` | 2.793 | 0.43 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/n` | 22 | 115 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_by_rule` | 22 | 114 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/0/drift_pp` | 21.741 | 41.243 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/0/share` | 0.5582 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/1/drift_pp` | 18.609 | 40.844 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/1/share` | 0.3092 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/2/drift_pp` | 17.204 | 35.702 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/2/share` | 0.4016 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/3/drift_pp` | 16.515 | 35.518 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/3/share` | 0.3373 | 0.7671 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/4/drift_pp` | 12.481 | 22.624 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/4/share` | 0.4016 | 0.6466 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/5/drift_pp` | 10.623 | 21.741 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/5/share` | 0.4819 | 0.5582 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/6/drift_pp` | 10.155 | 19.721 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/6/share` | 0.4177 | 0.3815 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/7/drift_pp` | 9.272 | 19.683 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/7/share` | 0.3655 | 0.6265 | RECOVERED_OLD_VALUE | 昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/refused_pairs/8/drift_pp` | 9.118 | 19.317 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/8/share` | 0.3655 | 0.3896 | RECOVERED_OLD_VALUE | 昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/refused_pairs/9/drift_pp` | 8.596 | 18.609 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/refused_pairs/9/share` | 0.4096 | 0.3092 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/share_max` | 0.5582 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/share_median` | 0.3916 | 0.3936 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/0/drift_pp` | 21.741 | 41.243 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/0/share` | 0.5582 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/1/drift_pp` | 18.609 | 40.844 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/1/share` | 0.3092 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/2/drift_pp` | 17.204 | 35.702 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/2/share` | 0.4016 | 0.7751 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/3/drift_pp` | 16.515 | 35.518 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/3/share` | 0.3373 | 0.7671 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/4/drift_pp` | 12.481 | 22.624 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/4/share` | 0.4016 | 0.6466 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/5/drift_pp` | 10.623 | 21.741 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/5/share` | 0.4819 | 0.5582 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/6/drift_pp` | 10.155 | 19.721 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/6/share` | 0.4177 | 0.3815 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/7/drift_pp` | 9.272 | 19.683 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/7/share` | 0.3655 | 0.6265 | RECOVERED_OLD_VALUE | 昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/8/drift_pp` | 9.118 | 19.317 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/8/share` | 0.3655 | 0.3896 | RECOVERED_OLD_VALUE | 昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算） |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/9/drift_pp` | 8.596 | 18.609 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/refused_same_name/year_killed_pairs/9/share` | 0.4096 | 0.3092 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/year_line_cost/1.0/price_refused_accepted` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/year_line_cost/1.0/same_name_accepted` | 169 | 402 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/year_line_cost/1.5/price_refused_accepted` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/year_line_cost/1.5/same_name_accepted` | 211 | 534 | RECOVERED_OLD_VALUE | 昨天的 211 今天仍在这页上：`/alias_stability/stability/by_trials/4/pairs`（改名，不是重算） |
| `/alias_census/calibration/year_line_cost/2.0/price_refused_accepted` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/year_line_cost/2.0/same_name_accepted` | 256 | 642 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/alias_census/calibration/year_line_cost/3.0/price_refused_accepted` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/alias_census/calibration/year_line_cost/3.0/same_name_accepted` | 294 | 753 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/base/flat_today_pct` | 12.15 | 12.21 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/base/pp_per_100bp` | 0.375 | 0.337 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/cash_rates/missing_bar_steps` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/carry_regime/cash_rates/observed_mean_pct` | 1.9757 | 1.9766 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/cash_rates/today_bar_lag` | 0 | 2 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/carry_regime/cash_rates/today_pct` | 1.175 | 1.265 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/quote_lag` | 0 | 2 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/carry_regime/rows/0/flat_today_pct` | 6.59 | 6.67 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/rows/0/pp_per_100bp` | 0.487 | 0.436 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/rows/1/flat_today_pct` | 12.15 | 12.21 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/rows/1/pp_per_100bp` | 0.375 | 0.337 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/rows/2/flat_today_pct` | 17.84 | 17.88 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/rows/2/pp_per_100bp` | 0.25 | 0.225 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/carry_regime/rows/3/pp_per_100bp` | 0.025 | 0.028 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_caliber/band_50_bp` | 33.75 | 33.5 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/band_90_bp` | 90.185 | 90.405 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/commission_bp` | 24.639 | 24.649 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/commission_share_pct` | 41.28 | 48.52 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/control_error_bp` | 0.0043 | 0.004 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/median_abs_bp` | 33.75 | 33.5 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/quote_pct` | 1.175 | 1.265 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/rate_diff_bp` | -84.335 | -75.455 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/share_in_band_pct` | 1.262 | 1.264 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/total_bp` | -59.696 | -50.806 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/window/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/window_gross_pct` | 2.0184 | 2.0196 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/window_net_pct` | 1.772 | 1.7731 | SECTION_ADVANCED | 这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_handshake/repo_rate_pct` | 1.175 | 1.265 | SECTION_ADVANCED | 这一节自己换了代：`cash_handshake` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_handshake/worst_case_annual_cny` | 6391.0 | 6903.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_handshake` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/forgotten_day_cny` | 18.0 | 20.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/rolls/GC028` | 12 | 13 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/rolls/GC091` | 3 | 4 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/annual_cny_realized_1y` | 7429.0 | 7424.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/annual_cny_spot` | 6675.0 | 7187.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/mean250_pct` | 1.3497 | 1.3518 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/1/realized_pct` | 1.3076 | 1.3068 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/3/days` | 1093 | 1095 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/3/realized_pct` | 1.671 | 1.6761 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/3/rolls` | 724 | 726 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/5/days` | 1825 | 1824 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/5/realized_pct` | 1.8891 | 1.8911 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/realized/5/rolls` | 1210 | 1211 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/0/spot_pct` | 1.175 | 1.265 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/annual_cny_realized_1y` | 6398.0 | 6384.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/annual_cny_spot` | 7016.0 | 6903.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/edge_bp/1` | -18.1 | -18.3 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/edge_bp/3` | -30.8 | -30.7 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/edge_bp/5` | -38.6 | -38.5 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/mean250_pct` | 1.3611 | 1.3626 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/1/realized_pct` | 1.1262 | 1.1237 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/3/days` | 1092 | 1094 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/3/idle_days` | 207 | 206 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/3/idle_share` | 0.1896 | 0.1883 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/3/realized_pct` | 1.3632 | 1.3694 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/3/rolls` | 295 | 296 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/5/days` | 1824 | 1823 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/5/idle_days` | 348 | 347 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/5/idle_share` | 0.1908 | 0.1903 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/realized/5/realized_pct` | 1.5035 | 1.5057 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/1/spot_pct` | 1.235 | 1.215 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/annual_cny_realized_1y` | 8140.0 | 8010.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/annual_cny_spot` | 7414.0 | 7812.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/edge_bp/1` | 12.5 | 10.3 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/edge_bp/3` | 5.3 | 4.8 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/edge_bp/5` | 0.5 | 0.8 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/idle_days_1y` | 10 | 14 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/idle_share_1y` | 0.0278 | 0.0385 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/mean250_pct` | 1.4624 | 1.4635 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/1/days` | 360 | 364 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/1/idle_days` | 10 | 14 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/1/idle_share` | 0.0278 | 0.0385 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/1/realized_pct` | 1.4328 | 1.4099 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/3/days` | 1088 | 1094 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/3/idle_days` | 45 | 44 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/3/idle_share` | 0.0414 | 0.0402 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/3/realized_pct` | 1.7242 | 1.7241 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/3/rolls` | 149 | 150 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/5/days` | 1820 | 1823 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/5/idle_days` | 77 | 80 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/5/idle_share` | 0.0423 | 0.0439 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/realized/5/realized_pct` | 1.894 | 1.8993 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/2/spot_pct` | 1.305 | 1.375 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/annual_cny_realized_1y` | 8371.0 | 8224.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/annual_cny_spot` | 7670.0 | 7812.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/edge_bp/1` | 16.6 | 14.1 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/edge_bp/3` | 4.9 | 5.6 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/edge_bp/5` | 4.0 | 4.2 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/idle_days_1y` | 3 | 7 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/idle_share_1y` | 0.0085 | 0.0196 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/mean250_pct` | 1.4673 | 1.4682 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/1/days` | 353 | 357 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/1/idle_days` | 3 | 7 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/1/idle_share` | 0.0085 | 0.0196 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/1/realized_pct` | 1.4734 | 1.4476 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/3/days` | 1081 | 1087 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/3/idle_days` | 45 | 37 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/3/idle_share` | 0.0416 | 0.034 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/3/realized_pct` | 1.7196 | 1.7322 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/3/rolls` | 74 | 75 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/5/days` | 1813 | 1816 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/5/idle_days` | 49 | 52 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/5/idle_share` | 0.027 | 0.0286 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/realized/5/realized_pct` | 1.9287 | 1.9328 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/3/spot_pct` | 1.35 | 1.375 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/annual_cny_realized_1y` | 8372.0 | 8242.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/annual_cny_spot` | 7698.0 | 7812.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/edge_bp/1` | 16.6 | 14.4 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/edge_bp/3` | 7.5 | 11.2 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/edge_bp/5` | 9.0 | 8.4 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/idle_days_1y` | 2 | 0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/idle_share_1y` | 0.0059 | 0.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/mean250_pct` | 1.4628 | 1.4639 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/1/days` | 338 | 364 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/1/idle_days` | 2 | 0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/1/idle_share` | 0.0059 | 0.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/1/realized_pct` | 1.4737 | 1.4508 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/1/rolls` | 12 | 13 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/3/days` | 1087 | 1093 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/3/idle_days` | 23 | 1 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/3/idle_share` | 0.0212 | 0.0009 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/3/realized_pct` | 1.7465 | 1.7882 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/3/rolls` | 38 | 39 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/5/days` | 1798 | 1801 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/5/idle_days` | 6 | 9 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/5/idle_share` | 0.0033 | 0.005 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/realized/5/realized_pct` | 1.9789 | 1.9755 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/rolls_1y` | 12 | 13 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/4/spot_pct` | 1.355 | 1.375 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/annual_cny_realized_1y` | 8068.0 | 8132.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/annual_cny_spot` | 7471.0 | 7641.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/edge_bp/1` | 11.2 | 12.5 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/edge_bp/3` | 11.7 | 10.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/edge_bp/5` | 4.6 | 3.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/idle_days_1y` | 8 | 0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/idle_share_1y` | 0.0285 | 0.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/mean250_pct` | 1.4335 | 1.4348 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/1/days` | 281 | 364 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/1/idle_days` | 8 | 0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/1/idle_share` | 0.0285 | 0.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/1/realized_pct` | 1.4201 | 1.4313 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/1/rolls` | 3 | 4 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/3/days` | 1009 | 1015 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/3/idle_days` | 8 | 14 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/3/idle_share` | 0.0079 | 0.0138 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/3/realized_pct` | 1.788 | 1.7765 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/5/days` | 1741 | 1744 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/5/idle_days` | 12 | 15 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/5/idle_share` | 0.0069 | 0.0086 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/realized/5/realized_pct` | 1.9347 | 1.9215 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/rolls_1y` | 3 | 4 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_ladder/tenors/5/spot_pct` | 1.315 | 1.345 | SECTION_ADVANCED | 这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/book_rate/annual_cny` | 10067.0 | 10073.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/book_rate/gap_vs_spot_bp` | -59.7 | -50.81 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/book_rate/gap_vs_spot_cny` | -3392.0 | -2887.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/book_rate/pct` | 1.772 | 1.7731 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/mean_tail/annual_cny` | 7668.0 | 7680.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/mean_tail/net_annual_cny` | 6287.0 | 6299.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/mean_tail/net_pct` | 1.1067 | 1.1088 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/mean_tail/pct` | 1.3497 | 1.3518 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/spot/annual_cny` | 6675.0 | 7187.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/spot/net_annual_cny` | 5295.0 | 5806.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/spot/net_pct` | 0.932 | 1.022 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/spot/pct` | 1.175 | 1.265 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/spread_vs_tail_cny` | -993.0 | -493.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/spread_vs_window_cny` | -5148.0 | -4634.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/window/annual_cny` | 11824.0 | 11821.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/window/net_annual_cny` | 10443.0 | 10440.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/window/net_pct` | 1.8382 | 1.8377 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/block/window/pct` | 2.0812 | 2.0807 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/book/cny` | 579.0 | 635.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/book/pct` | 1.772 | 1.7731 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/calendar_days` | 21 | 23 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/fee_cny` | 85.0 | 97.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/gap_bp` | 85.77 | 77.79 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/gap_bp_gross` | 59.7 | 50.81 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/gap_cny` | 280.0 | 279.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/rolls` | 15 | 17 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/spot/cny` | 384.0 | 453.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/spot/pct` | 1.175 | 1.265 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/spot_net/cny` | 299.0 | 356.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_money/forward/spot_net/pct` | 0.9143 | 0.9952 | SECTION_ADVANCED | 这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_yield/annual_cny` | 6675.0 | 7187.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_yield/daily_cny` | 27.0 | 29.0 | SECTION_ADVANCED | 这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_yield/rate_20d_pct` | 1.2345 | 1.232 | SECTION_ADVANCED | 这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_yield/rate_pct` | 1.175 | 1.265 | SECTION_ADVANCED | 这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/causal_rebuild/elapsed_sec` | 50.0 | 81.5 | CLOCK |  |
| `/family_coherence/floor_extrapolation/gap_pp` | 0.114 | -0.085 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/floor_extrapolation/observed_pp` | 0.43 | 0.51 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/floor_extrapolation/predicted_pp` | 0.316 | 0.595 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/floor_extrapolation/tolerance_pp` | 0.139 | 2.582 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/null_calibration/not_separable_share` | 0.035 | 0.0345 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/null_calibration/reject_share` | 0.965 | 0.9656 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/signflip/arms/0/cells_positive` | 5 | 7 | RECOVERED_OLD_VALUE | 昨天的 5 今天仍在这页上：`/capacity_edge/summary/n_names`（改名，不是重算） |
| `/family_coherence/signflip/arms/1/cells_positive` | 6 | 8 | RECOVERED_OLD_VALUE | 昨天的 6 今天仍在这页上：`/authority/gate_h`（改名，不是重算） |
| `/family_coherence/signflip/arms/2/cells_positive` | 0 | 1 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
| `/family_coherence/signflip/arms/3/cells_positive` | 8 | 12 | RECOVERED_OLD_VALUE | 昨天的 8 今天仍在这页上：`/alias_stability/stability/per_window/0/refused_days_apart`（改名，不是重算） |
| `/family_coherence/signflip/arms/4/cells_positive` | 7 | 9 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/signflip/arms/5/cells_positive` | 7 | 8 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/family_coherence/signflip/n_reject` | 4 | 3 | RECOVERED_OLD_VALUE | 昨天的 4 今天仍在这页上：`/alias_stability/stability/refused/0/trials`（改名，不是重算） |
| `/family_coherence/signflip/n_reject_standing` | 3 | 2 | RECOVERED_OLD_VALUE | 昨天的 3 今天仍在这页上：`/premium_leak/nav_ruler_history/159655/n_obs`（改名，不是重算） |
| `/fleet/rows/0/age_h` | 1.24 | 24.53 | CLOCK |  |
| `/fleet/rows/1/age_h` | 441.79 | 443.46 | CLOCK |  |
| `/fleet/rows/2/age_h` | 4.18 | 0.56 | CLOCK |  |
| `/forward/nav` | 1.0037762754 | 1.0037812718 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/forward/since_inception_pct` | 0.3776 | 0.3781 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
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
| `/k_gap/account_base_gap_cny` | 29571.45 | 28373.5 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/k_gap/nav_account_cny` | 998061.6 | 1000000.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lookahead/affected_faces` | 94 | 74 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/causal/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/causal/cagr` | 0.0845 | 0.0841 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/causal/cagr_pp` | 8.45 | 8.41 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/causal/sharpe` | 0.874 | 0.869 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_carry/bars` | 1665 | 1663 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_carry/cagr` | 0.0898 | 0.0911 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_carry/cagr_pp` | 8.98 | 9.11 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_carry/sharpe` | 0.941 | 0.952 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_no_carry/bars` | 1665 | 1663 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_no_carry/cagr` | 0.0839 | 0.0851 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_no_carry/cagr_pp` | 8.39 | 8.51 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/ledger_no_carry/sharpe` | 0.885 | 0.896 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/published/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/published/cagr` | 0.0941 | 0.0959 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/published/cagr_pp` | 9.41 | 9.59 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/arms/published/sharpe` | 0.971 | 0.987 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/decomposition/carry_pp` | 0.59 | 0.6 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/decomposition/mark_basis_pp` | 0.06 | -0.1 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/decomposition/price_of_the_one_bar_pp` | 0.96 | 1.18 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/0/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/0/cagr` | 0.1565 | 0.1582 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/0/cagr_pp` | 15.65 | 15.82 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/0/sharpe` | 1.504 | 1.518 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/1/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/1/cagr` | 0.1243 | 0.1241 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/1/cagr_pp` | 12.43 | 12.41 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/1/sharpe` | 1.271 | 1.268 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/1/vol` | 0.0999 | 0.1 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/2/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/2/cagr` | 0.0941 | 0.0959 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/2/cagr_pp` | 9.41 | 9.59 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/2/sharpe` | 0.971 | 0.987 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/3/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/3/cagr` | 0.0845 | 0.0841 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/3/cagr_pp` | 8.45 | 8.41 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/3/sharpe` | 0.874 | 0.869 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/4/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/4/cagr` | 0.0773 | 0.0747 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/4/cagr_pp` | 7.73 | 7.47 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/4/sharpe` | 0.797 | 0.773 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/5/bars` | 1664 | 1662 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/5/cagr` | 0.0503 | 0.0518 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/5/cagr_pp` | 5.03 | 5.18 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/lag_ladder/5/sharpe` | 0.54 | 0.554 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/gap_pp_per_year` | 0.96 | 1.18 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_pp/-1` | 12.43 | 12.41 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_pp/-2` | 15.65 | 15.82 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_pp/0` | 9.41 | 9.59 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_pp/1` | 8.45 | 8.41 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_pp/20` | 5.03 | 5.18 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_pp/5` | 7.73 | 7.47 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/verdict/ladder_spread_pp` | 10.62 | 10.64 | SECTION_ADVANCED | 这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/positions/accrual/rate_latest` | 1.175 | 1.265 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/positions/accrual/repo_quotes` | 3769 | 3767 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/positions/replay/cash_interest_cny` | 526.17 | 449.68 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/positions/replay/rf_missing_bars` | 0 | 2 | RECOVERED_OLD_VALUE | 昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算） |
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
| `/premium_leak/own_ruler/159519/above_own_median_pp` | -1.1434 | -0.5951 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159519/last_pct` | -0.9895 | -0.4407 | RECOVERED_OLD_VALUE | 昨天的 -0.9895 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/last_pct`（改名，不是重算） |
| `/premium_leak/own_ruler/159519/last_pctile` | 7.1 | 25.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159519/last_rank` | 720 | 579 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159519/median_pct` | 0.1539 | 0.1543 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159519/n_obs` | 775 | 772 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159519/p10_pct` | -0.8857 | -0.8827 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159519/p90_pct` | 1.5163 | 1.5173 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/above_own_median_pp` | 7.8586 | 6.8923 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/last_pct` | 9.0909 | 8.1154 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/last_pctile` | 98.37 | 96.44 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/last_rank` | 16 | 35 | RECOVERED_OLD_VALUE | 昨天的 16 今天仍在这页上：`/alias_stability/stability/per_window/1/refused_days_apart`（改名，不是重算） |
| `/premium_leak/own_ruler/159655/median_pct` | 1.2323 | 1.2231 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/n_obs` | 984 | 982 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/p10_pct` | -0.6486 | -0.6498 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/159655/p90_pct` | 6.2278 | 6.2027 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/510760/above_own_median_pp` | -0.0652 | -0.0795 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/510760/last_pct` | -0.0558 | -0.0701 | RECOVERED_OLD_VALUE | 昨天的 -0.0558 今天仍在这页上：`/premium_leak/nav_ruler_history/510760/last_pct`（改名，不是重算） |
| `/premium_leak/own_ruler/510760/last_pctile` | 31.26 | 26.31 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/510760/last_rank` | 1029 | 1101 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/510760/n_obs` | 1497 | 1494 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/510760/p10_pct` | -0.1627 | -0.1623 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/510760/p90_pct` | 0.2146 | 0.2148 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/above_own_median_pp` | -0.131 | 0.0269 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/last_pct` | -0.1828 | -0.025 | RECOVERED_OLD_VALUE | 昨天的 -0.1828 今天仍在这页上：`/premium_leak/nav_ruler_history/512040/last_pct`（改名，不是重算） |
| `/premium_leak/own_ruler/512040/last_pctile` | 20.91 | 56.12 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/last_rank` | 1509 | 836 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/median_pct` | -0.0519 | -0.052 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/n_obs` | 1908 | 1905 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/p10_pct` | -0.2723 | -0.2728 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/512040/p90_pct` | 0.1451 | 0.1454 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/above_own_median_pp` | -0.7649 | -0.6372 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/last_pct` | -0.8279 | -0.6964 | RECOVERED_OLD_VALUE | 昨天的 -0.8279 今天仍在这页上：`/premium_leak/nav_ruler_history/513690/last_pct`（改名，不是重算） |
| `/premium_leak/own_ruler/513690/last_pctile` | 15.62 | 20.24 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/last_rank` | 1124 | 1060 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/median_pct` | -0.063 | -0.0592 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/n_obs` | 1332 | 1329 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/p10_pct` | -1.0441 | -1.0446 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler/513690/p90_pct` | 1.1978 | 1.1987 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/own_ruler_summary/revert_to_own_median_cny` | 4183.31 | 4187.15 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/stress/if_premium_reverts_to_own_median_cny` | -4183.31 | -4187.15 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/premium_leak/stress/if_premium_reverts_to_own_median_pct_of_nav` | -0.4183 | -0.4187 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/defects/0/disk_n` | 5222 | 5221 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/0/declared_n` | 210 | 211 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/0/laneside/local_disk_n` | 186 | 187 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/0/local_disk_n` | 186 | 187 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/1/laneside/local_disk_n` | 27 | 1 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/1/local_disk_n` | 27 | 1 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/same_beta_benchmark/maxdd` | -0.0401 | -0.0402 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/ticket_book/sharpe` | 1.688 | 1.687 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/vs_basket/book_nav` | 1.0037762754 | 1.0037812718 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/vs_basket/excess_pp` | 2.9518 | 2.9523 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |

## 今天没有了的数（3 个，列前 40）

- `/family_coherence/receipt/elapsed_sec`
- `/family_coherence/receipt/family/total`
- `/family_coherence/receipt/group_arms`

## 今天新出现的数（235 个）落在这几块上

- `/alias_census/calibration`
- `/alias_stability/crosscheck`
- `/alias_stability/families`
- `/alias_stability/stability`
- `/authority/gate_h`
- `/authority/owner_silent_h`
- `/capacity_edge/criteria`
- `/capacity_edge/summary`
- `/capacity_ticket/one_lot_floor_cny`
- `/capacity_ticket/rungs`
- `/capacity_ticket/shortfall_to_typical_cny`
- `/derisk/instrument`
- `/derisk/n_phases`
- `/premium_leak/nav_ruler_history`

## 钱的两处（同一根 bar 上改了定价口径）

- `/alias_census/calibration/accepted_same_name/accepted_by_rule`：**169 → 402**（差 233）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/1/drift_pp`：**0.51 → 0.307**（差 -0.203）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/1/share`：**0.1165 → 0.1687**（差 0.0522）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/2/drift_pp`：**0.118 → 0.316**（差 0.198）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/2/share`：**0.1084 → 0.1647**（差 0.0563）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/3/drift_pp`：**0.837 → 0.005**（差 -0.832）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/3/share`：**0.1004 → 0.1606**（差 0.0602）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/4/drift_pp`：**0.445 → 0.284**（差 -0.161）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/4/share`：**0.0964 → 0.1526**（差 0.0562）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/5/drift_pp`：**0.816 → 0.815**（差 -0.001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/5/share`：**0.0763 → 0.1526**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/6/drift_pp`：**0.469 → 0.719**（差 0.25）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/6/share`：**0.0683 → 0.1486**（差 0.0803）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/7/drift_pp`：**0.475 → 0.857**（差 0.382）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/7/share`：**0.0683 → 0.1446**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/8/drift_pp`：**0.588 → 0.628**（差 0.04）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/8/share`：**0.0683 → 0.1446**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/9/drift_pp`：**0.573 → 0.171**（差 -0.402）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/accepted_pairs/9/share`：**0.0643 → 0.1365**（差 0.0722）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/by_gate/BOTH`：**3 → 28**（差 25）｜RECOVERED_OLD_VALUE｜昨天的 3 今天仍在这页上：`/premium_leak/nav_ruler_history/159655/n_obs`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/by_gate/DAY`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/by_gate/YEAR`：**148 → 439**（差 291）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/drift_buckets/1.0-1.5`：**43 → 137**（差 94）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/drift_buckets/1.5-2.0`：**45 → 109**（差 64）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/drift_buckets/2.0-3.0`：**39 → 115**（差 76）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/drift_buckets/3.0+`：**24 → 107**（差 83）｜RECOVERED_OLD_VALUE｜昨天的 24 今天仍在这页上：`/alias_stability/stability/by_trials/3/held_every_window`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/drift_max`：**10.925 → 19.879**（差 8.954）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/drift_min`：**1.01 → 0.437**（差 -0.573）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/n`：**320 → 870**（差 550）｜RECOVERED_OLD_VALUE｜昨天的 320 今天仍在这页上：`/alias_stability/stability/per_window/2/measured`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/refused_by_rule`：**151 → 468**（差 317）｜RECOVERED_OLD_VALUE｜昨天的 151 今天仍在这页上：`/alias_stability/stability/per_window/1/refused_walks_apart`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/refused_pairs/0/drift_pp`：**10.925 → 19.879**（差 8.954）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/0/share`：**0.2289 → 0.3052**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/1/drift_pp`：**7.816 → 15.331**（差 7.515）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/1/share`：**0.0683 → 0.3494**（差 0.2811）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/2/drift_pp`：**7.549 → 14.557**（差 7.008）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/2/share`：**0.0884 → 0.257**（差 0.1686）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/3/drift_pp`：**5.298 → 12.825**（差 7.527）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/3/share`：**0.0482 → 0.2289**（差 0.1807）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/4/drift_pp`：**5.148 → 12.432**（差 7.284）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/4/share`：**0.1486 → 0.3012**（差 0.1526）｜RECOVERED_OLD_VALUE｜昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/refused_pairs/5/drift_pp`：**4.872 → 12.022**（差 7.15）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/5/share`：**0.1486 → 0.1566**（差 0.008）｜RECOVERED_OLD_VALUE｜昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/refused_pairs/6/drift_pp`：**4.609 → 11.044**（差 6.435）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/6/share`：**0.1486 → 0.2932**（差 0.1446）｜RECOVERED_OLD_VALUE｜昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/refused_pairs/7/drift_pp`：**4.592 → 10.925**（差 6.333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/7/share`：**0.0723 → 0.2289**（差 0.1566）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/8/drift_pp`：**4.318 → 10.444**（差 6.126）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/8/share`：**0.0924 → 0.2008**（差 0.1084）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/9/drift_pp`：**4.3 → 9.772**（差 5.472）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/refused_pairs/9/share`：**0.0402 → 0.1205**（差 0.0803）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/share_max`：**0.2289 → 0.3655**（差 0.1366）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/share_median`：**0.0281 → 0.0321**（差 0.004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/0/drift_pp`：**10.925 → 19.879**（差 8.954）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/0/share`：**0.2289 → 0.3052**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/1/drift_pp`：**7.816 → 15.331**（差 7.515）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/1/share`：**0.0683 → 0.3494**（差 0.2811）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/2/drift_pp`：**7.549 → 14.557**（差 7.008）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/2/share`：**0.0884 → 0.257**（差 0.1686）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/3/drift_pp`：**5.298 → 12.825**（差 7.527）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/3/share`：**0.0482 → 0.2289**（差 0.1807）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/4/drift_pp`：**5.148 → 12.432**（差 7.284）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/4/share`：**0.1486 → 0.3012**（差 0.1526）｜RECOVERED_OLD_VALUE｜昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/5/drift_pp`：**4.872 → 12.022**（差 7.15）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/5/share`：**0.1486 → 0.1566**（差 0.008）｜RECOVERED_OLD_VALUE｜昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/6/drift_pp`：**4.609 → 11.044**（差 6.435）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/6/share`：**0.1486 → 0.2932**（差 0.1446）｜RECOVERED_OLD_VALUE｜昨天的 0.1486 今天仍在这页上：`/alias_census/calibration/refused_same_name/accepted_pairs/0/share`（改名，不是重算）
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/7/drift_pp`：**4.592 → 10.925**（差 6.333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/7/share`：**0.0723 → 0.2289**（差 0.1566）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/8/drift_pp`：**4.318 → 10.444**（差 6.126）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/8/share`：**0.0924 → 0.2008**（差 0.1084）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/9/drift_pp`：**4.3 → 9.772**（差 5.472）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/accepted_same_name/year_killed_pairs/9/share`：**0.0402 → 0.1205**（差 0.0803）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/accepted_by_rule`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/by_gate/BOTH`：**21 → 110**（差 89）｜RECOVERED_OLD_VALUE｜昨天的 21 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/n_obs`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/by_gate/DAY`：**0 → 2**（差 2）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/by_gate/YEAR`：**1 → 2**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 1 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_pairs`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/drift_buckets/1.0-1.5`：**0 → 3**（差 3）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/drift_buckets/1.5-2.0`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/drift_buckets/3.0+`：**21 → 109**（差 88）｜RECOVERED_OLD_VALUE｜昨天的 21 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/n_obs`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/drift_max`：**21.741 → 41.243**（差 19.502）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/drift_min`：**2.793 → 0.43**（差 -2.363）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/n`：**22 → 115**（差 93）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_by_rule`：**22 → 114**（差 92）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/0/drift_pp`：**21.741 → 41.243**（差 19.502）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/0/share`：**0.5582 → 0.7751**（差 0.2169）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/1/drift_pp`：**18.609 → 40.844**（差 22.235）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/1/share`：**0.3092 → 0.7751**（差 0.4659）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/2/drift_pp`：**17.204 → 35.702**（差 18.498）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/2/share`：**0.4016 → 0.7751**（差 0.3735）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/3/drift_pp`：**16.515 → 35.518**（差 19.003）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/3/share`：**0.3373 → 0.7671**（差 0.4298）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/4/drift_pp`：**12.481 → 22.624**（差 10.143）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/4/share`：**0.4016 → 0.6466**（差 0.245）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/5/drift_pp`：**10.623 → 21.741**（差 11.118）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/5/share`：**0.4819 → 0.5582**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/6/drift_pp`：**10.155 → 19.721**（差 9.566）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/6/share`：**0.4177 → 0.3815**（差 -0.0362）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/7/drift_pp`：**9.272 → 19.683**（差 10.411）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/7/share`：**0.3655 → 0.6265**（差 0.261）｜RECOVERED_OLD_VALUE｜昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/refused_pairs/8/drift_pp`：**9.118 → 19.317**（差 10.199）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/8/share`：**0.3655 → 0.3896**（差 0.0241）｜RECOVERED_OLD_VALUE｜昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/refused_pairs/9/drift_pp`：**8.596 → 18.609**（差 10.013）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/refused_pairs/9/share`：**0.4096 → 0.3092**（差 -0.1004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/share_max`：**0.5582 → 0.7751**（差 0.2169）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/share_median`：**0.3916 → 0.3936**（差 0.002）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/0/drift_pp`：**21.741 → 41.243**（差 19.502）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/0/share`：**0.5582 → 0.7751**（差 0.2169）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/1/drift_pp`：**18.609 → 40.844**（差 22.235）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/1/share`：**0.3092 → 0.7751**（差 0.4659）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/2/drift_pp`：**17.204 → 35.702**（差 18.498）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/2/share`：**0.4016 → 0.7751**（差 0.3735）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/3/drift_pp`：**16.515 → 35.518**（差 19.003）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/3/share`：**0.3373 → 0.7671**（差 0.4298）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/4/drift_pp`：**12.481 → 22.624**（差 10.143）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/4/share`：**0.4016 → 0.6466**（差 0.245）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/5/drift_pp`：**10.623 → 21.741**（差 11.118）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/5/share`：**0.4819 → 0.5582**（差 0.0763）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/6/drift_pp`：**10.155 → 19.721**（差 9.566）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/6/share`：**0.4177 → 0.3815**（差 -0.0362）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/7/drift_pp`：**9.272 → 19.683**（差 10.411）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/7/share`：**0.3655 → 0.6265**（差 0.261）｜RECOVERED_OLD_VALUE｜昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/year_killed_pairs/8/drift_pp`：**9.118 → 19.317**（差 10.199）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/8/share`：**0.3655 → 0.3896**（差 0.0241）｜RECOVERED_OLD_VALUE｜昨天的 0.3655 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/max_pct`（改名，不是重算）
- `/alias_census/calibration/refused_same_name/year_killed_pairs/9/drift_pp`：**8.596 → 18.609**（差 10.013）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/refused_same_name/year_killed_pairs/9/share`：**0.4096 → 0.3092**（差 -0.1004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/year_line_cost/1.0/price_refused_accepted`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/year_line_cost/1.0/same_name_accepted`：**169 → 402**（差 233）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/year_line_cost/1.5/price_refused_accepted`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/year_line_cost/1.5/same_name_accepted`：**211 → 534**（差 323）｜RECOVERED_OLD_VALUE｜昨天的 211 今天仍在这页上：`/alias_stability/stability/by_trials/4/pairs`（改名，不是重算）
- `/alias_census/calibration/year_line_cost/2.0/price_refused_accepted`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/year_line_cost/2.0/same_name_accepted`：**256 → 642**（差 386）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/alias_census/calibration/year_line_cost/3.0/price_refused_accepted`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/alias_census/calibration/year_line_cost/3.0/same_name_accepted`：**294 → 753**（差 459）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/base/flat_today_pct`：**12.15 → 12.21**（差 0.06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/base/pp_per_100bp`：**0.375 → 0.337**（差 -0.038）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/cash_rates/missing_bar_steps`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/carry_regime/cash_rates/observed_mean_pct`：**1.9757 → 1.9766**（差 0.0009）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/cash_rates/today_bar_lag`：**0 → 2**（差 2）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/carry_regime/cash_rates/today_pct`：**1.175 → 1.265**（差 0.09）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/quote_lag`：**0 → 2**（差 2）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/carry_regime/rows/0/flat_today_pct`：**6.59 → 6.67**（差 0.08）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/rows/0/pp_per_100bp`：**0.487 → 0.436**（差 -0.051）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/rows/1/flat_today_pct`：**12.15 → 12.21**（差 0.06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/rows/1/pp_per_100bp`：**0.375 → 0.337**（差 -0.038）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/rows/2/flat_today_pct`：**17.84 → 17.88**（差 0.04）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/rows/2/pp_per_100bp`：**0.25 → 0.225**（差 -0.025）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/carry_regime/rows/3/pp_per_100bp`：**0.025 → 0.028**（差 0.003）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_caliber/band_50_bp`：**33.75 → 33.5**（差 -0.25）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/band_90_bp`：**90.185 → 90.405**（差 0.22）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/commission_bp`：**24.639 → 24.649**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/commission_share_pct`：**41.28 → 48.52**（差 7.24）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/control_error_bp`：**0.0043 → 0.004**（差 -0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/median_abs_bp`：**33.75 → 33.5**（差 -0.25）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/quote_pct`：**1.175 → 1.265**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/rate_diff_bp`：**-84.335 → -75.455**（差 8.88）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/share_in_band_pct`：**1.262 → 1.264**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/total_bp`：**-59.696 → -50.806**（差 8.89）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/window/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/window_gross_pct`：**2.0184 → 2.0196**（差 0.0012）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/window_net_pct`：**1.772 → 1.7731**（差 0.0011）｜SECTION_ADVANCED｜这一节自己换了代：`cash_caliber` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_handshake/repo_rate_pct`：**1.175 → 1.265**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_handshake` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_handshake/worst_case_annual_cny`：**6391.0 → 6903.0**（差 512.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_handshake` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/forgotten_day_cny`：**18.0 → 20.0**（差 2.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/rolls/GC028`：**12 → 13**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/rolls/GC091`：**3 → 4**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/annual_cny_realized_1y`：**7429.0 → 7424.0**（差 -5.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/annual_cny_spot`：**6675.0 → 7187.0**（差 512.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/mean250_pct`：**1.3497 → 1.3518**（差 0.0021）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/1/realized_pct`：**1.3076 → 1.3068**（差 -0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/3/days`：**1093 → 1095**（差 2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/3/realized_pct`：**1.671 → 1.6761**（差 0.0051）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/3/rolls`：**724 → 726**（差 2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/5/days`：**1825 → 1824**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/5/realized_pct`：**1.8891 → 1.8911**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/realized/5/rolls`：**1210 → 1211**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/0/spot_pct`：**1.175 → 1.265**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/annual_cny_realized_1y`：**6398.0 → 6384.0**（差 -14.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/annual_cny_spot`：**7016.0 → 6903.0**（差 -113.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/edge_bp/1`：**-18.1 → -18.3**（差 -0.2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/edge_bp/3`：**-30.8 → -30.7**（差 0.1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/edge_bp/5`：**-38.6 → -38.5**（差 0.1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/mean250_pct`：**1.3611 → 1.3626**（差 0.0015）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/1/realized_pct`：**1.1262 → 1.1237**（差 -0.0025）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/3/days`：**1092 → 1094**（差 2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/3/idle_days`：**207 → 206**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/3/idle_share`：**0.1896 → 0.1883**（差 -0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/3/realized_pct`：**1.3632 → 1.3694**（差 0.0062）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/3/rolls`：**295 → 296**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/5/days`：**1824 → 1823**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/5/idle_days`：**348 → 347**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/5/idle_share`：**0.1908 → 0.1903**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/realized/5/realized_pct`：**1.5035 → 1.5057**（差 0.0022）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/1/spot_pct`：**1.235 → 1.215**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/annual_cny_realized_1y`：**8140.0 → 8010.0**（差 -130.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/annual_cny_spot`：**7414.0 → 7812.0**（差 398.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/edge_bp/1`：**12.5 → 10.3**（差 -2.2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/edge_bp/3`：**5.3 → 4.8**（差 -0.5）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/edge_bp/5`：**0.5 → 0.8**（差 0.3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/idle_days_1y`：**10 → 14**（差 4）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/idle_share_1y`：**0.0278 → 0.0385**（差 0.0107）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/mean250_pct`：**1.4624 → 1.4635**（差 0.0011）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/1/days`：**360 → 364**（差 4）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/1/idle_days`：**10 → 14**（差 4）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/1/idle_share`：**0.0278 → 0.0385**（差 0.0107）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/1/realized_pct`：**1.4328 → 1.4099**（差 -0.0229）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/3/days`：**1088 → 1094**（差 6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/3/idle_days`：**45 → 44**（差 -1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/3/idle_share`：**0.0414 → 0.0402**（差 -0.0012）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/3/realized_pct`：**1.7242 → 1.7241**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/3/rolls`：**149 → 150**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/5/days`：**1820 → 1823**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/5/idle_days`：**77 → 80**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/5/idle_share`：**0.0423 → 0.0439**（差 0.0016）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/realized/5/realized_pct`：**1.894 → 1.8993**（差 0.0053）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/2/spot_pct`：**1.305 → 1.375**（差 0.07）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/annual_cny_realized_1y`：**8371.0 → 8224.0**（差 -147.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/annual_cny_spot`：**7670.0 → 7812.0**（差 142.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/edge_bp/1`：**16.6 → 14.1**（差 -2.5）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/edge_bp/3`：**4.9 → 5.6**（差 0.7）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/edge_bp/5`：**4.0 → 4.2**（差 0.2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/idle_days_1y`：**3 → 7**（差 4）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/idle_share_1y`：**0.0085 → 0.0196**（差 0.0111）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/mean250_pct`：**1.4673 → 1.4682**（差 0.0009）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/1/days`：**353 → 357**（差 4）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/1/idle_days`：**3 → 7**（差 4）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/1/idle_share`：**0.0085 → 0.0196**（差 0.0111）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/1/realized_pct`：**1.4734 → 1.4476**（差 -0.0258）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/3/days`：**1081 → 1087**（差 6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/3/idle_days`：**45 → 37**（差 -8）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/3/idle_share`：**0.0416 → 0.034**（差 -0.0076）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/3/realized_pct`：**1.7196 → 1.7322**（差 0.0126）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/3/rolls`：**74 → 75**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/5/days`：**1813 → 1816**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/5/idle_days`：**49 → 52**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/5/idle_share`：**0.027 → 0.0286**（差 0.0016）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/realized/5/realized_pct`：**1.9287 → 1.9328**（差 0.0041）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/3/spot_pct`：**1.35 → 1.375**（差 0.025）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/annual_cny_realized_1y`：**8372.0 → 8242.0**（差 -130.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/annual_cny_spot`：**7698.0 → 7812.0**（差 114.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/edge_bp/1`：**16.6 → 14.4**（差 -2.2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/edge_bp/3`：**7.5 → 11.2**（差 3.7）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/edge_bp/5`：**9.0 → 8.4**（差 -0.6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/idle_days_1y`：**2 → 0**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/idle_share_1y`：**0.0059 → 0.0**（差 -0.0059）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/mean250_pct`：**1.4628 → 1.4639**（差 0.0011）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/1/days`：**338 → 364**（差 26）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/1/idle_days`：**2 → 0**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/1/idle_share`：**0.0059 → 0.0**（差 -0.0059）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/1/realized_pct`：**1.4737 → 1.4508**（差 -0.0229）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/1/rolls`：**12 → 13**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/3/days`：**1087 → 1093**（差 6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/3/idle_days`：**23 → 1**（差 -22）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/3/idle_share`：**0.0212 → 0.0009**（差 -0.0203）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/3/realized_pct`：**1.7465 → 1.7882**（差 0.0417）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/3/rolls`：**38 → 39**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/5/days`：**1798 → 1801**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/5/idle_days`：**6 → 9**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/5/idle_share`：**0.0033 → 0.005**（差 0.0017）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/realized/5/realized_pct`：**1.9789 → 1.9755**（差 -0.0034）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/rolls_1y`：**12 → 13**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/4/spot_pct`：**1.355 → 1.375**（差 0.02）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/annual_cny_realized_1y`：**8068.0 → 8132.0**（差 64.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/annual_cny_spot`：**7471.0 → 7641.0**（差 170.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/edge_bp/1`：**11.2 → 12.5**（差 1.3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/edge_bp/3`：**11.7 → 10.0**（差 -1.7）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/edge_bp/5`：**4.6 → 3.0**（差 -1.6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/idle_days_1y`：**8 → 0**（差 -8）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/idle_share_1y`：**0.0285 → 0.0**（差 -0.0285）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/mean250_pct`：**1.4335 → 1.4348**（差 0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/1/days`：**281 → 364**（差 83）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/1/idle_days`：**8 → 0**（差 -8）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/1/idle_share`：**0.0285 → 0.0**（差 -0.0285）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/1/realized_pct`：**1.4201 → 1.4313**（差 0.0112）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/1/rolls`：**3 → 4**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/3/days`：**1009 → 1015**（差 6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/3/idle_days`：**8 → 14**（差 6）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/3/idle_share`：**0.0079 → 0.0138**（差 0.0059）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/3/realized_pct`：**1.788 → 1.7765**（差 -0.0115）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/5/days`：**1741 → 1744**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/5/idle_days`：**12 → 15**（差 3）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/5/idle_share`：**0.0069 → 0.0086**（差 0.0017）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/realized/5/realized_pct`：**1.9347 → 1.9215**（差 -0.0132）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/rolls_1y`：**3 → 4**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_ladder/tenors/5/spot_pct`：**1.315 → 1.345**（差 0.03）｜SECTION_ADVANCED｜这一节自己换了代：`cash_ladder` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/book_rate/annual_cny`：**10067.0 → 10073.0**（差 6.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/book_rate/gap_vs_spot_bp`：**-59.7 → -50.81**（差 8.89）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/book_rate/gap_vs_spot_cny`：**-3392.0 → -2887.0**（差 505.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/book_rate/pct`：**1.772 → 1.7731**（差 0.0011）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/mean_tail/annual_cny`：**7668.0 → 7680.0**（差 12.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/mean_tail/net_annual_cny`：**6287.0 → 6299.0**（差 12.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/mean_tail/net_pct`：**1.1067 → 1.1088**（差 0.0021）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/mean_tail/pct`：**1.3497 → 1.3518**（差 0.0021）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/spot/annual_cny`：**6675.0 → 7187.0**（差 512.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/spot/net_annual_cny`：**5295.0 → 5806.0**（差 511.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/spot/net_pct`：**0.932 → 1.022**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/spot/pct`：**1.175 → 1.265**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/spread_vs_tail_cny`：**-993.0 → -493.0**（差 500.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/spread_vs_window_cny`：**-5148.0 → -4634.0**（差 514.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/window/annual_cny`：**11824.0 → 11821.0**（差 -3.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/window/net_annual_cny`：**10443.0 → 10440.0**（差 -3.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/window/net_pct`：**1.8382 → 1.8377**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/block/window/pct`：**2.0812 → 2.0807**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/book/cny`：**579.0 → 635.0**（差 56.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/book/pct`：**1.772 → 1.7731**（差 0.0011）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/calendar_days`：**21 → 23**（差 2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/fee_cny`：**85.0 → 97.0**（差 12.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/gap_bp`：**85.77 → 77.79**（差 -7.98）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/gap_bp_gross`：**59.7 → 50.81**（差 -8.89）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/gap_cny`：**280.0 → 279.0**（差 -1.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/rolls`：**15 → 17**（差 2）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/spot/cny`：**384.0 → 453.0**（差 69.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/spot/pct`：**1.175 → 1.265**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/spot_net/cny`：**299.0 → 356.0**（差 57.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_money/forward/spot_net/pct`：**0.9143 → 0.9952**（差 0.0809）｜SECTION_ADVANCED｜这一节自己换了代：`cash_money` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_yield/annual_cny`：**6675.0 → 7187.0**（差 512.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_yield/daily_cny`：**27.0 → 29.0**（差 2.0）｜SECTION_ADVANCED｜这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_yield/rate_20d_pct`：**1.2345 → 1.232**（差 -0.0025）｜SECTION_ADVANCED｜这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_yield/rate_pct`：**1.175 → 1.265**（差 0.09）｜SECTION_ADVANCED｜这一节自己换了代：`cash_yield` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/family_coherence/floor_extrapolation/gap_pp`：**0.114 → -0.085**（差 -0.199）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/floor_extrapolation/observed_pp`：**0.43 → 0.51**（差 0.08）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/floor_extrapolation/predicted_pp`：**0.316 → 0.595**（差 0.279）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/floor_extrapolation/tolerance_pp`：**0.139 → 2.582**（差 2.443）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/null_calibration/not_separable_share`：**0.035 → 0.0345**（差 -0.0005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/null_calibration/reject_share`：**0.965 → 0.9656**（差 0.0006）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/signflip/arms/0/cells_positive`：**5 → 7**（差 2）｜RECOVERED_OLD_VALUE｜昨天的 5 今天仍在这页上：`/capacity_edge/summary/n_names`（改名，不是重算）
- `/family_coherence/signflip/arms/1/cells_positive`：**6 → 8**（差 2）｜RECOVERED_OLD_VALUE｜昨天的 6 今天仍在这页上：`/authority/gate_h`（改名，不是重算）
- `/family_coherence/signflip/arms/2/cells_positive`：**0 → 1**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
- `/family_coherence/signflip/arms/3/cells_positive`：**8 → 12**（差 4）｜RECOVERED_OLD_VALUE｜昨天的 8 今天仍在这页上：`/alias_stability/stability/per_window/0/refused_days_apart`（改名，不是重算）
- `/family_coherence/signflip/arms/4/cells_positive`：**7 → 9**（差 2）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/signflip/arms/5/cells_positive`：**7 → 8**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/family_coherence/signflip/n_reject`：**4 → 3**（差 -1）｜RECOVERED_OLD_VALUE｜昨天的 4 今天仍在这页上：`/alias_stability/stability/refused/0/trials`（改名，不是重算）
- `/family_coherence/signflip/n_reject_standing`：**3 → 2**（差 -1）｜RECOVERED_OLD_VALUE｜昨天的 3 今天仍在这页上：`/premium_leak/nav_ruler_history/159655/n_obs`（改名，不是重算）
- `/forward/nav`：**1.0037762754 → 1.0037812718**（差 5e-06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/forward/since_inception_pct`：**0.3776 → 0.3781**（差 0.0005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
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
- `/k_gap/account_base_gap_cny`：**29571.45 → 28373.5**（差 -1197.95）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/k_gap/nav_account_cny`：**998061.6 → 1000000.0**（差 1938.4）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lookahead/affected_faces`：**94 → 74**（差 -20）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/causal/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/causal/cagr`：**0.0845 → 0.0841**（差 -0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/causal/cagr_pp`：**8.45 → 8.41**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/causal/sharpe`：**0.874 → 0.869**（差 -0.005）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_carry/bars`：**1665 → 1663**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_carry/cagr`：**0.0898 → 0.0911**（差 0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_carry/cagr_pp`：**8.98 → 9.11**（差 0.13）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_carry/sharpe`：**0.941 → 0.952**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_no_carry/bars`：**1665 → 1663**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_no_carry/cagr`：**0.0839 → 0.0851**（差 0.0012）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_no_carry/cagr_pp`：**8.39 → 8.51**（差 0.12）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/ledger_no_carry/sharpe`：**0.885 → 0.896**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/published/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/published/cagr`：**0.0941 → 0.0959**（差 0.0018）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/published/cagr_pp`：**9.41 → 9.59**（差 0.18）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/arms/published/sharpe`：**0.971 → 0.987**（差 0.016）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/decomposition/carry_pp`：**0.59 → 0.6**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/decomposition/mark_basis_pp`：**0.06 → -0.1**（差 -0.16）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/decomposition/price_of_the_one_bar_pp`：**0.96 → 1.18**（差 0.22）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/0/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/0/cagr`：**0.1565 → 0.1582**（差 0.0017）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/0/cagr_pp`：**15.65 → 15.82**（差 0.17）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/0/sharpe`：**1.504 → 1.518**（差 0.014）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/1/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/1/cagr`：**0.1243 → 0.1241**（差 -0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/1/cagr_pp`：**12.43 → 12.41**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/1/sharpe`：**1.271 → 1.268**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/1/vol`：**0.0999 → 0.1**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/2/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/2/cagr`：**0.0941 → 0.0959**（差 0.0018）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/2/cagr_pp`：**9.41 → 9.59**（差 0.18）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/2/sharpe`：**0.971 → 0.987**（差 0.016）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/3/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/3/cagr`：**0.0845 → 0.0841**（差 -0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/3/cagr_pp`：**8.45 → 8.41**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/3/sharpe`：**0.874 → 0.869**（差 -0.005）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/4/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/4/cagr`：**0.0773 → 0.0747**（差 -0.0026）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/4/cagr_pp`：**7.73 → 7.47**（差 -0.26）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/4/sharpe`：**0.797 → 0.773**（差 -0.024）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/5/bars`：**1664 → 1662**（差 -2）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/5/cagr`：**0.0503 → 0.0518**（差 0.0015）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/5/cagr_pp`：**5.03 → 5.18**（差 0.15）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/lag_ladder/5/sharpe`：**0.54 → 0.554**（差 0.014）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/gap_pp_per_year`：**0.96 → 1.18**（差 0.22）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_pp/-1`：**12.43 → 12.41**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_pp/-2`：**15.65 → 15.82**（差 0.17）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_pp/0`：**9.41 → 9.59**（差 0.18）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_pp/1`：**8.45 → 8.41**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_pp/20`：**5.03 → 5.18**（差 0.15）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_pp/5`：**7.73 → 7.47**（差 -0.26）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/verdict/ladder_spread_pp`：**10.62 → 10.64**（差 0.02）｜SECTION_ADVANCED｜这一节自己换了代：`lookahead` 2026-11-17 → 2026-11-13（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/positions/accrual/rate_latest`：**1.175 → 1.265**（差 0.09）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/positions/accrual/repo_quotes`：**3769 → 3767**（差 -2）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/positions/replay/cash_interest_cny`：**526.17 → 449.68**（差 -76.49）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/positions/replay/rf_missing_bars`：**0 → 2**（差 2）｜RECOVERED_OLD_VALUE｜昨天的 0 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_held_every_window`（改名，不是重算）
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
- `/premium_leak/own_ruler/159519/above_own_median_pp`：**-1.1434 → -0.5951**（差 0.5483）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159519/last_pct`：**-0.9895 → -0.4407**（差 0.5488）｜RECOVERED_OLD_VALUE｜昨天的 -0.9895 今天仍在这页上：`/premium_leak/nav_ruler_history/159519/last_pct`（改名，不是重算）
- `/premium_leak/own_ruler/159519/last_pctile`：**7.1 → 25.0**（差 17.9）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159519/last_rank`：**720 → 579**（差 -141）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159519/median_pct`：**0.1539 → 0.1543**（差 0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159519/n_obs`：**775 → 772**（差 -3）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159519/p10_pct`：**-0.8857 → -0.8827**（差 0.003）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159519/p90_pct`：**1.5163 → 1.5173**（差 0.001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/above_own_median_pp`：**7.8586 → 6.8923**（差 -0.9663）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/last_pct`：**9.0909 → 8.1154**（差 -0.9755）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/last_pctile`：**98.37 → 96.44**（差 -1.93）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/last_rank`：**16 → 35**（差 19）｜RECOVERED_OLD_VALUE｜昨天的 16 今天仍在这页上：`/alias_stability/stability/per_window/1/refused_days_apart`（改名，不是重算）
- `/premium_leak/own_ruler/159655/median_pct`：**1.2323 → 1.2231**（差 -0.0092）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/n_obs`：**984 → 982**（差 -2）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/p10_pct`：**-0.6486 → -0.6498**（差 -0.0012）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/159655/p90_pct`：**6.2278 → 6.2027**（差 -0.0251）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/510760/above_own_median_pp`：**-0.0652 → -0.0795**（差 -0.0143）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/510760/last_pct`：**-0.0558 → -0.0701**（差 -0.0143）｜RECOVERED_OLD_VALUE｜昨天的 -0.0558 今天仍在这页上：`/premium_leak/nav_ruler_history/510760/last_pct`（改名，不是重算）
- `/premium_leak/own_ruler/510760/last_pctile`：**31.26 → 26.31**（差 -4.95）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/510760/last_rank`：**1029 → 1101**（差 72）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/510760/n_obs`：**1497 → 1494**（差 -3）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/510760/p10_pct`：**-0.1627 → -0.1623**（差 0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/510760/p90_pct`：**0.2146 → 0.2148**（差 0.0002）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/above_own_median_pp`：**-0.131 → 0.0269**（差 0.1579）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/last_pct`：**-0.1828 → -0.025**（差 0.1578）｜RECOVERED_OLD_VALUE｜昨天的 -0.1828 今天仍在这页上：`/premium_leak/nav_ruler_history/512040/last_pct`（改名，不是重算）
- `/premium_leak/own_ruler/512040/last_pctile`：**20.91 → 56.12**（差 35.21）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/last_rank`：**1509 → 836**（差 -673）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/median_pct`：**-0.0519 → -0.052**（差 -0.0001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/n_obs`：**1908 → 1905**（差 -3）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/p10_pct`：**-0.2723 → -0.2728**（差 -0.0005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/512040/p90_pct`：**0.1451 → 0.1454**（差 0.0003）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/above_own_median_pp`：**-0.7649 → -0.6372**（差 0.1277）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/last_pct`：**-0.8279 → -0.6964**（差 0.1315）｜RECOVERED_OLD_VALUE｜昨天的 -0.8279 今天仍在这页上：`/premium_leak/nav_ruler_history/513690/last_pct`（改名，不是重算）
- `/premium_leak/own_ruler/513690/last_pctile`：**15.62 → 20.24**（差 4.62）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/last_rank`：**1124 → 1060**（差 -64）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/median_pct`：**-0.063 → -0.0592**（差 0.0038）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/n_obs`：**1332 → 1329**（差 -3）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/p10_pct`：**-1.0441 → -1.0446**（差 -0.0005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler/513690/p90_pct`：**1.1978 → 1.1987**（差 0.0009）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/own_ruler_summary/revert_to_own_median_cny`：**4183.31 → 4187.15**（差 3.84）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/stress/if_premium_reverts_to_own_median_cny`：**-4183.31 → -4187.15**（差 -3.84）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/premium_leak/stress/if_premium_reverts_to_own_median_pct_of_nav`：**-0.4183 → -0.4187**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/defects/0/disk_n`：**5222 → 5221**（差 -1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/0/declared_n`：**210 → 211**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/0/laneside/local_disk_n`：**186 → 187**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/0/local_disk_n`：**186 → 187**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/1/laneside/local_disk_n`：**27 → 1**（差 -26）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/1/local_disk_n`：**27 → 1**（差 -26）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/same_beta_benchmark/maxdd`：**-0.0401 → -0.0402**（差 -0.0001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/ticket_book/sharpe`：**1.688 → 1.687**（差 -0.001）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/vs_basket/book_nav`：**1.0037762754 → 1.0037812718**（差 5e-06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/vs_basket/excess_pp`：**2.9518 → 2.9523**（差 0.0005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明

同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；没有这两条说明的，就是这页偷偷换了数。

## 还有哪些节在同 bar 上改了数（224 个）

- `alias_census`：106 个
- `premium_leak`：37 个
- `premium_forward`：14 个
- `futures_sleeve`：12 个
- `carry_regime`：11 个
- `futures_hedge_tail`：9 个
- `family_coherence`：8 个
- `futures_hedge`：8 个
- `roster_audit`：6 个
- `positions`：3 个
- `forward`：2 个
- `k_gap`：2 个
- `vs_basket`：2 个
- `futures_ladder`：1 个
- `idle_cash`：1 个
- `same_beta_benchmark`：1 个
- `ticket_book`：1 个

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
