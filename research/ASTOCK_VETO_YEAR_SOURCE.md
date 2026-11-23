# A-share veto book: was 2026 the market, or did the sort stop paying?
generated 2026-11-23T18:43:04+08:00 · data cutoff 2026-11-20 (last rebalance decision 2026-10-14) · machine bm-c · 77 rebalance periods (2020-07-06 -> 2026-10-14, hold 20 bars, cost 8.00 bp/side)
**The one-line answer.** 2026: the veto arm (B) lost -13.24%. With beta 0.98 on CSI1000, the beta leg alone accounts for -19.74% and the rest (alpha) 8.10% -> **Y_BETA_DOMINANT** (beta log-share 1.55; a share above 1.00 means the beta leg was *bigger* than the loss and the book's own alpha offset that much of it). Meanwhile the sort itself (B minus the same pool, A) contributed +0.2428%/period (t +3.46) over the whole window and its year-by-year slope is +0.00007/period per year (t +0.20) -> **SORT_STABLE**.

## Year table (year totals, chained over that year's own periods)
| year | periods | A pool | B veto | R random | sort B-A | CSI1000 | beta leg (B) | alpha (B) |
|---|---|---|---|---|---|---|---|---|
| 2020 * | 7 | -5.76% | -5.43% | -5.72% | +0.35% | -2.80% | -2.71% | -2.80% |
| 2021 | 12 | +23.63% | +26.36% | +23.55% | +2.21% | +13.58% | +13.27% | +11.56% |
| 2022 | 12 | -3.05% | +2.38% | -2.95% | +5.59% | -10.09% | -9.75% | +13.44% |
| 2023 | 12 | -3.47% | -1.31% | -3.53% | +2.24% | -17.03% | -16.62% | +18.36% |
| 2024 | 12 | +4.70% | +10.55% | +4.61% | +5.59% | +4.90% | +4.93% | +5.35% |
| 2025 | 12 | +53.18% | +57.23% | +53.14% | +2.64% | +43.81% | +42.66% | +10.22% |
| 2026 * | 10 | -13.94% | -13.24% | -13.92% | +0.81% | -20.19% | -19.74% | +8.10% |

`*` fewer than 12 periods in that year: a partial year, never compared to a full one.
## Beta fits (full window, per-period returns)
| arm | benchmark | beta | alpha/period | R² | n |
|---|---|---|---|---|---|
| A | CSI300 | 0.932 | +0.8741% | 0.372 | 77 |
| A | CSI500 | 1.082 | +0.5477% | 0.706 | 77 |
| A | CSI1000 | 1.000 | +0.5811% | 0.882 | 77 |
| A | SSE50 | 0.748 | +0.9382% | 0.204 | 77 |
| B | CSI300 | 0.921 | +1.1163% | 0.370 | 77 |
| B | CSI500 | 1.058 | +0.7967% | 0.688 | 77 |
| B | CSI1000 | 0.976 | +0.8297% | 0.857 | 77 |
| B | SSE50 | 0.757 | +1.1823% | 0.213 | 77 |
| C | CSI300 | 0.930 | +1.0679% | 0.375 | 77 |
| C | CSI500 | 1.057 | +0.7480% | 0.683 | 77 |
| C | CSI1000 | 0.973 | +0.7816% | 0.848 | 77 |
| C | SSE50 | 0.772 | +1.1357% | 0.220 | 77 |
| R | CSI300 | 0.932 | +0.8731% | 0.372 | 77 |
| R | CSI500 | 1.082 | +0.5468% | 0.705 | 77 |
| R | CSI1000 | 1.000 | +0.5801% | 0.882 | 77 |
| R | SSE50 | 0.748 | +0.9371% | 0.204 | 77 |

## The sort, as its own series
| window | n | mean B-A /period | t | mean B-R /period | t |
|---|---|---|---|---|---|
| full window | 77 | +0.2428% | +3.46 | +0.2438% | +3.45 |
| everything before 2026 | 67 | +0.2657% | +3.94 | +0.2671% | +3.93 |
| 2026 | 10 | +0.0893% | +0.29 | +0.0877% | +0.29 |

## What this face does not say
- beta is one number over 2020-2026: it says what the book carried on average, not what it carried in any single year. A yearly refit over ~11 points would fit noise and call it a coefficient.
- the index legs are close-to-close index levels, not tradable ETF prices; the beta leg is an attribution device, not a hedge someone can buy at that price.
- 2026 is 10 periods to 2026-11-20. That is a partial year; the verdict says so.
- a beta share and a decay slope are two different questions with two different verdict tokens; neither one alone retires the book.
