# ETF book -- what the tape says a side costs (cutoff 2026-10-30)

the card charges every leg a flat 10 bp/side -- what do these names actually quote, and does the book survive the tape's answer?

**Verdict: CONSERVATIVE | SURVIVES**

the names this book actually traded quote a measured one-way cost of 5.9 bp half-spread; the card charges 10 bp, which is more than the tape says (the card over-charges) -- on the tape's cost the same engine earns 10.1% CAGR / 1.04 Sharpe (each name at its own 75th percentile: 9.7% / 1.00), so the book survives the measured cost

| arm | cost / side | CAGR | Sharpe | max drawdown |
|---|---|---|---|---|
| the card's assumption | 10.0 bp | 9.6% | 0.99 | -11.8% |
| the tape (turnover weighted) | 5.9 bp | 10.1% | 1.04 | -11.4% |
| tape, every name at its own p75 | 9.0 bp | 9.7% | 1.00 | -11.7% |

Control: the identical engine at 10 bp reproduces the published 9.6% within 0.5pp -> PASS.

Tape: 189 traded names carry an estimate (median own-median 13.2 bp, median p75 27.4 bp of price). Widest traded names: 159967 31.5 bp, 512690 31.1 bp, 159966 26.6 bp, 159952 26.3 bp, 512010 26.2 bp.

Decisions priced 83 of 83 (0 dropped: fewer than 60% of the traded weight had a tape on that bar).

How to read it: the estimator is a proxy, not a quote tape -- on a wide-range day the implied spread absorbs volatility, which is why the p75 arm is the pessimistic bound and not a forecast. The measured arm is the number to compare with the 10 bp the card charges; the p75 arm is what happens if the whole book trades at the wide end of its own history. Criteria were frozen before the first run (written before the first run).
