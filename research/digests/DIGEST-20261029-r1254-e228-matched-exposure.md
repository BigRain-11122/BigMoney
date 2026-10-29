# E228 -- the drift split was never a biased benchmark, it was an undetermined one

**Round** r1254 (bm-b) · **evidence_cutoff** 2026-10-28 · **face**
`results/state_tilt/MATCHED-2026-10-28.json` · **card** E228

## The question the card asked

E226 noticed that E225's drift split can hand a losing rule a positive residual: on the
equal-weight basket `binary_low` showed **+340 bp/yr** of `gate_specific` beside **+1.8 bp/yr**
of actual excess. The card asked whether that survives replacing the attribution with a
traded benchmark -- a flat arm held at the gated arm's own average weight, charged the same
toll -- and **how many arms change sign** between the two.

## What was built

`scripts/e228_matched_exposure.py` (run / selftest, **22 hermetic legs**) rebuilds E225's
per-decision rows (and pins that they reproduce the published annualised excess to 1e-9),
then prices two arms on one index set:

* **gated** -- the E225 weight series, unchanged;
* **matched null** -- a flat arm at the gated arm's own average weight, same `mu_is`, same
  `|dw| x 13.041bp` toll, `w_{-1} = 0`.

The measurement is the **paired daily difference** `d_t = excess_gated(t) - excess_matched(t)`,
summarised over the out-of-sample window with a Newey-West t (lag 20), an i.i.d. t beside it,
an effective sample size, and a minimum detectable effect. Bar = Bonferroni 5% over
4 gated arms x 2 panels = **2.7344**. Three matched constants are published because they
answer different questions: `is` (frozen at the split -- the only causal one), `oos` (exact
exposure match -- it looks at the answer, so it is a diagnostic), `full`.

## The reading

**The two benchmarks are one number.** On all 8 gated cells the E225 attribution and the
traded benchmark differ by **0.0 bp/yr** (max and median both 0.0) -> **0 of 8 sign changes**.
That is not luck, it is algebra, and the face states the identity:

> attribution - pair == -(matched arm's own out-of-sample toll)

A constant weight trades **once**, at entry, so its out-of-sample toll is exactly `0.0`
(measured: `cost_bp_per_year_oos = 0.0` on every matched arm). The drift split is therefore
the exposure-matched benchmark already -- what E226's worry named correctly was not bias but
**underdetermination**: the published residual had no standard error at all, and the paired
series is what supplies one.

**Exposure for exposure the tilt is dead at every arm.** 0 of 8 cells survive:

| panel | arm | gated | matched(oos) | pair bp/yr | t | MDE |
|---|---|---|---|---|---|---|
| single sh510300 | binary_low | -1081 | -558 | **-524** | -1.69 | 867 |
| single | tilt_step | -1466 | -829 | **-637** | -2.06 | 865 |
| single | tilt_linear | -1566 | -863 | **-704** | -2.15 | 918 |
| single | voltarget | -1722 | -1522 | **-200** | -1.99 | 283 |
| basket | binary_low | +2 | -217 | **+218** | 0.71 | 857 |
| basket | tilt_step | -487 | -304 | -182 | -0.57 | 889 |
| basket | tilt_linear | -483 | -311 | -172 | -0.53 | 908 |
| basket | voltarget | -967 | -571 | -396 | -2.61 | 426 |

The single best case for the tilt is the basket's `binary_low` at **+218 bp/yr, t = 0.71
against a bar of 2.73** -- and its own MDE is 857 bp/yr, so this test length could not have
resolved anything smaller than that either way.

The +340 / +218 pair resolves cleanly: E226's +340.08 was gate-specific **at zero cost**,
E225's +218.42 is at the model cost, and the difference **121.66 bp/yr equals the gate's own
out-of-sample toll 121.658** exactly. A gate that trades 9.3 turnover units a year against a
flat arm that trades once is paying for the privilege of being measured.

## Pits caught in-window

1. **The first version of my invariance leg was wrong, not the code.** I asserted that adding
   a constant to every return leaves the amount unchanged. It left *both* levels unchanged,
   because both arms are measured against the same `mu_is` and that estimate shifts with the
   data. The honest invariance is narrower and is the point of the card: a shift applied
   **only after the split** leaves the `oos`-matched pair untouched (`mean(w_t - c) == 0` by
   construction) while both levels move by their own exposure -- and the `is`-frozen constant
   leaves exactly the residue `k * (avg_w_oos - c_is) * 252` the mismatch predicts
   (76.3636 vs 76.3636 measured). One leg, two different benchmarks, both pinned.
2. **A zero that is a property, not a measurement.** Reporting "0 of 8 sign changes" without
   the identity would read as an empirical agreement that might break next quarter. It cannot
   break while the null arm stops trading after entry -- so the face publishes the identity
   and numbers where it would stop holding (any benchmark that rebalances).
3. **The basket's first session has no return, so its flat arm is never charged its entry.**
   `turnover_total` came back 0.0 against a constant of 0.327, and my own first assertion read
   that as a defect. It is not: the entry side lands on a skipped row for the gated arm too, so
   the pair stays comparable -- but the difference is now published as `entry_charged` beside
   the constant instead of being left for a reader to trip over. An uncharged entry is an
   unmeasured one, not a free trade.

## Pieces

* `scripts/e228_matched_exposure.py` (run / selftest 22/22)
* `results/state_tilt/MATCHED-2026-10-28.json` + `matched_latest.json` + `matched_by_arm_2026-10-28.csv`
* S6 leg `matched_exposure` immediately after `tilt_breakeven`
* smoke leg: re-derives every paired MDE from its own SE, refuses a matched arm that trades
  more than its entry side, refuses an attribution gap that is not the matched toll, refuses
  a survivor below the bar
* `knowledge/METHODOLOGY_ASSETS.md` card E228