# DIGEST 2026-10-30 r1277 (bm-b) — E251: what survives of the star column once the book aggregate is gone

Face: `results/state_tilt/STAROWN-2026-10-29.json` (+ `starown_latest.json`)
Runner: `scripts/e251_star_own_component.py` (selftest 18/18)
Card: `knowledge/METHODOLOGY_ASSETS.md` E251

## The question

E250 left exactly one number standing: with the book's leave-one-out aggregate turnover in the row,
every non-star column lost 60–130% of its lag-1 coefficient, and the star (`sh588000`) kept 90% of
its −0.805. That residual was the only sleeve-attributed piece of the E248/E249 reading that E250
did not take away.

## Read

| model | headline star b1 | share of the residual taken |
|---|---|---|
| D0 baseline (LOO aggregate in the row) | **−0.72504** | — |
| D1 + star's own lagged \|move\| | −0.73008 | **−0.0070** |
| D2 D1 + member age (days) | −0.73005 | −0.0069 |

* The residual is outside its own 200-draw shuffled band `[−0.2228, +0.2357]`.
* The drop the volatility term produces is **−0.00504**, inside the band of drops that the same
  term produces when it is shuffled in time `[−0.00888, +0.01343]` → it explains nothing.
* Verdict **`residual_is_own_turnover`**, stable in all four cells where a star exists:
  era 2023–2024 −0.833, era 2025–now −0.911, early-three (star `sh510050`) −0.494.
* Two cells are `unresolved_too_few_rows` **because no member was named star there**
  (`pre2020_four`, `era_2020_2022`), not because a fit failed.
* Age is published as **not identified** in one window: the star's age correlates 0.99998 with the
  row index, so its fitted coefficient (−2.5e−6) is a time trend wearing an age label. The only
  readable age statement is the cross-member gradient (residual vs age at mid, corr 0.794) and that
  is `decided: false`, n = 5 — descriptive, deliberately not a decision.
* The volatility coefficients themselves are all small and positive (0.027–0.044): the star's own
  preceding move does not price anyone's next move in this design.

## Three reusable findings

1. **A decomposition of a different number is not a decomposition.** The decomposition had to be
   performed on E250's published `b1_with_loo_aggregate`, and the two faces agree to 0.0
   (−0.7250430277727764 both sides) — pinned in the smoke leg to 1e−9, and the star naming was
   refactored into one shared function (`e250.name_star`) instead of being re-typed, because a
   copied star rule that drifts silently answers about a different sleeve.
2. **An addition must clear its own null.** "b1 fell when I added X" is not evidence unless the
   drop beats the drops produced by shuffling X in time. Here the observed −0.005 sits *inside* the
   shuffled-drop band, so the honest reading is "volatility takes nothing", not "small effect".
3. **Age inside one window is a row index.** A member's age is monotone in t within a window
   (corr 0.99998), so it cannot be separated from any other slow trend; publish `age_identified:
   false` and read age only cross-sectionally, where n = members and the result is descriptive.

Fixture lesson (cost: one red leg, no re-burn): the volatility fixture must write its truth in the
coordinates the design uses. The first version built the driver as `|0.7·dx_star + noise|` — an
absolute value of a small, noise-dominated series — so the proxy link to the star's *turnover* was
too weak, the base coefficient collapsed to 0.005, and the face correctly said
`residual_inside_shuffled_band`. Rewriting the fixture with the star's own exogenous move series
(`|dy_star|`) and its turnover built as `0.6·|dy_star| + noise` reproduced the intended branch.

## Not run / untouched

GPU parked (C-20261014-01; ~0 GB reserved for this face), no cloud calls, nothing deleted, no
quarantine. bm-a/bm-c lane collectors untouched. No bill, no adoption, no re-pricing: this face
names a channel and prices nothing.