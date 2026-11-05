# DIGEST 2026-11-06 r1471 (bm-b) -- the ten standing suite reds, named and republished

## What the last round left open

r1470's postscript named one P0 for this window: *re-run the smoke suite with a capture file so its
standing FAILs are named*. Every earlier window launched `python -m smoke_test` without redirection,
so the process ran for an hour and no leg's verdict survived it.

## What this window found

The suite was captured (`results/_smoke2_r1471.out`) and finished with **10 FAILs, 9 of them the same
class**: `the published summary does not re-derive from the live tree`. Every one of those faces was
correct when it was published and has been stale since the tree grew around it:

| leg | module | repair |
|---|---|---|
| wrong-side reader | `e390_wrong_side_reader` | republish: 1989 rows/75 sites -> 1993/77 (4 more `not_a_read`) |
| latest.json convention | `e398_latest_family` | republish 227 -> 232 readers **plus** content-anchored site keys |
| refresh vs read signal | `e408_writer_refresh_signal` | republish |
| unfloored faces | `e409_unfloored_faces` | republish |
| reader tiers | `e411_reader_tiers` | republish |
| red-capable readers | `e416_fresh_aim` | republish |
| face age | `e418_face_age` | republish |
| age-unknowable population | `e419_unstampable` | republish (9 -> 15 faces) |
| basename census audit | `e422_basename_census_audit` | republish |
| shadow face | `e417_shadow_face` | republish |
| directory-valued field | `e435_dir_is_a_face` | republish (571 -> 588) |

The tenth was not a study: **the heartbeat's GPU face carried 37 keys from a dozen rounds, disagreeing
by 216 MiB**; `Tools/gpu_face.py apply` re-probed once and wrote every alias from the same nvidia-smi
reading (`audit` then returns no findings).

## The durable lesson (card E454)

`e398` verified each published read site by its `file:line` address. Its corpus includes
`smoke_test.py`, which gains legs every round, so seven published addresses resolved to nothing --
sites that still exist thousands of lines away. A line number in a growing file is not an identity.
Sites are now verified on a content anchor `(file, kind, expr, occurrence index)`; the human address
stays in the face and a moved address is published as `address moves=N` instead of as a defect.

## What was NOT fixed

`product: dashboard carries the marks coverage gap` stays red: `results/dashboard_status.json` is last
written 2026-10-31 and `monitor/build_status.py` is single-writer on bm-a. A local rewrite would make
a second writer for a face bm-a owns, so the red is named and handed over rather than papered over.

## Evidence

`results/_smoke2_r1471.out` (first captured run: 281 pass / 3 fail / rest of the legs, then the two
owned reds fixed), `results/_smoke3_r1471.out` (final run started after the repairs),
`results/_rebuild_r1471.out` (the eight-face rebuild loop: all rc=0).