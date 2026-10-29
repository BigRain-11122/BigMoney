# E229 -- the pair, split three ways: which days, how much, and the toll

Round r1255 · bm-b · evidence cutoff 2026-10-29 · pool card
`E229-TIMING-VS-SELECTION-DECOMPOSITION`

## What the card asked

E228 gave the paired timing value a standard error for the first time (single sh510300
panel: -520..-710 bp/yr, basket `binary_low`: +227 bp/yr at t=0.72) but never asked where
the number comes from. A gated rule differs from a flat arm two ways: it is in the market
on different days, and on the days both are in, it holds a different amount. The card is
one sentence about the difference between "the gate cannot time" and "the gate picks days
but sizes them wrong".

## The decomposition (an identity, not a new study)

With `c` = the gated arm's own OOS average weight (E228's exact exposure match),
`mu_is` = the in-sample drift the arms are charged, per OOS session `t`:

```
d_t = (w_t - c)(r_t - mu_is) - cost_t
    = 1[w_t = 0] * (-c)(r_t - mu_is)        selection  (which days)
    + 1[w_t > 0] * (w_t - c)(r_t - mu_is)   sizing     (how much)
    - cost_t                                toll
```

Sizing in turn splits exactly into a LEVEL term (`n_in·m_w·m_r`, the gate's in-market
average weight sitting away from `c`) and a COVARIANCE term (holding more when the return
is above the drift). All three reconstruct the pair to 2.0e-12 bp on every cell, and the
face reproduces E228's own published pair to 0.0 bp on all 8.

## Numbers (OOS, 1,402 single-panel / 2,108 basket sessions)

Single panel, sh510300 (bar_arm 2.73, bar_channel 3.08):

| arm | pair | selection | sizing | toll | dominant | t |
|---|---|---|---|---|---|---|
| binary_low | -520 | **+261** | -580 | -202 | sizing | -2.48 |
| tilt_step | -638 | -30 | -425 | -183 | sizing | -2.44 |
| tilt_linear | -710 | -31 | -510 | -169 | sizing | -2.48 |
| voltarget | -201 | 0 | -175 | -26 | sizing | -1.74 |

Equal-weight basket (5,269 sessions, split 2018-02-14):

| arm | pair | selection | sizing | toll | dominant | t |
|---|---|---|---|---|---|---|
| binary_low | **+227** | **+265** | +83 | -122 | selection | 1.32 |
| tilt_step | -183 | -83 | +27 | -127 | toll | **-10.03** |
| tilt_linear | -170 | -85 | +49 | -135 | toll | **-10.05** |
| voltarget | -394 | 0 | -344 | -49 | sizing | -2.28 |

## What it says

1. **The one gate that dodges correctly does it for the wrong reason to count.** The days
   `binary_low` sits out average **-4.61 bp/session** (single) and **-4.79** (basket)
   against the drift, so its selection channel is the only positive one (+261/+265 bp/yr)
   -- but at t=1.26/1.32 it is nowhere near the 3.08 bar. E228's single positive cell is a
   right-signed, unresolved selection effect, not sizing skill.
2. **The tilt family dodges the *wrong* days.** `tilt_step`/`tilt_linear` sit out sessions
   averaging **+0.72** (single) and **+1.76** (basket) above drift -- it steps aside above
   the mean, which is exactly backwards for a long-only gate.
3. **The only channel that clears the bar is the toll** (`tilt_step`/`tilt_linear` on the
   basket, t=-10.03 / -10.05). What separates these arms from a flat constant is measurably
   the cost of moving, not any timing skill -- consistent with E226/E227, now attributed
   rather than inferred.
4. **A 0/1 gate cannot have a sizing channel.** For `binary_low` the covariance term is
   identically zero (max 6.8e-28 bp/yr) because such a gate holds one weight whenever it
   holds at all; its whole sizing channel is a level shift in average exposure. Any future
   claim of "sizing skill" from a binary rule is arithmetically impossible, and the face
   now says so per arm.
5. `voltarget` never leaves the market (selection identically 0) and its entire pair is
   sizing covariance, negative on both panels: it holds more when returns are below drift.

## Pits

* **Weight index and return index are off by one.** The weight set at `i` covers the return
  at `i+1`, so "sit out session j" is `w[j-1] = 0`. The first version of the construction
  legs picked the wrong sessions and failed both directional legs (selection came out
  negative while claiming to dodge the lowest days); the mirror leg failed the same way.
  Any construction that manufactures a channel must align on the *return* index.
* **An in-sample dodge moves `mu_is`.** Only OOS sessions are dodgeable in a construction
  leg, otherwise the reference drift moves with the trick.
* A 0/1 gate's `(w - c)` is constant on in-market days, so `covariance == 0` to machine
  precision; the smoke leg now refuses a binary arm that publishes a covariance.

## Artefacts

* `scripts/e229_timing_selection.py` (run / selftest, 16 hermetic legs)
* `results/state_tilt/TIMINGSEL-2026-10-29.json` + `timingsel_latest.json`
* `results/state_tilt/timingsel_by_arm_2026-10-29.csv`
* `Tools/s6_chain_bmb.py` leg `timing_selection` (after `matched_exposure`)
* `smoke_test.py` leg re-adding the published channels and refusing a face whose parts do
  not reconstruct its own pair, and refusing a binary arm that publishes a covariance
* `knowledge/METHODOLOGY_ASSETS.md` card E229