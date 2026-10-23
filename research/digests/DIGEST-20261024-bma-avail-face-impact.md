# T27 impact: does the first-announce availability repair change a factor cell?

r1102 bm-a · 2026-10-24 · evidence `results/fund_avail_face_impact.json`
(studies `results/fund_avail_notice.json` + `results/fund_avail_dispersion.json`)

## 0. A defect came first, and it was mine

The first `fund_avail_notice.py build` published a face that was wrong twice over.
The notice cache is keyed by **code inside one period**, but `build()` merged the
whole panel against a *concatenation of every period's cache*:

| face | panel rows | published face rows (draft) |
|---|---|---|
| income | 461,679 | 24,751,774 (53x) |

Every extra row was a duplicate, and — the part that matters — a row could be
handed the notice date of a **different period**. Nothing was consuming the file
yet, so nothing downstream was poisoned; the draft face was killed mid-build.

Fixed by aggregating period by period (`build_face_by_period`), with two
assertions that now live at the write site rather than downstream (r1096 law):
row count equals the panel row count, and `(code, period_end)` is unique.
Selftest 10/10 → 12/12, two new legs pinning "one code's Q1 notice must never
reach its Q2 row" and "a period with no cache falls back to *its own* deadline".
Rebuilt: 461,679 / 292,537 / 283,955 rows, 86/86 periods each.

## 1. Does the repair change a headline factor cell? It depends where you look

Sampling rule for both faces: per code, the latest period available on date *d*.
Month-ends 2010-01 → 2026-09 (201 dates), four headline income factors.

**At month-end: no.** Spearman between the two faces' rankings is ≥ 0.9966 for all
four factors and the top-decile basket turns over ≤ 1.7%. A month-end rebalance
cannot tell the two faces apart — by the last day of a month every deadline of the
quarter has passed and both faces have admitted the same rows.

**Inside the disclosure window: yes.** Probing at the statutory deadline −10
days, the ranking correlation drops and the basket moves:

| factor | ρ at deadline−10 | basket turnover | ρ at month-end | turnover |
|---|---|---|---|---|
| roe | 0.9503 | 6.9% | 0.9966 | 1.7% |
| np_yoy (net profit YoY) | 0.8932 | 15.9% | 0.9976 | 0.5% |
| rev_yoy (revenue YoY) | 0.9273 | 12.7% | 0.9974 | 0.7% |
| gpm (gross margin) | 0.9899 | 2.5% | 0.9995 | 0.3% |

So the repair is **not** a month-end asset. It matters exactly where a PIT event
study or a day-resolved decision operates — and the growth factors are where it
matters most (a sixth of the top decile is a different set of names).

## 2. The coverage curve inverts, which is the real hazard

Share of a quarter's rows actually available on a date, published face vs repair:

| probe | published (`avail_pit`) | repair (`avail_first`) |
|---|---|---|
| deadline −10d | **0.04%** | **7.0%** |
| deadline | **100%** | **98.7%** |
| deadline +30d | 100% | 99.1% |

The published face is not merely optimistic at the deadline (it asserts that a
whole quarter lands on one day); before the deadline it is **pessimistic** — it
says almost nobody has reported when ~7% have. Both errors come from the same
place: `min(stored_revision, deadline)` collapses the distribution onto the
deadline. Any "as of the deadline" statement built on it is one day-accurate and
thirty days-wrong.

## 3. Face-specific honesty (two surprises)

* **balance does not have the r1098 defect.** After the notice-window gate,
  97.7% of its 2010+ rows get an identical date under both faces (tighten 0.0%,
  delay 2.3%) — its stored stamp already tracks the announce date (median lag
  50d stored vs 48d notice). The distinct-date count still rises 22 → 54, but
  only for the late filers. The revision-stamp defect is an *income + cashflow*
  phenomenon, not a statement-panel universal — the r1099 headline should be
  read that way.
* **cashflow's notice field is mostly unusable as fetched:** 26,514 of 292,537
  rows land inside the plausible disclosure window, i.e. 90% fall back to the
  deadline (99.4% of rows identical to the published face). Until that is
  diagnosed (different report's date column? page-coverage hole?), the cashflow
  first-announce face is honest but thin, and the JSON says so row by row rather
  than pretending.

## 4. Limits of this measurement

* Universe is the statement panel as stored: it carries delisted and non-A codes
  (medians ≈ 10k names), not a tradable universe filtered by price data.
* Probes use calendar days; a trading-day probe would shift single days, not the
  shape of the coverage curve.
* No return is computed anywhere in this study — it measures the input cell
  (sample + ranking), so no prereg is implied and none is claimed.

## 5. What a consumer should do

1. Month-end / quarterly rebalances: the published face is adequate; do not
   re-burn on the repair.
2. Anything that resolves on a *day* inside a disclosure window, or that claims
   "known as of the deadline": use `avail_first` and drop `notice_status != "ok"`
   rows if you want the conservative bound, or keep the deadline fallback rows but
   report their share.
3. Never join the notice cache across periods — that is the r1102 defect, now
   asserted against in code.

## 6. Full-coverage dispersion (re-run)

`fund_avail_dispersion.py` re-ran on the completed cache (86/86 periods for all
three faces). Income, which is the face that actually carries the defect: 63.8%
of all rows become available earlier (2010+ era: 69.4% earlier, 27.8% unchanged,
2.9% later), and the number of distinct announce dates in a period goes from 10
to 66 (2010+ mean 13.9 → 80.1). That is the ordering capacity the repair
restores; §1 says what it is and is not worth.