# E104 — a split CAN sit inside an unchanged holding, and the repair is not always the plausible side

- date: 2026-10-27 (bm-b r1170)
- face: `results/e44_midmonth/HELDSPLIT-20261026-s2018.json`
- code: `scripts/e39_panel_census.py` mode `heldsplit`, selftest 307 -> 320
- pool: E104 (closed here) + E105 (answered as the `largest_single_name_read` column)
- question (pool E104): E100 closed the gap arm as a price-read story and then had to
  admit that "a split inside an unchanged holding would be invisible here even though
  it still moves the book's curve". Does such a split exist, and how big is it?

## The blind spot is real: 4 of 6 cells carry one

For every transition, read the names the repair arm held at **both** ends (no swap, so
E100's entrant/exit lists cannot see them) under both arms' prices, same dates.

| era | book | delta mean bp | max window bp | windows with a split | verdict |
|---|---|---|---|---|---|
| 2024_now | me | **+15.2** | **247.4** | 51.5% | one window (2024-08-30) |
| 2024_now | mid | **+14.1** | **162.0** | 48.5% | one window (2024-08-15) |
| 2021_2023 | mid | +5.5 | 55.4 | 22.2% | one window (2021-01-15) |
| 2021_2023 | me | +3.9 | 35.5 | 19.4% | one window (2023-03-31) |
| 2017_2020 | me | 0.0 | 0.0 | 0.0% | no split inside unchanged holdings |
| 2017_2020 | mid | 0.0 | 0.0 | 0.0% | no split inside unchanged holdings |

Per-name pieces add up to each window delta exactly (residual 0.0 by construction and
published). The horizon is one window each, so nothing here is a rate.

## E105 answered in the same pass: a level is a mean over few names

Every cell now carries `largest_single_name_read` — the biggest absolute read in the
window plus that name's share of the window mean, with the share suppressed
(`share_eligible=false`) where the mean is inside 0.5%, because "200% against a 0.02%
mean" is a ratio of noise, not a finding.

The largest reads are not splits that the repair fixes — they are prints present in
**both** arms:

| era | book | name | unscreened | repaired | window |
|---|---|---|---|---|---|
| 2021_2023 | mid | sz159845 | **+200.0%** | +200.0% | 2022-07-15 |
| 2021_2023 | me | sz159845 | +169.1% | +169.1% | 2022-07-29 |
| 2017_2020 | me | sz159967 | **-72.8%** | -72.8% | 2020-10-30 |

A one-month +200% on an ETF is a print artefact, not a return, and the repair did not
touch it. That is a limitation of the repair's scope, not a defect in it.

## But the repair is the implausible side in at least one window

`sh510580` over 2024-08-30 → 2024-09-30:

| series | 2024-08-30 | 2024-09-02 | read across the jump |
|---|---|---|---|
| unscreened | 0.576 | 2.278 | **+295%** |
| repaired | 5.79 | 90.58 | **+1464%** |

Both arms see the same step date; the ratio between the arms changes from ×10.05
(2024-08-30) to ×39.8 (2024-09-02), i.e. the repair rewrites this name's level by a
further ×3.96 AT the event while the raw series already jumps ×3.96 there. An ETF does
not gain 1464% in a month, so the repaired read is the broken one in this window.

Counted mechanically, not by eye: the face publishes `reads_beyond_100pct` for both arms
per window and per cell — **repaired arm 16 implausible reads, unscreened arm 14**, the
extra two both `sz159747` in 2023. The asymmetry is small, but the direction is not
guaranteed: assuming "the repair is the plausible side" is exactly the assumption this
leg refuses to make.

## How this changes what E99–E103 may claim

- E100's sentence "the repair prices a split print" stays true for the windows it named.
  It must not be generalised to "the repair always improves a read" — 2024-08 sh510580
  is the counter-example.
- Unchanged holdings carry split exposure too, so the E99 family levels are **not**
  clean of print artefacts even inside the arm-swap decomposition; the exposure is
  +3.9..+15.2bp of mean read per cell, up to 247bp in a single window.
- Any future use of a repaired price series should print `reads_beyond_100pct` beside it,
  per arm, so the plausibility question is answered by data rather than by provenance.

## Honest limits

- Descriptive only: no gate, no strategy verdict, no prereg, no trial count, no ledger.
- The population is the repair arm's persistent names; where the arms hold different
  names, the unscreened arm's own persistent set is not measured here.
- An equal-weight mean of name-level reads is not a portfolio return.
- `reads_beyond_100pct` is a shape test (|read| > 100% in one window), not a corporate
  action lookup; it flags candidates for E106, it does not adjudicate them.

## Seeded next

- **E106-REPAIR-STEP-CONSISTENCY**: for the names flagged by `reads_beyond_100pct`,
  check whether the repaired series steps consistently at the split date (level ratio
  before vs across the event). A repair that rescales a name without stepping at the
  event fabricates a read (sh510580 / 2024-09-02 is the witness).
- **E107-UNCHANGED-HOLDING-CURVE-EFFECT**: this leg measures the read, not the curve;
  price the same windows on the engine's own simulated book to see how many bp of the
  era curve those persistent-name splits actually move.