# Monthly exam 2026-10 -- six-face assembly (T-2 deliverable)

- ticket: T-2026-10-01-143; exam 2026-10-31; deliverable 2026-10-29
- month-open bar: 2026-09-30; accounts swept: 63; paired deltas: 41
- marks floor: 2026-10-27 (exam requirement 2026-10-30; met=False)
- what this is: month-open baseline vs latest marks, per account and per family. A level readout, not an annualized statistic.

## Six employees (month-to-date vs 2026-09-30 month-open equity)

| employee | asof | equity_open_cny | equity_now_cny | mtd_pct |
|---|---|---:|---:|---:|
| COMPOSITE-CE-01 | 2026-10-27 | 1001009.96 | 992438.77 | -0.8563 |
| COMPOSITE-CE-02 | 2026-10-27 | 1000665.47 | 986712.79 | -1.3943 |
| DROUGHT-CE-01 | 2026-10-27 | 1000000.0 | 993853.07 | -0.6147 |
| ENGULF-CE-01 | 2026-10-27 | 1000000.0 | 991773.45 | -0.8227 |
| NEEDLE-DE-01 | 2026-10-27 | 1000000.0 | 1000000.0 | 0.0 |
| VOLATILITY-CE-01 | 2026-10-27 | 996820.33 | 995040.32 | -0.1786 |

## Harness families

| family | n | up | mean_mtd_pct |
|---|---:|---:|---:|
| AGGR | 20 | 1 | -0.5412 |
| ALLOC | 7 | 0 | -2.5124 |
| B_MAXDIV | 1 | 0 | -0.6448 |
| EMPLOYEE | 6 | 0 | -0.6444 |
| GRID | 5 | 1 | -2.6835 |
| SYSV1 | 2 | 0 | -1.9624 |

## Owner-lane faces (read-only aggregation, faces 2/3)

| face | name | status | asof | mtd_pct | artifact |
|---|---|---|---|---:|---|
| 2 | SYSTEM-V1 | PRESENT (read-only, owner lane) | 2026-10-20 | -0.903 | results/system_v1_paper/SYSTEM-V1_paper.json |
| 3 | REV-OSC | PRESENT (read-only, owner lane) | 2026-10-20 | -3.0218 | results/system_v1_paper/REV-OSC-STD_paper.json |

## Frozen face fingerprints (drift = gate red, version a new file)

- `accounts_monthopen_baseline.json` sha16=0d61233fbc60e485
- `roster_monthopen_baseline.json` sha16=c5e1e273e9e1ed93
- `criteria_freeze.json` sha16=9a7b925a0b93e954

## Gaps

- owner-lane face SYSTEM-V1 is at 2026-10-20 while the panel floor is 2026-10-27 -- an exam-day readout off this face would be stale; its owner lane must refresh before 10-30
- owner-lane face REV-OSC is at 2026-10-20 while the panel floor is 2026-10-27 -- an exam-day readout off this face would be stale; its owner lane must refresh before 10-30
- marks floor 2026-10-27 < exam requirement 2026-10-30 (legal: bars stop there; re-run at freeze_eve after the last full bar)

## Notes

- PROS/PROS-ANTS-01 has no month-open baseline row
- PROS/PROS-ANTS-CE-01 has no month-open baseline row
- PROS/PROS-BBS-01 has no month-open baseline row
- PROS/PROS-BBS-CE-01 has no month-open baseline row
- PROS/PROS-DOJI-01 has no month-open baseline row
- PROS/PROS-DOJI-CE-01 has no month-open baseline row
- PROS/PROS-DUCK-01 has no month-open baseline row
- PROS/PROS-DUCK-CE-01 has no month-open baseline row
- PROS/PROS-HAM-01 has no month-open baseline row
- PROS/PROS-HAM-CE-01 has no month-open baseline row
- PROS/PROS-IBB-01 has no month-open baseline row
- PROS/PROS-IBB-CE-01 has no month-open baseline row
- PROS/PROS-IMM-01 has no month-open baseline row
- PROS/PROS-IMM-CE-01 has no month-open baseline row
- PROS/PROS-MCB-01 has no month-open baseline row
- PROS/PROS-MCB-CE-01 has no month-open baseline row
- PROS/PROS-OVB-01 has no month-open baseline row
- PROS/PROS-OVB-CE-01 has no month-open baseline row
- PROS/PROS-RSRS-CE-01 has no month-open baseline row
- PROS/PROS-TMU-01 has no month-open baseline row
- PROS/PROS-TMU-CE-01 has no month-open baseline row
- PROS/PROS-VOB-CE-01 has no month-open baseline row

## Honesty anchors

month-to-date pct is a level readout, not an annualized statistic (D-20260930-27 Q3 window_metrics suppression); PROSPECT observation-lane accounts carry no equity face (O-2045) and are never scored here; negative results reported as-is, no makeup
