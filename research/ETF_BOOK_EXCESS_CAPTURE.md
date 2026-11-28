# Does the book earn its excess on the way up or on the way down?

<!-- BEGIN GENERATED -->

**verdict: NEAR_PARITY_BOTH_SIDES_BUT_CARRIED_BY_FEW_BARS**

Bars 1673 (2020-01-02..2026-11-27, 6.85 years at 244 bars/yr). Basket = four-exposure equal weight on the book's own grid and fill.

## Selection arm (full size, no vol overlay) versus the basket

| half | bars | basket sum | book sum | capture | excess pp/yr |
|---|---|---|---|---|---|
| up (basket bar > 0) | 914 | 4.3427 | 4.5046 | 1.037 | 2.101 |
| down (basket bar < 0) | 758 | -3.6927 | -3.6033 | 0.976 | 0.984 |
| **total** | 1672 | | | | **3.085** |

Capture is `sum(book return in that half) / sum(basket return in that half)`. Sums, not means: 914 up-bars and 758 down-bars do not get averaged into each other.

## The headline arm, and the wedge between them

| arm | CAGR | vol | Sharpe | max DD | mean cash | up capture | down capture | excess pp/yr |
|---|---|---|---|---|---|---|---|---|
| basket (four exposures, equal weight) | 9.33% | 10.6% | 0.90 | -14.0% | 0.0% | 1.000 | 1.000 | 0.000 |
| production (8% vol target) | 8.73% | 9.9% | 0.89 | -13.3% | 29.1% | 0.674 | 0.628 | -0.554 |
| base_book (selection only) | 12.76% | 15.1% | 0.87 | -16.3% | 0.1% | 1.037 | 0.976 | 3.085 |
| overlay wedge | | | | | | | | -3.639 |

The production arm gives up 0.55 pp/yr of raw return against the basket and carries 0.7 pp less volatility and a 0.8 pp shallower drawdown. Whether that trade is worth it is the risk-dial decision the desk already priced elsewhere (8% is a risk dial, not a return dial); this table does not re-litigate it, it only prints both sides so `-0.55 pp/yr` cannot be read as "the book was pointless".

The selection arm buys its 3.08 pp/yr with **more** volatility (15.1% against the basket's 10.6%) and a Sharpe of 0.87 against 0.90 -- it is a return engine, not a risk-adjusted one, and the vol target is what turns it into the production row.
The production arm's capture in up-bars is below the selection arm's by construction: it sits in cash 29.1% of the time, so it cannot capture a full up-bar. That gap is the vol target's price, printed here as the wedge, not folded into the selection reading.

**Not the same number as r2229.** r2229 printed +2.79pp of excess on the **live 26-bar window** (the first five weeks of the ledger). The rows above are the **full 1,672-bar history**. A five-week window and a seven-year history disagreeing is not a defect in either; neither may stand in for the other.

## Is the excess recurring or a few bars?

Best 10% of bars (n=167) carry **953.1%** of the total log excess; removing them leaves **-26.322 pp/yr** against the headline's 3.085 pp/yr -- **the rest of the history loses to the basket**.

## Sign of the excess, by calendar year (selection arm)

| year | bars | log excess | sign |
|---|---|---|---|
| 2020 | 242 | -0.0075 | negative |
| 2021 | 243 | 0.0461 | positive |
| 2022 | 242 | 0.0538 | positive |
| 2023 | 242 | -0.1166 | negative |
| 2024 | 242 | -0.1001 | negative |
| 2025 | 243 | 0.2137 | positive |
| 2026 | 218 | 0.1221 | positive |

<!-- END GENERATED -->

## Why the two halves are not one number

A book that drops 0.5x while the basket drops and rises 1.0x while it rises is insurance: it is already earning its keep in the half where the reader is losing money, and adding capital does not make it better at the other half. A book that rises 1.2x in up-bars and falls 1.0x in down-bars is selection, and the risk of adding capital is that the selection stops finding names. Both print the same `+x pp` excess. This face separates them.

Caveats carried from the artifact: Capture ratios are sums over a half, not means: a half with a few violent bars is not averaged against the other half's many quiet bars.; The basket is the four-exposure equal-weight one the book itself is measured against (F.bench_block) -- the same ruler r2229 printed +2.79pp on.; The production arm holds 29.1% mean cash because of its 8% vol target; its capture ratios are structurally below 1 in up-bars. Reading that as bad selection is the error this face exists to prevent -- base_book is the selection arm.; The pool is today's listed ETFs, so the equity sleeve still carries survivorship inherited from the backtest, not introduced here.

