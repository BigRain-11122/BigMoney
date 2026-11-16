# the carry sleeve, booked forward

evidence cutoff: **2026-11-16** | contract bars to **2026-11-13** | generated 2026-11-16T22:13:05 | source judgement: `results/idx_fut_desk_sheet.json`

The two dates are printed because they are two dates: the ticket is judged on the continuous panel and the contract cache can lag it by a few sessions, so a ticket stamped with the judgement date is not a fill at that date.

Forward lines only.  The forward series starts at the anchor below and grows one bar a day; the replay block is labelled and never merged into it.

## forward (what this position has actually made since the anchor)

| product | contract | lots | notional | since | bars | NAV (CNY) | P&L | index leg | discount leg | max DD | rolls |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IC | IC2612 | 4 | 800 x spot | 2026-11-13 | 1 | 1,000,000.00 | +0.0000% | +0 | +0 | 0.000% | 0 |
| IM | IM2612 | 4 | 800 x spot | 2026-11-13 | 1 | 1,000,000.00 | +0.0000% | +0 | +0 | 0.000% | 0 |

## replay (the same position over the last 1 year -- a backtest, kept apart)

| product | window | days | total | of which index | of which discount | max DD |
|---|---|---|---|---|---|---|
| IC | 2025-11-13..2026-11-13 | 242 | -11.90% of capital | -70.35% | +58.45% | -72.18% |
| IM | 2025-11-13..2026-11-13 | 242 | -21.28% of capital | -97.21% | +75.93% | -74.63% |

**Read the two legs together.**  The ticket's headline carry is an *excess* number: it is what the future earns over the index, not what the account earns.  At this size the index leg dominates the absolute line, so a year that looks like a broken carry can be a working carry inside a falling index -- and the reverse.  Sizing is therefore a decision about the index exposure, not about the discount.

## the same position at the 8% vol target (two arms, because they are two trades)

Vol is measured on the same replay window as the block above (2025-11-13..2026-11-13, 242 bar(s)), not on the full contract history, so it answers 'what would this size have put on the table this year' rather than 'how volatile is the discount forever'.

| product | arm | vol of 1 lot | lots for 8% | lots at or below | capital for 1 lot | this ticket's lots | vol of those lots |
|---|---|---|---|---|---|---|---|
| IC | index + carry | 448,941 CNY/yr (44.89% of capital) | 0.18 | 0 | 5,611,768 | 4 | 179.58% |
| IC | carry only | 89,690 CNY/yr (8.97% of capital) | 0.89 | 0 | 1,121,125 | 4 | 35.88% |
| IM | index + carry | 428,642 CNY/yr (42.86% of capital) | 0.19 | 0 | 5,358,019 | 4 | 171.46% |
| IM | carry only | 91,909 CNY/yr (9.19% of capital) | 0.87 | 0 | 1,148,864 | 4 | 36.76% |

## what the hedge costs (the short leg's carry, not an estimate)

| product | long carry | cheapest hedge | hedge cost | net carry | verdict | index corr |
|---|---|---|---|---|---|---|
| IC | 6.856 pp/yr | short IF | 0.650 pp/yr | +6.206 pp/yr | HEDGE_KEEPS_THE_CARRY | 0.886 |
| IM | 8.068 pp/yr | short IF | 0.650 pp/yr | +7.418 pp/yr | HEDGE_KEEPS_THE_CARRY | 0.834 |

**Read the two arms together.**  The ticket sizes on drawdown survival -- how many lots survive the drawdown this sleeve has already seen.  That is a different ruler from the book's 8% vol target: unhedged, one lot is mostly index beta, so the target buys a fraction of a lot; hedged to the discount it buys a whole lot or more.  The hedge is priced at the short leg's own carry, which is why the cheap hedge is the contract sitting nearest par -- shorting a leg that carries as much as the long one hands the sleeve away, and that shows up as a negative net carry rather than as a caveat.

Basis risk is printed as the daily-return correlation of the two indices: a cross-index hedge leaves that residual behind, and it is not netted out of the net-carry column.

Entry is filled at the anchor close and rolls are booked at the same close (no slippage assumed, printed as `entry_fill_assumed_at_close` and `n_rolls` so a reader can charge them).

