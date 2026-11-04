# DIGEST 2026-11-05 r1450 bm-b -- E432: the 21 fixture-shaped write sites, priced

**Card** `E432-WHICH-FIXTURE-SHAPED-PARAMETER-WRITE-SITE-IS-READ-BY-A-PUBLISHED-READER`
(closed in-window; seeded from the r1449 supply floor).

## Question the card asked

E428 counted 21 `fixture_shaped` parameter-directory write sites among its 35 unplaced rows and
never asked a single question about them. For each of the 21: resolve the directory its callers
actually pass (temp / repo-relative / runtime name), and decide whether any reader in the corpus
opens the composed name. A temp-dir writer must not be called dead.

## Answer

Face `results/state_tilt/FIXTUREWRITE-2026-11-04.json` (+ `fixturewrite_latest.json`),
evidence_cutoff `2026-11-04`, 21 rows, 3,436 sources, 3,276 read calls scanned.

Verdict:
`no_fixture_site_writes_into_a_directory_a_reader_in_the_corpus_opens_and_the_sites_that_share_a_reader_name_share_only_the_name`

| reading | count |
|---|---|
| fixture-shaped sites priced | 21 / 21 live (0 rows lost since E428) |
| `temp` (a tempdir constructor in the caller's argument) | 15 |
| `runtime_constant` (a module constant / forwarded name / joined expression) | 6 |
| `repo_relative` (a lone quoted directory inside the tree) | 0 |
| reached only from a selftest caller | 19 |
| reached from a production caller | 2 (`p1e_ic_batch._save`, `t24_prospect_paper._save_member`) |
| a reader spells the composed name as a segment | 9 |
| a reader **could** open the written file | **0** |

## Three defects the study caught in itself

1. **Substring match.** `status.json` matched inside `results/dashboard_status.json`, which
   invented nine "a reader opens this" rows. The reader test is now a path-segment regex.
2. **Quote in the argument is not a quoted directory.** `os.path.join(tmp, "ok")` and
   `item["nm"]` were graded `repo_relative` by a "contains a quote" test; that gave a false
   verdict (`some_fixture_sites_write_into_repository_paths_a_reader_opens`) for two commits'
   worth of run. Only a lone literal counts.
3. **Card premise.** The pool card says "21 among its 310"; the 21 are a subset of the 35
   *unplaced* rows. Published as `summary.population_premise_correction`, not silently fixed.

## Cost learned

Rebuilding E428's 97-name call index costs minutes of CPU for call sites this study never reads;
the bulk index is now narrowed to the 21 helpers, and the reader pass is prefiltered by name
before any file is parsed. Full build ~3 min, verify re-derives the same table.

## Wiring

* smoke leg `# E432 (r1450 bm-b)` + `scripts/run_e432_smoke_leg.py` -- 1/1 green, 1/1 red on a
  doctored `by_class`, face restored byte-identical (`1f84eeda…`).
* S6 leg `fixture_write` in `Tools/s6_chain_bmb.py`.
* card `E432` in `knowledge/METHODOLOGY_ASSETS.md` (46 added lines, no flattening).
* pool: E432 done, E427/E433 still ready.

## Honest limits

Directory class is read from the text a caller supplies, not from the runtime value: a caller that
builds a temp directory through a differently named helper is graded `runtime_constant`. Readers
are found by AST over read calls whose first argument spells the composed name; a reader that
composes the same name from parts is invisible. No writer or reader was run or edited.