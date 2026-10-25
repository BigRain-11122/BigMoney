# ETF book -- production candidate, order sheet (2026-10-23 bar)

Config: 12 names of a 1499-instrument bond-free pool, rebalance every 20 bars, 10 bp/side, 8% vol target (de-lever only).

| window | CAGR | Sharpe | max drawdown | realised vol | target |
|---|---|---|---|---|---|
| 2020-01 onwards | 9.5% | 0.98 | -11.8% | 10.2% | 8% (1.27x) |
| 2020-2023 | 3.8% | 0.44 | -11.8% | 10.0% | 8% (1.25x) |
| 2024 onwards | 18.1% | 1.71 | -10.7% | 10.4% | 8% (1.31x) |

**Vol label vs delivered risk: target 8% -> delivered 10.2% over the full window (1.27x).** The overlay only de-levers, so a sleeve sized on its own backward vol can run hotter than 8%; read the risk column, not the label.


**Today (2026-10-23 bar): HOLD: 13 bars until the next decision point** (last grid decision 2026-10-14).

Realised 60d book vol 6.0% -> risk scale 1.00, cash slot 0.0%.

| code | name | sleeve | weight | amount (CNY) | 100-share lots |
|---|---|---|---|---|---|
| 515450 | 红利低波50ETF南方 | equity | 8.3% | 83,333 | 58400 |
| 515300 | 300红利低波ETF嘉实 | equity | 8.3% | 83,333 | 62300 |
| 511180 | 可转债ETF海富通 | convertible | 8.3% | 83,333 | 7000 |
| 510760 | 上证指数ETF国泰 | equity | 8.3% | 83,333 | 65200 |
| 511380 | 可转债ETF博时 | convertible | 8.3% | 83,333 | 6500 |
| 159307 | 红利低波100ETF博时 | equity | 8.3% | 83,333 | 81600 |
| 510980 | 上证指数ETF汇添富 | equity | 8.3% | 83,333 | 62900 |
| 513400 | 道琼斯ETF鹏华 | equity | 8.3% | 83,333 | 63200 |
| 512890 | 红利低波ETF华泰柏瑞 | equity | 8.3% | 83,333 | 33900 |
| 159980 | 有色ETF大成 | commodity | 8.3% | 83,333 | 39500 |
| 510210 | 上证指数ETF富国 | equity | 8.3% | 83,333 | 17500 |
| 159887 | 银行ETF富国 | equity | 8.3% | 83,333 | 59900 |
| cash | - | money | 0.0% | 0 | - |

## Caveats

- ETF pool is today's listed set: survivorship inflates the equity sleeve.
- 2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.
- The vol target only de-levers; it is a drawdown tool, not an edge.
- Delivered vol is not the label: target 8% -> delivered 10.2% over the full window (1.27x).
- Order sheet is research output, not an investment recommendation.
