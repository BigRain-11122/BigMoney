# ETF book -- quote-flip contamination in its published numbers

Evidence cutoff 2026-10-30 · production rule untouched · repair = `etf_equity_alpha.repair_flips` (imported, not re-written)

## The answer

168 flip prints on the panel move the book's own numbers by +1.17pp of annual return, +1.13pp of drawdown and +0.286 of Sharpe (full history) -- and the worst day it publishes, -4.70% on 2025-07-07, is one of them: on repaired prices the worst day is -2.88%

Verdict: **MATERIAL** (band: 0.50pp CAGR / 0.50pp drawdown / 0.10 Sharpe).

## The panel

1613 symbols x 5270 bars; **168** flip prints flattened (158 of 1613 symbols carry at least one, on 125 distinct days).

| window | bars | | CAGR | Sharpe | max drawdown | worst day |
| --- | --- | --- | --- | --- | --- | --- |
| full_history | 1525 | raw | 6.54% | 1.056 | -6.91% | -4.70% (2025-07-07) |
| full_history | 1525 | clean | 7.71% | 1.342 | -5.78% | -2.88% (2025-04-23) |
| full_history | 1525 | **delta** | **+1.17pp** | **+0.286** | **+1.13pp** | |
| since_inception | 555 | raw | 17.32% | 1.042 | -13.06% | -9.66% (2025-07-07) |
| since_inception | 555 | clean | 22.85% | 1.401 | -13.06% | -6.07% (2025-04-23) |
| since_inception | 555 | **delta** | **+5.53pp** | **+0.359** | **+0.00pp** | |

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
