# DIGEST r1610 (bm-b, 2026-11-09): E581 — the money ticket prints a price for a bar it did not price on

**Face**: `results/etf_book_order/BREADTHAUDIT-2026-11-06.json`
**Instrument**: `scripts/etf_book_ticket_audit.py` (selftest 19/19)
**Code fix**: `scripts/etf_book_order.py` now publishes `pricing_bar`,
`pricing_bar_is_the_priced_bar`, `pricing_drift_vs_priced_bar` + a printed warning line
(module selftest 42/42, ticket regenerated in-window).

## What was measured

r1609 added `panel_breadth` — the third freshness face on the ticket — going forward. This
round asked the backward question: **can the already-published tickets be executed at the
bar they name?**

Six tickets under `results/etf_book_order/`. Zero are priced on the bar they name.

| ticket | named bar | prices from | trading bars earlier | weighted price drift |
|---|---|---|---|---|
| TICKET-2026-10-23 | 2026-10-23 | 2026-10-14 | 7 | +5.10% |
| TICKET-2026-10-26 | 2026-10-26 | 2026-10-14 | 8 | +5.18% |
| TICKET-2026-10-27 | 2026-10-27 | 2026-10-14 | 9 | +4.68% |
| TICKET-2026-10-28 | 2026-10-28 | 2026-10-14 | 10 | +2.65% |
| TICKET-2026-11-06 | 2026-11-06 | 2026-10-14 | 17 | +6.43% |
| TICKET-2026-10-28-card | 2026-10-28 | — (1 leg matches no bar) | — | +44.3% |

Root cause, in code: `build_ticket(score.loc[dec_bar], close.loc[dec_bar], ...)` (line 529)
prices the order on the **decision** bar while `evidence_cutoff`, `feed_status.ticket_bar`
and `panel_breadth.priced_bar` all name the **newest** bar. The card ticket's
`513100 @ 11.8419` is 2.17× the highest close that symbol ever printed (5.448 on
2021-11-22), i.e. a different class — a price that exists in no bar at all.

Breadth was never the binding constraint: 1,672–1,675 of 1,677 panel symbols printed on
every one of those bars (>99.6%, gate 0.50). So `feed: current`, `breadth: OK` and
`staleness: 0/415 picks` were all green at once while the printed order was 2.6–6.4% off
the price level it named.

## Three instruments, and they agree

The audit matches each printed price against the symbol's whole bar history, then
intersects the candidate bars across all off-bar names — a single name's candidate set is
useless (513100's 2.399 also occurred on 2018-12-11), the intersection is not. After the
in-window fix, the ticket's own `pricing_drift_vs_priced_bar` (0.064251) and the audit's
independently measured drift (0.064251) agree exactly.

## Pitfalls paid for in this round

1. **A filename is not a ticker.** `data/daily` mixes bare (`159901.csv`) and
   exchange-prefixed (`sz159501.csv`, `sh513690.csv`) spellings; keying on the filename
   first reported all six tickets' holdings as `not_in_panel`.
2. **"This price occurred somewhere" is not provenance.** Taking the latest matching bar
   per name produced `2026-11-04` for the 11-06 ticket; the shared-bar intersection
   produced the true `2026-10-14`.
3. **A price matching no bar is its own class**, not a large disagreement.

## Caveat

Breadth is measured on today's tree and the panel only grew (r1609 appended 8,514 rows), so
a historical breadth reading is an upper bound — it can excuse a ticket but not convict it.
The held-name and price checks carry no such weakness.