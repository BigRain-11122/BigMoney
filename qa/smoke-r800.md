# BigMoney QA self-verification r800 (debt discharge)

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).
> Debt note: r800 ledger row recorded honest debt "QA pack r800 NOT produced (time-budget guard)"; delivered by successor r801 session per debt-discharge labeling precedent (QA r802 pack by r803 session).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 93 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.1586 annual=0.0056 maxdd=-0.0433 win_rate=0.4624 trades=93
- [x] 3. equity curve png -- equity-curve-r800.png
- [x] 4. live-signal generation clean -- market_clock_call rc=0 (r801 S6 chain run-2 leg 07, idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar 2026-09-30; S6 35-leg chain rc0 receipts in round report (golden-week no-op family, reopen 10-08)

## evidence pointers

- chart: equity-curve-r800.png
- raw log: smoke-r800.log
