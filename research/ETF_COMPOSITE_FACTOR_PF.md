# ETF composite factor portfolio — does the IC edge survive construction and costs?

- date: 2026-10-25 (r1241 authored the script + null; r1242 bm-c corrected the
  sub-window metric basis — see the correction section)
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
| evidence cutoff | 2026-10-23 (panel last bar) |

## Results (results/etf_composite_pf.json, corrected basis)

Every window is measured on its own first level (`start_level` is recorded per row).
A sub-window slice of a running equity curve does **not** start at 1.0.

| book | window | start level | total | CAGR | vol | Sharpe | maxDD | turns/rebal |
|---|---|---|---|---|---|---|---|---|
| composite R5 | full | 0.998 | +57.2% | 6.87% | 9.3% | 0.79 | -12.0% | 0.92 |
| composite R5 | 2020-2023 | 0.998 | +14.3% | 3.40% | 8.5% | 0.45 | -12.0% | 0.92 |
| composite R5 | 2024+ | 1.138 | +37.8% | **12.12%** | 10.4% | 1.21 | -7.2% | 0.92 |
| composite R20 | full | 0.998 | +80.2% | 9.04% | 10.7% | 0.90 | -12.8% | 1.32 |
| composite R20 | 2020-2023 | 0.998 | +21.1% | 4.92% | 10.8% | 0.52 | -12.8% | 1.32 |
| composite R20 | 2024+ | 1.206 | +49.1% | **15.30%** | 10.5% | 1.47 | -10.2% | 1.32 |
| EW universe R20 | full | 1.001 | +17.9% | 2.44% | 18.1% | 0.23 | -40.0% | — |
| EW universe R20 | 2020-2023 | 1.001 | -8.5% | -2.21% | 17.2% | -0.05 | -33.0% | — |
| EW universe R20 | 2024+ | 0.911 | +29.5% | 9.65% | 19.3% | 0.60 | -18.9% | — |
| EW universe R5 | full | 1.001 | +16.5% | 2.27% | 18.2% | 0.22 | -40.4% | — |
| bench 510300 | full | 1.000 | +0.7% | 0.10% | 19.1% | 0.10 | -45.1% | — |
| bench 510300 | 2024+ | 0.832 | +21.0% | 7.03% | 19.0% | 0.47 | -19.3% | — |

Yearly composite R20: 2020 +11.5% / 2021 +3.7% / 2022 +1.7% / 2023 +3.1% /
2024 +9.2% / 2025 +35.7% / 2026 YTD +1.0%.

Current signal (2026-10-23) is defensive: the top-5 are all bond/money-market ETFs
(159396, 159395, 511190, 551900, 551510) — the book is not holding equity right now.

## Correction (r1242 bm-c): the 2024+ rows were overstated

The r1241 json measured every slice's `total_ret` as `level_end - 1` and `cagr` as
`level_end^(1/years) - 1`, i.e. **against the global base rather than the slice's own
first level**. Because the running level at 2024-01-01 was already 1.21 (R20) the
"2024+" row reported the six-year cumulative return and an inflated annualisation.

| row | reported (pre-fix) | corrected | delta |
|---|---|---|---|
| composite R20 2024+ | +79.7% / 23.26% | +49.1% / 15.30% | −8.0pp CAGR |
| composite R5 2024+ | +56.8% / 17.39% | +37.8% / 12.12% | −5.3pp CAGR |
| bench 510300 2024+ | +0.7% / 0.25% | +21.0% / 7.03% | **+6.8pp CAGR** |
| EW universe R20 2024+ | +18.0% / 6.07% | +29.5% / 9.65% | +3.6pp CAGR |

Sharpe, vol and maxDD were unaffected: they are computed on the slice's own returns
(maxDD on the slice's own running max), so the post-2024 Sharpe 1.47 vs the 0.60/0.47
controls still stands. The old numbers stay visible in `correction_r1242` inside the
json rather than being quietly overwritten.

What the correction changes in the reading: the benchmark was **not** flat after 2024
(+7.0%/yr, not +0.25%), so the OOS excess is ~8.3pp/yr over 510300 and ~5.7pp/yr over
the equal-weight universe — still a real gap, but a smaller one, and the "beats every
window by a wide margin" phrasing was a metric artefact, not a portfolio fact.

## Permutation null (300 shuffles, same untrained universe/costs)

Each factor's cross-section is shuffled **date by date**, which keeps the per-date rank
distribution and the universe but destroys the factor→return link; the composite is
rebuilt and the book re-run with the same cost model. The null is carried forward from
the pre-fix run: the construction, the signs and the shuffle scheme are untouched by the
metric fix (only the reporting of sub-windows changed).

| statistic | value |
|---|---|
| real period-Sharpe (R20) | 0.911 |
| null mean / p95 / max | 0.144 / 0.454 / 0.758 |
| p-value (null >= real) | **0.000** (0 / 300) |

Verdict on this question: **construction does not eat the edge**. No shuffled composite
came within 0.15 Sharpe of the real book in 300 tries.

## Honest caveats (all of them load-bearing)

1. **Close-to-close basis, no open fill.** The signal is read at the close of day t and
   the book is set at that same close. There is no open-print execution model, so the
   overnight gap is neither charged nor credited; entry slippage is unmodelled.
2. **Turnover cost is the whole story between R5 and R20.** R5 turns 0.92 per rebalance
   (~50 rebalances/yr ≈ 3.7%/yr of cost), R20 turns 1.32 but only ~12.6 rebalances/yr
   (≈1.3%/yr). R20 therefore carries a higher gross return with roughly a third of the
   drag — the R20 book, not R5, is the honest headline.
3. **The 2024+ window is one regime.** 2025 alone (+35.7%) produces most of the
   post-2024 excess; 2020-2023 is positive but only ~3-5% CAGR.
4. **Roughly half the calendar is cash/bonds.** Across the 2020-2026 span the defensive
   sleeve (bond ETFs) occupies a large share of rebalances, so part of the return is
   carry, not equity selection. This has not been decomposed yet.
5. **Survivorship.** The panel is whatever `_load_prices` finds on disk; delisted ETFs
   are absent, biasing the universe (and any momentum sleeve) upward.
6. **Not actual liquidity.** A 20M CNY median turnover floor is a screen, not a fill.
   Top-5 concentration means a few hundred million of capacity at best.
7. **Exploratory only.** No preregistration, no marks. Promoting this to a paper
   account requires a prereg with an explicit exit axis (TRIAL_LABOR_LAW §4).

## Next step (pointer, not a promise)

(a) re-run with a genuine next-open fill using the already-loaded `openp` panel;
(b) split the book's return into equity-sleeve vs bond-sleeve contributions — the
bond carry question is the biggest unmeasured piece of the headline.