# DIGEST 2026-11-01 r1358 (bm-b) -- E338: the census green window is a duration, and the two-reading split is vacuous

**Card:** E338 · **Face:** `results/state_tilt/GREENWINDOW-2026-11-01.json` · **Script:** `scripts/e338_census_green_window.py`

## The question

E337 showed that executing the opt-in cost 0 of 21 numbers and that every number a reader would have billed to it
was the **corpus**. That is a statement about the population every census face reads — `e326.corpus()`, every
`.py` under scripts/Tools/live/monitor/firm, read off the disk. E338's card asked two things: measure how long a
green window actually lasts, and price a commit-pinned population.

## What was measured

Sixteen census faces (e322…e337). For each: the commit that first added it (`git log --diff-filter=A`), then the
next commit touching any `.py` in the five producing packages (2,284 such commits in this repository's history).

| reading | median window | min | max | inside one 600s round | open |
|---|---|---|---|---|---|
| all `.py` touches | 2,014 s (33.6 min) | 794 s | 6,286 s | 0 of 15 | 1 (e337) |
| touches outside the census family | 2,014 s | 794 s | 6,286 s | 0 of 15 | 1 |

The two readings are **identical on 15 of 15 closed windows** — same closing commit every time.

## Why the split is vacuous

Every closing commit **adds the next census sibling** (15 of 15) and every one of those commits also modifies a
producer file — usually `Tools/s6_chain_bmb.py`, because landing a study wires its chain leg in the same commit.
So "research touched a file" and "production changed" are the same event, by construction of the workflow. The
design that was meant to separate them cannot: publishing two equal numbers would have implied corroboration, so
the face publishes `readings_coincide {compared: 15, same_closing_commit: 15}` and the verdict says the split
measures nothing.

The consequence is worth stating plainly: a census face's green window is **the research cadence**, not a property
of the analysis. It ends when the next study lands, whether or not anything it reads changed.

## Pinning, priced on three axes

| axis | measurement |
|---|---|
| size | pinned (oldest census landing): 2,205 files / 42.3 MB · today's disk: 2,301 files / 43.1 MB |
| read time | `git cat-file --batch` over the pin: 0.42 s · disk read: 0.14 s |
| dependency | the pin is only reproducible while those blobs survive and git is available |

So pinning is cheap in CPU terms and expensive in a way CPU accounting does not see: it trades a disk read for an
object dependency. The verdict names that trade instead of claiming a win.

## Defects caught in this round

1. **`git log` is newest-first.** The first burn published `median 0.0s, 16/16 closed` — every window computed
   `older - newer` clamped at zero. Fixed by reversing, plus `is_ascending()` fail-closed in `build()` and selftest
   legs L28–L30. A zero-defect-looking headline was the loudest possible symptom.
2. **A stopwatch in a deterministic face.** The first `verify` reported `pinned_read_seconds 0.4188 vs 0.4169` and
   nothing else. Timings moved into a `timings` block excluded from `_cmp`, with a leg (L36) that pins the
   exclusion.
3. **A fixture disagreeing with the frozen rule** (L15 expected `inside_one_round == 1` when both fixture windows
   are inside the round) — re-read the fixture, not silenced the assertion (E336 pit 3 family).

## Verification

- `selftest 36/36`.
- `run` → face + `greenwindow_latest.json`.
- `verify` → 0 problems (re-derives the whole face over git history, ~5.5 s).
- Smoke leg extracted verbatim and run standalone: PASS; doctored face (one window's seconds +7, coincidence zeroed)
  caught with two named problems and the published bytes restored identically.
- Chain leg `census_green_window` wired into `Tools/s6_chain_bmb.py`.

## Seeded next

`E341-WHAT-THE-SIBLING-CLOSER-ACTUALLY-CHANGED` — decompose each closing commit into census study / S6 wiring /
producer / unrelated, and price excluding the census family from its own corpus (which numbers would move, for
which faces).