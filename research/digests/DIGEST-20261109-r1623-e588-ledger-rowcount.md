# DIGEST — E588: the ledger's row count is a denominator for two of its eleven consumers (r1623 bm-b, 2026-11-09)

**Question.** E584 (r1614) found a run that both rebased and appended, publishing six bars twice
(17 rows over 11 bars) and feeding all 17 to the significance block. The record was repaired. The
consumers of that one file were never enumerated: anyone who uses `len(bars)` as a count inherits
whatever the file holds, while anyone who keys by `bar` or reads `bars[-1]` never sees the fault.

**Readings** (`results/state_tilt/LEDGERROWCOUNT.json`)

- 11 modules name both `etf_book_forward` and `LEDGER` in their own text (one-shot round helpers and
  smoke mirrors are published as excluded, with their own class). Graded by the roles their own lines
  play, **2 are blind** (`scripts/e592_carry_phase.py`, `scripts/etf_book_ceo_page.py`), **5 guard**
  (the writer's `_dedupe_bars`, e584, `etf_book_order`'s `rows_equal_bars`, `exchange_calendar_audit`,
  `smoke_test.py`), **3 are immune by keying**, 1 only relays the path.
- Three live arms on a temp copy of the real ledger with its last six rows appended again:
  - `e592.published_rate_series`: 11 → 17 rows, and a per-row rate mean moves 0.004445% → 0.004332%
    because six bars are weighted twice (a row count used as a denominator);
  - `etf_book_order._ledger_book`: **0 fields change** — it reads `bars[-1]` and `book_in_force`;
  - `etf_book_ceo_page.build`'s `forward` block: `bars` **11 → 17**, while `as_of`, `nav` and
    `since_inception_pct` do not move at all. The CEO page's "N trading days" is the number that
    would have been wrong by 54%.
- No consumer puts the row count into arithmetic on its own line (`modules_where_the_row_count_feeds
  _arithmetic = 0`); the exposure is through what they publish and what they hand on, not through a
  division written next to the `len()`.

**Verdict.** `some_consumer_publishes_the_row_count_and_would_have_reported_17_bars_for_11`.

**Lessons.**

- Repairing the record is not repairing the readings: the fault's *consumers* are a separate
  population, and only running them says who would have been wrong and by how much.
- `len(bars) < 1` is not a count — the first build graded `etf_book_card_track` blind on that line,
  but 11 and 17 rows pass the same emptiness test; it was demoted to `row_count_presence_only`.
  A judgement has to survive its own units.
- A guard is only a guard if both numbers are published: the writer emits a deduped series and the
  order face emits `accrued_bars_on_disk` beside `rows_equal_bars`; a surface that publishes a single
  count has no second chance to contradict itself.
- Being immune is not being correct: three modules cannot be wrong about duplication because they
  only ever ask for the last bar. That is a different fact from "they validate the file" and the
  census publishes it separately.

**Limits.** Role detection is line-level on each module's own literals — a count relayed through
helper frames is invisible, so the blind count is a lower bound. A relay module that hands the path
to another module is `names_the_path_but_reads_no_bars`, not a reader defect. The duplication arm
reproduces E584's shape (17 rows / 11 bars), not its exact row objects. Arm 3 patches the module-level
`LEDGER` constant of `etf_book_ceo_page` and calls its pure `build()`; `run()` is never touched.

**Evidence.** `scripts/e588_ledger_rowcount.py` (selftest 29/29, check/verify problems=[]),
`scripts/run_e588_smoke_leg.py` (PASS, 1/1 red under `--doctor`), `results/state_tilt/LEDGERROWCOUNT.json`
(+ `-latest`), S6 leg `ledger_row_count` (rc0 1.50s), smoke leg `E588` (52 added lines, 0 deleted).