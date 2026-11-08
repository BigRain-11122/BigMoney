# DIGEST 2026-11-09 r1614 bm-b — E584: the ledger's rows, the gap they close, and the six bars published twice

**Question.** The forward ledger (`results/etf_book_forward/LEDGER.json`) is the one artefact of
this book that accrues money in public: every row carries a `bar`, a `nav` and a `carry`. E583/E585
priced the *tickets* against the bar their file names. Nobody had asked the same of the ledger's own
rows: (1) is every row a distinct bar; (2) does the carry on a row pay the calendar gap that row
closes — Friday's 1-day contract earning three days over the weekend — or one day's interest on
every row.

**Reading, as found.** 17 rows, **11 distinct bars**. `2026-10-30`, `11-02`, `11-03`, `11-04`,
`11-05`, `11-06` each appear twice, byte-identical. Carry summed over rows `2.203e-04` vs
`1.463e-04` over distinct bars — **7.403e-05** extra, i.e. **74.03 CNY** on the 1,000,000 seed
capital. The significance block had been fed `len(led["bars"])` = **17** where 11 bars exist, so its
bar count read **+54.55%** of the record — and that count is exactly the ruler this forward ledger
uses to say how long it would need to adjudicate itself (E316 family).

**Root cause, with the proof in the file.** One run both rebased and appended. The rebase branch
rebuilds the whole series (`led["bars"] = _indexed(marks, seed_bar)`); `new_bars` had been computed
*before* it, from the pre-rebase last bar (`[f for f in _indexed(marks, seed_bar) if f["bar"] >
led["bars"][-1]["bar"]]`), and `led["bars"].extend(new_bars)` then appended bars the rebase had
already published. The two timestamps in the file are the same run: `rebases[0].ts = 22:35:12` and
`runs[-1] = 22:35:15, new_bars=6` — and the six duplicated dates are exactly those six bars.

**The gap question, answered.** The two three-day gaps do pay three days: `10-26` carry `3.312e-05`
and `11-02` `3.337e-05` against `1.104e-05` on adjacent single-day rows — a ratio of ~3.0. The
weekend is not flattened by a 252-day convention. Three rows are classed as the calendar gap, six
have no reference rate (below), one carries a negative rate.

**Fix.** Write-side guard in `etf_book_forward.py`: `_dedupe_bars()` keeps one row per bar and
reports what it dropped, applied at load (repairs a record already on disk) and after `extend`
(stops the rebase-then-append shape from re-creating it). The published file is then repaired by the
tool's own `--rebase` escape, never by hand-editing JSON — a hand-deleted row would leave a
`significance` block whose bar count disagrees with `len(bars)`. After repair: 11 rows / 11 bars,
`+0.00%` inflation, `rebases` carries a second entry (`universe_membership_drift`, universe
1613→1624 that night — a data fact, not this repair's doing).

**Honest walls, published rather than hidden.**
- `implied_accrual_days` is measured at the **GC001** short rung. The engine's cash leg is
  `etf_book_cash_ladder`'s three-rung ladder (GC007/GC014/GC028, commission charged), which
  apportions a maturing contract's interest across the bars it spans. That split cannot be rebuilt
  from the short rung: `rows_reproducing_the_ladder = 0` of 11, published as its own reading and
  driving no verdict.
- The repo panel (a bm-a lane) stops at **2026-10-28** while the book runs to 11-06: **6 rows have
  no reference rate** and are classed `prev_bar_has_no_repo_quote`, not judged.
- `11-05` carries a negative carry (`-3.84e-06`) and no reference rate on that window, so it is
  classed `negative_carry` and not claimed as a defect: GC001 can quote either side of zero.

**Evidence.** `scripts/e584_ledger_bar_accrual.py` (selftest 30/30, build/check/verify) →
`results/state_tilt/LEDGERBARS-2026-11-06.json` + `ledgerbars_latest.json`; the pre-repair reading is
archived as `LEDGERBARS-2026-11-06_defect-as-found.json`; S6 leg `ledger_bar_accrual` (rc=0, 0.04s);
smoke leg `#E584` + `scripts/run_e584_smoke_leg.py` (1/1 green, 1/1 red under `--doctor`); card E584
in `knowledge/METHODOLOGY_ASSETS.md`; treasure row in `knowledge/TREASURE_REGISTRY.md`; pool: E584
done, E588 seeded (whether any reader takes the ledger's row count as a denominator).