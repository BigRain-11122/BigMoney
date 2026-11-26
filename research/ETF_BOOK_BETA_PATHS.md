# ETF book: is the sizing window's beta a phase or a level?

Face: `results/etf_book_beta_paths.json`  ·  evidence cutoff 2026-11-25  ·  1670 paired bars, 1293 graded symbols

## Ruling

**UNDECIDABLE**

the two windows differ by 0.0213 beta=2.13pp of size, and the same book over another stretch of this world moves the reading by 0.1420 (sd, 500 bootstrap draws) -- the difference is 0.2 sd, below the 2.0 sd the rule needs, so this panel cannot tell a phase from a level -- and the ruler itself carries 12.2pp of k-noise, against the 1.9pp the window choice is worth: arguing about the window is arithmetic below the ruler's own resolution; sliding the SAME rule's 306-bar window through this history moves k from 0.291 to 1.000 (70.9pp between p10 and p90), so the window pair the desk has been arguing about is the small term; the path does drift (t=-3.33) -- that says the reading moves, not that this particular pair of windows can be told apart

## Readings

| reading | value |
| --- | --- |
| beta_now | 0.481394 |
| beta_full | 0.460084 |
| difference_abs | 0.021311 |
| noise_sd | 0.141992 |
| noise_ratio | 0.150083 |
| resolvable | False |
| beta_now_pctile | 69.565217 |
| path_median | 0.297907 |
| path_sd | 0.205505 |
| path_p10 | 0.170225 |
| path_p90 | 0.688981 |
| in_tail | False |
| path_drifts | True |
| k_from_now | 0.41546 |
| k_from_full | 0.434704 |
| k_gap_pp | -1.9244 |
| k_noise_pp | 12.25 |
| k_gap_pp_agrees | True |
| k_by_window_p10 | 0.291021 |
| k_by_window_p50 | 0.671349 |
| k_by_window_p90 | 1.0 |
| k_by_window_range_pp | 70.9 |
| window_choice_is_the_small_term | True |
| cny_gap_at_1m | -19244.0 |

Path slope -0.00386056 (t=-3.33054219196682, n=69)

## How to read this

The floor is a reciprocal (r1473): k = target / beta, so every 0.01 of beta is about 0.8pp of size on a 1,000,000 book at a 0.20 target. The two windows that matter are the 306-bar graded window that signs the floor in force and the all-history reading that would sign the wider one.

A difference that is smaller than the bootstrap spread is not a finding. `UNDECIDABLE` means: this panel cannot tell phase from level, so switching the signing window is a policy choice, not a correction -- pre-register it before changing production sizing.


data: `results/etf_book_beta_paths.json`
