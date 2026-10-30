# DIGEST 2026-10-31 -- E270: the guard's reach is a coverage fact, not an arithmetic one

**Card** knowledge/METHODOLOGY_ASSETS.md E270
**Face** results/state_tilt/BANDFIELDS-2026-10-29.json (verdict `guard_inputs_are_face_local`)
**Runner** scripts/e270_guard_field_audit.py (selftest 29/29, verify 0 problems)
**Chain leg** `guard_field_audit` (rc=0, 0.07s)
**Pool** E270-GUARD-FIELD-AUDIT done; E273-GUARD-FROM-THRESHOLD seeded

## What was asked

E267 shrank the transfer screen to one operative rule -- judge a row with its OWN side's p95.
E268 then showed that the row's own p95 is the number a table reader does not have, and that the
pooled tight end substitutes for it. Both statements are about numbers that were *published*, so
the screen's real reach is bounded by a question nobody had measured: **which published faces
actually carry the four inputs the rule consumes?**

## What was measured

Domain = every dated `BAND*` face under `results/state_tilt` (18 after excluding the `_latest`
mirrors and this study's own output). For each record collection: which of
`b / band_lo / band_hi / own_p95` are present, how many records carry all four, and which
verdict-shaped fields sit on records carrying none of them.

| bucket | count |
| --- | --- |
| faces scanned | 18 |
| record collections | 86 |
| collections carrying ≥1 guard input | 25 |
| collections carrying the FULL triple | 4 (72 record-readings, 3 on measured rows only) |
| verdict collections with no guard input | 27 (584 records) |
| joined guard cells | 420 -- **420 agree, 0 disagree, max abs diff 0.0** |

So the guard is re-runnable exactly where the triple lives (`BANDSCREEN /comparison_rows`,
`BANDTRANSFER /rows`, `BANDTIGHT /rows`, `BANDNEAR1 /rows`) and is a black box on the derived
faces that publish margins, curves or thresholds instead.

## Why the join is the load-bearing half

Counting fields would leave "present" ambiguous: two faces can both carry `own_p95` and publish
different numbers, in which case a reader picking a different page gets a different screen. Joining
each record to the canonical row for the same index compares 420 shared cells and finds zero
disagreement at |diff| = 0.0 -- the family's gap is **coverage, not inconsistency**. That is a
different conclusion from "the faces disagree", and only the join can tell them apart.

## Disclosures

* `b` is two different quantities in this family: the row's own move (row faces) and the clearance
  curves' buffer grid (9 collections). Buffer grids are published under `b_without_a_band` and kept
  out of the row census; folding them in would read a 43-value sweep as 43 half-built rows.
* The domain excludes `*_latest.json` (byte copies of a dated face) and the study's own face --
  self-inclusion is the r1238 defect that makes a second burn answer differently.
* A record with no `index` is counted `unjoined`, never dropped; both counts are published.

## Pit (one, in-window)

The first burn published `canonical: none` / `cells_compared: 0` and still printed a coverage
verdict. Cause: `canon_map` required a collection whose *every* record carried all four inputs, but
unmeasured rows hold `None` in precisely those fields, so the true canonical collection was rejected
and the value cross-check silently measured nothing. Rule now: the collection with the **most
complete** records, with `canonical_basis` and `cells_compared` published so the degenerate case is
visible rather than green.

## Next

E273-GUARD-FROM-THRESHOLD: a missing triple is not necessarily a missing screen -- `BANDMARGIN`
publishes `t_side` / `t_max_end` per comparison, so the decision `donor_p95 > t` may be reachable
from a threshold alone. Score that substitute against the published `actual_moved` and state which
faces a reader can actually run the screen from.

## Second pit: a count that moves is not a re-derivable count

The domain grew **mid-round** -- a downstream S6 leg published `BANDPATH-2026-10-30.json` while this
face was being written -- and every total moved (17 -> 18 faces, 536 -> 584 records). A scan whose
input is a *directory* has to publish the inventory it measured and re-derive over that list:
`verify` now takes `source_faces` as its scope and reports a grown/shrunk domain as a notice
("re-run to republish"), never as a silent change of the published numbers. This is the same
family as the r1285 multi-shape pit: a face is a measurement of a moment, and the moment has to be
named.
