# Cited faces: what a clone can open, and what points nowhere

generated 2026-11-23T13:46:41+08:00 | evidence_cutoff 2026-11-23 | machine bm-c

**Verdict: `EVERY_CITED_FACE_IS_IN_GIT_OR_MACHINE_LOCAL_BY_DESIGN`**

1358 face paths are literally named by a committed reader. 1181 are on disk and in git, 27 are machine-local by `.gitignore` policy, and **0 are on disk but unreadable from a fresh clone** -- the r1783/r1987 defect.

Citations live inside a `selftest` / `test_*` / `*_fixture` function are excluded (96 paths): those readers are exercising their own missing-input branch with a path that *must* not exist, and publishing it would be the wrong fix. Without that exclusion this census reported 167 "dead pointers", and the first draft counted `a.json` and `deadbeef.json` as evidence.

| state | count | reading |
|---|---|---|
| TRACKED | 1181 | clone opens it |
| IGNORED | 27 | machine-local by policy, never published |
| NEGATIVE_FIXTURE | 96 | named only by a test — must be missing |
| ROUND_ARTIFACT | 0 | `_r####bm?` round bookkeeping |
| MACHINE_SCOPED | 0 | another machine's local state |
| EXTERNAL_CANON | 4 | lives in the group tree above this repo |
| ABSENT_LOCALLY | 0 | in origin, not on this disk — one fetch |
| ORPHAN | 0 | **defect**: on disk, cited by real code, not in git |
| DELETED_LOCALLY | 0 | **defect**: in the index, gone from disk |
| DEAD_POINTER | 50 | advisory: real code names it, no clone has it |

## Dead pointers (advisory)

Real code (not a test) names these and no clone has them. Either that branch has never run, or the file was renamed and the reader was not updated. Neither is an orphan -- there is nothing on disk to publish -- and this census cannot separate the two cases, so they are listed, not counted as defects.

| family | count | examples |
|---|---|---|
| results | 17 | `...json`, `b.json`, `brand_new_face.json` |
| results/mass_trial | 8 | `mass_trial/w2_judge_shard_0of4.json`, `mass_trial/w2_judge_shard_1of4.json`, `mass_trial/w2_judge_shard_2of4.json` |
| research | 3 | `FOO_PREREG.md`, `b.md`, `ideas.md` |
| docs/daily_report | 2 | `daily_report/REPORT-YYYY-MM-DD.md`, `daily_report/REPORT-YYYYMMDD.md` |
| results/a5_acceptance | 2 | `a5_acceptance/PACK-YYYYMMDD.json`, `a5_acceptance/streak.json` |
| results/trial_labor_w20 | 2 | `trial_labor_w20/w20_judge.json`, `trial_labor_w20/w20_screen.json` |
| docs/live_book | 1 | `live_book/LIVE-BOOK-YYYYMMDD.md` |
| docs/live_usage | 1 | `live_usage/LIVE-YYYYMMDD.md` |
| docs/panel_coverage | 1 | `panel_coverage/COVERAGE-YYYYMMDD.md` |
| results/alphagen_w18 | 1 | `alphagen_w18/W18-2026-10-09.json` |
| results/ce_admission | 1 | `ce_admission/CE_ADMISSION_B1.json` |
| results/e44_midmonth | 1 | `e44_midmonth/ENTRYDELAY-x.json` |
| results/etf_book_order | 1 | `etf_book_order/ledger.json` |
| results/etf_composite_live | 1 | `etf_composite_live/ledger.json` |
| results/etf_paper | 1 | `etf_paper/ledger.json` |
| results/fusion_p1 | 1 | `fusion_p1/navs.json` |
| results/idx_fut_roll_gap.json | 1 | `idx_fut_roll_gap.json/.md` |
| results/local_coding_pilot | 1 | `local_coding_pilot/ledger.json` |
| results/paper | 1 | `paper/marks/marks-YYYYMMDD.json` |
| results/paper_export | 1 | `paper_export/export-YYYY-MM-DD.json` |
| results/post_review | 1 | `post_review/REPORT-YYYYMMDD.md` |
| results/t101_v4_a14 | 1 | `t101_v4_a14/shard_0of1.json` |

## How to read this

An ORPHAN is not a broken number -- it is a number nobody else can read. The face was computed here, a committed reader names it, and the file never entered git, so the same reader on another machine or in a fresh clone gets nothing (or, worse, catches the error and continues: the r98 shape, where a missing face is printed as zero). Adding the file to git is the whole fix.

Limits: (1) literal citations only -- paths assembled at runtime are invisible, so every count is a floor; (2) IGNORED comes from `.gitignore` policy and is not audited for whether that policy is still right; (3) the test-context filter trusts function names, so a real reader whose function happens to be called `test_*` would be hidden, and a fixture in a function with an innocent name shows up as an orphan; (4) the ast walk falls back to a context-free regex on files that will not parse, and those citations count as real; (5) ABSENT_LOCALLY is measured against `origin/main` as of this run, so a machine whose peer has not pushed yet looks the same as one behind.
