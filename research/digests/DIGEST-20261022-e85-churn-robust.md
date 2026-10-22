# E85 — every churn cell gets a median and a 10% trimmed mean beside its mean (r1153 bm-b)

Evidence cutoff 2026-10-21. Face: `results/e44_midmonth/CHURNROBUST-20261021.json`.
Runner: `python scripts/e39_panel_census.py robustchurn` (4 universes × 2 books × full churn rows, CPU-only, ~50 s).
Selftest: `python scripts/e39_panel_census.py selftest` → 202/202 PASS (7 new legs on the estimators).

## Question

E83 measured how much of each published churn cell survives removing ONE transition.
That is a magnitude statement about the mean. This leg asks the complementary question
on the same burn: **does the cell's centre of mass survive?** Each cell now carries
`mean`, `median`, `trimmed_mean_10pct`, the two keep-percentages, and the share of the
cell's signed total carried by its three largest transitions.

## Answer 1 — the level cells are tail statistics, but not single-outlier statistics

16 level cells (2 books × 4 universes × 2 eras with data):

| reading | count |
|---|---|
| median keeps < 50% of the mean | 13 / 16 |
| trimmed mean keeps < 50% | 3 / 16 |
| median flips the mean's sign | 4 / 16 |
| top-3 transitions carry > 50% of the signed total | 5 / 16 |

The median collapses while the trimmed mean usually does not: the churn alpha is a
**right-skewed** cell (most transitions small, several moderately large), not a
one-outlier cell. Trimming 10% per tail therefore does not rescue it, and a "typical
transition" read understates the cell by 3–7×.

## Answer 2 — the two eras differ in SHAPE, not only in size

Newest era, mid-month book (bp per swap):

| universe | mean | median | trim10 | median keeps | top-3 share |
|---|---|---|---|---|---|
| unscreened | −123.7 | **+18.1** | +2.7 | −14.6% (sign flip) | 151.6% |
| neutralise_int | −364.7 | **+18.1** | +7.4 | −5.0% (sign flip) | 118.6% |
| neutralise | −364.7 | **+18.1** | +7.4 | −5.0% (sign flip) | 118.6% |
| drop | +28.0 | +12.2 | +32.5 | 43.6% | 58.0% |

2021_2023, same book:

| universe | mean | median | trim10 | median keeps | top-3 share |
|---|---|---|---|---|---|
| unscreened | +2185.4 | +284.6 | +2001.9 | 13.0% | 40.0% |
| drop | +2327.3 | +346.6 | +2155.3 | 14.9% | 38.7% |

So the newest era's mid-month churn deficit is a **three-transition** statement whose
typical swap is mildly positive (+18.1bp), while 2021_2023's correction is diffuse —
trimmed mean ≈ mean and the top-3 carry only 15–40%. E80's "second mechanism" in
2021_2023 is therefore a broad property of that era's universe, not a few prints;
the newest-era deficit is the opposite.

Month-end churn stays positive on both estimators in every era (2024_now: mean +87.3 /
median +63.8 / trim +107.0; under neutralise +92.4 / +63.8 / +113.0), so the
month-end book is not tail-dependent.

## Answer 3 — the repair screen does not move the median transition at all

12 per-transition delta cells (mode minus baseline); 4 of them have a mean of exactly
0.0 (the screen swaps no name in that book/era, so no keep-percentage exists).
Of the 8 with a defined keep:

- **all 8** keep less than half of their mean under the median;
- the median delta is **exactly 0.0** in 7 of them (±0.2bp in the eighth);
- top-3 share of the signed total is 78.7%–321.7%, i.e. ≥100% in five cells.

Read: the E80/E82 churn-gap "amplification" lives entirely on 1–3 transitions per era;
the typical transition is untouched by the split screen. This is consistent with
E83 (one transition owns the 2021_2023 gap) and extends it — E83 removed the single
biggest one, this leg shows the *whole distribution* sits at zero.

## Honest limits

- n = 25–29 transitions per era; medians on ~27 points are coarse (±1 transition moves them).
- `neutralise_int` and `neutralise` are bit-identical on these cells (E84's duplicate-screen
  finding, reproduced here), so the 4 universes are effectively 3.
- Start window fixed at 2020-01-01; a start-2013 reread is seeded as E87 and not claimed here.
- Descriptive only: no prereg, no judgement, zero ledger booking, no predictor claimed.

## Next

E86 (single-print distribution over all removals) and E87 (robustness at the 2013 start)
both sit on this same burn. E88 checks that the robust table reproduces the published
E80/E82 means bit-for-bit, so the two faces cannot be two different burns.