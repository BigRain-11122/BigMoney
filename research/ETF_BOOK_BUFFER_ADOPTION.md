# ETF book -- is the incumbent buffer an edge, or one decision sequence?

Window ends 2026-10-28 | 5 books x 4 decision phases = 20 comparison cells | 10bp/side

## Verdict (rule frozen before the run)

**REJECT** -- median return effect -0.14pp is below the floor -0.05pp

## Control

k=0 at the production cell reproduces the published n12_vt08: 9.70% vs 9.70% (delta +0.000pp, within tolerance)

## Does the phase move the book at all?

Decision calendar per phase (production book): 2020-01-02: 83 decisions, 2020-01-02..2026-10-14; 2020-01-09: 83 decisions, 2020-01-09..2026-10-21; 2020-01-16: 82 decisions, 2020-01-16..2026-09-22; 2020-01-23: 82 decisions, 2020-01-23..2026-09-30 -- distinct calendars.

Note: 2 of 4 phases carry a distinct decision count -- the count is not the signature, the dates are.

## Phase noise vs the buffer effect

| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |
|---|---|---|---|---|---|
| n8_r20 | 4 | 8.48% | 10.84% | 0.740 | 0.128 |
| n12_r10 | 4 | 12.85% | 14.38% | 0.383 | 0.059 |
| n12_r20 | 4 | 9.12% | 10.93% | 0.528 | 0.100 |
| n12_r40 | 4 | 3.71% | 10.28% | 3.007 | 0.208 |
| n20_r20 | 4 | 6.85% | 8.91% | 0.687 | 0.101 |

Median phase IQR of CAGR: **0.687 pp**; the k=0.05 effect is -0.140pp median -- smaller than the phase noise.

## The buffer across every cell

| k | cells | turnover down | return not worse | return up | Sharpe not worse | median dCAGR | median dSharpe | dTurnover |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 20 | 100% | 55% | 30% | 30% | -0.140pp | -0.011 | -0.030 |
| 0.20 | 20 | 100% | 60% | 55% | 60% | +0.030pp | +0.005 | -0.104 |

## Per-cell detail (k=0.05 vs its own k=0)

| book | phase | dCAGR | dSharpe | dTurnover | turnover base -> arm |
|---|---|---|---|---|---|
| n8_r20 | 2020-01-02 | -0.17pp | -0.010 | -0.026 | 1.018 -> 0.992 |
| n8_r20 | 2020-01-09 | -0.27pp | -0.018 | -0.033 | 1.040 -> 1.007 |
| n8_r20 | 2020-01-16 | -0.24pp | -0.021 | -0.030 | 1.047 -> 1.018 |
| n8_r20 | 2020-01-23 | -0.44pp | -0.040 | -0.027 | 1.068 -> 1.041 |
| n12_r10 | 2020-01-02 | -0.42pp | -0.034 | -0.031 | 0.821 -> 0.790 |
| n12_r10 | 2020-01-09 | -0.13pp | -0.012 | -0.034 | 0.832 -> 0.798 |
| n12_r10 | 2020-01-16 | -0.42pp | -0.034 | -0.031 | 0.822 -> 0.791 |
| n12_r10 | 2020-01-23 | -0.13pp | -0.011 | -0.035 | 0.832 -> 0.797 |
| n12_r20 | 2020-01-02 | +0.07pp | +0.014 | -0.033 | 0.934 -> 0.901 |
| n12_r20 | 2020-01-09 | -0.24pp | -0.013 | -0.032 | 0.961 -> 0.929 |
| n12_r20 | 2020-01-16 | -0.14pp | -0.019 | -0.039 | 0.987 -> 0.948 |
| n12_r20 | 2020-01-23 | +0.41pp | +0.036 | -0.028 | 0.964 -> 0.936 |
| n12_r40 | 2020-01-02 | -0.20pp | -0.011 | -0.033 | 1.043 -> 1.010 |
| n12_r40 | 2020-01-09 | -0.22pp | -0.019 | -0.013 | 1.057 -> 1.044 |
| n12_r40 | 2020-01-16 | +0.04pp | +0.003 | -0.015 | 0.962 -> 0.947 |
| n12_r40 | 2020-01-23 | -0.14pp | -0.010 | -0.034 | 1.018 -> 0.984 |
| n20_r20 | 2020-01-02 | +0.27pp | +0.018 | -0.022 | 0.828 -> 0.806 |
| n20_r20 | 2020-01-09 | -0.13pp | -0.007 | -0.025 | 0.845 -> 0.820 |
| n20_r20 | 2020-01-16 | +0.36pp | +0.030 | -0.016 | 0.863 -> 0.846 |
| n20_r20 | 2020-01-23 | +0.10pp | +0.009 | -0.023 | 0.851 -> 0.828 |

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
