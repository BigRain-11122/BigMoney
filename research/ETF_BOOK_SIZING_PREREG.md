# ETF book: pinning the sizing ruler and pricing the cap

Face: `results/etf_book_sizing_prereg.json`  ·  evidence cutoff 2026-11-06  ·  1657 paired bars

## Ruling

**PREREG_PINNED**

the floor is signed by a 306-bar window and the reading carries 10.43pp of its own k-noise, so the band is fixed at +/-10.43pp (warn at 20.86pp, refuse beyond) and the window may change only by amendment; under the production estimator the de-lever-only clip binds on 0.0% of decision bars (None..None) and never in 2020_2022, 2023, 2026, while under the floor's own window estimator it binds 17 times -- its removal is CAP_NEVER_BINDS on the estimator that actually sizes the book

## Pre-registration (frozen)

| item | value |
| --- | --- |
| issuing window | 306 trailing bars, anchored on the last graded decision bar |
| may change | by pre-registered amendment only, never per round |
| band inside | +/-10.43 pp of k |
| band warn | +/-20.86 pp of k |
| band outside | print BAND_EXCEEDED, require a re-issue receipt |
| production effect | advisory in v1 -- the ticket's k is unchanged until the band reproduces twice |

## Does the de-lever-only cap bind?

**CAP_NEVER_BINDS**

under the estimator production actually uses (expanding beta, its minimum over the whole path is 0.42) the clip never meets its edge in 1531 decision bars -- there is no leverage to withhold; under the fixed-window estimator the clip fires on 17 of 68 readings (2024-08-22..2025-12-18, k_raw up to 2.9509, withholding up to 93.222pp of risk) and removing it would have bought 9.693pp of CAGR with -0.0099 of Sharpe over MDD -11.015pp -> CAP_COSTS_NOTHING_RISK_ADJUSTED.

| arm | CAGR | vol | Sharpe | max DD |
| --- | --- | --- | --- | --- |
| capped | 7.95% | 5.90% | 1.3267 | -5.80% |
| uncapped | 7.95% | 5.90% | 1.3267 | -5.80% |

| binding (production estimator) | value |
| --- | --- |
| decision_bars | 1531 |
| bars_capped | 0 |
| share_capped | 0.0 |
| first_capped | None |
| last_capped | None |
| k_raw_max | None |
| beta_at_max | None |
| risk_withheld_pp_max | None |
| expanding_beta_min | 0.42 |

### The same question under the floor's own estimator (trailing 306-bar beta (the floor's own reading))

**CAP_COSTS_NOTHING_RISK_ADJUSTED**

| arm | CAGR | vol | Sharpe | max DD |
| --- | --- | --- | --- | --- |
| capped | 14.33% | 11.37% | 1.2350 | -13.95% |
| uncapped | 24.03% | 19.10% | 1.2251 | -24.96% |

| window arm binding | value |
| --- | --- |
| decision_bars | 68 |
| bars_capped | 17 |
| first_capped | 2024-08-22 |
| last_capped | 2025-12-18 |
| k_raw_max | 2.9509 |
| delta_cagr_pp | 9.693 |
| delta_sharpe | -0.0099 |
| delta_mdd_pp | -11.015 |

this estimator does not size the book; it is reported because the desk has been arguing about the window, not about the engine rule

## Which era does the cap bind in?

The reading is a window-by-window beta from `results/etf_book_beta_paths.json`; k_raw = target / beta, capped when k_raw > 1.

| era | windows | beta range | k_raw range | capped windows |
| --- | --- | --- | --- | --- |
| 2020_2022 | 22 | 0.2556..0.8668 | 0.2307..0.7824 | 0 (0%) |
| 2023 | 12 | 0.2405..0.3569 | 0.5605..0.8315 | 0 (0%) |
| 2024_2025 | 24 | 0.1317..0.3088 | 0.6476..1.519 | 12 (50%) |
| 2026 | 10 | 0.4602..0.622 | 0.3215..0.4345 | 0 (0%) |

## How to read this

Two different rulers size this book and they are not interchangeable: the engine's expanding-beta rule decides k every rebalance bar, while the floor is a reciprocal signed by a fixed-length window. Pinning the window is what turns the second one from a choice into a rule -- otherwise every round can pick the window that prints the number it likes, inside a 10pp noise band it cannot resolve.

The cap question has a mechanical answer, not a taste one: capping only lowers exposure, so it is a real constraint exactly when the unlevered version would have raised Sharpe. If return falls and Sharpe does not rise, the cap bought nothing but a smaller number.

data: `results/etf_book_sizing_prereg.json`
