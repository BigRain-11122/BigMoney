# E171 — the sign face's dissenting era is decided by 4 of 17 months

**Cutoff** 2026-10-27 · **Leg** `e39_panel_census.py tilt3screensign` · **Face**
`results/e43_tilt_4member/TILT3SCREENSIGN-20261027.json` · **Pool row** E171

## What was asked

E169 published the tilt-vs-engine sign face on the RAW arm: 2017_2020 and
2024_now disagreed at the era scale and no era cleared 57% month-level
agreement. E170 had already measured the tilt series as arm-invariant
(0.0bp on every era), so the screened twin could only move the engine column —
and the question was which of the two disagreeing eras keeps its disagreement
once the wide book's own path is re-priced.

## What the burn says

78 cells compared, 5 moved, all of them in the engine column:

| era | engine raw bp | engine screened bp | Δ | era verdict |
|---|---|---|---|---|
| pre2017 | 287.2 | 287.2 | 0.0 | agree → agree |
| 2017_2020 | 331.7 | 331.7 | 0.0 | **disagree → disagree** |
| 2021_2023 | 251.1 | 280.4 | +29.3 | agree → agree |
| 2024_now | −21.6 | +25.1 | +46.7 | **disagree → agree** |
| full | 227.6 | 243.9 | +16.3 | agree → agree |

1. **The tilt column did not move at all** (0 of 25 era tilt cells): E170's
   invariance claim re-measured on a different leg the same day, not trusted.
2. **2024_now's disagreement is a repair artefact of the level**, not a
   property of the tilt. Its engine difference crosses sign (−21.6 → +25.1bp)
   under the split-event repair, so the era that E169 published as "the tilt and
   the book disagree" is the only era whose verdict flips.
3. **2017_2020 keeps its disagreement on both arms** — and it is the era where
   the tilt reads −924bp against a +331.7bp engine, an order of magnitude apart
   rather than a near-zero crossing. That one is not a split-print story.
4. **The month-scale information did not change on any arm**: agreement is
   bit-identical per era (45.8 / 44.4 / 23.5 / 43.8 / 56.8%), because the repair
   moves era levels through a handful of name-months, not through month signs.
   So 2024_now's post-repair "agreement" is an era level carried by 4 of 17
   months — the same weakness E169 already named, now measured on the arm a
   reader would quote.

## Controls

* same-arm control: 0 of 78 cells move, 0 claim moves.
* cutoff control (arm held fixed, raw face on disk): 0 cells, max |Δ| 0.0bp.
* all eras priced on the same month count on both arms (`months_same` true).
* 0 cells exist on one arm only.

## Defect caught in-window (F-20261028-09)

The first cut of the per-era table derived `recovered = screened > raw` and
published `worsens` as its negation. Since every rate was bit-identical, the
face printed **"worsens in ['2017_2020','2021_2023','2024_now','full','pre2017']"**
beside five pairs of identical numbers. Fixed with a three-state
`_agreement_change()` (`recovered` / `worsened` / `unchanged` / `not_measurable`)
plus a selftest leg pinning that equality is neither direction. Same family as
E94/E171's own subject: a label narrower than the evidence.

## Honest limits

* Both arms are burnt off one panel load, so the twin differs in the repair and
  not in what was read — but that also means this face cannot speak about a
  different cutoff (the two published faces carry the same one).
* No era clears 57% month agreement on either arm: this is a census, not a
  signal, and the era "agree" rows should not be quoted as timing evidence.
* Descriptive only: no gate, no verdict, no prereg, no trial count.