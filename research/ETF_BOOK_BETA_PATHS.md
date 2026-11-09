# ETF book: is the sizing window's beta a phase or a level?

Face: `results/etf_book_beta_paths.json`  ·  evidence cutoff 2026-11-06  ·  1657 paired bars, 1279 graded symbols

## Ruling

**UNDECIDABLE**

the two windows differ by 0.0577 beta=5.77pp of size, and the same book over another stretch of this world moves the reading by 0.1394 (sd, 500 bootstrap draws) -- the difference is 0.4 sd, below the 2.0 sd the rule needs, so this panel cannot tell a phase from a level -- and the ruler itself carries 10.4pp of k-noise, against the 4.9pp the window choice is worth: arguing about the window is arithmetic below the ruler's own resolution; sliding the SAME rule's 306-bar window through this history moves k from 0.287 to 1.000 (71.2pp between p10 and p90), so the window pair the desk has been arguing about is the small term; the path does drift (t=-3.53) -- that says the reading moves, not that this particular pair of windows can be told apart

## Readings

| reading | value |
| --- | --- |
| beta_now | 0.517074 |
| beta_full | 0.459406 |
| difference_abs | 0.057668 |
| noise_sd | 0.139448 |
| noise_ratio | 0.413543 |
| resolvable | False |
| beta_now_pctile | 70.588235 |
| path_median | 0.291557 |
| path_sd | 0.206671 |
| path_p10 | 0.170015 |
| path_p90 | 0.697979 |
| in_tail | False |
| path_drifts | True |
| k_from_now | 0.386792 |
| k_from_full | 0.435345 |
| k_gap_pp | -4.8553 |
| k_noise_pp | 10.43 |
| k_gap_pp_agrees | True |
| k_by_window_p10 | 0.287496 |
| k_by_window_p50 | 0.686297 |
| k_by_window_p90 | 1.0 |
| k_by_window_range_pp | 71.25 |
| window_choice_is_the_small_term | True |
| cny_gap_at_1m | -48553.0 |

Path slope -0.00416447 (t=-3.5292459691173392, n=68)

## How to read this

The floor is a reciprocal (r1473): k = target / beta, so every 0.01 of beta is about 0.8pp of size on a 1,000,000 book at a 0.20 target. The two windows that matter are the 306-bar graded window that signs the floor in force and the all-history reading that would sign the wider one.

A difference that is smaller than the bootstrap spread is not a finding. `UNDECIDABLE` means: this panel cannot tell phase from level, so switching the signing window is a policy choice, not a correction -- pre-register it before changing production sizing.


data: `results/etf_book_beta_paths.json`
