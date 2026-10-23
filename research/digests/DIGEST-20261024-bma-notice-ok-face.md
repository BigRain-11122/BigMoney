# The ok-only availability face is a coverage cut, not a cleaner ordering

r1103 bm-a · 2026-10-24 · evidence `results/fund_avail_face_impact.json`
(`notice_ok_face` + `factors.*.notice_ok_sensitivity`)
prereg-adjacent to r1102 · digest of `DIGEST-20261024-bma-avail-face-impact.md`

## 0. The question r1102 left open

The first-announce repair (`avail_first`) is built from two kinds of rows:

| row status | rows | what the date means |
|---|---|---|
| `ok` | 369,231 | a real first-announce stamp, inside the plausible disclosure window |
| `out_of_window` | 91,067 | no usable stamp; fell back to the statutory deadline |
| `absent` | 1,381 | no stamp at all; fell back to the statutory deadline |

The repair's measured effect (turnover 0.3-1.7% at month-end) mixes the two. The
open question: **does the effect survive if you refuse every row you cannot
verify?** That is the `avail_first_ok` sensitivity face — fallback rows are
dropped outright, never re-dated, because re-dating would invent a stamp.

## 1. Answer: the date repair is small, the coverage cut is large

Month-ends 2010-01 → 2026-09, four income factors, same panel, same dates:

| factor | turnover `pit→first` | turnover `first→first_ok` | ρ `first→first_ok` | dropped names (med) |
|---|---|---|---|---|
| roe | 1.7% | **43.3%** | 0.9786 | 911 of 10,015 (9.1%) |
| np_yoy | 0.5% | 11.0% | 0.9820 | 574 of 9,606 (6.0%) |
| rev_yoy | 0.7% | 12.1% | 0.9837 | 577 of 9,599 (6.0%) |
| gpm | 0.3% | 14.5% | 0.9934 | 922 of 9,967 (9.3%) |

Restricting to verified announcements moves the top-decile basket **an order of
magnitude more** than repairing the dates did. Rank correlation stays high
(0.98-0.99), so this is not re-ordering — it is the sample shrinking.

## 2. Why it moves so much: the dropped names rank best

If the removed rows were random with respect to the factor they would be a
proportional cut. They are not:

| factor | dropped share of sample | share of the top decile that is dropped | over-representation |
|---|---|---|---|
| roe | 10.1% | **38.5%** | **3.2x** |
| np_yoy | 6.2% | 9.9% | 1.4x |
| rev_yoy | 6.2% | 10.3% | 1.5x |
| gpm | 10.2% | 13.4% | 1.2x |

Single-date anchors (roe, from `drop_selection.per_date`):

| date | n | n_ok | dropped | dropped in top decile | turnover |
|---|---|---|---|---|---|
| 2013-06-28 | 4,825 | 2,691 | 2,134 | 454 of 482 | 0.942 |
| 2016-12-30 | 9,035 | 7,277 | 1,758 | 398 of 904 | 0.476 |
| 2020-12-31 | 10,693 | 9,905 | 788 | 338 of 1,069 | 0.391 |
| 2024-12-31 | 11,712 | 11,236 | 476 | 212 of 1,171 | 0.194 |
| 2026-09-30 | 11,740 | 11,681 | 59 | 9 of 1,174 | 0.009 |

**Read this as a bias warning, not as a data-quality win.** Demanding a verified
announcement systematically deletes the high-ROE tail — for roe it removes 10% of
the names and 39% of the best decile. Any study that ranks on `avail_first_ok`
alone is measuring a truncated cross-section, and the truncation is correlated
with the signal. The full `avail_first` face keeps those names with a defensible
(if conservative) date; that is the right face for ranking, and `first_ok` is the
honesty bound to quote beside it.

## 3. Where the restriction actually bites

Deadline-window probes (`first` vs `first_ok`, roe):

| probe | n wide | n restricted | jaccard | turnover |
|---|---|---|---|---|
| deadline −10d | 8,417 | 3,875 | 0.804 | 0.60 |
| deadline | 8,713 | 3,923 | 0.781 | 0.78 |
| deadline +30d | 8,714 | 3,949 | 0.785 | 0.78 |

Inside the disclosure window more than half the names have no verifiable stamp
(same-quarter rows are the ones that just arrived). So the ok-only face is least
usable exactly where the date repair is most valuable — the two effects are not
substitutes, they are complements.

By year, the restriction's basket damage fades with data quality:

| year | roe turnover | np_yoy turnover |
|---|---|---|
| 2013 | 0.92 | 0.32 |
| 2016 | 0.75 | 0.76 |
| 2020 | 0.41 | 0.11 |
| 2023 | 0.24 | 0.04 |
| 2025 | 0.12 | 0.04 |
| 2026 | 0.02 | 0.01 |

The modern era (2023+) is where the restriction is nearly free; anything before
2017 is where it is expensive and where a reader must be told.

## 4. A defect fixed on the way here

`top_set()` took `k = max(min_k, share × n)` with no cap at the sample size. On a
sample thinner than the 10-name floor, `k` exceeded `n`, so two **identical**
faces reported `1 − n/k` turnover — a 2-name sample read 0.8. Selftest leg 12
now pins "identical faces ⇒ 0.0 turnover, including on a thin sample"; the
published numbers are unaffected (samples here are 10k names, `k`=SHARE×n), but
any small-universe reuse of this module would have been silently wrong.

## 5. Limits

* Universe is the stored statement panel (delisted and non-A codes included),
  not a tradable universe — same limit as r1102.
* The over-representation is a description, not a diagnosis: this study does not
  establish *why* unverifiable stamps concentrate in the high-roe tail. A next
  step would be per-year, per-industry decomposition of `out_of_window`.
* No return is computed anywhere; this measures the input cell only.