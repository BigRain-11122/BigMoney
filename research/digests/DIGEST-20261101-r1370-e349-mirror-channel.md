# DIGEST 2026-11-01 r1370 -- E349: what a mirror actually decides

**Card:** E349 · **Study:** `scripts/e349_latest_mirror_census.py` (selftest 15/15, verify 0
problems) · **Face:** `results/state_tilt/MIRROR-2026-11-01.json` + `mirror_latest.json`
**Pool card burned:** `E349-WHAT-THE-LATEST-MIRROR-DECIDES`

## The question E347 left open

E347 measured 191 dated faces and found that none of them gates an operational decision. It did
not conclude "nothing decides" -- it published the bound: the readers it expects live on another
channel, namely the `*_latest.json` mirrors and the live state files a round rewrites in place.
A dated face is a citation of a moment; a mirror is a pointer that resolves to whatever is on
disk when it is opened. So the question a dated face cannot answer is the one a mirror must.

## Readings (pinned corpus, 2412 source files, 1109 carrying a channel token)

| reading | value |
| --- | --- |
| channel files (128 mirrors + 11 live-state) | 139 |
| reached by an in-repo `.py` source | 122 (87.8%) |
| reach a non-fixture comparison | 63 (45.3%) |
| carry a **freshness** comparison | 8 (5.8%) |
| comparisons outside fixtures | 840 |
| of which freshness | 14 (1.67%) |
| operational comparisons | 235 |
| of which freshness | **2** |
| chain-wired sources that read the channel | 2 of 119 |
| chain-wired operational comparisons that test freshness | **0 of 2** |
| write-only to Python | 17 |
| never named by any in-repo file at all | 13 |
| named by a non-Python operational file | 10 (7 state, 3 mirror) |

## Verdict

> the mirror channel is opened by operational branches and almost never asks whether what it
> opened is current

Two thirds of the mirror population is *reached* (122/139) and nearly half of it *decides*
something (63/139), but the one comparison a mirror alone can carry -- "is this pointer still
current?" -- appears in 14 of 840 non-fixture comparisons and in 2 of 235 operational ones. The
only two chain-wired readers in the repo (`scripts/compute_audit.py` and `smoke_test.py`) open
the channel through a directory sweep and never compare a date to a fresh clock.

## Pitfalls found while building it

1. **A sweep is not N readers.** `for p in glob(results/*.json)` reaches every mirror at once.
   The first build attributed that one comparison to each of the 50 files the sweep admitted and
   reported 147 "gates" for a single probe script (`Tools/_r698bmc_s3_probe.py`). Attribution now
   belongs to `<sweep pattern>`, and per-file rows only count named loads. The headline moved from
   2039 comparisons / 269 operational to 1070 / 235.
2. **`parents_of(tree)` inside `gate_rows` is recomputed per load binding.** 697 bindings over
   1109 sources took 212s; memoising the identical function per tree object brought it to 134s.
   Same answer, fewer walks.
3. **A population prefilter must be published.** 1303 of 2412 sources mention no channel token and
   are skipped by a text test -- `prefiltered_out` is in the face so the denominator cannot
   silently shrink (E332's rule).
4. **The live-state half of the channel is read by nothing in Python.** `watermark_red.json`,
   `idle_trigger.<id>.json` and `autofill_state.<id>.json` are written every round and opened by
   no `.py` file. Rather than publish "nobody reads it", the census counts `.ps1/.cmd/.txt/.js`
   citations: 10 channel files are named there, so the honest statement is *the readers are
   outside the parsed corpus*, and 13 files are named nowhere at all.
5. **The chain cut changes the verdict.** Historical closeout scripts (`Tools/_r1029bmc_close.py`
   and 20 siblings) assert on `heartbeat_epoch_utc` and were classified operational. They ran
   once. Cutting by "the source is named inside `Tools/s6_chain_bmb.py`" leaves 2 readers and 0
   freshness checks -- which is the claim worth making, and the population number is still
   published beside it.

## Bound

The corpus is the in-repo `.py` tree at the face's pin; a consumer outside it (the loop prompt,
the scheduled-task wrappers, dashboard JavaScript, the browser) is counted as a citation only.
`results/` is excluded because it holds the artifacts this census would be reading the output of.