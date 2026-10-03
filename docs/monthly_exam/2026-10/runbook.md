# Monthly exam 2026-10 -- runbook face: date-driven exam-day assembly

- ticket: T-2026-10-01-143 face 6 (O-20261001-2355 sec.3)
- exam date: 2026-10-31 (month-boundary first exam); T-2 deliverable: 2026-10-29
- phase TODAY (2026-10-03): capture_window_open
- law: exam day = pure aggregation, zero new judgment (T-105 one-pager precedent); this file regenerates (asof_date inside), NOT a frozen baseline

## Phase schedule

| phase | window | action |
|---|---|---|
| capture_window_open | until 2026-10-08 | month-open baselines captured during golden week (DONE r405-r407); do-not-overwrite |
| assembly_window | 2026-10-09 .. 2026-10-29 | capture gates close 10-09 (rc2 = verify-only signal, correct); faces 2/3 assembly on owner lanes; T-2 deliverable 10-29 |
| freeze_eve | 2026-10-30 | verify-only: selftest + runbook regeneration, all six faces PRESENT, no new artifacts |
| exam_day | 2026-10-31 | EXAM: pure aggregation, zero new judgment, no new burns (T-143 spec face 6 verbatim) |
| post_exam | 2026-11-01 .. | results readout; any change to frozen faces = version a new file, never edit in place |

## Six-face status (sha256-16 fingerprints regenerated at write time)

| # | face | owner lane | status | assembly command |
|---|---|---|---|---|
| 1 | roster | bm-c (T-143 owner) | FROZEN sha16=c5e1e273e9e1ed93 | python scripts/monthly_exam_prep.py roster --month 2026-10 |
| 2 | SYSTEM-V1 | bm-a primary (SYSTEM_V1_PREREG author precedent) | PENDING (assembly window) | bm-a lane: system_v1_paper month readout (assembly command lands with the face) |
| 3 | REV-OSC | family-owner lane (ETF oversold-rebound family) | PENDING (assembly window) | family-owner lane: rev_osc state assembly (assembly command lands with the face) |
| 4 | accounts | bm-c (T-143 owner) | FROZEN sha16=9cddb73e51a5fd91 | python scripts/monthly_exam_prep.py baseline --month 2026-10 |
| 5 | criteria | bm-c (T-143 owner) | FROZEN sha16=9a7b925a0b93e954 | python scripts/monthly_exam_prep.py criteria --month 2026-10 |
| 6 | runbook | bm-c (this generator, T-143 owner) | ACTIVE (this generator; self-excluded from fingerprints) | python scripts/monthly_exam_prep.py runbook --month 2026-10 |

## Exam-day sequence (zero new judgment)

1. regenerate this runbook (python scripts/monthly_exam_prep.py runbook --month 2026-10); phase must read exam_day
2. verify frozen fingerprints: roster/accounts/criteria sha256-16 values must equal the values recorded here; drift = gate red, version a new file, never edit in place
3. six-face assembly: roster + accounts + criteria frozen (no re-capture); SYSTEM-V1 + REV-OSC readouts come from their owner lanes
4. promotion/demotion evaluation: firm/hr.py THRESHOLDS + FIRE rules exactly as frozen in the criteria face (single-source, zero hand-tuning on exam day)
5. honest reporting: negative results as-is; PROS observation-lane excluded from the CEO face; insufficient_data stats never quoted as annualized
6. output: exam one-pager under docs/monthly_exam/2026-10/ (T-105 one-pager precedent) + freeze receipt committed

## Gates (verbatim law echoes)

- zero new judgment on exam day (pure aggregation, T-143 spec face 6 verbatim)
- no new burns on exam day (T-143 spec: prep/aggregation only; any judged work rides its own prereg per TRIAL_LABOR_LAW)
- baselines do-not-overwrite after 2026-10-09; capture gates rc2 after that date = verify-only signal, never worked around
- PROSPECT accounts are observation-lane (O-2045) -- never scored in exam tables
- window_metrics insufficient_data suppression (D-20260930-27 Q3) carried, never quoted as annualized stats
- negative results reported as-is, no makeup
