# the carry sleeve, booked forward

evidence cutoff: **2026-11-20** | contract bars to **2026-11-20** | generated 2026-11-22T03:11:17 | source judgement: `results/idx_fut_desk_sheet.json`

The two dates are printed because they are two dates: the ticket is judged on the continuous panel and the contract cache can lag it by a few sessions, so a ticket stamped with the judgement date is not a fill at that date.

Forward lines only.  The forward series starts at the anchor below and grows one bar a day; the replay block is labelled and never merged into it.

## forward (what this position has actually made since the anchor)

| product | contract | lots | notional | since | bars | NAV (CNY) | P&L | index leg | discount leg | max DD | rolls |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IC | IC2612 | 4 | 800 x spot | 2026-11-13 | 6 | 621,600.00 | -37.8400% | -362,380 | -16,020 | -37.840% | 0 |
| IM | IM2612 | 4 | 800 x spot | 2026-11-13 | 6 | 415,040.00 | -58.4960% | -559,730 | -25,230 | -58.496% | 0 |

## replay (the same position over the last 1 year -- a backtest, kept apart)

| product | window | days | total | of which index | of which discount | max DD |
|---|---|---|---|---|---|---|
| IC | 2025-11-20..2026-11-20 | 242 | -28.22% of capital | -83.73% | +55.50% | -74.74% |
| IM | 2025-11-20..2026-11-20 | 242 | -62.59% of capital | -133.93% | +71.33% | -85.92% |

**Read the two legs together.**  The ticket's headline carry is an *excess* number: it is what the future earns over the index, not what the account earns.  At this size the index leg dominates the absolute line, so a year that looks like a broken carry can be a working carry inside a falling index -- and the reverse.  Sizing is therefore a decision about the index exposure, not about the discount.

## the same position at the 8% vol target (two arms, because they are two trades)

Vol is measured on the same replay window as the block above (2025-11-20..2026-11-20, 242 bar(s)), not on the full contract history, so it answers 'what would this size have put on the table this year' rather than 'how volatile is the discount forever'.

| product | arm | vol of 1 lot | lots for 8% | lots at or below | capital for 1 lot | this ticket's lots | vol of those lots |
|---|---|---|---|---|---|---|---|
| IC | index + carry | 452,495 CNY/yr (45.25% of capital) | 0.18 | 0 | 5,656,186 | 4 | 181.00% |
| IC | carry only | 89,958 CNY/yr (9.00% of capital) | 0.89 | 0 | 1,124,479 | 4 | 35.98% |
| IM | index + carry | 435,394 CNY/yr (43.54% of capital) | 0.18 | 0 | 5,442,422 | 4 | 174.16% |
| IM | carry only | 92,208 CNY/yr (9.22% of capital) | 0.87 | 0 | 1,152,596 | 4 | 36.88% |

## what the hedge costs (the short leg's carry, not an estimate)

| product | long carry | cheapest hedge | hedge cost | net carry | verdict | index corr |
|---|---|---|---|---|---|---|
| IC | 6.599 pp/yr | short IF | 0.591 pp/yr | +6.008 pp/yr | HEDGE_KEEPS_THE_CARRY | 0.883 |
| IM | 7.557 pp/yr | short IF | 0.591 pp/yr | +6.966 pp/yr | HEDGE_KEEPS_THE_CARRY | 0.827 |

**Read the two arms together.**  The ticket sizes on drawdown survival -- how many lots survive the drawdown this sleeve has already seen.  That is a different ruler from the book's 8% vol target: unhedged, one lot is mostly index beta, so the target buys a fraction of a lot; hedged to the discount it buys a whole lot or more.  The hedge is priced at the short leg's own carry, which is why the cheap hedge is the contract sitting nearest par -- shorting a leg that carries as much as the long one hands the sleeve away, and that shows up as a negative net carry rather than as a caveat.

Basis risk is printed as the daily-return correlation of the two indices: a cross-index hedge leaves that residual behind, and it is not netted out of the net-carry column.

## the same target read in whole lots

| product | budget at the target | vol of 1 lot (hedged) | lots if the target is a ceiling | nearest integer | the ticket's lots | verdict |
|---|---|---|---|---|---|---|
| IC | 80,000 CNY | 89,958 CNY | 0 | 1 | 4 | THE_RULER_DECIDES_THE_LOTS |
| IM | 80,000 CNY | 92,208 CNY | 0 | 1 | 4 | THE_RULER_DECIDES_THE_LOTS |

