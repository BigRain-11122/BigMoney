# DIGEST 2026-10-29 · E190 drop-fragility curve (pool row E190, closed here on bm-c)

**Question.** E189 removed exactly one month per pair -- the month E186 had called the
carrier -- and all four era-level reversals collapsed. That proved the verdicts were
fragile but not *how* fragile: one month removed is a different finding from five, and a
reversal that needs eight months of a 34-month era taken out would be an era property.
Measure the curve instead of the point.

**Deliverable.** `results/e43_tilt_4member/LADDERDROPCURVE-20261027.json` (mode
`tilt3ladderdropfragility`, `scripts/e39_panel_census.py`, selftest 658 -> 670,
panel_screen 39/39). Control first: both era effects are rebuilt untrimmed from the
published month rows and must reproduce E186's numbers (join max |diff| 8.8e-05 bp).
Four pairs x 3 trims x k=1..8.

**Finding.** Eleven of twelve cells are two-month artefacts; only one needs more than
two months, and its curve is not monotone.

| era | drop | n months | untrimmed arith / comp (bp) | k=1 by \|gap\| | k=1 by \|delta_sum\| | k=1 by edges |
|---|---|---|---|---|---|---|
| 2024_now | sh510050 | 34 | 73.16 / -34.01 | agrees (204.25 / 141.93) | agrees | agrees |
| full | sh510050 | 162 | 0.07 / -38.20 | agrees (44.89 / 1.63) | agrees | still disagrees -> agrees at k=4 |
| pre2017 | sh510300 | 44 | -32.57 / 6.18 | agrees (-103.85 / -95.56) | agrees | agrees at k=1 |
| pre2017 | sh510500 | 44 | 36.58 / -9.66 | agrees (-197.98 / -203.73) | agrees | agrees at k=1 |

Three secondary reads, all of which cost the headline nothing to publish and would have
been invisible if only "the k at which it first agreed" were quoted:

1. **The two concentration trims remove the same month, and it is the carrier.** The k=1
   columns above are numerically identical to E189's carrier-removal column, so the
   largest-|gap| month and E186's declared carrier are one object and the two studies
   corroborate each other instead of being two independent stories.
2. **Trimming the ends is not a clean ruler.** Both pre2017 pairs agree at k=1 and then
   disagree again from k=2..5 (or 2..7) before agreeing at the top of the ladder, and the
   full-era pair alternates (X,X,X,-,X,X,X,-). An agreement you reach by shaving the era's
   ends is a window artefact of the same kind -- which is why the face publishes
   `stable_agree_k` beside `first_agree_k`: a curve that flips back is not a level.
3. **Only one cell survives past k=2.** The full-era sh510050 needs k=4 (and only
   stabilises at k=8). It is published as `fragile_mid`, not as an era property, because
   the untrimmed effect there is +0.07bp against -38.20bp -- a summary of two annualised
   levels whose sum-side reading is already zero to the basis point.

**Consequence.** "The ladder-drop effect reverses at era level" stays withdrawn for all
four pairs, now with the derivative attached: the reversal is a one-month object under
both concentration trims on every era, so no era-level claim may be quoted from this
family without naming the month it rests on.

**Reusable.** Card E194 in `knowledge/METHODOLOGY_ASSETS.md`: publish the curve, not the
crossing; keep `first_agree_k` and `stable_agree_k` as separate readings; and note that
trimming the ends and trimming the concentration are different experiments that happen
to share a k axis.