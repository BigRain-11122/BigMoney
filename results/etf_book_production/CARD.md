# ETF book -- production candidate, order sheet (2026-10-29 bar)

Config: 12 names of a 1503-instrument bond-free pool, rebalance every 20 bars, 10 bp/side, 8% vol target (de-lever only).

| window | CAGR | Sharpe | max drawdown | realised vol | target |
|---|---|---|---|---|---|
| 2020-01 onwards | 9.7% | 1.00 | -11.8% | 10.2% | 8% (1.27x) |
| 2020-2023 | 3.8% | 0.44 | -11.8% | 10.0% | 8% (1.25x) |
| 2024 onwards | 18.6% | 1.76 | -10.7% | 10.4% | 8% (1.30x) |

**Vol label vs delivered risk: target 8% -> delivered 10.2% over the full window (1.27x).** The overlay only de-levers, so a sleeve sized on its own backward vol can run hotter than 8%; read the risk column, not the label.


**Feed: current** -- priced on the 2026-10-29 bar; the official calendar expects 2026-10-29 (lag 0 official day(s)).

**Today (2026-10-29 bar): HOLD: 9 bars until the next decision point** (last grid decision 2026-10-14).

Realised 60d book vol 11.4% -> risk scale 0.70, cash slot 29.9%.

| code | name | sleeve | weight | target (CNY) | executable (CNY) | 100-share lots |
|---|---|---|---|---|---|---|
| 159501 | 纳指ETF嘉实 | equity | 5.8% | 58,398 | 58,340 | 26700 |
| 513100 | 纳指ETF国泰 | equity | 5.8% | 58,398 | 57,398 | 4900 |
| 513690 | 港股红利ETF博时 | equity | 5.8% | 58,398 | 58,300 | 53000 |
| 159577 | 美国50ETF汇添富 | equity | 5.8% | 58,398 | 58,311 | 34200 |
| 159263 | 价值ETF易方达 | equity | 5.8% | 58,398 | 58,344 | 52000 |
| 513630 | 港股低波红利ETF摩根 | equity | 5.8% | 58,398 | 58,360 | 37700 |
| 513300 | 纳斯达克ETF华夏 | equity | 5.8% | 58,398 | 58,194 | 21200 |
| 513850 | 美国50ETF易方达 | equity | 5.8% | 58,398 | 58,262 | 30600 |
| 159207 | 高股息ETF广发 | equity | 5.8% | 58,398 | 58,300 | 50000 |
| 159307 | 红利低波100ETF博时 | equity | 5.8% | 58,398 | 58,374 | 56400 |
| 513870 | 纳指ETF富国 | equity | 5.8% | 58,398 | 58,328 | 27500 |
| 159632 | 纳斯达克ETF华安 | equity | 5.8% | 58,398 | 58,297 | 23300 |
| cash | - | money | 29.9% | 299,225 | 301,192 | - |

**Which column is money.** A weight times capital is the sizing INTENT; only whole 100-share lots can be placed. So the executable column can only spend 698,808 of the 700,776 target book, and the desk keeps 1,968 (0.20% NAV) in cash that the risk scale never asked for -- that residue is the price of lot granularity, not a position. Place the executable column. Until r1342 this card printed the target column as if it were the order, which is why the ticket disagreed with it by 0.13% NAV (E201); the two faces now reconcile to the yuan.

## What the rotation is worth

Against a static mix of this book's own class exposure -- no scoring, no rotation, same grid, same cost rule, same 8% overlay -- the book returns 9.5%/yr vs 3.1%/yr (+6.4pp), worst drawdown -11.8% vs -22.9%, carrying 10.5x the static arm's turnover. That is the number the machinery has to beat to justify trading at all. See results/etf_book_passive_mix.json.

The same test outside the regime this card was published on -- the 193 ETFs that already existed before 2020, priced 2015-2019, same engine, same grid, same cost rule, same overlay on both arms: the book returns 5.1%/yr vs 2.9%/yr for the static mix (+2.2pp), against +4.4pp on those SAME 193 names over 2020+. Read the two together: the premium survives the period change, so the machinery is not what the pre-2020 window was missing.

## The 2015-2019 reconciliation

This card states two things about 2015-2019 that look like a contradiction: the caveat below reports -8.9pp of excess (-5.0%/yr absolute) before 2020, while the rotation section above reports a premium on that same window. They are different cells, and the ladder between them is measured, not argued: from the caveat's cell (all classes, 5 names, no sizing rule) to this book's cell, holding the window and the fill rule fixed, the CAGR moves +10.1pp in total (+5.8pp from dropping the bond/money sleeve, -0.1pp from widening the book to 12 names, +4.4pp from adding the 8% sizing rule). Both ends reproduce their published number within 0.5pp. See results/etf_book_window_decomp.json.

