# E248 — the envelope's one free parameter, priced: the location is the book, the tail is the ruler

r1348 · bm-c · 2026-10-29 (the dead window labelled itself r1349; the commit chain says r1348) · face `results/etf_book_bootstrap/BLOCKS-2026-10-29.json`
arms `ENVELOPE-2026-10-29[-b5|-b60|-b250].json` · card E248 · chain leg `etf_book_block_length`

> **CORRECTION (r1348, the window that verified this estate).** Both defects below were fixed
> by the dead window, but the face it published carried a THIRD one: `readings`
> compared `maxdd_p5.range` (a fraction, 0.0794) against the threshold `3.0`, so
> `drawdown_tail_is_block_dependent` shipped **False** while this page, the reading string and
> every downstream sentence said the tail is the ruler. The three cut-offs now go through one
> function that states its unit (`blocks_readings`, pp for return spans, percentile points for
> `point_pctile`), `blocks --check` re-derives the spread AND the three flags from the re-judged
> arms (an edited flag is now contradicted by the gate, not merely by a comment), and the face
> was republished: all three readings are `true`, and `blocks --check` on the un-republished
> face printed `readings.drawdown_tail_is_block_dependent: published False but the arms say True`.
> Distribution of that band to the operator faces is E250 (card caveat + order-sheet section).

## Why

E246 (r1348) published the book's distribution and then had to admit the one thing it could not
answer: **the block length was a choice.** 20 bars = one rebalance cycle reads as principled, but
nothing had been measured to support it, and three pool rows (E247/E248/E249, block 5 / 60 / 250) were
registered in the pool specifically to bound it. This round ran them.

## Two defects found before the arms could be trusted

1. **The ruler moved with the worker count.** `run()` seeded each job with `SEED + 7919 * k`, so
   the *set of draws* depended on how many processes the host split the work into. Re-running the
   published face with the default `--procs` moved CAGR p5 from 3.79% to 3.66% and the point
   percentile from 51.0 to 49.8 — a wider band than most arms in this repo are judged on, and a
   number that would differ between two machines running "the same" face. Fixed: seed belongs to
   the **resample index** (`seed_i = SEED + 7919 * i`), jobs declare only which indices they own,
   and every row now carries its `i`.
2. **Every arm mislabelled its own parameter.** `_reading(env, point)` was evaluated inside the
   `env.update({...})` literal, i.e. *before* `criteria` landed in `env`, so all four arms printed
   "block=20 bars". A face that misreports its own parameter is the cheapest possible way to publish
   a wrong sentence.

Both are now gates, not comments:

* `--selftest` 11 → **14** legs. L12 asserts that splitting the same index span across three jobs
  changes nothing (this is the leg that would have caught #1); L13 asserts rows carry their index;
  L14 asserts a stored row equals a re-draw from its index.
* `--check` re-derives all percentiles/shares **and** re-draws 21 of 2000 rows from the seed rule,
  so a face produced by the old procs-dependent seeding is contradicted by its own rows.
* `blocks --check` re-derives every number the comparison face quotes from each arm's own rows.

## Reading (2000 resamples per arm, same seed rule)

| block | CAGR p5 | p50 | p95 | Sharpe p50 | maxDD p5 | maxDD p50 | break −20% | point pctile |
|---|---|---|---|---|---|---|---|---|
| 5 (week) | 2.92% | 9.74% | 16.98% | 0.98 | −25.02% | −14.59% | 16.1% | 49.6 |
| 10 | 2.84% | 9.70% | 16.79% | 0.98 | −23.16% | −13.97% | 11.8% | 50.0 |
| 20 (cycle) | 3.43% | 9.69% | 16.46% | 0.98 | −20.58% | −13.18% | 6.4% | 50.1 |
| 40 | 3.59% | 9.65% | 16.72% | 0.98 | −20.54% | −13.05% | 6.1% | 50.8 |
| 60 (quarter) | 3.18% | 9.53% | 16.93% | 0.97 | −21.36% | −13.09% | 7.5% | 51.6 |
| 120 | 3.18% | 9.54% | 17.61% | 0.97 | −19.44% | −12.94% | 4.2% | 51.8 |
| 250 (year) | 3.57% | 9.21% | 18.18% | 0.95 | −17.08% | −12.14% | 1.1% | 53.6 |

The three interior rungs (10/40/120, pool rows E251/E248/E249) were run in the same window after
the four-rung table above: with them the curve is **measured, not interpolated**, and it changes one
sentence. The drawdown tail falls from −25.02% (block 5) to −17.08% (block 250) but not strictly:
it *rises* at block 60 (−21.36% against −20.54% at block 40) and the −20% break share does the same
(7.5% against 6.1%). So "longer block = smaller tail" is a trend with a bump at one quarter, not a
law — the four-rung table could not have seen it either way.

1. **The location is the book, not the ruler.** The published point estimate sits at the 49.6–53.6
   percentile across all seven choices and the median CAGR spans 9.21–9.74%/yr. "This headline is not
   a lucky path" survives the free parameter.
2. **The tail is the ruler.** maxDD p5 spans 7.94pp (−25.02% to −17.08%) and the share of resamples
   breaking −20% spans 1.1% to 16.1% — a 14.6× factor, purely from how long a block is. E246's
   "6.6% break a −20% drawdown" is therefore a **block-20 sentence** and may not be quoted without
   its block.
3. **"Longer block = wider band" is false.** CAGR p5 is non-monotone (2.92 / 2.84 / 3.43 / 3.59 /
   3.18 / 3.18 / 3.57) — and with the interior rungs the drawdown side is *also* non-monotone
   (a bump at block 60), so the parameter changes the tail's SIZE without giving a monotone knob.
4. Consequence for the operator: the card's −12.5% headline drawdown is a median-ish number whose
   honest tail is **−17% to −25%** depending on the dependence assumption, which is 5–12pp worse
   than the card says — now printed on the card and the executable sheet (E250, r1348).

## Honest limits

* One panel, one window, one cost assumption — inherited from the card; block length prices the
  *resampling* assumption only.
* The three readings in the face (location stable / tail block-dependent / median stable) use
  descriptive 5pp / 3pp / 1pp cut-offs fixed **after** the arms ran; they name which sentences
  survive, they are not gates.
* 2000 resamples makes the p5 estimate itself noisy at the ~0.1pp level; the differences reported
  here (0.65pp on CAGR p5, 7.9pp on maxDD p5) are larger than that.