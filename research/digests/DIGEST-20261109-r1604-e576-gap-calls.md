# DIGEST 2026-11-09 r1604 bm-b -- E576: where the chain executions no round row follows actually sit

**Question inherited from E575 (r1603).** E575 read 491 chain executions out of this host's
session transcripts and found 39 that no row of their own machine follows inside a 6h tolerance.
It published them as "unattributable" and stopped, so the per-round answer silently excludes
whatever ran in a gap: an interactive session, a manual rerun, a hung chain.

**Population, re-derived live (never copied from the card).** `e575.command_corpus()` ->
`e575.round_index()` -> `e575.attribute()`; the unattributed set is re-derived and compared to
E575's own count (`population_agrees_with_e575 = true`, 39 vs 39).

**Readings.**

| class | n | what decides it |
|---|---|---|
| a_duplicate_of_a_run_attributed_to_a_round | **0** | no gap line's normalized text appears among the attributed executions |
| a_row_of_another_machine_follows_inside_the_tolerance | **7** | nearest following row belongs to another machine, 30.3-35.7 min later |
| only_a_row_beyond_the_tolerance_follows | **31** | first following row is 387.3-890.5 min later (6.5-14.8 h) |
| no_row_of_any_machine_follows_it | **1** | the round's own 02:xx read of the E573 leg -- its row is written at round close |

Hours hit: 13. Densest 13:00 (6), 19:00 (6), 12:00 (5), 14:00 (5); 00:00 (2) and 02:00 (1).
23 of 39 carry `--only`.

**Three lessons.**

1. *"Unattributable" is a bucket, not a conclusion.* Split by "whose row is next and how far
   away", the largest class (31) is not unattended automation -- it is overnight batch work
   followed 6.5-14.8 h later by the next row. The 6h tolerance is tight precisely for the
   cross-night case the round loop is built around.
2. *Duplicates must be excluded explicitly.* A command that already runs inside an attributed
   round, if counted again in the gap, invents a second execution that never happened. Zero of 39
   are duplicates here -- but the arm now exists and is published, rather than assumed.
3. *The round's own commands structurally land in the "nothing follows" class* (rows are written
   at round close). The single row of that class is this round's own leg read; publishing it
   without that sentence would read as one execution nobody ever saw.

**Walls.** Only this host's transcripts (`.codely-cli/auto-saves`, not carried by git) plus the
three round-report files; another machine's gap commands are not on this host, so their gaps are
unreadable here. Who typed a gap command remains an unnamed witness.

**Evidence.** `scripts/e576_gap_calls.py` build/check/verify + selftest 22/22;
`results/state_tilt/GAPCALLS-2026-11-08.json` + `gapcalls_latest.json`; S6 leg `gap_calls`
rc=0 0.04s; smoke leg `#E576` + `scripts/run_e576_smoke_leg.py` (1/1 green, 1/1 red under
`--doctor`); card E576 in `knowledge/METHODOLOGY_ASSETS.md`; treasure row.