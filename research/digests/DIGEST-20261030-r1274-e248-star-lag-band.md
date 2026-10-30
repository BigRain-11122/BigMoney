# DIGEST 2026-10-30 r1274 bm-b -- E248: the sign flip was a coefficient read against a model

Card: `knowledge/METHODOLOGY_ASSETS.md` E248. Runner `scripts/e248_star_lag_band.py`
(selftest 14/14, ~8s for the whole face). Face `results/state_tilt/STARLAGBAND-2026-10-29.json`
(+ `starlagband_latest.json`). S6 leg `star_lag_band` (after `era_power`), smoke leg added.

## What E246 claimed, and what was missing

E246 read the star column at three lags -- +0.769 / -0.527 / +0.397 -- and published the verdict
`star_flow_leads_with_sign_flip`. Two holes: it stopped at lag 2, so a two-session oscillation
and a coefficient that decays into noise look identical at two points; and each coefficient was
compared with its own **HAC interval**, which is a model, not the design's null. On a persistent
series the model is exactly what the question is about.

## What this face did

The row is extended to lags 1..5, all in **one** regression per member (own turnover plus the
star's turnover at lags 0..5, so each lag is a partial effect rather than a re-read of the
contemporaneous column), and every reading is decided against a **200-draw permutation band**:
the star's turnover series shuffled in time, same design, same members, same row count.

The band is **family-wise**: five lags are screened at once, so a lag must beat the largest
|coefficient| any shuffled draw produced anywhere in lags 1..5. Measured necessity, not taste --
the first draft used a per-lag 95% band and a pure-noise fixture crossed it at lag 5 in one
screen out of four.

## Reading (13,911-row common grid, star sh588000 by E245's own rule)

Lag column: **lag0 +0.653, lag1 -0.586, lag2 +0.091, lag3 -0.204, lag4 +0.077, lag5 +0.027.**
The family-wise line is 0.351. **Only lag 1 crosses. Nothing else does, at any lag, in any cell.**

Across the six cells lag 1 is negative and crosses in five of six (era_2020_2022 is the one cell
where even lag 1 lands inside its 0.453 line). Lag 2 -- the coefficient E246 published as the
rebound at +0.397 -- never crosses anywhere (0.09 / -0.17 / 0.09 / 0.02 / 0.22 / -0.18 against
lines of 0.35..0.66).

So E246's "the star leads, but the sign alternates" collapses into a smaller, sharper object:
**one negative lead at one session, and no rebound outside the design's own noise.** The
frozen four-name vocabulary does not carry that shape (it is neither a period-2 oscillation --
lag 2 is nowhere near half of lag 1 -- nor a monotone decay across five lags), so the published
verdict is honestly `band_without_shape` in five cells and `inside_permutation_band` in one, with
a **post-hoc** descriptive label `single_lag_lead_no_rebound` published beside it and explicitly
not in place of it.

The direction is still real and it is still negative: a spike in the star's turnover is followed
by *smaller* moves in the other sleeves. That is a bounce/absorption signature, not a source, and
it may not be billed to that sleeve as a one-way channel.

## The two-session sum

Same row on a two-session sum of increments, read with **disjoint** windows (stride 2) so
overlapping observations cannot manufacture structure. In the headline cell the summed row
crosses at lag 2 only (`oscillation_survives_two_session_sum = false`) -- i.e. the summed design
does not reproduce an opposing pair. A control leg on a no-signal panel asserts the disjoint row
fabricates nothing either, so the flag is a statement about the data rather than about
arithmetic.

## Three traps this face pins

1. **A per-lag band is not a screen.** Five columns at 95% is a discovery machine. The family-wise
   line (max |coefficient| over the draws, anywhere in 1..5) is what makes one crossing mean
   something.
2. **More lags change the partials.** Going from lags {1,2} to {0..5} in one regression moved lag 2
   from +0.397 to +0.091 -- the "rebound" was carrying the lag-3 coefficient. A distributed-lag
   row is only comparable to another row with the same lag set.
3. **A frozen vocabulary must be allowed to fail.** The data's shape (one decaying negative lead)
   is not in the four names. Publishing the closest name would have been the dishonest option;
   naming the shape post-hoc, labelled as post-hoc, is not.

## No bill

Shape only. No adoption, no re-pricing, and a period-2 oscillation (were one found) may not be
billed to the star as a one-way flow.