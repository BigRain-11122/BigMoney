# DIGEST 2026-10-27 — E102: a panel cutoff is a maximum, not a coverage claim

Source: `results/astock_daily_update_status.json` (`panel` block, live read 05:10)
Runner: `scripts/update_astock_daily.py` (gate + refresh writer, selftest green)
Instrument: `smoke_test.py` leg *product: astock panel states its coverage, not just its date*
Trigger: `fleet/inbox/MSG-20261027-0400-bm-b-revosc-bridge-stale-4td.md` (bm-a)

## The misreading

bm-a reported that this machine's `rev_osc_live` SIG/BARS bridge was four trading days
behind the exchange calendar: latest bridge 2026-10-20, calendar 2026-10-26, downstream
SYSTEM-V1 book quoting a current-looking `equity_cny=990,156.71` at the older face. The
natural hypothesis — the consumer's gate is reading the wrong thing — was wrong in a more
interesting way.

## The numbers

`panel.cutoff` is `max(local last date)` over 5,223 `data/astock_daily/per/*.csv`. On a
panel mid-refresh that is a statement about **one file**:

| field | value |
|---|---|
| `panel.cutoff` (max tail) | 2026-10-26 |
| names actually at that date | 1,639 of 5,223 = **31.4%** |
| date at which 90% of names are covered | **2026-10-20** |
| tail histogram | 10-26: 1,639 · 10-21: 450 · 10-20: 3,128 · older: 6 |

The refresh had been running 7.5h (todo 5,223, fetched 5,220, 3 conn timeouts), writing
names in its own order. So the bridge at 2026-10-20 was **right** — 2026-10-20 was the
only date the panel could defend — and the face that was wrong was the collector's, which
published a currency it had not earned. A consumer reading `panel.cutoff` cannot tell
"the panel is current" from "one file is current".

## What was changed

1. `panel` now carries `coverage_pct`, `coverage_90`, `coverage_floor_pct` (90) and a
   6-row `dates_tail` histogram, plus `cutoff_is: "max tail across all per/*.csv — read
   coverage_pct/coverage_90 before calling the panel current"`. E136's >=90% rule
   (`exchange_calendar_audit`) is applied at the point where the ambiguity is born, not
   only in the downstream lag audit.
2. The "refresh in progress (lock alive)" branch of the gate used to set
   `mode` and nothing else, so a stale `no_op_reason` kept sitting beside a fresh
   `spawn_reason`. Worse, because `complete=false` drops `cutoff` inside `stale_gate`,
   the branch reported `no panel cutoff (first pull / empty panel)` on a 5,223-file
   panel — a factually false line, and the one that makes this look like a consumer bug.
   It now publishes the real state: `refresh in progress: panel incomplete at cutoff
   2026-10-26 (coverage 31.4%, 90% date 2026-10-20)` and clears the superseded line.
3. Four selftest legs pin the arithmetic: 50% on a two-name panel, 66.7% on three, the
   90% date must **not** equal the max date on a mixed panel, and an empty panel states
   nothing rather than 0%.

## Deliberately not changed

`rev_osc_signal_export`'s gate was left strict. Building a SIG day dated 2026-10-26 from
names whose last bar is 2026-10-20 would produce a mixed-date cross-section — a worse
defect than a book that lags and says so. The bridge will export the newer date by itself
once the refresh reaches coverage.

## The law

A face that publishes a MAX over a heterogeneous population has to publish the
population's shape beside it. Two dates in the same file (`cutoff` and `coverage_90`) is
the cheapest form of that; one date plus one percentage is enough to turn "current" from
an assertion into a measurement. Sibling of E136 (lag audit: read lag from the maintained
queue plus a >=90% coverage floor, never from `min` over all files) — the same trap at the
other end of the same panel, and the reason both ends must state coverage.