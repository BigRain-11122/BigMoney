# Does the order sheet price the execution it declares?

Generated 2026-11-19T17:42:10+0800 from `scripts/etf_book_causal_headline.py` (panel 2005-02-23 -> 2026-11-19, 1526 symbols, cutoff `2026-11-19`).

## Verdict

**TABLE_PRINTS_BOTH_ARMS** -- the card's own table labels both arms (declared row 8.40%/yr, as-coded row 9.40%/yr); each labelled cell is this face's own measurement of the arm it names (+0.01pp and +0.01pp), so the eye cannot land on a number the sheet does not also label

Recommendation: No further change is called for on this face: the card's table prints both arms with their basis in the row label (declared 8.40%/yr, as-coded 9.40%/yr) and both cells are this face's own measurements, so the operator can size off the tradeable row without reading prose.

## The three numbers, each with its own convention

| arm | convention | CAGR | Sharpe | max drawdown |
|---|---|---|---|---|
| as coded | lag 0: score(bar d) selects, the book earns open[d] -> open[d+1] | 9.39% | 0.97 | -11.8% |
| declared by the card | lag +1: score(bar d-1) selects, the book earns open[d] -> open[d+1] -- the same lattice point as 'decide at close d, fill at open d+1', which is what the card's config.execution string claims | 8.39% | 0.87 | -16.6% |
| the live paper | etf_book_forward: decide at close d, fill open d+1, mark to close, repo ladder credited | 8.88% | 0.93 | -13.3% |

## What the operator's files say

- the card prints **9.40%/yr** (row label '2020-01 onwards -- as coded', results\etf_book_production\CARD.md)
- the card claims execution **decide at close t -> fill at open t+1 -> hold to next rebalance** (results\etf_book_production\latest.json)
- the card discloses beside it **8.39%/yr declared vs 9.39%/yr as-coded, verdict SAME_OPEN_ARM** (results\etf_book_production\latest.json)

- the card's own row labels state the basis: as_coded = 9.40%/yr; declared = 8.40%/yr

## Why this is a defect and not a preference

The two arms differ in exactly one number -- how many bars of information the signal has when the book is paid for. `as coded` ranks on bar d's own close and then buys at bar d's open, i.e. at a price set before the information it ranks on; `declared` is the same rule holding the signal one bar back, which is what the card's own execution string promises. A sheet may print either, but it cannot print one and declare the other: the operator sizes a position on the difference.

Full ladder and the mechanism pin: `results/etf_book_lookahead_audit.json`. This face adds only the comparison against the published claim, and it refuses to move its own tolerance.

