# How precise is "3,919 lots"?

`BAND_WIDER_THAN_THE_DATING` · `BETA_ERROR_IS_CHEAP_IN_RISK_TERMS`

Evidence cutoff **2026-11-20**.  Fitted on 43 periods ending 2023-12-31; 34 periods were held back and are printed, never used to choose anything.

## 1. The short version

- The beta behind every ticket in this family is **0.9013**, and its standard error is **0.0526** (t = 17.13 on 41 degrees of freedom).
- Its two-sided 95% band is **0.7950 .. 1.0076** — a width of **0.2126**.
- On 1,000,000 that band is **3457 .. 4381 lots**: **924 lots wide**, against the **595 lots** the price date moves the same ticket (r2028).
- The beta fitted on the held-back periods is **1.0263** — using it would move the ticket by **543 lots**, the same order again.
- But the risk barely notices: the worst end of the band adds only **0.79 pp** of annualised residual volatility over the point estimate (line: 1.0pp).

So the honest instruction is not *3,919 lots* and not *3,918.83*.  It is **about 3,900 lots, give or take 900** — and because the risk does not care where in that band you land, the ticket should print the round number.

## 2. The fit and its own error

| fit | periods | beta | se(beta) | t | 95% band | R^2 |
|---|---|---|---|---|---|---|
| in-sample (frozen at 2023-12-31) | 43 | 0.9013 | 0.0526 | 17.13 | 0.7950 .. 1.0076 | 0.8774 |
| held back (after 2023-12-31) | 34 | 1.0263 | 0.0800 | 12.83 | 0.8634 .. 1.1891 | 0.8373 |
| full window | 77 | 0.9707 | 0.0472 | 20.57 | 0.8766 .. 1.0647 | 0.8494 |
| IM arm, its own window | 52 | 0.9757 | 0.0574 | 17.01 | 0.8605 .. 1.0909 | 0.8526 |

The point estimate is not new: it re-derives r2022's published 0.9013 (max absolute difference 0.00e+00, which is floating-point noise on the same arithmetic).  Nothing here is re-fitted against later data to make the band look better.

The two fits disagree by more than either one's standard error: in-sample 0.9013, held-back 1.0263.  That is the second thing this face measures — the beta is not a constant that happens to have sampling error; it moves.

### Rolling fits, 20 periods each, 10 apart

| from | to | periods | beta | se(beta) |
|---|---|---|---|---|
| 2020-07-06 | 2022-01-24 | 20 | 0.908 | 0.108 |
| 2021-04-29 | 2022-11-23 | 20 | 0.885 | 0.056 |
| 2022-02-28 | 2023-09-15 | 20 | 0.893 | 0.061 |
| 2022-12-21 | 2024-07-18 | 20 | 1.280 | 0.114 |
| 2023-10-23 | 2025-05-20 | 20 | 1.118 | 0.079 |
| 2024-08-15 | 2026-03-17 | 20 | 0.940 | 0.074 |

Range across rolling fits: **0.885 .. 1.280** — about 0.395 wide, or 7.5 times the in-sample standard error.  A single number cannot represent this.

## 3. Three ways to get a different lot count

All three are printed on the same capital (1,000,000) and the same price (2.300 on 2026-11-20 for 512100):

| what changes | from | to | lots moved | source |
|---|---|---|---|---|
| the price date | 3919 | 3323 | **595** | r2028 (11-11 book, 11-20 price) |
| the beta's 95% band | 3457 | 4381 | **924 wide** | this face |
| the beta from held-back data | 3919 | 4462 | **543** | this face |

The band is **1.55x** the date shift.  Read the other way: r2028's *DATING_MOVES_THE_ORDER* is true, and it is the smallest of the three effects.

## 4. What the error costs in risk

Lots are not the goal; removed volatility is.  Residual = book − beta × hedge, annualised on the full window (book itself: 27.34%).

| beta taken | residual annual vol | vs point estimate |
|---|---|---|
| 0.7950 (ci_low) | 11.55% | +0.79 pp |
| 0.9013 (point) | 10.76% | +0.00 pp |
| 1.0076 (ci_high) | 10.65% | -0.11 pp |
| 1.0000 (one_unit) | 10.64% | -0.12 pp |
| 1.0263 (oos_beta) | 10.71% | -0.05 pp |

`BETA_ERROR_IS_CHEAP_IN_RISK_TERMS`: the worst end of the 95% band adds only 0.79pp of annualised residual volatility over the point estimate (the line is 1.0pp) -- a beta that is off by a whole standard error barely changes the risk removed

This is why the ticket should stop at whole hundreds.  Rounding 3918.83 to 3900 moves the implied beta by 0.00433 — 8.23% of one standard error, and less than the width of its own band by two orders of magnitude.

## 5. The ladder

| capital | arm | one lot | lots | 95% band | band width | lots per 0.01 beta |
|---|---|---|---|---|---|---|
| 1,000,000 | etf | 230 | 3918.83 | 3456.72 .. 4380.94 | 924.22 | 43.48 |
| 1,000,000 | im | 1109120 | 0.88 | 0.78 .. 0.98 | 0.21 | 0.01 |
| 3,000,000 | etf | 230 | 11756.49 | 10370.16 .. 13142.83 | 2772.67 | 130.43 |
| 3,000,000 | im | 1109120 | 2.64 | 2.33 .. 2.95 | 0.62 | 0.03 |
| 10,000,000 | etf | 230 | 39188.32 | 34567.20 .. 43809.43 | 9242.24 | 434.78 |
| 10,000,000 | im | 1109120 | 8.80 | 7.76 .. 9.84 | 2.08 | 0.09 |
| 20,000,000 | etf | 230 | 78376.63 | 69134.40 .. 87618.87 | 18484.47 | 869.57 |
| 20,000,000 | im | 1109120 | 17.59 | 15.52 .. 19.67 | 4.16 | 0.18 |

The futures arm's band is narrower in lots only because one contract is 1,109,120 CNY: at 1,000,000 the whole band (0.78 .. 0.98 lots) sits inside a single contract, which is the r2027 finding restated — that arm cannot be sized to a beta at this capital at all.

## 6. What this face does not say

- No new data and no new strategy: the book, the prices and the beta are the same files r2022–r2028 read.
- The 95% band is a sampling band under the classical OLS error model.  It does **not** cover the possibility that the relationship itself changes — the held-back fit (1.0263 vs 0.9013) is the printed evidence that it does.
- Costs, basis, carry, margin and borrow are not modelled here; they are quoted from the faces that own them.
- The band is on the *ratio*, not on the book's own value: if the book is not marked, both the point estimate and the band sit on a stale capital (r2028).
- A narrower band is available by fitting on more periods, at the price of fitting on data the reader cannot see yet.  This face does not choose that trade; it prints both.

## Reproduction

```
python scripts/astock_veto_hedge_band.py selftest
python scripts/astock_veto_hedge_band.py run
python scripts/astock_veto_hedge_band.py check
```
