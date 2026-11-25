# the carry sleeve, booked forward

evidence cutoff: **2026-11-24** | contract bars to **2026-11-23** | generated 2026-11-25T09:14:37 | source judgement: `results/idx_fut_desk_sheet.json`

The two dates are printed because they are two dates: the ticket is judged on the continuous panel and the contract cache can lag it by a few sessions, so a ticket stamped with the judgement date is not a fill at that date.

Forward lines only.  The forward series starts at the anchor below and grows one bar a day; the replay block is labelled and never merged into it.

## forward (what this position has actually made since the anchor)

| product | contract | lots | notional | since | bars | NAV (CNY) | P&L | index leg | discount leg | max DD | rolls |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IC | IC2612 | 4 | 800 x spot | 2026-11-13 | 7 | 746,400.00 | -25.3600% | -265,427 | +11,827 | -25.360% | 0 |
| IM | IM2612 | 4 | 800 x spot | 2026-11-13 | 7 | 583,360.00 | -41.6640% | -430,433 | +13,793 | -41.664% | 0 |

## replay (the same position over the last 1 year -- a backtest, kept apart)

| product | window | days | total | of which index | of which discount | max DD |
|---|---|---|---|---|---|---|
| IC | 2025-11-24..2026-11-23 | 241 | -1.95% of capital | -58.84% | +56.89% | -71.28% |
| IM | 2025-11-24..2026-11-23 | 241 | -32.29% of capital | -106.61% | +74.32% | -81.78% |

**Read the two legs together.**  The ticket's headline carry is an *excess* number: it is what the future earns over the index, not what the account earns.  At this size the index leg dominates the absolute line, so a year that looks like a broken carry can be a working carry inside a falling index -- and the reverse.  Sizing is therefore a decision about the index exposure, not about the discount.

## the same position at the 8% vol target (two arms, because they are two trades)

Vol is measured on the same replay window as the block above (2025-11-24..2026-11-23, 241 bar(s)), not on the full contract history, so it answers 'what would this size have put on the table this year' rather than 'how volatile is the discount forever'.

| product | arm | vol of 1 lot | lots for 8% | lots at or below | capital for 1 lot | this ticket's lots | vol of those lots |
|---|---|---|---|---|---|---|---|
| IC | index + carry | 451,981 CNY/yr (45.20% of capital) | 0.18 | 0 | 5,649,768 | 4 | 180.79% |
| IC | carry only | 90,365 CNY/yr (9.04% of capital) | 0.89 | 0 | 1,129,566 | 4 | 36.15% |
| IM | index + carry | 435,335 CNY/yr (43.53% of capital) | 0.18 | 0 | 5,441,685 | 4 | 174.13% |
| IM | carry only | 92,733 CNY/yr (9.27% of capital) | 0.86 | 0 | 1,159,159 | 4 | 37.09% |

## what the hedge costs (the short leg's carry, not an estimate)

| product | long carry | cheapest hedge | hedge cost | net carry | verdict | index corr |
|---|---|---|---|---|---|---|
| IC | 6.554 pp/yr | short IF | 0.498 pp/yr | +6.056 pp/yr | HEDGE_KEEPS_THE_CARRY | 0.879 |
| IM | 7.492 pp/yr | short IF | 0.498 pp/yr | +6.994 pp/yr | HEDGE_KEEPS_THE_CARRY | 0.821 |

**Read the two arms together.**  The ticket sizes on drawdown survival -- how many lots survive the drawdown this sleeve has already seen.  That is a different ruler from the book's 8% vol target: unhedged, one lot is mostly index beta, so the target buys a fraction of a lot; hedged to the discount it buys a whole lot or more.  The hedge is priced at the short leg's own carry, which is why the cheap hedge is the contract sitting nearest par -- shorting a leg that carries as much as the long one hands the sleeve away, and that shows up as a negative net carry rather than as a caveat.

Basis risk is printed as the daily-return correlation of the two indices: a cross-index hedge leaves that residual behind, and it is not netted out of the net-carry column.

## the same target read in whole lots

| product | budget at the target | vol of 1 lot (hedged) | lots if the target is a ceiling | nearest integer | the ticket's lots | verdict |
|---|---|---|---|---|---|---|
| IC | 80,000 CNY | 90,365 CNY | 0 | 1 | 4 | THE_RULER_DECIDES_THE_LOTS |
| IM | 80,000 CNY | 92,733 CNY | 0 | 1 | 4 | THE_RULER_DECIDES_THE_LOTS |

