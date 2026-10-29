# DIGEST 2026-10-29 r1252 bm-b -- E225: a continuous weight buys sessions, not resolution

Study: `scripts/e225_state_tilt.py` (run / selftest, 18 hermetic legs)
Face: `results/state_tilt/TILT-2026-10-28.json` + `latest.json` + `by_arm_2026-10-28.csv`
Card: `knowledge/METHODOLOGY_ASSETS.md` E225
Chain: S6 leg `state_tilt` (after `vol_gate`), smoke leg *the state tilt publishes its own
effective sample size*

## The question

E224 rejected a volatility state gate and closed on a cap, not a finding: a hold of H
sessions limits a gate to 252/H independent episodes a year, so no sampling rate can raise
the count. It named the successor the accounting does not throttle -- a continuously-held
tilt, weight varying with the state, no per-episode round trip.

E225 keeps the signal and the toll identical to E224 and changes only the accounting:

| | E224 | E225 |
|---|---|---|
| weight | 0 or 1, locked H sessions | any value in [0,1], decided every close |
| cost | two sides per episode | one side per unit of |dw| (w_{-1}=0) |
| independent unit | episode | session, discounted to n_eff |

Five arms on one signal: `always_on` (null), `binary_low` (E224's shape, daily rebalanced),
`tilt_step` (1/0.5/0), `tilt_linear` (1 at the low threshold, 0 at the high), `voltarget`
(w = clip(IS-median vol / v, 0, 1)).

## The reading

sh510300, 3,503 sessions to 2026-10-28, split 2021-01-13, 1,401 OOS decisions, 10-test
Bonferroni bar.

**0 of 5 primary arms and 0 of 5 basket arms adopt.** But the verdict is the least
interesting number here.

1. **Daily reweighting does escape the cap.** n_eff = 1,363 of 1,401 sessions = 97%. The
   excess series is nearly independent at daily frequency, exactly as the design intended.
2. **And the annual bar gets worse anyway**: 1,006bp/yr against the episode lock's 811 --
   a 0.81x move in the wrong direction. More independent observations, worse annual
   resolution. A fractional weight spreads the same signal over more observations at lower
   amplitude, so per-observation dispersion falls by less than the count grows, and the toll
   is charged per unit of weight change (`binary_low`: 11.0 turnover/yr = 199bp/yr), which
   the episode lock pays once per hold instead.
3. **The null arm prices the drift, so a gated arm's excess is not a verdict on the gate.**
   `always_on` (w=1, zero turnover) reads **-1,628bp/yr**: the out-of-sample drift sits below
   the in-sample drift the face normalises to. Charging each arm that deficit by its average
   exposure leaves the gate-specific residual:

   | arm | avg w | drift component | gate-specific | cost/yr |
   |---|---|---|---|---|
   | binary_low | 34.3% | -558 | **-524** | 199 |
   | tilt_step | 50.9% | -829 | **-637** | 182 |
   | tilt_linear | 53.0% | -863 | **-704** | 169 |
   | voltarget | 93.5% | -1,522 | **-200** | 26 |

   The tilt genuinely lost money beyond the drift, and the smallest loss is the arm that
   traded least (2.8 turnover/yr), not the one that timed best. That is the shape of a
   rule whose cost is its design.

## What carries forward

Any continuously-held overlay must publish (a) n_eff beside its session count, or "more
data" is an assumption; (b) the null arm's excess as the drift deficit; (c) `gate_specific =
excess - avg_weight x null_excess`, or a market-wide drift miss gets read as a verdict on
the rule.

## Pit found in-window

A HAC leg whose fixture is a sawtooth carries negative lag-1 correlation and fails the
"Newey-West >= i.i.d." assertion the method needs -- the fixture noise has to be white
(small LCG) before that leg means anything. Second trap: the causality leg must perturb
returns strictly *after* the inspected index, because the signal at t already contains the
return of t; perturbing from t itself makes a correct implementation look broken.

## Named successor

E226 (seeded ready): breakeven toll for the tilt -- the gate-specific residuals are all
negative, but whether the rule is wrong or merely expensive is one monotone sweep in cost,
not a new study.