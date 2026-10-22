# E86 — every removal, not just the argmin: churn cells are 7-swap objects, with one 1-swap exception (r1154 bm-b)

Evidence cutoff 2026-10-21. Face: `results/e44_midmonth/LOODIST-20261021.json`.
Runner: `python scripts/e39_panel_census.py loodist` (4 universes × 2 books, full churn rows, CPU-only, ~55 s).
Selftest: `python scripts/e39_panel_census.py selftest` — 212/212 PASS (10 new legs on the LOO and breakdown helpers).

## Question

E83 flagged a cell as "single print" when removing its single most influential
transition left under half the magnitude. That flag cannot distinguish a cell that
dies on 1 of 27 removals from a cell that dies on 20 of 27 — both read `single_print`.
E86 takes the whole leave-one-out distribution and the breakdown count:

- **LOO spread** — all n re-reads `(n·m − a_i)/(n−1)`, reported as min/p10/median/p90/max;
- **kills-pct** — the share of the n removals that drop |mean| below half;
- **breakdown k** — greedy removal (always the transition farthest from the current
  mean, the E83 rule iterated) until |mean| ≤ 50% of the original, with the path.

## Answer 1 — one removal is enough in 5 of 16 cells, but it is never the typical removal

| reading | count |
|---|---|
| level cells with a LOO (n ≥ 2) | 16 / 16 |
| cells where ≥1 removal halves the magnitude | 5 / 16 |
| cells where that removal is < 10% of all removals | 15 / 16 |
| cells where a majority of removals halve the magnitude | **0 / 16** |
| median breakdown k (removals needed to halve) | **7** |
| median breakdown k as share of the cell | **25.9%** |

So the E83 flags are not flukes, but they are also not the cell's story: in 15 of the
16 cells there is exactly one (occasionally two) killing removal out of 25–29. The
typical transition does not move the cell at all — E85's median delta of exactly 0.0
and this leg's 0/16 majority-kill statement are the same fact read two ways.

## Answer 2 — the mid-month newest-era cell is the one genuine 1-swap object

`mid15 / 2024_now` is the only cell in the whole matrix whose breakdown k is 1:

| universe | n | mean bp | LOO min | LOO median | kills % | breakdown k |
|---|---|---|---|---|---|---|
| unscreened | 27 | −123.7 | −148.8 | −129.1 | 3.7 | **1** |
| neutralise_int | 27 | −364.7 | −399.1 | −379.4 | 3.7 | **1** |
| neutralise | 27 | −364.7 | −399.1 | −379.4 | 3.7 | **1** |
| drop | 27 | +28.0 | +8.1 | +28.6 | 11.1 | 3 |

Every other cell needs 3 to 10 removals (17–37% of its transitions). Month-end
newest era needs 7 (25.9%); mid15 2021_2023 needs 5 (17.2%); month-end 2021_2023
needs 10 (37.0%). Read together with E85 that means the newest-era mid-month
deficit is a three-transition statement with a one-transition cliff inside it,
while its 2021_2023 counterpart is a broad property of the era.

## Answer 3 — the gap faces survive nearly every perturbation

Two gap cells (mid15 minus me, unscreened):

| era | gap bp | LOO draws | LOO min | LOO median | LOO max | kills half | flips sign |
|---|---|---|---|---|---|---|---|
| 2021_2023 | +318.8 | 56 | **−60.7** | +342.1 | +575.6 | 5 / 56 | 1 |
| 2024_now | −211.0 | 54 | −259.5 | −213.3 | −86.3 | 1 / 54 | 0 |

The newest-era gap is the more robust of the two: 53 of 54 removals keep it negative
and the worst single removal still leaves −86.3bp. The 2021_2023 gap keeps its sign
under 55 of 56 removals but one removal (the E83 transition) drags it to −60.7 — the
published +318.8 is therefore a magnitude statement, not a sign statement, for that era.

## Honest limits

- LOO is unweighted single removal only; the breakdown k path is greedy, not the
  minimal-cardinality set (a proper minimum would need a subset search over 27 items).
- The greedy path is printed (`path_bp`) so a stepwise collapse can be told from a cliff.
- n = 25–29 per cell; a cell of n=2 has a 0-by-construction breakdown and is excluded
  from the median k by the `k is None` guard rather than by hand.
- `neutralise_int` and `neutralise` remain bit-identical here (E84), so 16 cells are
  effectively 12 independent universes × books.
- Descriptive only: no prereg, no judgement, zero ledger booking, no predictor.

## Next

E87 (the same robust/LOO read at the 2013 start) and E88 (bit-for-bit reproduction of
the published E80/E82 means from this face) sit on the same burn and remain unclaimed.