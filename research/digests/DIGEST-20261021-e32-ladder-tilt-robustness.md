# E32 — ladder weighting tilts: cost stress and the 2018+ screen

Date: 2026-10-21 (r1103, bm-b)
Faces: `results/e32_tilt_robustness/TILT-{trend150h-x3,trend150h-2018,mix-2018}-20261021.json`
Runner: `scripts/e24_ladder_weighting.py` (existing; no new engine code this round)
Universe: the five-rung desk ladder (sh510300, sh510050, sh510500, sh512100, sh588000), monthly
rebalance at close, 13.041bp/side turnover cost, GC001 cash leg, panel cutoff 2026-10-20.

## What was asked

E25 showed the trend150h tilt positive at x1 (+72.6bp/yr) and dead as a return edge at the half-weight
variants; E30/E31 showed long-sample universe excesses dying in the recent window. E32 puts the tilt
family through the same two doors: cost stress (x3) and the 2018+ window.

## Results

| leg | vs equal-weight ladder | t | cost/yr | vol | Sharpe |
|---|---|---|---|---|---|
| trend150h, cost x3 (full sample) | +60.9bp/yr | 0.43 | 28.6bp | 17.08% | 0.416 |
| trend150h, 2018+ | **-156.8bp/yr** | -0.59 | 10.6bp | 16.12% | 0.308 |
| invvol, 2018+ | -25.2bp/yr | -0.30 | 6.7bp | 18.74% | 0.365 |
| liq, 2018+ | -147.0bp/yr | -1.33 | 6.7bp | 19.41% | 0.291 |
| momtilt, 2018+ | -90.1bp/yr | -0.81 | 10.7bp | 20.54% | 0.317 |
| equal (2018+ reference) | — | — | 4.1bp | 19.64% | 0.370 |

Era detail on the trend tilt: pre-2017 +17.3bp/mo, 2017-2020 +8.6, 2021-2023 +27.2, **2024-now -33.7**.
The tilt's whole life is pre-2024.

## Verdict

The tilt family is **closed as a wash-to-loss**. Cost is not the binding constraint (x3 only shaves
~12bp/yr and the sign survives), the 2018+ window kills every tilt, and the only survivor is the
vol-reduction of trend150h — which is a defensive-shape property, not extra return, and it does not
clear an evidence bar (|t| <= 0.59).

Desk consequence: the equal-weight ladder stays the reference book; no weighting scheme is adopted,
no prereg drafted, zero ledger booking, trial_count 0 (descriptive census only).

## Honest limits

- Five members only: every tilt is estimated on a 5-asset book, so per-leg noise is large by construction.
- Monthly rebalance is an untested assumption on this book (seeded as E33-LADDER-CADENCE).
- The 2018+ window is short (8.46y) and dominated by one regime break in 2024.
- Nothing here tests whether the ladder beats a single-index hold (seeded as E33-LADDER-VS-510300).