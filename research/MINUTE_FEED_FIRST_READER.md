# The minute feed's first reader

generated 2026-11-26T23:33:45+08:00 | cutoff 2026-11-26 | feed `data/minute_feed`

`data/minute_feed/` has had a writer since 2026-09-15 and never a reader. This is its first one. It audits the delivery, prices the fill the book assumes, and sizes the question the board still calls data-blocked.

## What was delivered

| symbol | sessions | full | median bars | 09:30 missing | duplicate minutes | first | last |
|---|---|---|---|---|---|---|---|
| 510050 | 47 | 46 | 238 | 46 | 0 | 2026-09-15 | 2026-11-26 |
| 510300 | 47 | 46 | 238 | 46 | 0 | 2026-09-15 | 2026-11-26 |
| 510500 | 47 | 46 | 238 | 46 | 0 | 2026-09-15 | 2026-11-26 |
| 511010 | 9 | 8 | 223 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 511880 | 9 | 8 | 238 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 511990 | 9 | 8 | 238 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 512100 | 47 | 46 | 238 | 46 | 0 | 2026-09-15 | 2026-11-26 |
| 513100 | 12 | 0 | 0 | 0 | 0 | 2026-09-10 | 2026-09-28 |
| 518880 | 9 | 8 | 238 | 8 | 0 | 2026-09-15 | 2026-09-28 |
| 588000 | 47 | 46 | 238 | 46 | 0 | 2026-09-15 | 2026-11-26 |

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
| 09:45 | 46 | -6.91 | -6.35 | 55.67 | -0.84 | 46% |
| 10:00 | 46 | -13.49 | -13.41 | 63.37 | -1.44 | 41% |
| 10:30 | 46 | -15.61 | -5.69 | 87.13 | -1.22 | 37% |
| 11:30 | 46 | -7.88 | -25.37 | 98.19 | -0.54 | 39% |
| 14:00 | 46 | -17.55 | -37.74 | 128.66 | -0.93 | 33% |
| 14:57 | 46 | -20.89 | -57.85 | 150.85 | -0.94 | 41% |

Read it as a dispersion problem, not a forecast: the mean is the size of the toll and the sd is why a person cannot pick the good minute in advance. A t under 2 on 46 sessions says the average toll is not distinguishable from zero, not that waiting is free.

## The question the board still calls data-blocked

Does the first half hour predict the rest of the day? Census over the same full sessions, pooled per symbol:

| symbol | n | slope | t | sd first30 | sd rest | MDE mean bp | sessions for 5bp |
|---|---|---|---|---|---|---|---|
| 510050 | 46 | -0.5386 | -2.53 | 46.54 | 70.41 | 29.08 | 1557 |
| 510300 | 46 | -0.5755 | -1.84 | 41.24 | 88.72 | 36.65 | 2471 |
| 510500 | 46 | +0.0955 | 0.30 | 76.17 | 162.60 | 67.17 | 8301 |
| 512100 | 46 | +0.0618 | 0.21 | 93.04 | 185.55 | 76.65 | 10809 |
| 588000 | 46 | +0.0867 | 0.29 | 129.76 | 254.59 | 105.16 | 20349 |


Five slopes are tested at once here. A single |t| near 2.5 among five tests sits on the line a Bonferroni-style correction draws, and 44 sessions from one autumn regime is not a robustness check -- quote the slope as a measurement of this sample only.
`MDE mean bp` is the smallest rest-of-day move a 5 bp/session claim could clear at 80% power with this many sessions; `sessions for 5bp` is how many full sessions one symbol needs before that claim is even askable. Neither number is a result -- they are the price of asking.

## What this face does not say

- the feed carries no 09:30 (auction) print in any session, so the ladder's baseline is each session's first continuous print -- the book's real fill is the auction print this panel cannot see
- ladder bp is measured against each session's own first print, so a roll in price level between session and session cancels out
- the session-level table averages the deep symbols within one session before averaging sessions; the per-symbol rows in this JSON share that session noise
- the reversal block is a census with n, slope and the sessions still missing -- it is not a verdict and must not be quoted as one
- five reversal slopes are tested at once; |t| has to clear the per-test line that controls for that, and 44 sessions of one regime is not a robustness check
