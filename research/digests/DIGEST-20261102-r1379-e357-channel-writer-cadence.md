# DIGEST 2026-11-02 r1379 -- E357: who writes a lagging channel file, and at what cadence

**Question (pool card E355-WHO-WRITES-EACH-LAGGING-CHANNEL-FILE-AND-HOW-OFTEN, seeded by r1374 at
E352 close).** E352 measured that 58 of 59 deciding channel files lag their newest writer, median 80
commits, and stopped at the number. Ask who writes each of them and at what cadence, then test
whether each file's lag is bounded by that cadence.

**Answer.** For 46 of the 59 files the question has no answer, and that is the finding: they are
written **exactly once** in the 240-commit window. They have an age, not a cadence. Only 8 files
have a rewrite interval to compare a lag against, and they split 4 inside / 4 beyond.

| | count |
|---|---|
| files measured (E352 `measured=true`) | 59 |
| written exactly once in the window | **46** |
| not written in the window at all | 4 |
| rewritten by the boundary commit | 1 |
| have a cadence, lag inside it | 4 |
| have a cadence, lag beyond it | **4** |
| declared writer pairs (E352) | 1291 |
| pairs that ever co-changed with the file | **54** |
| ...of which are the suite itself | 54 |
| declared pairs that never co-changed | **1237 (95.8%)** |

Beyond-cadence (the only four files whose reader gets a copy older than the file's own rhythm):

    results/state_tilt/bandswitch_latest.json     lag 22 / cadence 4.5   7 writes
    results/state_tilt/precisiongap_latest.json   lag 26 / cadence 9.0   4 writes
    results/state_tilt/gatetol_latest.json        lag 45 / cadence 3.0   2 writes
    results/state_tilt/addos_latest.json          lag 56 / cadence 50.0  3 writes

Inside: `precisioncensus_latest` 8/10, `replaycensus_latest` 8/10, `reachwide_latest` 15/32,
`quantityname_latest` 17/43.

## The two wrong answers this shipped before the right one

1. **Co-commit as proof.** Any source that changed in the same commit as the file was called its
   producer. `smoke_test.py` is touched in 102 of 240 commits, so a file rewritten once co-occurs
   with it necessarily -- the suite became producer of the whole channel and every fastest period
   came out **2.0**. Symptom: `distinct_fastest_periods: [2.0]`, 54/54 "stale". Exactly the r1261
   shape (two populations equal because nothing ran). Fixed by excluding the harness and by
   refusing any source present in >40% of commits; `periods_collapsed` now forces the verdict to
   `measurement_collapsed` so the shape cannot be published again.
2. **Source edits as cadence.** Requiring >= 3 source edits inside the window then reported that
   *no* channel file has a standing producer, because a producer that runs every round but whose
   code has not been edited in 240 commits has zero touches. Both drafts measured source edits.
   Production is the file's own change history.

## Wiring

* `scripts/e357_channel_writer_cadence.py` -- build / verify / selftest **26/26**; verify re-derives
  classes and the partition against the face's own pin, **0 problems over 59 rows**.
* `results/state_tilt/CHWRCAD-2026-11-02.json` + `chwrcad_latest.json`.
* S6 chain leg `channel_writer_cadence` (verify, **3.31 s rc=0** through the runner).
* smoke leg E357 -- **structural on purpose** (partition sums, no collapsed cadence, stored verdict
  re-derives, no beyond-cadence row without a cadence, the suite is never named a producer), so it
  cannot go red the moment a face is republished. Extracted verbatim from `smoke_test.py` by
  `scripts/run_e357_smoke_leg.py` and executed in the suite's own namespace (E355 rule): PASS.
* Card E357 in `knowledge/METHODOLOGY_ASSETS.md`.

## Bound

Population is E352's; the window is E352's 240 first-parent commits, so the two studies cannot
disagree about what a round is. The window is HEAD-based, so every commit moves it -- the face is a
snapshot, and `verify` at the face's pin is what makes it re-derivable. Co-change is in-repo
evidence only: a producer that writes a face from a machine outside this clone leaves no trace here
and is published as `declared_only`, never as absent.