# ETF book -- does a vol target clear the calendar today?

As-of 2026-11-20. Verdict: **STILL_REFUSED** -- no arm clears it; the wait in r1428 is not a scaling artifact

| arm | vol target | verdict | median CAGR | median Sharpe | median maxDD | turnover |
|---|---|---|---|---|---|---|
| unscaled | None | REFUSED | 13.74% | 0.92 | -18.07% | 1.54 |
| vt08 | 0.08 | REFUSED | 8.19% | 0.853 | -12.99% | 1.08 |
| vt06 | 0.06 | REFUSED | 6.09% | 0.819 | -9.97% | 0.85 |
| vt04 | 0.04 | REFUSED | 4.03% | 0.79 | -6.69% | 0.57 |
| vt03 | 0.03 | REFUSED | 3.04% | 0.79 | -5.05% | 0.43 |
| vt02 | 0.02 | REFUSED | 2.03% | 0.79 | -3.39% | 0.28 |

## Does scaling move the ruler?

* **effective_years** -- max |d| across 25 phase pairs = 0.851818, arm median range 0.421265. scaling does move this ruler (max |d| 0.851818) but the arm median moves 0.421265 and no arm admits: de-risking is not an admission lever here
* **years_for_half** -- max |d| across 25 phase pairs = 1.0, arm median range 0.0. scaling does move this ruler (max |d| 1.0) but the arm median moves 0.0 and no arm admits: de-risking is not an admission lever here

## Why each arm was refused

* **unscaled** -- gate CONDITIONAL,REFUSE; ruler FAIL years_for_half
  - rulers: effective_years median 4.706452 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: ADMIT, ADMIT, REFUSE, CONDITIONAL, CONDITIONAL
* **vt08** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 5.040978 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt06** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.921739 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt04** -- gate CONDITIONAL,REFUSE; ruler FAIL years_for_half
  - rulers: effective_years median 4.651912 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, REFUSE, CONDITIONAL
* **vt03** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.619713 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt02** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.67271 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL

Money face is published beside every verdict on purpose: a scaling that clears the calendar by earning nothing is not supply, and one that earns by concentrating the year is exactly what the elected ruler refuses.
