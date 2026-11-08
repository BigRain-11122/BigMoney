# DIGEST 2026-11-09 r1621 bm-b — E586: no reader drops the bar, but the same fact is spelled three ways

**Round**: 1621 (bm-b). **Card**: E586, closed. **Face**: `results/state_tilt/TICKETREADERBAR.json`
(+ `TICKETREADERBAR-latest.json`).
**Script**: `scripts/e586_ticket_reader_bar.py` (selftest 27/27, check/verify `problems=[]`,
standalone smoke leg PASS and 1/1 red under `--doctor`, 1.3s). **S6 leg**: `ticket_reader_bar` (rc0).

## Question

E581/E582 fixed the ticket producer (it now stamps `pricing_bar` and `book_decided_at`), E583
repriced the sheets already on disk, and E585/E590/E591/E592 priced the cash leg against the repo
panel. Every one of those repairs the **source**. None of them asks the question a follower cares
about: does the page a follower reads print the ticket's money without saying which bar priced it?

## Reading

Readers — every module that addresses a ticket (a code literal naming `TICKET-`/`ORDER-2026`, a
literal naming `results/etf_book_order`, or an import of its producer):

| measure | n |
|---|---|
| modules addressing a ticket | **21** |
| … addressing by ticket literal / by family dir / by producer import | 12 / 20 / 1 |
| naming one of the ticket's 7 **strict money** fields (nav, book_amount, cash_amount, weights, k) | **9** |
| … of those, also naming a bar field | **9** |
| **silent readers** (money, no bar) | **0** |
| modules hitting only **generic** money names (`legs`, `weight`, `order`) | 3 — published, never deciding, because a name is a signature, not evidence |

Surfaces — every published file that names the newest ticket (bounded candidate set, published in
the face):

| measure | n |
|---|---|
| surfaces naming the ticket | 10 |
| carrying its money (field names or 471,225 / 528,774.5 rendered) | **6** |
| … of those, stating a bar | **6** |
| silent surfaces | **0** |
| witness dialect: `field_names` / `dated_field` / `prose_dates` (+4 surfaces carrying no money) | 8 / 1 / 1 |

The one heterodox spelling is the pointer face `results/etf_book_order/latest.json`: it carries
`k_now` and states the bar as **`as_of: 2026-11-06`**, never as `pricing_bar`. It is the face
`etf_book_ceo_page.py` follows (`TICKET_PTR`), so a consumer that joins on the field *name* learns
nothing from it; the page survives only because it falls back to `file`/`path`.

## What the first two builds got wrong (both kept in the round report)

1. **Broad money names manufacture readers.** The first build called `Tools/s6_chain_bmb.py` a
   ticket-money reader because it names `legs` — its own chain receipt key. Strict vs generic arms
   were split; 3 generic-only hits are published and excluded from the verdict.
2. **A name-only bar test manufactures silent surfaces.** It called `latest.json` silent (it says
   `as_of`) and called the CASH* research faces silent (they carry no money at all). Fixed by
   requiring money before silence, and by taking the bar from **a dated key's value** on JSON faces
   while keeping prose-dates for the human page.

Both directions of the same error (false positive and false negative) came from one habit: deciding
with a name instead of with a value and a shape.

## Verdict

No reader and no money-carrying surface prints a ticket's money without saying which bar priced it.
The residual issue is not silence but **dialect**: one fact (`the bar this money comes from`) is
spelled `pricing_bar`, `ticket_bar`, `evidence_cutoff`, `as_of`, and prose. Any consumer joining on
one spelling sees only part of the population.