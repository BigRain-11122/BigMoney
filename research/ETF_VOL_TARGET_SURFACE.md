# ETF book — is the volatility target a plateau or a spike? (r1270)

The production card (12 names, 20-bar cadence, 10bp/side, next-open) carries a headline
that de-levers on an **8% target computed from a 60-bar realised-vol estimate**. Every
other knob in that configuration has a grid behind it — holdings x cadence x cost
(r1260-r1262), capacity and breadth (r1263), the cash leg (r1268-r1269). These two
numbers never were swept. A single unpriced choice on two axes is the classic shape of a
setting that reads as "tuned" whether or not it is, so this round prices the surface.

**Short answer: the target is a risk dial, the window is load-bearing and 60d sits on a
slope, not a plateau — and the "8% target" actually delivers ~10.2% realised vol.**

## Method

One engine, no copies: every cell is `etf_book_production.backtest`, which is
`etf_robust_pf.open_to_open_equity` with next-open fill. The panel prep was extracted into
`etf_book_production.prep_panel()` so a sweep cannot quietly price a different universe
than the card (class filter + flip repair included). The vol window became a parameter
(`vol_window=60`, default-preserving; selftest pins `maxdiff 0.00e+00` against the legacy
path). Grid: window in {30, 45, 60, 90, 120} x target in {6, 8, 10}%, at the 12-name
production sleeve and at 5 names, 2020-01-02 .. 2026-10-23 (1499 names, 5265 bars).

Raw CAGR **cannot referee either axis**: a higher target mechanically buys more return in
a sample that rose, so a CAGR spread across targets is expected and proves nothing. The
referee is whether the dial changes *risk-adjusted* quality.

## CAGR (%/yr, full window)

12-name production sleeve:

| target | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|
| 6% | 7.80 | 7.64 | 7.24 | 5.87 | 5.47 |
| **8%** | 10.33 | 10.08 | **9.47** | 7.63 | 7.12 |
| 10% | 12.21 | 11.70 | 11.00 | 9.13 | 8.71 |

5-name variant:

| target | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|
| 6% | 9.31 | 9.24 | 8.97 | 7.35 | 6.92 |
| **8%** | 12.03 | 11.95 | **11.49** | 9.75 | 9.26 |
| 10% | 13.31 | 13.20 | 12.81 | 11.03 | 10.71 |

## The two axes are different animals

**Target axis = risk dial.** At the 12-name sleeve Sharpe spreads only 0.024 across 6-10%
(0.980 / 0.978 / 0.956) while CAGR moves 3.76pp and drawdown runs -9.5% .. -12.9%. Return
and risk scale together: 8% is a **preference**, not a fit. Same reading at 5 names
(Sharpe spread 0.081). Nothing to fix here — but also nothing to defend; the card should
say the target is a risk choice.

**Window axis = load-bearing.** Same 8% target, only the estimate length changes:

| book | Sharpe 30d | 45d | 60d | 90d | 120d | Sharpe spread |
|---|---|---|---|---|---|---|
| 12 names | 1.045 | 1.039 | **0.978** | 0.841 | 0.817 | 0.228 |
| 5 names | 1.168 | 1.182 | **1.132** | 1.011 | 1.000 | 0.182 |

Drawdowns at 12 names: -11.9% / -11.2% / -11.8% / -12.4% / -12.2% — i.e. the shorter
windows are not paying for their extra return with more drawdown. The published 60d cell
is a dip between 45d and 30d, and the curve is monotone beyond it. OOS agrees in direction
(12 names: 30d 19.25% / SR 1.78, 60d 18.08% / SR 1.71, 120d 13.06% / SR 1.45).

**Honest limit:** the direction (shorter = better, down to the fastest length tested) is
what the data says, but re-picking the window at 30d on this evidence would be exactly the
fitting this script exists to detect. The finding is recorded, not acted on. What it does
change: the card may no longer imply 60d is the settled/correct value — it is a
convention on a slope.

## The bigger find: the label undershoots its own risk

Realised vol of every cell, against the number in its name:

| target | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|
| 6% | 7.88 | 7.72 | 7.74 | 7.36 | 7.04 |
| **8%** | 10.31 | 10.12 | **10.18** | 9.66 | 9.30 |
| 10% | 12.11 | 12.04 | 12.15 | 11.64 | 11.18 |

(12-name sleeve; 5 names is the same story, 8% -> 10.5%.)

An "8% vol target" delivers **10.2%**, i.e. ~27% more risk than the label, and no window
fixes it. The mechanism is structural, not a bug: `scale = min(1, target / v)` caps at 1.0,
so the overlay only ever de-levers, and the book is sized on the *picked names' backward*
vol — momentum picks are recently calm, then they move. A de-lever is therefore applied
against a low estimate and never catches up inside the 20-bar holding period.
Consequence for anyone reading the card: the sleeve runs closer to 10% vol than 8%. The
card's `cash`/`risk_scale` fields stay correct per bar (r1268 fixed that path); what was
never reported is the gap between the target's name and what it delivers.

Not fixed here by fitting a correction multiplier on the same 1648 bars — that would be a
second fitted constant on top of the first. The right place to settle it is the forward
ledger (r1267/r1268), which measures delivered vol out of sample by construction.

## What this is and is not

- Exploratory sensitivity face: no prereg, no verdict, no promotion, no ledger booking.
- Costs, fill basis, decision grid, universe: identical to the production card's engine.
- Survivorship (live-code ETF pool) and IS-heavy history are unchanged caveats.
- The published configuration is **not** changed by this round.

## Reproduce

```
python scripts/etf_vol_target_sweep.py --selftest     # 8/8, offline, no panel needed
python scripts/etf_vol_target_sweep.py run            # results/etf_vol_target_sweep.json
```