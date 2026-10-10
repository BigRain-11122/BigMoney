# BigMoney QA self-verification r852

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 91 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.199 annual=0.0072 maxdd=-0.0431 win_rate=0.4725 trades=91
- [x] 3. equity curve png -- equity-curve-r852-bm-c.png
- [x] 4. live-signal generation clean -- market_clock_call run rc=0 (idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar 2026-10-09; S6 chain rc0 receipts in round report

## evidence pointers

- chart: equity-curve-r852-bm-c.png
- raw log: smoke-r852-bm-c.log