**Read this beside the fraction above.**  The same sentence -- "8% vol target" -- names three positions: 0 / 1 / 4 lots at 1,000,000 CNY.  Each way out has a price, and the page prints it whole:

- **IC**  A keep 8%: one lot needs 1,124,479 CNY; B keep 1,000,000 CNY: one lot needs 8.9958%; C keep both: 0 lot.
- **IM**  A keep 8%: one lot needs 1,152,596 CNY; B keep 1,000,000 CNY: one lot needs 9.2208%; C keep both: 0 lot.

### the road this book runs on: A_keep_target_raise_capital

Target **8%**, read as **hard_cap_vol_le_target** (decided 2026-11-17 in bm-c round 1779). 8% is a risk dial and not a fit (results/etf_vol_target_sweep.json, book n5: target 8% prints 11.49% cagr / -10.56% maxdd / sharpe 1.13 against 15.56% / -16.04% / 1.00 with no target -- sharpe moves 0.08 while return and drawdown scale together, so the target sets the size of the drawdown, not the return). raising it to 9% to make one contract fit would spend 1pp of drawdown tolerance for no return; the capital is the free variable and the risk number is a preference

| product | lots the adopted ruler allows now | first executable rung (CNY) | gap to that rung (CNY) | the desk's lots | the desk's lots against the ruler | capital those lots would need (CNY) |
|---|---|---|---|---|---|---|
| IC | **0** | 1,124,479 | 124,479 | 4 | OUT_OF_RULER (4.50x the budget) | 4,497,916 |
| IM | **0** | 1,152,596 | 152,596 | 4 | OUT_OF_RULER (4.61x the budget) | 4,610,384 |

Zero lots at this capital is the rule's answer, not a missing measurement: one hedged lot's annualised vol is larger than the whole budget, so the sleeve sits below its first rung. The desk's size is printed beside the ruler and **not rewritten** -- it is an input to this book, and a conformance flag is the honest way to carry a disagreement.

### what it costs to open this book

To open this book at all needs 1,124,479 CNY of capital (IC account). IC is 124,479 CNY short of its first lot (capital 1,000,000, gap 12.45%). IM is 152,596 CNY short of its first lot (capital 1,000,000, gap 15.26%). IC: the desk's 4 lot(s) are withdrawn from the ticket and the executable line is 0; IM: the desk's 4 lot(s) are withdrawn from the ticket and the executable line is 0. The forward paper series that ran on 8 lot(s) across the accounts is kept and labelled FUNDED_BY_A_LARGER_CAPITAL: it is what a larger account would have done, not what this one can. It comes back the moment the capital does.

Funding line read from `results/idx_fut_carry_open_capital.json` (generated 2026-11-21T23:29:59+08:00, cutoff 2026-11-20), so a reader can see which pass it came from.

| product | executable lots | desk lots withdrawn | forward paper lots (relabelled) | first rung (CNY) | gap at this capital (CNY) | capital those desk lots would need (CNY) |
|---|---|---|---|---|---|---|
| IC | **0** | 4 | 4 (FUNDED_BY_A_LARGER_CAPITAL) | 1,124,479 | 124,479 | 4,497,916 |
| IM | **0** | 4 | 4 (FUNDED_BY_A_LARGER_CAPITAL) | 1,152,596 | 152,596 | 4,610,384 |

Cheapest way in: **IC** at 1,124,479 CNY; both legs together 2,277,075 CNY. Decision **WITHDRAW_FROM_TICKET** (2026-11-17, bm-c round 1780). Fund the account to the first rung and re-run: the same rule hands the ticket back one lot and this file prints it -- the withdrawal is conditional on capital, not a judgement about the sleeve

Scope of the withdrawal: the executable ticket only. The forward paper series is an append-only evidence line: it is re-labelled FUNDED_BY_A_LARGER_CAPITAL, never rewritten, truncated or deleted

Entry is filled at the anchor close and rolls are booked at the same close (no slippage assumed, printed as `entry_fill_assumed_at_close` and `n_rolls` so a reader can charge them).

