# DIGEST — E238: the book contains the member, and only one of the three designs cared

- round r1264 (bm-b), 2026-10-30
- face `results/state_tilt/LOOBOOK-2026-10-29.json`, by-member `loo_by_member_2026-10-29.csv`
- runner `scripts/e238_leave_one_out_book.py` (selftest 8/8), S6 leg `leave_one_out_book`
- card `knowledge/METHODOLOGY_ASSETS.md` E238
- evidence cutoff 2026-10-29; 5 members / 13,911 pooled differenced rows

## Question the card asked

E236's three designs read the own-turnover coefficient 25x apart (0.017 .. 0.431) and E237
could not name what it measures. Each member's own turnover sits inside the book turnover its
share is divided by, so the share regressor may be arithmetic rather than a market object.
Build the book WITHOUT the member and re-run the same three designs on the same sessions.

## What was measured

| design | inclusive | leave-one-out | gap | arithmetic predicts | verdict |
|---|---|---|---|---|---|
| differences (A) | 0.4371 [0.3467, 0.5275] | 0.5963 [0.5100, 0.6825] | -0.1592 [-0.1778, -0.1359] | -0.0486 | `own_channel_survives_the_denominator` |
| frozen_z (B) | -0.0366 [-0.0561, -0.0171] | +0.0013 [-0.0170, 0.0196] | -0.0379 | -0.0354 | `own_channel_is_a_denominator_artefact` |
| two_way_fe (C) | 0.02346 [0.0118, 0.0352] | 0.02289 [0.0124, 0.0333] | -0.0006 | n/a (b_agg absorbed) | `own_channel_survives_the_denominator` |

Own share of book turnover: **0.218 turnover-weighted** (kappa 0.279), not the nominal 1/5
(kappa 0.25); per-member medians run 0.029 (sh512100) .. 0.462 (sh510050).

Per member: 4 survive / 0 artefact, sh510300 `unresolved_gap_beyond_arithmetic`.

## Why it matters

1. The article of faith going in — "the own channel is the denominator" — is FALSE for the
   design that produced the big number. Removing the member from its own book makes the
   coefficient 36% LARGER (0.437 -> 0.596), i.e. the inclusive denominator attenuates it. The
   differenced design's own channel is not arithmetic.
2. The design that produced the *small* number is the arithmetic one. frozen_z's -0.0366 is
   93% reproduced by `kappa*(b_own_loo - b_agg_loo)`, and the leave-one-out reading is +0.0013
   (t 0.14). So E236's 25x disagreement is not one mystery but two different mechanisms, and
   only one of them is a denominator artefact.
3. design C never had the denominator in it: the date fixed effects absorb the book, so its
   reading is unchanged to three decimals. Reading "the three designs agree in sign" as
   "the channel is robust" was always wrong — two of the three were measuring different things.

## Method notes worth carrying

- The mechanical prediction has to be published as a number, and it has to use the REALISED
  weight. At the nominal 1/5 the prediction is -0.0436; at the realised 0.218 it is -0.0486 —
  small difference here, but the per-member kappa spans 0.03..0.85, so a nominal weight would
  be a fiction on a panel whose turnover shares are not equal.
- The regressor identity d(share)_incl - d(share)_loo = -d(log(1-w)) holds to 0.0e+00, so the
  two denominators are two restrictions of one regression. That is why the gap can be
  *predicted* and why a gap alone is not evidence.
- With a constant own share the inclusive regressor is dust (sd ~ 1e-16) and OLS on dust
  returns 3.8e13. The runner refuses below 1e-8; the selftest pins the refusal AND that the
  leave-one-out design stays estimable (an equivalence-style leg that would otherwise "pass"
  on a degenerate panel — r1261 family).
- The paired gap is bootstrapped with 400 joint-date blocks of 20 sessions, using a lean
  normal-equation fit inside the replicates (29s); recomputing HAC covariance 400 times would
  add nothing but minutes.

## Next

E239 seeded (`E239-OWN-VS-SINGLE-CROSS-ELASTICITY`): in the rest-free book the cross
coefficient 0.771 exceeds the own 0.596, which is either an economic ordering or the units of
summing four members into one aggregate. The apples-to-apples form is per pair — dy on
d(log own) and d(log other_j) for each of the four others — and the impact story predicts
own > cross on that footing.