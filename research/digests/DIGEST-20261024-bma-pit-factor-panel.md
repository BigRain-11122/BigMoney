# Digest — the PIT availability face now has a factor consumer (r1109 bm-a, 2026-10-24)

Pointer: `scripts/fund_pit_factor_panel.py` · `results/fund_pit_factor_panel.json` ·
`data/fund_statement_export/pit_avail/pit_factor_monthly.parquet` (local lane).

## Question

r1104–r1108 built, audited and then exposed the fundamental availability face
(`<face>_avail_event.parquet` + `asof_slice`). Every measurement so far counted
**rows** that a `period_end` join would have read too early. A factor builder does
not consume rows, it consumes **rankings on a rebalancing date**. So: does the
lookahead actually damage the cross-section at the resolution a consumer uses?

## What was built

`pit_factor_panel()` — month-end cross-sections carrying `asof`, `code`,
`period_end`, `avail_event`, `avail_tier` plus `roe`, `np_yoy`, `rev_yoy`,
a cross-sectional `roe_rank_pct` and a `degenerate` flag (|roe| > 200 or book
value per share ≤ 0, r1107's concentration point). `compare_to_naive()` — the same
date under a `max period_end ≤ asof` join that ignores availability, compared on
the shared codes: how many codes change report, Spearman ρ of roe, and top-decile
membership overlap.

## Result (200 month-ends 2010-01 … 2026-08, 461,679 income rows)

* Median share of shared codes that get a **different report period** between the
  naive and strict join: **0.727** over the last 24 month-ends, 0.661 over the
  full grid (max 0.992).
* Median Spearman ρ of roe between the two faces: **0.896** (window), 0.877
  (grid), minimum 0.465.
* Top-decile overlap: median **0.677** (window) / 0.754 (grid), minimum
  **0.211** (2012-03-31) and 0.392 inside the window.
* The last two grid points are the sanity pair: 2026-07-31 differs on 95.8% of
  codes (H1 reports are still landing), 2026-08-31 on **0.06%** — the statutory
  H1 deadline is 08-31, so after it the two joins nearly coincide. A lookahead
  measurement is a function of *when in the disclosure cycle* you sample
  (r1102 measurement-resolution law, re-confirmed).

## Reading

The naive join is not a small perturbation: it hands the builder a partly
future cross-section on most month-ends, and one in five of its top-decile roe
names does not belong there at the worst dates. Wire the panel, not the
`period_end` join. Keep `degenerate` and `avail_tier` as confidence columns —
r1107 already established that the deadline-bound block must be weighted, not
excluded (dropping it cuts 10% of the sample but 38% of the top decile).

## Honest bounds

* Scope is the income face only; cashflow/balance availability is built but not
  yet carried into this panel.
* `degenerate` screens on the code's last stored book value, not a period-exact
  value (the test is a plausibility screen, not a join).
* `avail_tier` still says "most credible never-early upper bound" for the
  deadline-bound block (r1104 caveat unchanged); pre-2010 periods with no usable
  stamp stay on the deadline bound.
* Rankings are within one as-of date only; no sector neutralisation, no winsorising
  beyond the degenerate mask.