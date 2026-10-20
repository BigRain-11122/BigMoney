# DIGEST 2026-10-21 — E46 era split: the newest era is the only one whose number averages two opposing markets

Round r1122, bm-b. Script `scripts/e39_panel_census.py` (`livespan` leg, selftest 68/68).
Faces `results/e46_live_span/LIVESPAN-20261020.json` (cost x1) and `...-x3-p2.json`.
Evidence cutoff 2026-10-20. Same warm pair of curves as E45 (full calendar from 2012-05-28,
sliced per era), each era then cut into equal-bar halves.

## Three of four eras are stable; one inverts

| era | era spread | first half | second half | band | sign flip |
|---|---|---|---|---|---|
| pre2017 | +236 bp | +249 bp | +208 bp | 41 bp | no |
| 2017-2020 | +419 bp | +428 bp | +398 bp | 30 bp | no |
| 2021-2023 | +243 bp | +154 bp | +349 bp | 195 bp | no |
| 2024-now | **+89 bp** | **+380 bp** | **−215 bp** | **595 bp** | **yes** |

The two oldest eras move by 30-41bp across a decade of their own history — their single number
*is* a property of the era. The two newest do not: 2021-2023 doubles from its first to its second
half, and 2024-now flips sign.

## The flip is not a cost artefact

At cost x3 the same cut reads +373 / −224 (era 81bp, band 597bp) — a 9bp move from x1. So the
wide book's negative second half is not fee drag; it is underperformance against the ladder
(-215bp at x1, -224bp at x3, so ~9bp of the negative half is churn).

## What the newest-era number actually means

`+89bp/yr` is the average of a +380bp first half and a −215bp second half, and the split point
falls within a few weeks of 2025-02-05 — the bar at which the 250-bar gate first lets a cold-start
book hold anything (E45). Two independent cuts (warm forward slice: −129bp; second half of the
era: −215bp) therefore agree that **the live stretch of the newest era is negative**, while the
era's headline is positive because it includes the 13 months a cold book could not trade.

The 2021-2023 pattern is the opposite and equally interesting: its edge is entirely in the second
half, so an era's *sign* is not stable even when it has no internal flip.

## Consequence for every downstream consumer

Any spread quoted from E34-E44 must be read with two labels attached: the warm/cold convention
(E45, up to 166bp) and where inside the era it was earned (this face, up to 595bp). The
E43-E44 robustness grid quotes month-end cells on 2020+ windows; the mid-month cell that loses
the most bars to the eligibility block is also the cell most exposed to this decomposition, which
is what E44-MIDMONTH-WEAKNESS should price next.

Descriptive census only: no gate, no verdict, no prereg, no trial count, zero ledger booking.