# E112 — the burn-in face on the screened arm: does the conclusion survive the repair?

Face: `results/e44_burnin/BURNINSCREEN-20261026.json` (arms beside it as
`BURNSCREEN-arm-raw-20261026.json` and `BURNSCREEN-arm-neutralise_int-20261026.json`),
evidence_cutoff 2026-10-26. Leg: `scripts/e39_panel_census.py burninscreen`
(selftest 331 → **338/338**). Pool row `E112-BURNIN-SCREENED-TWIN`.

## Why this leg exists

E97's routing table found 21 of 25 charged modes with no screened twin, ranked by
how many published numbers each one carries. The top row is `run_burnin`: one
burn feeds four published modes (burnin / e44 / knife / skinloo) and carries
1,727 numbers — 33% of the whole uncovered surface. E77 moved the wide book when
the split repair was switched on, so the open question is not *whether* the
burn-in numbers move but whether the **burn-in conclusion** — the gate dates, the
un-invested session counts, the size of the first eligible set — survives them.

## The measurement

Both arms are burned off **one load** of the panel, at **one cutoff**, through the
same `run_burnin` (`raw=` is now a seam; the default path still loads the shipped
universe for every existing face). The screen is `neutralise_int`: 67 prints on
67 of 1,317 names, every one integer-like, **0 non-integer adjacent prints
skipped**, names in = names out = 1,317 (a neutralising repair cancels the print;
it never drops a name, so eligibility cannot move by construction).

The join harvests 56 numeric cells per arm and publishes every one.

| start | sessions un-invested | first invested bar | eligible at first trade | wide ann % (raw → screened) | Δ |
|---|---|---|---|---|---|
| 2013-01-01 | 259 | 2014-02-07 | 34 | 7.48 → 7.67 | **+0.19** |
| 2016-01-01 | 262 | 2017-02-03 | 34 | 4.91 → 5.15 | **+0.24** |
| 2018-01-01 | 265 | 2019-02-01 | 34 | 6.81 → 7.11 | **+0.30** |
| 2020-01-01 | 263 | 2021-02-01 | 34 | 0.25 → 0.61 | **+0.36** |

* **Gate columns: 0 of 20 moved. Gate dates: 0 of 20 moved.** Sessions
  un-invested, un-invested share, months, `first_invested_bar`,
  `first_trading_rebalance`, `earliest_possible_trading_decision`,
  `first_rebalance_with_elig_ge_5`, eligible-at-first-trade, symbols eligible —
  all bit-identical between the arms.
* **Return columns: 13 of 36 moved.** The movement is entirely in the wide book;
  the ladder book is identical everywhere (no ladder member carries a print). The
  2021→now span moves +0.42pp, and the warm wide drawdown improves 0.42pp
  (−36.55% → −36.13%).
* The largest single move on this face is **0.42pp**, an order of magnitude below
  the ~216bp/yr figure the `panel_screen` header attributes to E75's adjacent-print
  census. The two are not the same quantity: E75 priced a one-off impact on an
  equal-weight book, and E77's 216bp came off `e27.run`'s engine headline, while
  this leg reads the warmed full-calendar curve sliced afterwards (which dilutes
  a handful of one-session prints over 5–14 years). Do not quote 216bp against
  this face.

## Three controls, all published

| control | what it isolates | result |
|---|---|---|
| identity (raw vs raw) | did the join machinery move anything? | 0 of 56 cells moved, max Δ 0.0 |
| coverage | is the twin actually a twin? | 56 compared, 0 one-sided, 0 null-on-either-side |
| **cutoff (BURNIN-20261020 raw vs today raw)** | the panel refresh, arm held fixed | **26 of 56 cells moved; max Δ 6 (symbols_eligible +6 names); returns move −0.12…−0.28pp** |

The cutoff control is the load-bearing one. It says the six-day refresh moves
**more cells** than the split repair does, and on the same order on the return
columns. Consequence for every future burn-in read: **a 0.2–0.3pp gap between two
published burn-in faces is inside refresh noise** and cannot be attributed to a
code change without this control. The gate columns are stable on both axes
(`gate_dates_moved = 0` on each), which is what makes the burn-in argument safe to
cite at all.

## What survives, and what this does not say

* The burn-in conclusion survives: the 250-bar gate is window-relative, the first
  invested bar lands the session after the first month end at or past index 250,
  and neither the repair nor a panel refresh moves it. That is a property of the
  membership rule, and the rule is arm-free.
* It does **not** say the panel is clean: `neutralise_int` repairs prints without
  changing which bars are missing, so unchanged eligibility counts are a property
  of the mode, not evidence of data quality.
* It is **not** a strategy verdict: descriptive census, no gate, no prereg, no
  trial count, no ledger booking.
* One burn per runner: `knife` and `cutcurve` keep their own tickets — the knife
  leg re-burns `run_burnin` at MIN_BARS 60/120/250 and is a separate 3× burn.