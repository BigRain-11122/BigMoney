# DIGEST 2026-10-30 — E241: the pair does not reproduce because the reader is one session out of step

Face: `results/state_tilt/REPRO-2026-10-29.json` (pointer `repro_latest.json`)
Runner: `scripts/e241_pair_reproduction.py` (run / selftest 15/15)
Card: `knowledge/METHODOLOGY_ASSETS.md` E241
Defect: **F-20261030-01** — `scripts/e240_aggregate_attenuation.py::design_share_book`
Repair window: 2026-10-30 06:2x–06:4x (bm-b r1267)

## The question

E238 published the leave-one-out pair `(b_own 0.596, b_agg 0.771)` on each member's OWN date
grid (13,911 differenced rows, 3,504 sessions). E240 re-ran "E238's coordinates" on the common
five-member grid and read `(A_share -0.333, B_book -0.174)`, publishing the gap as a finding
about the population. Three candidate causes were named: ROWS, WEIGHTS, RESPONSE.

## The ladder (one change per rung)

| rung | change vs previous | rows | a_share | denominator coef | b_agg (derived) |
|---|---|---|---|---|---|
| r0 `published_rows_loo` | baseline — E238 on its own rows | 13,911 | 0.5963 | 1.3669 | 0.7706 |
| r1 `common_rows_loo` | **ROWS** (common dates, same construction) | 6,640 | 0.8911 | 1.3582 | 0.4671 |
| r2 `common_rows_inclusive` | **DENOMINATOR** (leave-one-out → inclusive) | 6,640 | 0.7904 | 1.3441 | 0.5537 |
| r3 `common_grid_e240_code_path` | **CODE PATH** (E240's routine as published) | 6,635 | -0.3330 | -0.1742 | 0.1588 |
| r3b `e240_code_y_realigned` | **Y ALIGNMENT** (same routine, y from the same session) | 6,635 | 0.7910 | 1.3430 | 0.5519 |

r0 reproduces E238 to 0.0000 on both coefficients, so the grid is not the problem, and r2 ≈ r3b
confirms that the rung difference is not the 5-row date-set change.

## The defect

`e240.common_increments` indexes its arrays by the **kept** session: `dy[i]` is the move INTO
`dates[i]`. `design_share_book` re-paired the sessions from `k = 1` and appended `dy[m][k - 1]`,
so the dependent variable was the move into `dates[k-1]` while the share increments described
`dates[k-1] → dates[k]`. Counted, not asserted:

* rows tested **6,635**, dy matches the PREVIOUS session's move on **6,630**, the same
  session's move on **0** (the 5 misses are the panel's first rows).

Repair: the y is now taken from the same session pair as the increments
(`per[m][d1][0] - per[m][d0][0]`). `scripts/e240_aggregate_attenuation.py` selftest stays
12/12. E240's `dy`/`dx` designs (aggregate rest, pair one-vs-rest, two-way FE) are **not**
affected: they index both arrays by the same session, so their numbers stand.

## What the corrected numbers say

* Corrected common-grid pair: **A 0.7910 [0.6289, 0.9531]**, denominator coef 1.3430,
  derived rest channel **b_agg 0.5519**.
* The row restriction alone moves the rest channel **0.7706 → 0.5519** (-0.219 aligned gap:
  rows -0.304, denominator +0.087, code-path -0.002, residual 0.0). **No sign flips.**
* The published face's A/B pair is **superseded** (`README`: F-20261030-01). Its `A_share` and
  `B_book` are reproduced exactly by the as-published replica, which is why the ladder keeps
  that rung rather than erasing it.
* The naive gap E240 published (-0.945 on the derived rest channel) decomposes into **0.333
  of parametrisation** (a derived `b_agg = g - b_own` compared against a raw `B_book`) plus
  **0.612 aligned**; the published figure from the digest (-1.178) is the same defect class at
  the A side (-1.164) plus its internal `parametrisation_check`, which compares a fit on
  `(d share, d agg)` against a fit on `(d own, d one, d rest3)` — different conditioning sets,
  so those two are also not the same object.

## Why it matters

Two rounds ago the family published "the rest aggregate is only 54% of four counterparties"
as a market statement. It was, in part, a mis-indexed `y`. And the general shape recurs in this
repo: a face and its consumer share a *grid* while disagreeing about *alignment*, and the
disagreement is then attributed to the population.

## For the next round

* E242 (ready) — sweep the published family slopes for inflation by omitting the other
  members; it must quote **identified** counterparts, and it inherits this rounding law.
* E243 (ready) — is the additivity reading stable outside the window that produced it.
* E240's face needs one re-derivation on the repaired runner before its pair is quoted again;
  until then the corrected numbers live in REPRO-2026-10-29.json.