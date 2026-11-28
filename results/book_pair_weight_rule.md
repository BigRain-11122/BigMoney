# Would you have found the split without peeking? -- 2026-11-27

*generated 2026-11-28T05:59:26+08:00 · window 2020-01-03 -> 2026-11-27 (1672 bars, the overlap of both books) · every arm scored from 2021-02-01 (1410 bars)*

**THE_RULE_LOSES_TO_HOLDING_THE_SPLIT** -- A rule that only knows the past picks monthly / expanding and earns Sharpe 1.114, against 1.236 for just holding the published 30/70 with the same quarterly move -- and against the 1.076 the page prints, which assumes the weight was known in advance and the wallet walked back to it every day for free. The rule held 55% convertible at the median, went all-in on one book 0% of the time, and sat 24pp away from the published split on average. It also loses to a plain 50/50, which needs no hindsight at all (that arm is scored below).

The published split is 30% convertible / 70% ETF, taken from `results/book_pair_blend.json` field `best.w_cb` (taken as published -- this face never re-picks it).

## The rule, walked forward (past-only picks, 10bp per side on every move)

| cadence | lookback | moves | CAGR | Sharpe | max DD | median w_cb | all-in share | changes | mean distance from 30% |
|---|---|---|---|---|---|---|---|---|---|
| monthly ** | expanding | 70 | 9.41% | 1.114 | -10.1% | 55% | 0% | 31 | 24pp |
| monthly | trailing3y | 70 | 8.56% | 1.014 | -11.3% | 50% | 1% | 42 | 22pp |
| quarterly | expanding | 23 | 8.68% | 1.050 | -10.0% | 55% | 0% | 16 | 24pp |
| quarterly | trailing3y | 23 | 9.36% | 1.110 | -9.9% | 50% | 0% | 17 | 21pp |
| annual | expanding | 5 | 6.22% | 0.774 | -10.7% | 60% | 0% | 3 | 28pp |
| annual | trailing3y | 5 | 7.81% | 0.907 | -10.1% | 60% | 0% | 4 | 24pp |

## What the weight actually was, beside the split you were shown

| arm | w_cb | moves | CAGR | Sharpe | max DD |
|---|---|---|---|---|---|
| published 30/70, quarterly move, paid | 30% | 23 | 9.83% | 1.236 | -9.3% |
| published 30/70, daily walk-back, free (the page's number) | 30% | 1409 | 9.77% | 1.237 | -9.3% |
| 50/50, quarterly move, paid | 50% | 23 | 9.15% | 1.177 | -13.1% |
| published 30/70, quarterly move, paid, FULL window | 30% | 27 | 9.21% | 1.075 | -9.3% |

Best rule (`monthly` / `expanding`): it held between 10% and 85% convertible, sat at 55% at the median, changed its mind 31 times over 70 decisions, and was all-in on a single book in 0% of them.

## The test with no machinery: pick on the first half, score the second

- best weight on 2020-01-06 -> 2023-06-15: **55%** convertible (first-half Sharpe 0.938)
- that weight on the second half (quarterly move, paid): Sharpe 0.978, CAGR 7.89%, max DD -14.0%
- the published 30/70 on the same half: Sharpe 1.302, CAGR 10.91%, max DD -9.3%
- the best weight with the second half's own data (not attainable, printed as the size of the prize): 15% convertible at Sharpe 1.351

## The arm that needs no hindsight at all

A neutral 50/50, which needs no hindsight about which split is best, earns Sharpe 1.177 -- more than the best past-only rule's 1.114. So the money the rule gives up is the churn's, not the weight's: it pays to move and still lands on a worse split.

## Does this face read the same books as the page?

- free daily walk-back on the full window: Sharpe 1.076 against the blend face's 1.076 (diff +0.0000, match)
- the same arm restricted to the scored window: 1.237 (diff +0.1607) -- that difference is the window, not the books.

## How to read it

- trailing Sharpe of the static-weight blend on the bars strictly up to the decision date (no cost inside the pick, the cost is charged when the wallet actually moves).
- the rule may not speak until it has 244 bars; the wallet is parked at 50/50 before that and every arm is scored only after the warm-up, so no arm is paid for the learning year.
- moving x from one book to the other is a sell of x and a buy of x, so each move pays 2x the moved share at 10bp per side.
- Not in this cost: tax, bid-ask on the underlying names, the whole-lot grid, and the gap between a fund's NAV and its traded price.

## Unverified

- the cadence and the lookback are picked on the same window they are scored on -- a reader adopting either should expect less than the printed number
- the trailing Sharpe the rule maximises is itself noisy: with one year of warm-up the first picks rest on few bars and flip easily
- each parent's own unverified list still applies (etf pool survivorship, the cb book's close-fill assumption, its 2026 drawdown being one regime)
- tax, the underlying bid-ask and the whole-lot grid are not in this cost
- the 6.9-year overlap contains one ETF-only regime; a rule tested only inside it cannot be shown to survive an ETF bad year

