# DIGEST 2026-10-27 — E98: the end-choice grid on every era, not just the newest one

Source face: `results/e42_tilt_era/ENDCHOICE-ALLERAS-20261026.json`
Runner: `scripts/e39_panel_census.py endchoice` (selftest 276/276, +6 legs)
Evidence cutoff: **2026-10-26** · one panel read, one loader, deterministic
Predecessor: E95 `NEWESTERA-STABILITY-20261026.json` (1184.1bp span on the newest era alone)

## What was open

E95 demoted the newest-era tilt cell from "a level" to "a mechanism" because moving the
evaluation end alone moved it 1184.1bp — 23x the 50.5bp spread the repo had published.
One era is one observation: the caveat could have been a property of the *newest years*
(short, open-ended, most revision-prone) rather than of the instrument. E98 runs the
identical grid on every era. Same panel, same loader, same 12-end width; only the era
window differs.

## The grid, per era

| era | panel months | grid ends | months dropped | cell now (bp) | era monthly sd (bp) | span (bp) | span / monthly sd | verdict |
|---|---|---|---|---|---|---|---|---|
| pre2017 | 0 | — | — | — | — | — | — | structurally empty |
| 2017_2020 | 1 | — | — | — | — | — | — | structurally empty |
| 2021_2023 | 36 | 12 | 11 | 609.2 | 538.4 | **515.0** | 0.96 | inside_end_choice_span |
| 2024_now | 34 | 12 | 11 | 697.6 | 621.4 | **1184.1** | 1.91 | inside_end_choice_span |

`pre2017` and `2017_2020` are **not** measured. The E42 panel opens in 2020-12, so two of
the four era names carry zero and one month respectively. E98's ask ("run the grid on the
other three eras") therefore returns exactly **one** additional era on this panel; the
other two are reported structurally empty rather than swept on borrowed months.

## Three readings worth keeping

1. **The caveat belongs to the instrument, not to the newest years.** Every era the panel
   reaches re-derives under its own end grid. `2021_2023` moves 515.0bp on end choice
   alone while its *published* readings agree to the last decimal (see below). So no era
   tilt level may be quoted as a measurement, and any E41/E42 ratio must print its window
   end — the rule now holds on both eras, not on one.

2. **Published agreement is not measurement stability — and here the published spread is
   exactly 0.0.** `2021_2023` reads 609.2bp in all four published cells (the flat
   2026-10-20 face plus all three screening arms of the 2026-10-26 face): zero spread
   across a panel revision *and* across two repair arms. Its own end grid still moves it
   515.0bp. This is the strongest form of the E95 lesson: perfect reproducibility across
   cutoffs and arms says nothing at all about sensitivity to the evaluation end, because
   the two faces share the same end. A twin control cannot substitute for an end grid.

3. **Identical grid width, identical dropped count, 2.3x different span.** Both eras drop
   11 months under the same 12-end grid (31% of `2021_2023`, 32% of `2024_now`), so the
   515.0 vs 1184.1 difference cannot be a grid-width artefact. Stating each span against
   its own era's monthly sd (0.96 vs 1.91) shows the newest era is simply a more volatile
   specimen of the same cell — the ratio is the era's character, the sweep is the
   instrument's.

Sibling observation, free of charge: `beta_ladder_on_tilt` is stable *within* an era
across all 12 ends (2021_2023: 0.116–0.171; 2024_now: 1.013–1.173) but differs by ~9x
*between* them. So the often-quoted "ladder loads ~1.0 on size tilt" is an era-local
characteristic of 2024-now, not a property of the ladder. End choice barely touches beta
in either era — the level is fragile, the load is not.

## Cost and discipline

One panel load, no network, no engine burn beyond the loader; descriptive census only —
zero prereg, zero gate, zero judgement, zero ledger booking, trial_count 0. The six new
selftest legs pin the four things that must hold before any era span is quotable: the
reader sees **both** face schemas (a flat-only reader reports "nothing published" for the
entire screened family), an era the panel does not reach is skipped rather than priced,
the grid is proven to actually move the cell, and each span carries the months it threw
away plus its own era's monthly movement.

## Next (seeded as E101)

The same end grid on the *gap-arm* levels E99 named: if the level is end-fragile on every
era, the arm deltas (−745.9bp / −1098.3bp) need the same treatment — are they stable across
ends, or do they inherit the fragility of the level they are subtracted from?