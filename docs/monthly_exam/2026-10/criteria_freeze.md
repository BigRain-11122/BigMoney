# Monthly exam 2026-10 -- criteria face: exam criteria freeze

- ticket: T-2026-10-01-143 face 5 (O-20261001-2355 sec.3)
- freeze: single-source import (firm/hr.py @ sha16 d7bb7eca9cd59abf, science_gates signature defaults via inspect); zero hand-copying
- identity anchor: g2_registration_v2 dsr_gate=0.95 pbo_gate=0.25 (already-registered roster; exam does not reopen)
- reform standing standard: batch-internal BH FDR q=0.1 (W14+ verdict face, additive only)

## Promotion thresholds (firm/hr.py THRESHOLDS, single-source)

| ladder | thresholds |
|---|---|
| INTERN_TO_TRAINEE | max_dd_max=0.25, os_sharpe_min=0.8, paper_months_min=1, trades_min=30 |
| SENIOR_TO_PRINCIPAL | max_dd_max=0.15, months_min=12, sharpe_min=1.5 |
| TRADER_TO_SENIOR | months_min=6, sharpe_min=1.0 |
| TRAINEE_TO_TRADER | max_dd_max=0.15, months_min=3, win_rate_min=0.55 |

## Fire rules

| rule | line | source |
|---|---|---|
| ic_decay | IC衰减>50% | firm/hr.py FIRE_REASONS |
| live_monthly_loss | 实盘单月亏>8% | firm/hr.py FIRE_REASONS |
| paper_dd | 模拟盘回撤>20% | firm/hr.py FIRE_REASONS |
| risk_violation | 违反风控 | firm/hr.py FIRE_REASONS |
| paper_dd | -0.2 (TRAINEE current_dd) | hr._evaluate_level inline (inspect-verified) |
| monthly_loss | -0.08 (TRADER last month) | hr._evaluate_level inline (inspect-verified) |

## Honesty anchors

- window_metrics status=insufficient_data (bars<20 suppression per D-20260930-27 Q3) is carried in the JSON face and must never be quoted as annualized stats
- x2_watch probation status is reported as-is (roster baseline carries it); probation is disclosed, never hidden behind aggregate rows
- negative results reported as-is, no makeup (T-143 spec verbatim)
- PROSPECT accounts are observation-lane (O-2045 constructive exclusion from the CEO face) -- never scored in exam tables
- anchor IS/OOS block = hire-time registration anchor, not exam evidence

## Benchmark double-line (carried from roster baseline, no recompute)

- 510300 month-open close: 4.432
