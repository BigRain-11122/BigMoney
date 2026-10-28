# DIGEST 2026-10-28 r1221 bm-b — E187: is the wide book's surviving monthly motion just its own churn?

Pool head burned: `E187-WIDE-CROSSMONTH-CHURN-TIE` (seeded r1217 after E184, ready since
2026-10-28T14:05). Leg `tilt3widechurntie` in `scripts/e39_panel_census.py`; face
`results/e43_tilt_4member/WIDECHURNTIE-20261027.json`; evidence cutoff 2026-10-27.

## The question, stated as a falsifiable prediction

E184 (r1217) showed the wide book's thin net is a between-month sign disagreement: 0.872 of
the monthly motion survives inside a month but only 0.472 survives across months (2024_now).
E187 asks whether the months that disagree are the months the book re-selected its holdings.
If they are, the spread is a statement about **who was held** and must be discounted by
turnover instead of quoted as repair quality. The discount is applied only if measured:
`|r| >= 0.5` between the monthly repair net and the same month's membership turnover.

## Result: the discount does not apply — churn is independent of the repair everywhere

| era | months | repairing months | mean turnover | r(net, turnover) | class |
|---|---|---|---|---|---|
| pre2017 | 44 | 0 | 0.0572 | — | `no_repair_in_era` |
| 2017_2020 | 48 | 0 | 0.0352 | — | `no_repair_in_era` |
| 2021_2023 | 36 | 14 | 0.0500 | **+0.048** | `turnover_independent` |
| 2024_now | 34 | 24 | 0.0248 | **+0.159** | `turnover_independent` |
| full | 162 | 38 | 0.0419 | **-0.013** | `turnover_independent` |

Restricted to months where the repair actually moved something, the correlation does not
rescue the churn story either: +0.192 / +0.135 / +0.122. On the absolute-motion side it is
mildly **negative** (-0.107 / -0.051 / -0.122): bigger churn goes with smaller repair motion.

Three readings that make the refutation concrete:

1. **The high-churn half carries LESS motion, not more.** 2024_now's above-median-turnover
   months average 7.27bp of |net| against 10.26bp for the quiet half, and hold only 41.5% of
   the era's absolute motion (2021_2023: 2.25 vs 4.86, 31.6%). Seventeen hot months of
   thirty-four buying less than half the motion is the opposite of a churn signature.
2. **The months that fight the era total sit in the COLD half.** Against-month mean turnover
   0.0465 vs 0.0508 (2021_2023), 0.0204 vs 0.0255 (2024_now), 0.0356 vs 0.0424 (full); the
   share of against-months in the hot half is 57.1% / 20.0% / 33.3% — i.e. chance.
3. **The biggest single months are quiet months.** 2024_now's three largest-gross months are
   2024-09 (turnover 0.0196, net -55.3bp), 2025-09 (0.0108, +42.2bp) and 2026-07 (0.0351,
   +36.3bp) — all below the era's own maximum turnover of 0.0388. The reversals are the same
   names moving, not different names being held.

So E184's between-month reversal is **not** a membership artefact. The spread may still be
too thin to quote (E184 already says that), but quoting it does not require a turnover
discount, and a turnover discount applied by default would have removed motion for no reason.

## What the leg also had to publish to be honest

- **An empty repair set is not a flat net.** pre2017 and 2017_2020 have *zero* months in which
  the repair moved the wide book at all (net exactly 0.0 in every month, `months_repairing = 0`).
  Classified as `no_repair_in_era`, not `net_flat`: E182's "exactly flat" for those eras is an
  empty repair set, and reporting it as a measured flatness would claim a measurement nobody took.
- **Membership has to come from a presence recorder.** The contribution sink is written per
  name-day while the name is held, so a member whose daily returns were all zero still counts
  as present while a name that never traded cannot appear. `__cash__` is the un-invested
  residual and is excluded from membership, from the name count and from `net_bp` (published
  beside it as `cash_bp`); a count that swallows the cash leg reads complete while being short
  by one pseudo-member.
- **Turnover must be a ratio, not a count of entries.** turnover =
  (entered + left) / mean(prev_size, cur_size). The wide book grew 0 → 56 → 159 → 619 → 1202
  names across the panel, so raw entry counts would track panel growth and would correlate with
  anything that also grows. The same column also says something worth knowing on its own: this
  book's churn FELL as it widened (0.057 → 0.035 → 0.050 → 0.025 per month).
- The first era month takes its turnover anchor from the panel month before the era (membership
  only, no era returns), so the row set stays exactly the era's months.
- Join to E184 on disk reproduces the published era net to 4.87e-4 bp; cash delta is 0.000bp in
  every era of this panel.

## Limits

- n is months (34-162), not trials; no gate, no prereg, no trial count. This is a descriptive
  census leg like the rest of the E4x family.
- Turnover above 1.0 would mean more than the whole book turned; the observed maximum is 0.16.
- Membership cannot see a name held for the whole month if the panel had no row for it at all.

## Next

`E188-DECOM-LABEL-DUTY` (r1218) is the remaining ready pool row and is the natural follow-up on
the label side of the same family; `E190-DROP-FRAGILITY-SWEEP` (r1220) is the seeded third.