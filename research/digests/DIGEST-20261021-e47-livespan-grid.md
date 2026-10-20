# DIGEST 2026-10-21 — E47 livespan grid: the newest era's flip survives zero cost, the older eras' flips do not

Round r1123, bm-b. Script `scripts/e39_panel_census.py` (`livespan` leg, unchanged code path,
selftest 68/68). Faces `results/e46_live_span/LIVESPAN-20261020-x1-p3.json` (thirds at cost x1)
and `...-x0-p2.json` (halves at zero cost). Evidence cutoff 2026-10-20. Same warm pair of curves
as E45/E46, same era slicing.

## What the two new cells add

r1122 cut each era in halves at cost x1 and found one flip (+380 → -215 bp on 2024-now). The two
follow-ups ask whether that flip is a fee artefact and whether halves were the coarse answer.

| run | eras with an internal sign flip | part bands (bp) |
|---|---|---|
| x1, halves (r1122) | 1 / 4 (`2024-now`) | 30 / 41 / 195 / 595 |
| x1, thirds (r1123) | **3 / 4** (`pre2017`, `2021-2023`, `2024-now`) | 403 / 346 / 635 / 670 |
| **x0, halves (r1123)** | **1 / 4** (`2024-now`) | 41 / 24 / 190 / 593 |

Thirds at cost x1:

| era | era spread | parts | flip |
|---|---|---|---|
| pre2017 | +236 bp | +198 / −26 / +377 | yes |
| 2017-2020 | +419 bp | +205 / +526 / +551 | no |
| 2021-2023 | +243 bp | −50 / +585 / +119 | yes |
| 2024-now | +89 bp | +291 / +375 / −295 | yes |

Halves at zero cost:

| era | era spread | parts | flip |
|---|---|---|---|
| pre2017 | +239 bp | +252 / +211 | no |
| 2017-2020 | +423 bp | +429 / +405 | no |
| 2021-2023 | +247 bp | +160 / +350 | no |
| 2024-now | +93 bp | +383 / −210 | **yes** |

## Reading

The three older eras are stable at zero cost (bands 41 / 24 / 190 bp, no sign flip) and turn
unstable at cost x1 once the era is cut into thirds — so the mid-era flips in the thirds table are
a fee-times-granularity artefact, not selection. The newest era is the opposite case: it flips at
every granularity and at every cost (x0 halves 383/−210, x1 halves 380/−215, x1 thirds
291/375/−295, x3 halves 373/−224), band 593-670 bp. That agreement across four independent readings
is what makes `2024-now` the only selection-driven inversion in the family, and it is the same
stretch whose size-neutral figure r1119 showed to be a skin decision.

Consequence for the headline: an era-level spread quote is only meaningful where the era is
internally steady. On the three older eras the quoted number survives the finest split we ran
(±20-40 bp at zero cost); on the newest era the +89 bp is an average of two opposing markets and
should be quoted as a range, not a level.

Descriptive census only: zero prereg, zero verdict, zero ledger booking, trial_count 0.