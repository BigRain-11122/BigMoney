# The two-producer wedge is a fee, so the labels were wrong and the numbers were not (r1218, bm-b, 2026-10-28)

## What was published before

E180 (`results/e79/DECOMLEVELQUOTES-2026-10-27.json`) audited every level cell in the
family and found one field name -- `decomposition_engine_bp` -- published from two
producers:

* E176 (`results/e43_tilt_4member/TILT3SIGNBOOKSPLIT-20261027.json`) reads the per-name
  `w*r` sink of both books and differences their annualised sums;
* E177 (`results/e43_tilt_4member/TILT3SIGNDECOMOFFSET-20261027.json`) differences the two
  books' daily curve returns and annualises the difference.

On ten comparable era/arm cells they disagree by 2.92..3.63bp with a 0.70bp spread. E180
correctly refused to call that rounding (a near-constant gap across eras of very different
volatility cannot be within-month compounding) but could not say which term, on which side,
made it. An unattributed wedge is a third reading of the same level, not a tolerance.

## What this measures

`run_tilt3levelwedge()` -> `results/e79/LEVELWEDGE-20261027.json`, mode `tilt3levelwedge`,
e39 selftest 636/636. Three candidates are tested per era and per arm instead of argued:

| candidate | what it removes | residual on the ten cells |
|---|---|---|
| (a) additive constant | the gap minus its own arm mean | 0.20..0.35bp (fails) |
| (b) scale factor | gap minus least-squares multiple of the level | up to 3.4bp (fails) |
| (c) dropped term | gap minus the rebalance fee | **0.0000bp on 10/10** |

The fee is not inferred. `_monthly_core()` gained a `cost_mult` seam and both arms were
rebuilt with `cost_mult=0.0` on the same panel (same cutoff asserted). The difference between
the fee-on and fee-off daily-difference reading is the term the sink cannot see, because
`simulate()` records `growth = sum w*r` and subtracts the turnover fee from the curve
afterwards. Measured fee term: 2.9207 / 3.5300 / 3.6208 / 3.3984 / 3.3570bp (pre2017, 2017_2020,
2021_2023, 2024_now, full). Wired as a check, both published faces are reproduced exactly
(max |diff| 0.0bp on 10 cells each), so the gap is the faces' own number and not a re-burn.

## What it changes

The two numbers were never two arithmetics of one object:

* the sink-based reading is **gross** of the turnover fee;
* the curve-based reading is **net** of it;
* and the difference is the price of the wide book's turnover minus the fixed ladder's,
  about 2.17%/month of extra turnover (0.283bp a month at 13.041bp a side).

So the repair is a labelling duty on the published faces, not a re-derived number. Quoting
either as "the decomposition" without the gross/net word is the category error E180 flagged;
the near-constancy is not a property of the signal but of a monthly rebalance paid every month.

## Traps this closes

1. **A wedge that is measured three ways is located; a wedge that is labelled "definitional"
   is deferred.** The decisive instrument was not a smarter decomposition but a `cost_mult`
   seam on the shared build, which turns a definitional question into two runs of one panel.
2. **A near-constant offset is often a per-period charge.** Before attributing a constant to
   compounding or to a scale factor, ask which term is paid every period: a fee, a
   withholding, a fixed minimum. Compounding scales with the era; a charge does not.
3. **The field-name collision survived because the label was silent.** Both producers publish
   the same key with the same units and the same 2dp quantum; only the fee differs, so no
   tolerance would ever have flagged it as an error. E180's collision sweep found it; this leg
   says what to write on it.