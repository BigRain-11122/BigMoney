# E274 -- can a row's own numbers say, in advance, whether an axis will move it?

**Face** `results/state_tilt/BANDSTRADDLESWEEP-2026-10-29.json` (+ `bandstraddlesweep_latest.json`)
**Runner** `scripts/e274_spread_straddle_sweep.py` (run / verify 0 problems / selftest 29/29)
**Source** four published faces: BANDTRANSFER (rows + arms), BANDTIGHT, BANDDONORCHOICE, BANDTOPFLIP.
No band rebuilt, no shuffle drawn, no panel, no bill.

## The question

E271 answered the donor question case by case: the donor axis is decisive only on the rows whose
flip multiplier falls inside the p95 spread their `(leg, base)` group actually offers. That is a
mechanism, so it should be a *screen* -- but it had only ever been scored on one axis, against the
one moved set one face happened to publish. A reader does not care about the donor axis in
isolation; they care whether "do not borrow from this cell" is decidable from two numbers without
re-running anybody's sweep.

So the family was walked asking the same question three times, on the three axes that publish
**both** halves of the answer:

| axis | range offered | published moved set |
|---|---|---|
| `wide_donor` | the group's p95 spread (BANDTRANSFER arms) | BANDDONORCHOICE `moved_row_indices` (E271's sweep) |
| `tight_p05` | the same group's p05 spread | BANDTIGHT `rows_could_move_within_observed_p05_range` |
| `top_ladder` | the row's own `[multiplier_min, multiplier_max]` | BANDTOPFLIP `depends_ids` |

Per row: the flip multiplier (`b/lo` on the negative side, `b/hi` on the positive), the range, and a
four-way reading -- `inside` / `near_edge` (inside but within 5% of the range width from an end) /
`outside` / `untested`. Never a bare boolean: an untested row must not read as "safe".

## Answer

**The screen is exact on all three axes: 4 moved observations, 4 hits, 0 missed, 0 flagged-but-inert.**

| axis | rows | straddlers | published moves | missed | inert |
|---|---|---|---|---|---|
| wide_donor | 12 | {9, 13} | {9, 13} | -- | -- |
| tight_p05 | 12 | -- | -- | -- | -- |
| top_ladder | 12 | {E252:STARSELF/early_three/cross, E251:STAROWN/early_three/star_lag1_residual} | same two | -- | -- |

So `do not borrow from this cell` **is** decidable in advance from `m_flip` and the offered range,
on this population. Two disclosures keep that from being over-read:

1. **12 rows, 4 moved observations, one book.** Above the 3-positive floor but untested at scale;
   the verdict says so.
2. **The near-edge band (5% of range width) is disclosed, not absorbed.** A row flagged `near_edge`
   counts with the flag but is published apart from a decided `inside`, so the exactness is not
   borrowed from rows sitting on a boundary.

## The trap that broke the first cut

`BANDTOPFLIP.summary` publishes **two** movement sets:

* `flipped_ids` -- rows that flip at **every** published measurement (empty on this population)
* `depends_ids` -- rows that flip at **some** measurement (2 rows)

The first cut scored the `flipped_ids` set (it reads like "the rows that flipped") and reported the
two real moves as **screen misses**, i.e. it would have published `the_screen_is_unsafe_on_some_axis`
off a lookup error. The straddle flag answers "can this row move at all", so the matching published
set is the SOME set. Both sets are now carried, and their gap is published arithmetically as
`moves_only_in_the_weaker_set` rather than chosen silently.

This is the same-name-different-quantity family as r1292/r1315 (cpu_pct holding memory load) and
r1280 (a delta column keyed by the compared column rather than the arm): the name promised one
measurement and the value was another.

## Pits born here

1. **Join keys must match the published id format.** `depends_ids` is `source/cell/row`; the first
   cut built `source/row`, so every id missed and the face looked unsafe. A join that silently
   matches nothing looks exactly like a screen that fails -- the key shape is part of the contract.
2. **Integers in one list, strings in another.** `published_moved` came from a face of ints while
   `moves_only_in_the_weaker_set` was built by stringifying, so the smoke leg's arithmetic check
   failed on types alone. Normalise once, at the point the set is built.
3. **A zero-width range cannot decide anything.** `straddle(m, 3.0, 3.0)` returned `inside` under
   the plain interval test; the reading must be `untested`, because a single point offers no spread
   to be inside of (E269's degenerate-`cross:200` family, one level down).
4. `group_ranges` must not invent an entry for a `(leg, base)` pair with no arms -- an empty range
   record reads downstream as "range published, nothing inside it".

Evidence: `scripts/e274_spread_straddle_sweep.py` (selftest 29/29, verify 0 problems),
`results/state_tilt/BANDSTRADDLESWEEP-2026-10-29.json` (verdict=
`two_published_numbers_predict_every_scored_axis`; 12 rows x 3 axes, 4 moved observations, 4 hits),
source faces BANDTRANSFER / BANDTIGHT / BANDDONORCHOICE / BANDTOPFLIP (all 2026-10-29),
S6 leg `spread_straddle_sweep` (rc=0, 0.16s), digest
`research/digests/DIGEST-20261031-r1299-e274-straddle-sweep.md`.