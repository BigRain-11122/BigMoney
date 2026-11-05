# DIGEST 2026-11-06 r1471.1 bm-b -- E453: mtime age cannot exceed the age of the checkout that set it

Study: `scripts/e453_abandoned_stale.py` (selftest 25/25, run rc0, check `problems=[]`,
verify `problems=[]`) -> `results/state_tilt/ABANDONEDSTALE-2026-11-06.json` +
`abandonedstale_latest.json`. Card: `knowledge/METHODOLOGY_ASSETS.md` **E453**.

## What was asked

E452 (`results/state_tilt/abandonedguard_latest.json`) found 11 read sites under a base no write
site produces, whose artifact is present, and stated that a guard announces absence and is silent
about age. E453 asks which of those present targets is stale at the cutoff and whether any reader
checks an age.

## What came back

| arm | reading |
|---|---|
| target ages at cutoff | min 8, max 20 days |
| threshold (`STALE_DAYS`, fixed before the data) | 180 days |
| class table | 11 `fresh_artifact`, 0 stale-checked, 0 stale-bare |
| age-check forms | 6 `reads_the_clock`, 4 `names_a_max_age_constant`, 0 `compares_an_mtime` |
| consumer split | 6 smoke-suite, 5 lane-host (0 stale in either) |
| bases contributing sites | 6 of the 7 E452 bases |

## The finding

The class table is not the finding; the floor block is. 58,178 files walked, **29,133 of them share
the mtime date 2026-10-17**, 20 distinct mtime dates in total, oldest 2026-10-16 ->
`max_identifiable_age_days = 21`. A checkout stamps every file with the materialisation moment, so
on this tree no file can measure older than 21 days. `180 > 21`, so the staleness question is **not
identifiable here**, and an all-fresh table is an artefact of the clone rather than evidence about
the pipeline.

Verdict published:
`mtime_age_cannot_exceed_the_checkout_floor_so_staleness_is_not_identifiable_here_and_every_fresh_reading_is_an_artifact_of_materialisation`.

## The law

Before any freshness/staleness claim from filesystem mtimes, measure the tree's mtime floor (oldest
mtime, modal mtime date + count) and compare `max_identifiable_age_days` against the threshold. If
the floor is younger than the threshold, publish **not identifiable**, not **fresh**. A staleness
gate that passes on a freshly materialised tree is measuring `git clone`.

## What remains true regardless of mtime

The age-check arm does not depend on the floor: every site's enclosing function is located and
published, 6 read the clock and 4 name a max-age constant or argument -- but a clock read inside a
reader is incidental hygiene, not a check that the bytes it just opened are current. No site
performs an `st_mtime` comparison.

## Guards shipped with the face

* `check` refuses a class that does not re-derive, a verdict that disagrees with the floor it
  publishes, a target older than its own published floor, and a site population that disagrees on
  identifiability.
* smoke leg `e453 abandoned base target staleness (r1471.1 bm-b)` refuses the same, plus a doctored
  control: a stale target with no age-check form must not grade fresh, and an identifiable floor
  must not produce the unidentifiable verdict.

## Next

The floor makes the mtime arm unanswerable on this clone. The two escape routes are (a) a producer
that stamps its own `as_of`/`built_at` into the artifact -- content-addressable freshness, which the
repo already uses for cutoffs -- or (b) a tree materialised long enough ago that the floor clears
the threshold. Neither is in scope for this face.