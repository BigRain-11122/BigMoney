# DIGEST — E470: the targets of pointers that need another base are opened by nobody (r1493 bm-b)

**Face.** `results/state_tilt/TARGETREAD-2026-11-06.json` (+ `targetread_latest.json`)
**Producer.** `scripts/e470_target_read.py` (run rc0 / `check` problems=[] / `verify` problems=[] / selftest 26/26)
**Population source.** `results/state_tilt/pointerreach_latest.json` (E468 rows, re-read, not re-derived)

## Question

E468 (r1492) measured who NAMES the 37 pointer instances whose target needs a base other than the
repo root: 24 distinct targets, 16 named by no source, 8 naming sites inside the producer of the
target. Naming is not reading (E207 / E436 / E466). The open question was whether the target FILE
is ever opened by any route — by the producer checking its own output, by a study that knows the
literal, by a glob, or by nobody.

## Reading

| channel | targets |
|---|---|
| never opened by any site in the corpus | **17 of 24** |
| opened only by a smoke/runner leg | 5 |
| opened only by a one-off round script | 2 |
| opened only by its own producer | 0 |
| opened by an unrelated study | 0 |
| reached only through a glob | 0 |
| pointer-key read sites (open the pointing face AND carry the key) | 0 |

All 24 targets exist on disk. Opener sites: 24 total, 2 spelling the whole repo-relative path and
22 spelling only the basename (the base is not proven by the site). Verdict:
`some_targets_that_need_another_base_are_never_opened_by_any_site`.

## Why the first drafts read differently

1. **fnmatch is not glob.** With fnmatch semantics a single `glob('*')` in
   `scripts/e273_guard_from_threshold.py` "reached" 24 of 24 targets, so the face read 17 targets
   as glob-reached and 0 as never opened. Matching is per segment now (`*` inside one segment,
   `**` across) and a pattern with no literal segment is refused as an unbounded sweep. Glob sites
   24 → 0; the never-opened count 0 → 17. A channel that constrains nothing cannot explain
   anything.
2. **Wrong stem rule on one side of the join.** `e468.producer_map` is keyed by
   `e464.face_stem` (dates and separators stripped), so looking the target up by `splitext` never
   matched a producer and the producer class came out empty while every writer's own write looked
   like an unrelated reader.
3. **A composed path is two hops away.** `p = os.path.join(HERE, 'lane', NAME)` then `open(p)`;
   one-hop name resolution published `lane` and lost the file name, so the writer's own open() was
   invisible. Names are now resolved transitively (4 rounds, cycle-safe).

## Consequence for the corpus

A `source_face`-style pointer with a bare filename is documentation, not a dependency: no program
in this tree follows it, so publishing the target as a repo-relative path would not by itself make
the edge live — an opener has to exist. Any future audit that claims a pointer is "used" must show
an opener site, not a string match.