# The ladder's risk column, measured

generated 2026-11-25T22:32:51+08:00 | cutoff 2026-11-25 | schema `idx-fut-carry-ladder-risk/v1`

## One sentence

`research/POLICY_RETURN_LADDER.md` prices every rung's return in money and every rung's risk in two constants (`L2_CARRY_VOL` 4.0 %/yr per unit notional, `RHO` 0.10); measured on the legs' own daily spreads the instructed rung draws **13.66% vol / -11.06% max drawdown**, so the declared number is **DECLARED_RISK_UNDERSTATES_MEASURED** (3.20 pp).

## What was measured, and on what

| input | declared | measured |
|---|---|---|
| IC leg vol (%/yr of notional) | 4.0 | **5.92** |
| IM leg vol (%/yr of notional) | 4.0 | **6.82** |
| IC/IM correlation | 0.10 | **0.833** |
| equity sleeve vs futures | 0.10 | **-0.038** |

Both legs quote on 1052 common days; one lot is 1153800 CNY (IC) / 1086880 CNY (IM), read out of the ladder's own rungs.

## Every rung, return and risk on the same ruler

| IC/IM lots | expected %/yr | declared vol% | measured vol% | delta pp | measured MDD% | measured Sharpe |
|---|---|---|---|---|---|---|
| 0/0 | 5.17 | 4.57 | **1.85** | -2.72 | -2.07 | 0.73 |
| 0/1 *(in band)* | 9.05 | 6.61 | **7.53** | +0.92 | -5.41 | 1.66 |
| 0/2 | 12.94 | 10.22 | **14.83** | +4.61 | -10.67 | 1.63 |
| 0/3 | 16.82 | 14.24 | **22.21** | +7.97 | -15.73 | 1.64 |
| 1/0 | 13.49 | 6.81 | **6.99** | +0.18 | -6.58 | 1.35 |
| 1/1 **<- instruction** | 17.38 | 10.46 | **13.66** | +3.20 | -11.06 | 1.53 |
| 1/2 | 21.26 | 14.50 | **20.84** | +6.33 | -16.13 | 1.58 |
| 1/3 | 25.14 | 18.68 | **28.14** | +9.46 | -20.99 | 1.61 |
| 2/0 | 21.81 | 10.70 | **13.70** | +3.00 | -12.87 | 1.28 |
| 2/1 | 25.70 | 14.75 | **20.24** | +5.49 | -17.24 | 1.45 |
| 2/2 | 29.58 | 18.94 | **27.23** | +8.29 | -21.77 | 1.53 |
| 2/3 | 33.46 | 23.18 | **34.40** | +11.22 | -26.21 | 1.58 |
| 3/0 | 30.14 | 15.01 | **20.48** | +5.47 | -19.00 | 1.26 |
| 3/1 | 34.02 | 19.20 | **26.94** | +7.74 | -23.36 | 1.40 |
| 3/2 | 37.90 | 23.44 | **33.80** | +10.36 | -27.68 | 1.49 |
| 3/3 | 41.78 | 27.72 | **40.85** | +13.13 | -31.87 | 1.54 |

## The three judgments

1. **Declared vs measured vol** — `DECLARED_RISK_UNDERSTATES_MEASURED` (declared 10.46 pp vs measured 13.66 pp on the instructed rung).
2. **Does cutting to the band cut risk?** — `BAND_CUT_ALSO_CUTS_RISK`: the in-band rung (0/1) draws down **-5.41%** against the instruction's **-11.06%** (gap +5.66 pp).
3. **Return vs risk ranking** — `SHARPE_DISAGREES_WITH_RETURN`: best measured Sharpe is [0, 1], best expected return is [3, 3].

## What this face does NOT do

* it does not re-derive a leg: the spreads come from `idx_fut_carry_risk.product_spread` by import;
* it does not size the equity sleeve: that stays the ladder's `k`;
* it does not touch the ladder itself — the ladder is the published face and a CONTENTION round may not rewrite shared faces; rebasing its two constants onto these measurements is a separate, clean-window job;
* `check` re-probes the two futures legs but only digests the equity arm.

## Usage

```
python scripts/idx_fut_carry_ladder_risk.py run
python scripts/idx_fut_carry_ladder_risk.py check
python scripts/idx_fut_carry_ladder_risk.py --selftest
```
