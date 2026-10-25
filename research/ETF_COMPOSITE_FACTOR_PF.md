# ETF composite factor portfolio — does the IC edge survive construction and costs?

- date: 2026-10-25 (r1241, bm-c) — script authored by the dead r1241 window, this
  window completed the permutation null and froze the verdict.
- code: `scripts/etf_composite_pf.py`
- product: `results/etf_composite_pf.json`
- status: **exploratory measurement, zero marks, zero admission** (not a paper account,
  not a preregistered trial, no fleet lane claimed).

## Question

Single-factor IC says nothing about a tradable book. This asks the next question:
build the composite, hold the top-5, pay 8bp per side on turnover — is anything left?

## Setup (frozen in code)

| item | value |
|---|---|
| universe | 1,653 ETFs with >=120 bars and 20d median (close*volume) >= 20M CNY |
| factors | mom_12_1, price_position, drawdown_60, adx_14 (+), vol_60, intraday_range (-) |
| composite | cross-sectional rank-score in [-1,1], equal weight across factors with signs |
| book | top-5 equal weight, rebalance every 5 or 20 bars, start 2020-01-01 |
| cost | 8bp per side x turnover (no stamp duty on ETFs, no open-fill slippage — see caveats) |
| execution basis | signal at close of t, book set at that close, close-to-close returns |

## Results (results/etf_composite_pf.json)

| book | window | CAGR | vol | Sharpe | maxDD | turns/rebal |
|---|---|---|---|---|---|---|
| composite R5 | full | 6.83% | 9.3% | 0.79 | -12.0% | 0.92 |
| composite R5 | 2020-2023 | 3.33% | 8.5% | 0.45 | -12.0% | 0.92 |
| composite R5 | 2024+ | 17.39% | 10.4% | 1.21 | -7.2% | 0.92 |
| composite R20 | full | 9.00% | 10.7% | 0.90 | -12.8% | 1.32 |
| composite R20 | 2020-2023 | 4.85% | 10.8% | 0.52 | -12.8% | 1.32 |
| composite R20 | 2024+ | 23.26% | 10.5% | 1.47 | -10.2% | 1.32 |
| EW universe R5 | full | 2.28% | 18.2% | 0.22 | -40.4% | — |
| EW universe R20 | full | 2.46% | 18.1% | 0.23 | -40.0% | — |
| bench 510300 | full | 0.10% | 19.1% | 0.10 | -45.1% | — |

Yearly composite R20: 2020 +11.5% / 2021 +3.7% / 2022 +1.7% / 2023 +3.1% /
2024 +9.2% / 2025 +35.7% / 2026 YTD +1.0%.

## Permutation null (300 shuffles, same untrained universe/costs)

Each factor's cross-section is shuffled **date by date**, which keeps the per-date rank
distribution and the universe but destroys the factor→return link; the composite is
rebuilt and the book re-run with the same cost model.

| statistic | value |
|---|---|
| real period-Sharpe (R20) | 0.911 |
| null mean / p95 / max | 0.144 / 0.454 / 0.758 |
| p-value (null >= real) | **0.000** (0 / 300) |

Verdict on this question: **construction does not eat the edge**. The book beats its
equal-weight universe control and the 510300 benchmark on every window, and no
shuffled composite came within 0.15 Sharpe of the real one in 300 tries.

## Honest caveats (all of them load-bearing)

1. **Close-to-close basis, no open fill.** The signal is read at the close of day t and
   the book is set at that same close. There is no open-print execution model, so the
   overnight gap is neither charged nor credited; entry slippage is unmodelled.
2. **Turnover cost is the whole story between R5 and R20.** R5 turns 0.92 per rebalance
   (≈50 rebalances/yr ⇒ ≈3.7%/yr of cost), R20 turns 1.32 but only ≈12.6 rebalances/yr
   (≈1.3%/yr). R20 therefore carries a higher gross return with roughly a third of the
   drag — the R20 book, not R5, is the honest headline.
3. **The 2024+ window is one regime.** 2025 alone (+35.7%) produces most of the
   post-2024 excess; the 2020-2023 stretch is positive but only ~3-5% CAGR. A single
   strong year is not a Sharpe.
4. **Survivorship.** The panel is whatever `_load_prices` finds on disk; ETFs that were
   delisted are absent, biasing the universe (and any momentum sleeve) upward.
5. **Not actual liquidity.** A 20M CNY median turnover floor is a screen, not a fill.
   Top-5 concentration means a few hundred million of capacity at best.
6. **Exploratory only.** No preregistration, no `evidence_cutoff` trial record, no
   marks. Promoting this to a paper account requires a prerereg with an explicit exit
   axis (TRIAL_LABOR_LAW §4) and its own trial count.

## Next step (pointer, not a promise)

If picked up again: (a) re-run with a genuine next-open fill using the already-loaded
`openp` panel and compare — that is the single cheapest robustness test; (b) freeze an
R20 prereg with the six factors and the 8bp/edge cost model as the C1 null.