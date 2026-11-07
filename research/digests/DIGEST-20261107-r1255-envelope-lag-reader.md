# DIGEST 2026-11-07 r1255 (bm-a) — the envelope is a report, the panel is the measurement

## What the board said before this round

`data_lane_freshness` judged every status-kind lane on the date written inside its
status envelope. An envelope is a committed derived face, so a rebase / autostash /
checkout can restore an older copy of it while the panel on disk keeps advancing —
and nothing re-pushes the envelope because the writer's own no-op path had already
run. Live case (2026-11-07, carded at r1254): `futures` read `stalled` (tail
2026-11-02, missing 4) while `data/futures_daily/*.csv` held 2026-11-06 and
`update_futures` itself had just reported a zero-network no-op covering 11-06.

That is not bad data — it is a reader and a writer reading two different objects.

## What this round landed

`scripts/data_lane_freshness.py`:

- `panel_tail_csv(dir, pattern)` — newest `YYYY-MM-DD` first column across a CSV
  panel, last 4 KB of at most 40 files, no network.
- status specs may declare `panel_csv`; `futures` (`data/futures_daily`) and
  `repo` (`data/repo_daily`) do.
- when the host can read the panel and it holds a NEWER bar than the envelope:
  the panel becomes the tail the board judges on, and the row publishes
  `panel_tail` / `envelope_tail` / `envelope_stale` / `envelope_lag_until` /
  `envelope_lag_days` (calendar-counted, or `None` + `envelope_lag_beyond_calendar`
  when the panel runs past the official calendar — a silent 0 would be a lie).
- the opposite direction is NOT a licence: a panel that lags its envelope changes
  nothing (the envelope stays governing, `envelope_stale: false`), because a short
  panel must not heal a late lane.
- the markdown board gains an "Envelopes older than the panel they describe"
  section, so the two numbers travel to the human face instead of only into JSON.

Guards: selftest 16 → 18 legs (L17 older envelope cannot stall a lane holding
newer bars; L18 lagging panel cannot heal a lagging envelope), plus one smoke leg
(`fleet: a panel newer than its envelope is not a stall`) that re-derives the rule
from the PUBLISHED rows — no row may quote a tail older than the panel it also
publishes, and a stale envelope must publish both dates.

## Why this is the fix and not a band-aid

Re-running the puller would erase the symptom once. The envelope is a derived
face; derived faces are what git history rewrites hand back. As long as the reader
believes it unconditionally, the same false red returns after any rebase
(card E392 §正法 2 — the card existed, the reader was not wired).

## Honest state

The live board today shows `futures` `in_sync` at 2026-11-06 with envelope and
panel agreeing (the 10:12 no-op branch wrote the envelope), so the stale branch is
proven by fixtures rather than by production this hour. `moneyflow`, `repo`,
`marks`, `zt_pool`, `astock_daily`, `heat`, `etf_panel` remain `unverifiable`
(bm-b host silent) — unchanged by this round and not masked by it.