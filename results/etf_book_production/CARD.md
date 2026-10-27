# ETF book -- production candidate, order sheet (2026-10-26 bar)

Config: 12 names of a 1499-instrument bond-free pool, rebalance every 20 bars, 10 bp/side, 8% vol target (de-lever only).

| window | CAGR | Sharpe | max drawdown | realised vol | target |
|---|---|---|---|---|---|
| 2020-01 onwards | 9.5% | 0.98 | -11.8% | 10.2% | 8% (1.27x) |
| 2020-2023 | 3.8% | 0.44 | -11.8% | 10.0% | 8% (1.25x) |
| 2024 onwards | 18.1% | 1.72 | -10.7% | 10.4% | 8% (1.30x) |

**Vol label vs delivered risk: target 8% -> delivered 10.2% over the full window (1.27x).** The overlay only de-levers, so a sleeve sized on its own backward vol can run hotter than 8%; read the risk column, not the label.


**Feed: current** -- priced on the 2026-10-26 bar; the official calendar expects 2026-10-26 (lag 0 official day(s)).

**Today (2026-10-26 bar): HOLD: 12 bars until the next decision point** (last grid decision 2026-10-14).

Realised 60d book vol 11.4% -> risk scale 0.70, cash slot 29.9%.

| code | name | sleeve | weight | amount (CNY) | 100-share lots |
|---|---|---|---|---|---|
| 159501 | 纳指ETF嘉实 | equity | 5.8% | 58,398 | 27300 |
| 513100 | 纳指ETF国泰 | equity | 5.8% | 58,398 | 5100 |
| 513690 | 港股红利ETF博时 | equity | 5.8% | 58,398 | 52900 |
| 159577 | 美国50ETF汇添富 | equity | 5.8% | 58,398 | 35500 |
| 159263 | 价值ETF易方达 | equity | 5.8% | 58,398 | 52300 |
| 513630 | 港股低波红利ETF摩根 | equity | 5.8% | 58,398 | 38000 |
| 513300 | 纳斯达克ETF华夏 | equity | 5.8% | 58,398 | 21700 |
| 513850 | 美国50ETF易方达 | equity | 5.8% | 58,398 | 31700 |
| 159207 | 高股息ETF广发 | equity | 5.8% | 58,398 | 50900 |
| 159307 | 红利低波100ETF博时 | equity | 5.8% | 58,398 | 56500 |
| 513870 | 纳指ETF富国 | equity | 5.8% | 58,398 | 28200 |
| 159632 | 纳斯达克ETF华安 | equity | 5.8% | 58,398 | 23900 |
| cash | - | money | 29.9% | 299,225 | - |

## Caveats

- ONE REGIME, NOT A VERIFIED EDGE: on the 224 ETFs that existed before 2020, priced 2015-2019 (a window this card never covered) the same engine returned -4.97%/yr against +3.89%/yr equal weight = -8.86pp excess, worse in 6 of 6 grid cells, random-score p=0.96. The published CAGR is the 2020+ regime, not a property of the factors. See results/etf_book_pre2020.json.
- THE COMMODITY SLEEVE IS MOSTLY METAL BETA WITH A MODEST RANKING OVERLAY: it produced 30.1% of gross return; the same engine restricted to the 41 commodity ETFs returned +16.31%/yr against +11.45%/yr for holding those names equally (+4.86pp), and the deepest-turnover commodity name (518880) returned +13.91%/yr passively, i.e. the book beat holding the metal by +2.40pp. Read the sleeve as commodity/gold exposure plus a small selection add-on, not a commodity ranking that pays. See results/etf_book_commodity_split.json.
- ETF pool is today's listed set: survivorship inflates the equity sleeve.
- 2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.
- The vol target only de-levers; it is a drawdown tool, not an edge.
- Delivered vol is not the label: target 8% -> delivered 10.2% over the full window (1.27x). The label is a per-hold risk target, so an 8% label annualises near 10% once hold-level vol dispersion is priced in -- a definition gap, not a sizing bug (research/ETF_VOL_CALIBRATION.md).
- Order sheet is research output, not an investment recommendation.
- The sheet is the book decided at book_decided_at, not a re-ranking of the latest bar: the engine only re-decides every 20 bars, so an off-grid ranking would trade names the book never held.
