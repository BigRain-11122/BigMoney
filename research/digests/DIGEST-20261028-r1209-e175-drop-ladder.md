# E175 — the drop ladder, and the base E174 read it off (r1209 bm-b, 2026-10-28)

Face: `results/e43_tilt_4member/TILT3SIGNDROPSWEEP-20261027.json`
Leg: `python scripts/e39_panel_census.py tilt3signdropsweep` (e39 selftest 558 -> 567)
Pool: E175-TILT3SIGN-DROP-LADDER (done, this round)
Card: E175 in `knowledge/METHODOLOGY_ASSETS.md`

## Question

E174 published two drop points for 2024_now's era flip and they disagreed: the
verdict came back when the top carrier was removed (raw +14.86 vs screened
+78.97) and disappeared again when the top five were removed (raw -4.48 vs
+72.08). Two points of a curve nobody drew. This leg draws it: k = 0..n carriers
removed in |contribution| order, verdict printed at every k, and the same ladder
run on an era whose engine level never moved as a control.

## What the first cut found before it published anything

The ladder's k=0 verdict disagreed with E171's headline on 2024_now (ladder
"agree", headline "disagree"), so the leg refused to publish a curve that did not
start where the published face starts. Root cause, and it is E174's:

* the per-name terms are **sums of daily `w * r`** inside a month, while the
  published engine level is a **compounded monthly mean**; the two bases are not
  the same quantity
* the offset is up to **55.8bp** (2024_now: decomposition base raw +31.3 vs
  published -21.6), which is **larger than the 46.7bp delta E174 was attributing**
* on 2024_now the offset alone flips the raw arm's sign (+31.3 -> -21.6)

E174's `flip_survival` read both of its points off the decomposition base. So
"the flip disappears when sh510580 is dropped" was the base offset moving, not
the carrier. The published TILT3SIGNNAMES face is frozen as-is (r1206 precedent);
this face carries a machine-readable `corrections` block naming the field and the
corrected reading, and the corrected reading is what should be quoted.

Fix, in-window: `_drop_ladder` takes the published era levels as its anchor and
every rung subtracts one carrier's contribution from them. k=0 IS the headline by
construction, and the offset is published beside it (`level_reconstruction`) plus
a selftest leg that pins two bases to opposite verdicts so an unanchored ladder
cannot be published as *the* ladder again.

## Findings (anchored)

1. **2024_now's disagreement survives every rung inside its own delta span.**
   k=0..9 reads disagree while 0.0 -> 98.5% of the delta is removed. The verdict
   only breaks at **k=11, when 108.5% of the delta has been removed** — i.e. only
   after eroding more than the delta is made of. Within span the raw arm runs
   -21.6 -> -57.3 while the screened arm falls +25.1 -> +5.6; no single-carrier
   removal reconciles them. Reading: **the 2024_now disagreement is a property of
   the two books, not one name-month** — the opposite of E174's implied answer.
2. **2021_2023 is the stable control and it is flat**: 625 carriers swept, 626
   rungs, "agree" at every k. That is what a verdict that is not carried by a few
   months looks like, and it is what a ladder is for.
3. **The two zero-delta eras are a control with no rungs.** pre2017 and 2017_2020
   have `engine_bp_delta = 0.0` exactly, so they have zero moved carriers and the
   ladder is a single rung. `flat_eras_ladder_is_flat` is true for both — a ladder
   that was not flat there would be broken before it said anything about 2024_now.
4. **The `full` era oscillates, and only out of span.** Seven bands, but the first
   change is at k=1160 of 1193 carriers — by then 99.7% of the names are gone and
   the remaining rungs are rounding. It is published flagged
   `beyond_delta_span` rather than suppressed: a reader should see that the tail
   is noise, not that the tail was hidden.

## What a reader should now say differently

"2024_now's engine verdict flips with the repair" holds at every carrier count up
to the point where more than the delta has been removed — so quote it as a book
property. And **do not quote E174's `flip_survival`**: it was read off a base
52.9bp away from the published level, which is more than the delta it explains.
E176 (wide-vs-ladder book split) is now the sharper open question: this leg says
the disagreement belongs to the books, but not yet which of the two books owns it.