# Digest r1390 -- E368: a repaired seam pins the population, not the number

Face: `results/state_tilt/SEAMREPLAY-2026-11-02.json` (+ `seamreplay_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E368. Study: `scripts/e368_seam_replay.py`.

## What was repaired

E366 published ten studies as `NEEDS_SEAM`: their `build()` takes no member list, so any replay
re-walks the tree. This round repaired the root walker and its consumer:

- `scripts/e350_field_branch_census.py` -- `_sources(files=None)` and `build(pin=None, files=None)`;
  a member may be `relpath` or `(relpath, text)`, so the *list* and the *bytes* are two seams.
  `population_source` is published on every face; `pin_members(path)` reads a pin file; the CLI
  takes `build --files <pin.json>`.
- `scripts/e353_unwritten_guard_presence.py` -- `_population(files=None)` /
  `build(pin=None, index=None, files=None)`, inheriting E350's seam instead of walking privately.

## What it measured (pin: 2,368 members @ 1,244ee23)

| arm | E350 corpus_sources | fields_with_no_writer | guard_fields_with_no_writer | E353 pairs |
|---|---|---|---|---|
| published | 2,343 | 1,698 | **131** | **131** |
| live walk | 2,392 | 1,717 | 131 | 131 |
| pinned list (today's bytes) | 2,367 | 1,356 | 131 | 131 |
| pinned bytes (disk else git) | 2,367 | 1,356 | 131 | 131 |

Byte provenance: 2,361 disk / 6 git / 1 `store_needed` (`Tools/s6_chain_bmb.py`) / 0 unreadable.

Verdict: `a_pinned_replay_reproduces_the_published_number_yet_the_pin_is_not_the_publishing_commit_so_the_reproduction_is_stability_not_provenance_and_a_pin_must_be_taken_at_the_face_it_serves`

## The four readings worth keeping

1. **The seam is insurance, not a repair.** Every number the two verdicts rest on came back
   unchanged across all four populations -- including the live walk that skips the seam entirely.
2. **A neighbouring count in the same face is not stable**: `fields_with_no_writer` 1,698 -> 1,356
   (pinned) -> 1,717 (live). One face, two counts, one moving ~20%: which population produced a
   number has to be published beside it.
3. **List-only replay reads today's bytes.** The 19 members whose sha256 no longer matched the pin
   were resolved from the pin commit, and the 1 untracked member is disclosed as `store_needed`
   instead of being silently borrowed from disk.
4. **Vintage, not reproduction.** The pin commit (1,244ee23) is not the commit E350's face was built
   at (daf9a897), so "131 comes back" is stability evidence. A pin taken for a face must be taken at
   that face's commit; otherwise E366's bill is pins-per-vintage.

## Wiring

- `smoke_test.py`: leg `E368` re-derives the verdict from the face and refuses an arm claimed to
  reproduce with a non-zero delta, a missing `population_source`, a provenance that does not sum to
  the pin, a vintage block naming one commit, or a plain "reproduced" verdict over another vintage.
  Run standalone by `scripts/run_e368_smoke_leg.py` (execs the leg's own text).
- selftest: E368 9/9 (fixtures prove `build(files=[])` really bypasses the walk -- r1261 family),
  E350 23/23.
- `e368 verify`: `problems=[]`.

## Not run this window

Full smoke suite (~35 min), the S6 maintenance chain (dualrun/compute_audit/py_watermark),
lane collectors, `update_*`, paper/scorecard faces. GPU untouched (parked, C-20261014-01).
Cloud untouched. Nothing deleted, no quarantine action.

## Next

E369: take one pin at the *publishing* commit of the face it serves and re-run E368's comparison --
the only way to tell a stable number from a pinned one.