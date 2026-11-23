# Which index do you short?

<!-- BEGIN:ASTOCK-VETO-HEDGE-INSTRUMENT -->

Nine faces short **512100, the CSI 1000 ETF**, against a book that is built from **CSI 300 and CSI 500** names.  None of them argues the choice of index; they argue only the size.  This face prices the choice.

**Answer, one line: HEDGE_INSTRUMENT_MATTERS | NO_RIVAL_REACHES_THIS_RISK | SECOND_LEG_DOES_NOT_PAY | BOOK_LEANS_SMALL.**  The best index by variance removed is 512100 (84.94%) against 510300 (39.32%) -- a 45.62% spread, line 5.0%; at 512100's own risk level (10.61% vol) the nearest rival 510500 bottoms out at 16.17% vol, so no rival can be held at that risk at any size -- the k=1 return gap of 3.95 pp is return the rivals never removed the risk for

## 1. The three candidates and what one lot of each is worth

| ETF | index | last price | one lot (CNY) | lots per CNY 1m at its own beta | repaired prints |
|---|---|---|---|---|---|
| 510300 | CSI 300 | 4.018 | 402 | 2402.34 | 0 |
| 510500 | CSI 500 | 6.053 | 605 | 1610.94 | 1 |
| 512100 | CSI 1000 | 2.300 | 230 | 4220.23 | 1 |

Every one of them prices every period: 510300 misses 0, 510500 misses 0, 512100 misses 0.

## 2. One unit of beta, three indexes, one book

| hedge | beta | R^2 | beta (in-sample only) | book vol | residual vol | share removed |
|---|---|---|---|---|---|---|
| none | - | - | - | 27.34% | 27.34% | 0.00% |
| 510300 CSI 300 | 0.9653 | 0.3932 | 0.7698 | 27.34% | 21.30% | 39.32% |
| 510500 CSI 500 | 0.9751 | 0.6502 | 0.9300 | 27.34% | 16.17% | 65.02% |
| 512100 CSI 1000 | 0.9707 | 0.8494 | 0.9013 | 27.34% | 10.61% | 84.94% |

Fitted on all 77 paired periods; the in-sample column is the same fit on dates <= 2023-12-31, printed because r2030 showed the beta moves when it is refitted.

## 3. What the hedged book actually earns (k = 1, full window)

| arm | periods | annualised | vol | per unit of vol | max drawdown | worst period | down periods |
|---|---|---|---|---|---|---|---|
| book, no hedge | 77 | 10.30% | 27.34% | 0.38 | -25.92% | -17.18% | 45 |
| short 510300 | 77 | 10.49% | 21.30% | 0.49 | -25.24% | -19.47% | 47 |
| short 510500 | 77 | 8.53% | 16.17% | 0.53 | -23.94% | -15.98% | 49 |
| short 512100 | 77 | 6.54% | 10.61% | 0.62 | -14.08% | -8.63% | 44 |

Same k, same costs, same periods -- the only thing that changes between those three rows is which index is shorted.  **That table cannot be read as a trade-off**: an index that removes 39% of the variance keeps return it never removed the risk for.  Section 5 is the control that makes the comparison apples to apples.

## 4. The ticket: rounding to whole lots costs beta, and it costs it unevenly

| ETF | lots needed for CNY 1m | filled | realised beta | beta error |
|---|---|---|---|---|
| 510300 | 2402.34 | 2402 | 0.9651 | -0.00014 |
| 510500 | 1610.94 | 1611 | 0.9751 | +0.00004 |
| 512100 | 4220.23 | 4220 | 0.9706 | -0.00005 |

CNY 1m needs **4220** lots of 512100 against **1611** of 510500: the index that removes the most risk also needs the most tickets.  The rounding those tickets force is smaller than the beta's own uncertainty in all three cases (|error| <= 0.00014 against the 0.2126 band r2029 printed), so granularity is not a reason to prefer a weaker hedge -- it is a reason to check the order before sending it.

## 5. The equal-risk control: can the cheap index even hold this book?

Every rival is scanned over **k in 0..4** (step 0.005) for the lowest volatility it can leave the book at.  The target is the size the family already uses: short 512100 at k = 1, which holds the book at **10.61%** annual volatility.

