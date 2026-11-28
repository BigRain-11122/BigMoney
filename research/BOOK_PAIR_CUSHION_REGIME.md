# BOOK PAIR -- is the cushion conditional on the convertible market's price?

Face: `results/book_pair_cushion_regime.json` · markdown: `results/book_pair_cushion_regime.md` · verdict `CUSHION_DIFFERENCE_NOT_SEPARABLE`.

## Why this was asked

r2179 found the 30/70 book cushions ETF drawdowns by an average of 0.43pp a month, and r2181 showed that average is separable from noise (block bootstrap, 90% band +0.07..+0.82pp). Both faces averaged over the whole overlap. Neither asked whether the cushion survives when the CB market itself is expensive -- and the sleeve is a dual-low convertible book, whose return is mostly premium expansion/contraction over parity.

## Method

- parents imported, not rebuilt: cb = `cb_dual_low` n_hold=20/rebal=20/10bp, etf = `etf_nobond_vt` vol_target=8% n_hold=5 entry_lag=1; weight read from `results/book_pair_blend.json` best.w_cb = 0.30
- regime: tertiles of the CB market's median conversion premium (`conv_premium`), read at the previous month end, edges from an expanding window of at least 250 premium observations -- no look-ahead
- cushion = blend month return minus ETF month return, measured only in months the ETF fell; the same subtraction in up months is the upside given up
- the rule pays 10bp per side on the traded share, and treats an unlabelled month (not enough history) as invested

## Numbers

| regime | months | mean month | falling months | cushion | better in | rising months | upside given up |
|---|---|---|---|---|---|---|---|
| cheap | 6 | +1.18% | 3 | +0.26 pp | 1/3 | 3 | +1.19 pp |
| mid | 29 | +1.48% | 6 | +0.93 pp | 4/6 | 23 | -0.24 pp |
| rich | 46 | +0.28% | 22 | +0.26 pp | 10/22 | 24 | -0.70 pp |

Rule vs always-on vs the same-exposure control: `1.391404` / `1.234035` / `1.281467` Sharpe, 11 switches, 0.33 pp of cost, average cb exposure 0.4321 -> rule verdict `THE_RULE_BEATS_ITS_OWN_EXPOSURE`.

## Reading

The first thing the numbers say is about the sample, not the book: the CB market sat in the top tertile of its own premium history for almost the entire overlap, so the cheap side holds only **9** falling months against **22** on the rich side (gate: 8 each).

The number that would make this actionable is the rich-minus-rest difference and its band: -0.44 pp (-1.34 .. +0.65). A negative band with the two sides on opposite signs is the only configuration that would justify switching the sleeve to cash; CUSHION_DIFFERENCE_NOT_SEPARABLE is what the sample actually supports.

## Owed

- chain leg + smoke leg (shared faces; this round ran under a contention window and touched only new files)
- CEO page section, once the shared page can be edited
- the sleeve-level premium (the 20 held bonds' own premium) as a second regime, to test whether the market median is the wrong measure

