# BigMoney QA self-verification r771

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 93 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.1586 annual=0.0056 maxdd=-0.0433 win_rate=0.4624 trades=93
- [x] 3. equity curve png -- equity-curve-r771.png
- [x] 4. live-signal generation clean -- market_clock_call run rc=0 (idempotent same-day regen, cell=ORANGE_COOL; r771 adopted chain leg)
- [x] 5. data pull healthy -- latest panel bar 2026-09-30 (golden-week no-op until 10-09); S6 35-leg chain rc0 receipts in round report (dead r771 session 10:00-10:04, adopted this round)

## evidence pointers

- chart: equity-curve-r771.png
- raw log: smoke-r771.log
