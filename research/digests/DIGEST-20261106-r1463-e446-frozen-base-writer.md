# DIGEST r1463 (bm-b) — E446: a frozen face-home base is dormant or abandoned, and 23 of 51 are abandoned

Card: E446 (`knowledge/METHODOLOGY_ASSETS.md`). Judge: owner bm-b. 2026-11-06.

## The question E441 did not ask

E441 (r1461) graded 72 face-home bases and published **51 as frozen**, where frozen is a
measurement of exactly one thing: no published member of the base has an mtime later than the
carrier that names it. E445 (r1462) then priced the 21 live bases. The 51 frozen ones kept the
word, and the word invites a second claim it never made — that nothing will ever write there
again.

E446 asks it: for each frozen base, does the **corpus** hold a write site whose target statically
resolves into that base?

## Reading

| | bases |
|---|---|
| frozen bases (E441's published set, re-read from its summary) | 51 |
| with a write site that resolves into the base | 28 |
| with no write site at all | 23 |
| reachable only by a literal *tail* reading (head unfollowable) | 7 |
| with a writer once suffix evidence is allowed | 35 |
| still without a writer even then | 16 |

Write sites found on frozen bases: 5,972 over 12,131 walked `.py` files, 31,152 write-shaped
calls total (22,323 resolved, 233 parse errors, 2 files over the 2 MB cap). **`results` itself is
one of the 51 frozen bases** and accounts for 6,291 of those sites purely because it is an
ancestor of 49 others, so the face publishes the population excluding ancestor bases next to the
full one (`frozen_bases_excluding_ancestor_bases` = 49, 26 with a writer, 23 without) and prints
both verdicts.

The abandoned set is not exotic: `results/etf_book_production`, `results/etf_book_order`,
`results/m6_regime5`, `results/overnight_gap_census`, `results/t23_census`, `results/e79`,
`results/g25`, and the three rollback/backup dirs (`results/_r753bmc_churn_backup`,
`results/_r903bmc_ff_backup`, `results/_r1024bma_rollback_side`). The last three are *meant* to be
abandoned — they are the artifacts of a surgical push — and that is the useful part of the split:
a backup dir with no writer is correct, a production dir with no writer is a dangling consumer.

## What this cost to get right (each now a selftest leg)

1. **A read is not a writer, and that is the whole study.** 31,150 write-shaped calls out of a
   corpus where `open(` appears far more often — the discrimination lives entirely in the mode
   argument and in the sink name (`to_parquet`, `write_text`, `mkdir`, copy/rename destination).
   Without it the answer would have been "every base has a writer" and the card would be empty.
2. **The repo-root idiom is the shape most constants are written in.** The first run reported
   `results/etf_book_production` as abandoned while `scripts/etf_book_production.py` obviously
   creates it — the constant is
   `OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "etf_book_production")`.
   Teaching the resolver `__file__`, `dirname`, `abspath` (and then the literal-tail reading for
   heads it still cannot follow) moved 7 bases out of the abandoned set. A resolver that cannot
   read the idiom the repository is written in measures its own ignorance.
3. **A base that contains another base cannot be abandoned.** Crediting a write anywhere below
   `results` to `results` is literally correct and completely uninformative; a single ambient base
   would have decided the headline. Fixed by publishing both populations and both verdicts.
4. **A suffix reading is a weaker class, never a full path.** `?etf_book_production/x.json` is
   "some unknown ancestor, then this" — it is published as its own count and refused by the smoke
   leg if it ever appears in the full-path list (and the reverse).

## Artifacts

* face `results/state_tilt/frozenwriter_latest.json` + `FROZENWRITER-2026-11-06.json`
* producer `scripts/e446_frozen_writer.py` (`run` / `verify problems=[]` / **selftest 31/31**)
* smoke leg `e446 frozen base writer (r1463 bm-b)` + `scripts/run_e446_smoke_leg.py`
  (standalone 1/1; `--doctor` reds it and restores the face byte-identical `7b7ed3eee7996c7e`)
* S6 leg `frozen_writer`

## Also found this round

`e442 which path composition is never consumed (r1462 bm-b)` is **red in the suite**: its leg reads
`results/state_tilt/deadpath_latest.json`, which has never been published. `scripts/e442_deadpath.py`
exists (32 KB, written 22:30 yesterday) but `run` produces no output and no face within 5 minutes,
so the leg has been red since the round that wrote it. Naming the hang is next round's P0.