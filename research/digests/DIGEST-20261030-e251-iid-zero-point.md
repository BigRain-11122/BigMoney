# E251 — the ruler's zero point: independence does not bound the drawdown tail, it sits at the deep end of it

r1348 · bm-c · 2026-10-30 · face `results/etf_book_bootstrap/ENVELOPE-2026-10-29-b1.json`
(gate: `etf_book_nav_envelope.py --check --block 1` → *2000 resample rows re-judged, every
percentile and share matches*) · comparison face `BLOCKS-2026-10-29.json` now carries 8 arms
(1/5/10/20/40/60/120/250) · card E251 · pool row E252-BOOT-BLOCK1-IID (claimed and delivered here)

## Why

E248 priced the block length across 5..250 bars and published the sentence "the tail is the
ruler" — but every one of those arms still *assumes* some persistence. The grid had no zero
point: with no dependence-free arm, "the tail is a parameter" could not be separated from "the
tail is what a dependent process does". Block = 1 is that zero point (resample single days, the
iid limit).

## What

The same engine, same seed rule (seed belongs to the resample index, E247), same 2,000
resamples, block = 1. Nothing else changed, so every difference against block = 5 is the
dependence assumption and nothing else.

## Reading (1,651 bars to 2026-10-29, 2,000 resamples)

| block | CAGR p5 | p50 | p95 | Sharpe p50 | maxDD p5 | maxDD p50 | break −20% | point maxDD pctile |
|---|---|---|---|---|---|---|---|---|
| **1 (iid)** | **3.17%** | 9.79% | 16.64% | 0.98 | **−24.72%** | −14.45% | **15.3%** | 76.2 |
| 5 (week) | 2.92% | 9.74% | 16.98% | 0.98 | −25.02% | −14.59% | 16.1% | 77.0 |
| 20 (cycle) | 3.43% | 9.69% | 16.46% | 0.98 | −20.58% | −13.18% | 6.4% | 66.8 |
| 250 (year) | 3.57% | 9.21% | 18.18% | 0.95 | −17.08% | −12.14% | 1.1% | 55.4 |

1. **Independence is the deep end, not the bound.** The iid arm's p5 drawdown is −24.72%,
   within 0.30pp of the week-block arm (−25.02%) and 7.6pp worse than the year-block arm.
   Assuming *more* memory makes the resampled book look **calmer**, not wilder: long blocks
   carry the crash and the recovery together, so they smooth the path they replay.
2. **The worst single ordering loses 44.9%.** The minimum over the 2,000 iid resamples is
   −44.92% (CAGR min −4.17%). A p5 is still a percentile of an assumption; the row exists in
   the face, so the operator can read the floor rather than trust the label.
3. **So the tail band is not "dependence" and not "noise" — it is the assumption.** The full
   8-arm spread on maxDD p5 is 7.94pp (−25.02% to −17.08%); the dependence-free arm sits at
   the bad end of it, and the whole improvement is bought by *assuming* a year of memory.
   For sizing, that inverts the usual instinct: the reading to size against is the
   short-memory one, and no arm justifies quoting better than −24.7% as the "tail".
4. **The location claim survives the new arm unchanged.** Point CAGR pctile spans 49.2–53.6
   across all eight arms, median CAGR 9.21–9.79%/yr — the frozen readings
   (`headline_not_a_lucky_path` / `drawdown_tail_is_block_dependent` / `median_cagr_stable`)
   all stay `true`, and `blocks --check` re-derived them from the eight arms' own rows rather
   than trusting the stored booleans.

## Consequence published

The card and the executable ticket already print the band (E250). What changes is the
sentence attached to it: the band is not "how much memory the market has", it is "how much
the resampling assumption is worth" — and the operator's number is the pessimistic end,
−24.7%, which is what a reader gets for free by assuming no memory at all.

## Honest limits

- One book, one panel, one window, one cost assumption — block = 1 prices the *resampling*
  assumption only; it says nothing about whether the realised path was typical.
- The p5 estimate itself is noisy at ~0.1pp with 2,000 draws; the 0.30pp gap between block 1
  and block 5 is above that but only just, so it is reported as "within 0.3pp", not as a
  measured ordering.
- The block-5 bump above block-1 is non-monotone in the same way E248 found at block 60 — the
  curve has bumps, so no monotone "longer memory ⇒ wider band" rule may be quoted.