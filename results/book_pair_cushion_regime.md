# The cushion, split by what the convertible market costs

Generated 2026-11-28T06:01:42+08:00 · bars to **2026-11-27** · 82 months, 81 of them labelled (the last month is month-to-date through 2026-11-27)

**Verdict: `CUSHION_DIFFERENCE_NOT_SEPARABLE`**

Question: the 30/70 book was measured as a dilution, not a hedge (r2179) and that average was separable from noise (r2181). But the cb sleeve is the dual-low book, and a convertible is mostly a premium over parity -- so the question here is whether the cushion is a property of the sleeve or a property of a *cheap* market.

| regime | months | mean month | falling months | cushion | better in | rising months | upside given up |
|---|---|---|---|---|---|---|---|
| cheap | 6 | +1.18% | 3 | +0.26 pp | 1/3 | 3 | +1.19 pp |
| mid | 29 | +1.48% | 6 | +0.93 pp | 4/6 | 23 | -0.24 pp |
| rich | 46 | +0.28% | 22 | +0.26 pp | 10/22 | 24 | -0.70 pp |

Months available to each side of the split: **22 falling months in rich months vs 9 in the rest** (the gate asks for 8 each). The CB market spent most of this window in the top tertile of its own premium history, which is a fact about the sample before it is a fact about the cushion.

Difference in cushion, rich months minus the rest: **-0.44 pp** (95% band -1.34 .. +0.65; share of resamples at or below zero 0.8062).

## What the rule would have cost

Rule: hold cash in the cb sleeve while the previous month end said the market was in the top tertile of its own premium history; otherwise hold the book. Priced at 10bp per side on the 0.30 cb share.

| arm | cagr | sharpe | maxdd | worst month | months |
|---|---|---|---|---|---|
| rule | 10.01% | 1.391 | -4.37% | -3.56% | 81 |
| always_on | 9.39% | 1.234 | -8.40% | -3.57% | 81 |
| matched_exposure | 8.22% | 1.281 | -4.78% | -2.89% | 81 |

Rule verdict: **`THE_RULE_BEATS_ITS_OWN_EXPOSURE`** (rule Sharpe minus the same-exposure control, +0.11; the edge it was bought on is +0.14 pp a month, band +0.02 .. +0.27). The control arm carries the rule's own average cb exposure (**+0.43**) every month, so the difference is *when* the exposure was held, not *how much* of it there was.

Switches: **11**, cost paid **0.33 pp** of the wallet, months with the sleeve in cash: **46** of 81 scored.

Where that edge lives: the rule's whole edge over its own exposure is **+11.49 pp** across 81 months, of which the best 5 months carry **+65.50%** (**+7.53 pp**). An edge that sits in a handful of months is a drawdown story, not a return story -- read it beside the maxdd row above, not alone.

## Where the market sits today

Median conversion premium **65.61%** as of 2026-11-27 -- the **97.7th percentile** of its own history; last label **rich**.

So the rule puts the sleeve **in cash** today: the label now in force (**rich**) was read at the 2026-10-31 month end and governs the month ending 2026-11-30; the next decision falls on **2026-11-30**. With the sleeve in cash the wallet is **100% ETF / 0% cash**, not the split it was designed as.

## What this face does not claim

- the premium regime is a market-wide median; the sleeve holds 20 bonds, so a market-rich month need not be a sleeve-rich month
- the rule is priced on monthly switches only; intra-month runs are not modelled
- the cb arm and the etf arm are the parents' published arms -- this face does not re-test them
- there is one window: 2020-02-29..2026-11-27. The CB market was rich in 46 of 81 labelled months and in cash in 46 of them, so the rule reads mostly as 'be out of the sleeve when it is expensive' over a single premium cycle -- a repeated reading is what would make its 0.142 pp a month edge durable
- the cheap side holds only 3 falling months -- the cheap-vs-rich split is printed for the record and is not evidence of anything

Reconciliation against the parent's own cb window: reproduced.