So the pre-2020 failure belongs to the bond-inclusive, unsized cell (-5.0%/yr) and not to the ranking: with the same sizing rule on both arms the ranking still pays before 2020, just less than it pays after. What the ladder does NOT say is that the ranking works without the sizing rule -- on this window it does not.

## What is left after the four betas

Regressed on the four exposures an account could hold instead of this book (gold / Nasdaq-100 QDII / CSI300 / treasury bond, same execution basis, same cost), the book's daily returns leave an intercept of **+5.9%/yr with t=1.96** and R2=0.43, as of 2026-10-29. The equal-weight four-ETF basket itself returns 10.2%/yr at Sharpe 0.99 and worst drawdown -11.3%, against the book's 9.7%/yr, Sharpe 1.00 and -11.8%.

Read that as **not distinguishable from a fixed loadings mix**, not as zero and not as proven skill: the in-sample half of the window prints t=1.16 and the out-of-sample half t=1.99, so the point estimate is carried by the later period and the line is a risk statement rather than a return one.

The single arm that out-earns the book is gold (13.5%/yr) at a -31.5% drawdown -- the comparison has to be printed next to the return or it reads as a verdict. See results/etf_book_spanning.json.

The staggered 6+6 book (same universe, score, execution and cost; second sleeve offset half a rebalance period) leaves **+6.9%/yr at t=2.40** (IS t=1.26 / OOS t=2.35) with residual vol 7.3%, against the single sleeve's +5.9%/yr at t=1.96 and 7.7%. The split clock clears a t of 2 where the single sleeve does not: that is a strategy difference worth its own test, not a free lunch -- one arm over the threshold is a hypothesis, not an edge.

## Does any of it survive outside 2020-2026?

