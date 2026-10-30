# DIGEST 2026-10-30 r1279 bm-b -- E252: the star prices itself at the price it charges everyone else

Card: `knowledge/METHODOLOGY_ASSETS.md` E252. Runner `scripts/e252_star_prices_itself.py`
(selftest 17/17). Face `results/state_tilt/STARSELF-2026-10-29.json` (+ `starself_latest.json`).
S6 leg `star_self_price` (after `star_own_component`), smoke leg added.

## The question E251 left open

E251 settled what the star's residual is (its own lagged turnover; volatility and age both took
nothing) but every one of its fits prices OTHER members' moves -- dy_m for m != star. The reading
is "the star's turnover moves the rest of the book". E246/E249 had also found the star's own row
carrying a negative lead whose sign alternates by era, and E248 published the +-0.805 without ever
asking whether the star prices ITSELF. A channel that moves the book and a channel that moves its
own sleeve are two different mechanisms, and until now only one of them had been measured.

## Design

The same decomposition, turned around -- the star as the outcome, the same regressor, the same
estimator (e248._ols, Newey-West), the same row grid:

    S0  dy_s[t] = a + b_own dx_s[t] + b_self dx_s[t-1] + c1 dagg_loo[t-1]
    S1  S0 + b2 |dy_s[t-1]|          (the star's own lagged move)
    S2  S1 + b3 age_s(t)             (headline only; age is a row index inside a window)
    C   dy_m[t] = a + b_own dx_m[t] + b_cross dx_s[t-1] + c1 dagg_loo_m[t-1]     (m != s)

b_self and b_cross are the same regressor against two outcomes, so the comparison is in units by
construction; it is also the only comparison the face makes.

Two nulls, both design-shaped:

* **paired permutation band** -- the star's turnover is shuffled in time ONCE per draw and BOTH
  fits are re-run on that one shuffle, so the two coefficients are compared under the same
  destroyed signal exactly as they are compared under the same real one;
* **paired block bootstrap** -- contiguous 20-session blocks are resampled and both fits re-run per
  draw, so the interval on (b_self - b_cross) carries the correlation the two fits share through
  the common regressor. Two separately-built intervals would ignore it.

## Read (headline cell: 5 members, 1,328 common sessions, cutoff 2026-10-29)

star sh588000.

* b_self **-0.7339**, own shuffled band **[-0.3148, 0.2269]** -- far outside.
* b_cross **-0.7250**, band **[-0.2681, 0.2579]** -- far outside. (E251's published star column
  to the last digit: -0.7250430277727764, pinned at 1e-9 in the smoke leg.)
* difference **-0.0088**, paired bootstrap CI **[-0.3049, +0.2986]** (400 draws, sd 0.1553).
  Verdict `own_row_is_the_same_quantity`.
* Volatility takes nothing from the self coefficient in the other direction too: **b2 = +0.3209**,
  share **-0.068** (adding |dy_s| slightly *widens* b_self rather than absorbing it), so the
  self coefficient is not the star's own return autocorrelation wearing a turnover label.
* b_own (own contemporaneous turnover on the star's own move) = **+1.7528** -- the mechanical leg,
  published for context, not a finding.
* Per-member cross slopes: sh510300 -0.878, sh510500 -0.856, sh512100 -0.749, sh510050 -0.418.
  The star charges its largest counterparty most; its own row sits at the middle of that range.

Cells: all_five and era_2023_2024 are same-quantity (-0.734 vs -0.725, and -0.803 vs -0.833,
diff +0.031). era_2025_now reads self -0.463 INSIDE its band while cross -0.911 stays outside it;
early_three reads self -0.203 inside its band while cross -0.494 is outside. pre2020_four and
era_2020_2022 name no star at all (E245 lag-0 rule) and say so.

## Three reusable findings

(1) **"The same number" is a resolution claim, not an equality.** The point difference is 0.009
against a paired interval of +-0.30 -- the honest sentence is "no difference larger than 0.30 is
detectable", not "they are equal". Publish the resolution beside the point estimate, or a reader
takes an unresolved comparison for an identity.

(2) **Silence is per-side.** In 2025-now the cross coefficient is still -0.911 and outside its
band while the self coefficient falls inside its own. That is not "the star stopped pricing
itself"; it is 408 sessions not being enough to measure the star's own row. Reading the pair as
one verdict would have manufactured a regime change out of a width difference -- the verdict
vocabulary therefore has a branch for each side being unmeasured, and neither outranks the other.

(3) **A self-coefficient is a channel, not a cost.** Nothing here bills a member: b_self is what
the star's own turnover does to the star, and its equality with b_cross says the mechanism is one
quantity seen through two outcomes, not two effects that happen to add up.

## Traps

* The fixture's truth must be written in the coordinates the design uses. E251's lesson (an
  absolute-value-of-noise proxy is too weak to be a proxy) was applied up front: the volatility
  fixture drives the star's move with an exogenous |dy| and builds turnover as `0.9*|dy| + noise`,
  and the fit recovers b2 = -0.79 for a written -0.8.
* The first draft of the same fixture wrote the star's self term from its own CONTEMPORANEOUS
  step, which folds the truth into b_own and leaves b_self reading noise -- caught before any burn;
  a self-lead must come from the previous step by construction.
* Two faces must agree on WHICH sleeve is the star before any identity check means anything: the
  smoke leg refuses the comparison when the star differs, rather than pinning numbers from two
  different sleeves.