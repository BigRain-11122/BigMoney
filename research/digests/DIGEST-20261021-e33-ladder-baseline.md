# E33 ladder-baseline — digest (r1104 bm-b, panel cutoff 2026-10-20)

Family question: E24-E32 closed every *how* axis on the five-rung desk ladder
(weighting, trend filters, drift bands, timing). E33 asks the *whether* and the
*clock*: does the ladder earn anything over simply holding 510300, does the
rebalance cadence matter, and can a causal rule rebuild the frozen five?

Runner: `scripts/e33_ladder_baseline.py` (selftest 7/7 hermetic; accounting
imported from `e24_ladder_weighting` and `e27_universe_expansion`, nothing
re-implemented). Faces: `results/e33_ladder_baseline/Q{1,2,3}-*-WIN-{FULL,2016,2018}.json`.

## Q1 — ladder equal-weight vs 510300 buy-and-hold (net of cost)

| window | ladder | 510300 B&H | delta bp/yr | monthly-rel t |
|---|---|---|---|---|
| full (2012-05..2026-10, 3,671 bars) | 5.27%/yr, Sharpe 0.347 | 3.43%/yr | **+187.9** | 0.83 |
| 2016-11+ (all five members listed) | 1.84%/yr, 0.191 | 2.29%/yr, 0.215 | **-35.6** | -0.02 |
| 2018-01+ | 5.48%/yr, 0.370 | 0.18%/yr | **+640.0** | 1.61 |

Era month means of ladder-minus-bench (full sample): pre2017 +42.7bp,
2017-2020 -26.2bp, 2021-2023 +28.8bp, 2024-now +29.9bp.

**Read: no demonstrated edge.** Not one window clears |t| = 2, and the sign
flips depending on whether 2017's large-cap year is inside the window (the
ladder equal-weights small/mid members against a cap-weighted CSI300). The
+188bp full-sample and +640bp 2018+ point estimates are era artefacts, not a
measurable premium: the only window where all five members exist (+2016-11)
comes out slightly negative. Equal weight remains the reference book; nothing
here justifies a claim that the ladder beats holding 510300.

## Q2 — rebalance clock (monthly / quarterly / semiannual / annual)

Cost is not the question: x1 cost is 2.6-4.2bp/yr in every clock, x3 is
7.1-12.6bp/yr, turnover 0.18-0.29x/yr. What changes is drift given up.

| window | monthly | quarterly | semiannual | annual |
|---|---|---|---|---|
| full ann% (x1) | 5.27 | 5.74 (+45.8bp, t 0.86) | 5.66 (+37.7bp) | 6.19 (+92.0bp, t 0.84) |
| 2016-11+ ann% | 1.84 | 1.87 (+3.5bp, t 0.15) | 1.78 (-6.1bp) | 1.49 (-34.2bp, t -1.04) |
| 2018-01+ ann% | 5.48 | 2.73 (-236.9bp, t -1.48) | 3.25 | 2.41 |

**Read: wash.** The full-sample "annual wins by 92bp/yr" collapses to -34bp on
2016+ and the quarterly advantage turns into -237bp on 2018+. All |t| <= 1.5,
sign is window-dependent, and the cost saving (1-2bp/yr) is an order of
magnitude smaller than the drift noise. Monthly stays as the default because
nothing beats it reliably, not because it is demonstrably best.

## Q3 — frozen five vs causal membership re-selection (top-5 by trailing liquidity)

Universe: 1,276 ETF codes (1,231 after dropping the sh511 money/bond block),
28-month... 250-bar eligibility, trailing-60d turnover ranking read at the
decision close.

| window | frozen5 monthly | top5 monthly | top5 equity-only monthly | vs frozen |
|---|---|---|---|---|
| full | 5.27%/yr | -0.23%/yr | 1.44%/yr | -378 / -290bp (t -1.08 / -1.17) |
| 2016-11+ | 1.84 | -1.78 | -2.42 | -306 / -351bp |
| 2018-01+ | 5.48 | -1.34 | -2.20 | -510 / -559bp (t -1.00 / -1.95) |

Last quarters' picks are the big index funds (510300/510500/512100/588000) plus
a treasury ETF when the wide universe is used; cost runs 13-24bp/yr, so the gap
is selection, not fees.

**Read: the frozen five are not reproducible by any causal rule we can run.**
A liquidity rule buys today's crowded large funds and lands 300-560bp/yr below
the fixed set. That is a statement about hindsight, not about skill: the fixed
five carry information a live rule would not have had, so "membership choice
adds value" cannot be claimed from this comparison either. Honest reading: the
ladder's five members are a design choice, and no mechanical re-selection rule
justifies itself.

## Verdicts (descriptive, no gate / no prereg / no trial count)

- Q1: ladder vs 510300 = **not demonstrated** (|t| <= 1.61, sign window-dependent).
- Q2: cadence = **wash** (cost immaterial, drift dominates, no clock wins reliably).
- Q3: causal membership re-selection = **loses** (-290..-559bp/yr vs the frozen five).
- Net for the family: the ladder survives as the reference book *by default*,
  not by evidence. Every further "improve the ladder" axis now has to answer
  Q1 first, which nothing in E24-E33 does.
- Follow-ups seeded as E34: ladder vs equal-weight-all-equity-ETFs (is the
  ladder just a mid-cap tilt?), cost-x3 stress on the Q1 comparison, and the
  2016+ cadence re-read with a rolling 3-year window.