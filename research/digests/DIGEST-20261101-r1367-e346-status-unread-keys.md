# DIGEST 2026-11-01 r1367 bm-b — E346 what a status writer writes that nobody reads

E343 discounted ten `st["key"] = value` stores from its bound-read count because they write
into the dict that was just loaded instead of reading the key back. That discount was about
the *reader* side. This study asks the other half: of everything the ten status-writing
producers file, who reads it at all, and does a wrong value change anyone's decision?

## Headline

**93 keys over 10 producers. 44 are read by nobody (47.3%), and only 8 rows in the whole
corpus reach a live code path that is neither the dashboard nor a one-off merge resolver.**

The class split alone would have said 30 of 93 are "read by someone". Splitting those 30 by
what kind of reader it is moves 22 of them out:

| tier | rows | what the reader does with the value |
|---|---|---|
| `no_reader` | 44 | nothing in the tree names the key |
| `self_fed_only` | 19 | only the writer's own next run reads it |
| `display_only` | 20 | only `monitor/build_status.py` reads it -- it is drawn, not decided |
| `merge_only` | 2 | only one-off `Tools/_r<N>*_merge|rebase|close` scripts read it, once, at a conflict |
| `live` | 8 | a live consumer that is neither of the above |

The inversion that matters: **17 state fields decide the writer's own next run, against 8
that inform anyone else's.** The status faces are mostly the writer talking to itself.

## The named operational row

`last_spawn_attempt` is a persisted throttle read straight off the status face and compared
to a module constant; nothing outside the writer reads it, so nothing can catch a wrong value.
Set it to "now" by hand and the refresh silently stops for 30 minutes.

It is not one row. The same field with the same bound (`MIN_SPAWN_S = 30 * 60 = 1800 s`)
exists in **four collectors** — `update_options`, `update_astock_daily`, `update_sina_mf`,
`update_moneyflow` — so the edit is available in each. `update_minute_feed.last_success_ts`
is the same shape at `THROTTLE_MIN = 20` minutes. Six rows carry a numeric bound; all six are
`carried`, i.e. the branch text never mentions the field, which is why a text-only reader
would call these fields unread by their own writer.

## Two measurement decisions worth carrying forward

1. **`30 * 60` is not a Constant node.** The first bound reader collected only
   `ast.Constant` module assignments and reported *zero* bounds, which would have read as
   "no status field gates anything numerically". Folding `BinOp`/`UnaryOp` over numeric
   operands found all six. A constant reader that cannot evaluate arithmetic measures the
   spelling of the constant, not the constant.
2. **A latch is not only a read inside a branch.** The lexical rule (read lexically inside
   `If`/`While`/`Assert`) found 14 latches. Adding the carried shape — value assigned from
   the key read, then carried through local expressions into a branch — found 17, and the
   three it added are the ones that matter most, because their branch text says nothing
   about the field. The published `bound.shape` records which rule fired.

## What this does not say

* `monitor/build_status.py` is in the producer list per the card, and it publishes no keys of
  this shape (`extraction_empty: true`, disclosed by name) — it is a consumer of 22 faces,
  not a writer of one.
* A `display_only` key is not useless: a human reads the dashboard. The claim is narrower and
  mechanical — nothing *branches* on it, so a wrong value survives until someone looks.
* The reader corpus is the in-repo tree (`scripts`, `monitor`, `Tools`, `firm`, `live`,
  `content`, plus `smoke_test.py`); an out-of-tree consumer would not be seen.

## Product

* `scripts/e346_status_writer_unread.py` — `build` / `verify` (0 problems) / `selftest` 22/22
* `results/state_tilt/UNREADSTATUS-2026-11-01.json` + `unreadstatus_latest.json`
* S6 leg `status_writer_unread` (verify, ~5 s, no builds)
* smoke leg E346 (registered in `smoke_test.py`; extracted verbatim and executed standalone:
  PASS — it went red on the first build because a carried latch carried no decision context,
  which is the defect this round fixed)
* `scripts/run_e346_smoke_leg.py` — the standalone extractor used to run that leg inside the
  round budget
* methodology card E346, pool `E346` closed with `result_ref`