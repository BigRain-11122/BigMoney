# DIGEST 2026-10-30 r1259 (bm-b) -- E233: the curvature was assumed, so measure it

Card: E233-EMPIRICAL-GAMMA. Face: `results/state_tilt/EMPIRICAL-GAMMA-2026-10-29.json`.
Runner: `scripts/e233_empirical_gamma.py` (run / selftest, 13 hermetic legs).

## What was asked

E232 swept gamma over 0.75 / 1.00 / 1.25 / 1.50 and found the family's toll *significance*
curvature-invariant while its *size* is not (tilt_linear -247.3 -> -93.2 bp/yr), and found
E230's single passing band dying as soon as the charge turns convex. Both readings are
statements about a four-point grid nobody calibrated: the family has always charged 13.041 bp
per side, i.e. gamma = 1.0 by construction. The card asked for a measured gamma with an
interval, and then for the family verdicts to be re-read at the measured value.

## What was run

Estimand `|r_oc| = k * amount ** gamma` on the in-repo daily panels (r_oc = open-to-close,
amount = session turnover in CNY). Three estimators because the regressor is endogenous:

* **A naive** `log|r_t| ~ 1 + log amount_t`
* **B controlled** `log|r_t| ~ 1 + log amount_t + log|r_(t-1)| + log amount_(t-1)` (primary,
  frozen before reading numbers)
* **C reverse** `log amount_t ~ 1 + log|r_t|` -- published as a diagnostic, never as an estimate

Newey-West HAC (lag 20), 95% interval beta +/- 1.96 se, era edge 2017-01-01 (E190's), two
panels (sh510300, equal-weight basket). Downstream set = {interval lo, point, interval hi}
**plus** the naive estimate, so the family is also asked whether it survives the
identification dispute and not only sampling error. Bar = |t| >= 3.08 (two-sided 5% over
3 arms x 2 panels x 4 gamma points).

## The answer, in three parts

**1. The assumed gamma = 1.0 is inside the measurement -- on this instrument.**
gamma = **0.928 [0.830, 1.026]** on sh510300 over 2012-05-28..2026-10-29 (n=3,455, R2=0.112),
and 0.917 [0.811, 1.024] on the basket. The era split straddles 1.0 rather than sitting on it:
pre-2017 1.079 [0.904, 1.255], 2017+ 0.883 [0.768, 0.998]. So the family's linear charge was
not an arbitrary pick; on aggregate turnover the price response is very nearly proportional.

**2. The dominant uncertainty is identification, not sampling error.**
The naive contemporaneous regression gives 0.255 [0.200, 0.309] -- the same panel, one control
set apart, 0.7 apart in gamma and disjoint intervals. On the basket the naive reading collapses
to 0.003 [-0.026, 0.032], i.e. "turnover tells you nothing about the size of the move", which is
what a simultaneous system looks like when the move is allowed to set the volume. The honest
envelope is therefore **0.255..1.026**, not the sampling interval: an audit that publishes only
the HAC interval would report 0.83..1.03 and would be wrong about how well gamma is known.
The reverse regression (amount on |r|) is reported for completeness and its reciprocal is
**not** an estimate -- 1/0.169 = 5.9, an object with no interpretation, which is exactly why it
is fenced off in the code.

**3. Re-read at the measured gamma: the toll survives everywhere; one band survives the data.**
* Toll channel, 6 of 6 arm cells clear |t| >= 3.08 at every point including the naive one.
  On tilt_linear the toll is -217.3 (lo) / -187.3 (point) / -163.0 (hi) bp/yr on the single and
  -171.9 / -148.9 / -130.1 on the basket, taking the pair from -758.1 to -703.8. Selection
  stays at -31.1 bp/yr exactly, as constructed. The charge bill over the whole path is
  2,406.7 / 2,066.4 / 1,791.4 bp -- the measured gamma sits between E232's 1.00 and 1.25 cells
  and much closer to 1.00, so E232's headline erosion is real but its four points bracketed it
  generously: at the measured exponent the family loses about 16% of its toll over the path,
  not 2.6x.
* Ladder, 12 of 12 cells keep one verdict across the *sampling* interval. The fine scan puts
  E230's single passing band (tilt_linear / band 0.10 x sd_is / sh510300) as BAND_PAYS at
  **every gamma from 0.25 to 1.10** -- its support is far wider than E232's four-point grid
  suggested, and it covers the measured interval with room above it (boundary ~1.10 vs upper
  bound 1.026). The 0.25-band cell on the same arm is BAND_PAYS only at 0.30-0.35.
* 3 of 12 cells flip **only** when gamma is pushed to the naive 0.255, all in the same
  direction (BAND_PAYS appears at low gamma): tilt_linear f=0.25 on the single and f=0.10 and
  f=0.25 on the basket. So those three are decided by where gamma is placed, and that is now
  printed rather than discovered by a reader who is brave enough to try another grid.

## What this does not establish

The bridge is an assumption, stated on the face in `frozen_spec.bridge`: what is measured is
the **market's** elasticity of price to aggregate turnover on this instrument. Treating it as
**our** charge exponent for a weight change follows only if the amount we trade is proportional
to |dw| and our own flow meets the same concavity as everyone else's. Daily bars cannot test
that. And the passing band, however wide its gamma support, is still one cell on one panel;
E231 measured it positive on 12 of 12 paths but clearing the strict bar on only 4 of 12, so
"the direction is data, the size is fragile" is the consistent reading across E231 and E233.

## Pits

1. **A constant regressor does not make X'X singular in floats.** A column of `1e8` gives a
   near-singular matrix that inverts to garbage and yields a confident gamma. The guard has to
   be scale aware: normalise to the correlation form and test its determinant (1e-10), which is
   what the selftest leg now pins.
2. **`e232.channel_rows` publishes the OOS slice, `e228.rows_for` publishes the whole path.**
   The first invariance leg compared row counts and failed for the wrong reason; the honest
   comparison is per-session cost on the index set the two share, with an assertion that the
   slice did not leave the family index.
3. **The interval is not the uncertainty.** One control set moves gamma further than the HAC
   interval is wide, so a face that reports only the interval understates what it does not
   know; the identification span has to be an explicit published point set, and the number of
   verdicts that move inside it has to be counted.