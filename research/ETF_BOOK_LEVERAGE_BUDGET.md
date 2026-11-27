# 这本书能不能靠借钱补上自己的目标？

<!-- ETF-BOOK-LEVERAGE-BUDGET:BEGIN -->
**verdict** `THE_BOOK_ALREADY_RUNS_ABOVE_ITS_TARGET`

the published book delivers 10.47% vol against an 8% target (2.47 pp over) with the sizing rule capped at 1.00x -- there is no gap for leverage to close, only an overshoot for it to deepen.

r2198 printed 'reaching 8% would take 1.31x leverage'. Two things are worth separating: the 1.31x belongs to the MIXED wallet (its 6.12% vol), not to this book, which runs at 10.47% vol on its own; and the production sizing rule is cap=1.0, so it can only lever down. This face prices both: what the rule could do at a higher cap, and what the mixed wallet's 1.31x costs to fund.

generated 2026-11-28T02:31:17+08:00 | cutoff 2026-11-27 | borrow rate 6%/yr | target 8%

| cap | gross cagr | gross Sharpe | net cagr | net Sharpe | net vol | net maxDD | financing pp | leverage days | max scale |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.00x | 9.99% | 0.962 | 9.99% | 0.962 | 10.47% | -10.11% | 0.00 | 0.0% | 1.00 |
| 1.25x | 10.24% | 0.966 | 10.10% | 0.955 | 10.68% | -10.11% | 0.14 | 15.6% | 1.25 |
| 1.50x | 10.28% | 0.961 | 10.10% | 0.946 | 10.79% | -10.11% | 0.18 | 15.6% | 1.50 |
| 2.00x | 10.28% | 0.961 | 10.10% | 0.946 | 10.79% | -10.11% | 0.18 | 15.6% | 1.50 |

`cap 1.00x` is the published book (the sizing rule may only de-lever). Its reconciliation against `book_pair_blend.load_etf()` is 0.0 -- zero means this face rebuilds the parent exactly and only adds the leverage question.

### where the 1.31x actually lives

r2198's `1.31x` is the **mixed wallet** (ETF 65% / convertible 35% / carry 0%), not this book. That face already prints what the mix earns rescaled to 8% vol, gross of borrowing: **8.59%** a year for 1.3065x leverage. Charge the leverage a 6% funding rate and it becomes:

| reading | cagr | vol | Sharpe |
|---|---:|---:|---:|
| the mix as published | 6.51% | 6.12% | 1.060 |
| same mix at 1.3065x, gross (parent's own number) | 8.59% | 8.00% | 1.073 |
| same mix at 1.3065x, net of 1.84 pp financing | 6.75% | 8.00% | 0.843 |

the middle row is not quite the parent's arithmetic: it prints 8.5856% for the 8% rescale while 6.5078% x 1.3065x = 8.5024%, and Sharpe therefore reads 1.073 rather than 1.060. The gap (0.08 pp) is the parent's, printed here so a reader who multiplies the two numbers is not left thinking they made a mistake; the net row uses the parent's printed number, because that is the one the reader was handed.

**LEVERAGE_TO_THE_TARGET_COSTS_MORE_SHARPE_THAN_IT_BUYS_VOL** -- buying the last 1.88 pp of volatility pays 0.24 pp of CAGR and costs 0.217 of Sharpe. The borrowed rupee is dearer than the risk it buys.

annualised rates are added linearly: a 1.3065x book pays 0.3065 of a 6% rate on its borrowed share; a real margin account has haircuts and roll rules this does not model

### what the numbers say

- the published book runs at 10.47% vol against an 8% target, i.e. 2.47 pp OVER it, not under. An overshoot with a rule that can only de-lever means the 60-bar estimate ran low exactly when vol was rising: the cap cannot correct a book that is already too risky
- raising the cap does almost nothing: the best levered arm (cap_1.25) adds 0.22 pp of vol, 0.25 pp/yr of gross CAGR, 0.11 pp of net CAGR, and its Sharpe is 0.955 vs the published 0.962. Drawdown does not move at all (-10.11% in every arm) -- this face does not locate which days set that figure, so it states the fact and leaves the explanation open rather than inventing one
- levered decisions are rare by construction: the cap only binds in calm windows, and even at 2.00x the book is levered on 15.6% of days, never above 1.50x -- which is why the 1.50x and 2.00x rows are identical. A cap nobody reaches is not a setting, it is a ceiling that never binds

### what this face refuses to hide

- the financing line is an assumption (6%/yr), not a measurement; a cheaper funding rate would flatter every levered arm equally, a dearer one would sink them
- leverage does not make the book better informed: same signal, same panel, same costs. It buys more of the same return and more of the same drawdown.
- the panel holds ETFs that exist today; the early years are optimistic in exactly the way the parent is, and leverage does not repair that.
<!-- ETF-BOOK-LEVERAGE-BUDGET:END -->
