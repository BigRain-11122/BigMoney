# ETF book -- quote-flip contamination in its published numbers

Evidence cutoff 2026-11-06 · production rule untouched · repair = `etf_equity_alpha.repair_flips` (imported, not re-written)

## The answer

169 flip prints on the panel move the book's own numbers by +1.16pp of annual return, +1.13pp of drawdown and +0.283 of Sharpe (full history) -- and the worst day it publishes, -4.70% on 2025-07-07, is one of them: on repaired prices the worst day is -2.88%

Verdict: **MATERIAL** (band: 0.50pp CAGR / 0.50pp drawdown / 0.10 Sharpe).

## The panel

1624 symbols x 5275 bars; **169** flip prints flattened (159 of 1624 symbols carry at least one, on 126 distinct days).

| window | bars | | CAGR | Sharpe | max drawdown | worst day |
| --- | --- | --- | --- | --- | --- | --- |
| full_history | 1530 | raw | 6.42% | 1.036 | -6.91% | -4.70% (2025-07-07) |
| full_history | 1530 | clean | 7.58% | 1.319 | -5.78% | -2.88% (2025-04-23) |
| full_history | 1530 | **delta** | **+1.16pp** | **+0.283** | **+1.13pp** | |
| since_inception | 560 | raw | 16.68% | 1.010 | -13.06% | -9.66% (2025-07-07) |
| since_inception | 560 | clean | 22.12% | 1.363 | -13.06% | -6.07% (2025-04-23) |
| since_inception | 560 | **delta** | **+5.44pp** | **+0.353** | **+0.00pp** | |

## The ten deepest prints on the panel

| symbol | date | print |
| --- | --- | --- |
| 510150 | 2021-05-31 | -91.6% |
| 159943 | 2021-10-22 | -91.5% |
| 510180 | 2009-05-21 | -90.2% |
| 511220 | 2023-01-16 | -90.1% |
| 510580 | 2021-07-19 | -90.1% |
| 159975 | 2021-01-29 | -90.0% |
| 511030 | 2021-01-11 | -90.0% |
| 159909 | 2021-03-11 | -89.7% |
| 510030 | 2021-06-21 | -87.7% |
| 159970 | 2025-12-22 | -83.1% |

## What this does and does not say

* Nothing was changed in the production path. This face measures the cost of leaving it unchanged; the repair decision is a separate, deliberate one because it moves every published number of the book at once.
* The clean arm is the same rule on the same dates with the flip prints read as flat days -- not a different strategy, and not a better backtest.
* A deeper drawdown under raw prices is the tell: a phantom -50% print in a held name looks exactly like a real crash to any statistic that only sees returns.
* The absolute levels in each row are **this face's own construction** (the production rule over the bars where the index exists). They are not the ticket's metrics block, which is built differently, and this face makes no claim to reproduce it -- only the raw/clean delta is being measured here. The same code, the same dates, one panel difference.
