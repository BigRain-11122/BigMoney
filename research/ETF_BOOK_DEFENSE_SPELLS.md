<!-- ETF-BOOK-DEFENSE-SPELLS:BEGIN -->

**verdict** `DEFENCE_IS_A_SPELL_NOT_A_STATE` / `A_HALF_LIFE_YOU_CAN_BUDGET`

cell N5_R20_10bp · evidence_cutoff 2026-11-25 · panel 1670 bars from 2005-02-23

The book is defensive (equity weight <= 0) on **910 of 1670 bars (54.5%)**, in **17 spells**;
a spell lasts a median **20 bars** (p90 **108**, longest **190**).

While defensive the book earns **2.52%/yr**; while offensive **18.09%/yr**.
Forced to hold the eligible equity sleeve over the same defensive bars instead, the rule is worth **-0.0208 log** in total (**-20841 CNY** on the 1000000 ticket), helping in **9 of 17 spells**;
its worst call was 2024-08-16 (80 bars, -0.2055 log vs equities)

What the -20841 bought: inside the defensive bars the equity sleeve's worst peak-to-trough was **-31.3%** while the book's was **-5.8%**; over the whole sample the book's max drawdown is **-13.4%** against the sleeve's **-52.8%** -- the defence did not add return, it bought the journey.

Re-entry sticks less often than it feels: **0 of 16** spell ends are back in defence inside 20 bars (0.0%).

**Today (2026-11-25): the book is defensive, this spell is 190 bars old, and 0.0% of prior spells ran at least as long.**

| start | end | bars | cal days | book log | equity log (same bars) | book - equity |
|---|---|---:|---:|---:|---:|---:|
| 2020-03-09 | 2020-04-03 | 20 | 25 | -0.0085 | -0.1114 | +0.1030 |
| 2020-09-29 | 2020-11-03 | 20 | 35 | -0.0003 | +0.0439 | -0.0442 |
| 2020-12-30 | 2021-01-27 | 20 | 28 | -0.0037 | +0.0789 | -0.0826 |
| 2021-04-01 | 2021-04-29 | 20 | 28 | +0.0004 | +0.0459 | -0.0456 |
| 2021-06-02 | 2021-06-30 | 20 | 28 | -0.0395 | +0.0254 | -0.0649 |
| 2021-11-29 | 2021-12-24 | 20 | 25 | +0.0061 | -0.0161 | +0.0222 |
| 2022-01-25 | 2022-03-28 | 40 | 62 | +0.0128 | -0.1314 | +0.1442 |
| 2022-04-28 | 2022-06-28 | 40 | 61 | +0.0064 | +0.1947 | -0.1884 |
| 2022-07-27 | 2023-01-19 | 120 | 176 | -0.0069 | -0.0219 | +0.0149 |
| 2023-02-24 | 2023-06-21 | 80 | 117 | +0.0062 | -0.0418 | +0.0480 |
| 2023-07-24 | 2023-12-18 | 100 | 147 | +0.0004 | -0.1176 | +0.1179 |
| 2024-01-17 | 2024-05-22 | 80 | 126 | +0.0795 | +0.0655 | +0.0141 |
| 2024-06-21 | 2024-07-18 | 20 | 27 | +0.0008 | -0.0155 | +0.0163 |
| 2024-08-16 | 2024-12-16 | 80 | 122 | +0.0054 | +0.2109 | -0.2055 |
| 2025-01-15 | 2025-02-19 | 20 | 35 | +0.0313 | +0.0776 | -0.0463 |
| 2025-12-12 | 2026-01-12 | 20 | 31 | -0.0023 | +0.0846 | -0.0869 |
| 2026-02-10 | 2026-11-25 | 190 | 288 | +0.0019 | -0.2611 | +0.2630 |

tags: `n_spells=17` / `defensive_pct=54.5` / `bars_median=20` / `bars_p90=108` / `defense_added_log=-0.0208` / `false_start_pct=0.0`

## caveats

- The ETF pool is today's listed set (survivorship), so early spells are read on a panel that would have been thinner in real time.
- The counterfactual leg is the eligible equity equal-weight universe this book already publishes, not 'the index'.
- A spell is measured in bars the book actually held: gaps in the panel shorten spells rather than splitting them.
- This is the all-classes cell. The production candidate (nobond_vt08, 8% vol target) has no bond slot, so it cannot print a defensive spell -- read this table as the all-class book's own history, not the production book's.
- 43.4% of rebalance DATES are fully defensive (etf_equity_alpha) against the bar share printed here: the bar ruler weights the long spells, which is the honest way to ask how much of the calendar the book is parked.
