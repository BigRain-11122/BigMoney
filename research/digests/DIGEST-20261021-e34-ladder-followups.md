# DIGEST 2026-10-21 — E34: the ladder family's follow-up questions

Source faces (all descriptive census, zero prereg, zero judgment, trial_count 0):

* `results/e34_broad_eq/UNIV-4170ac-xsh511-20261021.json` — E34-LADDER-VS-BROAD-EQ
* `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-FULL-X3.json` + `...-WIN-2018-X3.json` — E34-LADDER-VS-510300-X3
* `results/e34_cadence_rolling/CADENCE-ROLLING-3Y-20261020.json` — E34-CADENCE-ROLLING-3Y
* Runner: `scripts/e34_cadence_rolling.py` (selftest 6/6, deterministic offline)

Cutoff 2026-10-20, calendar 2012-05-28..2026-10-20 (13.88y, 3,497 bars).
Accounting imported from E33/E27/E24 — no re-implementation.

## Q-A · Is the ladder just a mid/small tilt? (equal weight every eligible equity ETF vs frozen five)

1,231 eligible equity ETFs (sh511 money/bond block excluded), monthly equal weight,
same cost model, same cash leg:

| book | ann % | vol % | Sharpe | cost bp/yr |
|---|---|---|---|---|
| frozen five (ladder) | 5.27 | 21.54 | 0.347 | 4.2 |
| all equity ETFs (equal w) | **8.24** | 18.77 | **0.516** | 8.3 |

Delta **+338.7bp/yr, monthly-rel t = 1.97** — the widest book we can build beats the
five-name desk book on return *and* on volatility at the same time. The ladder is not
a diversified expression of the idea; it is a concentrated mid/small tilt carrying
21.5% vol for 5.3%/yr.

Live-mark disclosure: the selection face thins at the tail (eligible 15 at 2026-10-20
vs 491 in 2023 because the trailing-turnover filter needs recent amounts); the
equal-weight leg is therefore built from the names passing each month-end, and the
last month of the sample is thin. Full-sample length is unaffected.

## Q-B · Does the Q1 read survive cost x3?

| window | ladder ann % | 510300 ann % | delta bp/yr | monthly t | ladder cost bp/yr |
|---|---|---|---|---|---|
| full sample x1 | 5.27 | 3.43 | +187.9 | 0.83 | 4.2 |
| full sample x3 | 5.19 | 3.43 | +179.8 | 0.80 | 12.6 |
| 2018+ x3 | 5.39 | 0.18 | +632.1 | 1.59 | 12.3 |

Fees are not the story: tripling cost moves the delta by ~8bp in both windows. The
2018+ +632bp survives cost x3 but its t is 1.59 and it is dominated by 510300's flat
path (0.18%/yr) over that window, not by ladder skill. Nothing here clears an
evidence bar; the honest read is unchanged from E33 — the ladder's edge over simply
holding CSI300 is **not demonstrated**.

## Q-C · When does the cadence wash flip? (rolling 36-month monthly-vs-quarterly)

Full sample: quarterly beats monthly by **+45.8bp/yr**. 138 overlapping windows, 10 sign
flips. Era means of the rolling read (positive windows / n):

| era (window end) | mean bp/yr | min | max | positive |
|---|---|---|---|---|
| pre-2016 | **-189.5** | — | — | 0/8 |
| 2016-2017 | **-164.5** | — | — | 0/24 |
| 2018-2020 | -17.9 | — | — | 8/36 |
| 2021-2023 | -18.5 | — | — | 10/36 |
| 2024+ | +5.8 | — | — | 18/34 |

Dated flips: 2018-05 (the big one, -140.6 -> +87.8), 2019-02, 2019-06, 2020-12,
2021-08, 2021-09, 2021-12, 2024-12, 2026-06.

Reading: quarterly's large advantage lives entirely before 2018 — i.e. in the window
where the ladder's own members were mostly not yet listed, so it is a property of the
partial book, not of the clock. Since 2018 the difference is between -20 and +6bp/yr
and since 2024 it is a coin flip. Monthly stays default because the alternative never
earns anything where the book is real.

## Desk corollary

1. The weighting axis, the timing axis, the breadth axis, the cadence axis and the
   membership axis are now all closed as washes to losses. What is **left** is book
   width: equal weight across every eligible equity ETF dominates the frozen five by
   338.7bp/yr at *lower* vol. That is the only surviving positive in this family.
2. Those two survivors (broad book, and the 2018+ ladder-vs-510300) must be re-read on
   the recent window and at cost x3 before anyone treats them as real — seeded as
   E35-BROAD-EQ-2018 / E35-BROAD-EQ-X3 / E35-CADENCE-ROLLING-X3.

## Pits

* Annualising a rolling window on the nominal month count (36/12) overstates a
  36-month-end window by ~2% because the span is up to 3.1 calendar years — annualise
  on the realised bar span and use the geometric form (selftest leg 2 pins it: a
  synthetic 2%/yr alpha must reproduce exactly 200bp/yr).
* Pool seed timestamps written ahead of the wall clock (r1104's entered_at 02:20:00 at
  02:04) surface as an `updated_at` envelope-only dualrun drift. Read the clock once per
  write; this round did, and the remaining drift is the inherited future stamp.