# Was the live book's first five weeks normal?

generated 2026-11-28T23:46:53+0800 · cutoff 2026-11-27 · ledger results/etf_book_forward/LEDGER.json (sha16 f067f3b6447af067)

<!-- expectation-rows -->

## The record

| | live | backtest, whole history |
|---|---|---|
| bars | 26 (2026-10-23 to 2026-11-27) | 1673 (2020-01-02 to 2026-11-27) |
| total return | -1.14% | CAGR +8.73% |
| drawdown | -2.70% | worst -13.26% |
| annualised vol | 12.00% | 9.93% |
| cash share | 9.06% | mean 29.13% |

## Which ruler

The ledger books cash carry on 23 of its 26 bars, so the distribution below is the carry-on arm; the same book with cash earning nothing earns +8.14% a year against +8.73%, i.e. the ladder is worth 0.59 pp/yr and is not a rounding error.

Self-contradiction found in the ledger, reported not patched: the ledger's `config.cash` field ('cash leg earns 0 in the ledger (disclosed, not modelled away)') contradicts its own bars: 23 of 26 book a positive carry, and its `engine.cash_leg` says the repo ladder is charged. This face reads the bars, and says so rather than picking the string.

## Where the live window sits

| window | windows | live return | at or below | one in | live drawdown | as deep or deeper | one in |
|---|---|---|---|---|---|---|---|
| 4 weeks | 1653 (79 disjoint) | -1.14% | 21.1% | 5 | -2.70% | 31.3% | 3 |
| 5 weeks (the live window) | 1648 (64 disjoint) | -1.14% | 22.2% | 5 | -2.70% | 39.0% | 3 |
| 8 weeks | 1632 (39 disjoint) | -1.14% | 22.4% | 4 | -2.70% | 60.2% | 2 |
| 3 months | 1611 (26 disjoint) | -1.14% | 20.2% | 5 | -2.70% | 79.0% | 1 |

## Book minus its four-exposure basket

| window | windows | live excess | at or below | verdict |
|---|---|---|---|---|
| 4 weeks | 1653 | +2.79% | 90.0% | INSIDE_THE_USUAL_RANGE |
| 5 weeks (the live window) | 1648 | +2.79% | 87.4% | INSIDE_THE_USUAL_RANGE |
| 8 weeks | 1632 | +2.79% | 82.4% | INSIDE_THE_USUAL_RANGE |
| 3 months | 1611 | +2.79% | 78.0% | INSIDE_THE_USUAL_RANGE |

## How long the book stays under water

| depth reached | episodes | recovered | median bars | p90 bars | share back within 63 bars |
|---|---|---|---|---|---|
| 1.14% deep | 23 | 22 | 14 | 159 | 68.2% |
| 2.70% deep | 14 | 13 | 76 | 226 | 46.2% |

## Verdict

The live book is -1.14% after 26 bars (2026-10-23 to 2026-11-27). In this book's own history, 22.2% of 26-bar windows ended at or below that, i.e. roughly one window in 5; the drawdown of 2.70% was matched or exceeded by 39.0% of windows (one in 3). Against a plain four-ETF basket the same window is +2.79pp, which sits at the 87.4% mark of the book's own excess windows. Reaching this depth has happened 23 times since 2020-01-02; the book came back in a median of 14 bars (68% within a quarter), so the honest expectation is weeks under water, not days.

## What this does not say

- 26 bars is five weeks. The overlapping window count is not a sample size; the disjoint count is, and both are printed.
- The pool is today's listed ETFs, so the equity sleeve still carries survivorship (inherited from the backtest, not introduced here).
- A window inside the historical range is not evidence the book is fine -- it is evidence that nothing in these five weeks separates it from the backtest.
- The live book is running at 12.00% annualised vol against an 8.00% target on a 26-bar estimate: the vol window is the one number this face cannot separate from noise at this length.
- Research output, not an investment recommendation.

<!-- expectation-rows -->
