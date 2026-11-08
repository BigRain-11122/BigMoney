# DIGEST 2026-11-08 r1580 bm-b -- E554: the repository's whole "wrote <path>" population

**Study**: `scripts/e554_wrote_population.py` (card E554) · **Face**: `results/state_tilt/WROTEPOPULATION-2026-11-08.json` (+ `wrotepopulation_latest.json`) · **Pool card**: E554 -> done; E555 seeded.

**Window note**: this round inherited the face from a killed round (pid 37472, artifacts written 17:50-18:00, no closeout). The gate chain was re-run in-window rather than trusted: `check problems=[]`, `verify problems=[]`, `selftest 46/46`, smoke leg 1/1 green with `--doctor` 1/1 red, S6 leg `wrote_population` rc=0.

## What the card asked

E553 (r1579) measured six `etf_phase_*` render sites and closed with a bound that said the other
`print("wrote", ...)` sites were out of scope. That bound is this study's population: discover every render
call whose statically readable first word is `wrote`, then answer the two facts that decide whether a
rendered path is a machine-visible announcement -- (a) can any source in this repository spawn the writer,
and does that spawn capture stdout; (b) does the face the message names have another announcement (a
canonical `<stem>_latest.json` pointer or a source literal), or is the message the only one.

## What it found

| spawn class | rows |
|---|---|
| spawned by a source that captures its stdout | **0** |
| spawned by a source that leaves stdout on the console | **0** |
| no source in the repository spawns this writer | **121** |

| announcement class | rows |
|---|---|
| only the rendered message announces this face | **8** |
| a source literal announces this face | 10 |
| a pointer face announces this face | 8 |
| both a source literal and a pointer face | 5 |
| the message names no face this scan can resolve | 90 |

**121 render rows / 97 writers / 31 resolvable faces / 0 spawnable writers.** Risk classification:
**8 rows are `message_only` and nobody can spawn their writer** (the "message only *and* a source can spawn
it" cell is 0), 20 are announced without the message, 3 are writers that read their own face back, and 90
are published as `unassessable` because the message names nothing this scan can fold.

The 90 unassessable rows are not one bucket. `by_unresolved_reason` splits them: 67 are
`the_second_argument_is_a_name_this_scan_cannot_fold`, 18 are `a_key_of_a_dict_built_at_run_time`, 3 are
`a_count_or_a_flag_not_a_path`, 2 name nothing besides the word. The 67-row reason is itself a question and
seeds E555.

Workspace split: 99 rows sit in `scripts/` (a lane could run them), 22 are one-off scratch scripts under the
repo root or `results/` -- the population is mostly lane scripts, not throwaway code.

**Verdict** (recomputed from the rows): `some_wrote_messages_are_the_only_announcement_of_a_face_that_nothing_else_names`.

## Lessons

1. **A study's stated bound is the next study's population, not a footnote.** The six-row population of E553
   was the parent face's own rows; reading the bound as a to-do list produced 121 rows and a different answer
   about how common the shape is.
2. **"Nobody reads it" is two questions.** Can anyone run the writer, and does the face have a second
   announcement route. Asking only the first misreads "a human can type it" as machine visibility; asking only
   the second mistakes a pointer face for a consumer.
3. **Unassessable must be split by reason.** The 67-name bucket is worth more than the total 90: it names a
   concrete next measurement instead of a residue.
4. **A clean-looking verdict must prove it looked.** The gate pins "at least one resolved face" and "at least
   one unassessable row" beside the verdict, so a scanner that found nothing cannot print the same sentence.

## Bound published with the face

Spawn detection is static: a source counts only if it names the script inside a spawn function's arguments or
a shell command line; aliases and variable-built paths are not followed. Announcement detection reads source
literals and small `*_latest.json` pointer faces only -- not the large `results/` faces. Only in-repository
consumers are measured (external CI and human eyes are out of scope).

## Wiring

- `scripts/e554_wrote_population.py` -- build / check / verify / selftest 46/46
- `results/state_tilt/WROTEPOPULATION-2026-11-08.json` + `wrotepopulation_latest.json`
- S6 leg `wrote_population` in `Tools/s6_chain_bmb.py` (rc=0, 173.7s)
- smoke leg `# E554` in `smoke_test.py`, standalone runner `scripts/run_e554_smoke_leg.py` (1/1 green, `--doctor` 1/1 red)
- card E554 in `knowledge/METHODOLOGY_ASSETS.md`
- pool: E554 done; E555 seeded (`...the 67 unfolded second arguments...`), ready back to 3 = floor