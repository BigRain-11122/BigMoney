# E239 -- own turnover vs one counterparty's turnover (r1265 bm-b)

Cutoff: 2026-10-29. Panel: `data/daily` equal-weight basket (sh510300, sh510050, sh510500,
sh512100, sh588000), 3,497 sessions. Face: `results/state_tilt/OWNCROSS-2026-10-29.json`,
per-pair table `results/state_tilt/owncross_pairs_2026-10-29.csv`. Runner:
`scripts/e239_own_vs_cross.py` (selftest 11/11).

## The question E238 left open

E238 rebuilt the book without its own member and found the REST coefficient (0.771 on
d(log rest)) larger than the own coefficient (0.596 on d(log own)). Two readings survive:

1. economics -- a member's own turnover matters less than the rest of the book's;
2. units -- the rest aggregate is the SUM of four members, so one log point of it is four
   participants' worth.

Rescaling the sum by 1/4 multiplies the coefficient by four and changes nothing about its
t-statistic, so it cannot settle the question. The apples-to-apples form is per pair.

## Reading

| design | own | cross (one counterparty) | difference |
|---|---|---|---|
| pair fixed effects (within-pair demeaned) | 0.797 [0.748, 0.846] | 0.314 [0.274, 0.353] | 0.484 [0.408, 0.560] |
| member + date fixed effects | 0.539 | 0.055 | 0.484 [0.438, 0.530] |

- Multiplicity bar: |t| >= 3.227 (two-sided 5% over the 20 pair differences).
- Both designs return **own_exceeds_a_single_counterparty**; the difference point estimate is
  identical to three decimals, so the ordering does not depend on which fixed effects are
  absorbed.
- Mean single-member cross **0.356** over 20 ordered pairs (range -0.242..1.128, 15/20
  positive). Four counterparties would imply 4 x 0.356 = **1.425** against E238's published
  rest **0.771** -> ratio **0.541**.

## What the numbers say, and what they refuse to say

- The E238 ordering is not merely a unit artefact: even priced against a single counterparty,
  the own channel is larger than the cross channel, and the difference clears a bar that
  already accounts for 20 comparisons.
- But the aggregate is **not** an additive sum of participant impact: the sum's coefficient is
  about half of what four single-counterparty coefficients imply. Roughly half of what one
  counterparty's turnover carries does not survive in the sum -- a common-liquidity component,
  or attenuation from the members' turnovers moving together.
- No charge is granted and no arm is adopted. The family still has no bill.

## Reproducibility

- Rows: consecutive **joint** sessions of each ordered pair (a session one side did not print
  cannot turn a one-day move into a two-day move); 13,911 pooled pair rows.
- Estimation: `e235._ols_hac_full`, Newey-West lag 20, identical for every design.
- Pooled design keeps k=3 by demeaning each pair block (pair fixed effects in demeaned
  coordinates) instead of 20 dummies; the estimate is the same object, the HAC sandwich becomes
  tractable.
- Cross-check against E238 is **machine-read** from `loobook_latest.json`, never transcribed;
  if the file is missing the face publishes `available: false` with the reason.

## Selftest legs (11/11)

planted own > cross is called / planted equal is indistinguishable / planted cross > own is
called / the machinery really ran (20 pairs, >5000 rows, regressor sds above the dust floor) /
mean cross recovers the planted value / own slope recovers the planted value / a dust
counterparty regressor is refused, not fitted / every difference interval contains its point /
no fittable pairs is a verdict not a crash / no charge is asserted / the E238 cross-check is
read or declared absent.