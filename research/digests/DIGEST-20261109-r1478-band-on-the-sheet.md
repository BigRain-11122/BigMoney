# r1478 — the band reaches the sheet an operator actually opens

Face: `results/etf_book_order/TICKET-2026-11-06.json::size_band` · `results/etf_book_order/ORDER-2026-11-06.md`
Product: `scripts/etf_book_order.py` (selftest 120/120 · legs 51n..51s) · card E486
Prereq: `results/etf_book_sizing_prereg.json` (r1477) · smoke leg r1478

## What the round asked

r1477 pinned the sizing band to the ruler's own noise (±10.43pp, warn at 2 sd) and left the
wiring for this round: the ticket must print `BAND_EXCEEDED` when k sits outside the band,
attach the list of faces a re-issue receipt has to rerun, stay read-only in v1 (k unchanged),
and observe one real round of k against the band.

## Findings

**The sheet now carries the band.** A new section prints the band, the three numbers it was
decided from (signed k, freshly re-read k, the ticket's own k) and the two distances, then the
zone. On the live ticket (2026-11-06) all three read 0.393073 → `WITHIN_BAND`, drift +0.000pp,
ticket gap +0.000pp against inside 10.43 / warn 20.86.

**Two distances, because they answer two questions.** The fresh re-reading against the signed
floor asks whether the ruler still says the same thing (the panel advances every day, so a
re-read moves). The ticket's k against that same floor asks whether the sheet obeys it. The zone
is the *worse* of the two: a ticket that obeys an old floor while the ruler has walked away is
not "inside", and printing only the flattering number is how a drift hides.

**The re-issue list is derived, never hand-written.** A hand-kept list is r1108 one level up —
a list nobody maintains reads as "nothing depends on this". `floor_quoting_faces()` walks the
published results tree and names every JSON that carries the floor's value under a key naming it
(k / floor / permitted), tagging the issuers (`source`) apart from the consumers. Live: **13
faces carry k=0.393073, 11 of them consumers** — that is the blast radius of a re-issue, printed
with its count.

**v1 is advisory and says so.** The band never changes k (`production_effect: advisory in v1`);
the promise is printed on the sheet so a reader cannot mistake a warning for a resized order.

## Verification

- `scripts/etf_book_order.py --selftest` → **120/120** (51n inside / 51o no-default → "cannot
  answer" / 51p warn vs outside / 51q worst-of-two / 51r scanned list / 51s printed section).
- `scripts/etf_book_order.py run` → ticket rebuilt, `size band: WITHIN_BAND | drift +0.000 pp |
  ticket gap +0.000 pp`.
- Chain legs re-run in order (9/9 rc0): size_rulers, rebalance_permission, cut_order_gap,
  decision_line, permission_persistence, floor_ledger, swap_stack, positions_ledger,
  live_size_provenance.
- In-lane red closed: `etf_book_cut_order_gap.json` now carries `sizing_source` /
  `base_bar` / `as_of` / `k_rule_capped_by_floor` off the ticket, so the smoke leg that compares
  the two faces no longer reads a phantom drift (0.393073 rule-capped vs 0.392401 account).

## Still open

The band reproduces twice before it is allowed to change anything (that is the prereg's own
condition), and the foreign-lane smoke reds (moneyflow tail certification / fund_statements
statute / marks cause table / etf_panel+minute_feed double host) belong to other hosts.