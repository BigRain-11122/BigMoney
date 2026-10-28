# ETF book -- selection premium across decision phases

Question: the card's headline is +6.59pp/yr of selection premium on one decision calendar -- does that premium survive four phases of that calendar?

**Verdict**: level: the premium is positive on 4/4 phases (median +6.59pp/yr, floor 2.00) -- the card's headline is a level, not one decision sequence

| phase | start | decisions | book CAGR | static CAGR | premium pp | book Sharpe |
|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 83 | 9.70% | 3.11% | +6.59 | 1.00 |
| 1 | 2020-01-09 | 83 | 9.60% | 3.01% | +6.59 | 0.94 |
| 2 | 2020-01-16 | 83 | 9.12% | 3.57% | +5.55 | 0.92 |
| 3 | 2020-01-23 | 82 | 10.93% | 3.77% | +7.16 | 1.14 |

Premium: positive on 4/4 phases, median +6.59 pp/yr, range +5.55..+7.16 (+1.61 pp spread).

Ruler: the book's own CAGR spans 9.12%..10.93% across these phases (1.81 pp) -- compare the premium's spread against that before quoting any single number.

Control: phase 0 is the published window, so it must reproduce the published arm

## Caveats
- the static arm rides class equal-weight indices that rebalance daily at ZERO cost, so the premium is a LOWER bound on what the ranking adds -- unchanged from the face this one re-prices
- all four phases share one panel and one vintage of the data, so this measures calendar dependence, not data dependence
- the book's own phase spread is printed next to the premium: if the premium is smaller than that spread it cannot be told apart from calendar luck
- ETF pool is survival-filtered and both arms share the pool, so the bias cancels in the premium, not in the levels
