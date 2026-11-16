# ETF book -- does a vol target clear the calendar today?

As-of 2026-11-16. Verdict: **STILL_REFUSED** -- no arm clears it; the wait in r1428 is not a scaling artifact

| arm | vol target | verdict | median CAGR | median Sharpe | median maxDD | turnover |
|---|---|---|---|---|---|---|
| unscaled | None | REFUSED | 14.05% | 0.938 | -18.07% | 1.54 |
| vt08 | 0.08 | REFUSED | 8.43% | 0.877 | -12.99% | 1.08 |
| vt06 | 0.06 | REFUSED | 6.3% | 0.842 | -9.97% | 0.85 |
| vt04 | 0.04 | REFUSED | 4.22% | 0.812 | -6.69% | 0.57 |
| vt03 | 0.03 | REFUSED | 3.19% | 0.812 | -5.05% | 0.43 |
| vt02 | 0.02 | REFUSED | 2.13% | 0.812 | -3.39% | 0.28 |

## Does scaling move the ruler?

* **effective_years** -- max |d| across 25 phase pairs = 0.85295, arm median range 0.424674. scaling does move this ruler (max |d| 0.85295) but the arm median moves 0.424674 and no arm admits: de-risking is not an admission lever here
* **years_for_half** -- max |d| across 25 phase pairs = 1.0, arm median range 0.0. scaling does move this ruler (max |d| 1.0) but the arm median moves 0.0 and no arm admits: de-risking is not an admission lever here

## Why each arm was refused

* **unscaled** -- gate CONDITIONAL,REFUSE; ruler FAIL years_for_half
  - rulers: effective_years median 4.654482 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: ADMIT, ADMIT, REFUSE, CONDITIONAL, CONDITIONAL
* **vt08** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.995503 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt06** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.874988 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt04** -- gate CONDITIONAL,REFUSE; ruler FAIL years_for_half
  - rulers: effective_years median 4.603678 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, REFUSE, CONDITIONAL
* **vt03** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.570829 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: ADMIT, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt02** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.623249 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: ADMIT, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL

Money face is published beside every verdict on purpose: a scaling that clears the calendar by earning nothing is not supply, and one that earns by concentrating the year is exactly what the elected ruler refuses.
