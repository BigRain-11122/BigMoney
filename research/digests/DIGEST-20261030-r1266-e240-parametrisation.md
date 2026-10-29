# DIGEST 2026-10-30 r1266 bm-b — E240: the 0.541 was two unit errors, not an attenuation

Face: `results/state_tilt/AGGATT-2026-10-29.json` (1,328 common sessions, 2020-11-17 → 2026-10-29,
basket sh510300/sh510050/sh510500/sh512100/sh588000). Selftest 12/12.
Method card E240 in `knowledge/METHODOLOGY_ASSETS.md`.

## What was wrong with the 0.541

E239 divided E238's `loo_b_agg` (0.771) by four times the mean single-counterparty cross slope
(1.425). Neither side is what it was taken for.

| quantity | value | what it actually is |
|---|---|---|
| E238 `loo_b_agg` | 0.771 | coefficient on d(log agg) — BOOK SCALING, in the (d share, d book) parametrisation |
| implied rest channel | 0.140 | `c = (B − A)/(1 + κ)`, κ = w/(1−w) = 0.25 nominal; A = 0.596 published |
| direct rest (own + sum of four log increments) | 0.138 [0.100, 0.177] | this face's own fit on the common grid |
| one counterparty (identified) | 0.183 | own + one counterparty + sum of the other three |
| sum of the other three (same units) | 0.175 | difference +0.008 [−0.012, +0.022] |
| naive pair cross | 0.325 | own + one counterparty only; inflated by 1.89 at ρ = 0.424 |
| four times the naive cross | 1.299 | the comparator E239 used |

## Verdict

`rest_channel_is_additive`. One counterparty and the sum of the other three are
indistinguishable per log point; the rest channel adds up. The aggregate is not "keeping 54%"
of anything — 0.771 was the whole book's scaling coefficient, and 1.425 was four times a slope
already inflated 1.89× by the omission of three channels.

## Two controls that cannot be built (published as refusals)

1. **Book-move control is singular.** On an equal-weight leave-one-out book, B₋ₘ = SUM/(k−1)
   exactly (measured max deviation 0.0). (own, sum, book) has no three-dimensional content;
   "common component" and "aggregate channel" are the same regressor.
2. **Two-way FE form is non-identified.** The total book move is a date effect, so inside the
   within transform SUM₋ₘ = total − own collapses to −own (residual correlation −1.0). E238's
   design C only ever published b_own for this reason.

## Reproduction gap (open, next round)

Re-running E238's coordinates on this grid gives (A, B) = (−0.333, −0.174) against the published
(0.596, 0.771). The basis differs too: the published pair sits on the LEVEL rest (d log(agg −
own), the turnover-weighted mean of the others' increments) while this face's direct design uses
the SUM of the four other log increments — identical only at exactly w = 1/5, and the realised
turnover shares span 0.10..0.29. Both numbers are published with the face; the rotation is the
next wave's job.

## Reusable laws

- A coefficient is comparable only inside the parametrisation that produced it; the coordinate
  map between two parametrisations of the same regression is `B = a + c`, `A = a − κc`.
- "k × one member" is never the right comparator for a sum regressor: partialling the sum on the
  own regressor leaves the additive world's coefficient equal to the per-member one.
- A pair regression that omits the other members is biased by
  `(1 + (k−1)ρ − kρ²)/(1 − ρ²)` — measure the factor next to ρ instead of trusting the slope.