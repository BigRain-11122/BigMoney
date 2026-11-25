# The minute feed's first reader

generated 2026-11-26T04:53:48+08:00 | cutoff 2026-11-24 | feed `data/minute_feed`

`data/minute_feed/` has had a writer since 2026-09-15 and never a reader. This is its first one. It audits the delivery, prices the fill the book assumes, and sizes the question the board still calls data-blocked.

## What was delivered

| symbol | sessions | full | median bars | 09:30 missing | duplicate minutes | first | last |
|---|---|---|---|---|---|---|---|
| 510050 | 45 | 44 | 238 | 44 | 0 | 2026-09-15 | 2026-11-24 |
| 510300 | 45 | 44 | 238 | 44 | 0 | 2026-09-15 | 2026-11-24 |
| 510500 | 45 | 44 | 238 | 44 | 0 | 2026-09-15 | 2026-11-24 |
| 511010 | 9 | 8 | 223 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 511880 | 9 | 8 | 238 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 511990 | 9 | 8 | 238 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 512100 | 45 | 44 | 238 | 44 | 0 | 2026-09-15 | 2026-11-24 |
| 513100 | 12 | 0 | 0 | 0 | 0 | 2026-09-10 | 2026-09-28 |
| 518880 | 9 | 8 | 238 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 588000 | 45 | 44 | 238 | 44 | 0 | 2026-09-15 | 2026-11-24 |

A *full* session is one with at least 200 one-minute bars; earlier sessions are fragments of the collector's rolling window and are counted here rather than quietly dropped.

## What the feed cannot price at all

- no **09:30** print in any session of 510050, 510300, 510500, 511010, 511880, 511990, 512100, 518880, 588000 — the auction print the book actually fills against is not in this panel, so every ladder number below is measured from the first *continuous* print instead
- 09:30 missing in 9 symbol(s)
- 14:58 missing in 9 symbol(s)
- 14:59 missing in 9 symbol(s)
- 10:45 missing in 1 symbol(s)

## What buying later than the open costs

Measured against each session's first continuous print, in bp. Positive = you paid more by waiting; negative = waiting was cheaper. The 5 deep symbols (510050, 510300, 510500, 512100, 588000) are averaged inside each session first, so `n` is sessions, not rows.

| minute | n | mean bp | median bp | sd bp | t | share above zero |
|---|---|---|---|---|---|---|
| 09:45 | 44 | -5.28 | -6.35 | 54.81 | -0.64 | 45% |
| 10:00 | 44 | -12.94 | -13.41 | 63.73 | -1.35 | 41% |
| 10:30 | 44 | -17.04 | -11.60 | 88.78 | -1.27 | 36% |
| 11:30 | 44 | -6.30 | -25.37 | 99.56 | -0.42 | 39% |
| 14:00 | 44 | -12.78 | -31.21 | 129.52 | -0.65 | 34% |
| 14:57 | 44 | -14.59 | -50.39 | 151.22 | -0.64 | 43% |

Read it as a dispersion problem, not a forecast: the mean is the size of the toll and the sd is why a person cannot pick the good minute in advance. A t under 2 on 44 sessions says the average toll is not distinguishable from zero, not that waiting is free.

## The question the board still calls data-blocked

Does the first half hour predict the rest of the day? Census over the same full sessions, pooled per symbol:

| symbol | n | slope | t | sd first30 | sd rest | MDE mean bp | sessions for 5bp |
|---|---|---|---|---|---|---|---|
| 510050 | 44 | -0.5565 | -2.58 | 47.46 | 71.46 | 30.18 | 1603 |
| 510300 | 44 | -0.5754 | -1.82 | 42.08 | 89.56 | 37.83 | 2519 |
| 510500 | 44 | +0.1708 | 0.53 | 76.33 | 161.07 | 68.03 | 8145 |
| 512100 | 44 | +0.1673 | 0.56 | 93.43 | 180.80 | 76.36 | 10263 |
| 588000 | 44 | +0.0763 | 0.25 | 129.59 | 256.83 | 108.47 | 20709 |


Five slopes are tested at once here. A single |t| near 2.5 among five tests sits on the line a Bonferroni-style correction draws, and 44 sessions from one autumn regime is not a robustness check -- quote the slope as a measurement of this sample only.
`MDE mean bp` is the smallest rest-of-day move a 5 bp/session claim could clear at 80% power with this many sessions; `sessions for 5bp` is how many full sessions one symbol needs before that claim is even askable. Neither number is a result -- they are the price of asking.

## What this face does not say

- the feed carries no 09:30 (auction) print in any session, so the ladder's baseline is each session's first continuous print -- the book's real fill is the auction print this panel cannot see
- ladder bp is measured against each session's own first print, so a roll in price level between session and session cancels out
- the session-level table averages the deep symbols within one session before averaging sessions; the per-symbol rows in this JSON share that session noise
- the reversal block is a census with n, slope and the sessions still missing -- it is not a verdict and must not be quoted as one
- five reversal slopes are tested at once; |t| has to clear the per-test line that controls for that, and 44 sessions of one regime is not a robustness check
