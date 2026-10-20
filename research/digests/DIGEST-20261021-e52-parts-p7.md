# DIGEST 2026-10-21 — E52 sevenths (P7): the flip set saturates, the band does not

Source: `results/e46_live_span/LIVESPAN-20261020-x0-p7.json` and `LIVESPAN-20261020-x3-p7.json`
(burned by bm-b r1128, census leg `scripts/e39_panel_census.py livespan --cost {0,3} --parts 7`,
evidence_cutoff 2026-10-20). Descriptive census only: zero prereg, zero judgement, zero ledger
booking, trial_count 0.

## 1. What sevenths added

E51 (sixths) was the first cut where all four eras flip internally (4 of 4). At sevenths the set is
unchanged: **4 of 4 eras still flip at both cost levels**, with identical part indices dominating.

| era | x0 parts (bp) | x0 flip | x3 parts (bp) | x3 flip |
|---|---|---|---|---|
| pre2017 | 0, -7, 708, -1732, 533, 771, 113 | yes | 0, -11, 700, -1779, 535, 767, 93 | yes |
| 2017_2020 | -182, 238, 963, -774, 791, 408, 876 | yes | -190, 242, 952, -789, 779, 391, 842 | yes |
| 2021_2023 | 213, -220, 667, 8, 971, 246, -113 | yes | 188, -233, 659, -20, 969, 238, -107 | yes |
| 2024_now | 803, -317, 406, 685, -602, -1848, 438 | yes | 796, -331, 394, 675, -613, -1862, 427 | yes |

Era levels (x0 / x3): pre2017 239 / 230, 2017_2020 423 / 410, 2021_2023 247 / 237, 2024_now 93 / 81.
The fee axis moves every era level by 8–13 bp and every single part by ≤14 bp — the sixth-to-seventh
step did not change what the x3 face says.

## 2. The band is cut-artefactual, now with a slope

Part band (max − min of the era's parts), zero cost, by cut count:

| parts | pre2017 | 2017_2020 | 2021_2023 | 2024_now | mean |
|---|---|---|---|---|---|
| 2 | 41 | 24 | 190 | 593 | 212 |
| 3 | 403 | 353 | 637 | 670 | 516 |
| 4 | 931 | 761 | 512 | 751 | 739 |
| 5 | 1569 | 847 | 346 | 1139 | 975 |
| 6 | 1109 | 959 | 1017 | 1051 | 1034 |
| 7 | 2503 | 1737 | 1191 | 2651 | 2021 |

Read honestly: the band is **not** monotone in the cut count (pre2017 dips at sixths, 2021_2023 falls
from fifths to p5 then rises), so no "band law" exists — but sevenths is the widest cut at three of
four eras, and the driver is visible: one part of each era now carries ±1700–1900 bp (pre2017 −1732,
2024_now −1848). Shrinking a part does not shrink its risk: the extreme part simply absorbs the same
total book over a shorter slice.

**Consequence for claims**: a "the spread is stable" statement quoted with a band must name its cut;
the era-level number (230–423 bp) is cut-stable, the band is not. This is the same lesson E50 gave
at fifths, now with a second, larger instance.

## 3. Live reading (descriptive)

- 2024_now era level +93 bp is the smallest of four; its newest stretched part (−1848 bp at part 6)
  says the last ~1 year of live span is a single strong dump, not a level shift.
- 2021_2023 loses its last clean stretch at this resolution (first/last parts +213 / −113).
- pre2017's dead first part is still exactly 0.0 bp (259-session eligibility burn-in) — a seventh
  of the era now carries zero information, and it still does not create the flip.

## 4. Next honest step

E53-PARTS-P8 (eighths, x0 + x3) seeded: does the band keep widening, and does the flip count stay at
4 of 4? E44-MIDMONTH-WEAKNESS remains authoring-blocked (needs a name-level mid-month vs month-end
holdings diff leg that does not exist yet).