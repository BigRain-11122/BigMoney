# E236 digest -- the operator picks a vector, not six IC signs, and that procedure earns nothing

r1345 bm-c · script `scripts/etf_sign_pit_combo.py` (selftest 18/18) · face
`results/etf_sign_pit_combo.json` · card E236 · chain leg `etf_sign_pit_combo` · smoke leg
"E236 the sign-vector re-selection procedure is priced".

## The hole this closes

Three chain legs already answer "were the six signs knowable?" -- `etf_sign_pit` (E205)
re-signs each factor from its own trailing IC and earns **-10.81%/yr** against the published
**+6.14%**; `etf_sign_enum` (E208) prices all 2^6 vectors on one window and finds the
published vector **rank 6 of 64** (median arm -1.76%/yr); `etf_sign_cells` (E227) shows only
two directions keep their sign across cells.

None of those is the operator's actual alternative. An operator does not sign six factors
independently off an IC table. The operator **picks one vector out of the 64 and runs it.**
That is the only procedure by which this line could be shipped without hindsight, and it had
never been priced.

## What was measured (declared before any file was read)

Two cells (R20xN12, R20xN5), 64 vectors each through the same reference engine, then a
walk-forward arm: every `reselect` bars rank the 64 by realised Sharpe over the trailing
`lookback` bars **strictly before** that date, take the winner, apply its own causal return
path for the next `reselect` bars. 3 reselect x 2 lookback = 6 variants per cell = 12 declared
tests. Control = equal weight over the whole eligible universe at the same cadence.

| arm | R20xN12 | R20xN5 |
|---|---|---|
| equal-weight control | +1.66% (Sharpe 0.185) | +1.66% (0.185) |
| PROD vector (oracle, in-sample) | +6.14% (0.644) | +7.86% (0.809) |
| BEST of 64 (oracle, in-sample) | +8.50% | +12.82% |
| PIT re-selection, 6 variants | -9.9% .. +0.6%, median **-4.3%** | -11.0% .. -3.8%, median -5.2% |

**0 of 12 variants clear the control + 1pp. 1 of 12 is positive. Median gap to control
-6.52pp/yr.** Verdict recomputed by the gate: `pit_combo_no_value`.

## The number that matters more than the CAGR

At every selection event the chosen vector's forward mean return is compared with the mean
across all 64 valid vectors. That "selection lift" is **a coin flip**: it is positive in
40-67% of events (median variant 0.50) and its size flips sign across variants
(-4.8e-4 .. +2.2e-4 per bar). A rank-1 trailing Sharpe earns, on average, what the mean
vector earns. Twenty-four events choose **13 distinct vectors**; five events choose four.

So the loss is not a bad rule, it is an empty one: on this panel trailing Sharpe carries no
information about next-quarter relative performance among sign vectors. The PIT book bleeds
the 10bp/side toll of switching plus the PIT arm's own turnover, which is exactly why
`S60` (most switches) is the worst variant in both cells (-9.9% / -5.8%).

## Consequence for the published book

* The published +9.13%/yr headline is a **full-sample reading with no live counterpart**.
  Both honest PIT procedures now agree: per-factor IC signs -10.81%/yr (E205), per-vector
  re-selection -4.86%/yr median (this face), equal weight +1.66%/yr. The card may quote the
  in-sample number only beside this face.
* The in-sample optimum shares only **three of six** signs with the published vector
  (`price_position` +/-, `adx_14` +/-, `intraday_range` -/+), so "rank 6 of 64" is not a
  near-best vector either -- it is a mid-pack member of a hindsight table.
* What survives unchanged is what the last two rounds already isolated: the vol-target /
  cash-ladder / width machinery is a risk-shaping layer and does not depend on which signs
  the score uses; the alpha claim does.

## Honest limits

- Both oracle arms are in-sample (their signs were read off this panel); only PIT arms could
  ever support a live claim, and they lose.
- PIT here re-selects a **vector**; E205 re-signs each **factor** from its own IC. Different
  procedures, not interchangeable numbers.
- Selection statistic is trailing Sharpe only -- no other statistic was swept, so the 3x2
  variant grid is a declared grid, not an optimised surface.
- Reference engine, 10bp/side, no impact/gap; the control runs the same engine and cadence,
  so the comparison is paired (it is not a claim about live trading costs).
- One panel, one cost level, survivorship pool: unchanged caveats.