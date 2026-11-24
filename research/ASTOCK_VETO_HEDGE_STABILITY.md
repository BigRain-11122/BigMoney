# Does the carrier flip survive cutting the window up?

r2036 put both carriers of this hedge on a funded ruler and the family has been quoting the result since: **THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT** -- gross the ETF short leads by 0.08pp, net of the lender it trails by 1.91pp, and once the collateral is charged it trails by 2.87pp. A flip is a claim about the sign of a difference, and a sign computed on 52 periods is exactly the kind of number a sample can manufacture. This face cuts the same 52 periods five ways and asks whether the futures leg stays in front.

Evidence cutoff **2026-11-20**. 52 periods (2022-07-26 .. 2026-11-11), 12.6 periods a year, reference cell k=1.0, haircut 100%, rent 2.00%. Parents: beta `results/astock_veto_hedgeable_beta.json`, carrier `results/astock_veto_hedge_carrier.json`, funding `results/astock_veto_hedge_funding.json`.

## 1. The anchor

| window | periods | IM annual | ETF annual | gap (annualised) | gap (cumulative) |
|---|---|---|---|---|---|
| all 52 | 52 | 9.39% | 6.52% | 2.87pp | 15.03pp |

The annualised gap here is the number r2036 published (2.87pp); the cumulative one is what the sign test below uses, because annualising a 13-period block turns a rounding difference into a percentage point.

## 2. Two halves and in/out of sample

| cut | periods | from | to | IM annual | ETF annual | gap annualised | gap cumulative |
|---|---|---|---|---|---|---|---|
| first_half | 26 | 2022-07-26 | 2024-09-12 | 10.05% | 7.01% | 3.04pp | 6.85pp |
| second_half | 26 | 2024-09-12 | 2026-11-11 | 8.73% | 6.04% | 2.69pp | 5.99pp |
| in_sample | 18 | 2022-07-26 | 2024-01-16 | 14.10% | 10.04% | 4.06pp | 6.08pp |
| out_of_sample | 34 | 2024-01-16 | 2026-11-11 | 6.97% | 4.70% | 2.27pp | 6.75pp |

The parent's `in_sample` flag is the fitted part of the window and the out-of-sample piece is everything after it; if the flip only existed in the fitted half it would be a description of the fit, not of the hedge.

## 3. Quarter blocks (13 periods each)

| block | periods | from | to | IM annual | ETF annual | gap annualised | gap cumulative |
|---|---|---|---|---|---|---|---|
| Q1 | 13 | 2022-07-26 | 2023-08-18 | 12.74% | 9.50% | 3.24pp | 3.35pp |
| Q2 | 13 | 2023-08-18 | 2024-09-12 | 7.43% | 4.57% | 2.86pp | 2.95pp |
| Q3 | 13 | 2024-09-12 | 2025-10-16 | 13.49% | 8.58% | 4.91pp | 5.08pp |
| Q4 | 13 | 2025-10-16 | 2026-11-11 | 4.17% | 3.56% | 0.61pp | 0.63pp |

Thirteen periods is the shortest block that still spans a year at 12.6 periods a year, and it is the noisiest cut here. The annualised column is printed for completeness; the cumulative column is the one a sign is read off.

## 4. Rolling 26-period windows (stride 1)

| windows | IM leads | share | cumulative gap min | median | max | annualised min | median | max |
|---|---|---|---|---|---|---|---|---|
| 27 | 27 | 100.00% | 3.32pp | 7.02pp | 11.05pp | 1.56pp | 3.13pp | 4.79pp |

The 27 windows overlap by 25 of 26 periods, so the share is a description of the path and not 27 independent trials; no multiplicity correction is claimed.

## 5. Period-level sign test

| periods | IM periods | ETF periods | IM share | two-sided binomial p | mean per-period difference |
|---|---|---|---|---|---|
| 52 | 34 | 18 | 65.38% | 0.0365 | 0.22pp |

## 6. Drop-one jackknife

| periods | full gap | min | max | largest move | worst period dropped | all positive |
|---|---|---|---|---|---|---|
| 52 | 2.87pp | 2.30pp | 3.37pp | 0.56pp | 2025-06-18 | yes |

## 7. The deposit rate the flip needs

r2036's second caveat was that the frozen balance may earn less than the declared 2% -- a short-sale proceeds balance is often frozen outright. That is not a reason to doubt the flip unless the flip moves inside the range a broker could pay, so this section sweeps the yield and solves for the tie.

