# What each vehicle pays at a given account size

`scripts/capital_placement.py` -> `results/capital_placement.json` (read-only consumer of three published faces; it measures nothing itself)

The book, the four-ETF basket and the futures sleeve were each measured in their own window and cost model. This face puts them on the only axis an allocator holds: how much money you are trying to place. Profit is CNY **per year**, capacity ceiling applied where one exists, and the undeployable remainder priced at the net repo rate (1.777%/yr).

| capital | ETF book (card config, size-free) | ETF book (ticket, size applied) | 4-ETF basket | futures sleeve | best | basket vs card | card vs ticket | ticket vs size | size vs effective |
|---|---|---|---|---|---|---|---|---|---|
| CNY 300,000 | CNY 28,800 | CNY 39,810 | CNY 29,700 | floor not met (repo only CNY 5,331) | etf_book | +0.30pp/yr | -3.67pp/yr | +0.00pp/yr | -0.00pp/yr |
| CNY 1,000,000 | CNY 96,000 | CNY 132,700 | CNY 99,000 | floor not met (repo only CNY 17,770) | etf_book | +0.30pp/yr | -3.67pp/yr | +0.00pp/yr | -0.00pp/yr |
| CNY 1,500,000 | CNY 144,000 | CNY 190,785 | CNY 148,500 | floor not met (repo only CNY 26,655) | etf_book | +0.30pp/yr | -3.67pp/yr | +0.55pp/yr | -0.00pp/yr |
| CNY 3,000,000 | CNY 288,000 | CNY 220,274 (capped at CNY 1,526,694) | CNY 297,000 | floor not met (repo only CNY 53,310) | four_etf_basket | +0.30pp/yr | -3.67pp/yr | +0.56pp/yr | +5.37pp/yr |
| CNY 8,000,000 | CNY 768,000 | CNY 309,124 (capped at CNY 1,526,694) | CNY 792,000 | floor not met (repo only CNY 142,160) | four_etf_basket | +0.30pp/yr | -3.67pp/yr | +0.56pp/yr | +8.85pp/yr |
| CNY 50,000,000 | CNY 4,800,000 | CNY 1,055,464 (capped at CNY 1,526,694) | CNY 4,950,000 | CNY 650,000 | four_etf_basket | +0.30pp/yr | -3.67pp/yr | +0.56pp/yr | +10.60pp/yr |

Four columns, four different statements, and they add up exactly to the gap in the table above (a selftest leg enforces the sum). **basket vs card**: the basket beats the card's own configuration, size-free -- the book loses that one on its own terms. **card vs ticket**: the card headline is not the rule the order sheet executes; this is that distance, measured knob by knob in `research/ETF_BOOK_CAGR_RECONCILE.md`. **ticket vs size**: impact only, taken from the capacity ladder's own delta rather than from its absolute levels (which are priced on a different universe). **size vs effective**: the part of the account that cannot be deployed and earns repo.

## How to read it

* Every number is read from a published face, not re-measured: book card headline 9.60%/yr (results/etf_book_spanning.json), book level as traded 13.27%/yr (the executable ticket, results/etf_book_cagr_reconcile.json), basket 9.90%/yr (results/etf_book_spanning.json), sleeve lot arm (results/futures_sleeve_economics.json).
* Risk is not free: the ticket carries ~13.5% vol and a ~-16% max drawdown against the card's 10.2% / -11.8% -- it earns more because it takes more, Sharpe 1.04 vs 0.99.
* The card headline and the executable ticket are DIFFERENT books: the card prints a 12-name 8%-vol-target run, the order sheet trades 5 names with a 0.20 beta cover at 8bp. The distance between them (+3.7pp/yr on the same stack) is decomposed knob by knob in research/ETF_BOOK_CAGR_RECONCILE.md, including the -1.25pp width x rule interaction.
* The capacity face's absolute levels (7.2-7.4%/yr) are priced on a different universe (un-repaired panel, no class filter) and run ~5.5pp/yr below the production stack at identical settings; only its impact DELTA is used here, never its levels.
* Impact is priced at the DEPLOYED size, so an account above the ceiling pays the ceiling's impact, not the ladder's 50M rung; below the first rung (1M) impact is zero and the size-free ticket is used.
* The book's ceiling is a p90-of-ADV statement: half of its decisions trade less than that, so the ceiling is a tail constraint, not an average.
* The basket has no modelled capacity ceiling. It is bought once and held, so liquidity binds only on the entry print; that print is not measured here.
* The futures sleeve pays nothing usable below its one-lot floor and stays under 2%/yr until roughly the 10M tier -- the continuous-weight series is not a tradable claim.
* Cash remainder is priced at the NET repo rate 1.777%/yr (gross quote minus roll commission), not at zero and not at the gross quote.
* All three vehicles were measured on 2020-2026 panels; the book's own pre-2020 test says the rotation premium there is a fraction of the boom-window figure.
* The basket is not a neutral benchmark either: over this window it is carried by Nasdaq-100 QDII (20.7%/yr) and gold (13.3%/yr) with CSI300 at 0.2%. Its 10.09% is a window statement about a mix chosen in that window -- the point of the column is that the BOOK does not beat it, not that the basket keeps paying.
