# E106: the repair steps at the print — but on upward prints it steps the wrong way

- date: 2026-10-27 (bm-b r1171)
- face: `results/e44_midmonth/REPAIRSTEP-20261026.json`
- code: `scripts/e39_panel_census.py` mode `repairstep`
- pool: E106 (closed here); E108 seeded with the one-line factor fix + re-derivation list
- question (pool E106): E104 flagged 16 reads past +/-100% inside unchanged holdings and
  left one witness unexplained — sh510580 reads +1464% in the repaired arm where the raw
  series reads +295%, and the arm-vs-raw level ratio moves x10.05 -> x39.8 *at* the event.
  Does the repaired series step where the print is, and does the step cancel it?

## Answer: where yes, which way no

For every flagged (name, window) the arm-vs-raw ratio is walked over consecutive priced
closes, so each rep/raw move is a step with a date, a factor, the raw one-session read and
the repaired one-session read beside it. 16 windows, 322 steps, and the per-window step
product reconciles to the published ratio change in **0 of 16 mismatches**.

| verdict | windows | meaning |
|---|---|---|
| `arm_untouched_raw_print` | 8 | the arm never touched the name; the raw print is still there |
| `step_amplifies_print` | 8 | the step sits on the print and **multiplies instead of dividing** |
| `step_without_a_print` | 0 | no step lands on a session without a print |

So the placement test passes and the direction test fails: every step lands on a session
that carries a >100% one-session print, and every one of those steps reads
`rep_ret = (1 + raw_ret)^2 - 1` — it doubles the print instead of removing it.

| name | window | raw read | arm read | step date | step | raw @step | arm @step | reciprocal read |
|---|---|---|---|---|---|---|---|---|
| sh510580 | 2024-08-30 -> 09-30 (me) | +406.4% | **+1902.8%** | 2024-09-02 | x3.955 | +295.5% | **+1464.1%** | +28.1% |
| sh510580 | 2024-08-15 -> 09-18 (mid) | +283.9% | +1418.1% | 2024-09-02 | x3.955 | +295.5% | +1464.1% | -2.9% |
| sh510310 | 2024-08-30 -> 09-30 (me) | +145.6% | +393.5% | 2024-09-23 | x2.009 | +100.9% | +303.8% | +22.2% |
| sh510310 | 2024-09-18 -> 10-15 (mid) | +143.4% | +389.0% | 2024-09-23 | x2.009 | +100.9% | +303.8% | +21.1% |
| sz159747 | 2023-03-31 -> 04-28 (me) | +84.1% | +274.2% | 2023-04-26 | x2.032 | +103.2% | +313.1% | -9.4% |
| sz159747 | 2023-04-17 -> 05-15 (mid) | +87.6% | +281.3% | 2023-04-26 | x2.032 | +103.2% | +313.1% | -7.7% |
| sh510100 | 2025-02-28 -> 03-31 (me) | +102.5% | +305.0% | 2025-03-10 | x2.000 | +100.0% | +300.0% | +1.3% |
| sh510100 | 2025-02-17 -> 03-17 (mid) | +106.5% | +313.0% | 2025-03-10 | x2.000 | +100.0% | +300.0% | +3.3% |

The last column is the same print with the reciprocal factor. It is the read the arm would
publish had the factor been applied the other way — and it is the plausible one: an ETF
does not gain 30x in a month, and +28%/-9%/+22% is the kind of number these windows carry.

## Root cause (one line, and it is not in the price data)

`panel_screen.implied_ratio()` folds the direction away to answer a different question —
it returns a *share ratio* >= 1 so the "nearest integer" test can recognise 1:2 and 1:4
conversions (`ratio = 1/(1+ret)`, then inverted when `< 1`). `split_events()` then reuses
that same folded number as the price factor (`"factor": ir["ratio"]`). For a downward print
the folded ratio equals the cancelling factor (a halved price is multiplied back by 2, so
the repair is right), but for an upward print the cancelling factor is `< 1` while the
folded ratio is `> 1` — the repair multiplies the print by itself. That is why every
amplified step reads `(1+r)^2 - 1` and why the level ratio jumps exactly AT the event: the
date is right, the direction is mirrored.

## The other 8

The untouched windows are the integer gate working as designed, and they are a different
defect: `sz159845` (+176.9% print, implied ratio 2.77, nearest 3, resid 7.7% > 2%),
`sh512200` (+170.1%), `sh516160` (+292.1%, +207.7%), `sh516300` (+153.9%, +165.6%). Both
arms carry the raw print, so all 8 reads are print artefacts living in the published
screened arm — the panel never fixed them and nothing downstream is told.

## What this changes

- No published face is re-derived here: the arm semantics belong to
  `panel_screen.neutralise`, and changing it silently would move every screened face in
  the repo without a before/after. That is seeded as E108 with the exact patch and the
  re-derivation list.
- Reading rule until E108 lands: any screened/gap-arm read whose window spans a >100%
  upward print is inflated by that print, and the inflation is `x(1+r)`, not a mystery.

## Honest

- Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count.
- A step is judged against the panel's own one-session reads, not a vendor corporate-action
  file; a real 1:N conversion and a misprint look identical here.
- `reciprocal_factor_read` is arithmetic on the published step, not a re-burn.