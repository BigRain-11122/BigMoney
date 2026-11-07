# DIGEST 2026-11-07 r1522 bm-b -- E496: does E479's residue class survive the mode arm?

Study: `scripts/e496_twin_mode.py` (run / check / verify / selftest 15/15)
Face: `results/state_tilt/TWINMODE-2026-11-07.json` + `twinmode_latest.json`
Card: `knowledge/METHODOLOGY_ASSETS.md` E496 (26/0 numstat)

## Question

E483 (r1521) measured 78 opener sites on E479's 36 latest-pointer twins: 57 read, 18 write,
3 indirect, and said "10 of the 30 twins labelled 'opened only by a leg' are in fact opened for
writing by the script that publishes them". Being written is not the same as having no reader.
This study re-derives the residue class for all 36 twins using read-mode openers only.

## Method

No re-implementation: population/residue via `e479.population()/scan()/classify()`, mode per
site via `e483.source_tree()/open_call_near()/mode_of_site()`, re-classification via
`e479.class_of()` fed with read-only sites, roles via `e483.role_of()`.

## Readings (2026-11-07; 36 twins / 95 sites = 66 read + 26 write + 3 indirect)

- Baseline residue vs reads-only: leg-only 30 -> 30 (unchanged), study 4 -> 4,
  producer-only 1 -> 0, never 1 -> 2. **One** class change, not ten.
- The single change: `results/market_clock/CALL_latest.json` (16 members / 30,743 B) -- its 7
  opener sites are all writes (`results/_r392_resolve6.py` x6 + `scripts/market_clock_call.py:406`),
  reads 0, so readings-only it is `never_opened_by_any_site_in_the_corpus`.
- Twins that lose their last reader: **0**. Writer as the only remaining opener: **0**.
  So E483's ten twins keep every leg read they had; the leg-only label was never wrong about them.
- Write sites by role (whole 36): instrument 13 / leg runner 7 / one-off round script 6;
  leg-role writes land on 4 twins (the same 4 as E483's doctor-harness twins).
- Retirement price unchanged: 21 members / 125,541 B retirable whole, identical before and after.
- Cross-check: on E483's 30-twin subset this study reproduces 57 read / 18 write / 3 indirect
  with deltas 0 (numbers machine-read from `legdebt_latest.json`, never restated from the card).

## PIT

1. "Written" is neither "unread" nor "mislabeled": re-reading a residue class means changing the
   *arm* (count reads only), not converting a count of write sites into a count of wrong labels.
2. A writer is a producer by construction -- E479 builds its producer map from write sites, so a
   field named "write sites not from a listed producer" is structurally 0. Published instead:
   write sites by *role*, with the structural zero disclosed next to it.
3. Two populations cannot be compared before the populations are named: 95 vs 78 is 36 twins vs
   30, not a reproduction failure. Reconcile on the subset, and take the sibling's numbers by
   machine read.
4. An unresolved (helper-handoff) site must stay its own class: counting it as a read would
   manufacture 3 readers and could lift a never-opened face into leg-only.