# BigMoney QA self-verification r890

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).
> Lineage: _r805bmb_qa_pack.py bloodline rolled to r890 (bm-a); r890 path no prior committer (F-20261008-03 interim law check: zero collision).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, 93 trades, determinism=True
- [x] 2. results have real numbers -- sharpe=0.1586 annual=0.0056 maxdd=-0.0433 win_rate=0.4624 trades=93
- [x] 3. equity curve png -- equity-curve-r890.png
- [x] 4. live-signal generation clean -- market_clock_call rc=0 (r890 S6 chain JSON, idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar 2026-09-30; S6 40-leg chain rc0 (bad_legs NONE); 10-08 reopen bar not yet at sina source, collector no-op honest, retry continues

## evidence pointers

- chart: equity-curve-r890.png
- raw log: smoke-r890.log
