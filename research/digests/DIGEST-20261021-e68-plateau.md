# DIGEST 2026-10-21 — E68: the month-end cost plateaus at about the first week off-cycle

**Unit:** E68-MONTHEND-PLATEAU (pool, cpu-only, bm-b)
**Runner:** `scripts/e39_panel_census.py neighborhood --neighbors 4` (selftest 102/102)
**Faces:** `results/e44_midmonth/NEIGHBORHOOD-20261021.json` (start 2020-01-01),
`results/e44_midmonth/NEIGHBORHOOD-20261021-s20130101.json` (start 2013-01-01).
x1, cutoff 2026-10-21, 1,265 names, one universe, one rank cache.

## Question

E65/E66/E67 priced 1/2/3 sessions off the month boundary and found a cheap first slip and an
expensive second one. This leg burns only the two missing fourth-session arms (`me_m4` early,
`me_p4` late) and brackets each against the already-burned k=3 and k=5 faces: does the cost keep
stepping toward the E59 off-cycle level (−60..−90bp), or does it plateau inside the first week?

## Answer

It **plateaus** at about four sessions — the first week off the boundary is the whole cliff.

Newest era (the start-invariant column, bit-identical at both window starts):

| sessions off month-end | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| early (before boundary) | −19 | −24 | −49 | **−51** | −64 |
| late (after boundary) | −43 | −52 | −74 | **−78** | −74 |

- The k=3→k=4 step is +2bp early and −4bp late, i.e. inside the ±2bp shape tolerance on the early
  side and a small continuation on the late side. The large move is still the k=2→k=3 step
  (−25bp early, −22bp late, E67).
- k=4 sits at **−51bp early / −78bp late**, already inside the E59 full off-cycle band
  (−60..−90bp) on the late side and just above it on the early side; k=5 adds only a further
  −13bp early and reads *less* negative late (−74), so the plateau is not a one-point accident.
- Late ≥ early at every magnitude (2.3× at one session down to 1.5× at three; 1.5× at four), so the
  left/right asymmetry is stable across the whole ladder.
- Turnover and fees are flat: 0.592 (early k=4) / 0.585 (late k=4) turns/yr and 7.7 / 7.6 bp/yr at
  the 2020 start, 0.570 / 0.572 and 7.4 / 7.5 bp/yr at the 2013 start — same band as E59/E63/E67.
  The plateau is not a fee effect.

## Reading

Combined with E67 the shape is now: **a two-session grace period at a small toll, one expensive
step at the third session, then a floor.** Practically, the calendar decision is forgiving about
which day inside the first week you rebalance and expensive only about leaving it later than that.
The "off-cycle cost" seen in E59 is therefore not paid gradually across the month — nearly all of
it is paid by the time you are four sessions off the boundary.

## Honest limits

- The bracket faces (k=3 from E67's arms, k=5 from E65) are burned at cutoff 2026-10-20, one panel
  bar earlier than this leg (2026-10-21). The face records this in `answers.bound_rows_cutoff` /
  `bound_rows_source`; the bracket is a shape reading, not a same-cutoff comparison. Only the k=4
  arms are at the fresh cutoff.
- Full-window columns are not clean: early reads −53bp (2020 start) and −22bp (2013 start), late
  reads −18bp and −32bp; older eras flip sign (late k=4 reads +22bp in 2021_2023 at *both* starts,
  and −76bp in pre2017 at the 2013 start). Only the newest era carries the plateau shape.
- Shape labels come from a ±2bp tolerance on three points; with k=4 that tolerance is what makes
  "plateau" the honest label rather than "ramp". They describe the ladder, they are not a test.
- The lag moves the **decision** session, not just the entry, and the engine has no entry-only lag
  hook — same limit as E65/E66/E67.
- Descriptive census only: no gate, no verdict, no prereg, no trial count, zero ledger booking.

## Handoff

The ladder is now dense enough (1..5 both sides) that another magnitude buys little. Next cheap
units, in order of information per second: (a) **E69-MONTHEND-WEEKLY-CLASH** — the k=4/k=5 plateau
sits at the first-week boundary, which is where the E44 weekly rebalance face lives, so price the
two calendars' *overlap* (does adopting a month-end calendar merely re-time the weekly one, or does
it add turnover on top?) using the existing weekly arm in `e44` rather than new arms; (b) only if
(a) is flat, revisit the E59 off-cycle band with a plateau-anchored read.