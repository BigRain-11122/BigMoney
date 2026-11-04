# DIGEST 2026-11-04 r1437 bm-b -- E419: who writes the 9 faces nothing can age

**Card.** E419-WHICH-UNSTAMPED-FACE-HAS-A-WRITER-HOLDING-A-DATE-IT-NEVER-WRITES
**Face.** `results/state_tilt/UNSTAMPABLE-2026-11-04.json` (+ `unstampable_latest.json`)
**Script.** `scripts/e419_unstampable.py` -- `run` / `verify problems=[]` / `selftest 10/10`

## What was asked

E418 aged 36 of its 45 blind faces by their own stamp and published 9 as age-unknowable (8 with no
stamp field, 1 with `generated = "deterministic"`). The open question was not "how old are they" but
"is a date even reachable": which script writes each face, does that writer hold a date at write
time, and would a reader of the face be able to go red on age.

## What was measured

| class | n |
|---|---|
| writer holds a date it does not write | 1 |
| writer already writes a date | 1 |
| writer has no date in hand | 4 |
| no writer in the tree | 3 |

The only row where a date is in hand and never written is `results/futures_tsmom_signal.json`
(`scripts/futures_tsmom_signal.py run` calls `datetime.now()` and emits no date key). The
`PROFILE-*.json` template is written by `scripts/e221_dom_profile.py run` *with* `evidence_cutoff`
and `ts` -- that row was unageable because the E418 population names a template, not a file.

**0 of the 9 faces has a reader that can go red on age today.** So the 1 writable row would change
nothing on its own: the missing artifact is a reader, not a field. That is the deliverable's second
half and the reason no writer was edited.

## Pits worth carrying

1. **Attribution by file** graded 9 of 9 as "already writes a date": a file that mentions a name and
   writes some other face was read as that face's writer.
2. **Attribution by function** graded 8 of 9 the same way, because `smoke_test.main()` is one
   function that names every face it reads and writes temporary fixtures -- it manufactures a writer
   for every face in the suite. Fixture-path veto (`tmp|tempfile|scratch`) plus a directory token is
   what fixed it; `CARD` alone is not a name.
3. A suffix test on date words is wrong: `update` ends with `date`, `exists` ends with `ts`. Token
   membership instead; 2 of 9 rows carried a phantom date before the change.
4. `ast.get_source_segment` per call node cost >5 min on this tree (killed at CPU 125 s); slicing
   pre-split lines costs 30 s for the same walk.
5. A one-off `Tools/_r746bmc_addendum.py` outranks the real producer of `dashboard_status.json`
   unless scratch names (`_`, `tmp`, `closeout`) are ranked last.

## Wiring

* smoke leg `# E419 (r1437 bm-b)` in `smoke_test.py`, executed verbatim by
  `scripts/run_e419_smoke_leg.py` (1/1 green). It refuses a vocabulary-outside class, a
  holds-a-date row whose graded writer holds none, a no-writer row that publishes writers, a
  population that is not E418's age-unknown rows, and a summary/verdict that does not re-derive.
* S6 leg `unstampable` in `Tools/s6_chain_bmb.py` (rc 0, 0.05 s) -- `verify`, so the chain refuses a
  face that no longer re-derives.
* Methodology card E419 in `knowledge/METHODOLOGY_ASSETS.md` (42 added lines, 0 removed).

## Honest limits

The census reads a write target's own text plus one hop through a named path constant; a path
composed inside a helper the study cannot see is graded `no_writer_in_the_tree`. That is why
`CARD.md` (written through an `OUT_DIR` argument) and `AGGATT-%s.json` stay in the no-writer class --
they are named here as an unresolved shape, not as an absence of a writer.