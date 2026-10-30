# DIGEST-20261030-r1282-e255-band-draw-starvation

**Study** E255 — is the undetermined band exponent starved of DRAWS or of RUNGS?
**Runner** `scripts/e255_band_draw_starvation.py` (run / selftest 15/15 / verify) · **Face** `results/state_tilt/BANDDRAW-2026-10-29.json`
**Verdict** `exponent_clears_on_draws_alone` (both families clear the frozen 0.80 r2 floor inside the measured draw grid)

## What was asked

E254 rebuilt the shuffled band inside `era_2025_now` at seven session counts and could not name an
exponent: HEAD fitted r2 0.67 against the frozen 0.80 floor, and a 3-rung re-read at 200 draws gave
HEAD 0.200 while TAIL stayed 0.758. Two readings survived and they cost very different things — too
few permutation draws (more draws buys it) or too few rungs on 408 sessions (only a longer window
buys it). The card asked for the endpoint spread as a function of draws at a FIXED rung set, the
propagation into gamma's scatter, and the draw count at which the floor is cleared — or the
statement that no count does.

## What was done

The same seven rungs (n = 100/150/200/250/300/350/408) are measured at 60/120/240/480 draws, in the
two families E254 used (HEAD = first n sessions, TAIL = last n). The four ladders are ONE experiment
read four ways: `random.Random(seed)` emits the same shuffle sequence whatever the loop length, so
each draw stream is generated once at 480 per seed and every smaller count reads its own PREFIX
(selftest leg 1 pins this). Three seeds per rung, star pinned to the whole-era name, no coefficient
re-priced, no bootstrap.

Two scatter sources are published per (family, draw count): `gamma_sd_seed` (the Monte-Carlo part
that more draws should shrink) and `gamma_se` (the regression's own slope SE, which draws cannot
touch). The frozen verdict compares them only when no measured draw count clears the floor.

## What it says

- **The floor is cleared by draws, in the grid.** r2 by draw count — HEAD 0.539 / 0.647 / 0.679 /
  **0.890**; TAIL 0.697 / 0.689 / 0.822 / **0.933**. `draws_needed` = 480 (HEAD, the grid's top) and
  240 (TAIL). E254's "undetermined" was therefore at least partly a draw-starvation artefact, not a
  missing-rungs problem.
- **But draws move the LEVEL, not only the noise.** The band's endpoint is a 5% quantile, and a
  quantile read off too few draws sits inside the true boundary. At n = 408 the edge is 0.4549 at 60
  draws and 0.6255 at 480 (+37.5%); the rise from 240 to 480 is still positive in 6 of 7 rungs in
  both families (median +9.8% HEAD, +11.7% TAIL; +21.1% / +34.5% against the 60-draw read). So
  `endpoint_converged = false` at 480 draws — more draws will keep widening the band.
- **The exponent has not converged either.** gamma drifts down with draws (HEAD 0.3481 / 0.3366 /
  0.3026 / 0.3155; TAIL 0.6468 / 0.5947 / 0.5822 / 0.5855) and both families are still falling at
  the top of the grid, so the honest statement is a direction, not a value.
- **E254's rule, re-applied to the converged ladder, still refuses — for a different reason.** At 480
  draws both ladders are straight, but HEAD 0.3155 vs TAIL 0.5855 is a gap of 0.270, 2.7x the frozen
  0.10 tolerance, so `exponent_undetermined_inside_the_cell` survives with the reason "families
  straddle the line" instead of "r2 below floor". Straightness was the symptom; the ladder not being
  one object is the cause.
- **E253's session target was computed on a starved band and is optimistic.** With the 480-draw edges
  and each family's own converged exponent, the inversion asks for **1055** sessions (HEAD) / **681**
  (TAIL) against 408 available — versus E253's 516 and E254's 434 / 420. Every one of those earlier
  numbers understates the wait, because the band they divided by was too narrow.
- The seed scatter does **not** fall with draws (HEAD 0.0439 / 0.0393 / 0.1717 / 0.1894; TAIL 0.2845 /
  0.1417 / 0.1366 / 0.1411), so `mc_over_fit` (3.81 / 2.01) is published as a flag, not as a ratio:
  three seeds is a two-degree-of-freedom estimate and it is itself noisy.

## Defects found and fixed in-window

1. The face's own `_summary` read a key (`families`) that the face no longer carried — every function
   selftest was green while `run` died. Caught by running the pair (`selftest` then `run`) rather than
   the selftest alone.
2. `extrapolate_draws` refused a two-row table ("fewer than three draw counts") although the 1/D model
   it fits has one parameter, and it computed a target below the measured top instead of first asking
   whether the top already clears; the fixtures for the "reaches" and "out of budget" branches were
   both wrong (one already cleared, one landed inside the budget). All three fixed and pinned by legs
   8-10.
3. The first cut of the deliverable stopped at the r2 verdict. That sentence is true and useless on its
   own: it says the ladder is straight, not that the band is measured. The convergence table
   (rung-by-rung rise, `endpoint_converged`) and the target re-inversion were added because the
   load-bearing finding is the level shift.

## Not done

No bootstrap, no bill, no adoption, no re-pricing of any coefficient; the window is not extended (408
sessions is all `era_2025_now` has, and extending it is exactly what this face says is unavailable).
Draw counts above 480 were not measured. GPU untouched (parked, C-20261014-01); cloud untouched; no
cleanup or quarantine action.