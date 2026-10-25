# ETF book -- production candidate, order sheet (2026-10-23 bar)

Config: 12 names of a 1499-instrument bond-free pool, rebalance every 20 bars, 10 bp/side, 8% vol target (de-lever only).

| window | CAGR | Sharpe | max drawdown | realised vol | target |
|---|---|---|---|---|---|
| 2020-01 onwards | 9.5% | 0.98 | -11.8% | 10.2% | 8% (1.27x) |
| 2020-2023 | 3.8% | 0.44 | -11.8% | 10.0% | 8% (1.25x) |
| 2024 onwards | 18.1% | 1.71 | -10.7% | 10.4% | 8% (1.31x) |

**Vol label vs delivered risk: target 8% -> delivered 10.2% over the full window (1.27x).** The overlay only de-levers, so a sleeve sized on its own backward vol can run hotter than 8%; read the risk column, not the label.


**Today (2026-10-23 bar): HOLD: 13 bars until the next decision point** (last grid decision 2026-10-14).

Realised 60d book vol 11.4% -> risk scale 0.70, cash slot 29.9%.

| code | name | sleeve | weight | amount (CNY) | 100-share lots |
|---|---|---|---|---|---|
| 159501 | 纳指ETF嘉实 | equity | 5.8% | 58,398 | 27200 |
| 513100 | 纳指ETF国泰 | equity | 5.8% | 58,398 | 5000 |
| 513690 | 港股红利ETF博时 | equity | 5.8% | 58,398 | 53600 |
| 159577 | 美国50ETF汇添富 | equity | 5.8% | 58,398 | 35000 |
| 159263 | 价值ETF易方达 | equity | 5.8% | 58,398 | 52800 |
| 513630 | 港股低波红利ETF摩根 | equity | 5.8% | 58,398 | 38400 |
| 513300 | 纳斯达克ETF华夏 | equity | 5.8% | 58,398 | 21700 |
| 513850 | 美国50ETF易方达 | equity | 5.8% | 58,398 | 31400 |
| 159207 | 高股息ETF广发 | equity | 5.8% | 58,398 | 51400 |
| 159307 | 红利低波100ETF博时 | equity | 5.8% | 58,398 | 57200 |
| 513870 | 纳指ETF富国 | equity | 5.8% | 58,398 | 28000 |
| 159632 | 纳斯达克ETF华安 | equity | 5.8% | 58,398 | 24000 |
| cash | - | money | 29.9% | 299,225 | - |

## Caveats

- ETF pool is today's listed set: survivorship inflates the equity sleeve.
- 2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.
- The vol target only de-levers; it is a drawdown tool, not an edge.
- Delivered vol is not the label: target 8% -> delivered 10.2% over the full window (1.27x). The label is a per-hold risk target, so an 8% label annualises near 10% once hold-level vol dispersion is priced in -- a definition gap, not a sizing bug (research/ETF_VOL_CALIBRATION.md).
- Order sheet is research output, not an investment recommendation.
- The sheet is the book decided at book_decided_at, not a re-ranking of the latest bar: the engine only re-decides every 20 bars, so an off-grid ranking would trade names the book never held.
