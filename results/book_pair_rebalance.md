# Keeping the wallet at its weight -- 2026-11-27

*generated 2026-11-28T05:58:25+08:00 · window 2020-01-03 -> 2026-11-27 (1672 bars, the overlap of both books)*

**REBALANCE_PAYS** -- Rebalancing quarterly pays: Sharpe 1.075 against 1.052 for holding, after 0.01pp of cost drag, with 27 moves over the window (0.05 one-way turnover per year); what the paid cadence buys is the paper number: the blend face's 1.076 assumes the wallet is walked back to 30/70 every day, and the best paid cadence lands at 1.075 -- so the edge is the price of not drifting, not a second source of return

Target: 30% convertible / 70% ETF, taken from `results/book_pair_blend.json` field `best.w_cb` -- this face does not re-pick it.

## Each cadence, after the cost of moving

Cost: 10bp per side; a move of x is a sell of x plus a buy of x, so each rebalance pays 2x of the traded share.

| cadence | moves | turnover/yr | CAGR | Sharpe | max DD | worst year | max drift | cost drag (pp CAGR) |
|---|---|---|---|---|---|---|---|---|
| hold | 0 | 0.00 | 8.96% | 1.052 | -8.9% | -5.1% | 8.9pp | 0.00 |
| every20 | 83 | 0.08 | 9.15% | 1.067 | -9.3% | -5.5% | 4.5pp | 0.02 |
| monthly | 82 | 0.08 | 9.13% | 1.068 | -9.3% | -5.5% | 4.8pp | 0.02 |
| quarterly | 27 | 0.05 | 9.21% | 1.075 | -9.3% | -5.5% | 5.3pp | 0.01 |
| semiannual | 13 | 0.04 | 9.23% | 1.070 | -9.1% | -5.3% | 7.5pp | 0.01 |
| annual | 6 | 0.03 | 9.26% | 1.071 | -8.9% | -5.1% | 7.2pp | 0.01 |

Left alone: left alone from 2020-01-03 to 2026-11-27, a 30/70 wallet ends at 25.6/74.4 and at its worst carried 8.9pp away from target -- that drift is what a paid cadence buys back.

## Does this face read the same books as the blend page?

- This face's daily, zero-cost arm: Sharpe 1.076 against the blend face's 30/70 1.076 (diff -0.0000, match).
- what the paid cadence buys is the paper number: the blend face's 1.076 assumes the wallet is walked back to 30/70 every day, and the best paid cadence lands at 1.075 -- so the edge is the price of not drifting, not a second source of return.

## Does a different per-side rate change the ranking?

| cost per side | holding Sharpe | best cadence | cadence Sharpe | cadence ahead? |
|---|---|---|---|---|
| 5bp | 1.052 | quarterly | 1.075 | yes |
| 10bp | 1.052 | quarterly | 1.075 | yes |
| 20bp | 1.052 | quarterly | 1.073 | yes |

## Does paying to rebalance move the answer away from the target weight?

| convertible share | hold | every 20 | quarterly | annual | best cadence |
|---|---|---|---|---|---|
| 10% | 1.024 | 1.024 | 1.027 | 1.025 | quarterly |
| 20% | 1.054 | 1.059 | 1.064 | 1.061 | quarterly |
| 30% ** | 1.052 | 1.067 | 1.075 | 1.071 | quarterly |
| 40% | 1.014 | 1.041 | 1.050 | 1.048 | quarterly |
| 50% | 0.946 | 0.982 | 0.991 | 0.992 | annual |
| 60% | 0.862 | 0.899 | 0.907 | 0.910 | annual |
| 70% | 0.773 | 0.805 | 0.811 | 0.816 | annual |
| 80% | 0.689 | 0.711 | 0.715 | 0.720 | annual |
| 90% | 0.613 | 0.624 | 0.626 | 0.628 | annual |

Best cell under cost: 30% convertible on `quarterly` at Sharpe 1.075; the target weight is 30%. Cost does not move the weight choice.

## How to read it

- moving an amount x from one book to the other is a sell of x and a buy of x -- the round trip is 2x the per-side rate, and each parent already pays its own 10bp inside its published series.
- the move is charged at the close of the bar the cadence fires, after that day's return; a reader who moves at the next open pays the same 2x on a slightly different price.
- Not in this cost: tax, bid-ask on the underlying names, the whole-lot grid, and the spread between a fund's NAV and its traded price.

## Unverified

- the cadence is picked on the same window it is scored on (in-sample pick): a reader who adopts it should expect less than the printed edge
- each parent's own unverified list still applies (etf pool survivorship, the cb book's close-fill assumption, its 2026 drawdown being one regime)
- the move is charged at the bar close, not at the open a reader would use
- tax, the underlying bid-ask and the whole-lot grid are not in this cost
- a 2x per-side round trip is the stated floor; a real desk moving size pays more

