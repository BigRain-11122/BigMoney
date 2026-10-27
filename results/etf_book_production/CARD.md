# ETF book -- production candidate, order sheet (2026-10-27 bar)

Config: 12 names of a 1499-instrument bond-free pool, rebalance every 20 bars, 10 bp/side, 8% vol target (de-lever only).

| window | CAGR | Sharpe | max drawdown | realised vol | target |
|---|---|---|---|---|---|
| 2020-01 onwards | 9.6% | 0.99 | -11.8% | 10.2% | 8% (1.27x) |
| 2020-2023 | 3.8% | 0.44 | -11.8% | 10.0% | 8% (1.25x) |
| 2024 onwards | 18.4% | 1.75 | -10.7% | 10.4% | 8% (1.31x) |

**Vol label vs delivered risk: target 8% -> delivered 10.2% over the full window (1.27x).** The overlay only de-levers, so a sleeve sized on its own backward vol can run hotter than 8%; read the risk column, not the label.


**Feed: current** -- priced on the 2026-10-27 bar; the official calendar expects 2026-10-27 (lag 0 official day(s)).

**Today (2026-10-27 bar): HOLD: 11 bars until the next decision point** (last grid decision 2026-10-14).

Realised 60d book vol 11.4% -> risk scale 0.70, cash slot 29.9%.

| code | name | sleeve | weight | amount (CNY) | 100-share lots |
|---|---|---|---|---|---|
| 159501 | 纳指ETF嘉实 | equity | 5.8% | 58,398 | 27100 |
| 513100 | 纳指ETF国泰 | equity | 5.8% | 58,398 | 5000 |
| 513690 | 港股红利ETF博时 | equity | 5.8% | 58,398 | 53000 |
| 159577 | 美国50ETF汇添富 | equity | 5.8% | 58,398 | 35200 |
| 159263 | 价值ETF易方达 | equity | 5.8% | 58,398 | 52200 |
| 513630 | 港股低波红利ETF摩根 | equity | 5.8% | 58,398 | 37900 |
| 513300 | 纳斯达克ETF华夏 | equity | 5.8% | 58,398 | 21600 |
| 513850 | 美国50ETF易方达 | equity | 5.8% | 58,398 | 31500 |
| 159207 | 高股息ETF广发 | equity | 5.8% | 58,398 | 51000 |
| 159307 | 红利低波100ETF博时 | equity | 5.8% | 58,398 | 56400 |
| 513870 | 纳指ETF富国 | equity | 5.8% | 58,398 | 28000 |
| 159632 | 纳斯达克ETF华安 | equity | 5.8% | 58,398 | 23800 |
| cash | - | money | 29.9% | 299,225 | - |

## What the rotation is worth

Against a static mix of this book's own class exposure -- no scoring, no rotation, same grid, same cost rule, same 8% overlay -- the book returns 9.5%/yr vs 3.1%/yr (+6.4pp), worst drawdown -11.8% vs -22.9%, carrying 10.5x the static arm's turnover. That is the number the machinery has to beat to justify trading at all. See results/etf_book_passive_mix.json.

The same test outside the regime this card was published on -- the 193 ETFs that already existed before 2020, priced 2015-2019, same engine, same grid, same cost rule, same overlay on both arms: the book returns 5.1%/yr vs 2.9%/yr for the static mix (+2.2pp), against +4.4pp on those SAME 193 names over 2020+. Read the two together: the premium survives the period change, so the machinery is not what the pre-2020 window was missing.

## The 2015-2019 reconciliation

This card states two things about 2015-2019 that look like a contradiction: the caveat below reports -8.9pp of excess (-5.0%/yr absolute) before 2020, while the rotation section above reports a premium on that same window. They are different cells, and the ladder between them is measured, not argued: from the caveat's cell (all classes, 5 names, no sizing rule) to this book's cell, holding the window and the fill rule fixed, the CAGR moves +10.1pp in total (+5.8pp from dropping the bond/money sleeve, -0.1pp from widening the book to 12 names, +4.4pp from adding the 8% sizing rule). Both ends reproduce their published number within 0.5pp. See results/etf_book_window_decomp.json.

So the pre-2020 failure belongs to the bond-inclusive, unsized cell (-5.0%/yr) and not to the ranking: with the same sizing rule on both arms the ranking still pays before 2020, just less than it pays after. What the ladder does NOT say is that the ranking works without the sizing rule -- on this window it does not.

## What is left after the four betas

