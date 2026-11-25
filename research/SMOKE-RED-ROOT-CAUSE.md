# Red legs, grouped by the face that stopped answering

source: `logs/smoke_legs.json` @ 2026-11-24T20:12:28 | 765 legs, 34 red

**PERMISSION_UNREADABLE_BECAUSE_IDENTITY_BROKEN**

## where the red legs sit

| family | legs |
|---|---|
| book (ticket / sheet / page / sizing) | 29 |
| outside the book | 5 |

Outside the book:

- product: the discount subset sits on the ledger's own line (r1528)
- product: the paper book owns the book the card sells
- product: astock_resid_veto_layer (published cutoff still matches the panel frontier)
- product: futures TSMOM face is current, capped and not an order
- product: the live-quote section and the panel's own lane agree on tonight

## the upstream receipts, as they stand on disk

| face | verdict | why | generated |
|---|---|---|---|
| size_rulers | IDENTITY_BROKEN | ["ticket_k_reproduced"] | 2026-11-24T17:25:28+0800 |
| permission | UNREADABLE | {"baseline_published": "baseline k=0.460253452 does not equal the ticket's k=0.458463000: the circularity identity is broken, so no reading can be called independent"} | 2026-11-24T18:58:55+0800 |
| cut_order_gap | UNREADABLE | incomplete_receipts | 2026-11-24T18:59:00+0800 |

## what the page would say if the identity held

readable path readings give `permitted_k = 0.435003` (from `universe`); the size in force is `k=0.435003`, tolerance `0.005` -> **KEEP_ALLOWED**.

if the baseline identity held, this face would publish a size; today it publishes nothing.

## rebuild chain (writes shared faces -- run only when no other host is writing)

1. `python scripts/etf_book_size_rulers_decision.py run`
2. `python scripts/etf_book_rebalance_permission.py run`
3. `python scripts/etf_book_cut_order_gap.py run`
4. `python scripts/etf_book_order.py run`

then re-run the book legs and let the smoke list speak.

## what this does not claim

- 5 red legs sit outside the book family and this face says nothing about them
- a KeyError leg may carry a second cause (e.g. a missing cash field) -- being in the family is not proof of this root
- rebuilt legs are not verified here: the smoke legs must re-run for that
- the counterfactual is arithmetic on the published readings, not a permission

