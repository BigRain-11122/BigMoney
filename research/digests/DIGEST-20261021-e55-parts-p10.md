# DIGEST 2026-10-21 — E55: livespan census split into TENTHS (x0 / x3)

Study: `e46_live_span_split` (runner `scripts/e39_panel_census.py livespan --cost {0,3} --parts 10`)
Faces: `results/e46_live_span/LIVESPAN-20261020-x0-p10.json`, `...-x3-p10.json`
Universe: 1,265 members, evidence_cutoff 2026-10-20. Descriptive census only — zero prereg, zero
judgement, zero ledger booking, trial_count 0.

## 1. Flip set saturates at a fifth consecutive cut

| cut | halves | thirds | quarters | fifths | sixths | sevenths | eighths | ninths | tenths |
|---|---|---|---|---|---|---|---|---|---|
| eras with internal sign flip | 1 | 3 | 3 | 3 | 4 | 4 | 4 | 4 | **4** |
| era levels (x0) | — | — | — | — | — | — | 239/423/247/93 | 239/423/247/93 | **239/423/247/93** |

Era levels are **bit-identical between ninth and tenths** at x0 and identical at x3 (230/410/237/81),
so the era split has converged: no cut from ninths on moves the era average by even 1bp. What has
*not* converged is the within-era dispersion described next.

## 2. Per-part spreads (x0, `spread_bp = 100*(wide − ladder)`; negative = ladder ahead)

- pre2017: 0 / 0 / 787 / 638 / −306 / −1830 / 1177 / 279 / 38 / 231
- 2017_2020: 659 / −952 / 204 / 1138 / 246 / −645 / 457 / 532 / 1005 / 506
- 2021_2023: 167 / 43 / −710 / 504 / 143 / 759 / 1065 / −286 / 92 / 87
- 2024_now: 621 / 493 / −890 / 999 / −38 / −1235 / 371 / 351 / **−5745** / 1177

x3 shifts every part by ≤ 42bp (bands 3049/2099/1761/6929 vs 3007/2090/1775/6922), i.e. cost is not
what moves these readings.

## 3. Band series: three eras narrow, the newest widens again

| era | p9 band | p10 band | delta |
|---|---|---|---|
| pre2017 | 3232 | 3007 | −7% |
| 2017_2020 | 2380 | 2090 | −12% |
| 2021_2023 | 2426 | 1775 | −27% |
| 2024_now | 5815 | **6922** | +19% |

Aggregate read: mean band 3463 → 3448 (plateau, +0.4% off), median 2829 → 2549 (falls). So the
"band grows with granularity" story of r1130 is **not** universal — it now holds for exactly one era,
the newest one, and that era's band is 2.3× the next widest (1.8× at ninths).

## 4. The extreme part is boundary-mobile, not a fixed episode

| cut | part | window | bars | ladder %/yr (maxDD) | wide %/yr (maxDD) | spread |
|---|---|---|---|---|---|---|
| ninths | 8 | 2026-03-10 → 2026-06-29 | 75 | +49.73 (−9.08%) | +7.32 (−8.08%) | −4241 |
| tenths | 9 | 2026-03-25 → 2026-07-02 | 67 | +81.19 (−8.48%) | +23.74 (−8.08%) | **−5745** |

Same rally leg, two cuts, two magnitudes 1.35× apart, with drawdown essentially unchanged (±0.4pp) on
both legs. The part that "owns the band" is therefore a function of where the slice boundary falls
inside a single leg: cutting later moved the boundary *into* the rally and inflated the spread.
Conclusion sharpened from r1130: the band is not only an amplitude sum, its magnitude is a
**cut-boundary artefact within one economic episode**, so "the newest era is the most dispersed" is a
statement about the cut, not about the strategy.

Its immediate successor part 10 = 2026-07-03 → 2026-10-20 (ladder −52.09%/−40.32% wide, spread
+1177) keeps the r1130 two-quarter opposite-extreme reading: the +93bp era average is an average of a
+81%/yr quarter and a −52%/yr quarter.

## 5. Data-reality note (new, cheap, load-bearing)

pre2017 parts 1–2 both print a spread of exactly **0.0** with ladder and wide identical to 2dp
(3.07/3.07 and 3.33/3.33). Those are the 2012-05-29→2012-11-08 and 2012-11-09→2013-05-02 warm-up
windows where the eligible ladder and the wide book coincide, i.e. 20% of the oldest era's parts carry
no information by construction. Any era band that includes them inherits two zero rows — which is part
of why pre2017's band is cut-sensitive at coarse cuts and stable at fine ones.

## 6. Pit rows for the record

- A band quoted without its cut and without its owning part's window is not reproducible: the same
  economic episode produced −4241bp (ninths) and −5745bp (tenths).
- Degenerate parts (ladder ≡ wide) print spread 0.0 and silently occupy band slots; check for them
  before reading a band as dispersion.
- Era levels converge (1bp) long before within-era dispersion does — publish both, never one alone.