# r1169 — does the production book's width sign survive a signal-free book on its own panel?

**Question (from bm-c r1362 card E276):** the width direction was measured inside one grid on one
panel and flipped on another, and E276 closed by demanding the family's width sign get its own null
*on its own panel*. This round ran that null.

**Face:** `scripts/etf_book_width_null_production.py` — production panel (5,270 bars x 1,504
equity/commodity/convertible names, repaired prints, same builder as the card), widths 3/5/8/12,
cadence 20, 10bp, no vol target; real score vs 6 seeded random score sets masked to the real
eligibility. Artifact: `results/etf_book_width_null_production.json` (+ `.md`).

| width | real CAGR | null median (min..max) | real − best null | Sharpe | vol |
|---|---|---|---|---|---|
| 3 | 15.58% | 0.77% (−6.53..+3.39) | +12.19pp | 0.95 | 17.4% |
| 5 | 15.73% | 0.30% (−2.89..+2.23) | +13.50pp | 1.01 | 16.4% |
| 8 | 15.15% | 0.48% (−1.70..+2.64) | +12.51pp | 1.00 | 15.9% |
| 12 | 14.21% | 1.77% (−1.63..+3.68) | +10.53pp | 0.98 | 15.3% |

rank corr(width, CAGR): real **−0.80**, null **+0.40** → verdict `WIDTH_SIGN_DIFFERS_FROM_NOISE`.

**What that means.** On this panel the erosion from widening is the score's, not diversification
arithmetic: real earns 10.5-13.5pp above the null's *best* seed at every rung, and the real curve
slopes down while the null slopes up. This is the opposite of E276's cross-panel read, which is the
whole point of demanding the null where the number lives.

**The half that panel evidence cannot answer.** The ticket already prices the same two widths under
two leverage rules: beta-scaled says 12 names cost 1.53pp vs 5 (agrees with this face), vol-target
says 12 names *gain* 0.24pp (disagrees) -- and 0.24pp is smaller than the 2.045pp engine
disagreement the ticket itself publishes. So the width sign is a property of a (panel, rule) pair.
The face reads the ticket rather than retyping it, and publishes `RULES_DISAGREE_ON_THE_WIDTH_SIGN`.

**Book in force unchanged** (width 5). This face is a measurement, not an optimisation, and the
panel is the live ETF universe, so the survivorship caveat travels with it.

Methodology card: E278. Wired: chain leg `etf_book_width_null_production` + smoke leg that
recomputes the verdict from the published columns (smoke 255/255 PASS after the wiring).