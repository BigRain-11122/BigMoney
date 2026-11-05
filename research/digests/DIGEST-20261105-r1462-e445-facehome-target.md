# Digest -- E445: the live face-home rows compose a doubled path, and the target already exists at the repo root

Round r1462 (bm-b), 2026-11-05. Card `E445-WHICH-LIVE-BASE-ALREADY-RECEIVED-A-FACE-NAMED-WHAT-THE-JOIN-WOULD-COMPOSE`.
Producer `scripts/e445_facehome_target.py`. Face `results/state_tilt/facehometarget_latest.json`.

## The question

E441 (r1461) graded each face-home base of E435 as live (a member was written after the carrier) or
frozen, and read the 82 composable rows on a live base as "one round away" from a landing target.
E445 asks the sharper question: does any of those bases already hold a face whose basename is what
the row's own name field would compose onto it?

## The reading

| class | rows |
|---|---|
| `target_already_exists` | 0 |
| `target_is_the_carrier` | 0 |
| `target_would_be_new` | 36 |

36 live composable rows over 9 bases, from 3 carrier spellings (`SHADOWFACE-2026-11-04.json`, its
`-2026-11-05` twin, `shadowface_latest.json` -- one face republished three ways, so 36 rows = 12 x 3).

Every candidate composes a **doubled** path: the carriers' name field is `path`, holding a full
relative path (`results/tom_overlay/latest.json`), so `join(base, name)` gives
`results/tom_overlay/results/tom_overlay/latest.json`.  `rows_where_the_composition_repeats_the_base`
= 36 of 36.

The part that makes it a defect: **the same name resolves from the repo root on 36 of 36 rows** --
nine distinct names, all present on disk, none newer than the carrier.  The target exists now and
only the join misses it.  E441's live/frozen axis measured the mtime of a directory while the reader
it stands in for composes a name that is already a path, so "one round away" is wrong for every live
row in this population.

## What the face carries

* per row: `target_class`, `landing_targets`, `composition_repeats_the_base`,
  `name_field_is_already_a_path`;
* per candidate: `name_value`, `composed_path`, `exists`, `is_the_carrier`,
  `composition_repeats_the_base`, `name_value_resolves_from_the_repo_root`,
  `basename_published_elsewhere`, `own_output`;
* summary: class table, candidate counts, `distinct_carriers` (3) / `distinct_live_bases` (9),
  `rows_where_the_target_exists_but_the_join_misses_it` (36), and a `distance_check` against E441's
  own published population.

## Verification

`selftest` 24/24; `verify` problems=[] (re-derives the population, the class table and every
candidate from the live tree); smoke leg `e445 face-home target` PASS; S6 leg `face_home_target`
rc=0 in 142.8s.

## Follow-on

E446 seeded: the 51 frozen bases were graded by mtime only -- ask whether the corpus holds a writer
for each of them at all (dormant vs abandoned).