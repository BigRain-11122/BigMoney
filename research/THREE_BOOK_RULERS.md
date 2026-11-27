# Three books on one ruler

## The question

This repo now quotes three books in annual percentages. Readers compare them. The comparison is only fair if the three numbers are the same kind of thing. This face asks: on one window and one clock, are they?

## Answer

Two of them are. The third is not, and the third is the one that wins the table.

- ETF composite: **9.94%** cagr, vol 10.47%, Sharpe 0.950 (per unit of capital)
- CB dual-low sleeve: **6.34%** cagr, vol 12.93%, Sharpe 0.491 (per unit of capital)
- carry, basis arm: **10.22%** cagr, vol 3.21%, Sharpe 3.189 (per unit of **notional**)

The carry family prints three Sharpes for the same IC leg because it is three arms: basis-only 2.9720, excess-after-hedge 1.4162, unhedged per-lot points 0.5057. The one a sleeve can hold is the middle one.

## Why the smooth number is smooth

The basis arm removes the index. What is left is a slow, low-vol rent -- vol 3.21% a year against the index's own tens of percent. That is a real property of the trade and it is also why the number cannot be read as a book: the capital that must stand behind one contract is set by the hedged sleeve's vol, not by the basis's.

## What it costs to find out

At the book's 8% hard cap one IC lot needs 1,137,862 CNY of capital. The wallet has 1,000,000 CNY. Executable lots today: **0**. The published decision on the desk ticket is `WITHDRAW_FROM_TICKET`.

The vol-target identity turns Sharpe into capital return: 8% x 1.4162 = 11.33%. For the basis arm the same identity gives 23.78% -- and that is the arithmetic a reader would run if they took the page's Sharpe at face value.

## Verdict

`THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD`

On one window (2020-01-03..2026-11-26) and one clock the three books print 9.94% / 6.34% / 10.22% (ETF / CB / carry basis). The carry line wins and cannot be bought: it is the basis arm, quoted per notional, and the family's own hedged arm on the same leg is 1.42 Sharpe, not 2.97. At the book's 8.0% vol target one IC lot still needs 1,137,862 CNY of capital against a 1,000,000 CNY wallet, so the executable line is 0 lots.

## What would change this

- capital to 1,137,862 CNY: the same rule hands back one lot and the hedge arm's Sharpe becomes the book's Sharpe, at 11.33% expected on capital.
- a published arm that measures the basis rent against capital at the sleeve's own vol (the r2185 ruler argument): if that arm's Sharpe lands near the basis Sharpe, the gap in this page is a measurement artifact, not a holding cost.
- a common window that starts 2018-10 (IC's first bar) would give the carry arm six more years the other two books do not have; this face refuses that window on purpose.

## Caveats

- the carry arm is a daily excess return on notional; the ETF/CB books are returns on capital
- the carry row's sharpe on this common window is not the family's published 2.97 — that one is the 2017-2026 IC-only window; the two differ because the window differs, not because the rule changed
- 2020-01..2022-07 the carry arm is IC only (IM listed 2022-07-25); after that it is the mean of the two legs
- the ETF book's vol target makes its drawdown a dial, so its return is not a fair 'more risk more return' comparison
- costs: ETF/CB 10bp per side as published, carry 1.5bp per side as published

Generated 2026-11-27T23:13:43+08:00, cutoff 2026-11-26, verdict `THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD`.
