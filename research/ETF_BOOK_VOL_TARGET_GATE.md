# ETF book -- does a vol target clear the calendar today?

As-of 2026-11-18. Verdict: **STILL_REFUSED** -- no arm clears it; the wait in r1428 is not a scaling artifact

| arm | vol target | verdict | median CAGR | median Sharpe | median maxDD | turnover |
|---|---|---|---|---|---|---|
| unscaled | None | REFUSED | 14.04% | 0.937 | -18.07% | 1.54 |
| vt08 | 0.08 | REFUSED | 8.42% | 0.876 | -12.99% | 1.08 |
| vt06 | 0.06 | REFUSED | 6.27% | 0.841 | -9.97% | 0.85 |
| vt04 | 0.04 | REFUSED | 4.2% | 0.812 | -6.69% | 0.57 |
| vt03 | 0.03 | REFUSED | 3.17% | 0.812 | -5.05% | 0.43 |
| vt02 | 0.02 | REFUSED | 2.13% | 0.812 | -3.39% | 0.28 |

## Does scaling move the ruler?

* **effective_years** -- max |d| across 25 phase pairs = 0.852585, arm median range 0.41946. scaling does move this ruler (max |d| 0.852585) but the arm median moves 0.41946 and no arm admits: de-risking is not an admission lever here
* **years_for_half** -- max |d| across 25 phase pairs = 1.0, arm median range 0.0. scaling does move this ruler (max |d| 1.0) but the arm median moves 0.0 and no arm admits: de-risking is not an admission lever here

## Why each arm was refused

* **unscaled** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.652379 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt08** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.970427 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt06** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.849168 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt04** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.577083 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt03** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.550967 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED
* **vt02** -- gate CAPACITY_LIMITED; ruler FAIL years_for_half
  - rulers: effective_years median 4.595888 vs line 3.0 (PASS); years_for_half median 2.0 vs line 3 (FAIL)
  - gate verdicts per phase: CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED, CAPACITY_LIMITED

Money face is published beside every verdict on purpose: a scaling that clears the calendar by earning nothing is not supply, and one that earns by concentrating the year is exactly what the elected ruler refuses.
