# DIGEST 2026-10-21 — E53 eighths (perpetual livespan, parts = 8)

Evidence cutoff 2026-10-20. Descriptive census only: zero prereg, zero judgement, zero ledger
booking, trial_count 0. Runner unchanged: `scripts/e39_panel_census.py livespan --cost 0|3 --parts 8`.

Faces: `results/e46_live_span/LIVESPAN-20261020-x0-p8.json`,
`results/e46_live_span/LIVESPAN-20261020-x3-p8.json` (~7s per leg, inline).

## 1. Headline

Two readings survive the cut, one published claim does not:

1. The internal-sign-flip set stays at **4 of 4 eras** at both cost levels (sixths → sevenths →
   eighths unchanged). The flip count has plateaued; granularity no longer adds members.
2. **r1128's "the band keeps widening to the broadest cut" is withdrawn.** At eighths three of the
   four eras *narrow*; the mean band rises only because one pre2017 part is an outlier. Median band
   falls (2120bp at sevenths → 1628.5bp at eighths).

## 2. Per-era faces

| era | x0 parts (bp/yr) | x0 band | x3 band | era x0 / x3 |
|---|---|---|---|---|
| pre2017 | 0, 432, 1335, -856, **-4997**, 935, 655, 311 | 6332 | 6339 | 239 / 230 |
| 2017_2020 | 222, -137, 933, 290, -238, 685, 483, 618 | 1171 | 1185 | 423 / 410 |
| 2021_2023 | 350, -273, 336, 141, 653, 748, 157, -76 | 1021 | 1017 | 247 / 237 |
| 2024_now | 850, 315, -1236, 441, -12, -225, -1006, 510 | 2086 | 2095 | 93 / 81 |

Cost x3 moves every part by ≤32bp (fees, not sign), era levels −9/−13/−10/−12bp — the same fee
signature every cut since thirds has carried.

Widest-part index is identical across the two cost legs (pre2017 3, 2017_2020 3, 2021_2023 6,
2024_now 1): the cost axis reorders nothing.

## 3. Band series across cuts (x0)

Per-era bands, halves → eighths:

- pre2017: 212 → 516 → 739 → 975 → 1034 → 2503 → **6332**
- 2017_2020: … → 1737 → **1171**
- 2021_2023: 195/637/512/346/1017/1191 → **1021**
- 2024_now: … → 2651 → **2086**

Mean 2020.5 → 2652.5 (up), median 2120 → 1628.5 (down). The mean is a single-part tail, not a
trend. **No band law exists**; every stability claim must name its cut, and quoting a mean band
without the median lets one bull-market part speak for the panel.

## 4. Attribution of the outlier part (the -4997bp)

pre2017 part 5 = **2014-09-16 .. 2015-04-16** (140 bars):

- ladder +203.83%/yr, maxDD −8.07%
- wide book +153.86%/yr, maxDD −6.14%
- spread 49.97 pp/yr = −4997bp

This is the 2014Q4–2015Q1 bull leg, where a concentrated ladder outran the broad benchmark by ~50
percentage points in half a year. The spread statistic is a *difference of annualised returns*, so a
part with a huge common level turns a modest relative edge into a four-digit basis-point reading. The
band is therefore a **return-magnitude artefact, not a risk reading** — existing maxDD figures
(−8.07% vs −6.14%) show no comparable risk gap.

Same reading explains why pre2017's era mean is untouched at 239bp: one part in eight moved, and the
era is a bar-weighted blend.

## 5. Live readings carried forward

- 2024_now +93bp is still its opening stretch (+850, +315) against a −1236 third part and a −1006
  seventh part; the era is a rebound on its first tenth, not a persistent edge.
- 2021_2023 remains the blandest era (band 1021bp, first part +350, last −76).
- pre2017's first part is still exactly 0.0bp with both legs byte-identical (the 259-session burn-in
  measured in E44), and it still sits inside the live range without creating the flip.

## 6. Honest corrections

- Withdrawn: "the band keeps widening to the broadest cut at three of four eras" (r1128). Eighths
  narrows three eras; only pre2017 widens, and by an outlier.
- Withdrawn: "part bands grow monotonically with granularity" (r1125, already withdrawn at r1126).
- Retained: era levels are cut-stable (239/423/247/93 with a −9..−13bp cost shift at every cut ≥ 2);
  flip *membership* is cut-artefactual, and by eighths the count is saturated at 4.

## 7. Next

E54 = ninths, same runner (`--parts 9`), inline; the cut ladder is now past the point where it
changes the flip answer, so the next unit after that should pivot from "how many parts" to "how wide
a part can move the era mean" (bar-weighted sensitivity), which is the question the outlier part
actually raises.