# Does the order sheet price the execution it declares?

Generated 2026-11-01T23:40:12+0800 from `scripts/etf_book_causal_headline.py` (panel 2005-02-23 -> 2026-10-30, 1504 symbols, cutoff `2026-10-30`).

## Verdict

**EXECUTION_CLAIM_MISMATCH** -- the card prints +1.14pp against the execution it declares (9.60 vs 8.46%/yr); the printed number reproduces the same-open arm within 0.25pp

Recommendation: The order sheet should carry the declared-execution number (8.46%/yr) beside the as-coded one, or fix the engine to fill at open t+1 -- until then the headline is -1.14pp/yr above the execution the sheet itself claims; the live paper, which does fill next open and earns the repo ladder, reads 9.12%/yr.

## The three numbers, each with its own convention

| arm | convention | CAGR | Sharpe | max drawdown |
|---|---|---|---|---|
| as coded | lag 0: score(bar d) selects, the book earns open[d] -> open[d+1] | 9.60% | 0.99 | -11.8% |
| declared by the card | lag +1: score(bar d-1) selects, the book earns open[d] -> open[d+1] -- the same lattice point as 'decide at close d, fill at open d+1', which is what the card's config.execution string claims | 8.46% | 0.87 | -16.6% |
| the live paper | etf_book_forward: decide at close d, fill open d+1, mark to close, repo ladder credited | 9.12% | 0.95 | -13.3% |

## What the operator's files say

- the card prints **9.60%/yr** (results\etf_book_production\CARD.md)
- the card claims execution **decide at close t -> fill at open t+1 -> hold to next rebalance** (results\etf_book_production\latest.json)


## Why this is a defect and not a preference

The two arms differ in exactly one number -- how many bars of information the signal has when the book is paid for. `as coded` ranks on bar d's own close and then buys at bar d's open, i.e. at a price set before the information it ranks on; `declared` is the same rule holding the signal one bar back, which is what the card's own execution string promises. A sheet may print either, but it cannot print one and declare the other: the operator sizes a position on the difference.

Full ladder and the mechanism pin: `results/etf_book_lookahead_audit.json`. This face adds only the comparison against the published claim, and it refuses to move its own tolerance.