The same regression, run on the 193 ETFs that already existed before the boom, over 2015-01-01..2019-12-31 (a window this card's configuration was never fitted in, control delta 0.13pp against the published pre-2020 cell):

| arm | CAGR | Sharpe | maxDD | intercept | t | R2 |
|---|---|---|---|---|---|---|
| single sleeve | 5.1% | 0.70 | -16.7% | +2.0%/yr | 1.04 | 0.70 |
| staggered 6+6 | 4.3% | 0.57 | -17.6% | +1.0%/yr | 0.48 | 0.68 |
| equal-weight four ETFs | 8.6% | 0.97 | -13.0% | - | - | - |

**Neither arm clears a t of 2 outside 2020-2026** (single t=1.04, staggered t=0.48; the out-of-sample half prints t=-0.39 and t=-0.77, i.e. no intercept there at all). Read it as: the published intercept is a property of the boom window and the panel that grew in it, not yet a property of the rule -- the pre-2020 cross-section is small and survival-filtered, so this is one honest negative, not a demolition. It is, however, the reason not to scale size on the 9-10% headline.

In that window a static equal-weight basket of the same four ETFs returned 8.6%/yr at Sharpe 0.97 against the book's 5.1%/yr at 0.70 (-3.5pp), so the negative is not merely a failed t-test -- the rotation cost money there. See results/etf_book_spanning_pre2020.json.

## Does the book trade on noise?

The book holds 12 names and re-decides every 20 bars, so its score only has to separate the 12th name from the 13th. Over 83 decisions that gap is a median of 0.018 standard deviations of the bar's own cross-section, and 86.8% of decisions sit inside 0.10 sd -- **the cut line is, literally, a coin flip at the margin**.

The trades are not. Of the 590 executed pairs (a name leaving, a name entering) the median score gap is 0.97 sd and only 2.9% sit inside 0.10 sd. Read the two lines together: the ranking is noisy exactly where it costs nothing, and decisive where it costs 10.0 bp a side.

Priced the other way: a buffer that only displaces an incumbent when the challenger beats it by k*sd, run through the same engine on the same grid (k=0/k=0.05/k=0.1/k=0.2/k=0.35/k=0.5, 10.0 bp/side, control arm 9.70% vs 9.70% published = +0.00pp):

| buffer | turnover/decision | CAGR | Sharpe | maxDD |
|---|---|---|---|---|
| k=0 | 0.934 | 9.70% | 1.00 | -11.8% |
| k=0.05 | 0.901 | 9.77% | 1.01 | -11.6% |
| k=0.1 | 0.887 | 9.76% | 1.01 | -12.6% |
| k=0.2 | 0.843 | 9.81% | 1.02 | -12.5% |
| k=0.35 | 0.762 | 9.59% | 0.99 | -12.6% |
| k=0.5 | 0.702 | 9.66% | 1.00 | -13.5% |

k=0.05 is the only arm that lowers turnover (0.934 -> 0.901), keeps the return (+0.07pp) and improves both Sharpe and drawdown; past k=0.35 the buffer starts costing return and depth. So the buffer is a **cost knob, not a discovered edge** -- worth using, worth nothing to brag about.

- exploratory: no preregistration, no verdict, no ledger booking
- MEASURED (results/etf_book_buffer_adoption.json): that path-dependence test was run on 60 cells -- verdict REJECT. Read the arms above as one decision sequence, not an edge.

## How bad can the drawdown be?

The drawdown column above is one ordering of the trading days. Bootstrapping the book's own return path (blocks 1/5/10/20/40/60/120/250 bars, 2000 resamples) puts the 5th-percentile drawdown between **-25.0% and -17.1%** and the median between -14.6% and -12.1% -- a spread of 7.9pp produced by the block length alone, i.e. by how long the ruler remembers dependence.

| block (bars) | maxDD p5 | maxDD p50 | share worse than -20% | point maxDD pctile |
|---|---|---|---|---|
| 1 | -24.72% | -14.45% | 15.3% | 76.2 |
| 5 | -25.02% | -14.59% | 16.1% | 77.0 |
| 10 | -23.16% | -13.97% | 11.8% | 73.2 |
| 20 | -20.58% | -13.18% | 6.4% | 66.8 |
| 40 | -20.54% | -13.05% | 6.1% | 65.6 |
| 60 | -21.36% | -13.09% | 7.5% | 65.0 |
| 120 | -19.44% | -12.94% | 4.2% | 64.8 |
| 250 | -17.08% | -12.14% | 1.1% | 55.4 |

Read the card's own -11.8% as the median of that ruler, not its tail: size the position against the p5 column, which is 13.2pp worse than the headline at the widest block.

> Band priced on the **2026-10-29** bar from results/etf_book_bootstrap/BLOCKS-2026-10-29.json. A tail quoted without its block is a sentence without its parameter (E248).

## Caveats

- THE DRAWDOWN LINE ABOVE IS A MEDIAN, NOT A TAIL: it is priced on one ordering of the trading days. Bootstrapping this book's own return path at blocks 1/5/10/20/40/60/120/250 (the block is a free parameter) puts the 5th-percentile drawdown between -25.0% and -17.1% and the share of resamples worse than -20% between 1.1% and 16.1%. Size against the p5 column. See results/etf_book_bootstrap/BLOCKS-2026-10-29.json.
- THE SIX FACTOR DIRECTIONS WERE CHOSEN WITH HINDSIGHT: every published number here uses a fixed sign block, and those signs are exactly this panel's full-sample IC signs (6 of 6 factors match). Re-priced with signs estimated only from already-realised windows, the same engine returns -10.81%/yr (Sharpe -0.41) against +6.14%/yr (+0.64) for the fixed signs -- and reversing the trailing sign does not recover it (-0.87%/yr). Read the headline as the size of a period, not the size of a rule. See results/etf_sign_pit.json.
- ONE REGIME, NOT A VERIFIED EDGE: on the 224 ETFs that existed before 2020, priced 2015-2019 (a window this card never covered) the same engine returned -4.97%/yr against +3.89%/yr equal weight = -8.86pp excess, worse in 6 of 6 grid cells, random-score p=0.96. The published CAGR is the 2020+ regime, not a property of the factors. That cell is bond-inclusive, 5 names wide and has no sizing rule; 'The 2015-2019 reconciliation' below prices what each of those differences is worth. See results/etf_book_pre2020.json.
- THE COMMODITY SLEEVE IS MOSTLY METAL BETA WITH A MODEST RANKING OVERLAY: it produced 30.1% of gross return; the same engine restricted to the 41 commodity ETFs returned +16.31%/yr against +11.45%/yr for holding those names equally (+4.86pp), and the deepest-turnover commodity name (518880) returned +13.91%/yr passively, i.e. the book beat holding the metal by +2.40pp. Read the sleeve as commodity/gold exposure plus a small selection add-on, not a commodity ranking that pays. See results/etf_book_commodity_split.json.
- ETF pool is today's listed set: survivorship inflates the equity sleeve.
- 2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.
- The vol target only de-levers; it is a drawdown tool, not an edge. Priced on the draw tail (paired bootstrap, 2000 resamples, blocks 5/20/60/120/250): the median drawdown gain is +6.04pp but only 21% of it survives at the worst 1% of histories (+1.26pp), bought with -4.61pp of median CAGR -- mostly a middle-path tool.
- Delivered vol is not the label: target 8% -> delivered 10.2% over the full window (1.27x). The label is a per-hold risk target, so an 8% label annualises near 10% once hold-level vol dispersion is priced in -- a definition gap, not a sizing bug (research/ETF_VOL_CALIBRATION.md).
- Order sheet is research output, not an investment recommendation.
- The sheet is the book decided at book_decided_at, not a re-ranking of the latest bar: the engine only re-decides every 20 bars, so an off-grid ranking would trade names the book never held.
