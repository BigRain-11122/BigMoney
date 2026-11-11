# ETF book -- is the incumbent buffer an edge, or one decision sequence?

Window ends 2026-11-10 | 5 books x 4 decision phases = 20 comparison cells | 10bp/side

## Verdict (rule frozen before the run)

**REJECT** -- median return effect -0.13pp is below the floor -0.05pp

## Control

k=0 at the production cell reproduces the published n12_vt08: 9.62% vs 9.62% (delta +0.000pp, within tolerance)

## Does the phase move the book at all?

Decision calendar per phase (production book): 2020-01-02: 83 decisions, 2020-01-02..2026-10-14; 2020-01-09: 83 decisions, 2020-01-09..2026-10-21; 2020-01-16: 83 decisions, 2020-01-16..2026-10-28; 2020-01-23: 83 decisions, 2020-01-23..2026-11-04 -- distinct calendars.

Note: 1 of 4 phases carry a distinct decision count -- the count is not the signature, the dates are.

## Phase noise vs the buffer effect

| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |
|---|---|---|---|---|---|
| n8_r20 | 4 | 8.43% | 10.75% | 0.768 | 0.122 |
| n12_r10 | 4 | 12.83% | 14.36% | 0.398 | 0.064 |
| n12_r20 | 4 | 9.12% | 11.06% | 0.508 | 0.092 |
| n12_r40 | 4 | 3.79% | 9.94% | 2.827 | 0.194 |
| n20_r20 | 4 | 6.85% | 8.98% | 0.585 | 0.089 |

Median phase IQR of CAGR: **0.585 pp**; the k=0.05 effect is -0.130pp median -- smaller than the phase noise.

## The buffer across every cell

| k | cells | turnover down | return not worse | return up | Sharpe not worse | median dCAGR | median dSharpe | dTurnover |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 20 | 100% | 55% | 30% | 35% | -0.130pp | -0.011 | -0.030 |
| 0.20 | 20 | 100% | 60% | 60% | 60% | +0.125pp | +0.004 | -0.106 |

## Per-cell detail (k=0.05 vs its own k=0)

| book | phase | dCAGR | dSharpe | dTurnover | turnover base -> arm |
|---|---|---|---|---|---|
| n8_r20 | 2020-01-02 | -0.07pp | +0.000 | -0.026 | 1.018 -> 0.992 |
| n8_r20 | 2020-01-09 | -0.26pp | -0.018 | -0.033 | 1.040 -> 1.007 |
| n8_r20 | 2020-01-16 | -0.24pp | -0.021 | -0.029 | 1.057 -> 1.028 |
| n8_r20 | 2020-01-23 | -0.44pp | -0.039 | -0.027 | 1.069 -> 1.042 |
| n12_r10 | 2020-01-02 | -0.53pp | -0.045 | -0.031 | 0.826 -> 0.795 |
| n12_r10 | 2020-01-09 | -0.12pp | -0.010 | -0.034 | 0.832 -> 0.798 |
| n12_r10 | 2020-01-16 | -0.52pp | -0.045 | -0.032 | 0.827 -> 0.796 |
| n12_r10 | 2020-01-23 | -0.12pp | -0.010 | -0.035 | 0.832 -> 0.797 |
| n12_r20 | 2020-01-02 | +0.07pp | +0.014 | -0.033 | 0.934 -> 0.901 |
| n12_r20 | 2020-01-09 | -0.27pp | -0.015 | -0.032 | 0.961 -> 0.929 |
| n12_r20 | 2020-01-16 | -0.21pp | -0.027 | -0.040 | 0.996 -> 0.955 |
| n12_r20 | 2020-01-23 | +0.30pp | +0.027 | -0.027 | 0.968 -> 0.941 |
| n12_r40 | 2020-01-02 | -0.20pp | -0.011 | -0.033 | 1.043 -> 1.010 |
| n12_r40 | 2020-01-09 | -0.22pp | -0.020 | -0.013 | 1.057 -> 1.044 |
| n12_r40 | 2020-01-16 | +0.04pp | +0.004 | -0.014 | 0.970 -> 0.956 |
| n12_r40 | 2020-01-23 | -0.14pp | -0.011 | -0.034 | 1.028 -> 0.995 |
| n20_r20 | 2020-01-02 | +0.29pp | +0.021 | -0.022 | 0.828 -> 0.806 |
| n20_r20 | 2020-01-09 | -0.12pp | -0.007 | -0.024 | 0.844 -> 0.820 |
| n20_r20 | 2020-01-16 | +0.36pp | +0.030 | -0.016 | 0.867 -> 0.850 |
| n20_r20 | 2020-01-23 | +0.07pp | +0.008 | -0.023 | 0.853 -> 0.830 |

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
