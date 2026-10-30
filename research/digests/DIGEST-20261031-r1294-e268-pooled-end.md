# E268 -- can a reader without the row's own draws still run the screen?

**Face** `results/state_tilt/BANDPOOLED-2026-10-29.json` (+ `bandpooled_latest.json`)
**Runner** `scripts/e268_screen_on_pooled_end.py` (run / verify 0 problems / selftest 41/41)
**Source** E262's published pairs and pooled ends, re-read through E266's 36 comparisons.
No band rebuilt, no shuffle drawn, no panel, no bill.

## The question

E267 established that the operative half of the wide-end screen is the own-side guard
(`donor_p95 > t_side` **and** the row's own end below `t_side`). That guard needs `own_p95` -- the
one number a reader who did not draw that row's band does not have. Two substitutes do live in the
same published face:

| substitute | where it comes from |
|---|---|
| `group_flat_tight` | the (leg, base) group's pooled `flat_tight_p95` |
| `group_flat_wide` | the group's pooled `flat_p95` |
| `row_published_verdict` | the row's own `published_verdict_wide` -- a boolean, no draw needed |

Only the own-end slot changes; donor end, threshold and population are held fixed, so any
difference in the confusion table is attributable to the substitution.

## Answer

| screen | own p95 | pooled tight | pooled wide | published boolean |
|---|---|---|---|---|
| guarded_side | 2 tp / 0 fp / 0 fn **exact** | 2 / 0 / 0 **exact** | 0 / 0 / 2 (misses both) | 1 / 0 / 1 |
| bracket_side | 2 / 0 / 0 **exact** | 2 / 0 / 0 **exact** | 0 / 4 / 2 | 1 / 2 / 1 |

The pooled **tight** end is not merely exact on the moved set -- it answers the guard **identically
on all 36 comparisons** (24 below t, 12 above, **0 disagreements**), which is what makes it a
disclosure rather than a lucky fit. The pooled **wide** end answers **6** comparisons the other way
(row indices 9 and 13) and the **published boolean answers 3** (row index 13).

Row 13 is the one E262 already disclosed as interval-dependent: `era_2023_2024 star_lag1_residual`,
own p95 **2.0161** against its cross-arm threshold **2.1384** (below -> outside), while the published
boolean says **inside**. The boolean is E259's **self-arm** judgement, not this face's resolved leg.
A reader holding it is not holding a rounded version of the right number -- they are holding a
different leg.

### Why the equivalence is weaker than it looks

The nearest comparison to its own threshold is index 15 at **0.0835** (4.43% of the threshold), and
nothing in the table is closer. So the two ends have only been compared where disagreeing was
impossible; inside that band they are untested. The face publishes this as `ambiguity_band` per
substitute (numeric ends only -- a boolean end has no distance to a line), and `underpowered: true`
because 2 moves sit below the 3-positive floor.

### The card's own question -- disclosure or change of meaning?

| substitute | exact on moves | differs elsewhere | reading |
|---|---|---|---|
| own p95 | yes | 0 | reference |
| pooled tight | yes | **0** | `disclosure_same_calls_as_the_rows_own_end` |
| pooled wide | no | 6 | `change_of_meaning` |
| published boolean | no | 3 | `change_of_meaning` |

## What this changes operationally

A reader with only the table can run the screen **only** through the group's pooled tight end, and
only outside the ambiguity band. Anyone handed the per-row boolean is being handed E259's self-arm
verdict and will miss exactly the row where the arms disagree. Face supply downstream: E270 asks the
same sufficiency question across every state-tilt face, E271 asks whether the moved set depends on
*which* donor was picked rather than only how wide it is.

## Engineering pits (both caught in-window)

1. Three selftest legs failed on **correct code**: the fixtures put the pooled end at 1.9 against a
   2.0 threshold and asserted "reads the row as inside" -- 1.9 < 2.0 is below. The assertion was
   wrong, not the code (r1281 shape, third sighting).
2. `published_verdict_wide` is not on E266's comparison records (it lives on the source rows), so the
   boolean variant scored `undefined` on all 36 comparisons until it was joined back by row index.
   The only visible symptom was the agreement block reporting **0 judged rows** -- an undefined
   population reading as "no disagreements" is the r1261 both-sides-equal shape one field over.
3. A verdict branch reading `perm` before `run()` defined it is a run-time NameError but compiles
   clean, so `verify` -- not `selftest` -- is the leg that catches ordering.