| hedge | beta | best k | lowest vol it can reach | annualised at that point | max drawdown there | reaches 512100? |
|---|---|---|---|---|---|---|
| 510300 | 0.9653 | 1.000 | 21.30% | 10.49% | -25.24% | **no** |
| 510500 | 0.9751 | 1.000 | 16.17% | 8.53% | -23.94% | **no** |
| 512100 | 0.9707 | 1.000 | 10.61% | 6.54% | -14.08% | reference |

**No rival gets there.**  The nearest one, 510500, bottoms out at **16.17%** annual volatility -- 5.56% above the level the family already holds -- and it cannot be pushed lower at any size, because what is left is the part of the book that index does not explain.  There is therefore no risk/return trade-off to price here: the 3.95 pp the rivals keep at k = 1 is return they never removed the risk for.  Choosing a large-cap index is not a cheaper hedge, it is a weaker hedge wearing the same position size.

## 6. Does a second short pay for itself?

| fit | large-cap loading | small-cap loading | R^2 | residual vol | lean |
|---|---|---|---|---|---|
| CSI300+CSI500 | -0.2110 | 1.1127 | 0.6560 | 16.04% | BOOK_LEANS_SMALL |
| CSI300+CSI1000 | -0.3003 | 1.1283 | 0.8650 | 10.05% | BOOK_LEANS_SMALL |

A **negative** loading on the large-cap leg (-0.3003 in the 300+1000 fit) is the mechanical reason the large-cap indexes fail above: this book is not just 'more beta than the CSI 300', it is long small against large.  Shorting a large-cap index therefore adds exposure on the very spread the book earns from instead of removing it, which is why the 510300 fit stops at R^2 0.3932 at every size.

The best single index leaves **10.61%** of annual volatility; the best two-leg fit leaves **10.05%** -- a further **0.57%** removed, against the frozen line of 2.00%.  It does not earn its extra roll cost, so one index is enough.

## 7. Verdicts (frozen lines, printed with the numbers)

| token | reading |
|---|---|
| HEDGE_INSTRUMENT_MATTERS | share removed spans 45.62% (line 5.0%) |
| NO_RIVAL_REACHES_THIS_RISK | nearest rival bottoms out at 16.17% vol against the target 10.61% (tol 1.00%); k=1 raw gap 3.95 pp is confounded and is not used |
| SECOND_LEG_DOES_NOT_PAY | second leg removes 0.57% of annual vol (line 2.00%) |
| BOOK_LEANS_SMALL | two-leg fit loads -0.3003 on the large-cap index and 1.1283 on the small-cap one |

## 8. The anchor: this really is the parents' book

| quantity | r2022 published | recomputed here | abs diff |
|---|---|---|---|
| beta used for the arms (in-sample fit) | 0.9013 | 0.9013 | 0.00e+00 |
| beta on the full window | 0.9707 | 0.9707 | 0.00e+00 |
| share of variance removed | 0.849391 | 0.849391 | 0.00e+00 |

Anchor agrees: the 512100 column is not a new model of the same book, it is the same model re-run, so any divergence in the other two columns is about the index and not about a different pipeline.

## 9. What this face does not say

- It does not model borrow cost, margin, recall or basis: r2022 quotes the borrow axis (0/2/5 percent a year) and r2027 quotes the futures basis.  The base habit here is the parents' 8 bp + 16 bp roll.
- It does not re-choose k or a drawdown budget: r2023/r2025/r2026 own those.
- It does not walk the beta forward: r2030 does that, and this face keeps its full-window beta so the three indexes are compared on one identical footing.
- ETF prices are as-traded (no dividend adjustment); the book is priced at its last mark (2026-10-14) while the hedge panels run to 2026-11-20, and that dating gap belongs to r2028 -- it is not repaired here.
- A single-history answer: the spread between indexes is a reading of 2020-07..2026-10-14, not a law about which index hedges a future book.

## 10. Reproduction

```
python scripts/astock_veto_hedge_instrument.py selftest
python scripts/astock_veto_hedge_instrument.py run
python scripts/astock_veto_hedge_instrument.py check
```

<!-- END:ASTOCK-VETO-HEDGE-INSTRUMENT -->
