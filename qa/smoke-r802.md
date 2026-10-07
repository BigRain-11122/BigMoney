# BigMoney QA self-verification r802

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).
> Lineage: r800 debt pack delivered by r801; this r802 pack produced in-round (no debt).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 93 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.1586 annual=0.0056 maxdd=-0.0433 win_rate=0.4624 trades=93
- [x] 3. equity curve png -- equity-curve-r802.png
- [x] 4. live-signal generation clean -- market_clock_call rc=0 (r802 S6 chain leg 07, idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar 2026-09-30; S6 35-leg chain rc0 receipts in round report (golden-week no-op family, reopen 10-08)

## evidence pointers

- chart: equity-curve-r802.png
- raw log: smoke-r802.log
