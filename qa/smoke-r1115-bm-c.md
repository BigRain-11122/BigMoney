# BigMoney QA self-verification r1115

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 90 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.209 annual=0.0076 maxdd=-0.0431 win_rate=0.4778 trades=90
- [x] 3. equity curve png -- equity-curve-r1115-bm-c.png
- [x] 4. live-signal generation clean -- market_clock_call run rc=0 (idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar 2026-10-16; S6 chain rc0 receipts in round report

## evidence pointers

- chart: equity-curve-r1115-bm-c.png
- raw log: smoke-r1115-bm-c.log
