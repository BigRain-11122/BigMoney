# E236 -- can a share-and-difference design settle the granularity question the level regression could not?

Round r1262 (bm-b), evidence cutoff 2026-10-29, face `results/state_tilt/SHAREDIFF-2026-10-29.json`,
runner `scripts/e236_share_difference.py` (selftest 18/18), S6 leg `share_difference`.

## Why the card existed

E235 asked whether a five-sleeve book pays five concave charges or one aggregate charge, and
answered `unresolved_spec_inadequate`: on **levels** two of five sleeves carried a negative own
elasticity, the aggregate turnover level is 0.94..0.97 autocorrelated, and the lagged control
block inverted on 2 of 5 sleeves. That is a statement about the estimator, not about the book.
E236 re-asks the question where the regressors are stationary.

## Three designs, one truth, three different answers

| design | b_own [95%] | b_agg [95%] |
|---|---|---|
| differences (d(share), d(book)) | **0.431** [0.341, 0.520] t 9.43 | **0.879** [0.769, 0.990] t 15.57 |
| frozen_z (share demeaned, level in frozen-half sd units) | **0.017** [-0.004, 0.038] t 1.59 | 0.101 [0.065, 0.138] t 5.43 |
| two_way_fe (member intercepts + date FE) | **0.023** [0.012, 0.035] t 3.93 | absorbed (5,233 date FE) |

Sign agreement holds on both channels -- b_own positive in 3 of 3 readers, b_agg positive in
2 of 2 readers that can see it. Size agreement does not: span 0.017..0.431, ratio **25.4**,
and the difference design's interval is disjoint from both others.

## Verdict

`unresolved_magnitude_disagreement`. No granularity charge is published (only the family's
`linear` model charge is priced for the record), so the family's single exponent stays a
**price without a bill**, and E234's per-sleeve sum is not a substitute for it.

The E235 negative own elasticity does **not** survive -- `negative_survives: false`. What
survives is a name collision: the difference design prices a session against that session's
change in own turnover, which co-moves with the same information arrival that sets `|r|`,
while the cross-sectional designs price the share of book turnover and find almost nothing.
Those are two different quantities, and averaging them would invent a number neither design
supports.

Per member the picture is heterogeneous, which is why the pooled verdict was not read as a
member-level finding: 2 of 5 sleeves are `unresolved_sign_fragile` (sh510500, sh512100), 1 is
`own_dominates` (sh510050), 1 is `unresolved` (sh510300), 1 is `unresolved_magnitude_disagreement`
(sh588000, ratio 12.1).

## Load-bearing lessons

1. **Sign agreement is not size agreement.** Two designs returning +0.43 and +0.017 are not
   "agreed" -- a bill built on the first is 25x the bill built on the second. The gate is now
   frozen into the runner: 95% intervals must overlap across any two identifying designs, and
   the ratio is published beside the verdict. Without it this same data names
   `both_channels_live`, which is what the first burn produced before the gate existed.
2. **A design that cannot see a regressor must say so.** Date fixed effects are collinear with
   a date-common aggregate by construction; the face publishes `b_agg: null`,
   `identifies_b_agg: false` and `absorbed.date_fixed_effects: 5233`, and the agreement test
   scores b_agg over 2 readers instead of pretending to 3.
3. **One observation per cell identifies nothing.** With a single member, within-date
   demeaning removes the share along with everything else. The fit returns
   `identifiable: false`, and a selftest leg pins that a single-member panel never publishes
   b_own. My first fixture hit exactly this and I fixed the fixture, not the code.

## What this round did not do

No arm was re-adopted and no family verdict moved: E226..E235 stand untouched. GPU untouched
(parked, C-20261014-01). Cloud untouched. No cleanup or quarantine action.