# Digest r1453 bm-b -- E433: the name rides along

**Card** E433-WHICH-REPUBLICATION-SITE-CARRIES-A-FILE-VALUED-DIRECTORY-FIELD-INTO-A-NEW-FACE
**Face** `results/state_tilt/REPUBLISHCHAIN-2026-11-03.json` (+ `republishchain_latest.json`)
**Script** `scripts/e433_republication_chain.py` (run / verify / selftest, 9/9)
**Verdict** `a_republication_row_binds_a_name_beside_a_file_capable_directory_field_and_its_published_rows_are_still_double_ready`

## The question E423 left open

E423 showed the first face: 822 directory-named fields, 44 holding a file path, 8 read sites that
republish the field without joining it. What it did not price is what happens *after* the
republication. If the new row also carries a name, a consumer of that face can compose a doubled
name -- `results/x.json` + `x` -- exactly as it could in the face the value came from. The defect
would then be a chain, not a set of isolated rows.

## What was measured

| population | count |
| --- | --- |
| republish sites (from E423's face) | 8 |
| sites binding a name beside a file-capable directory key | 3 |
| writer faces those modules open for writing | 2 |
| file-valued directory rows in those faces | 16 |
| rows carrying a sibling name | 12 |
| rows where the name already equals the value's basename | 11 |

Pairs measured: `directory_expression`+`fragment` (e404's `build_site_row` / `build`), `parent_dir`+
`key` (e399's `name_row`). e403's five republish rows bind no name at all, and its face's 4
file-valued rows are published as NOT double-ready rather than folded into the headline.

The 12 double-ready rows are all in `constdirs_latest.json`, keyed `resolved_directory` with
`fragment` beside it. That near-identity (11 of 12 names equal the basename) is structural: in that
census the name *is* the fragment being resolved into a path, which is precisely why a later join
would double it.

## The instrument defects caught in-window

1. **Naming a face is not writing it.** The first draft collected every bare `*.json` literal in a
   module and published **32 writer faces**, most of which the module only reads (e403's
   `latestfamily_latest.json` is its SEED face, read-only). Fixed by reading the `open(..., 'w')`
   call and following module constants plus one level of for-loop bindings
   (`for name in (FACE, LATEST)`), the way these faces are actually addressed. 32 -> 2, and a
   selftest leg now pins both directions (a written name is a stem, a merely-read name is not).
2. **A site that emits no name is not a null result.** e403's rows carry class/expr/dir only. Had
   they been pooled with e404's, the headline would have described the key, not the row.
3. **Repo-relative paths.** E423's read sites store absolute paths; the first build published
   `C:\Fluxgroup\...` in `sites_by_file`. Normalised at the row.

## Honest bounds

* A writer is owned only when the module spells the face as a bare `*.json` literal under a write
  call; e399's `unresolved_latest.json` is published by name in
  `republish_files_without_a_writer_face` instead of being silently dropped or over-attributed.
* A literal is graded by its own key set, so a row assembled from `**kwargs` or mutated after the
  literal is invisible and is disclosed as such in `method_limits`.
* The name test is E423's row test (a name key holding the value's basename) -- reused by import,
  so the two faces cannot drift into two definitions of "double ready".

## Wiring

* smoke leg `# E433 (r1453 bm-b)` re-derives the entire study (0.47 s) and refuses a stored count
  that a fresh build does not come back with; `scripts/run_e433_smoke_leg.py` 1/1 green, 1/1 red on
  a doctored `double_ready_rows_in_writer_faces`, face restored byte-identical `595c19613dcd4be9`.
* S6 leg `republication_chain` -> `verify problems=0`, rc=0, 0.5 s (`results\_r1453bmb_s6_chain.json`).
* Methodology card E433 appended (`42+/0-`, `newline="\\n"`, no CRLF flip).

## Why it matters for the company

The census faces we publish are themselves read by later censuses. If a directory field carries a
file path and a name rides beside it, the next census can compose a path that never existed and
publish it as a measurement. This card prices that propagation on the existing chain and gives the
next reader a machine-checked answer instead of a warning in prose.