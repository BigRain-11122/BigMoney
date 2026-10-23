# DIGEST 2026-10-24 bm-a -- cross-statement PIT accrual factor (r1112)

## What was built

`scripts/fund_pit_crossface_factor.py` (selftest 11/11, smoke leg added) -- the
first factor that needs all three statements at once, built on the r1108 as-of
primitive and consumed at the resolution a factor builder works at (month-end
cross-sections).

* `coherent_triple()` -- per as-of date, per code, the newest report that was
  public at that date in **income + cashflow + balance** AND whose `period_end`
  agrees across all three. Availability and tier are taken from the worst face.
* `accrual = (net profit - operating cash flow) / total assets` (both flows as
  reported for the same period, YTD cumulative), plus
  `cash_quality = operating cash flow / net profit` where net profit > 0.
* Two ranks: global cross-sectional rank and **peer rank inside the
  `period_end` cohort** (a month-end cross-section mixes annual and quarterly
  filers, so the two are not the same question).
* `compare_to_naive()` -- the same factor built by a `max period_end` join
  (availability ignored) versus the strict build, measured as rank Spearman and
  top-decile membership overlap, plus the two damage shapes separately:
  a *period flip* on a shared code and a *face gap* (a code that exists only in
  the naive build).
* Artifacts: `results/fund_pit_crossface_factor.json`,
  `data/fund_statement_export/pit_avail/pit_crossface_monthly.parquet`
  (124,681 rows / 24 month-ends / 5,238 codes, gitignored data lane).

## Result 1 -- the coherence filter is nearly free, and it grows

Median coherent codes at a month-end: **4,407** = **95.0%** of the codes present
in all three faces (min 86.8% in 2010, 99.98% today: 5,238 of 5,239 at
2026-08-31). So the earlier r1111 coverage limit (three statements share only
44.6% of income's 11,757 codes) is the binding constraint, **not** period
coherence.

## Result 2 -- lookahead on accruals is worse than on roe, and it is a calendar function

Over 200 month-ends (2010-01 .. 2026-08):

| metric | value |
|---|---|
| median share of shared codes whose report period flips | **79.2%** (max 99.8%) |
| median accrual rank Spearman (strict vs naive) | **0.837** (min **0.286**) |
| median top-decile overlap | **0.675** (min **0.202**) |
| median naive codes reading a not-yet-public report | 2,468 (max 5,230) |

The average hides the structure. Damage is a function of *where in the
disclosure cycle the month-end falls*, not of the factor:

| month | median rho | median top-decile overlap | reading |
|---|---|---|---|
| Jan / Feb | 0.658 / 0.663 | 0.505 / 0.504 | before the 04-30 annual deadline |
| **Mar** | **0.344** | **0.308** | annual season at its peak |
| Apr / May | 0.966 / 0.975 | 0.943 / 0.960 | annual reports landed |
| Jun / Jul | 0.751 / 0.769 | 0.605 / 0.632 | before the 08-31 H1 deadline |
| Aug | 0.992 | 0.985 | H1 landed |
| Sep | 0.867 | 0.696 | before the 10-31 Q3 deadline |
| Oct / Nov | 0.995 / 0.998 | 0.976 / 0.988 | quiet |
| Dec | 0.653 | 0.498 | next annual cycle starts |

All ten worst month-ends are **March** (worst 2012-03-31: rho 0.291, top-decile
overlap 0.202, 98.1% of shared codes flipped period). This is the r1102
measurement-resolution law in its clearest form yet: a study that sampled quiet
month-ends would have concluded "no lookahead" by construction, and a study that
sampled March would have concluded the factor is garbage. Both readings are
artifacts of the sampling calendar; the honest statement is the calendar itself.

## Result 3 -- cohort mixing is *not* the problem (honest negative)

Peer rank (within `period_end`) versus global rank: median Spearman **0.997**
(min 0.966) over the last 24 month-ends. Mixing annual and quarterly filers does
not materially reorder accruals -- so the `peer` column is published for
completeness and for future quarterly-only slices, not because it changes any
current conclusion.

## Honest gaps

* Accrual is YTD-cumulative, not quarter-isolated: cross-sections are comparable
  within one as-of date, but a Q3 YTD figure and an annual figure are different
  spans. The `cohort_size` and `period_end` columns are carried so a consumer can
  restrict to a single cohort.
* No forward-return join yet: this is a factor-construction face, not a judged
  batch. Any IC/return claim needs a fresh prereg (PREREG_TEMPLATE + explicit
  exit axis + D6 same-family correlation screen).
* `cash_quality` is undefined whenever net profit <= 0 (NaN, disclosed, never
  filled) -- that is a large minority of the universe in weak years.
* Total assets come from the balance face at the same `period_end`; a code whose
  balance statement lags by one period is excluded rather than paired across
  periods (deliberate: cross-period ratios are a different, unmeasured factor).

## Next

1. Wire the accrual face into a judged prereg only after deciding the sampling
   calendar question above (a March-only sample is not a smaller sample, it is a
   different experiment).
2. Add the forward-return join on the astock qfq panel once that panel is fresh
   again (bm-b lane was 31h silent this round; a declared stale takeover was
   executed by bm-a to restart it).