# ETF book -- what the tape says a side costs (cutoff 2026-11-26)

the card charges every leg a flat 10 bp/side -- what do these names actually quote, and does the book survive the tape's answer?

**Verdict: CONSERVATIVE | SURVIVES**

the names this book actually traded quote a measured one-way cost of 5.9 bp half-spread; the card charges 10 bp, which is more than the tape says (the card over-charges) -- on the tape's cost the same engine earns 9.4% CAGR / 0.97 Sharpe (each name at its own 75th percentile: 9.0% / 0.93), so the book survives the measured cost

| arm | cost / side | CAGR | Sharpe | max drawdown |
|---|---|---|---|---|
| the card's assumption | 10.0 bp | 8.9% | 0.92 | -11.8% |
| the tape (turnover weighted) | 5.9 bp | 9.4% | 0.97 | -11.4% |
| tape, every name at its own p75 | 9.0 bp | 9.0% | 0.93 | -11.7% |

Control: the identical engine at 10 bp, run on the card's own window (2026-11-26 -> 2026-11-26), reproduces the published 8.9% within 0.5pp -> PASS.
Since that card the panel has grown to 2026-11-26, where the same book reads 8.92% (+0.00pp). That gap is the book moving, not the engine.

Tape: 189 traded names carry an estimate (median own-median 13.3 bp, median p75 27.2 bp of price). Widest traded names: 159967 31.8 bp, 512690 30.4 bp, 512010 27.0 bp, 159966 26.8 bp, 159952 26.6 bp.

Decisions priced 84 of 84 (0 dropped: fewer than 60% of the traded weight had a tape on that bar).

How to read it: the estimator is a proxy, not a quote tape -- on a wide-range day the implied spread absorbs volatility, which is why the p75 arm is the pessimistic bound and not a forecast. The measured arm is the number to compare with the 10 bp the card charges; the p75 arm is what happens if the whole book trades at the wide end of its own history. Criteria were frozen before the first run (written before the first run).
