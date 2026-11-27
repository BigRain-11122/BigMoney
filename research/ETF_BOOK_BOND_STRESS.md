<!-- ETF-BOOK-BOND-STRESS:BEGIN -->

**verdict** `THE_DEFENSIVE_HALF_SURVIVES_WITHOUT_BOND_CARRY` / `BONDS_DID_LOSE_ROLLING_YEARS_IN_THIS_PANEL` / `THE_SLEEVE_IS_DRY_POWDER_NOT_AN_ENGINE`

cell N5_R20_10bp · evidence_cutoff 2026-11-27 · no vol target (the all-class book)

The book holds no equity on **912 of 1672 bars (54.5%)**, and bond+money is more than half of the book on **73.7%** of bars.
The bond+money leg carries **13.08% of the book's net log return** (78,706 CNY on the 1000000 ticket): the sleeve is where the book waits, not what pays it.

If that leg pays **nothing** while held, the book earns **7.72%/yr** (Sharpe 0.802, max drawdown -12.54%) instead of **8.95%/yr** (0.912, -12.54%) -- -1.23pp a year, -137,433 CNY on the ticket.

| stress | cagr | sharpe | maxdd | worst year | OOS 2024+ | final on 1m |
|---|---:|---:|---:|---:|---:|---:|
| base | 8.95% | 0.912 | -12.54% | -1.17% | 14.55% | 1,825,345 |
| bond_flat | 7.72% | 0.802 | -12.54% | -1.85% | 12.52% | 1,687,912 |
| bond_bear_300bp | 5.53% | 0.594 | -12.54% | -4.28% | 10.27% | 1,464,619 |
| bond_bear_600bp | 3.38% | 0.387 | -14.94% | -6.64% | 8.07% | 1,270,847 |

The base arm is the published book, not a rebuild: `results/etf_equity_alpha.json` `all_classes` prints 8.95% / 0.913 / -12.54% and this face prints 8.95% / 0.912 / -12.54% (same within cagr 1e-4 / sharpe 2e-3 / maxdd 2e-3).

Realised bond bears are shallow, and the sample does contain them: over 2013..2026 (from the first bar with an eligible bond/money name, 2013-10-10) the class equal-weight's worst rolling year was **-1.00%** (2025-11-11), 14.7% of rolling years were negative, and the down calendar years were 2013, 2017, 2026 -- 3 of 14 years.
Inside the book's own window the worst rolling year was **-1.00%** (window starting 2025-11-11), so the -300/-600 bp arms are shocks the market has not delivered in this panel -- they are a bound, not a forecast.

So the sleeve is not the engine of the headline -- it is the thing that keeps the book compounding on the 912 bars where nothing else does. Zeroing it costs 1.23pp a year and 0.11 of Sharpe, not the book.

Two readings, printed side by side and not averaged: this face is a **level shock** -- the crash arrives after the book already owns the bonds, so the rule cannot see it. An investor who believes the bear is coming takes the other reading and refuses the bond universe outright: `no_bond_equity_mix` (14.84%/yr, Sharpe 0.962, drawdown -16.04%) with no vol target, `nobond_vt08` (10.89%/yr, 1.076, -10.56%) with the 8% one. Those two differ by the vol target as well as by the universe, so neither is 'what refusing bonds is worth'.

Today (2026-11-27): bond+money weight **100.0%**, equity weight **0.0%** -- the book is in defence.

<!-- ETF-BOOK-BOND-STRESS:END -->
