# DIGEST 2026-10-29 · E196 carrier-month identifiability (bm-c r1331)

**Question.** E190 closed with "no era-level claim may be quoted from this family
without naming the month it rests on". That sentence is only useful if the month can be
named *before* someone quotes the verdict. So: is the carrier month knowable ex ante
(scheduled calendar, a data event), knowable at the month's close, or only in hindsight?

**Deliverable.** `results/e43_tilt_4member/LADDERDROPCARRIER-20261027.json` (mode
`tilt3ladderdropcarrier`, `scripts/e39_panel_census.py`, selftest 670 -> 682, plus one
smoke leg that recomputes the verdict from the numbers on disk). Control first: the
carrier is recomputed from the month rows and must equal the published E186 carrier in
every cell, and the untrimmed effect reproduces the published one (join 8.8e-05 bp).

**The one thing that is ex ante.** All four cells' carrier months sit inside the
scheduled semi-annual index-review window — the review month and the month it spills
into, {6, 7, 12, 1} — declared before any gap is read:

| era | drop | carrier | share | months | in window |
|---|---|---|---|---|---|
| 2024_now | sh510050 | 2026-07 | 0.237 | 34 | 11 |
| full | sh510050 | 2014-12 | 0.118 | 162 | 54 |
| pre2017 | sh510300 | 2016-01 | 0.358 | 44 | 15 |
| pre2017 | sh510500 | 2014-12 | 0.591 | 44 | 15 |

Three distinct months carry four cells (2014-12 is shared), so the honest hit
probability under a uniform month draw is (1/3)^3 = 3.7%, not (1/3)^4.

**What the window test actually says.** Review-window months do hold bigger |gaps| —
standardised |gap| is 2.39x the rest when the eras are pooled — but the strength is
almost entirely an artefact of non-independent cells:

| reading | p |
|---|---|
| pooled, 4 cells / 284 months (nested eras counted twice) | 0.0022 |
| deduplicated to 3 distinct carriers | 0.0048 |
| **disjoint eras only (2 cells / 78 months)** | **0.031** |

Only 2 of 4 cells individually clear p<=0.10 (full 0.032, pre2017/sh510300 0.087;
2024_now 0.132, pre2017/sh510500 0.248). The frozen gate reads the **disjoint** reading,
so the face publishes `review_window_suggestive`, not `established`. The pooled numbers
stay on the face precisely so a reader can see how much of the strength is nesting.

**What is only knowable at the month's close.** The largest-|book return| months are the
carriers' neighbourhood: carrier rank by |full_ret| is 2 / 3 / 1 / 2 of 34 / 162 / 44 / 44
months. So a *live* selector exists — drop the k months with the largest |full_ret|
(no gap column involved) — and at **k=2** all four readings stop disagreeing:

| era@drop | rule hit k | reading at k=2 (arith / comp bp) |
|---|---|---|
| 2024_now@sh510050 | 2 | +159.0 / +91.2 |
| full@sh510050 | 1 | -10.2 / -46.2 |
| pre2017@sh510300 | 1 | -103.8 / -95.6 |
| pre2017@sh510500 | 2 | +37.4 / -10.6 |

**But the proxy is not a mechanism.** Spearman(|full_ret|, |gap|) = 0.682 and r2 = 0.465:
half of a gap's magnitude is *not* explained by how big the month was. And the rule is
not the carrier rule — in 2024_now the top-|return| month is 2024-09 (+24% book month),
not the carrier 2026-07, so k=1 fails there while the top-3-gap trim (E190) succeeds.
Two different months, two different experiments.

**Second reading, offered as a by-product.** Removing the whole review window kills the
reversal in all four cells, and the *complement* (window months only) also reads one way
per pair — but at sizes that differ by sign across pairs (+258/+218, +153/+125 for the
510050 drops; -129/-148, -96/-114 for the pre-2017 pair). This is not evidence the drop
effect exists; it says the window is where the two readings' disagreement lives.

**Consequence.** The E190 sentence gets its answer: the carrier month is **not** fully
identifiable ex ante. One genuinely scheduled label covers all three distinct carriers,
but the evidence for that label's *effect* survives only at p=0.031 on two independent
eras, and the alternative selector that does hit 4/4 is a half-explained proxy for the
quantity it is supposed to predict. Therefore no era-level claim from this family is
quotable on the strength of the calendar alone; the quote must carry the month, and the
month can be *flagged* at month-close (top-2 |return|), never *predicted*.

**Reusable.** Card E196 in `knowledge/METHODOLOGY_ASSETS.md`: a label that is scheduled
years ahead and a label that is computed at the month's close are two different claims —
grade them separately; and when cells are era slices, deduplicating by carrier month is
still not independence (a "full" era literally contains its own sub-eras), so the gate
has to read the disjoint subset.