Regressed on the four exposures an account could hold instead of this book (gold / Nasdaq-100 QDII / CSI300 / treasury bond, same execution basis, same cost), the book's daily returns leave an intercept of **+5.9%/yr with t=1.94** and R2=0.43, as of 2026-10-27. The equal-weight four-ETF basket itself returns 10.1%/yr at Sharpe 0.98 and worst drawdown -11.3%, against the book's 9.6%/yr, Sharpe 0.99 and -11.8%.

Read that as **not distinguishable from a fixed loadings mix**, not as zero and not as proven skill: the in-sample half of the window prints t=1.16 and the out-of-sample half t=1.97, so the point estimate is carried by the later period and the line is a risk statement rather than a return one.

The single arm that out-earns the book is gold (13.3%/yr) at a -31.5% drawdown -- the comparison has to be printed next to the return or it reads as a verdict. See results/etf_book_spanning.json.

The staggered 6+6 book (same universe, score, execution and cost; second sleeve offset half a rebalance period) leaves **+6.8%/yr at t=2.36** (IS t=1.26 / OOS t=2.30) with residual vol 7.3%, against the single sleeve's +5.9%/yr at t=1.94 and 7.7%. The split clock clears a t of 2 where the single sleeve does not: that is a strategy difference worth its own test, not a free lunch -- one arm over the threshold is a hypothesis, not an edge.

## Does any of it survive outside 2020-2026?

The same regression, run on the 193 ETFs that already existed before the boom, over 2015-01-01..2019-12-31 (a window this card's configuration was never fitted in, control delta 0.13pp against the published pre-2020 cell):

| arm | CAGR | Sharpe | maxDD | intercept | t | R2 |
|---|---|---|---|---|---|---|
| single sleeve | 5.1% | 0.70 | -16.7% | +2.0%/yr | 1.04 | 0.70 |
| staggered 6+6 | 4.3% | 0.57 | -17.6% | +1.0%/yr | 0.48 | 0.68 |
| equal-weight four ETFs | 8.6% | 0.97 | -13.0% | - | - | - |

**Neither arm clears a t of 2 outside 2020-2026** (single t=1.04, staggered t=0.48; the out-of-sample half prints t=-0.39 and t=-0.77, i.e. no intercept there at all). Read it as: the published intercept is a property of the boom window and the panel that grew in it, not yet a property of the rule -- the pre-2020 cross-section is small and survival-filtered, so this is one honest negative, not a demolition. It is, however, the reason not to scale size on the 9-10% headline.

In that window a static equal-weight basket of the same four ETFs returned 8.6%/yr at Sharpe 0.97 against the book's 5.1%/yr at 0.70 (-3.5pp), so the negative is not merely a failed t-test -- the rotation cost money there. See results/etf_book_spanning_pre2020.json.

## Caveats

- ONE REGIME, NOT A VERIFIED EDGE: on the 224 ETFs that existed before 2020, priced 2015-2019 (a window this card never covered) the same engine returned -4.97%/yr against +3.89%/yr equal weight = -8.86pp excess, worse in 6 of 6 grid cells, random-score p=0.96. The published CAGR is the 2020+ regime, not a property of the factors. That cell is bond-inclusive, 5 names wide and has no sizing rule; 'The 2015-2019 reconciliation' below prices what each of those differences is worth. See results/etf_book_pre2020.json.
- THE COMMODITY SLEEVE IS MOSTLY METAL BETA WITH A MODEST RANKING OVERLAY: it produced 30.1% of gross return; the same engine restricted to the 41 commodity ETFs returned +16.31%/yr against +11.45%/yr for holding those names equally (+4.86pp), and the deepest-turnover commodity name (518880) returned +13.91%/yr passively, i.e. the book beat holding the metal by +2.40pp. Read the sleeve as commodity/gold exposure plus a small selection add-on, not a commodity ranking that pays. See results/etf_book_commodity_split.json.
- ETF pool is today's listed set: survivorship inflates the equity sleeve.
- 2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.
- The vol target only de-levers; it is a drawdown tool, not an edge.
- Delivered vol is not the label: target 8% -> delivered 10.2% over the full window (1.27x). The label is a per-hold risk target, so an 8% label annualises near 10% once hold-level vol dispersion is priced in -- a definition gap, not a sizing bug (research/ETF_VOL_CALIBRATION.md).
- Order sheet is research output, not an investment recommendation.
- The sheet is the book decided at book_decided_at, not a re-ranking of the latest bar: the engine only re-decides every 20 bars, so an off-grid ranking would trade names the book never held.
