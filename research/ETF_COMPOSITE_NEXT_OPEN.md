# ETF composite book — does it survive a real next-open fill?

Question left open by `research/ETF_COMPOSITE_FACTOR_PF.md` (caveat #1: "the signal is read at
the close of day t and the book is set at that same close ... entry slippage is unmodelled").
This note answers it with an explicit execution model instead of a haircut.

Artifact: `results/etf_composite_pf_open.json` (evidence_cutoff 2026-10-23, basis `next_open`).
Engine: `scripts/etf_composite_pf.py --basis=next_open` (`--selftest` = 3/3 offline legs).

## The two bases, stated plainly

| basis | decision | fill | overnight gap on the fill bar |
|---|---|---|---|
| `close` (published) | close of t | at that same close | earned by the NEW book (you bought before the gap) |
| `next_open` (this note) | close of t | open of t+1 | earned by the OLD book; the new book only earns open→close |

`next_open` charges 8bp/side on the same turnover at the open, then marks the new book
open→close on the fill bar and close→close afterwards. Nothing else changed: same 1,653-ETF
panel, same six factor signs, 20d median amount ≥ 20M CNY screen, 120-bar history floor,
top-5 equal weight, same 8bp cost.

## Result — the edge survives, the *fast* variant does not

| run | close basis | next-open | Δ |
|---|---|---|---|
| R20 full 2020-01→2026-10 | 9.04% / SR 0.898 / DD −12.8% | **8.57% / SR 0.854 / DD −13.1%** | −0.47pp |
| R20 2020-2023 (IS) | 4.92% / 0.516 | 4.58% / 0.484 | −0.34pp |
| R20 2024+ (OOS) | 15.30% / 1.466 | **14.50% / 1.395 / DD −10.2%** | −0.80pp |
| R5 full | 6.87% / 0.792 | **5.40% / 0.602** | −1.47pp |
| R5 2024+ | 12.12% / 1.206 | 9.73% / 0.944 | −2.39pp |

Turnover is *identical* across bases (R20 1.318/rebal, R5 0.917/rebal) — the picks are the same
decisions, so the entire difference is execution legs. That is the point of the test: it
isolates the fill model.

Controls unchanged by basis (they hold a static book, so the fill model barely bites):
equal-weight universe R20 2.44% full / 9.65% OOS, 510300 0.10% full / 7.03% OOS.
So the honest excess of the R20 book over its own universe on a next-open fill is ~6.1pp/yr
full-window and ~4.9pp/yr OOS — not the 6.6pp/5.7pp the close basis advertised.

## What actually costs money

- **Overnight-gap loss scales with turnover.** R20 loses 0.5pp/yr of CAGR; R5 loses 1.5pp/yr.
  The intraday (open→close) share of ETF returns is where the composite's ranking lives, and a
  next-open fill gives away the overnight part of it on every rebalance. Fewer, slower
  rebalances are therefore not just a cost saving — they are the difference between surviving
  the fill model (R20) and not (R5).
- **2024 is where the giveaway is concentrated**: close basis 9.20% vs next-open 5.27% for that
  year (−3.9pp), while 2025 is flat (35.71% vs 36.16%) and 2020 differs by only 1.5pp. One year
  doing most of the damage is a warning about how stable this haircut is, not a licence to
  average it away.
- Yearly next-open: 2020 +10.0%, 2021 +4.4%, 2022 +0.9%, 2023 +3.0%, 2024 +5.3%, 2025 +36.2%,
  2026 +1.0%. Every year still positive, but the pre-2024 years are thin.

## Honest caveats (still load-bearing)

1. **Permutation null was not re-run on this basis.** The published p=0.000 (300 date-wise
   shuffles) belongs to the close basis and is carried, not re-established. A next-open null is
   a separate run (`--null` is wired only for the close basis).
2. **Fixed weights inside the holding period** — the same implicit daily weight-rebalance
   approximation the close basis already carries. Weights drift in reality; drift is unmodelled.
3. **No slippage beyond the 8bp/side and no size cap.** Turnover 1.318/rebal on a top-5 book of
   liquid ETFs is small, but a 20M CNY median-amount screen is not a fill model.
4. **Missing open prints on held symbols** fall back to that bar's close. This happened 16 times
   for R20 and 15 times for R5 out of ~1,600 bars × 5 names (book-relative count; a panel-wide
   NaN count is meaningless because most ETFs do not print an open on a given day — that
   mistake was made and corrected in this window, see the selftest leg 3).
5. Survivorship in the on-disk panel (existing ETFs only) is unchanged by this note, as is the
   close-to-close-of-decision-day signal read.

## Next step (pointer)

The two remaining unmeasured pieces are (i) a next-open permutation null, and (ii) the
bond-sleeve decomposition re-run on this basis — the earlier sleeve note showed gold is the
load-bearing sleeve and bonds were a drag on the close basis; whether that ordering survives an
open fill has not been tested. Promotion still requires a prereg with an explicit exit axis.