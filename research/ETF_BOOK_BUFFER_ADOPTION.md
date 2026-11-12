# ETF book -- is the incumbent buffer an edge, or one decision sequence?

Window ends 2026-11-12 | 5 books x 4 decision phases = 20 comparison cells | 10bp/side

## Verdict (rule frozen before the run)

**REJECT** -- median return effect -0.15pp is below the floor -0.05pp

## Control

k=0 at the production cell reproduces the published n12_vt08: 9.65% vs 9.65% (delta +0.000pp, within tolerance)

## Does the phase move the book at all?

Decision calendar per phase (production book): 2020-01-02: 84 decisions, 2020-01-02..2026-11-11; 2020-01-09: 83 decisions, 2020-01-09..2026-10-21; 2020-01-16: 83 decisions, 2020-01-16..2026-10-28; 2020-01-23: 83 decisions, 2020-01-23..2026-11-04 -- distinct calendars.

Note: 2 of 4 phases carry a distinct decision count -- the count is not the signature, the dates are.

## Phase noise vs the buffer effect

| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |
|---|---|---|---|---|---|
| n8_r20 | 4 | 8.34% | 10.76% | 0.718 | 0.126 |
| n12_r10 | 4 | 12.72% | 14.19% | 0.398 | 0.058 |
| n12_r20 | 4 | 9.03% | 10.90% | 0.535 | 0.099 |
| n12_r40 | 4 | 3.71% | 9.79% | 2.960 | 0.205 |
| n20_r20 | 4 | 6.79% | 8.86% | 0.630 | 0.093 |

Median phase IQR of CAGR: **0.63 pp**; the k=0.05 effect is -0.150pp median -- smaller than the phase noise.

## The buffer across every cell

| k | cells | turnover down | return not worse | return up | Sharpe not worse | median dCAGR | median dSharpe | dTurnover |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 20 | 100% | 55% | 30% | 30% | -0.150pp | -0.011 | -0.030 |
| 0.20 | 20 | 100% | 60% | 60% | 60% | +0.105pp | +0.004 | -0.106 |

## Per-cell detail (k=0.05 vs its own k=0)

| book | phase | dCAGR | dSharpe | dTurnover | turnover base -> arm |
|---|---|---|---|---|---|
| n8_r20 | 2020-01-02 | -0.07pp | -0.001 | -0.024 | 1.022 -> 0.997 |
| n8_r20 | 2020-01-09 | -0.27pp | -0.018 | -0.033 | 1.040 -> 1.007 |
| n8_r20 | 2020-01-16 | -0.23pp | -0.020 | -0.029 | 1.057 -> 1.028 |
| n8_r20 | 2020-01-23 | -0.44pp | -0.040 | -0.027 | 1.069 -> 1.042 |
| n12_r10 | 2020-01-02 | -0.51pp | -0.043 | -0.030 | 0.827 -> 0.797 |
| n12_r10 | 2020-01-09 | -0.13pp | -0.011 | -0.033 | 0.832 -> 0.799 |
| n12_r10 | 2020-01-16 | -0.51pp | -0.044 | -0.030 | 0.828 -> 0.798 |
| n12_r10 | 2020-01-23 | -0.13pp | -0.012 | -0.034 | 0.832 -> 0.798 |
| n12_r20 | 2020-01-02 | +0.06pp | +0.014 | -0.033 | 0.938 -> 0.905 |
| n12_r20 | 2020-01-09 | -0.25pp | -0.013 | -0.032 | 0.961 -> 0.929 |
| n12_r20 | 2020-01-16 | -0.19pp | -0.024 | -0.040 | 0.996 -> 0.955 |
| n12_r20 | 2020-01-23 | +0.28pp | +0.026 | -0.028 | 0.968 -> 0.940 |
| n12_r40 | 2020-01-02 | -0.20pp | -0.011 | -0.033 | 1.043 -> 1.010 |
| n12_r40 | 2020-01-09 | -0.23pp | -0.019 | -0.013 | 1.057 -> 1.044 |
| n12_r40 | 2020-01-16 | +0.04pp | +0.004 | -0.014 | 0.970 -> 0.956 |
| n12_r40 | 2020-01-23 | -0.15pp | -0.011 | -0.034 | 1.028 -> 0.995 |
| n20_r20 | 2020-01-02 | +0.30pp | +0.021 | -0.021 | 0.834 -> 0.814 |
| n20_r20 | 2020-01-09 | -0.15pp | -0.009 | -0.024 | 0.844 -> 0.820 |
| n20_r20 | 2020-01-16 | +0.36pp | +0.030 | -0.016 | 0.867 -> 0.850 |
| n20_r20 | 2020-01-23 | +0.06pp | +0.007 | -0.023 | 0.853 -> 0.830 |

## Frozen criteria

```
{
  "k_test": 0.05,
  "turnover_down_share_min": 0.9,
  "cagr_share_min": 0.8,
  "cagr_share_floor_pp": -0.15,
  "sharpe_share_min": 0.75,
  "median_cagr_floor_pp": -0.05,
  "frozen": "constants above were written before the first run; the gate refuses a face that echoes others"
}
```

## Caveats

* exploratory: no preregistration, no ledger booking; this changes a config only if ADOPT
* cells share one panel and overlap in time -- the sign test counts cells, not independent bets
* one panel / one cost model; survivor-pool, young-fund and 2024+ regime caveats unchanged
* the reference arm k=0.20 exists to bound the direction, not as a candidate
