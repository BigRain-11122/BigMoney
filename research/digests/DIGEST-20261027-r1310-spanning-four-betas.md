# The shipped book, tested against the four things an account could hold instead

Round r1310, bm-c, 2026-10-27. Face: `results/etf_book_spanning.json`
(`schema etf_book_spanning/v1`). Implementation: `scripts/etf_book_spanning.py`
(selftest 12/12). Chain leg: `etf_book_spanning` in `Tools/s6_chain_bmc.py`.

## Why this test and not another window

r1305 measured that the composite's edge is period-bound (pre-2020 it loses to equal
weight). r1306 measured that the commodity sleeve's excess over its own class is mostly
beta (16.3pp/yr of which 13.9 is the metal, +2.4 is the ranking). Both say the same thing
from different sides: a share of what the book earns may not be *the book*. The question a
funder asks before wiring money is narrower than either:

> after the four liquid exposures this account could simply hold -- gold, US tech (QDII),
> broad A-share, government bond -- does the book's daily return still have an intercept?

So the shipped book (configuration read off `results/etf_book_production/latest.json`, never
hardcoded: 12 names, 20-bar grid, 8% de-lever-only overlay, 10bp/side, close t decision ->
open t+1 fill) is regressed on the four span assets' open-to-open returns over the same
window:

    r_book(t) = a + b_gold*r_gold + b_tech*r_tech + b_300*r_300 + b_bond*r_bond + e(t)

## Result over 2020-01-03 -> 2026-10-27 (1646 paired days, the face as the chain refreshed it)

| arm | CAGR | Sharpe | max DD | vol |
| --- | --- | --- | --- | --- |
| the book (12 names, 8% overlay) | 9.62% | 0.99 | -11.8% | 10.2% |
| equal-weight gold+NQ+300+bond, same 20-bar grid, same 10bp | **10.09%** | 0.983 | **-11.4%** | 10.8% |
| gold alone (518880) | 13.31% | 0.81 | -31.5% | 18.1% |
| Nasdaq-100 QDII alone (513100) | 20.65% | 0.89 | -27.5% | 25.8% |
| CSI300 alone (510300) | 0.21% | 0.11 | -46.7% | 20.1% |
| bond alone (511010) | 2.51% | 1.21 | -5.2% | 2.2% |

Regression on the four spans: **R2 = 0.43**, loadings gold 0.15 (t=14.5), NQ 0.07 (t=8.8),
CSI300 0.25 (t=24.3), bond -0.03 (t=-0.3); **alpha +5.85%/yr, t = 1.94**.

IS (<=2023-12-31, 966 days) alpha +3.88%/yr (t=1.16); OOS (680 days) alpha +10.12%/yr
(t=1.97). Walk-forward (IS coefficients applied to OOS, nothing refitted): predicted
+10.57%/yr, realised +18.20%/yr, residual +7.63%/yr.

## How to read it

1. **The book is not a gold bet, and it is not a beta bet either -- but it is also not
   proven to be a skill bet.** The four spans explain 43% of its daily variance and it
   carries meaningful loadings to all three risk assets, yet the point estimate of the
   intercept (+5.9%/yr) is larger than the raw gap to the basket (+4.7pp) because the book's
   *average* loading is below 1, i.e. it spends part of its life de-levered.
2. **The honest sentence is a risk sentence, not a return sentence.** A four-ETF
   buy-and-hold basket with the same grid and cost lands within 0.5pp of the book's CAGR
   and within 0.4pp of its drawdown. What the book buys over that basket is *not* return --
   it is a de-lever rule that gets the same drawdown from a different mix.
3. **2 sigma is not reached, and the window matters.** t=1.91 on the full window; IS alone
   is t=1.16 (r1305's period-bound finding again, seen from the alpha side); OOS alone is
   t=1.93. Publishing only the OOS number would be picking the window that flatters.
4. **The arms must be priced for risk, or gold wins the contest.** Gold alone makes 13.3%/yr
   against the book's 9.5%/yr, which sounds decisive until its 18.1% vol and -31.5%
   drawdown are printed beside it. The bond arm has the highest Sharpe of all six (1.21) at
   2.2% vol -- a reminder that "highest Sharpe" without a return is a different product.

## Trap caught inside this face (worth keeping)

The first run priced the four span arms off the raw panel files and reported the Nasdaq
QDII leg at **-5.3%/yr**. The reason: 513100 carries a single split on 2022-01-14, which
prints as a -50% day, and the book's own panel gets a flip repair that the span frame did
not. After applying the same `repair_flips` to the span frames the same arm reads **+20.4%/yr**
and the equal-weight basket moves from 6.41% to 9.99%/yr -- i.e. the entire conclusion
("the book beats buy-and-hold by 3pp") inverted because the benchmark was corrupt, not the
book. This is r1262's data-pit at the benchmark end: a repaired strategy arm benchmarked
against an unrepaired comparison arm measures the repair, not the strategy. Both the repair
and a selftest leg on its unit semantics are now inside the face, and the flip count is
published in `caveats`.

## What is not claimed

- Not a rejection of the book: an alpha of +5.85%/yr with 7.7% idiosyncratic vol and a
  t of 1.94 is "not yet distinguishable", not "zero".
- No HAC correction (daily, non-overlapping returns; autocorrelation would widen the alpha
  interval, so a t below 2 is not rescued by it).
- Loadings are treated as constant over the window; the IS/OOS columns are the check, not a
  fix. A time-varying-beta version is the obvious next face.
- Span set is deliberately the four exposures a retail account can hold today; a wider span
  (credit, overseas equity, commodities ex-gold) would only lower the alpha, never raise it.

## Next pointers

- The book's live ticket and the 12-name card are both on the same panel date; the next
  question in this line is whether the *staggered* book (r1301, +0.92pp CAGR, -34% turnover)
  spans differently -- if its alpha is the same 5.8% with a lower residual vol, the turnover
  saving is the only real edge, which would match r1301's own verdict.
- `etf_book_spanning` now rides the S6 chain, so this table refreshes with the panel instead
  of ageing (r1257/r1290/r1291/r1293/r1295 class).