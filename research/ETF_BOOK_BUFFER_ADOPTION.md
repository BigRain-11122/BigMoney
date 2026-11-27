# ETF book -- is the incumbent buffer an edge, or one decision sequence?

Window ends 2026-11-26 | 5 books x 4 decision phases = 20 comparison cells | 10bp/side

## Verdict (rule frozen before the run)

**REJECT** -- median return effect -0.14pp is below the floor -0.05pp

## Control

k=0 at the production cell reproduces the published n12_vt08: 8.92% vs 8.92% (delta +0.000pp, within tolerance)

## Does the phase move the book at all?

Decision calendar per phase (production book): 2020-01-02: 84 decisions, 2020-01-02..2026-11-11; 2020-01-09: 84 decisions, 2020-01-09..2026-11-18; 2020-01-16: 84 decisions, 2020-01-16..2026-11-25; 2020-01-23: 83 decisions, 2020-01-23..2026-11-04 -- distinct calendars.

Note: 2 of 4 phases carry a distinct decision count -- the count is not the signature, the dates are.

## Phase noise vs the buffer effect

| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |
|---|---|---|---|---|---|
| n8_r20 | 4 | 7.50% | 10.13% | 1.062 | 0.130 |
| n12_r10 | 4 | 11.97% | 13.99% | 0.903 | 0.112 |
| n12_r20 | 4 | 8.29% | 10.83% | 0.785 | 0.090 |
| n12_r40 | 4 | 3.32% | 9.72% | 3.100 | 0.229 |
| n20_r20 | 4 | 6.30% | 8.72% | 0.770 | 0.071 |

Median phase IQR of CAGR: **0.903 pp**; the k=0.05 effect is -0.135pp median -- smaller than the phase noise.

## The buffer across every cell

| k | cells | turnover down | return not worse | return up | Sharpe not worse | median dCAGR | median dSharpe | dTurnover |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 20 | 100% | 60% | 25% | 30% | -0.135pp | -0.009 | -0.030 |
| 0.20 | 20 | 100% | 65% | 65% | 65% | +0.145pp | +0.009 | -0.108 |

## Per-cell detail (k=0.05 vs its own k=0)

| book | phase | dCAGR | dSharpe | dTurnover | turnover base -> arm |
|---|---|---|---|---|---|
| n8_r20 | 2020-01-02 | -0.07pp | -0.001 | -0.024 | 1.022 -> 0.997 |
| n8_r20 | 2020-01-09 | -0.17pp | -0.007 | -0.040 | 1.051 -> 1.011 |
| n8_r20 | 2020-01-16 | -0.24pp | -0.021 | -0.029 | 1.067 -> 1.038 |
| n8_r20 | 2020-01-23 | -0.43pp | -0.040 | -0.027 | 1.069 -> 1.042 |
| n12_r10 | 2020-01-02 | -0.49pp | -0.042 | -0.032 | 0.830 -> 0.798 |
| n12_r10 | 2020-01-09 | -0.13pp | -0.011 | -0.034 | 0.835 -> 0.801 |
| n12_r10 | 2020-01-16 | -0.49pp | -0.042 | -0.032 | 0.831 -> 0.799 |
| n12_r10 | 2020-01-23 | -0.13pp | -0.011 | -0.034 | 0.834 -> 0.800 |
| n12_r20 | 2020-01-02 | +0.06pp | +0.013 | -0.033 | 0.938 -> 0.905 |
| n12_r20 | 2020-01-09 | -0.15pp | -0.005 | -0.034 | 0.969 -> 0.936 |
| n12_r20 | 2020-01-16 | -0.24pp | -0.029 | -0.043 | 1.004 -> 0.961 |
| n12_r20 | 2020-01-23 | +0.15pp | +0.014 | -0.029 | 0.968 -> 0.939 |
| n12_r40 | 2020-01-02 | -0.20pp | -0.011 | -0.033 | 1.043 -> 1.010 |
| n12_r40 | 2020-01-09 | -0.22pp | -0.019 | -0.013 | 1.057 -> 1.044 |
| n12_r40 | 2020-01-16 | +0.04pp | +0.004 | -0.014 | 0.970 -> 0.956 |
| n12_r40 | 2020-01-23 | -0.14pp | -0.011 | -0.034 | 1.028 -> 0.995 |
| n20_r20 | 2020-01-02 | +0.29pp | +0.022 | -0.021 | 0.834 -> 0.814 |
| n20_r20 | 2020-01-09 | -0.07pp | -0.003 | -0.025 | 0.850 -> 0.825 |
| n20_r20 | 2020-01-16 | +0.37pp | +0.030 | -0.017 | 0.869 -> 0.852 |
| n20_r20 | 2020-01-23 | -0.01pp | +0.000 | -0.023 | 0.853 -> 0.830 |

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
