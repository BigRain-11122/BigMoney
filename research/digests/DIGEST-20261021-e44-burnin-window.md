# DIGEST 2026-10-21 — E44 burn-in: the missing years are a 250-bar gate, not missing data

Round r1120, bm-b. Script `scripts/e39_panel_census.py` (`burnin` leg, selftest 54/54).
Face `results/e44_burnin/BURNIN-20261020.json`. Evidence cutoff 2026-10-20. Wide book =
top9999 over the de-duplicated panel with `sh511*` excluded, ladder5 = the E24 five, cost x1,
250-bar eligibility (`e24_ladder_weighting.MIN_BARS`).

## The gate binds exactly, in every start window

`elig()` needs 250 **consecutive, non-missing, in-window** closes. Two consequences fall out,
and both are measured rather than asserted:

| start | bars | gate clears (idx 250) | first possible decision | first actual trade | sessions un-invested | share | eligible names at first trade |
|---|---|---|---|---|---|---|---|
| 2013-01-01 | 3,347 | 2014-01-20 | 2014-01-30 | **2014-01-30** | 259 | 7.74 % | 24 |
| 2016-01-01 | 2,620 | 2017-01-11 | 2017-01-26 | **2017-01-26** | 262 | 10.00 % | 54 |
| 2018-01-01 | 2,132 | 2019-01-11 | 2019-01-31 | **2019-01-31** | 265 | 12.44 % | 81 |
| 2020-01-01 | 1,645 | 2021-01-13 | 2021-01-29 | **2021-01-29** | 263 | 16.00 % | 184 |

In all four windows the first trade lands on **the earliest date the rule can physically allow**:
the first month end at or past index 250. The book does not wait for names to appear — it waits
for the calendar. That is why "the wide book's monthly series begins 2016-12 on a 2018 start"
was never a data mystery.

`first_rebalance_with_elig_ge_5` and `..._ge_20` are both **the same date** as the first trade in
every window: the eligible set arrives whole (24 / 54 / 81 / 184 names at once), not gradually.
The 2020 window is the widest (184 of 290 priced names clear on day one), so it is not scarcity
of names that delays the start — it is the 250-bar counter.

## The pre-2017 hole is worth money

Cold start (burn-in paid inside the measured window) versus warm start (the same spec run on the
full 2012-05-28 calendar, sliced afterwards):

| window | wide cold | wide warm | ladder cold | ladder warm |
|---|---|---|---|---|
| 2013-01-01 → cutoff | **+7.61 %/yr** | **+13.68 %/yr** | +5.55 %/yr | +10.93 %/yr |

The gate costs **6.07 pp/yr on the wide book** (5.38 pp on the ladder) purely by deleting the
first ~12.3 months of each window.

Warm calendar-year returns make the size of the missing block concrete:

| | 2013 | 2014 | 2015 | 2016 |
|---|---|---|---|---|
| wide | +6.94 % | **+41.04 %** | +14.36 % | −4.98 % |
| ladder5 | +2.82 % | **+46.61 %** | +8.89 % | −9.13 % |

2013-2016 annualises +13.68 %/yr on the wide book — better than 2017-2020 (+12.68 %/yr) and far
better than 2021-now (+0.74 %/yr). The pre-2017 years are not a weaker regime that was rightly
skipped; they are the second-best block in the panel and they are missing for a counting reason.

## Why it matters

1. **Every cold-started window is biased low by construction.** All E34-E44 faces start cold, so
   the first 12.3 months of each are repo, and the annualised column silently absorbs that. The
   like-for-like comparison is the warm column.
2. **The bias grows as the window shortens.** The dead block is a fixed ~260 sessions, so it is
   7.7 % of a 3,347-bar window and 16.0 % of a 1,645-bar one — which is exactly the shape of the
   "newest era is weaker" readings in E41/E42.
3. **It is a spec decision, not a defect.** 250 bars is intentional (no freshly listed ETF can
   enter on a thin history). What was unmeasured is that the counter restarts at every start
   date, so the cost of honesty is paid inside the very window being measured.

## Honest limits

- The warm run pays the burn-in on 2012-05-28..2012-12-31, which is a partial year; every
  calendar-year return here chains off a real year-end mark, so 2013 is not distorted.
- Symbol coverage is a genuine second gate: 43 names become eligible in 2014, 249 only in 2022,
  so the wide book at a 2013 start holds 24 names, not 100+. The 2013-2016 figures are therefore
  a small-book sample, disclosed, not the modern universe projected backwards.
- The 2022 cohort (249 names) is the panel's bulk-listing wave; no reading here assumes the
  panel's membership is stationary.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.