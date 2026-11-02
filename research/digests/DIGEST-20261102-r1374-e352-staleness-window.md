# E352 -- what a reader of the channel actually sees, in commits and hours

Round r1374 (bm-b), absorbing the E352 study authored at 2026-11-02 03:33-04:12 by a window that
stopped before wiring. The producer and its face were on disk uncommitted; this window verified
them, wired them, and closed the round.

## The question, and why E349 left it open

E349 counted the channel: 139 live pointers (128 `*_latest.json` mirrors + 11 live state files),
840 comparisons outside fixtures, and **14 of those 840 ask whether what was read is current**.
That is a rate, not a cost. The cost is the window: between the last time a writer touched a file
and the boundary at which a reader opens it, how far behind is the copy the reader gets?

## Measurement

Clock = this line's own first-parent history, 240 commits (`e847e099` head, 70.38 hours). At each
commit (a round boundary) and for each deciding channel file, the copy a reader would take is the
blob as of that commit; the lag is `boundary - last write`, in commits and in hours.

Content is read from the **working tree**, never through `git show`/`git grep`: this clone is
`blob:none`, so any unmaterialised blob starts a lazy fetch and hangs the round (r1255 family). Only
`git log` / `ls-tree` metadata is asked of git. This is also the honest model of the reader: a
cross-machine consumer takes the committed copy.

## Readings

| | |
|---|---|
| deciding rows (E349's published table) | 60 |
| resolved / unmeasurable | 59 / 1 (`latest.json` -- 28 files share that basename) |
| files rewritten every round | **1** (`fleet/machines/bm-b.json`, 150 writes in 240 commits) |
| files lagging | **58** |
| median of file medians | **80 commits** (p90 111) |
| files carrying a stale fence | **54**, one boundary each, deepest fence 1 commit |
| worst | `state-bm-c.json`, p90 **216 commits / 59.3 h** |
| verdict | `stale_window_unmeasured` |

46 of the 59 files were touched **exactly once** in the 240-commit window. That is the mechanism
behind the headline: a `*_latest.json` mirror is written by the round that produced it and then
frozen, so "latest" is a snapshot of its own study, not a pointer kept current. The one file that
is fresh is the heartbeat -- the only channel file every round stages.

The stale fence is the sharper half: at 54 boundaries a gate's own source changed while the
artifact it reads was already older than that change. The fence is exactly one commit deep, which
is the correct reading rather than a small number -- the gate changed, the face it grades did not,
so the first run of the new code grades an old copy.

## Two checks that keep the headline honest

1. **Censored, not zero.** Four rows (`bm-a.json`, `bm-c.json`, `state-bm-a.json`,
   `state-bm-c.json`) are never touched on this line -- they are written by the other machines'
   lines. They are published as censored with a floor (median 121 = the window length), never as
   fresh. Defended rather than hidden: dropping all four moves the median of medians 80 -> 76 and
   the p90 111 -> 107, so the headline is not made of floors.
2. **The population is E349's table, which is itself truncated.** E349 published 60 of its 63
   deciding rows (79 rows held back by its own row cap). This study measures what E349 published
   and names the bound rather than re-deriving the population; the 3 unmeasured deciding files are
   a property of the upstream face, not of this one.

## What the round should do with it

The S6 leg (`staleness_window`, verify) re-derives the table, so this face cannot silently age.
The finding that matters for operations: only the heartbeat is refreshed every round; everything
else on the channel is a snapshot, and the repo carries hundreds of modified-but-uncommitted
faces at any moment, so the disk a writer sees and the channel a remote reader sees are two
different objects.

## The leg could not run, and that was the second finding

As absorbed, the study asked git per file (`git log -- <path>`, plus a `--diff-filter=A` walk for
every file absent at the window's first boundary). A path-limited `git log` diffs trees commit by
commit: each call took one to two minutes on this tree and the whole verify ran **~16 minutes** --
over the chain's own 900 s wall, so the leg reported `rc=99 timeout` and graded nothing. Fixed by
one unfiltered `git log --name-only -z` over the same 240 commits, parsed into the same
`{path: [boundary idx]}` map in one pass; the add index falls out as the file's own first touch
(all that `--diff-filter=A` was recomputing per file). **Verify: 16 min -> 2.4 s in the chain
runner, with `problems: []` against the unchanged published face** -- the numbers are byte-identical,
which is the proof the rewrite preserved the measurement rather than improving the answer. Two
selftest legs pin the parser (per-commit attribution, a path with a space surviving `-z`, and a path
outside any known commit not being attributed).

Also fixed before wiring: the window was anchored at `HEAD`, so the commit that publishes the face
would shift the window and turn the leg red the next round. It is now anchored at the face's own
`pin` (`first_parent_window(width, pin)`), i.e. the table is a function of the history it names.

## Wiring

- producer: `scripts/e352_staleness_window.py` (`run` / `verify` / `selftest 17/17`)
- faces: `results/state_tilt/STALEWIN-2026-11-02.json` + `stalewin_latest.json`
- chain: `Tools/s6_chain_bmb.py` leg `staleness_window`
- smoke: leg E352 in `smoke_test.py`, extracted verbatim by `scripts/run_e352_smoke_leg.py`
- card: `knowledge/METHODOLOGY_ASSETS.md` E352