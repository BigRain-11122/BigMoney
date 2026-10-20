# DIGEST-20261020 · E24 grid closed at h=60 · E25 trend-filter family opened and answered

Round: bm-b r1095 · dept: research + engineering · cost: zero prereg, zero judgment, zero trial count · all faces descriptive.

## 1. E24 mode x horizon grid closed (three h=60 cells burned)

Pool units `E24-{DISPERSION,BREADTH,LADDER}-H60` burned; faces in
`results/e24_regime_census/CENSUS-*-h60-20261020.json` (apart from the earlier
`CENSUS-dispersion-h60` note, all three share the same run window:
2012-05-28..2026-10-20, 250-day causal burn-in, expanding quintiles).

| cell (h=60) | bottom quintile | top quintile | top stride t | read |
|---|---|---|---|---|
| ladder 20d momentum | +276.5bp | +170.8bp | +190.9bp, t 1.73 | ordering collapses; the top bucket is the *weakest* |
| breadth (share above 20d MA) | +274.1bp | +286.0bp | +268.5bp, t 2.87 | monotonicity gone, every bucket earns beta |
| dispersion (stdev of 5d returns) | +355.9bp | +136.4bp | +141.0bp, t 1.55 | **inverted**: the calm regime earns the most |

Interpretation: at a 60-bar horizon every E24 mode degenerates into "the ladder
drifts up"; the only structure left is the dispersion inversion, i.e. low
cross-sectional dispersion precedes stronger 60-bar returns. That inversion is
the last open read of the family, tested in §3.

## 2. E25 opened: per-member trend filter is a wash that costs money

New schemes in `scripts/e24_ladder_weighting.py` (`trendN` = cash for filtered
members, `trendNr` = renormalised, `trendNh` = half weight); faces
`results/e25_trend_tilt/TREND-{e35432,5f6c7c}-20261020.json` (13.88y, 3,497 bars,
monthly rebalance, 13.041bp/side on turnover).

| scheme | CAGR | vol | Sharpe | turnover/yr | cost bp/yr | edge vs equal |
|---|---|---|---|---|---|---|
| equal (baseline) | 5.00% | 21.54% | 0.335 | 0.32 | 4.2 | — |
| trend100 renormalised | 5.00% | 21.29% | 0.336 | 1.71 | 22.3 | **-0.1bp/yr** (t 0.12) |
| trend50 renormalised | 2.30% | 23.13% | 0.213 | 2.90 | 37.8 | -218.7 (t -1.21) |
| trend150 renormalised | 3.38% | 21.62% | 0.263 | 1.95 | 25.4 | -139.5 (t -0.81) |
| trend200 renormalised | 2.79% | 22.08% | 0.236 | 1.67 | 21.7 | -184.5 (t -1.06) |
| trend200 cash-share | 2.80% | 21.96% | 0.236 | 1.70 | 22.2 | -183.6 (t -1.04) |
| trend100 half weight | 4.34% | 21.38% | 0.306 | 1.73 | 22.6 | -60.5 (t -1.15) |
| trend200 half weight | 3.85% | 21.41% | 0.284 | 1.70 | 22.1 | -102.0 (t **-2.10**) |

Read: the 100-day filter is exactly the baseline after cost (it neither helps nor
hurts); every other window loses, the soft (half-weight) version loses less than
the hard switch but still loses. Era split is unstable: the 200d filter is
positive in 2017-2020 (+24bp/mo) and negative in 2021-2023 (-55bp/mo).

## 3. Why (whipsaw diagnostic, `results/e25_whipsaw/WHIPSAW-f20-20261020.json`)

Across the five members, 13.88y, forward window 20 bars:

| MA window | entries | exits | mean fwd after entry | mean fwd after exit | spread | mean member exposure |
|---|---|---|---|---|---|---|
| 50d | 481 | 484 | +38.1bp | -9.5bp | +47.6bp | 0.498 |
| 100d | 347 | 348 | +11.1bp | -17.3bp | +28.3bp | 0.498 |
| 200d | 188 | 190 | +74.0bp | **+116.7bp** | **-42.7bp** | 0.522 |

The 50/100-day filters are directionally right (entries beat exits) but cross
about seven times per member per year, so the 22-38bp/yr of turnover eats the
edge. The 200-day filter is outright wrong-way: exits are followed by *higher*
returns than entries - it sells before gains. That is the mechanism behind the
-184bp/yr.

## 4. Dispersion-h60 entry test = honest negative, and structurally empty

`scripts/e24_dispersion_h60_entry.py` (selftest 15/15) +
`results/e24_dispersion_h60_entry/ENTRY-20261020.json`. Bottom-tail gate
(signal <= expanding 0.20 cutoff), 60-bar non-overlapping holds, T+1, two-sided
13.041bp cost: 47 monthly windows, **2 active**, gated net +85.5bp/yr vs
always-on +3,146.8bp/yr -> edge **-3,061bp/yr** (paired t -1.31); sensitivity
q33 (-3,012), q50 (-3,560), offset10 (-3,660). All four pre-declared criteria
fail.

Diagnostics explain why the test is empty rather than merely negative: the
dispersion signal roughly doubled over the sample (decision-day median 0.0229
vs expanding cut max 0.0146), so an expanding bottom-tail cutoff can only fire
in the era where the signal was still low - it fired only in 2017 and 2019.
The census's low-dispersion bucket is therefore an **early-sample artifact**,
not a repeatable regime read.

## Consequence for supply

E24 is closed end to end (grid 15/15, timing, weighting, entry, dispersion-h60).
E25 opened and answered the trend-filter question in the same round. Supply
floor refilled 3/3 with unrun E25 configs (`E25-SOFT-150`,
`E25-TREND-50CASH`, `E25-WHIPSAW-H60`). No prereg is justified by any of this
round's faces.