# ETF book -- does a vol target clear the calendar today?

As-of 2026-11-26. Verdict: **STILL_REFUSED** -- no arm clears it; the wait in r1428 is not a scaling artifact

| arm | vol target | verdict | median CAGR | median Sharpe | median maxDD | turnover |
|---|---|---|---|---|---|---|
| unscaled | None | REFUSED | 13.39% | 0.9 | -18.07% | 1.54 |
| vt08 | 0.08 | REFUSED | 7.92% | 0.828 | -13.37% | 1.08 |
| vt06 | 0.06 | REFUSED | 5.98% | 0.794 | -10.24% | 0.85 |
| vt04 | 0.04 | REFUSED | 4.01% | 0.766 | -6.9% | 0.57 |
| vt03 | 0.03 | REFUSED | 3.03% | 0.766 | -5.2% | 0.43 |
| vt02 | 0.02 | REFUSED | 2.03% | 0.766 | -3.49% | 0.28 |

## Does scaling move the ruler?

* **effective_years** -- max |d| across 25 phase pairs = 0.846774, arm median range 0.413409. scaling does move this ruler (max |d| 0.846774) but the arm median moves 0.413409 and no arm admits: de-risking is not an admission lever here
* **years_for_half** -- max |d| across 25 phase pairs = 1.0, arm median range 1.0. scaling does move this ruler (max |d| 1.0) but the arm median moves 1.0 and no arm admits: de-risking is not an admission lever here

## Why each arm was refused

* **unscaled** -- gate CONDITIONAL,REFUSE; ruler FAIL years_for_half
  - rulers: effective_years median 4.775456 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, ADMIT, REFUSE, CONDITIONAL, CONDITIONAL
* **vt08** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 5.093344 vs line 3.0 (PASS); years_for_half median 1.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt06** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.975651 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt04** -- gate CONDITIONAL,REFUSE; ruler FAIL years_for_half
  - rulers: effective_years median 4.707942 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, REFUSE, CONDITIONAL
* **vt03** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.679935 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL
* **vt02** -- gate CONDITIONAL; ruler FAIL years_for_half
  - rulers: effective_years median 4.730064 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL, CONDITIONAL

Money face is published beside every verdict on purpose: a scaling that clears the calendar by earning nothing is not supply, and one that earns by concentrating the year is exactly what the elected ruler refuses.
