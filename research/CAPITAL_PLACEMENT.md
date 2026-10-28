# What each vehicle pays at a given account size

`scripts/capital_placement.py` -> `results/capital_placement.json` (read-only consumer of three published faces; it measures nothing itself)

The book, the four-ETF basket and the futures sleeve were each measured in their own window and cost model. This face puts them on the only axis an allocator holds: how much money you are trying to place. Profit is CNY **per year**, capacity ceiling applied where one exists, and the undeployable remainder priced at the net repo rate (1.777%/yr).

| capital | ETF book (rule, size-free) | ETF book (achievable at 1% ADV) | 4-ETF basket | futures sleeve | best | rule gap | run diff | capacity cost |
|---|---|---|---|---|---|---|---|---|
| CNY 300,000 | CNY 28,860 | CNY 21,840 | CNY 30,270 | floor not met (repo only CNY 5,331) | four_etf_basket | +0.47pp/yr | +2.34pp/yr | +0.00pp/yr |
| CNY 1,000,000 | CNY 96,200 | CNY 72,800 | CNY 100,900 | floor not met (repo only CNY 17,770) | four_etf_basket | +0.47pp/yr | +2.34pp/yr | +0.00pp/yr |
| CNY 1,500,000 | CNY 144,300 | CNY 109,200 | CNY 151,350 | floor not met (repo only CNY 26,655) | four_etf_basket | +0.47pp/yr | +2.34pp/yr | +0.00pp/yr |
| CNY 3,000,000 | CNY 288,600 | CNY 137,324 (capped at CNY 1,526,694) | CNY 302,700 | floor not met (repo only CNY 53,310) | four_etf_basket | +0.47pp/yr | +2.34pp/yr | +2.70pp/yr |
| CNY 8,000,000 | CNY 769,600 | CNY 226,174 (capped at CNY 1,526,694) | CNY 807,200 | floor not met (repo only CNY 142,160) | four_etf_basket | +0.47pp/yr | +2.34pp/yr | +4.45pp/yr |
| CNY 50,000,000 | CNY 4,810,000 | CNY 972,514 (capped at CNY 1,526,694) | CNY 5,045,000 | CNY 650,000 | four_etf_basket | +0.47pp/yr | +2.34pp/yr | +5.33pp/yr |

Three columns, three different statements, and they add up exactly to the gap in the table above (a selftest leg enforces the sum). The **rule gap** is the book's ranking versus the basket with size taken out of the picture -- the basket wins that one already. The **run diff** is not a finding: the capacity face's return does not reproduce the spanning face's headline by ~2.3pp even under the ceiling, and this window does not separate that difference (cost model vs cell definition), so it is published as unattributed instead of being charged to the ceiling. The **capacity cost** is the 1%-of-ADV ceiling alone: zero while the book is under it, and it widens with size.

## How to read it

* Every number is read from a published face, not re-measured: book 9.62%/yr (results/etf_book_spanning.json), basket 10.09%/yr (results/etf_book_spanning.json), sleeve lot arm (results/futures_sleeve_economics.json).
* The book's ceiling is a p90-of-ADV statement: half of its decisions trade less than that, so the ceiling is a tail constraint, not an average.
* The basket has no modelled capacity ceiling. It is bought once and held, so liquidity binds only on the entry print; that print is not measured here.
* The futures sleeve pays nothing usable below its one-lot floor and stays under 2%/yr until roughly the 10M tier -- the continuous-weight series is not a tradable claim.
* Cash remainder is priced at the NET repo rate 1.777%/yr (gross quote minus roll commission), not at zero and not at the gross quote.
* All three vehicles were measured on 2020-2026 panels; the book's own pre-2020 test says the rotation premium there is a fraction of the boom-window figure.
* The basket is not a neutral benchmark either: over this window it is carried by Nasdaq-100 QDII (20.7%/yr) and gold (13.3%/yr) with CSI300 at 0.2%. Its 10.09% is a window statement about a mix chosen in that window -- the point of the column is that the BOOK does not beat it, not that the basket keeps paying.
