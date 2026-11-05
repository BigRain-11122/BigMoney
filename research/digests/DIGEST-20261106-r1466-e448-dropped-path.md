# DIGEST 2026-11-06 r1466 bm-b -- E448: the dropped composition is usually a dead pointer, not a lost write

Card: `E448-WHICH-COMPOSED-AND-DROPPED-PATH-IS-STILL-WRITTEN-BY-ANOTHER-BRANCH`
Face: `results/state_tilt/droppedpath_latest.json` (`DROPPEDPATH-2026-11-06.json`)
Producer: `scripts/e448_dropped_path.py` (selftest 19/19, `verify problems=[]`, `check problems=[]`)
Leg: `smoke_test.py` `# E448 (r1466 bm-b)` + `scripts/run_e448_smoke_leg.py` (1/1 green, 1/1 red doctored, sha in == sha out)
S6: `Tools/s6_chain_bmb.py` leg `dropped_path_open` (`check`, rc 0, 0.1 s)

## Question
E442 published 85 compositions that are never used in the scope that composed them and graded none
of them. A dropped composition is harmless when it was superseded (the same file opens a path under
the same parent) and wrong when the intended write never happens.

## Answer
85 drops over 69 files, 4,655 opener calls scanned, verdict
`some_dropped_path_compositions_are_opened_nowhere_in_their_file`.

| class | n |
|---|---|
| superseded_by_a_wider_open | 19 (exact re-open of the same path 10, sibling under the parent only 9) |
| opened_nowhere_in_the_file | 30 |
| parent_not_resolvable (temp dir / parameter) | 33 |
| not_a_path_composition (`"\n".join(lines)`) | 3 |

Of the 30 orphans: **25 name a path that already exists on disk**, 2 name a path that does not
exist (both `K:` group-layout anchors -- dead on this host), 2 are glob patterns
(`FAMILY_GLOB = results/trial_labor_w*`, never globbed), 1 is not checkable.

The largest single orphan family is a dead research-note pointer: six study scripts compose
`os.path.join(ROOT, "research", "<STUDY>-P1.md")` as a `PREREG` constant and never open it -- all
six notes exist (hand-authored). It is a dead read, not a lost write, and the disk probe is what
makes that visible.

## Pits (both were in the instrument)
1. `__file__` was resolved to the repo root, so `ROOT = dirname(dirname(abspath(__file__)))` landed
   one level above the repo (parents read as `.../quant/results` instead of
   `.../quant/bigmoney/results`) and the disk probe reported 1 present instead of 25. The selftest
   fixture had been written with the same wrong anchor, so it agreed with the bug. Fixed by seeding
   the constant environment with the module's own path and pinning both dirname shapes.
2. A prefix test is not a boundary test (parent `r` must not cover `results/x.json`), and a `.git`
   plumbing write under the repo parent is not evidence about the artifact -- 2 such hits are now
   published in `ignored_hits` and counted separately instead of superseding the drop.

## Method limits (published on the face)
The parent is a string prefix of the composed key, not a filesystem question; resolution follows only
a literal or a module-level constant of the same file; superseded means "some open in this file lands
under that parent", not "the intended artifact exists"; openers are recognised by a frozen tail
vocabulary, so an aliased opener (`op = open`) is invisible; static only.

## Next card (seeded)
E449: of the 25 orphans whose composed path already exists, how many are a `PREREG`/`NOTES`
document pointer that the study's own code never reads -- i.e. how many published studies declare
their prereg as documentation only, and does any study's *result* depend on the note?