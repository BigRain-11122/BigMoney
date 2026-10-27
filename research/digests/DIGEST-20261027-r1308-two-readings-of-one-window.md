# One window, two readings: the 2015-2019 premium, and the ladder that reconciles it

r1308 bm-c, 2026-10-27. Artifacts: `results/etf_book_passive_mix.json` (schema
`etf_book_passive_mix/v2`), `results/etf_book_window_decomp.json` (schema
`etf_book_window_decomp/v1`). Code: `scripts/etf_book_passive_mix.py` (selftest 13/13),
`scripts/etf_book_window_decomp.py` (selftest 8/8). Card face:
`results/etf_book_production/CARD.md` sections *What the rotation is worth* and *The
2015-2019 reconciliation*. Method card: E144 (E142 was taken by bm-b r1176 in the same rebase).

## The question r1307 handed over

The card had just published "what the rotation is worth": on the 2020+ window the book
returns 9.49%/yr against 3.13%/yr for a static mix of its own class exposure (+6.36pp).
The obvious next question was whether that premium is a property of the ranking or of the
period -- r1305 had already shown the same engine losing to equal weight over 2015-2019.

## Answer 1: the premium is positive in both periods, roughly halved outside the published one

Three cells, each moving one axis, all on the production engine, the same grid, the same
10bp/side cost rule and the same 8% de-lever-only overlay on both arms:

| cell | window | universe | book | static mix | premium |
|---|---|---|---|---|---|
| full | 2020-01..2026-10-26 | 1,499 names | 9.49% | 3.13% | **+6.36pp** |
| pre2020 | 2015-01-01..2019-12-31 | 193 names (first bar <= 2020-01-01) | 5.12% | 2.95% | **+2.17pp** |
| post2020_pre_universe | 2020-01-01..2026-10-26 | the same 193 names | 9.12% | 4.73% | **+4.39pp** |

Delivered vol is comparable across the two arms in every cell (full 10.2% vs 9.3%, pre2020
7.8% vs 9.0%), so the premium is not a leverage difference. The pair `pre2020` vs
`post2020_pre_universe` holds the universe fixed, so the 2.2pp -> 4.4pp step is the period
and nothing else. Control: the full-window book arm re-prices the published 9.49% at
0.00pp against `etf_book_production/latest.json`.

## Answer 2: but that contradicts the -8.86pp caveat, so the gap gets priced

The card simultaneously carries the r1305 caveat (2015-2019: book -4.97%/yr, equal weight
+3.89%/yr, -8.86pp, negative in 6/6 grid cells). Same window, opposite sign. The ladder:

| rung | cell | CAGR | vs EW | step |
|---|---|---|---|---|
| r1_published_cell | all classes, N5, no overlay | -4.97% | -8.86pp | (control, 0.0pp vs r1305) |
| r2_bond_free_pool | production pool, N5, no overlay | +0.85% | -1.51pp | **+5.82pp** |
| r3_wider_book | production pool, N12, no overlay | +0.73% | -1.63pp | -0.12pp |
| r4_vol_overlay | production pool, N12, 8% overlay | +5.12% | +2.76pp | **+4.39pp** |

Both ends reproduce their published arms at 0.0pp (tolerance 0.5pp), which is what makes
the three deltas quotable. So the -4.97% belongs to the bond-inclusive, 5-name, unsized
cell: dropping the bond/money sleeve is worth +5.82pp on a window when bonds rallied and
the overlay is worth +4.39pp because 2015 and 2018 are exactly the drawdowns it exists for.

## What this changes on the card

1. The rotation section now prints the pre-2020 control next to the published window, with
   the universe size and both arms' CAGR -- not a bare premium.
2. A new section, *The 2015-2019 reconciliation*, carries the ladder and says in words that
   the caveat's cell and this book's cell are different experiments, and that the failure
   is the cell's, not the ranking's.
3. The hand-written caveat now names the three axes that separate the cells, and points at
   the reconciliation instead of standing alone.

## What it does NOT say (and must not be read as saying)

- It does **not** say the ranking works without the sizing rule. On this window the raw
  book (r3) still loses to equal weight (-1.63pp) and loses even more clearly to the
  unsized static mix on risk terms: 0.73%/yr at 19.9% vol and Sharpe 0.14 with a -46.2%
  drawdown, against 4.14%/yr at 18.3% vol, Sharpe 0.32, -32.0% drawdown. The pre-2020
  premium exists only once the same overlay is applied to both arms.
- It does **not** promote the pre-2020 premium to evidence: 193 names is a thin
  cross-section, the pre-2020 universe is survival-filtered (no delisted funds in the
  panel), and 4 trading years is one regime.
- The two benchmarks are not interchangeable: rung 4 reads +2.76pp vs equal weight and
  +2.17pp vs the static class mix. Both travel; neither is translated into the other.

## Standing pointers

- The staggered 5+5 book is still the only live face outside the S6 chain (r1293/r1294);
  unchanged this round.
- `etf_paper_signal` and the live ledger stop at 2026-10-26 with the panel; nothing new
  turned this round, next sleeve turn is 2026-11-06 (sleeve 0) / 2026-11-13 (sleeve 1).