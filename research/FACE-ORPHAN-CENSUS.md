# Cited faces: what a clone can open, and what points nowhere

generated 2026-11-25T19:22:10+08:00 | evidence_cutoff 2026-11-25 | machine bm-c

**Verdict: `EVERY_CITED_FACE_IS_IN_GIT_OR_MACHINE_LOCAL_BY_DESIGN`**

1476 face paths are literally named by a committed reader. 1319 are on disk and in git, 30 are machine-local by `.gitignore` policy, and **0 are on disk but unreadable from a fresh clone** -- the r1783/r1987 defect.

Citations live inside a `selftest` / `test_*` / `*_fixture` function are excluded (24 paths): those readers are exercising their own missing-input branch with a path that *must* not exist, and publishing it would be the wrong fix. Without that exclusion this census reported 167 "dead pointers", and the first draft counted `a.json` and `deadbeef.json` as evidence.

| state | count | reading |
|---|---|---|
| TRACKED | 1319 | clone opens it |
| IGNORED | 30 | machine-local by policy, never published |
| NEGATIVE_FIXTURE | 24 | named only by a test — must be missing |
| DOCUMENTED_EXAMPLE | 10 | named only inside a usage line / docstring |
| FIXTURE_LITERAL | 75 | a string inside a data literal, never an `open()` argument |
| TEMPLATE_PLACEHOLDER | 14 | the *shape* of a name (`REPORT-YYYYMMDD.md`) |
| ROUND_ARTIFACT | 0 | `_r####bm?` round bookkeeping |
| MACHINE_SCOPED | 0 | another machine's local state |
| EXTERNAL_CANON | 3 | lives in the group tree above this repo |
| ABSENT_LOCALLY | 0 | in origin, not on this disk — one fetch |
| ORPHAN | 0 | **defect**: on disk, cited by real code, not in git |
| DELETED_LOCALLY | 0 | **defect**: in the index, gone from disk |
| DEAD_POINTER | 1 | advisory: real code names it, no clone has it |

## Dead pointers (advisory)

Real code (not a test) names these and no clone has them. Either that branch has never run, or the file was renamed and the reader was not updated. Neither is an orphan -- there is nothing on disk to publish -- and this census cannot separate the two cases, so they are listed, not counted as defects.

| family | count | examples |
|---|---|---|
| research/INGEST | 1 | `INGEST/PACKS.json` |

## How to read this

An ORPHAN is not a broken number -- it is a number nobody else can read. The face was computed here, a committed reader names it, and the file never entered git, so the same reader on another machine or in a fresh clone gets nothing (or, worse, catches the error and continues: the r98 shape, where a missing face is printed as zero). Adding the file to git is the whole fix.

Limits: (1) literal citations only -- paths assembled at runtime are invisible, so every count is a floor; (2) IGNORED comes from `.gitignore` policy and is not audited for whether that policy is still right; (3) the test-context filter trusts function names, so a real reader whose function happens to be called `test_*` would be hidden, and a fixture in a function with an innocent name shows up as an orphan; (4) the ast walk falls back to a context-free regex on files that will not parse, and those citations count as real; (5) ABSENT_LOCALLY is measured against `origin/main` as of this run, so a machine whose peer has not pushed yet looks the same as one behind.
