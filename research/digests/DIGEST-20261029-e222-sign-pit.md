# E222 — the six factor directions were chosen with hindsight, and the honest book is negative (r1335 bm-c)

**Card:** E222 in `knowledge/METHODOLOGY_ASSETS.md`.
**Artifacts:** `results/etf_sign_pit.json` (re-emitted every chain run by the new
`etf_sign_pit` leg) + the new first caveat on `results/etf_book_production/CARD.md`.
**Code:** `scripts/etf_sign_pit.py` — `ic_table / pit_signs / ic_persistence / score_face /
gate`, selftest 15/15; card caveat wired through `sign_pit_support()` in
`scripts/etf_book_production.py`.

## The question nobody had priced

Every published number on this line (9.13%/yr, OOS 15.2%, the card, the ticket, the forward
ledger) comes out of one score face, and that face takes its six factor directions from a
hard-coded block:

`mom_12_1 +`, `price_position +`, `drawdown_60 +`, `adx_14 +`, `vol_60 −`, `intraday_range −`.

Those signs are not a theory. Measured on this panel they are **exactly** the full-sample
IC signs — all six:

| factor | full-sample IC | sign used | matches |
|---|---|---|---|
| mom_12_1 | +0.0609 | + | yes |
| price_position | +0.0775 | + | yes |
| drawdown_60 | +0.0285 | + | yes |
| adx_14 | +0.0446 | + | yes |
| vol_60 | −0.0549 | − | yes |
| intraday_range | −0.0408 | − | yes |

So the direction of every factor was read off the whole 2020-2026 sample before the
backtest that quotes 2020-2026. Path tests (E188/E199/E203) test *the arm*; none of them
tests the sign, because the sign sits above the arm.

## What was measured

Same six factors, same engine (`fast_next_open`, next-open fills), same costs (10bp/side),
same width (12 names), same cadence (20 bars), same window. Only the signs differ.

**fixed** = production `SIGNS`. **pit** = each factor's direction from windows that had
already finished by that decision date (trailing mean IC over the last 12 decision windows,
require ≥4 closed windows, |mean IC| < 0.02 = the factor is dropped for that date rather
than given a direction).

| arm | CAGR | Sharpe | maxDD | turnover/decision |
|---|---|---|---|---|
| fixed (production signs) | **+6.14%** | **0.645** | −12.84% | 1.17 |
| pit (trailing-IC signs) | **−10.81%** | **−0.407** | −67.45% | 1.51 |
| reversed trailing sign (exploratory) | −0.09% | 0.115 | −43.39% | — |
| equal-weight eligible (no sign at all) | +1.92% | 0.200 | — | — |

Both halves lose for the pit arm (`is_2020_2023` −10.02%/yr, `oos_2024_plus` −11.97%/yr), so
this is not an early-learning artefact. Verdict, recomputed by the gate from the payload:
**`signs_in_sample`**, and it holds in **all five** sensitivity cells — IC floor 0.01/0.02/0.05
(−11.00 / −10.81 / −8.79%) and lookback 6/12/24 windows (−4.59 / −10.81 / −4.37%). The wider
lookbacks matter: they kill the obvious defence that a 12-window IC is simply too noisy an
estimator.

## Why it fails — the sign does not carry forward

Measured directly, per factor, no engine involved: correlation between the trailing mean IC
(the number the rule trades on) and the IC of the next window, plus how often the sign flips
window to window.

| factor | carry_corr | sign_flip_rate | pit sign == production sign |
|---|---|---|---|
| mom_12_1 | −0.058 | 45.5% | 67.1% |
| price_position | −0.021 | 48.1% | 76.0% |
| drawdown_60 | +0.023 | 41.6% | **39.2%** |
| adx_14 | **−0.222** | 48.1% | 64.6% |
| vol_60 | −0.028 | 49.4% | 54.4% |
| intraday_range | −0.021 | 50.7% | 48.1% |

Mean carry 0.054 in the *wrong* direction, mean flip rate 47% — a coin. `drawdown_60` is the
sharpest case: the production sign is right 39% of the time, i.e. the trailing data said the
opposite two times in three, and the published sign is the one that only worked out over the
whole sample. Note the reversal result: flipping the trailing sign is worth −0.09%/yr, not
+10pp — the trailing IC is not anti-predictive either, it is **uninformative**, and an
uninformative direction on this factor mix picks worse names than not selecting at all
(equal weight +1.92%). That distinction is the whole finding: the sign is a property of *the
period*, not of the factor, so it cannot be chased in either direction.

## Consequence for money

- The published headline is a statement about **which period the book was priced on**, not
  about a rule a live operator could have run. That caveat now travels as the **first caveat
  on the production card**, derived from this artifact, not retyped.
- It does not say the book is worthless; it says the book's edge is not yet separable from
  one sign choice. A defensible live claim needs a sign rule frozen **before** the sample —
  e.g. an economic prior per factor, or a sign fixed per regime with a frozen test — which is
  a preregistered job, not this face.
- The one thing that is now *measured* rather than argued: reverse-engineering the signs from
  the recent past is worse than equal weight, so "just adapt the signs" is not a fix.

## Caveats on this face

- Reference engine only: no impact cost, no gap risk, flat sizing. The vol target/beta overlay
  is deliberately out — the sign question is orthogonal to sizing, and both arms are sized the
  same. (Hence the fixed arm's +6.14% sits below the card's overlay headline of 9.13%: it is
  the same book with no sizing rule.)
- One sign estimator family (trailing mean IC on the decision grid). Five cells are published;
  a materially different estimator was not tried.
- ETF pool is today's listed set — unchanged survivorship caveat, unaffected by this face.
- `L8` in the selftest pins the construction: with the SIGNS held constant this face
  reproduces `etf_composite_pf.build_score` to max|diff| = 0.0, so the A/B gap is the signs and
  nothing else.