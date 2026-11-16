# Is the de-levering timing, or just a smaller book?

Face: `results/etf_book_exposure_timing.json` (evidence cutoff 2026-11-16, 1664 bars, 84 decisions, 217.5 s).

All three arms hold the same names on the same 20-bar grid and pay the same 10 bp/side; only the exposure path differs.

| arm | CAGR | Sharpe | maxDD | vol | mean exposure | de-levered share | turnover/fill |
|---|---|---|---|---|---|---|---|
| production (8% vol target) | 9.03% | 0.946 | -13.26% | 10.06% | 0.708 | 88.0% | 0.938 |
| full (exposure 1.0) | 13.13% | 0.917 | -16.29% | 15.30% | 0.999 | 0.1% | 1.280 |
| constant (mean exposure 0.710) | 10.00% | 0.968 | -11.57% | 10.87% | 0.710 | 100.0% | 0.909 |

## Placebo: same exposure distribution, no timing

| | value |
|---|---|
| identity gap vs the untouched engine | 0.00e+00 (tol 1e-12) |
| arms | 20 (seed 20261031) |
| mean CAGR | 10.00% |
| mean Sharpe | 0.944 |
| mean exposure | 0.710 |
| exposure multiset preserved | True |
| production − constant | -0.97 pp |
| placebo band (p05..p95) | -1.73 .. +1.32 pp |
| constant − full (de-risking, not timing) | -3.13 pp |

## Verdict

**AVERAGE_EXPOSURE_ONLY** — TIMING_ADDS iff production beats the p95 of same-exposure placebo paths; TIMING_SUBTRACTS iff it loses to the p05; otherwise the overlay is average exposure, not timing

Read as: at matched average exposure the production exposure path earns -0.97 pp/yr against a placebo band of -1.73..+1.32 pp/yr, so what the operator is buying with the vol target is a smaller book, not a better-timed one.

## Caveats

- one panel, one grid; the placebo band is 20 permutations, not a null distribution over all orderings
- the constant arm is the book's own mean scale, so the comparison is matched on average exposure and not on realised volatility
- survivorship in the ETF pool travels with every arm here; the comparison is between arms on one panel, so it does not depend on the pool being complete
