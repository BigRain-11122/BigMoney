# ETF NAV lag face

Generated 2026-11-28T23:03:32+0800 · evidence cutoff 2026-11-27

Verdict: `MOST_LAGGING_ROWS_ARE_ESTIMATES_WEARING_A_DATE`

90 of 1670 legs in the 2026-11-27 snapshot are priced against a NAV that is not that session's (lag up to 9 trading day(s)); over this repo's snapshot history only 99.0% of rows are same-day. 46 are one-offs (their own history lands same-day on >= 85% of snapshots, so a later pass fixes them); 42 sit at 70-85% -- on most days that field is an intraday estimate, and today it fell back to yesterday's official NAV; the row cannot tell you which one it is holding; 2 rarely land same-day at all. On 89 of them the printed premium moved exactly as the price did since the previous snapshot, which is what an unchanged denominator forces -- those readings carry no premium information at all. Largest printed premiums among them: 159509 纳指科技 44.3%, 159501 纳指基金 22.8%, 159696 纳100ETF 22.7%, 159659 纳指 20.6%, 513870 纳指ETF富国 20.5%.

## Lag histogram over 13777 snapped rows

| lag (trading days) | rows |
|---|---|
| -1 | 41 |
| 0 | 13637 |
| 1 | 88 |
| 2 | 3 |
| 3 | 2 |
| 4 | 1 |
| 5 | 1 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1 |
| 9 | 1 |

## Lagging legs in the latest snapshot (2026-11-27)

| code | name | lag | nav_session | printed premium | rebanded p10..p90 | same-day | verdict |
|---|---|---|---|---|---|---|---|
| 159509 | 纳指科技 | 1 | 2026-11-26 | 44.33% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159501 | 纳指基金 | 1 | 2026-11-26 | 22.84% | 20.84%..25.08% | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159696 | 纳100ETF | 1 | 2026-11-26 | 22.72% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159659 | 纳指 | 1 | 2026-11-26 | 20.59% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 513870 | 纳指ETF富国 | 1 | 2026-11-26 | 20.49% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 513100 | 纳指ETF国泰 | 1 | 2026-11-26 | 20.48% | 18.52%..22.67% | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159660 | 纳指100 | 1 | 2026-11-26 | 20.36% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159941 | 纳指ETF | 1 | 2026-11-26 | 20.10% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 513300 | 纳斯达克ETF华夏 | 1 | 2026-11-26 | 19.84% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 513390 | 纳指100ETF博时 | 1 | 2026-11-26 | 19.35% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159632 | 纳斯达克 | 1 | 2026-11-26 | 18.85% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 159513 | 纳指大成 | 1 | 2026-11-26 | 17.97% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 513110 | 纳指ETF华泰柏瑞 | 1 | 2026-11-26 | 17.60% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |
| 513310 | 中韩半导体ETF华泰柏瑞 | 1 | 2026-11-26 | 16.70% | -..- | 89% of 9 | `DENOMINATOR_USUALLY_LANDS_SAME_DAY` |
| 520870 | 巴西ETF易方达 | 1 | 2026-11-26 | 13.61% | -..- | 78% of 9 | `DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS` |

Top 15 of 90 lagging legs by |printed premium|; the full roster is in `results/etf_nav/lag_face.json`.

## Notes

- premium_rebanded is (1+printed)/(1+r) over that leg's own official NAV daily returns; it is an interval for a number that has not been published yet, not a better estimate of it.
- identity_price_is_the_whole_story tests the exact relation (1+prem_T)/(1+prem_T-1) == P_T/P_T-1, which holds only while the denominator is unchanged; when it is true the printed premium change carries no premium information at all.
- same_day_share is over the snapshots this repo captured for that leg, not over the vendor's whole publication history; with a dozen snapshots the lines at 85% and 70% describe the two groups that exist on the board, they are not a statistical test.
