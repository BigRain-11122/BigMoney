# ETF book -- is the drawdown_60 sign flip an effect or one decision sequence?

Window ends 2026-11-06 | 5 books x 4 phases = 20 cells | 8.0bp/side | flipped drawdown_60 +1 -> -1

## Verdict (rule frozen before the run)

**PHASE_FRAGILE** -- median +1.25pp is inside the control's own phase IQR 2.54pp -- the effect is not separable from the decision grid

## Identity legs

Score face built from the production sign dict vs `build_score`: max gap 0.0 (0 means the control arm IS the production arm). Re-running that identical score through the engine: 4 cells, worst 0.0 bp.

## Phase noise of the control arm

| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |
|---|---|---|---|---|---|
| n5_r20 | 4 | 2.02% | 7.56% | 3.350 | 0.290 |
| n5_r10 | 4 | 5.36% | 7.46% | 0.840 | 0.171 |
| n5_r40 | 4 | -0.97% | 5.38% | 1.790 | 0.187 |
| n3_r20 | 4 | 0.82% | 6.08% | 4.270 | 0.446 |
| n8_r20 | 4 | 4.38% | 8.35% | 2.545 | 0.170 |

Median phase IQR of CAGR: **2.545 pp**; the flip's median effect is +1.25pp -- inside the noise.

## The flip across every cell

cells | return up | Sharpe not worse | OOS not worse | median dCAGR | median dSharpe | median dOOS | worst | best
|---|---|---|---|---|---|---|---|---|
20 | 85% | 75% | 75% | +1.25pp | +0.067 | +3.19pp | -2.63pp | +6.05pp

## Per-cell detail (flip vs its own frozen-sign control)

| book | phase | dCAGR | dSharpe | dOOS | dTurnover | dMaxDD |
|---|---|---|---|---|---|---|
| n5_r20 | 2020-01-02 | +0.87pp | +0.004 | +0.72pp | +0.207 | -0.45pp |
| n5_r20 | 2020-01-09 | +0.55pp | +0.070 | -2.11pp | +0.096 | +4.81pp |
| n5_r20 | 2020-01-16 | +0.51pp | +0.035 | +2.18pp | +0.255 | -0.01pp |
| n5_r20 | 2020-01-23 | +5.33pp | +0.381 | +7.28pp | +0.164 | -1.07pp |
| n5_r10 | 2020-01-02 | +1.27pp | +0.069 | +4.79pp | +0.214 | +4.24pp |
| n5_r10 | 2020-01-09 | +2.46pp | +0.039 | -4.73pp | +0.142 | +1.62pp |
| n5_r10 | 2020-01-16 | +1.22pp | +0.064 | +4.79pp | +0.213 | +4.24pp |
| n5_r10 | 2020-01-23 | +2.10pp | -0.067 | -4.73pp | +0.143 | +1.62pp |
| n5_r40 | 2020-01-02 | -2.63pp | -0.297 | +3.95pp | +0.133 | -18.78pp |
| n5_r40 | 2020-01-09 | +6.05pp | +0.576 | +12.59pp | +0.029 | +4.32pp |
| n5_r40 | 2020-01-16 | +2.68pp | +0.302 | +3.87pp | +0.257 | +0.77pp |
| n5_r40 | 2020-01-23 | +5.82pp | +0.477 | +7.97pp | +0.229 | -6.53pp |
| n3_r20 | 2020-01-02 | +3.72pp | +0.292 | +3.45pp | +0.241 | +7.60pp |
| n3_r20 | 2020-01-09 | +0.69pp | +0.004 | +0.73pp | +0.129 | -3.11pp |
| n3_r20 | 2020-01-16 | +0.92pp | +0.080 | -1.45pp | +0.257 | -1.55pp |
| n3_r20 | 2020-01-23 | +4.52pp | +0.329 | +3.50pp | +0.257 | -4.95pp |
| n8_r20 | 2020-01-02 | -1.24pp | -0.152 | +2.94pp | +0.175 | -13.22pp |
| n8_r20 | 2020-01-09 | -1.91pp | -0.247 | -0.42pp | +0.120 | -13.02pp |
| n8_r20 | 2020-01-16 | +1.85pp | +0.121 | +2.65pp | +0.181 | -5.85pp |
| n8_r20 | 2020-01-23 | +0.84pp | -0.062 | +5.05pp | +0.172 | -17.37pp |

## Frozen criteria

```
{
  "books": [
    [
      5,
      20
    ],
    [
      5,
      10
    ],
    [
      5,
      40
    ],
    [
      3,
      20
    ],
    [
      8,
      20
    ]
  ],
  "n_phases": 4,
  "phase_rebal": 20,
  "bar_pp": 0.5,
  "share_up_min": 0.75,
  "sharpe_ok_min": 0.75,
  "identity_tol_bp": 5.0,
  "frozen": "constants above were written before the first run; --check refuses a face that echoes others"
}
```

## Caveats

* exploratory: no preregistration, no ledger booking; no production config changes here
* cells share one panel and overlap in time -- the sign test counts cells, not independent bets
* the flip is chosen after the yearly table was read (6 factors examined, 1 flattering arm printed); the cell grid prices that arm, it does not undo the selection risk
* one panel / one cost model / 8bp per side; survivor pool and the 2020-2023 regime caveats of the underlying book are unchanged
* the ice is the drawdown_60 factor only: a flip of a DRIFT factor is a different question