| declared cash yield | gap (IM minus ETF) |
|---|---|
| 0.00% | 3.24pp |
| 2.00% | 2.87pp |
| 4.00% | 2.48pp |
| 6.00% | 2.10pp |
| 8.00% | 1.70pp |
| 10.00% | 1.30pp |

**Break-even: 16.34%.** the two carriers tie at a cash yield of 16.34%. The funded book return the comparison is measured against is 9.39%.

## 8. Verdict

**`THE_FLIP_IS_A_PROPERTY_OF_THE_RULE+THE_FLIP_IS_NARROWING+THE_FLIP_DOES_NOT_NEED_A_DEPOSIT_RATE`**

Every flag below is computed from its own inputs and several can hold at once; the headline names the ones that change what a reader would do.

- `THE_FLIP_IS_A_PROPERTY_OF_THE_RULE` -- every cut of the same 52 periods puts the futures leg in front, so the ordering is carried by the rule and not by where the sample starts or ends
- `THE_FLIP_IS_NARROWING` -- the sign is stable but the size is not: the most recent block is less than half the median block, so a reader who trades on the flip is trading on a gap that has been shrinking for a year
- `THE_FLIP_DOES_NOT_NEED_A_DEPOSIT_RATE` -- the frozen cash would have to earn more than the book itself returns before the two carriers tie, which no deposit pays -- the flip does not depend on the declared cash yield

## 9. Readings

- **R1.** the anchor reproduces: on all 52 periods the funded gap is 2.87pp (IM minus ETF), against the 286.66pp r2036 published -- the cut below starts from the same number, so this face is a decomposition and not a re-derivation
- **R2.** cut in half, the two halves agree: 3.04pp (first_half) and 2.69pp (second_half) on the annualised ruler, 6.85pp / 5.99pp on the cumulative one
- **R3.** and the parent's own in-sample / out-of-sample split agrees with the headline: 6.08pp in sample and 6.75pp out of it (cumulative), so the flip is not an artefact of the fitted part of the window
- **R4.** the 4 quarter blocks (13 periods each) run Q1 3.35pp, Q2 2.95pp, Q3 5.08pp, Q4 0.63pp -- 4 of 4 favour the futures leg; the annualised numbers on a 13-period block are noisy by construction, which is why the sign test below uses the cumulative one
- **R4b.** the flip is stable in sign and shrinking in size: the last block (2025-10-16 .. 2026-11-11) pays 0.61pp against a median block of 3.05pp, and it is the only block inside the 1.0pp tie band -- a reader who trades the flip forward is trading a gap that has been narrowing for a year
- **R5.** 27 rolling 26-period windows (stride 1) put the futures leg in front in 27 of them (100.00%); the cumulative gap runs 3.32pp .. 11.05pp with a median of 7.02pp, so the full-window number is a middle case and not the best window
- **R6.** period by period the futures leg wins 34 of 52 (65.38%) with a two-sided binomial p of 0.0365 -- a real bias, not a coin
- **R7.** the drop-one jackknife moves the gap by at most 0.56pp (dropping 2025-06-18) and the gap stays positive in all of the 52 single-period removals -- the headline does not rest on a single observation
- **R8.** sweeping the collateral's declared yield from 0.00% to 10.00% moves the gap from 3.24pp to 1.30pp -- the flip survives the whole range
- **R9.** the frozen cash would have to earn 16.34% a year for the two carriers to tie, against a funded book return of 9.39% -- the collateral assumption r2036 could not observe cannot overturn the conclusion, because no broker pays above the book

## 10. What this face does not settle

- every cut is a cut of the same 52 periods, so this face says the flip does not depend on where inside those 52 you start -- it cannot say the 52 are a fair sample of the regime
- the 13-period quarter blocks annualise 13 observations; their annualised gap is printed for completeness and the sign test runs on the cumulative gap for that reason
- rolling windows overlap by 25 of 26 periods, so the 27 windows are not 27 independent trials and no multiplicity correction is claimed for the share
- cash yield is swept inside the funding identity r2036 published; a broker that pays a tiered rate, or freezes the balance outright, is a different curve, not a different break-even
- the reference case is k=1, the full haircut and the cheapest rent, exactly r2036's headline cell; the other k and haircut cells are not re-cut here
- the window still starts where the IM panel starts (2022-07), so a regime that only exists after that date is inside every piece
- a stable sign is not a stable size: this face tests the ordering of the two carriers, not whether either return is worth committing capital to

Machine `bm-c`, generated 2026-11-24T08:35:39+08:00.

## 11. Reproduction

```
python scripts/astock_veto_hedge_stability.py selftest
python scripts/astock_veto_hedge_stability.py run
python scripts/astock_veto_hedge_stability.py check
```
