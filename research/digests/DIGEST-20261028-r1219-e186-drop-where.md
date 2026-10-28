# E186 — where an arithmetic-dependent drop effect lives in time (r1219 bm-b)

Face: `results/e43_tilt_4member/LADDERDROPWHERE-20261027.json`
Leg: `python scripts/e39_panel_census.py tilt3ladderdropwhere`
Pool row: E186-DROP-EFFECT-REVERSES-WHERE. Cutoff 2026-10-27 (flagged set read
from `LADDERLOMOCOMPOUND-20261027.json`, same cutoff).

## Why this was asked

E183 found four drops whose *effect* flips sign between the summed reading and
the compounded one while every era level keeps its sign. "The effect reverses"
is not actionable on its own: one bad month is a data artefact, a spread is a
property of the arithmetic. So each flagged drop was split into monthly
contributions under both readings.

## Answer

All 4 flagged pairs measured, identity holds: the era-level effects rebuilt from
the month vectors reproduce E183 to **0.000634bp** (published 3dp).

| era | drop | effect sum | effect comp | carrier month | share | eff. months | class |
|---|---|---|---|---|---|---|---|
| pre2017 | sh510500 | +36.58 | −9.66 | 2014-12 (+134.55) | 0.591 | 2.62 | single_month |
| pre2017 | sh510300 | −32.57 | +6.18 | 2016-01 (−71.11) | 0.358 | 5.45 | dispersion |
| 2024_now | sh510050 | +73.16 | −34.01 | 2026-07 (+64.39) | 0.237 | 8.97 | dispersion |
| full | sh510050 | +0.07 | −38.20 | 2014-12 (−95.91) | 0.118 | 25.36 | dispersion |

Three of four reversals are dispersions, not one bad month. The one single-month
carrier (pre2017 sh510500, 2014-12 holding 59.1% of the gap) is a deep-history
month, and the same month is also inside the top-3 gaps of the other two eras —
the early ladder history is where a single date can still carry a verdict.

**No month in any of the four pairs has opposite signs between the two
readings** (`months_with_opposite_sign` empty everywhere). The era-level
reversal is therefore never produced by a month flipping sign: every month moves
the drop's effect the same way under both readings, and the sign at era level is
decided by how the two columns scale the *same* months. That kills the natural
next hypothesis ("find the bad month") and redirects it to the cumulative path.

## The second reading is not the first

The compounded effect published by E183 is the **difference of two annualised
levels**; annualising the ratio of the two growth multiples is a different
number (2.43bp apart on this face, e.g. 2024_now −34.01 vs −31.58). Both are now
published under their own names (`effect_comp_bp`, `effect_comp_ratio_bp`) and a
selftest leg pins that annualising the ratio is not the same object. This is the
r1292 family: one word, two quantities.

## Honest limits

- descriptive census; no gate, no prereg, no trial count
- the flagged set is read from the E183 face rather than re-derived, so a
  missing face yields zero pairs (never an invented set)
- the gap between the two readings is definitional (same month returns under two
  annualisations) and does not shrink with more data

## Next pointer

E189-DROP-CURVE-CROSSING (seeded to the pool): publish the cumulative
delta_sum and delta_link paths per flagged drop, the month where they cross, and
whether removing the carrier month removes the reversal.