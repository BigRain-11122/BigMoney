# the carry sleeve, booked forward

evidence cutoff: **2026-11-16** | generated 2026-11-16T21:33:59 | source judgement: `results/idx_fut_desk_sheet.json`

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

Entry is filled at the anchor close and rolls are booked at the same close (no slippage assumed, printed as `entry_fill_assumed_at_close` and `n_rolls` so a reader can charge them).

