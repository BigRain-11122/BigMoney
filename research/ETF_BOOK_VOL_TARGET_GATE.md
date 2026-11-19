# ETF book -- does a vol target clear the calendar today?

As-of 2026-11-19. Verdict: **STILL_REFUSED** -- no arm clears it; the wait in r1428 is not a scaling artifact

| arm | vol target | verdict | median CAGR | median Sharpe | median maxDD | turnover |
|---|---|---|---|---|---|---|
| unscaled | None | REFUSED | 14.0% | 0.935 | -18.07% | 1.54 |
| vt08 | 0.08 | REFUSED | 8.39% | 0.873 | -12.99% | 1.08 |
| vt06 | 0.06 | REFUSED | 6.24% | 0.838 | -9.97% | 0.85 |
| vt04 | 0.04 | REFUSED | 4.14% | 0.809 | -6.69% | 0.57 |
| vt03 | 0.03 | REFUSED | 3.12% | 0.809 | -5.05% | 0.43 |
| vt02 | 0.02 | REFUSED | 2.09% | 0.809 | -3.39% | 0.28 |

## Does scaling move the ruler?

* **effective_years** -- max |d| across 25 phase pairs = 0.852717, arm median range 0.423999. scaling does move this ruler (max |d| 0.852717) but the arm median moves 0.423999 and no arm admits: de-risking is not an admission lever here
* **years_for_half** -- max |d| across 25 phase pairs = 1.0, arm median range 0.0. scaling does move this ruler (max |d| 1.0) but the arm median moves 0.0 and no arm admits: de-risking is not an admission lever here

## Why each arm was refused

* **unscaled** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.653384 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt08** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.97606 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt06** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.854966 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt04** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.583048 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt03** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.552061 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt02** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.602024 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED

Money face is published beside every verdict on purpose: a scaling that clears the calendar by earning nothing is not supply, and one that earns by concentrating the year is exactly what the elected ruler refuses.
