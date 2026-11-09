# DIGEST r1495 (bm-c) — a zero-append run cannot be a success claim

**Window** 2026-11-10 05:33–06:0x · machine bm-c · dept: 数据

## What was wrong

`data/minute_feed` held no bar at all for **2026-11-09**, a trading day. The last successful
write was 2026-11-08 07:52; nothing landed after it. The writer's success path printed the same
sentence for "no new bars today" and for "yesterday never ran":

```
update_minute_feed: done, +0 rows across 5 symbols (kind=gated)
```

The only face that noticed was the fleet board the next day (`behind_1d` on minute_feed). The
sina 1m window is ~8 sessions deep, so this is not a cosmetic gap: every missed session costs
5 × 238 bars and slides out of reach within days (`loss_mode` = a minute bar outside the rolling
window is gone).

## What changed

1. **The lane was healed while the window still covers the day.** `--force` appended
   **1,190 bars** (238 × 5 symbols); every archive now ends `2026-11-09 15:00`. A second forced
   run appended 0 and printed the new coverage line — the exact pair of runs that used to be
   indistinguishable.
2. **`_session_coverage()` in `scripts/update_minute_feed.py`** answers the question the row count
   cannot: which completed session does each archive's tail reach? It reads the local ETF calendar,
   refuses to demand today's session before `settle_t=15:30` (E136 lesson), and names missing
   sessions per symbol. The run prints `COVERAGE HOLE -- last completed session <d>, k/n archives
   reach it (missing: …)` or `coverage ok -- all n archives reach <d>`, and the status face carries
   the block under `coverage` (tail day per symbol, holes, law sentence).
3. **A smoke leg re-derives it from the archives on disk** ("a lane that appended nothing still says
   whether it reaches the last session"). It compares the published `tail_day_by_symbol` against the
   CSV tails, then recomputes the holes with the writer's own predicate and today's calendar — so the
   block cannot become decorative, and a status that lags the archives is called stale instead of
   being trusted.

## Verification

- `python scripts/update_minute_feed.py selftest` → **ALL PASS** (4 new legs: holes named per symbol,
  clean case, pre-settle day not demanded, empty calendar = unknown not a hole).
- Live: append run `+1190 rows`, then zero-append run `coverage ok -- all 5 archives reach 2026-11-09`.
- `results/minute_feed_status.json` carries `coverage` with `symbols_covering=5/5`.
- Board rebuilt: minute_feed `behind_1d` → `in_sync`; board now reads 11 in_sync / 1 behind_1d (lhb)
  / 1 absent (lhb_inst) / 1 unverifiable (marks) / 1 retired (options).
- `py_compile` clean on both edited files. Full smoke: **not claimed green in this window** — see the
  round report; the r1493 suite's two reds both re-derive green on this tree (all five certified
  panels are `current` at 11-09).

## Second product: a lane the board could only call `absent`

The board listed `lhb_inst` as **absent** (`missing_artifact: results/lhb_inst_update_status.json`).
Two separate things were wrong, and only one of them was about data:

1. **The panel and its status face were machine-local and untracked** (`data/lhb_inst/` and
   `results/lhb_inst_update_status.json` both `??`). A lane whose only published face is a file no one
   commits is a lane the fleet cannot verify, however full its disk copy is — the 58,636-row panel
   had been sitting there since 11-06 while the board printed `absent`.
2. **The writer could hang forever.** The first invocation printed nothing for five minutes and had to
   be cancelled. `fetch_page` called `ak.stock_lhb_jgmmtj_em(...)` with **no timeout**: requests has
   none by default, so one stuck eastmoney page is an unbounded wait inside a chain leg. Ported the
   r806 bounded-fetch jacket (`bounded_requests()`: `Session.request` gets `timeout=45` unless the
   caller set one) plus a `fetching <start>..<end>` line before each page, and two selftest legs
   (default gets a bound / an explicit timeout survives). Selftest 11 → **13 checks, 0 failed**.

Then the lane ran end to end: **82 monthly pages, 0 mismatches, 58,671 rows, 5,155 codes, cutoff
2026-11-09**, and wrote the status face. Board: `absent` → `in_sync` (12 in_sync / 1 behind_1d lhb /
1 unverifiable marks / 1 retired options). The consumers re-derived unchanged verdicts
(`zoo94` REFUSE excess +0.40pp/yr p=0.055; `zoo99` ADMIT_TO_PREREG p=0.50%, 81 cohorts, 51,462
stock-days) — the new bar moved coverage, not the finding, and that is what a healthy lane should do.

## Next

- `lhb_inst` now has a producer and a committed face; the remaining decision is whether the 3.9 MB
  parquet belongs in git (it does today) or should move to the data-plane channel in TRANSFER.md.