# DIGEST 2026-11-07 r1514 bm-b -- E489 write-wire

Card: E489 in `knowledge/METHODOLOGY_ASSETS.md`.

## Question
E488 placed 50 of 51 basename-only writers in the reader's directory by folding the *module's*
directory constant. That is a claim about the module. E487 had traced the write path only as far
as a bare basename. Does the write call's own path argument literally compose
`<reader directory>/<spelling>`?

## Reading (2026-11-07, 50 rows)
- write call composes the exact reader path: **39**
- write call composes the reader directory with another basename: **1**
  (`bandthreshguard` -- the traced line only writes `BANDTHRESHGUARD-2026-10-29.json`; the
  `_latest` copy is composed elsewhere)
- write call folds to another directory: **0**
- write call present but path does not fold: **9** (mostly `def _write(face, outdir)` helpers --
  the directory arrives at the call site, one more hop than this face follows; one temp-dir write)
- no write call at the recorded site: **1** (E487 recorded the helper call line)
- parent tally reproduced 50/50

Verdict: `most_same_directory_writer_write_calls_compose_the_path_their_reader_opens`

## The three lessons
1. **Re-price the hop budget whenever you add a layer** (second occurrence after r1513).
   A write path goes `for p in (dated, latest)` -> `Name` -> `Call` -> alias constant, two or three
   frames deeper than E488's directory constant. At 12 hops the alias chain
   `e453 -> e452 -> e451` fell off: the same row folded at depth 0 and not at depth 1. Fix: keep
   foreign modules in the *same* folder subclass so the budget has one source. The symptom of a
   short budget is "0 wired on the whole face", not an error.
2. **Read the parent's key names, not the names you expect.** E488 publishes
   `reader_directories`; the first draft read `resolved_directories`, every row's expected path came
   out empty, and the face read 0 wired / 20 elsewhere. Two names for one concept turn a key bug
   into a scientific claim (E366/E462 family).
3. **Split "does not fold" into "one hop away" and "not static".** Nine rows: mostly helper
   parameters (next hop at the call site), one temp directory. Folding those into one class reads
   the folder's own limit as a writer defect. E490 splits that class.

## Wiring
- `scripts/e489_write_wire.py` (run / check problems=[] / verify problems=[] / selftest 24/24)
- faces `results/state_tilt/WRITEWIRE-2026-11-07.json` + `writewire_latest.json` (50 rows)
- S6 leg `write_wire` rc0 0.07s; smoke leg 1/1 green, doctored (wired +1) 1/1 red, face sha restored
- pool: E489 done, E490 seeded (the helper-parameter arm)
