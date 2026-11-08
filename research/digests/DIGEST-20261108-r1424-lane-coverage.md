# DIGEST-20261108-r1424 — the freshness board was blind to the lane map

Group D-20261108-14 (12:00 batch, OB-20261108-120628-589) handed BigMoney two legs.
This round executed both.

## What was wrong

`config/lane_hosts.json` declared nine lanes owned by a machine whose heartbeat was
194h old, and `scripts/data_lane_freshness.py` had no row for any of them. The board
therefore printed "all fresh" about lanes nobody was reading, and the two states
"this lane produces nothing" and "nobody is looking at this lane" were the same blank.

## What changed

* `board_lanes()` = LANES ∪ every writer the map declares. A map writer with no reader
  becomes a row with `verdict=unmeasured` — never `absent`, never dropped.
* Rolling-window lanes (`window_trading_days`) are judged by their own window, and the
  gap still travels as `days_behind`; `worst` can no longer be a lane that is inside
  its contract.
* Silence is its own alarm: `HOST_SILENT_H = 24h` beside the 2h certification line,
  `hosts_silent` / `silence_verdict` / its own md section. A lane can be `in_sync`
  while its owner has been gone for 215h — that now prints as two facts.

## Live readings (2026-11-08 12:4x bm-c)

15 rows (11 registry + 4 map-only: ah_panel, minute_feed, sina_mf, ths_panel),
13 in_sync / 1 retired (options) / 1 unverifiable (marks), worst=marks.
`sina_mf` reads in_sync with `days_behind=9` inside its 20-trading-day window.
`hosts_silent=["bm-b"]` (215.6h, owns marks + the lanes the 10-21 redline already
moved off it). `coverage.declared_writers=12`, all 12 have a row once `period_lanes`
(fund_statements) is counted with `lanes`.

## Second leg

`fleet/backlog.md` gained rows 19-22 for the four compute cards the group named
(B-CITY3D-01/02, B-XIDUDU-01/02), definitions copied from
`compute/BigCompute/docs/ops/batch-pool-stock-v1.jsonl`, with the honest execution
face (they ignite inside the BigCompute pool, and B-CITY3D's gate is CLOSED at
vram_free=1407MiB rather than being a card defect).

## Self-catch

The first coverage leg failed on `update_fund_statements` because the board has two
sections (`lanes` and `period_lanes`) and I counted only one. A verdict about coverage
must be read off both, or it calls a covered lane missing.

Card: knowledge/METHODOLOGY_ASSETS.md E430.