**Read this beside the fraction above.**  The same sentence -- "8% vol target" -- names three positions: 0 / 1 / 4 lots at 1,000,000 CNY.  Each way out has a price, and the page prints it whole:

- **IC**  A keep 8%: one lot needs 1,129,566 CNY; B keep 1,000,000 CNY: one lot needs 9.0365%; C keep both: 0 lot.
- **IM**  A keep 8%: one lot needs 1,159,159 CNY; B keep 1,000,000 CNY: one lot needs 9.2733%; C keep both: 0 lot.

### the road this book runs on: A_keep_target_raise_capital

Target **8%**, read as **hard_cap_vol_le_target** (decided 2026-11-17 in bm-c round 1779). 8% is a risk dial and not a fit (results/etf_vol_target_sweep.json, book n5: target 8% prints 11.49% cagr / -10.56% maxdd / sharpe 1.13 against 15.56% / -16.04% / 1.00 with no target -- sharpe moves 0.08 while return and drawdown scale together, so the target sets the size of the drawdown, not the return). raising it to 9% to make one contract fit would spend 1pp of drawdown tolerance for no return; the capital is the free variable and the risk number is a preference

| product | lots the adopted ruler allows now | first executable rung (CNY) | gap to that rung (CNY) | the desk's lots | the desk's lots against the ruler | capital those lots would need (CNY) |
|---|---|---|---|---|---|---|
| IC | **0** | 1,129,566 | 129,566 | 4 | OUT_OF_RULER (4.52x the budget) | 4,518,264 |
| IM | **0** | 1,159,159 | 159,159 | 4 | OUT_OF_RULER (4.64x the budget) | 4,636,636 |

Zero lots at this capital is the rule's answer, not a missing measurement: one hedged lot's annualised vol is larger than the whole budget, so the sleeve sits below its first rung. The desk's size is printed beside the ruler and **not rewritten** -- it is an input to this book, and a conformance flag is the honest way to carry a disagreement.

### what it costs to open this book

To open this book at all needs 1,129,566 CNY of capital (IC account). IC is 129,566 CNY short of its first lot (capital 1,000,000, gap 12.96%). IM is 159,159 CNY short of its first lot (capital 1,000,000, gap 15.92%). IC: the desk's 4 lot(s) are withdrawn from the ticket and the executable line is 0; IM: the desk's 4 lot(s) are withdrawn from the ticket and the executable line is 0. The forward paper series that ran on 8 lot(s) across the accounts is kept and labelled FUNDED_BY_A_LARGER_CAPITAL: it is what a larger account would have done, not what this one can. It comes back the moment the capital does.

Funding line read from `results/idx_fut_carry_open_capital.json` (generated 2026-11-24T16:13:44+08:00, cutoff 2026-11-23), so a reader can see which pass it came from.

| product | executable lots | desk lots withdrawn | forward paper lots (relabelled) | first rung (CNY) | gap at this capital (CNY) | capital those desk lots would need (CNY) |
|---|---|---|---|---|---|---|
| IC | **0** | 4 | 4 (FUNDED_BY_A_LARGER_CAPITAL) | 1,129,566 | 129,566 | 4,518,264 |
| IM | **0** | 4 | 4 (FUNDED_BY_A_LARGER_CAPITAL) | 1,159,159 | 159,159 | 4,636,636 |

Cheapest way in: **IC** at 1,129,566 CNY; both legs together 2,288,725 CNY. Decision **WITHDRAW_FROM_TICKET** (2026-11-17, bm-c round 1780). Fund the account to the first rung and re-run: the same rule hands the ticket back one lot and this file prints it -- the withdrawal is conditional on capital, not a judgement about the sleeve

Scope of the withdrawal: the executable ticket only. The forward paper series is an append-only evidence line: it is re-labelled FUNDED_BY_A_LARGER_CAPITAL, never rewritten, truncated or deleted

Entry is filled at the anchor close and rolls are booked at the same close (no slippage assumed, printed as `entry_fill_assumed_at_close` and `n_rolls` so a reader can charge them).

