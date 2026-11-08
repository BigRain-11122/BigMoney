# Digest — E542 (r1569 bm-b): do the survivors of an ambiguous row differ in anything a reader can see?

**Question.** E541 left 32 census rows ambiguous: after applying the four arms the census row already
carries, two or three same-shape candidates survive. "32 ambiguous rows" is a count of candidates,
not a statement about what a consumer of the published row would get wrong.

**Method.** Take those 32 rows and their 73 survivors. Resolve every survivor to the context the
published row exposes — the innermost function, the innermost statement and its kind, that
statement's opening line, the innermost enclosing loop, and the signed distance from the candidate
line to the published line — then compare the survivors field by field. The sixth observable, `tier`,
is a property of the row, so it can never separate a row's own survivors; the face publishes that
invariance instead of letting it count as "no difference".

**Readings.** 32 rows / 73 survivors (23 rows with 2, 9 rows with 3).
**32 of 32 rows keep survivors in different statements** — 24 differ only in the statement (line,
and for 6 of them the kind), 8 differ on more than one substantive field; 4 rows differ in the
enclosing loop. **0 rows differ on nothing, 0 rows differ only in distance, 0 rows have an
unresolved context.** Distance separates on all 32 rows too, but always alongside the statement.

**Verdict.** `most_ambiguous_rows_keep_survivors_that_differ_in_the_function_the_statement_or_the_loop_so_the_ambiguity_changes_what_the_row_teaches`

So the 32 are a defect surface rather than an over-counted multiplicity: pick a different candidate
and the statement (and in 6 rows the statement kind, in 4 rows the loop context) a reader learns
changes.

**Two methodology lessons.**
1. *A candidate count is not a reading.* Publishing "N rows ambiguous" without saying which observable
   separates the candidates leaves the number standing in for the conclusion.
2. *A row-level field cannot be separation evidence.* `tier` takes one value per row; publishing that
   invariance is cheaper to check than letting it contribute a silent zero. The same holds for
   `function` while E541's function arm applies: a zero there is a consequence of the arm's order,
   not a measurement — the face says so.

**Two self-caught defects.**
- The first draft looked a survivor's context up by `(line, col)` and fell back to the whole index on a
  miss, which made every field `None` — i.e. it published "the survivors differ on nothing", the exact
  defect the study exists to measure. A miss is now an unresolved context, and the fixture uses the
  candidates' real columns.
- `_with_survivors` originally hardcoded `col=0`, so the fixture passed that same miss through; the
  selftest fixture now takes its survivors from E541's own candidate rows.

**Products.**
- `scripts/e542_survivor_spans.py` — run rc0, `check` problems=[], `verify` sites/summary identical, selftest 18/18
- `results/state_tilt/SURVIVORSPANS-2026-11-08.json` + `survivorspans_latest.json`
- `scripts/run_e542_smoke_leg.py` — leg green, `--doctor` 5 mutated faces all refused
- `smoke_test.py` leg `# E542`, `Tools/s6_chain_bmb.py` leg `survivor_spans` (rc0 0.09 s)
- `knowledge/METHODOLOGY_ASSETS.md` card E542, `knowledge/TREASURE_REGISTRY.md` closure line
- `results/runnable_pool.json`: E542 done, E543 seeded (ready 3)