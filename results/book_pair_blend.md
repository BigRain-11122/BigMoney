# Two books, one wallet -- 2026-11-26

*generated 2026-11-27T13:13:24+08:00 · window 2020-01-03 -> 2026-11-26 (1671 bars, the overlap of both books)*

**DIVERSIFICATION_PAYS** -- Splitting the wallet beats either book on its own: 30% convertible / 70% ETF gives Sharpe 1.066 (vs 0.540 and 0.958), worst year -6.0%, max drawdown -9.3%; the two books move together on the daily tape (corr 0.0899) and go down in 23% of months together -- read the gain as +0.11 Sharpe, not as insurance

## What each book does on its own

| book | arm | CAGR | Sharpe | max DD | vol | worst year | years |
|---|---|---|---|---|---|---|---|
| dual-low convertible | n_hold=20 rebal=20 cost=10bp phase=0 | 6.29% | 0.540 | -22.6% | 12.93% | -20.8% | 6.897 |
| bond-free ETF | nobond_vt08 vol_target=8% n_hold=5 rebal=20 cost=10bp entry_lag=1 | 9.86% | 0.958 | -10.1% | 10.47% | 0.9% | 6.897 |

Full-history, outside this window (printed so the overlap is not misread as the book): cb 7.35% / SR 0.758 over 2007-07-12..2026-11-26.

Reconciliation: the edge weights land on the parents read here (w=0 -> 9.87% vs etf 9.86%, match); (w=1 -> 6.30% vs cb 6.29%, match).

Parent reproduction (this face's rerun vs the parent's own published number, pp): cb CAGR 0.0 Sharpe 0.0 DD 0.0; etf CAGR 0.0 Sharpe 0.0.

## Does splitting pay?

| convertible share | ETF share | CAGR | Sharpe | max DD | vol | worst year | turnover/yr |
|---|---|---|---|---|---|---|---|
|    0% |   100% | 9.87% | 0.969 | -10.1% | 10.47% | 0.9% | 1.08 |
|   10% |    90% | 9.63% | 1.020 | -9.4% | 9.62% | -1.5% | 1.43 |
|   20% |    80% | 9.37% | 1.056 | -8.8% | 8.98% | -3.8% | 1.78 |
|   30% ** |    70% | 9.07% | 1.066 | -9.3% | 8.59% | -6.0% | 2.13 |
|   40% |    60% | 8.76% | 1.041 | -11.2% | 8.49% | -8.3% | 2.49 |
|   50% |    50% | 8.41% | 0.981 | -13.1% | 8.68% | -10.4% | 2.84 |
|   60% |    40% | 8.04% | 0.895 | -15.0% | 9.14% | -12.6% | 3.19 |
|   70% |    30% | 7.64% | 0.798 | -16.8% | 9.85% | -14.7% | 3.54 |
|   80% |    20% | 7.22% | 0.702 | -18.7% | 10.74% | -16.7% | 3.89 |
|   90% |    10% | 6.77% | 0.612 | -20.5% | 11.78% | -18.8% | 4.25 |
|  100% |     0% | 6.30% | 0.532 | -22.6% | 12.93% | -20.8% | 4.60 |

Correlation: daily 0.0899, monthly 0.1435; both books fall in 19 of 82 months (23%).

## What it takes to hold this split

- a 30% convertible sleeve needs the wallet to be at least 86,167 CNY before the twenty-name book fits in it at all (the cb book's own one-lot floor is 25,850 CNY for twenty names).
- Today's ETF picks (2026-11-26): 159207, 159549, 515300, 562060, 513690.

## How to read it

- The window is the overlap only (1671 bars). A blend cannot be priced on days one of the books does not exist, so this is a recent-years claim, not a 19-year one.
- Execution differs: signal at close t, filled at close t+1 vs decide at close t, own from the open of t+1.
- each parent already pays its own 10bp per side; the blend adds no rebalancing cost between books (not modelled -- a reader who moves money between them pays it).
- the etf book keeps a convertible sleeve, so a few convertible ETFs sit in both wallets -- the correlation is not independent by construction and is not claimed to be.

## Unverified

- no rebalancing cost between the two wallets is modelled
- the overlap window is 6.9 of cb's 19.4 years -- a blend is a recent-years claim
- the best weight is chosen on the same window it is scored on (in-sample pick): a reader who adopts it should expect less than the printed gain
- each parent's own unverified list still applies (survivorship in the etf pool, the cb book's close-fill assumption, its 2026 drawdown being one regime)

