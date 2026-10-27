# E141 -- Pricing the machinery against not trading at all (r1307 bm-c)

Question this round answered: **does the shipped ETF book beat simply holding its own asset
classes statically?** Every earlier number priced the book against other ranking rules; none
of them priced it against the thing a holder actually has as an alternative.

## Setup

Panel and control come from `etf_book_production.prep_panel()` (class filter + split repair);
the control arm is the shipped cell (n=12, 20-bar cadence, 10bp/side, 8% de-lever-only vol
overlay, close decision -> next open fill) and it reproduces the published card exactly:

    book  9.49% / SR 0.98 / -11.77% DD   vs published n12_vt08 9.49%  (delta 0.0pp)

Static arms are built from the class equal-weight indices (`etf_equity_alpha.ew_universe`),
blended at the book's own mean class shape (equity 66.3% / commodity 25.5% / convertible
8.2%, from the attribution chain), then run on the **same grid, same cost rule and same 8%
overlay** (`simulate_mix`), so the only difference left is scoring and rotation.

## Numbers

| arm | CAGR | Sharpe | max DD | realised vol | turnover/decision |
|---|---|---|---|---|---|
| book (n12_vt08) | 9.49% | 0.98 | -11.77% | 10.17% | 1.36 |
| static mix, same overlay | 3.13% | 0.39 | -22.90% | 9.33% | 0.13 |
| static mix, no overlay | 5.95% | 0.44 | -29.53% | 16.87% | 0.13 |

**Selection premium: +6.36pp/yr and 11.1pp less drawdown, at 10.5x the static arm's turnover.**

## What this does and does not establish

* It establishes the machinery is not decoration: a holder who never traded would have
  earned 3.1%/yr at double the drawdown. This is the first measurement in the repo that
  puts the book's own alternative on the same basis.
* It does **not** rescue the sleeve findings. r1306 showed the commodity sleeve is 13.9pp
  beta and +2.4pp overlay; r1305 showed the same engine loses to equal weight before 2020.
  A +6.4pp book-level premium in 2020+ is consistent with "the equity sleeve's selection and
  the vol overlay together are worth this much in this regime", not with "the factors work
  everywhere".
* The static arms are **favoured**, not handicapped: `ew_universe` rebalances daily at zero
  cost, and both arms share the same ETF pool (so survivorship inflates both and cancels in
  the premium). The premium is therefore a lower bound on what the rotation adds.
* The static mix's mean class shape comes from the fully-invested attribution chain, not from
  the shipped book's deployed exposure. Both arms get the same overlay afterwards; the
  delivered vol of each arm is published in `read.vol_delivered` so the comparison is
  checkable instead of assumed.

## Trap caught in this round (worth keeping)

The first cut reported a `static_mix_with_cash` arm that was **identical to the fully
invested arm** (both 3.13%). The attribution chain normalises class weights to 1, so
"raw exposure including the cash slot" summed to 1.000001 and the "cash" arm was a
duplicate wearing a different label. Caught by comparing the two arms's numbers before
writing the digest, not by any assertion. Lesson: when two arms print the same number, the
first hypothesis is that they are the same arm.

## Artifacts

* `scripts/etf_book_passive_mix.py` (selftest 8/8)
* `results/etf_book_passive_mix.json` (schema `etf_book_passive_mix/v1`)
* card face: `results/etf_book_production/CARD.md` section "What the rotation is worth",
  fed by `passive_mix_support()` in `scripts/etf_book_production.py` (selftest OK, two new
  legs: reads both arms, soft-fails when the artifact is missing)