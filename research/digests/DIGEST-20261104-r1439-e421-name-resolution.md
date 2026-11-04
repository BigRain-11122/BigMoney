# E421 — a name that resolves to no file is a join, not a basis

Round r1439, bm-b. Card `E413-DOES-THE-STRONG-BASIS-FACE-NAME-RESOLVE-TO-A-FILE`.
Face `results/state_tilt/NAMERESOLVE-2026-11-04.json` (+`nameresolve_latest.json`).

## The card's premise was upside down

E406 named 58 faces from blob readers; 32 of those names "resolved to no file", which was read as
32 faces the tree reads and does not hold. E412 then priced the 25 it *could* measure and disclosed
that all of them carry the weak attribution basis (`module_face_literal`), leaving the impression
that the strong-basis names might behave differently and were the ones outstanding.

The basis is not what decides resolution. **The directory the literal is joined against decides.**
Two of the 33 unresolved names are the strong-basis ones (`CORPUSPIN-2026-01-01/02.json`, literal
in a function body); both are selftest fixtures written into `tempfile.mkdtemp()`. 0 of 2 resolve
to a file. Reading the population by basis would have looked answered and been wrong.

## The reading

| verdict | count |
|---|---|
| the reader spells a repo path and the file exists there | 18 |
| written only into a selftest temp dir | 9 |
| named only by the census's own selftest | 5 |
| on disk (absent only at the census's HEAD) | 1 |
| **joined into the repo and genuinely absent** | **0** |

Control arm: the 25 faces E406 *did* compare — 25 of 25 resolve to a file, 0 called a fixture.
The classifier discriminates, which is the whole falsification test: "everything is a fixture"
would have been a green answer on this population.

The mechanism is in the recorded path. E406 stored **32 of the 33 unresolved rows as a bare
basename with no directory at all** (`unresolved_census_directory = {"." : 32}`). A bare basename
cannot resolve to a file, so "resolves to no file" was a property of the census's own path
construction, not a property of the tree. The 18 recoverable names live where their readers
actually spell them: `docs/live_usage/` 9, `docs/daily_report/` 9, `results/state_tilt/` 1.

## Pits

1. **`endswith(base)` is not "names the base".** `delta_latest.json` sits inside
   `keydelta_latest.json`, `gamma_latest.json` inside `empirical_gamma_latest.json`,
   `x_latest.json` inside `slopematrix_latest.json`. With suffix matching those three came out as
   **genuinely missing repo files** — a headline ("3 faces the tree lacks") produced entirely by
   reading a name out of a longer name. Exact-or-`/`-prefixed matching turned all three into what
   they are: fixtures of the census itself (E330 family, quote-adjacency not substring).
2. **Self-inclusion, fourth recurrence in this family.** The same three names are spelled *by my
   own selftest*, so after the exact-match fix they reappeared as repo reads from
   `scripts/e421_strong_basis_resolution.py`. The study now removes itself from the corpus it scans
   and publishes `corpus.self_excluded` plus a selftest leg; alpha/beta/delta/gamma/x are all
   "named only by the census's own selftest".
3. **A count over a growing corpus cannot sit in an equality gate** — E420's law, met again one
   round later by the same author. `modules_scanned` moved the moment the smoke-leg runner file was
   created, so the leg red on "the published summary does not re-derive". Corpus size now lives in
   a top-level `corpus` block outside the pinned summary.
4. **Ordering of evidence, not of intuition.** The first classifier put a temp join above
   existence, and immediately called 5 of the 25 control faces fixtures — those are real faces
   whose basename is *also* spelled by some round script's fixture. Existence at the recorded path
   is a fact about that path and outranks any reading taken from another site that happens to
   spell the same name.
5. **A stem match is not a resolution.** `ALLOWANCE-2099-01-01.json` has siblings
   (`ALLOWANCE-2026-11-01.json`); that makes it look like a renamed face. Published as its own
   column, never counted as resolving.

## Delivered

- `scripts/e421_strong_basis_resolution.py` — run / verify problems=0 / selftest 27/27
- `results/state_tilt/NAMERESOLVE-2026-11-04.json` + `nameresolve_latest.json` (byte-identical on
  re-run)
- smoke leg `# E421 (r1439 bm-b)` (1/1 green via `scripts/run_e421_smoke_leg.py`, proved red by
  doctoring the face's summary then restored)
- S6 leg `name_resolve` (the leg's command is `verify`, rc=0)
- card E421, this digest
- pool: E413 done with result_ref, E422 seeded

Read-only: no reader, no leg and no face was edited by the study.