# E291 - the ambiguity flag is the length base rate, and equal lengths are shape, not luck

**Round** r1313 (bm-b) · **evidence_cutoff** 2026-10-29 · **card** E291 · **pool** E291-AMBIGUITY-BY-LENGTH-CHANCE

## The question E290 left open

E290 published 12 of 27 checkable counts as ambiguous because another list of the same unit in the
same face has the same length. That flag only informs a reader if an equal length can be an accident.
If lengths collide routinely -- because a face draws all its arms from one schema, or three of four
lists of one unit are length 4 -- then "ambiguous" is a statement about the face's shape and says
nothing about the count.

Both halves are measured here, and they disagree in a way that is itself the answer: the flag's RATE
is exactly what the length distribution predicts, while the flag's MECHANISM is not chance at all.

## The rate is the base rate

| level | observed | expected from the pooled length distribution | tail p |
| --- | --- | --- | --- |
| the 27 checkable rows (E290's own set) | 12 flagged (44.4 pct) | 10.78 (39.9 pct) | 0.384 |
| all 125 eligible same-unit lists | 104 (83.2 pct) | 84.24 (67.4 pct) | 0.00005 |

The 12-of-27 rate carries no information: it is what you get from the length mix alone. All 12 rows
also come from just **two** scopes -- `BANDFLIPBUDGET :: cells` (8 rows) and `BANDGAPCEILING :: rows`
(4 rows) -- so they are two observations wearing twelve labels.

At list level the opposite happens: 83.2 pct against 67.4 pct expected. Lengths are MORE concentrated
inside a face than the pooled mix predicts, which is what a shared schema looks like. The pooled
length mix is lopsided to begin with (`24` appears 50 times, `4` 35 times, `16` 12 times, `1` 10
times), so a large base rate was never in doubt.

## What an equal-length pair actually is

All 746 equal-length pairs, classified by content:

| class | pairs | share | reading |
| --- | --- | --- | --- |
| same record schema, different rows | 605 | 81.1 pct | the face's shape repeating (25 `cells` lists of 24 each) |
| the very same list content (alias) | 135 | 18.1 pct | a duplicated list -- a hygiene finding, not a conflict |
| genuinely different content | 6 | 0.8 pct | the only pairs where a count could be read two ways |

So "two lists of the same unit with the same length" is 99.2 pct structure. The flag E290 publishes is
therefore honest but weakly informative in the direction its name suggests: it marks a shared record
shape, and it catches 135 duplicated lists that nothing else in the family reports.

## Why this is not just a re-derivation

The row set, the alternative counts and the flag are read from E290's published face (join asserted:
27 = 27 rows, 12 = 12 flags, identical ambiguous-row set). Only the equal-length classification is
measured here. Two aggregators are published with their own tail probabilities and the split is
declared on the face rather than smoothed away.

## Pits taken in-window

1. **Self-inclusion, fourth sighting.** `e286.face_universe()` only excludes E286's own faces, so
   E290's `BANDSELFAUDIT-2026-10-29.json` is inside the census universe (33 faces, not 32). A
   successor study must filter its sibling's face by name as well as its own; this face asserts both
   absences in `identity_check` and a smoke leg re-checks that E290's face is not censused.
2. **A rate without its null is not a finding.** The first draft of the verdict rule looked only at
   the row rate; with 12 vs 10.78 that would have been read either way. The rule now requires BOTH
   the tail to exceed alpha AND the structural share to fall below 0.5 before it may call the
   ambiguity real, so a high base rate cannot manufacture a conflict.
3. **Rows are not independent.** Publishing "12 of 27" without "2 scopes" inflates the evidence by
   6x; `distinct_scopes_behind_the_flag` and `rows_per_scope` are on the face and pinned by a
   selftest leg.

## Verification

* `python scripts/e291_ambiguity_chance.py selftest` -> **17/17**
* `run` then `verify` -> **0 problem(s)**; decisive blocks re-derive twice
* S6 leg `ambiguity_by_length_chance` -> rc=0 (wired after `self_auditable_face_profile`)
* smoke leg `product: an equal-length sibling is the face's shape repeating, not a coin flip` -> PASS
  (verified standalone by exec-ing the leg's own source out of `smoke_test.py`)
* identity: joins E290 (27 rows / 12 flags / identical ambiguous set), content classes partition the
  746 pairs, scopes partition the flagged rows, both self face and source face absent from the census