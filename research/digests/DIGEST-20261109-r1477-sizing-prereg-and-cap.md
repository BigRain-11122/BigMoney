# r1477 — the ruler gets a pinned window, and the cap is priced by its own two arms

Face: `results/etf_book_sizing_prereg.json` · evidence cutoff 2026-11-06 · 1657 paired bars
Product: `scripts/etf_book_sizing_prereg.py` (selftest 24/24 · check PREREG_PINNED)
Doc: `research/ETF_BOOK_SIZING_PREREG.md` · cards E484/E485

## What the round asked

r1475 ended with two open items: (1) write the sizing window as a mechanical pre-registration
(fixed calendar window, what has to be re-run when it changes, what the ticket does when k
lands outside the noise band), and (2) answer whether "de-lever only, never leverage" is an
effective constraint in the 2020-2022 segment where beta reads 0.17..0.29 and k hits the 1.0
ceiling.

## Findings

**The band is the noise, not a number someone liked.** The ruler's own 1-sd k-noise is 10.43pp
(r1475). The band is now derived from exactly that (`band_rule(noise_pp)` → inside 10.43pp,
warn 20.86pp, outside 20.86pp), with three distinct actions and `production_effect =
advisory in v1`. A band with no measured noise behind it, or an unordered one, fails the gate.

**The window is pinned.** 306 trailing bars, anchored on the last graded decision bar, changeable
only by pre-registered amendment. Self-test pins inside == noise × frozen multiple, and the
pinned length == the window the noise was measured on.

**The premise was wrong: the cap never binds in 2020-2022.** Walking the published window path
era by era (`eras`): 2020_2022 beta 0.256..0.867 → k_raw max 0.78, zero capped windows; 2023
zero; **2024_2025 beta down to 0.1317 → 12 of 24 windows capped, k_raw up to 1.519**; 2026 zero.
The segment the round named is not the segment where the clip is alive.

**Two estimators, two opposite answers — both true and both must be printed.**

| | production estimator (expanding beta) | the floor's own estimator (306-bar window) |
| --- | --- | --- |
| readings | 1531 decision bars | 68 windows |
| capped | 0 (min beta 0.42 vs a 0.20 target) | 17 (2024-08-22..2025-12-18), k_raw up to 2.95 |
| risk withheld | none | up to 93.2pp |
| removing the clip | no change (7.95% / Sharpe 1.3267 both arms) | CAGR +9.69pp, **Sharpe −0.0099**, MDD −11.0pp worse |
| verdict | `CAP_NEVER_BINDS` | `CAP_COSTS_NOTHING_RISK_ADJUSTED` |

So on the estimator that actually sizes the book the cap is a leash that never reaches its edge;
on the estimator the desk has been arguing about it fires a quarter of the time, and letting it
off would buy return with proportionally more risk, i.e. nothing risk-adjusted.

## Why it matters

`k = min(1.0, target/beta)` is a statement about risk, but which beta you read it off decides both
whether the cap ever acts and whether it ever cost anything. Until this round the two estimators
were sitting in the same sentence without a subject. The ticket now has one receipt that says
which ruler signed the floor, how much that ruler's reading can wobble, and what the ticket does
at each edge of that wobble.

## Wiring

* `check` re-derives both cap verdicts from their own arms; a hedge word or a verdict that does
  not follow from the numbers fails.
* S6 leg `sizing_prereg` (rc0, 0.1s, JSON reads only).
* Two smoke legs (selftest + check).
* Cards E484 (band = the noise) and E485 (cap judged by risk-adjusted return, and the estimator
  must be named).