# ETF NAV restatement face

Generated 2026-11-28T23:20:20+0800 · evidence cutoff 2026-11-26

Verdict: `THE_DISPLACEMENT_IS_THE_NAV_DAY_AND_IT_IS_SMALL_ON_MEDIAN`

6505 premium prints can be checked exactly, because a later print carries the NAV they were missing (119 lagging prints still cannot; 13678 prints needed no correction at all). Median misstatement 0.58 pp of premium, p90 1.63 pp, worst 11.87 pp. On all 6505 rows where the session's NAV return is known, the error equals that NAV return times (1+true premium) to within 5.0e-07 pp: the reading is not noisy, it is displaced by exactly one NAV day, in that day's direction. Worst case: 512040 on 2023-12-13 printed -11.65% against a stale denominator while the true premium was +0.23% -- the row was wrong by -11.87 pp. It is not uniform: on prints whose NAV barely moved (<0.5%) the median error is 0.23 pp, while on the >=2% moves it is 2.47 pp -- the reading is most wrong exactly on the days the fund moved most. 1 print(s) were excluded as share conversions or distributions (|NAV day move| > 35%), because a split is not a premium move. Checked against r2227's band on the 6490 rows where both exist: the band contained the truth 5141 times and missed it 1349 times.

## Measured misstatement

| prints measured | still unmeasured | needed no correction | median abs | p90 abs | worst |
|---|---|---|---|---|---|
| 6505 | 119 | 13678 | 0.58 pp | 1.63 pp | 11.87 pp |

### By leg

| code | prints | median printed premium | median abs error | worst |
|---|---|---|---|---|
| 159519 | 779 | +0.22% | 0.63 pp | 10.44 pp |
| 159655 | 987 | +1.31% | 0.54 pp | 8.88 pp |
| 510760 | 1499 | +0.04% | 0.51 pp | 8.03 pp |
| 512040 | 1906 | +0.01% | 0.58 pp | 11.87 pp |
| 513690 | 1334 | -0.02% | 0.66 pp | 11.65 pp |

### By lag length

| lag (trading days) | prints | median abs error |
|---|---|---|
| 1 | 6505 | 0.58 pp |

### Error by how far that day's NAV moved

| |NAV day move| | prints | median abs error |
|---|---|---|
| <0.5% | 2885 | 0.23 pp |
| 0.5-1% | 1850 | 0.70 pp |
| 1-2% | 1394 | 1.32 pp |
| >=2% | 376 | 2.47 pp |

### Identity check (printed - true == r*(1+true))

| rows checked | max abs residual |
|---|---|
| 6505 | 5.00e-07 pp |

### Band check (r2227 method)

| inside | outside | no band |
|---|---|---|
| 5141 | 1349 | 15 |

Truth fell outside the printed band on:

| code | session | printed | true | band |
|---|---|---|---|---|
| 512040 | 2019-01-14 | -0.91% | -0.16% | -2.70%..-0.18% |
| 512040 | 2019-01-22 | -1.38% | -0.31% | -2.74%..-0.64% |
| 512040 | 2019-01-30 | -0.94% | +0.01% | -2.31%..-0.18% |
| 512040 | 2019-02-01 | +1.71% | -0.21% | +0.48%..+2.49% |
| 512040 | 2019-02-11 | +1.61% | -0.25% | +0.20%..+2.38% |

## Notes

- printed premium = close / NAV(nav_session) - 1, so a later print tagged with that session hands over the NAV we were missing; no external source is used.
- error = printed - true, in pp. Positive means the row overstated the premium: the leg looked dearer than it was.
- The identity printed - true = r*(1+true) is arithmetic, so the residual column is a check on the measurement, not a second finding; it is bounded by the stored precision of the printed premium (~1e-4 pp).
- A lagging print whose session NAV never appeared is counted as unmeasured, never as a zero error.
- Prints whose NAV day move exceeds EVENT_LINE (35%) are excluded as share conversions or distributions, and counted; a split is not a premium move.
- A day on which both the price and the NAV jump (an ex-dividend day) is COUNTED as a misstatement, because from the reader's side it is one -- but its cause is the distribution, and this face has no ex-dividend flag, so it cannot separate that cause from the lag.
- Scale: on a position worth 100,000 CNY, one point of premium is about 1,000 CNY of NAV paid over or under. This face sizes nothing.
