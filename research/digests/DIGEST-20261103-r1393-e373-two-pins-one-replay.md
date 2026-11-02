# DIGEST 2026-11-03 r1393 bm-b -- E373: two vintages, one replay, and neither tree explains its own face

Queue card: E373-E353-WAS-PUBLISHED-FROM-ANOTHER-COMMIT. Face:
`results/state_tilt/TWOPINS-2026-11-02.json` (+ `twopins_latest.json`). Method card: E373 in
`knowledge/METHODOLOGY_ASSETS.md`.

## What was measured

E350's face records pin `daf9a897` (evidence cutoff 11-01); E353's face records `e847e099` (cutoff
11-02). E369 had taken ONE pin -- at E350's commit -- and reported that the arms reproduced, which is
the sentence "the pin covers the face". E373 takes both pins and crosses each study over both trees:

| arm | corpus_sources | fields_with_no_writer | guard_fields_with_no_writer | pairs |
|---|---|---|---|---|
| E350 published | 2343 | 1698 | 131 | -- |
| E350 @daf9a897 (own) | 2251 | 1687 | 129 | -- |
| E350 @e847e099 | 2254 | 1687 | 129 | -- |
| E353 published | -- | -- | -- | 131 |
| E353 @daf9a897 | -- | -- | -- | 129 |
| E353 @e847e099 (own) | -- | -- | -- | 129 |

Verdict (re-derived by the module, not written by hand):
`neither_study_reproduces_at_either_publishing_commit_so_the_published_numbers_come_from_neither_tree_and_the_pin_alone_does_not_explain_them`.

Pins: 2251 members @daf9a897 (pin_id 7aacd4d5), 2255 @e847e099 (pin_id b461158b); overlap common
2251, only in the older tree 0, only in the newer tree 4 (`scripts/e350_field_branch_census.py`,
`e351_gate_state_census.py`, `run_e350_smoke_leg.py`, `run_e351_smoke_leg.py` -- the corpus rule
excludes only the walking study's own file, so the newer tree counts 3 of them).

Bills, side by side (measured against E361's 11-02 disk pin, a population of the same family):

| commit | population | fetched | absent | must be stored |
|---|---|---|---|---|
| daf9a897 | 2368 | 2240 | 128 | 128 |
| e847e099 | 2368 | 2240 | 128 | 128 |

## Findings

1. **A pin is a property of a vintage, not of a study.** E353 was published from `e847e099` and does
   not reproduce there either: its 2 missing pairs are members no commit holds. E372 recovered 125 of
   the 128 from disk and 3 from history to reach 131. So the bill is not "one pin per study" either --
   it is a pin per vintage PLUS a store of the members the publish-day working tree carried.
2. **`guard_never_fires_on_a_falsy_value` = 34 comes back in all four cells**, while `pairs` and the
   `by_state`/`by_class` tallies move only where `pairs` moves. Shape of the number decides
   reproducibility: a predicate count over the population survives a 4-member drift; a total over the
   population does not.
3. **The verdict is a whole-cell notion.** A cell reproduces only when every comparable key does;
   a partial cell must still be published key by key, which is why "neither tree explains the numbers"
   can sit beside a key that does come back.

## Honest bounds

The pin covers the SOURCE population only: E353 reads faces from today's disk via `build_index()`, so
a cell proves the source vintage, never the faces' vintage. Keys that are not identical across the two
studies are compared within their own study and never across. The store bill is measured against
E361's disk pin, so it bounds the members a commit cannot supply -- it does not rebuild either face's
exact input.

## Wiring

- `scripts/e373_two_pins_one_replay.py` (run / verify / selftest 12/12; verify problems=[])
- `scripts/run_e373_smoke_leg.py` + smoke leg in `smoke_test.py` (exec'd verbatim, 1/1)
- E372 and E369 legs re-run after the insert (1/1 each); `smoke_test.py` compiles
- Pins: `results/state_tilt/CORPUSPIN-AT-COMMIT-daf9a897.json`, `...-e847e099.json`

## Provenance note

The run itself was executed by an orphaned process (parent dead at ~00:30, CPU live) that the
accepting window inherited at 00:47; `verify` and `selftest` were re-run by the closing window and the
face was not edited. The face's `evidence_cutoff` is 2026-11-02 because the study was designed and
claimed in r1392 (23:57) and its `TODAY` constant pins the dated face name.