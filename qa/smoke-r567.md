# BigMoney QA self-verification r567

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 93 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.159 annual=0.0056 maxdd=-0.0433 win_rate=0.4624 trades=93
- [x] 3. equity curve png -- equity-curve-r567.png
- [x] 4. live-signal generation clean -- market_clock_call run rc=0 (idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar 2026-09-30; S6 38-leg chain rc0 receipts in round report

## evidence pointers

- chart: equity-curve-r567.png
- raw log: smoke-r567.log
