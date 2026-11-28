<!-- THREE-BOOK-WALLET:BEGIN -->

**verdict** `THE_THIRD_BOOK_IS_BEHIND_A_GATE`

window 2020-01-06..2026-11-27 (1671 bars) · evidence_cutoff 2026-11-27 · wallet 1,000,000 CNY · each book scaled to an 8% volatility budget

Three books, one wallet: the carry book has the best Sharpe of the three (1.475 vs 0.962 and 0.553) and still takes weight 0.00 in a 1,000,000 wallet, because one IC lot consumes 91029 CNY of the 8% volatility budget -- it fits only once the wallet is 5689312 CNY (w=0.20) 3413588 CNY (w=1/3). Inside the gate the best mix is ETF 65% / convertible 35% / carry 0%: 6.573% a year, Sharpe 1.070, drawdown -6.72%. Ignoring the gate the same grid would print Sharpe 1.873, so the gate costs 0.803 of Sharpe -- and that number is not a loss, it is a price nobody has paid yet.

| book | cagr at 8% vol | sharpe | vol | maxdd | worst year | capital return at 8% vol | book floor |
|---|---:|---:|---:|---:|---:|---:|---:|
| etf | 7.66% | 0.962 | 8.00% | -7.80% | 1.35% | 7.70% | no floor |
| cb | 4.19% | 0.553 | 8.00% | -14.50% | -12.37% | 4.43% | 25,850 |
| carry | 12.16% | 1.475 | 8.00% | -7.31% | 3.45% | 11.80% | 1,137,862 |

Every book above is scaled to the same 8% volatility budget before it is read, so the rows are comparable and `capital return at 8% vol` = 8% x Sharpe is an identity, not a forecast. Raw per-book units differ (ETF/convertible are fractions per day, carry is index points per lot) and are printed in the JSON.

These rows sit on the 8% scale: a book scaled down from its own volatility shows a smaller drawdown than its published raw one (the convertible book's raw maxdd is -22.59%; both numbers are in the JSON).

| pair | daily corr | monthly corr | months both down |
|---|---:|---:|---:|
| ETF / convertible | 0.090 | 0.138 | 19 of 83 |
| ETF / carry | -0.044 | -0.123 | 13 of 83 |
| convertible / carry | -0.046 | -0.015 | 22 of 83 |

The third book is the only diversifier here that pays for itself: it moves **against** both others on the daily tape (-0.044 / -0.046), and it shares a losing month with the ETF book in only 13 of 83. That is where the 1.873 Sharpe in the ignored-gate row comes from -- and it is exactly the weight a 1,000,000 wallet cannot buy.

### the gate, in money

| book | book floor | max weight in a 1,000,000 wallet | wallet for 10% | 20% | one third |
|---|---:|---:|---:|---:|---:|
| etf | no floor | 1.00 | any | any | any |
| cb | 25,850 | 1.00 | 258,502 | 129,251 | 77,551 |
| carry | 1,137,862 | 0.00 | 11,378,625 | 5,689,312 | 3,413,588 |

A book floor is the capital the whole book needs before it fits at weight 1.0; weight w needs the wallet to be `floor / w`, so the weight a diversifier wants is exactly the weight that makes it unaffordable. `any` means the book has no lot granularity (the ETF leg is bought in shares).

### inside the gate vs ignoring it

| reading | weights (ETF / cb / carry) | cagr | sharpe | vol | maxdd | wallet it needs |
|---|---|---:|---:|---:|---:|---:|
| best, gate respected | 0.65 / 0.35 / 0.00 | 6.57% | 1.070 | 6.12% | -6.72% | 73,858 |
| best, gate ignored | 0.30 / 0.20 / 0.50 | 9.39% | 1.873 | 4.86% | -4.02% | 2,275,725 |

The two rows are **not** the same bet: the ignored-gate row runs at a lower volatility and needs a much larger wallet, so its higher Sharpe is not an argument for holding more carry today -- it is the price of the wallet it needs.

The gate-respecting mix runs at 6.12% vol, not 8%: reaching 8% would take 1.31x leverage (same Sharpe, bigger drawdown). a scaled portfolio with leverage > 1 is the same bet with more money on it; the Sharpe does not change, the drawdown does

### beside the faces this one reads

| book | sharpe here | published | diff |
|---|---:|---:|---:|
| etf | 0.962 | 0.950 | +0.0129 |
| cb | 0.553 | 0.491 | +0.0628 |
| carry | 1.475 | 1.416 | +0.0588 |

etf and cb reproduce book_pair_blend.in_window bit for bit (0.957817 vs 0.9578173792, 0.540241 vs 0.5402413276); three_book_rulers prints the same books on its own annualisation clock, so its etf/cb rows differ from this face without either being wrong. carry is compared to the family's own hedged-excess arm, never to its basis-only row (3.189), which is a notional figure no wallet can hold.

that face mixes the parents at their own published volatility (convertible ~10 pct, ETF 8 pct); this one scales every book to 8 pct first, so the weights mean shares of the risk budget

### what this face refuses to hide

- carry's series is the hedged **excess** (futures minus index, roll days zeroed, gross of the hedge leg's cost). A real hedge needs a second account; that capital and cost are the parent face's caliber and are not re-estimated here.
- the three books do not trade at the same price or the same time (ETF next open, convertible next close, carry close-to-close). Each keeps its own published lag.
- the window is the overlap only (carry starts 2017, the ETF book 2020). No parent's full-history number is blended into the overlap.

