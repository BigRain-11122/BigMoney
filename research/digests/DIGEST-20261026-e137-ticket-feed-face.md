# DIGEST 2026-10-26 — E137 — the order sheet could not say its own bar was old

**Round:** r1287 (bm-c) · **Product:** `scripts/exchange_calendar_audit.py`
(`ticket_feed_status` / `live_ticket_feed_status`), consumed by
`scripts/etf_book_order.py` and `scripts/etf_book_production.py`

## The gap

r1286 built the official exchange calendar and an audit that says whether the *panel*
is current (`in_sync` / `source_lag` / `panel_gap`). Nothing about the artefacts a
human acts on changed. Both of them carried a staleness leg already, and it was
useless for this question:

```
staleness: 0/415 picks (0.0%) priced before the decision bar | panel live on last bar 1496/1498 | worst gap 0d
feed:        stale_feed | ticket bar 2026-10-23 vs official 2026-10-26 | lag 1 day(s)
```

Both lines are from the same run of `etf_book_order.py run`. `staleness_stats` counts
symbols that are stale **inside** the panel, so a panel that is uniformly days old
scores a spotless 0/415 and reads exactly like a fresh one. The ticket therefore had
no way to tell its reader that it was priced on a bar the market had already moved past.

## What was added

`CA.ticket_feed_status(calendar_days, ticket_bar, expected_bar, verdict)` — a pure
function, plus `CA.live_ticket_feed_status()` which feeds it the on-disk calendar and
the live panel tails. One implementation, two consumers (no second copy in the boot).

| status | when | reads as |
|---|---|---|
| `current` | lag 0 | priced on the newest official bar that must exist |
| `stale_feed` | lag ≥ 1, verdict ≠ panel_gap | the signal is that many official days old |
| `feed_broken` | verdict = panel_gap | an older official day never arrived — a stopped feed, not a delay |
| `unknown` | no calendar, or the audit threw | explicitly *not* fresh |

Boundary rules, each pinned by a selftest leg:

* **lag counts official days only** — Fri 10-23 → Mon 10-26 is 1, not 3 (leg21);
* **`feed_broken` outranks the plain lag** (leg22) — a stop is worse than a delay;
* **`unknown` never reads as `current`** (leg23) — a missing calendar must not be
  mistaken for a clean face;
* **the warning reaches the one-page face**, not just the JSON (leg24) — the md a
  human opens carries the `⚠` line.

## Where it now shows up

`results/etf_book_order/TICKET-<asof>.json` and `ORDER-<asof>.md` carry a
`数据新鲜度` block; `results/etf_book_production/latest.json` and `CARD.md` carry
`feed_status` plus, when stale, a leading caveat:

> FEED IS BEHIND: this card is priced on the 2026-10-23 bar, 1 official trading
> day(s) short of the 2026-10-26 bar the market has already published. The names
> are that old, not a fresh call.

First live reading (2026-10-26, 17:52, both surfaces): `stale_feed`, lag 1 —
sina had not published the 2026-10-26 bar at 17:33 either, so this is the feed,
not the book.

## Selftests

`etf_book_order.py --selftest` **24/24** (was 19/19; legs 20-24 new),
`etf_book_production.py --selftest` OK, `exchange_calendar_audit.py selftest` 9/9.

## Next

The forward mark still waits on the 2026-10-26 bar (`data_lag_audit` verdict
`source_lag`). When the audit flips to `in_sync` the ledger accrues and the same
run will print `feed: current` — the two lines now agree by construction.