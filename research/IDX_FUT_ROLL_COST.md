# What a roll costs when you measure it

The roll book switches both legs at the same close, so the seam itself is free by construction. What is *not* free is crossing the spread twice on the way through. That charge has been `commission + one tick each leg` = **1.5bp per roll** -- an arithmetic composition of the fee and the minimum tick, not a measurement of anything anybody quoted.

This page measures it from the only tape the repo has: each contract's own daily high and low. Corwin-Schultz (2012) effective spread from daily high/low, 20-day rolling median, one-bar lag; imported from etf_book_cost_tape.cs_spread. Per roll the cost is half the incumbent's spread plus half the successor's plus the fee, priced at the roll date with the estimator's own one-bar lag.

Evidence cutoff: `2026-11-13`  ·  generated 2026-11-15T05:24:35

## §一 The measured cost of one roll (bp, per product)

| product | rolls | rolls/yr | p25 | **median** | mean | p75 | max | rolls at or under 1.5bp | unpriced |
|---|---|---|---|---|---|---|---|---|---|
| IF | 74 | 9.23 | 9.77 | **19.843** | 20.49 | 30.272 | 74.252 | 13.5% | 6 |
| IC | 63 | 7.86 | 17.66 | **30.792** | 32.16 | 44.554 | 83.529 | 7.9% | 6 |
| IH | 89 | 11.1 | 7.076 | **21.071** | 22.175 | 32.284 | 70.121 | 16.9% | 6 |
| IM | 23 | 5.38 | 11.342 | **28.232** | 31.441 | 43.59 | 100.46 | 4.3% | 0 |

The last two columns are the honesty of the estimate. `at or under 1.5bp` is the share of rolls whose range implies a spread no wider than the document floor -- a face that only printed the median would hide that the floor is met on a minority of rolls, and would also hide that the rest of the distribution is the estimator saturating rather than the market quoting. `unpriced` counts rolls where the cache could not price a leg; those are filled with that product's own median and the count is printed rather than the roll being dropped.

## §二 What the measured cost does to the carry

| product | discount gross | breakeven bp/roll | net @1.5bp (published) | net @measured median | net @measured p75 |
|---|---|---|---|---|---|
| IF | **3.567** | 6.14 | 3.43 | **1.74** | 0.77 |
| IC | **8.763** | 73.33 | 8.64 | **6.34** | 5.26 |
| IH | **2.392** | 0.0 | 2.23 | **0.05** | -1.19 |
| IM | **10.198** | 133.91 | 10.12 | **8.68** | 7.85 |

Admission line 3.0%/yr, the same one the basis pages use.

## §三 The verdict

| | products |
|---|---|
| admitted at the published floor | IC, IF, IM |
| admitted at the measured median | **IC, IM** |
| admitted at the measured 75th pct | IC, IM |
| below the line before any cost | IH |
| flips, published floor → measured | **IF** |

| | products |
|---|---|
| break-even **inside** the unmeasured cost band (no verdict) | **IF** |
| break-even above the whole band (admitted whatever the spread) | IC, IM |
| below the line whatever the spread (absent) | IH |

The cost of one roll is bounded below by the exchange document (fee + one tick each leg = 1.5bp) and above by what the day's range implies. Neither end is a quote, and the upper end is plainly saturated: it returns a number of the same order as the day's own range (0.9-2.6%) on a contract whose tick is 0.5bp, so it cannot resolve a spread two orders of magnitude below the range it reads.

That makes one line genuinely unjudgeable here rather than simply expensive. **IF** keeps its break-even inside that band, so it clears the line at the document floor and fails at the range-implied reading -- the same face says both, and choosing between them would be choosing an assumption. It is published as **unresolved pending a quote tape**, which is a different claim from rejected, and it stays out of every book until then.

The rest need no quote tape: **IC, IM** stay admitted with the whole band charged, because the discount is simply larger than any roll cost this tape can produce.

**IH** is below the line before a single roll is paid, so no cost question is open on it.

## §四 Is the estimator reading a spread, or a range?

Split the rolls by the day's own range. If the number were a quote, a quiet third and a violent third would imply the same spread. If it rises with the range, the estimator is carrying volatility and only its *ordering* is earned -- which is exactly the difference between "the roll costs 20bp" and "the estimator says 20bp on average and 6bp on the quiet third".

| product | quiet third | middle third | violent third | violent / quiet | flag |
|---|---|---|---|---|---|
| IF | 20.415 bp (range 0.911%) | 16.928 bp (range 1.27%) | 19.934 bp (range 2.219%) | ×0.98 | ok |
| IC | 24.704 bp (range 0.899%) | 30.792 bp (range 1.436%) | 39.464 bp (range 2.643%) | ×1.6 | **contaminated** |
| IH | 24.289 bp (range 0.864%) | 21.071 bp (range 1.507%) | 16.955 bp (range 2.37%) | ×0.7 | ok |
| IM | 30.502 bp (range 0.938%) | 14.464 bp (range 1.776%) | 40.606 bp (range 2.28%) | ×1.33 | ok |

## §五 What this face does not know

* the band is the honest form of the number: the p25 column is the quiet-day reading and p75 the violent-day one, printed side by side so no single figure has to carry the argument;
* the estimator clips a negative implied spread to zero. In a trending market the implied serial covariance is negative and the reading becomes 0 -- those rolls are inside the `at or under 1.5bp` column, and they pull the median down;
* the fee is the exchange's published rate, and it is the one input here that is a document rather than a tape.

## Roll ledger (last six per product)

**IF**

| date | from | to | cost bp |
|---|---|---|---|
| 2025-06-16 | IF2506 | IF2509 | 14.459 |
| 2025-09-12 | IF2509 | IF2512 | 20.352 |
| 2025-12-15 | IF2512 | IF2603 | 9.77 |
| 2026-03-13 | IF2603 | IF2606 | 0.46 |
| 2026-06-11 | IF2606 | IF2609 | 33.993 |
| 2026-09-11 | IF2609 | IF2612 | 26.772 |

**IC**

| date | from | to | cost bp |
|---|---|---|---|
| 2025-06-16 | IC2506 | IC2509 | 28.016 |
| 2025-09-15 | IC2509 | IC2512 | 33.037 |
| 2025-12-15 | IC2512 | IC2603 | 62.074 |
| 2026-03-10 | IC2603 | IC2606 | 23.976 |
| 2026-06-12 | IC2606 | IC2609 | 83.529 |
| 2026-09-14 | IC2609 | IC2612 | 43.067 |

**IH**

| date | from | to | cost bp |
|---|---|---|---|
| 2025-06-18 | IH2506 | IH2509 | 36.836 |
| 2025-09-15 | IH2509 | IH2512 | 45.65 |
| 2025-12-17 | IH2512 | IH2603 | 0.46 |
| 2026-03-17 | IH2603 | IH2606 | 16.868 |
| 2026-06-15 | IH2606 | IH2609 | 16.564 |
| 2026-09-14 | IH2609 | IH2612 | 21.071 |

**IM**

| date | from | to | cost bp |
|---|---|---|---|
| 2025-06-18 | IM2506 | IM2509 | 28.232 |
| 2025-09-15 | IM2509 | IM2512 | 48.631 |
| 2025-12-16 | IM2512 | IM2603 | 50.889 |
| 2026-03-13 | IM2603 | IM2606 | 6.912 |
| 2026-06-15 | IM2606 | IM2609 | 75.61 |
| 2026-09-14 | IM2609 | IM2612 | 49.623 |
