# r1301 — the staggered book, priced under the rule we actually publish

Question inherited from r1300 (`next`): the staggered 5+5 book was quoted at **20.77% CAGR /
Sharpe 1.32**, next to the published card's **9.49% / 0.98**. Those two numbers were never
one experiment: the stagger was priced on 8 names, R10 cadence, bonds excluded and no
volatility target, while the card is 12 names, R20, equity+commodity+convertible, 8% vol
target, 10bp/side. r1262 already showed that "width + clock" moved together, so quoting
them side by side was a category error, not a finding.

`scripts/etf_book_stagger_publish.py` prices the stagger design through the published rule
and nothing else:

| element | value (both arms) |
|---|---|
| universe | `etf_book_production.prep_panel()` — equity + commodity + convertible, 1499 names, 168 flip repairs |
| score | `etf_composite_pf.build_score` |
| execution | decide at close t → fill at open t+1 → hold to next decision |
| cost | 10 bp per side, charged on the weight actually turned over |
| sizing | 8% vol target, `min(1, target / realised)`, never levered up |
| window | 2020-01-01 → 2026-10-26 (6.81y) |
| control | N12 / R20 / vt08 — the shipped card's own cell, re-priced here |

The control arm **reproduces the published card exactly** (9.49% vs 9.49%, delta 0.0pp,
pinned at a 0.5pp tolerance — r1297's rule that a control arm has to be the asserted one).

## The comparable numbers

| arm | CAGR | Sharpe | maxDD | vol | turnover / decision | IS CAGR | OOS CAGR |
|---|---|---|---|---|---|---|---|
| control: single sleeve N12/R20/vt08 | 9.49% | 0.980 | −11.77% | 10.17% | 0.934 | 3.84% | 18.10% |
| staggered 6+6, offset 10 bars | **10.41%** | **1.054** | **−10.36%** | 10.29% | **0.619** | 4.17% | 19.88% |
| delta | **+0.92pp** | +0.074 | **+1.41pp** | +0.12pp | **−0.315** | +0.33pp | +1.78pp |

Capacity, on one measure (p90 single-name participation vs 20-day median amount, weights
already vol-scaled):

| arm | deployable @1% ADV | deployable @5% ADV | p90 participation per 1M CNY |
|---|---|---|---|
| control | CNY 2.417M | CNY 12.09M | 0.41% |
| staggered | CNY 2.539M | CNY 12.70M | 0.39% |

## What this settles

1. **The stagger is not a second book and does not buy capacity.** +5% deployable at both
   participation limits, against a +61% claim that came from comparing a 10-name book with
   an 8-name book. The earlier "+61% capacity" is retired.
2. **Under one rule it is a mildly better book, not a better strategy.** +0.92pp CAGR on
   the same signal is inside a single year's noise (IS +0.33pp / OOS +1.78pp disagree on
   magnitude); the durable gains are the ones tied to the mechanism, and they are real:
   turnover falls 34% (0.619 vs 0.934 per decision) and maxDD improves 1.41pp, because the
   two sleeves never hit the same names on the same day.
3. **The 20.77% quote is retired as a comparison.** Any future stagger number must carry
   the rule tag (`12@R20@vt08@with-bond-universe`), or it is not comparable to 9.49%.
4. **Honest limits**: same signal ⇒ the gain is execution/timing diversification, not new
   edge; sleeve B is half-cash for the first 10 bars (warm-up drag, ~0.2pp, included);
   survivorship in the ETF pool is unchanged from the card; both arms are IS-heavy and the
   published expectation band (r1300) still governs what a human should expect.

## Second artefact: the smoke gate's last five-minute leg

`scripts/etf_vol_calibration.py --selftest` called `P.prep_panel()` (1499×1649) and then
drove the engine ten times: ~5 minutes of silence, sitting exactly on the 300 s per-leg
timeout inside `smoke_test.py`. It is the same defect r1300 fixed one script over
(`etf_vol_delivery_audit`). Replaced with an offline synthetic fixture (`_fixture()`,
40 names × 1500 bars) and raised its dispersion so the de-lever branch still engages
(mean scale 0.80 → 0.64 when the ratio hook is 1.25). **12/12 in 12.7 s** (was ~290 s),
which is the difference between "the gate finishes" and "the gate times out".

Evidence: `results/etf_book_stagger_publish.json`, `scripts/etf_book_stagger_publish.py`
(selftest 10/10), `scripts/etf_vol_calibration.py` (selftest 12/12).