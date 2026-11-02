# DIGEST 2026-11-02 r1386 -- E364: the census family has a queue (and most of it cannot be rechecked)

**Study** `scripts/e364_unstamped_census.py` (selftest 28/28; `verify` problems=[])
**Face** `results/state_tilt/UNSTAMPEDCENSUS-2026-11-02.json` (+ `unstampedcensus_latest.json`)
**Leg** `Tools/s6_chain_bmb.py` -> `unstamped_census` (`e364 ... check`, ~4 s, no builds)
**Smoke leg** extracted verbatim by `scripts/run_e364_smoke_leg.py` (E355 rule: only the namespace the
suite provides), standalone 1/1.

## Question

E363 stamped two faces and found replay needs a `files=` seam. How much of the published census
family is in that state?

## Answer, measured

| | count |
|---|---|
| published studies (from `*_latest.json`) | 120 (121 faces) |
| resolved to a producer module | 117 (3 unresolved, reported by name) |
| studies that enumerate a directory | 28 (11 source corpus, 23 published faces, 6 both) |
| of those, quoting a population number | 15 |
| enumerating but quoting nothing | 13 |
| **naming the corpus they counted** | **2** (E331, E335 -- both with a `files=` seam) |
| **populations that cannot be rechecked** | **13** |
| need a `files=` seam before replay | 11 |
| stampable today (seam, no stamp) | 2 (E328 566 faces, E329 246 sources) |

Queue head by population size: E340 12,519 (flagged: 121 faces on disk), E350 2,343, E323 2,341,
E322 2,337, then E328 566 (stampable now).

## What the round had to get right

1. **Gate the name vocabulary on a structural fact.** A count key is only read as a population inside
   a study already measured to enumerate a directory; over `results/**` the same substring rule fires
   on 3,879 files and is worthless (E207/E208).
2. **Publish the refusals.** `median_of_file_medians_commits` 80 / `p90_...` 111 /
   `worst_file_p90_commits` 216 are statistics, `max_naive_writers_on_one_face` 973 is a maximum,
   `source_family_pairs` is a data population -- each rejected with its reason in the face.
3. **Over-rejection is the same disease.** `faces_named` 846 and `distinct_pointer_files_named` 20
   were refused by an earlier draft because "name" sat in the non-census list; narrowed to occurrence
   counts (`*_before`/`*_after`/`named_*`) after measuring what moved.
4. **A population can exceed its own directory.** E340's `faces_parsed` 12,519 vs 121 faces on disk is
   flagged, not dropped and not believed.
5. **Address kind.** The queue's populations are mostly over *published faces*, so a source-corpus pin
   would be a false address (the shape E331's leg refuses). Rows carry `population_kind` + `needs`.
6. **The leg fails on regressions, not on growth.** A study that loses its address is rc 1; a study
   new to the queue is printed and passes.

## Next

E365 (seeded): pin the *published-face* corpus the way E361 pins the source corpus, then stamp E328
(566 faces) at build time and replay it through its existing `files=` seam -- the first face whose
population is faces, not sources.