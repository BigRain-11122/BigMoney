# zt pool: a day slice that was written before the tape settled (r2123, bm-c)

## Symptom

`scripts/update_zt_pool.py` had been exiting **3** since 2026-11-23 without
naming a difference:

```
OVERLAP MISMATCH zt 2026-11-23 - kept local, no write
```

so the four pool faces (涨停 / 炸板 / 跌停 / 强势) stopped two sessions short of
the book's bar, and the CEO one-pager said so in words:

> **? 读数陈旧**：读到的是 2026-11-23 的副本：最后采集日 2026-11-23，比应有最新 bar 日 2026-11-25 落后 2 个交易日（车道宿主 bm-c）——上面的数不是今天的盘面

## Evidence (results/_r2123bmc_zt_overlap_probe.py, read-only)

| face | stored 2026-11-23 | source now | verdict |
|---|---|---|---|
| zt | 143 rows | 146 rows | 3 added, 0 removed, 2 restated |
| zbgc | 24 | 24 | match |
| dtgc | 3 | 3 | match |
| strong | 56 | 56 | match |

zt detail:

* codes only local : (none) — nothing was deleted at the source
* codes only source: `001360` `002623` `600838` — three arrived late
* restated among the 143 shared: `000700` 10.0 → 9.992372, `603706` 10.139860 →
  9.981430

Zero removals, late additions, and two values still moving on shared names is
the signature of a slice written **before the close settled**, not a restatement
of a settled day.

## Ruling

`data/zt_pool/amendments.json` (append-only) — `LATE_COMPLETION_SUPERSET`:
replace exactly that one (day, face) slice with the source's settled rows, keep
every other day untouched, record why. The collector's own docstring names this
door ("benign-completion amendment = a later round with evidence, not a silent
accept").

The amendment script refuses (rc 3, no write) when the stored slice is no longer
the one the probe examined (`rows != 143` or `added != {001360,002623,600838}`),
so it can never quietly cover a later, different edit.

## A slice rewrite that loses rows is worse than the bug it fixes

First attempt was wrong and is recorded rather than hidden: `fetch_day()` returns
the source frame **without** the day column, and the collector stamps `日期`
itself. Reindexing onto the panel's columns therefore produced 146 rows with a
**NaN day**, and the 11-23 slice's 143 rows were gone (panel 1894 → 1897 rows,
33 → 32 days). Caught by re-reading the file, restored with
`git checkout HEAD -- data/zt_pool/zt.parquet`, then three fixes:

1. stamp `new_day["日期"] = FLAT` (panel convention: `YYYYMMDD`, no dashes);
2. zero-pad `代码` to 6 characters (R58 row-shell defence — an unpadded code is
   a different row to every reader);
3. assert `len(merged) == len(old) - len(old_day) + len(new_day)` **before**
   writing, and refuse otherwise.

## Verification

* `stored=146 refetched=146 match=True value-diff codes=0` for zt (re-run of the
  probe after the amendment); the other three faces already matched.
* panel integrity: 1897 rows, 33 days, day values uniform `YYYYMMDD`
  (`first 20261008 / last 20261123`), 146 rows on 2026-11-23
  (results/_r2123bmc_zt_inspect.py).
* ledger `data/zt_pool/collected_days.json` still reads 2026-11-23 for all four
  faces — the collection pass itself has not run yet.

## What still has to happen (and when)

The collector's 30-minute attempt throttle was spent by the refusing attempt at
**08:57:58**, so the next pass cannot start before **≈09:28**. From then the
gate passes for all four faces and the pass should collect 2026-11-24 and
2026-11-25 (8 calls, ~2.5 s spacing). This round does not bypass the throttle:
the earlier attempt did reach the source, so the pressure counter is honest.
