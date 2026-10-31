# Does the commodity sleeve need a risk gate of its own?

Priced on the production engine through the same mechanism the concentration face uses: the sleeve's own score is set to NaN on the gated decision dates and the engine substitutes on its own grid -- nothing here re-implements selection, sizing or costs.

Cutoff 2026-10-30 | book 12 names, rebalance 20 bars, 10.0 bp/side, 8.0% vol target | baseline CAGR 9.60% / max drawdown -11.77% over 6.82 years.

| gate | sleeve off | CAGR vs baseline | max drawdown vs baseline | vs its own placebo | why |
|---|---|---|---|---|---|
| sleeve below its own 200d MA | 20/83 (24.1%) | -0.32pp | -2.77pp | loses | no drawdown gain vs baseline |
| sleeve vol > own trailing p80 | 25/83 (30.1%) | +0.02pp | +0.86pp | wins by +5.00pp dd / +2.92pp CAGR | short of the pre-frozen bar |
| sleeve 10% below its trailing peak | 13/83 (15.7%) | -0.18pp | -1.27pp | wins by +2.43pp dd / +2.00pp CAGR | no drawdown gain vs baseline |

Verdict **NO_GATE**.

Closest arm: the vol gate (+0.86pp drawdown against a pre-frozen 1.0pp bar, beating its placebo by +5.00pp). It is named as the re-test candidate on new data; the bar is not moved to meet it.

## The three reusable pieces

1. **Dose-matched placebo, or the arm measures nothing.** Switching a sleeve off a fixed share of decisions changes exposure and timing at once; a placebo with the same number of off-decisions spread evenly holds the exposure change fixed and destroys only the timing. Note what the table shows: two of the three gates DO beat their own placebo, and still do not improve the drawdown against simply holding the sleeve -- so a signal can be real and still not be worth trading (a gate here buys a shorter holding period).

2. **Freeze the bar before the run, then quote the near miss.** The vol gate cut the drawdown 0.86pp against a pre-registered 1.0pp bar: the honest publication is "re-test candidate on new data, NOT adopted", never "bar 1.0 -> 0.8".

3. **A new face must reproduce the old face's deletion arm.** Deleting the whole sleeve has to land on the concentration face's published number on the same cutoff, or the two faces are quoting different books (live gap 0.0 pp).
