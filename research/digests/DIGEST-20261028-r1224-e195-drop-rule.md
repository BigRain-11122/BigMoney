# DIGEST 2026-10-28 r1224 bm-b — E195: pick the drop-trim rule before you look at the answer

Pos: `results/e43_tilt_4member/LADDERDROPRULE-20261027.json` ·
leg: `python scripts/e39_panel_census.py tilt3ladderdroprules` ·
selftest 670 → 678 (8 legs) · method card E196.

## The question E190 left open

E190 published that all four flagged ladder-drop reversals vanish once you remove
a handful of months, but that the *class* flips depending on which removal rule
you use — 3/4 pairs were "two-month artefact" under the magnitude rules and
"era property" (or never agreeing) under the chronological edge rules. A verdict
whose class is chosen by the trimming method is not a verdict, so E195 fixes the
rule **in advance** on columns that cannot see the answer.

## The rule has to be blind to the drop's own gap series

The month rows carry six columns; `delta_sum`, `delta_link` and `gap_bp` *are*
the drop's measurement. The four tested rules read the book's own monthly return
(`full_ret`) only:

| rule | removes |
|---|---|
| `book_mad3` | months with \|book return\| > median + 3 × 1.4826·MAD |
| `book_gross_x2` | months with \|book return\| > 2 × the era median |
| `book_top_decile` | the largest \|book return\| months, top 10% (≥1) |
| `chrono_edges` | the era's first and last decision month |

E186's carrier month is published beside them as the **dependent** contrast —
it was read off the gap series, so it cannot justify removing a month. A
selftest leg pins the blindness: feed the same `full_ret` column with
gap/delta columns inflated 1000× and every rule selects identical months.

## What it says

| era | drop | base arith | base comp | pre-registered kills | survives | class |
|---|---|---|---|---|---|---|
| 2024_now | sh510050 | +73.16 | −34.01 | all 4 | — | quotable artefact |
| full | sh510050 | **+0.07** | −38.20 | mad3, gross×2, top-decile | chrono_edges | rule-sensitive |
| pre2017 | sh510300 | −32.57 | +6.18 | all 4 | — | quotable artefact |
| pre2017 | sh510500 | +36.58 | −9.66 | all 4 | — | quotable artefact |

- **3 of 4 pairs are now quotable as artefacts**: the reversal dies under every
  rule an observer could have written down before seeing the gap series, not
  just under the hand-picked carrier month.
- **The full-era sh510050 pair is the interesting failure**: its arithmetic
  level is **+0.07bp** — one five-hundredth of the 38bp gap it is being told
  apart from. Any removal that drops book-outlier months moves that hair across
  zero; only chronological edge-trimming (first + last month) leaves both halves
  where they were (+15.70 / −20.46). So the pair is neither an artefact nor a
  property: it is a near-zero arithmetic level whose sign is a rounding-scale
  fact, and the honest label is "the two readings differ in magnitude, not in
  direction".
- The carrier-only rule kills all four, which is exactly why E190's conclusion
  needed this test: used alone it would have called every pair fragile.

## What not to quote

- "The full-era drop reverses the effect" — the arithmetic side of that reversal
  is 0.07bp. Quote the gap (−38bp of compounded drag), not the sign.
- Any per-rule class as if it were the pair's class; the face publishes
  `rules_that_kill_the_reversal` and `rules_under_which_it_survives` so the
  reader sees both sets.
- Removing months still changes the sample: this measures fragility, it does not
  license dropping a month for real.

## Next

E192 (wide-book carrier persistence) and E193 (delta build stance) remain ready
in the pool; E195 hands them the same discipline — a class that depends on the
knob was never measured.