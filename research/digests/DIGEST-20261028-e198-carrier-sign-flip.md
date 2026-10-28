# E198 -- a persistent carrier is not a flipping carrier (round r1226, bm-b)

**Question.** E192 measured WHO does the wide book's monthly repair and found a
persistent carrier block (94-97% carry share, 80-89% of era gross, and the
months that fight the era total carried by those same names at 100%). That is a
statement about a stable *set*. It says nothing about whether the members of the
set repair the same *way*, so "the reversal is one set of names moving" could
still mean three different things: the same names alternate direction, or a few
big names flip while the rest hold, or the set is stable but a handful of its
members sit on the opposite side of the era total all along. E198 measures the
sign path of every carrier.

**Face.** `results/e43_tilt_4member/CARRIERFLIP-20261028.json`
(leg `scripts/e39_panel_census.py tilt3widecarriersignflip`, selftest 688 -> 697).

## What it reads

| era | carriers | pairs | flip rate (count) | flip rate (|value|-weighted) | within-name keep | across-name keep | top-3 opposite-net share |
|---|---|---|---|---|---|---|---|
| 2021_2023 | 352 | 3,399 | 55.8% | 59.9% | 0.9647 | 0.7120 | 90.5% |
| 2024_now | 873 | 18,081 | 45.7% | 35.3% | 0.9377 | 0.4387 | 83.5% |
| full | 697 | 20,256 | 48.1% | 37.1% | 0.9433 | 0.5175 | 71.9% |

pre2017 and 2017_2020 have **no repairing month at all** on this panel; they are
published as `no_carrier_survives_two_months` and are not zeroes dressed up as
readings.

1. **The count reading and the weight reading disagree, and the disagreement is
   the finding.** Roughly half of adjacent carrier months change sign (45.7% on
   2024_now), but the motion those flips destroy is only 8.13bp of a 341.6bp
   era gross -- 2.4%. Weighting the same events by `2 x min(|v_t|, |v_t-1|)`
   drops the rate to 35.3%. Carriers alternate direction often and cheaply.
2. **Nothing dies inside a name.** `within_name_keep` = 0.9377 (2024_now):
   only ~6% of the era's gross repair motion is cancelled between a name's own
   up-months and down-months. The carriers are one-directional in mass terms.
3. **The between-name term is not a new finding -- it is E182's headline.**
   `across_name_keep` reproduces `net_over_gross` on the published WIDESIDEGROSS
   face exactly (0.7120 / 0.4387 / 0.5175, `abs_diff = 0.0` on all three eras).
   E182 formed its denominator after netting each holding over the whole era, so
   its ratio *is* the name-level disagreement ratio; it was never a claim about
   time.
4. **The reversal has an owner, and the owner is directional.** The names whose
   era net points against the era total hold 28.1% of the name-net mass on
   2024_now, and three of them own 83.5% of that mass: sh510580 (net -41.11bp
   over 24 months, 16 of them down, keep ratio 1.000), sh510310 (-18.21, 18/24
   down, 1.000), sz159925 (-15.77, 10/16 down, 1.000). They are not flippers;
   they are one-way carriers on the wrong side.
5. **Flip rate is not a size property.** corr(typical magnitude, flip rate) =
   -0.028 on 2024_now and +0.009 on the full era: big carriers do not flip more
   often than small ones. The "a few big names alternate" story is dead.

**Verdict.** The between-month reversal is owned at name level, but the owner is
a persistent *directional* block, not a flipping cast. Naming carriers buys a
list of names that are structurally on the other side, not a prediction of when
they will move.

## Honest limits

- `idle_bp = gross - net` favours names with a negative era net (for them it is
  gross + |net|), so idle-share concentration is published beside the
  against-fraction, and the verdict rests on the against-fraction.
- The 2.4% flip-loss share is measured on adjacent *measured* months only; a
  carrier that repairs in January and again in March has no adjacent pair, and
  those gaps are not scored as zero (the E192 sparsity rule).
- Descriptive census: n is adjacent month pairs, not trials. No gate, no prereg,
  no trial count.
