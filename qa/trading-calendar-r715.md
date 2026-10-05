# BigMoney QA self-verification r715 (M1 gate-4 real trading calendar)

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Product = D-M1_FUNDING_SEASON_P1
> 前置门④真交易日历件 (group prereg D-20260930-30 §2/§8-4, mechanism slate D-20260930-29 M1,
> CEO order 2026-09-30 「量化金融适配国内市场风格」). Pure data piece: ZERO backtest, ZERO
> engine, ZERO network, ZERO trials-ledger, ZERO marks writes, ZERO threshold faces.
> Ticket T-2026-10-05-170-P1 (claim+start same round per O-1730; F-04 MSG declared).

## checklist

- [x] 1. selftest clean -- `python scripts/build_trading_calendar.py selftest` = **25/25 PASS rc0**
  (hermetic tmp sandbox: union order / weekend-zero / weekday map / n_src counting /
  single-source day kept with flags / gap-day kept-with-flag / month+quarter+year-end flag
  logic incl. quarter∩month∩year triple / weekend-corruption hard gate raises /
  byte idempotency / verify payload keys / missing-vs-backbone + extra counting /
  missing-source fail-closed)
- [x] 2. run clean on real data -- rc0: **5,253 canonical trading days 2005-02-23..2026-09-30**
  (21.6y), month_end=260 (== month count of span, identity check), quarter_end=87,
  year_end=22; **weekend rows = 0** (hard gate passed on all 8 sources)
- [x] 3. source agreement (honest disclosure, results/trading_calendar_verify.json) --
  backbone=sh510050 (2005-02→, deepest); **etf300 & etf588000 & repo001 & repo007:
  0 missing / 0 extra vs backbone across full overlap** (repo rate panel 2011-05→2026-09
  3,740 days == exchange fabric exactly = M1 rate-face/calendar zero divergence);
  source gaps disclosed not dropped: etf500 2 (2015-04-13/14), sz159915 1 (2021-02-08,
  tail stale 2026-09-22), etf512100 1 (2022-09-02) -- union keeps days, per-source flags carry it
- [x] 4. idempotency -- rerun sha256 byte-identical (IDEMPOTENT-BYTES-OK,
  csv_sha256 9d4cc61076f7b3ec.. 199,771B; zero wall-clock fields in either artifact)
- [x] 5. artifact lands -- data/trading_calendar.csv (canonical, 14 cols incl.
  per-source presence flags + is_month_end/is_quarter_end/is_year_end pure calendar
  facts) + results/trading_calendar_verify.json + deriver
  scripts/build_trading_calendar.py (run/selftest, exit 0/2 fail-closed)
- [x] 6. no-conflict scan -- replaces the month-approximation semantics named in the
  prereg (strategies/seasonal.py holiday_effect {1,2,10,11} stays untouched in place;
  consumption/retirement is M1-batch assembly face, not this piece). Zero existing
  trading_calendar artifact in repo (grep zero-hit), zero duplicate mechanisms.
- [x] 7. M1 gate accounting (post-this-piece) -- §8: ① RW-1~4 green (landed 09-30)
  ✅ ② D-17 v1.2 validation set = **BigCompute lane (group-tracked, not BigMoney)** ③
  D-19 delivery layer ✅ ④ real calendar piece ✅ **this round**. M1 runner+burn ticket
  opens when ② lands group-side; 12-year window data face verified: calendar 2005→
  + repo rates 2011-05→ (15.4y) + sh510300 2012→ (deep legs in-repo).

## verdict

**PASS** -- piece delivered and self-verified; M1 in-repo prerequisite gate now fully green
(remaining gate is cross-subsidiary and group-tracked).
