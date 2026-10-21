# DIGEST 2026-10-21 — E67: the boundary penalty is a step, and the step is between session two and three

**Unit:** E67-MONTHEND-NEIGHBORHOOD (pool, cpu-only, bm-b)
**Runner:** `scripts/e39_panel_census.py neighborhood` (selftest 102/102, +3 hermetic legs)
**Faces:** `results/e44_midmonth/NEIGHBORHOOD-20261021.json` (start 2020-01-01),
`results/e44_midmonth/NEIGHBORHOOD-20261021-s20130101.json` (start 2013-01-01).
x1, cutoff 2026-10-21, 1,265 names, one universe, one rank cache.

## Question

E65 (late) and E66 (early) each priced 1/3/5/10 sessions off the month boundary and both read a
cost at every magnitude. That leaves the second session unpriced, so "how fast does the cost
start?" had no answer between one and three. This leg burns only the two missing arms
(early 2 = `me_m2`, late 2 = `me_p2`) and brackets each against the already-burned 1- and
3-session faces: is the penalty a kick on one session, or a ramp?

## Answer

A ramp — but a **stepped** one. The newest era, which is the start-invariant column (E59/E66):

| sessions off month-end | early | step | late | step |
|---|---|---|---|---|
| 1 | −19bp | — | −43bp | — |
| 2 | **−24bp** | −5bp | **−52bp** | −9bp |
| 3 | −49bp | −25bp | −74bp | −22bp |

- Between one and two sessions the penalty barely moves (5bp early, 9bp late). Between two and
  three it triples: −25bp and −22bp of additional cost in a single session. The expensive part of
  going off-cycle is **not the first slip, it is the second**, so a one-session miss is the cheap
  case the ladder had already told us about and a two-session miss is still nearly as cheap.
- The left/right asymmetry of E66 survives every magnitude: late costs 2.3× early at one session,
  2.2× at two, 1.5× at three. Being early never becomes as expensive as being late.
- Turnover stays flat at 0.57–0.59 turns/yr for both new arms (0.592 early, 0.590 late at the 2020
  start) and the fee band is unchanged, so the step is not a fee step (same exclusion as E63).
- The second-session arms reproduce E66's start-invariance: `me_m2` reads −24bp and `me_p2` −52bp
  in the newest era at **both** window starts, while their full-window values move with the start
  (−17/−21bp early, −15/−26bp late).

## Reading

The month boundary behaves like a **deadline with a cheap grace period of about two sessions**:
slip one or two sessions and you pay a small toll; slip three and you pay the bulk of the
off-cycle cost. The earlier digest read this as "lateness is a cliff"; with the second session
priced, the cliff has a landing — the drop is not at the boundary, it is at the end of the first
week off the boundary.

## Honest limits

- The bracket faces were burned one panel bar earlier (**2026-10-20**) than this leg
  (**2026-10-21**), because the panel advanced during the round. The fallback is explicit in the
  face (`answers.bound_rows_cutoff`) and the bracket is a shape reading, not a same-cutoff
  comparison. Only the k=2 arms are at the fresh cutoff.
- Full-window columns do **not** show the clean step: early reads +8/−17/−65bp (2020 start) and
  −11/−21/−20bp (2013 start); late reads −27/−15/−17bp and −18/−26/−34bp. Older eras also flip
  sign on the new arms (`me_p2` reads +7bp in 2021-2023 at a 2020 start, +29bp at a 2013 start).
  Only the newest era carries the stepped shape.
- The lag moves the **decision** session, not just the entry: the book is re-ranked on the
  off-cycle date with whatever had published by then. An entry-only lag needs an execution hook
  the engine does not have (same limit as E65/E66).
- Shape labels come from a ±2bp tolerance on three points. They describe the ladder; they are not
  a test, and no arm here is a recommendation.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.

## Handoff

Next cheap unit seeded: **E68-MONTHEND-PLATEAU** — burn `--neighbors 4` on the same leg (one
command, two arms: `me_m4`/`me_p4`). Question: does the cost plateau once past the third session
(4 ≈ 3, i.e. the first week is the whole cliff), or does it keep stepping toward the E59
off-cycle level of −60..−90bp? Everything else in the ladder already exists, so this is two more
arms plus a `k=4` bracket against the k=3/5 faces.