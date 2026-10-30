# DIGEST 2026-10-31 r1304 (bm-b) -- E280: a claimed RNG drift that was a calendar difference

## What went red
S6 leg `star_self_price` (E252 verify, E251's published statistic) at r1303:

- E252's face (cutoff 2026-10-29): `cross_row.b_cross = -0.7250430277727764`
- `starown_latest.json` (now cutoff 2026-10-30): `star_residual.b1 = -0.7252014696754883`
- a field diff over the two E251 faces: **177 leaves moved**, including the shuffled band
  (`band_star_lag1.hi` 0.2357 -> 0.3514, width 0.0200 -> 0.0223)

The seeded pool head E280 assumed the r1277 star-rule refactor (`e250.name_star`) had changed how
the shared draw stream is consumed, silently re-randomising a published band.

## What the measurement says
Two independent readings, both exact:

| reading | e251 b1 | e252 b_cross | abs diff |
|---|---|---|---|
| published bytes, same vintage (2026-10-29) | -0.7250430277727764 | -0.7250430277727764 | **0.0** |
| one panel today (1329 sessions), one process | -0.7252014696754883 | -0.7252014696754883 | **0.0** |

So the two implementations are one regression. What differed is the panel: 1328 vs 1329 sessions.
A single extra bar moves the point estimate by 1.6e-4 and a 200-draw max-statistic band by a third.
The refactor never touched the stream.

## Repair applied (rule D1, declared in the runner before measurement)
- `scripts/e252_star_prices_itself.py` verify: prefer `STAROWN-<this face's cutoff>`; when only a
  newer vintage exists, publish `vintage_lag` and do NOT compare coefficients. selftest 21/21
  (new leg: "verify discloses a cross-vintage E251 face instead of calling it drift").
- `smoke_test.py`: the same latent flaw in the E252 product leg, fixed the same way, plus a new leg
  that pins the E280 decision and the draw stream.
- No face reburned, no stream restored -- both repairs offered by the card were unnecessary.

## The pin that outlives the case
The RNG pin is a property, not a number: same (panel, star, draws, seed) reproduces the band,
seed+1 moves it. The first version of the leg was **vacuous** -- with 8 draws `_band` returns
`band=None`, so "same input, same band" was true because neither side had a band. The leg now
requires `measurable` before it can pass.

## Artifacts
- `scripts/e280_e251_rng_drift_repin.py` (selftest 9/9, run publishes the decision)
- `results/state_tilt/STAROWNREPIN-2026-10-30.json` + `starownrepin_latest.json`
- `Tools/s6_chain_bmb.py` leg `star_own_rng_repin`
- `knowledge/METHODOLOGY_ASSETS.md` card E280